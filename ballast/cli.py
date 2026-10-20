"""`ballast` command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .chain_profile import MIN_SAMPLE_BLOCKS, ProfileError, identify
from .config import load_chain_config
from .rpc import RpcError, node_rpc


def write_pallets(cfg, ident, path: str) -> None:
    """Every pallet with its call names, from the live metadata, labelled with the profile."""
    from datetime import datetime, timezone

    from .chain import connect

    substrate = connect(cfg.profile, cfg.url)
    pallets = {}
    for pallet in substrate.metadata.pallets:
        calls = [c.value["name"] for c in (pallet.calls or [])]
        pallets[pallet.value["name"]] = {"index": pallet.value["index"], "calls": calls}
    out = {
        **ident.as_dict(),
        "url": cfg.url,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pallet_count": len(pallets),
        "pallets": pallets,
    }
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(f"wrote {len(pallets)} pallets -> {path}", file=sys.stderr)


def cmd_chain(args: argparse.Namespace) -> int:
    """Identify the chain behind the configured profile; print its label, decimals and block counts."""
    if args.blocks < MIN_SAMPLE_BLOCKS:
        print(f"ballast: --blocks must be >= {MIN_SAMPLE_BLOCKS}", file=sys.stderr)
        return 2
    try:
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
    except ProfileError as exc:
        print(f"ballast: {exc}", file=sys.stderr)
        return 2
    try:
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=not args.no_measure, sample_blocks=args.blocks)
    except (ProfileError, RpcError, ValueError) as exc:
        print(f"ballast: [{cfg.profile.name}] {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"ballast: [{cfg.profile.name}] node unreachable at {cfg.url}: {exc}", file=sys.stderr)
        return 3
    if args.pallets:
        write_pallets(cfg, ident, args.pallets)
    if args.json:
        print(json.dumps({**ident.as_dict(), "url": cfg.url}, indent=2))
        return 0
    print(ident.banner())
    print(f"  label     {ident.profile.label}")
    print(f"  url       {cfg.url}")
    print(f"  :code     {ident.facts.code_hash}")
    print(f"  decimals  {ident.decimals if ident.decimals is not None else 'unreported'}")
    data = ident.as_dict()
    print(f"  multisig  {data['multisig_shape']}")
    counts = data["block_counts"]
    if isinstance(counts, dict):
        print(
            f"  blocks    {counts['block_time_ms']:.0f} ms (median {counts['median_block_time_ms']:.0f}, "
            f"mean {counts['mean_block_time_ms']:.0f}) "
            f"over {counts['measured_over_blocks']} blocks "
            f"-> H={counts['H']} K={counts['K']} W={counts['W']} N={counts['N']}"
        )
    else:
        print(f"  blocks    {counts}")
    for note in ident.notes:
        print(f"  note      {note}")
    return 0


def cmd_reserves(args: argparse.Namespace) -> int:
    """Reserve token balance of a holder (the vault) from every provider, latest + finalized, compared."""
    from .sepolia import SEPOLIA_PROVIDERS, balance_of_data, chain_id, compare, cross_check, providers_from, read_all

    try:
        balance_of_data(args.holder)  # a malformed address is a usage error (2), not a provider outage (3)
        balance_of_data(args.token)
        providers = providers_from(args.provider or SEPOLIA_PROVIDERS, timeout=args.timeout)
    except ValueError as exc:
        print(f"ballast: {exc}", file=sys.stderr)
        return 2
    report: dict = {"erc20": args.token, "holder": args.holder, "chain_ids": {}, "tags": {}}
    if args.note:
        report["note"] = args.note
    for p in providers:
        try:
            report["chain_ids"][p.name] = chain_id(p)
        except Exception as exc:  # noqa: BLE001 — reported, never fatal: the readings below show the outage
            report["chain_ids"][p.name] = f"error: {exc}"
    for tag in args.tag:
        report["tags"][tag] = compare(read_all(providers, args.token, args.holder, tag)).as_dict()
    if args.cross_check:
        report["cross_check"] = cross_check(providers, args.token, args.holder, args.cross_check)
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2)
            fh.write("\n")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"token {args.token} · holder {args.holder} · chain ids {report['chain_ids']}")
        for tag, comp in report["tags"].items():
            for r in comp["readings"]:
                where = f"#{r['block_number']} {r['block_hash']}" if r["block_hash"] else "-"
                value = r["reserves"] if r["error"] is None else f"ERROR {r['error']}"
                print(f"  {tag:<9} {r['provider']:<12} {where}  {value}")
            for issue in comp["disagreements"]:
                print(f"  {tag:<9} DISAGREE {issue}")
        if args.cross_check:
            cc = report["cross_check"]
            print(f"  cross-check {cc['tag']} #{cc.get('block_number')} {cc.get('block_hash')}: "
                  f"{'AGREE' if cc['agree'] else 'DISAGREE'} {json.dumps(cc['providers'])}")
    # any requested tag with no successful reading at all = that read is down
    down = any(all(r["error"] for r in comp["readings"]) for comp in report["tags"].values())
    disagree = any(comp["disagreements"] for comp in report["tags"].values())
    if args.cross_check and not report["cross_check"]["agree"]:
        disagree = True
    return 3 if down else (1 if disagree else 0)


def _watcher_key(profile, uri: str | None):
    """Stand-in: a //Dev URI. Anything else: the secret URI in $BALLAST_WATCHER_SURI (never logged)."""
    import os

    from substrateinterface import Keypair

    from .chain import dev_keypair

    if profile.is_standin:
        return dev_keypair(profile, uri or "//BallastW1")
    suri = os.environ.get("BALLAST_WATCHER_SURI")
    if not suri:
        raise ProfileError(f"profile {profile.name}: set BALLAST_WATCHER_SURI (dev URIs are stand-in only)")
    return Keypair.create_from_uri(suri)


