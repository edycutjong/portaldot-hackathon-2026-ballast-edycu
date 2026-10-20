"""`ballast.toml` loader."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .chain_profile import Profile, ProfileError, get_profile


@dataclass(frozen=True)
class ChainConfig:
    profile: Profile
    url: str


def load_chain_config(path: str | os.PathLike | None = None, *, profile: str | None = None, url: str | None = None) -> ChainConfig:
    """Explicit arguments win, then `ballast.toml` ([chain] profile/url), then the profile's default URL.

    The file's url is used only for the file's own profile (or when the file names none)."""
    data: dict = {}
    cfg_path = Path(path or os.environ.get("BALLAST_CONFIG", "ballast.toml"))
    if cfg_path.exists():
        try:
            with cfg_path.open("rb") as fh:
                data = tomllib.load(fh).get("chain", {})
        except tomllib.TOMLDecodeError as exc:
            raise ProfileError(f"{cfg_path}: {exc}") from None
    name = profile or data.get("profile")
    if not name:
        raise ProfileError(f"no chain profile: pass --profile or set [chain] profile in {cfg_path}")
    prof = get_profile(name)
    # ballast.toml's url belongs to ballast.toml's profile: `--profile v3` must not inherit a stand-in's localhost URL.
    file_url = data.get("url") if data.get("profile") in (None, name) else None
    return ChainConfig(profile=prof, url=url or file_url or prof.default_url)
