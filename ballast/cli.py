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
    down = all(r["error"] for comp in report["tags"].values() for r in comp["readings"])
    disagree = any(comp["disagreements"] for comp in report["tags"].values())
    if args.cross_check and not report["cross_check"]["agree"]:
        disagree = True
    return 3 if down else (1 if disagree else 0)


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
    res.set_defaults(func=cmd_reserves)
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
