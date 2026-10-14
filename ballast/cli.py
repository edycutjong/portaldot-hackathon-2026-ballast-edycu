"""`ballast` command-line entry point."""

import argparse
import sys

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ballast", description=__doc__)
    parser.add_argument("--version", action="version", version=f"ballast {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
