"""Signing keys by role name, per chain profile.

Stand-ins use the public dev URIs (`//BallastA`, `//Alice`, ...). On a real chain the same names resolve to secret
seed files outside the repo, one per role: `$BALLAST_KEY_DIR/<profile>-<role>.seed` (default `~/.config/ballast`),
mode 600, holding a mnemonic. `//Alice` is the funder (`v3-funder.seed`), `//BallastJudge//2037` is the judge seed with
a `//2037` derivation. A seed is never printed, logged or written anywhere but its own file.
"""

from __future__ import annotations

import os
import re
import stat
from pathlib import Path

from substrateinterface import Keypair

from .chain import dev_keypair
from .chain_profile import Profile, ProfileError

FUNDER_URI = "//Alice"
_URI = re.compile(r"^//(?:Ballast)?(?P<role>[A-Za-z][A-Za-z0-9]*)(?P<path>(?://[^/]+)*)$")


def key_dir() -> Path:
    return Path(os.environ.get("BALLAST_KEY_DIR", "~/.config/ballast")).expanduser()


def role_of(uri: str) -> tuple[str, str]:
    """`//BallastJudge//2037` -> ("judge", "//2037"); `//Alice` -> ("funder", "")."""
    if uri == FUNDER_URI:
        return "funder", ""
    m = _URI.match(uri)
    if not m or not uri.startswith("//Ballast"):
        raise ValueError(f"not a Ballast role URI: {uri!r}")
    return m["role"].lower(), m["path"]


def seed_path(profile: Profile, role: str) -> Path:
    return key_dir() / f"{profile.name}-{role}.seed"


def _read_seed(path: Path) -> str:
    if not path.exists():
        raise ProfileError(f"no seed file {path} (create it with scripts/v3_keys.py)")
    if stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ProfileError(f"{path} is readable by group/others; chmod 600 it")
    phrase = path.read_text().strip()
    if not phrase:
        raise ProfileError(f"{path} is empty")
    return phrase


def keypair(profile: Profile, uri: str, ss58_format: int = 42) -> Keypair:
    """The signer for a role URI: the dev key on a stand-in, the role's seed file on any other profile."""
    if profile.is_standin:
        return dev_keypair(profile, uri)
    role, path = role_of(uri)
    return Keypair.create_from_uri(_read_seed(seed_path(profile, role)) + path, ss58_format=ss58_format)


def create_seed(profile: Profile, role: str, ss58_format: int = 42) -> str:
    """Write a fresh mnemonic for `role` (refuses to overwrite) and return only its public address."""
    if profile.is_standin:
        raise ProfileError("stand-ins use dev URIs; no seed files")
    path = seed_path(profile, role)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    phrase = Keypair.generate_mnemonic()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(phrase + "\n")
    return Keypair.create_from_uri(phrase, ss58_format=ss58_format).ss58_address
