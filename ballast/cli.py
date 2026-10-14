"""`ballast` command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .chain_profile import MIN_SAMPLE_BLOCKS, ProfileError, identify
from .config import load_chain_config
from .rpc import HttpRpc, RpcError


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
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=not args.no_measure, sample_blocks=args.blocks)
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
    from .sepolia import SEPOLIA_PROVIDERS, chain_id, compare, cross_check, providers_from, read_all

    try:
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

    if args.max_block_age < 0 or args.fail_closed_after < 0 or args.poll_interval < 0 or args.timeout <= 0:
        print("ballast: --max-block-age / --fail-closed-after / --poll-interval must be >= 0, --timeout > 0",
              file=sys.stderr)
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
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=args.poll_blocks is None)
        poll_blocks = args.poll_blocks
        if poll_blocks is None:
            if ident.counts is None:
                raise ProfileError("block time not measured: pass --poll-blocks")
            poll_blocks = ident.counts.poll_n
        keypair = _watcher_key(ident.profile, args.watcher)
        watchers = _addresses(ident.profile, args.watchers.split(","))
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
        dog = Watchdog(substrate=substrate, profile=ident.profile, head_rpc=HttpRpc(cfg.url),
                       keypair=keypair, providers=providers, cfg=wcfg, log=log)
        try:
            pre = dog.preflight()
        except Exception as exc:  # noqa: BLE001 — any preflight failure means "cannot freeze": say so, exit 2
            log("not-armed", message=f"{type(exc).__name__}: {exc}" if not isinstance(exc, RuntimeError) else str(exc))
            return 2
        log.context["reserve"] = pre["reserve"]
        log("start", **pre, poll_blocks=poll_blocks, fail_closed_after=args.fail_closed_after,
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
    w.add_argument("--until-frozen", action="store_true", help="exit 0 once the breaker asset is frozen")
    w.add_argument("--max-seconds", type=float, help="stop after this many seconds (exit 4 if --until-frozen)")
    w.add_argument("--log", metavar="FILE", help="append JSON-lines records to FILE")
    w.set_defaults(func=cmd_watch)

    d = sub.add_parser("drill", help="breaker drill on a stand-in against a local anvil reserve")
    d.add_argument("--scenario", choices=("drain", "outage"), default="drain",
                   help="drain: release 30%% of the vault; outage: every provider unreachable (fail-closed)")
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
