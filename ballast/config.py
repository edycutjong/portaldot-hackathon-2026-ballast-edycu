"""`ballast.toml` loader."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .chain_profile import Profile, get_profile


@dataclass(frozen=True)
class ChainConfig:
    profile: Profile
    url: str


def load_chain_config(path: str | os.PathLike | None = None, *, profile: str | None = None, url: str | None = None) -> ChainConfig:
    """Explicit arguments win, then `ballast.toml` ([chain] profile/url), then the profile's default URL."""
    data: dict = {}
    cfg_path = Path(path or os.environ.get("BALLAST_CONFIG", "ballast.toml"))
    if cfg_path.exists():
        with cfg_path.open("rb") as fh:
            data = tomllib.load(fh).get("chain", {})
    name = profile or data.get("profile")
    if not name:
        raise SystemExit(f"no chain profile: pass --profile or set [chain] profile in {cfg_path}")
    prof = get_profile(name)
    return ChainConfig(profile=prof, url=url or data.get("url") or prof.default_url)
