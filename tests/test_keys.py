import os

import pytest

from ballast.chain_profile import ProfileError, get_profile
from ballast.keys import create_seed, keypair, role_of, seed_path

V3 = get_profile("v3")


def test_role_uris_map_to_seed_names():
    assert role_of("//Alice") == ("funder", "")
    assert role_of("//BallastA2") == ("a2", "")
    assert role_of("//BallastJudge//2037") == ("judge", "//2037")
    with pytest.raises(ValueError):
        role_of("//Bob")


def test_standin_keeps_dev_uris(monkeypatch, tmp_path):
    monkeypatch.setenv("BALLAST_KEY_DIR", str(tmp_path))
    kp = keypair(get_profile("standin-upstream"), "//BallastA")
    assert kp.ss58_address.startswith("5") and not list(tmp_path.iterdir())


def test_v3_seed_files_are_created_600_and_never_overwritten(monkeypatch, tmp_path):
    monkeypatch.setenv("BALLAST_KEY_DIR", str(tmp_path))
    addr = create_seed(V3, "a")
    path = seed_path(V3, "a")
    assert path.name == "v3-a.seed" and (path.stat().st_mode & 0o777) == 0o600
    assert keypair(V3, "//BallastA").ss58_address == addr
    assert keypair(V3, "//BallastA//x").ss58_address != addr  # derivation path applies
    with pytest.raises(FileExistsError):
        create_seed(V3, "a")


def test_v3_refuses_missing_or_loose_seed(monkeypatch, tmp_path):
    monkeypatch.setenv("BALLAST_KEY_DIR", str(tmp_path))
    with pytest.raises(ProfileError, match="no seed file"):
        keypair(V3, "//BallastB")
    create_seed(V3, "b")
    os.chmod(seed_path(V3, "b"), 0o644)
    with pytest.raises(ProfileError, match="chmod 600"):
        keypair(V3, "//BallastB")


def test_cli_keys_on_v3_use_env_then_role_seed(monkeypatch, tmp_path):
    from ballast.cli import _key, _watcher_key

    monkeypatch.setenv("BALLAST_KEY_DIR", str(tmp_path))
    monkeypatch.delenv("BALLAST_OPERATOR_SURI", raising=False)
    monkeypatch.delenv("BALLAST_WATCHER_SURI", raising=False)
    a, w1 = create_seed(V3, "a"), create_seed(V3, "w1")
    assert _key(V3, None, "BALLAST_OPERATOR_SURI", "//BallastA").ss58_address == a
    assert _key(V3, "//BallastA", "BALLAST_OPERATOR_SURI", "//BallastB").ss58_address == a
    assert _watcher_key(V3, None).ss58_address == w1
    monkeypatch.setenv("BALLAST_OPERATOR_SURI", "//Explicit")
    assert _key(V3, None, "BALLAST_OPERATOR_SURI", "//BallastA").ss58_address != a
