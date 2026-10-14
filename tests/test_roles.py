import hashlib

import pytest
from substrateinterface import Keypair

from ballast.multisig import multi_address, public_key
from ballast.roles import Deployment, RoleMap, audit_team, keyless_account

A, A2, B, W1, W2 = (Keypair.create_from_uri(f"//Ballast{n}").ss58_address for n in ("A", "A2", "B", "W1", "W2"))


def rm() -> RoleMap:
    return RoleMap(a=A, a2=A2, b=B, watchers=(W1, W2))


def test_multisig_addresses_follow_the_role_map():
    m = rm()
    assert m.m_mint == multi_address([A, B], 2)
    assert m.m_admin == multi_address([B, A2, A], 2)  # order-independent
    assert m.m_watch == multi_address([W1, W2], 1)
    assert len({m.m_mint, m.m_admin, m.m_watch}) == 3


def test_breaker_team_owner_and_issuer_are_m_mint():
    team = rm().breaker_team()
    assert team["owner"] == team["issuer"] == rm().m_mint
    assert team["admin"] == rm().m_admin and team["freezer"] == rm().m_watch


def test_keyless_accounts_are_publicly_recomputable():
    assert keyless_account("owner") == hashlib.blake2b(b"ballast:a2-owner:v1", digest_size=32).digest()
    assert len({keyless_account(r) for r in ("owner", "issuer", "admin", "freezer")}) == 4
    with pytest.raises(ValueError):
        keyless_account("minter")


def test_role_map_refuses_shared_keys_and_threshold_above_one():
    with pytest.raises(ValueError):
        RoleMap(a=A, a2=A, b=B, watchers=(W1,))
    with pytest.raises(ValueError):
        RoleMap(a=A, a2=A2, b=B, watchers=(W1, W2), watch_threshold=2)
    with pytest.raises(ValueError):
        RoleMap(a=A, a2=A2, b=B, watchers=())


def test_audit_team_names_every_changed_role():
    m = rm()
    good = {"owner": m.m_mint, "issuer": m.m_mint, "admin": m.m_admin, "freezer": m.m_watch}
    assert audit_team(good, m.breaker_team()) == []
    disarmed = good | {"freezer": A}  # A + B re-teamed the freezer to A
    problems = audit_team(disarmed, m.breaker_team())
    assert len(problems) == 1 and problems[0].startswith("freezer is ")
    assert audit_team(None, m.breaker_team()) == ["asset does not exist"]


def test_deployment_round_trip_and_tamper_check(tmp_path):
    m = rm()
    d = Deployment(profile="standin-upstream", genesis_hash="0x00", breaker=1, control=2, decimals=6, s2=50,
                   roles=m.as_dict(), reserve={"vault": "0x" + "11" * 20})
    path = d.save(tmp_path / "standin-upstream.json")
    loaded = Deployment.load("standin-upstream", path)
    assert public_key(loaded.role_map().m_mint) == public_key(m.m_mint)
    with pytest.raises(ValueError):
        Deployment.load("v3", path)
    loaded.roles["M_mint"]["address"] = m.m_admin
    with pytest.raises(ValueError):
        loaded.role_map()
