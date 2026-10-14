import hashlib
from functools import lru_cache
from pathlib import Path

import pytest

from ballast.chain_profile import get_profile
from ballast.metadata import load_metadata

FIXTURES = Path(__file__).parent / "fixtures"
EVIDENCE = Path(__file__).parent.parent / "evidence"


def fixture_sha256(name: str) -> str:
    return hashlib.sha256((FIXTURES / name).read_bytes()).hexdigest()


def pinned_sums() -> dict[str, str]:
    sums = {}
    for line in (FIXTURES / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split()
        sums[name] = digest
    return sums


@lru_cache(maxsize=None)
def _metadata(profile_name: str, patched: bool = True):
    profile = get_profile(profile_name)
    if not patched:
        from dataclasses import replace

        profile = replace(profile, patch_assets_u64=False)
    name = f"{profile_name}-metadata.scale"
    assert fixture_sha256(name) == pinned_sums()[name], f"{name} does not match SHA256SUMS"
    return load_metadata((FIXTURES / name).read_bytes(), profile)


@pytest.fixture(scope="session")
def upstream_md():
    return _metadata("standin-upstream")


@pytest.fixture
def md_1002():
    # Not cached across tests: the 1002 patch mutates metadata in place.
    _metadata.cache_clear()
    return _metadata("standin-1002", patched=False)
