#!/usr/bin/env python3
"""Create the role seed files for a real-chain profile (default v3) and print their PUBLIC addresses only.

  python scripts/v3_keys.py [--profile v3]

Seeds go to $BALLAST_KEY_DIR/<profile>-<role>.seed (default ~/.config/ballast), mode 600, never into the repo.
An existing seed file is kept as is (its address is printed). The funder seed is the human's and is never created here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ballast.chain_profile import get_profile  # noqa: E402
from ballast.keys import create_seed, keypair, seed_path  # noqa: E402

ROLES = {"a": "//BallastA", "a2": "//BallastA2", "b": "//BallastB", "w1": "//BallastW1", "w2": "//BallastW2",
         "judge": "//BallastJudge", "peer": "//BallastPeer"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--profile", default="v3")
    args = ap.parse_args()
    profile = get_profile(args.profile)
    if profile.is_standin:
        print(f"v3_keys: {profile.name} is a stand-in; it uses public dev URIs", file=sys.stderr)
        return 2
    print(f"funder  {keypair(profile, '//Alice').ss58_address}  ({seed_path(profile, 'funder')})")
    for role, uri in ROLES.items():
        if seed_path(profile, role).exists():
            print(f"{role:7} {keypair(profile, uri).ss58_address}  (kept)")
        else:
            print(f"{role:7} {create_seed(profile, role)}  (new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
