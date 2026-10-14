"""`ballast` command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .chain_profile import MIN_SAMPLE_BLOCKS, ProfileError, identify
from .config import load_chain_config
from .rpc import HttpRpc


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
    cfg = load_chain_config(args.config, profile=args.profile, url=args.url)
    try:
        ident = identify(HttpRpc(cfg.url), cfg.profile.name, measure=not args.no_measure, sample_blocks=args.blocks)
    except ProfileError as exc:
        print(f"ballast: {exc}", file=sys.stderr)
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
            f"  blocks    {counts['block_time_ms']:.0f} ms mean over {counts['measured_over_blocks']} blocks "
            f"-> H={counts['H']} K={counts['K']} W={counts['W']} N={counts['N']}"
        )
    else:
        print(f"  blocks    {counts}")
    for note in ident.notes:
        print(f"  note      {note}")
    return 0


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