def _addresses(profile, items: list[str]) -> list[str]:
    from .chain import dev_keypair

    return [dev_keypair(profile, i).ss58_address if i.startswith("//") else i for i in items]


def cmd_watch(args: argparse.Namespace) -> int:
    """Run one watcher: freeze the breaker asset on a reserve deficit or a total provider outage."""
    from .chain import connect
    from .sepolia import SEPOLIA_PROVIDERS, providers_from
    from .watchdog import JsonLog, WatchConfig, Watchdog

    if (args.max_block_age < 0 or args.fail_closed_after < 0 or args.poll_interval < 0 or args.timeout <= 0
            or (args.poll_blocks is not None and args.poll_blocks < 1)):
        print("ballast: --max-block-age / --fail-closed-after / --poll-interval must be >= 0, --timeout > 0, "
              "--poll-blocks >= 1", file=sys.stderr)
        return 2
    try:
        from .sepolia import balance_of_data

        supply_ids = [int(x) for x in args.supply_assets.split(",")]
        if len(set(supply_ids)) != len(supply_ids) or args.breaker not in supply_ids:
            raise ValueError("--supply-assets: distinct ids, and must include --breaker (S1 + S2 = every backed asset)")
        balance_of_data(args.holder)  # holder and token must be EVM addresses before anything is armed
        balance_of_data(args.token)
        providers = providers_from(args.provider or SEPOLIA_PROVIDERS, timeout=args.timeout)
        cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
        if not cfg.url.startswith(("ws://", "wss://")):
            # submitting with wait-for-inclusion needs a websocket: an http URL would arm a watcher that cannot freeze
            raise ValueError(f"node URL {cfg.url!r}: the watcher needs a ws:// or wss:// URL")
        need_counts = args.poll_blocks is None or (args.bot and args.heartbeat_k is None)
        ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=bool(need_counts))
        poll_blocks = args.poll_blocks
        if poll_blocks is None:
            if ident.counts is None:
                raise ProfileError("block time not measured: pass --poll-blocks")
            poll_blocks = ident.counts.poll_n
        keypair = _watcher_key(ident.profile, args.watcher)
        watchers = _addresses(ident.profile, args.watchers.split(","))
        bot = _addresses(ident.profile, [args.bot])[0] if args.bot else None
        heartbeat_k = args.heartbeat_k if args.heartbeat_k is not None else (
            ident.counts.heartbeat_freeze_k if bot else None)
        if heartbeat_k is not None and heartbeat_k < 1:
            raise ValueError("--heartbeat-k must be >= 1")
    except OSError as exc:
        print(f"ballast: node unreachable: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001 — bad flags, profile, key URI: one line, exit 2, no traceback
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    wcfg = WatchConfig(
        breaker_id=args.breaker,
        supply_ids=supply_ids,
        watchers=watchers,
        threshold=args.threshold,
        token=args.token,
        holder=args.holder,
        poll_blocks=poll_blocks,
        fail_closed_after=args.fail_closed_after,
        poll_interval_s=args.poll_interval,
        max_block_age_s=args.max_block_age or None,
        read_deadline_s=2 * args.timeout,  # two requests per reading, each bounded by --timeout
        bot=bot,
        heartbeat_k=heartbeat_k if bot else None,
    )
    try:
        log = JsonLog(args.log, profile=ident.profile.name, chain=ident.profile.label, breaker=args.breaker)
    except OSError as exc:
        print(f"ballast: --log {args.log}: {exc}", file=sys.stderr)
        return 2
    try:
        try:
            substrate = connect(ident.profile, cfg.url)
        except Exception as exc:  # noqa: BLE001
            log("not-armed", message=f"node unreachable at {cfg.url}: {type(exc).__name__}: {exc}")
            return 3
        dog = Watchdog(substrate=substrate, profile=ident.profile, head_rpc=node_rpc(cfg.url),
                       keypair=keypair, providers=providers, cfg=wcfg, log=log)
        try:
            pre = dog.preflight()
        except Exception as exc:  # noqa: BLE001 — any preflight failure means "cannot freeze": say so, exit 2
            log("not-armed", message=f"{type(exc).__name__}: {exc}" if not isinstance(exc, RuntimeError) else str(exc))
            return 2
        log.context["reserve"] = pre["reserve"]
        log("start", **pre, poll_blocks=poll_blocks, fail_closed_after=args.fail_closed_after,
            heartbeat={"bot": bot, "k": heartbeat_k} if bot else "off",
            max_block_age=args.max_block_age or "off",
            supply_ids=supply_ids, providers=[p.name for p in providers], erc20=args.token, holder=args.holder,
            message=f"armed: M_watch {pre['m_watch']} · reserve {pre['reserve']} · freeze if reserves < supply of "
                    f"assets {supply_ids} (now {sum(int(v) for k, v in pre['supplies'].items() if int(k) in supply_ids)})"
                    f" · every {poll_blocks} blocks")
        return dog.run(until_frozen=args.until_frozen, max_seconds=args.max_seconds)
    except KeyboardInterrupt:
        log("stop", message="interrupted")
        return 0
    finally:
        log.close()


def _key(profile, uri: str | None, env: str, default: str):
    """Stand-in: a //Dev URI (default `default`). Anything else: the secret URI in $<env> (never logged)."""
    import os

    from substrateinterface import Keypair

    from .chain import dev_keypair

    if profile.is_standin:
        return dev_keypair(profile, uri or default)
    if uri:
        raise ProfileError(f"profile {profile.name}: dev URIs are stand-in only; set {env}")
    suri = os.environ.get(env)
    if not suri:
        raise ProfileError(f"profile {profile.name}: set {env}")
    return Keypair.create_from_uri(suri)


def _deployment_context(args: argparse.Namespace):
    """(profile, substrate, deployment) for the role-split commands; the node must be the manifest's chain."""
    from .chain import connect
    from .roles import Deployment

    cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
    ident = identify(node_rpc(cfg.url), cfg.profile.name, measure=False)
    dep = Deployment.load(ident.profile.name, args.deployment)
    if dep.genesis_hash != ident.facts.genesis_hash:
        raise ProfileError(f"deployment is for genesis {dep.genesis_hash}, the node is {ident.facts.genesis_hash}")
    return ident.profile, connect(ident.profile, cfg.url), dep


def _providers(args: argparse.Namespace, dep, bot_order: bool = False):
    from .sepolia import SEPOLIA_PROVIDERS, providers_from

    specs = args.provider or dep.reserve.get("providers")
    if not specs:  # Sepolia; the bot reads drpc first (archive depth for finalized / old block hashes)
        specs = list(reversed(SEPOLIA_PROVIDERS)) if bot_order else list(SEPOLIA_PROVIDERS)
    return providers_from(specs, timeout=args.timeout)


def _print_json(obj: dict) -> None:
    print(json.dumps(obj, default=str))


def cmd_mint(args: argparse.Namespace) -> int:
    """Operator (key A): propose a mint through M_mint — it executes only if the reserve bot co-signs."""
    from .bot import operator_accounts, parse_amount
    from .multisig_ops import call_hash, pending

    try:
        profile, substrate, dep = _deployment_context(args)
        amount = parse_amount(args.amount, dep.decimals)
        key = _key(profile, args.key, "BALLAST_OPERATOR_SURI", "//BallastA")
        beneficiary = _addresses(profile, [args.beneficiary])[0]
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    m_mint, _ = operator_accounts(dep, substrate.ss58_format or 42)
    call = substrate.compose_call(call_module="Assets", call_function="mint",
                                  call_params={"id": dep.breaker, "beneficiary": beneficiary, "amount": amount})
    op = pending(substrate, m_mint.address, call_hash(call))
    if args.cancel:
        if op is None:
            _print_json({"action": "cancel", "result": "nothing pending", "call_hash": call_hash(call)})
            return 1
        r = m_mint.cancel(substrate, profile, key, op, step="operator_cancel_mint", label="Assets.mint")
        _print_json({"action": "cancel", "call_hash": op.call_hash, "receipt": r.as_dict()})
        return 0 if r.outcome.ok and "Multisig.MultisigCancelled" in r.event_names() else 1
    if op is not None:
        _print_json({"action": "propose", "result": "already pending", "call_hash": op.call_hash, "timepoint": op.timepoint})
        return 1
    r = m_mint.propose(substrate, profile, key, call, step="operator_propose_mint", label="Assets.mint")
    _print_json({"action": "propose", "call_hash": call_hash(call), "amount": str(amount), "beneficiary": beneficiary,
                 "receipt": r.as_dict()})
    return 0 if r.outcome.ok and "Multisig.NewMultisig" in r.event_names() else 1


def cmd_thaw(args: argparse.Namespace) -> int:
    """Operator (A or A2): propose thaw_asset through M_admin — it executes only with a second signature."""
    from .bot import operator_accounts
    from .multisig_ops import call_hash, pending

    try:
        profile, substrate, dep = _deployment_context(args)
        key = _key(profile, args.key, "BALLAST_OPERATOR_SURI", "//BallastA")
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    _, m_admin = operator_accounts(dep, substrate.ss58_format or 42)
    call = substrate.compose_call(call_module="Assets", call_function="thaw_asset", call_params={"id": dep.breaker})
    op = pending(substrate, m_admin.address, call_hash(call))
    if args.cancel:
        if op is None:
            _print_json({"action": "cancel", "result": "nothing pending"})
            return 1
        r = m_admin.cancel(substrate, profile, key, op, step="operator_cancel_thaw", label="Assets.thaw_asset")
        _print_json({"action": "cancel", "call_hash": op.call_hash, "receipt": r.as_dict()})
        return 0 if r.outcome.ok else 1
    if op is not None:
        _print_json({"action": "propose", "result": "already pending", "call_hash": op.call_hash, "timepoint": op.timepoint})
        return 1
    r = m_admin.propose(substrate, profile, key, call, step="operator_propose_thaw", label="Assets.thaw_asset")
    _print_json({"action": "propose", "call_hash": call_hash(call), "receipt": r.as_dict()})
    return 0 if r.outcome.ok and "Multisig.NewMultisig" in r.event_names() else 1


def cmd_team(args: argparse.Namespace) -> int:
    """Operator (key A): propose set_team on asset 1 through M_mint (the owner) — executes only if the bot co-signs."""
    from .bot import operator_accounts
    from .multisig_ops import call_hash, pending

    try:
        profile, substrate, dep = _deployment_context(args)
        key = _key(profile, args.key, "BALLAST_OPERATOR_SURI", "//BallastA")
        issuer, admin, freezer = _addresses(profile, [args.issuer, args.admin, args.freezer])
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    m_mint, _ = operator_accounts(dep, substrate.ss58_format or 42)
    call = substrate.compose_call(call_module="Assets", call_function="set_team",
                                  call_params={"id": dep.breaker, "issuer": issuer, "admin": admin, "freezer": freezer})
    op = pending(substrate, m_mint.address, call_hash(call))
    if args.cancel:
        if op is None:
            _print_json({"action": "cancel", "result": "nothing pending", "call_hash": call_hash(call)})
            return 1
        r = m_mint.cancel(substrate, profile, key, op, step="operator_cancel_team", label="Assets.set_team")
        _print_json({"action": "cancel", "call_hash": op.call_hash, "receipt": r.as_dict()})
        return 0 if r.outcome.ok and "Multisig.MultisigCancelled" in r.event_names() else 1
    if op is not None:
        _print_json({"action": "propose", "result": "already pending", "call_hash": op.call_hash, "timepoint": op.timepoint})
        return 1
    r = m_mint.propose(substrate, profile, key, call, step="operator_propose_team", label="Assets.set_team")
    _print_json({"action": "propose", "call_hash": call_hash(call), "proposed": {"issuer": issuer, "admin": admin,
                 "freezer": freezer}, "receipt": r.as_dict()})
    return 0 if r.outcome.ok and "Multisig.NewMultisig" in r.event_names() else 1


def cmd_bot(args: argparse.Namespace) -> int:
    """Reserve bot (key B): co-sign the operator's pending mint / thaw only if the finalized reserve covers it."""
    from .bot import ReserveBot, parse_amount
    from .store import Store

    try:
        profile, substrate, dep = _deployment_context(args)
        key = _key(profile, args.key, "BALLAST_BOT_SURI", "//BallastB")
        providers = _providers(args, dep, bot_order=True)
        store = Store(args.db)
        max_age = getattr(args, "max_finalized_age", None)
        max_latest = getattr(args, "max_latest_age", None)
        if (max_age is not None and max_age < 0) or (max_latest is not None and max_latest < 0):
            raise ValueError("--max-finalized-age / --max-latest-age must be >= 0 (0 = off)")
        bot = ReserveBot(substrate=substrate, profile=profile, keypair=key, deployment=dep, providers=providers,
                         store=store, max_finalized_age_s=None if max_age == 0 else max_age,
                         max_latest_age_s=None if max_latest == 0 else max_latest,
                         log=lambda m: print(f"[{profile.name}] {m}", file=sys.stderr))
        if args.bot_command == "cosign-mint":
            amount = parse_amount(args.amount, dep.decimals)
            beneficiary = _addresses(profile, [args.beneficiary])[0]
        elif args.bot_command == "cosign-team":
            team = _addresses(profile, [args.issuer, args.admin, args.freezer])
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    try:
        if args.bot_command == "cosign-mint":
            out = bot.cosign_mint(amount, beneficiary)
        elif args.bot_command == "cosign-thaw":
            out = bot.cosign_thaw()
        elif args.bot_command == "cosign-team":
            out = bot.cosign_team(*team)
        else:
            from .attest import run_attester

            return run_attester(args, profile=profile, substrate=substrate, dep=dep, keypair=key,
                                providers=providers, store=store)
    finally:
        if args.bot_command != "attest":
            store.close()
    out["profile"] = profile.name
    _print_json(out)
    if out["decision"] == "signed-unknown":
        return 3
    if out["decision"] != "signed":
        return 1
    return 0 if out.get("executed_ok") else 3


def cmd_judge_reset(args: argparse.Namespace) -> int:
    """Before a demo: top the public judge account up to fees for --transfers transfers, then print what it holds."""
    from .chain import submit
    from .roles import JUDGE_URI
    from .watchdog import asset_state

    try:
        profile, substrate, dep = _deployment_context(args)
        funder = _key(profile, args.key, "BALLAST_FUNDER_SURI", "//Alice")
        judge = _addresses(profile, [args.judge or JUDGE_URI])[0]
        if args.transfers < 1:
            raise ValueError("--transfers must be >= 1")
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    transfer = substrate.compose_call(call_module="Assets", call_function="transfer",
                                      call_params={"id": dep.breaker, "target": judge, "amount": 1})
    fee = int(substrate.get_payment_info(call=transfer, keypair=funder)["partialFee"])
    ed = substrate.get_constant("Balances", "ExistentialDeposit").value
    target = ed + args.transfers * fee
    free = substrate.query("System", "Account", [judge]).value["data"]["free"]
    out: dict = {"profile": profile.name, "judge": judge, "fee_per_transfer": str(fee), "target_free": str(target),
                 "free_before": str(free)}
    if free < target:
        r = submit(substrate, profile, funder, "Balances", "transfer_keep_alive",
                   {"dest": judge, "value": target - free}, step="judge_reset")
        out["top_up"] = {"extrinsic_id": r.extrinsic_id, "outcome": str(r.outcome), "amount": str(target - free)}
        if not r.outcome.ok:
            _print_json(out)
            return 1
    head = substrate.get_block_hash(None)
    acct = substrate.query("Assets", "Account", [dep.breaker, judge], block_hash=head).value
    st = asset_state(dep.breaker, substrate.query("Assets", "Asset", [dep.breaker], block_hash=head).value)
    out |= {"free_after": str(substrate.query("System", "Account", [judge], block_hash=head).value["data"]["free"]),
            "asset": dep.breaker, "asset_status": st.status, "judge_asset_balance": str(acct["balance"] if acct else 0),
            "judge_account_status": str(acct["status"]) if acct else "none"}
    if not acct or acct["balance"] == 0:
        out["note"] = "the judge holds no asset 1: mint to it with `ballast mint` (operator) + `ballast bot cosign-mint`"
    _print_json(out)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    """Re-check every BALLAST/1 remark and asset-1 event of the deployment, on both chains."""
    from datetime import datetime, timezone

    from .receipts import EVIDENCE
    from .verify import Roles, Verifier, summary

    try:
        profile, substrate, dep = _deployment_context(args)
        providers = _providers(args, dep, bot_order=True)
        setup_steps = []
        if dep.setup_evidence and (EVIDENCE / dep.setup_evidence).exists():
            setup_steps = [st for st in json.loads((EVIDENCE / dep.setup_evidence).read_text())["steps"]
                           if st.get("receipt")]
        start = args.from_block
        if start is None:
            if not setup_steps:
                raise ValueError("no setup evidence for this deployment: pass --from")
            start = min(st["receipt"]["block_number"] for st in setup_steps)
        # control-asset events are expected only while the setup made asset 2 keyless
        control_settled_at = max((st["receipt"]["block_number"] for st in setup_steps
                                  if st["name"].startswith("asset 2") or "control asset 2" in st["name"]
                                  or st["name"].startswith("A creates asset 2")), default=0)
        end = args.to_block or substrate.get_block_number(None)
        if start > end:
            raise ValueError(f"--from {start} > --to {end}")
    except Exception as exc:  # noqa: BLE001
        print(f"ballast: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    quiet = args.json
    v = Verifier(substrate, Roles.from_deployment(dep), providers, dep.reserve["vault"], dep.reserve["erc20"],
                 log=(lambda s: None) if quiet else print, control_settled_at=control_settled_at)
    if not quiet:
        print(f"[{profile.name}] verify blocks #{start}..#{end} · asset {dep.breaker} · reserve {dep.reserve['label']}")
    findings = v.run(start, end)
    report = {"profile": profile.name, "chain": profile.label, "reserve": dep.reserve["label"], "from": start,
              "to": end, "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "summary": summary(findings), "findings": [f.as_dict() for f in findings]}
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(report, fh, indent=2, default=str)
            fh.write("\n")
    if quiet:
        print(json.dumps(report, default=str))
    else:
        sm = report["summary"]
        print(f"{sm['verdict']}: {sm['attestations_pass']}/{sm['attestations_counted']} B attestations PASS · "
              f"{sm['rejected']} REJECTED (not counted) · {sm['failures_or_flags']} FAIL/FLAGGED · {sm['counts']}")
    return 0 if report["summary"]["verdict"] == "PASS" else 1


def cmd_drill(args: argparse.Namespace) -> int:
    from .drill import run_drill

    return run_drill(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ballast", description="Reserve-gated circuit breaker on Portaldot.")
    parser.add_argument("--version", action="version", version=f"ballast {__version__}")
    parser.add_argument("--config", help="path to ballast.toml (default ./ballast.toml or $BALLAST_CONFIG)")
    parser.add_argument("--profile", help="chain profile: v3 | standin-upstream | standin-1002")
    parser.add_argument("--url", help="node URL (overrides ballast.toml)")
    sub = parser.add_subparsers(dest="command")
    chain = sub.add_parser("chain", help="identify the chain and derive H/K/W/N from its measured block time")
    chain.add_argument("--json", action="store_true")
    chain.add_argument("--no-measure", action="store_true", help="skip the block-time sample")
    chain.add_argument("--pallets", metavar="FILE", help="also write every pallet + call name to FILE (JSON)")
    chain.add_argument("--blocks", type=int, default=MIN_SAMPLE_BLOCKS, help="blocks to sample (>= 20)")
    chain.set_defaults(func=cmd_chain)
    from .sepolia import SEPOLIA_USDC

    res = sub.add_parser("reserves", help="read the vault's reserve-token balance from every EVM provider")
    res.add_argument("holder", help="address whose token balance is the reserve (the vault)")
    res.add_argument("--token", default=SEPOLIA_USDC, help="reserve token (default: Circle test USDC on Sepolia)")
    res.add_argument("--provider", action="append", metavar="NAME=URL",
                     help="EVM JSON-RPC provider, repeatable (default: Sepolia publicnode + drpc)")
    res.add_argument("--tag", action="append", choices=("latest", "safe", "finalized"),
                     help="block tag(s) to read (default: latest and finalized)")
    res.add_argument("--cross-check", nargs="?", const="finalized", choices=("latest", "safe", "finalized"),
                     help="pin one block and compare its hash + balance across all providers")
    res.add_argument("--timeout", type=float, default=10.0)
    res.add_argument("--json", action="store_true")
    res.add_argument("--out", metavar="FILE", help="also write the report as JSON")
    res.add_argument("--note", help="free-text label stored in the report (e.g. what the holder address is)")
    res.set_defaults(func=cmd_reserves)

    w = sub.add_parser("watch", help="run an OPERATOR watcher: freeze on reserve deficit (either provider) or "
                       "total provider outage (I6); the community-watcher rule is not implemented")
    w.add_argument("--breaker", type=int, required=True, help="asset id to freeze (asset 1)")
    w.add_argument("--supply-assets", required=True,
                   help="comma-separated ids of EVERY asset the reserve backs, incl. the breaker "
                   "(e.g. 1,2 = asset 1 + control asset 2: freeze when reserves < S1 + S2)")
    w.add_argument("--holder", required=True, help="vault address (holder of the reserve token)")
    w.add_argument("--token", default=SEPOLIA_USDC, help="reserve token (default: Circle test USDC on Sepolia)")
    w.add_argument("--provider", action="append", metavar="NAME=URL",
                   help="EVM provider, repeatable (default: Sepolia publicnode + drpc)")
    w.add_argument("--watcher", help="this watcher's key: //Dev URI on a stand-in (default //BallastW1); "
                   "elsewhere $BALLAST_WATCHER_SURI")
    w.add_argument("--watchers", default="//BallastW1,//BallastW2",
                   help="watcher-set members, comma-separated SS58 (or //Dev URIs on a stand-in)")
    w.add_argument("--threshold", type=int, default=1)
    w.add_argument("--poll-blocks", type=int, help="check every N Portaldot blocks (default: profile N)")
    w.add_argument("--poll-interval", type=float, default=1.0, help="seconds between head polls")
    w.add_argument("--fail-closed-after", type=float, default=300.0,
                   help="seconds with every provider unreachable before freezing (I6; default 300)")
    w.add_argument("--timeout", type=float, default=10.0, help="per-request EVM timeout (s)")
    w.add_argument("--max-block-age", type=float, default=120.0,
                   help="a provider whose latest block is older than this (s) counts as down; 0 = off "
                   "(only for an instant-mining local anvil, whose blocks exist only when a tx lands)")
    w.add_argument("--bot", help="reserve bot account (SS58, or //Dev on a stand-in): freeze if its nonce does not "
                   "move for K blocks (I8, heartbeat)")
    w.add_argument("--heartbeat-k", type=int, help="K in blocks (default: the profile's measured K = 3 x H)")
    w.add_argument("--until-frozen", action="store_true", help="exit 0 once the breaker asset is frozen")
    w.add_argument("--max-seconds", type=float, help="stop after this many seconds (exit 4 if --until-frozen)")
    w.add_argument("--log", metavar="FILE", help="append JSON-lines records to FILE")
    w.set_defaults(func=cmd_watch)

    def deployment_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--deployment", metavar="FILE", help="role-split manifest (default deployments/<profile>.json)")
        p.add_argument("--key", help="signer: //Dev URI on a stand-in; elsewhere the $BALLAST_*_SURI variable")

    m = sub.add_parser("mint", help="operator: propose a mint of asset 1 through M_mint (executes only if the "
                       "reserve bot co-signs)")
    m.add_argument("amount", help="decimal amount, e.g. 50.00")
    m.add_argument("beneficiary", help="SS58 address (or //Dev URI on a stand-in)")
    m.add_argument("--cancel", action="store_true", help="cancel the pending proposal (returns the deposit)")
    deployment_args(m)
    m.set_defaults(func=cmd_mint)

    t = sub.add_parser("thaw", help="operator: propose thaw_asset through M_admin (2-of-3)")
    t.add_argument("--cancel", action="store_true")
    deployment_args(t)
    t.set_defaults(func=cmd_thaw)

    tm = sub.add_parser("team", help="operator: propose set_team on asset 1 through M_mint (executes only if the "
                        "reserve bot co-signs: issuer stays M_mint, freezer unchanged)")
    tm.add_argument("--issuer", required=True)
    tm.add_argument("--admin", required=True)
    tm.add_argument("--freezer", required=True)
    tm.add_argument("--cancel", action="store_true")
    deployment_args(tm)
    tm.set_defaults(func=cmd_team)

    b = sub.add_parser("bot", help="reserve bot (key B): co-sign gated mints / thaws / team changes, post attestations")
    bsub = b.add_subparsers(dest="bot_command", required=True)
    bm = bsub.add_parser("cosign-mint", help="co-sign the pending mint iff finalized reserves >= S1 + S2 + amount "
                         "and asset 1 is not frozen (I7)")
    bm.add_argument("amount")
    bm.add_argument("beneficiary")
    bsub.add_parser("cosign-thaw", help="co-sign the pending thaw iff finality has passed the freeze and "
                    "finalized + latest reserves >= S1 + S2")
    bt = bsub.add_parser("cosign-team", help="co-sign the pending set_team iff the issuer stays M_mint and the "
                         "freezer is unchanged")
    bt.add_argument("--issuer", required=True)
    bt.add_argument("--admin", required=True)
    bt.add_argument("--freezer", required=True)
    ba = bsub.add_parser("attest", help="post BALLAST/1 attestations on change + a heartbeat every H blocks, "
                         "mirrored to ReserveOracle after each included remark")
    ba.add_argument("--heartbeat-blocks", type=int, help="H (default: the profile's measured H)")
    ba.add_argument("--poll-blocks", type=int, help="check every N blocks (default: the profile's N)")
    ba.add_argument("--no-oracle", action="store_true", help="do not mirror to ReserveOracle")
    ba.add_argument("--announce", action="store_true",
                    help="first post the one-off binding remarks: watcher set (t, members) and evm-attester")
    ba.add_argument("--max-seconds", type=float, help="stop after this many seconds")
    ba.add_argument("--max-posts", type=int, help="stop after this many remarks")
    ba.add_argument("--log", metavar="FILE", help="append JSON-lines records to FILE")
    for p in (bm, bsub.choices["cosign-thaw"], bt):
        p.add_argument("--max-finalized-age", type=float, default=3600.0,
                       help="refuse when the finalized reserve block is older than this (s; default 3600, 0 = off — "
                       "only for a local reserve chain that mines on demand)")
        p.add_argument("--max-latest-age", type=float, default=120.0,
                       help="refuse when the latest reserve block is older than this (s; default 120, 0 = off — "
                       "only for a local reserve chain that mines on demand)")
    for p in (bm, bsub.choices["cosign-thaw"], bt, ba):
        deployment_args(p)
        p.add_argument("--provider", action="append", metavar="NAME=URL",
                       help="EVM provider, repeatable (default: the manifest's, else Sepolia drpc + publicnode)")
        p.add_argument("--timeout", type=float, default=10.0, help="per-request EVM timeout (s)")
        p.add_argument("--db", default="ballast.db", help="SQLite decision log (default ballast.db)")
    b.set_defaults(func=cmd_bot)

    jr = sub.add_parser("judge-reset", help="before a demo: top up the public judge account's fees, print its holdings")
    jr.add_argument("--judge", help="judge account (SS58, or //Dev on a stand-in; default: the deployment's judge)")
    jr.add_argument("--transfers", type=int, default=20, help="fund fees for this many transfers (default 20)")
    deployment_args(jr)
    jr.set_defaults(func=cmd_judge_reset)

    v = sub.add_parser("verify", help="re-check every BALLAST/1 remark (per-type signers) and asset-1 event on both "
                       "chains; flags thaws without the bot, DISARMED teams, oracle posts without a remark")
    v.add_argument("--from", dest="from_block", type=int, help="first block (default: the role-split setup)")
    v.add_argument("--to", dest="to_block", type=int, help="last block (default: head)")
    v.add_argument("--provider", action="append", metavar="NAME=URL",
                   help="reserve-chain provider, repeatable (default: the manifest's, else Sepolia drpc + publicnode)")
    v.add_argument("--timeout", type=float, default=10.0)
    v.add_argument("--json", action="store_true")
    v.add_argument("--out", metavar="FILE", help="also write the report as JSON")
    deployment_args(v)
    v.set_defaults(func=cmd_verify)

    d = sub.add_parser("drill", help="breaker drill on a stand-in against a local anvil reserve")
    d.add_argument("--scenario", choices=("drain", "outage", "heartbeat"), default="drain",
                   help="drain: release 30%% of the vault; outage: every provider unreachable (fail-closed); "
                   "heartbeat: the bot never signs (I8)")
    d.add_argument("--heartbeat-k", type=int, default=10,
                   help="heartbeat scenario: K in blocks — a drill override; production K = 3 x H (profile)")
    d.add_argument("--evm-url", default="http://127.0.0.1:49545", help="local anvil (chain id 31337)")
    d.add_argument("--drain-pct", type=int, default=30)
    d.add_argument("--fail-closed-after", type=float, default=15.0,
                   help="outage scenario: watcher fail-closed timeout in seconds — a drill override; "
                   "the production default is 300 (I6)")
    d.add_argument("--timeout", type=float, default=180.0, help="max seconds to wait for the freeze")
    d.set_defaults(func=cmd_drill)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "command", None) == "reserves" and not args.tag:
        args.tag = ["latest", "finalized"]
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
