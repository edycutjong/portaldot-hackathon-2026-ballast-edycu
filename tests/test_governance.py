"""Governance branches: announced rotations, the wind-down thaw gate, the redemption gate, the role-map admin set."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest
from substrateinterface import Keypair

from ballast.governance import (
    Posted,
    announcement_of,
    announcement_text,
    final_text,
    holders,
    redeem_gate,
    redeem_id,
    redeem_text,
    rotation_gate,
    winddown_gate,
    winddown_hold,
)
from ballast.multisig import multi_address
from ballast.remarks import parse
from ballast.roles import RoleMap

A, A2, A3, B, W1, W2, W3, J, P = (Keypair.create_from_uri(f"//Gov{n}").ss58_address
                                  for n in ("A", "A2", "A3", "B", "W1", "W2", "W3", "J", "P"))
M_MINT = multi_address([A, B], 2)
M_ADMIN = multi_address([A, A2, B], 2)
M_WATCH = multi_address([W1, W2], 1)
M_WATCH2 = multi_address([W1, W2, W3], 1)
M_ADMIN2 = multi_address([A, A3, B], 2)
CURRENT = {"issuer": M_MINT, "admin": M_ADMIN, "freezer": M_WATCH}
EVM = "0x" + "ab" * 20


def posted(text: str, block: int = 100, signer: str = B, sender: str | None = None, idx: int = 1) -> Posted:
    return Posted(f"{block}-{idx}", block, signer, sender or signer, text, parse(text))


def ann(kind="watchers", members=(W1, W2, W3), t=1, asset=7, block=100, signer=B):
    return announcement_of(posted(announcement_text(kind, asset, t, list(members)), block, signer))


def gate(proposed, announcement=None, head=200, k=10):
    return rotation_gate(CURRENT, proposed, breaker=7, m_mint=M_MINT, m_admin=M_ADMIN, b=B,
                         announcement=announcement, head=head, k=k)


# --- rotation ---------------------------------------------------------------------------------------------------
def test_unchanged_team_falls_back_to_the_plain_gate():
    assert gate(dict(CURRENT)) is None


def test_watcher_rotation_signs_after_k_blocks():
    sign, why = gate(CURRENT | {"freezer": M_WATCH2}, ann(), head=110, k=10)
    assert sign and "100-1" in why and ">= K = 10" in why


def test_watcher_rotation_refused_without_announcement():
    sign, why = gate(CURRENT | {"freezer": M_WATCH2})
    assert not sign and "without an announcement" in why


def test_watcher_rotation_refused_before_k_blocks():
    sign, why = gate(CURRENT | {"freezer": M_WATCH2}, ann(), head=109, k=10)
    assert not sign and "9 blocks ago < K = 10" in why


def test_rotation_refused_when_the_address_is_not_the_announced_set():
    sign, why = gate(CURRENT | {"freezer": multi_address([W1, W3], 1)}, ann())
    assert not sign and "not the announced set's address" in why


@pytest.mark.parametrize("kw,needle", [
    ({"signer": A}, "not the bot key B"),
    ({"asset": 8}, "for asset 8"),
    ({"kind": "admins", "members": (A, A3, B), "t": 2}, "announces admins"),
])
def test_rotation_refused_on_a_wrong_announcement(kw, needle):
    sign, why = gate(CURRENT | {"freezer": M_WATCH2}, ann(**kw))
    assert not sign and needle in why


def test_watcher_set_must_be_one_of_n():
    two = multi_address([W1, W2, W3], 2)
    sign, why = gate(CURRENT | {"freezer": two}, ann(t=2))
    assert not sign and "1-of-N" in why


def test_admin_rotation_signs_with_b_in_the_set():
    sign, why = gate(CURRENT | {"admin": M_ADMIN2}, ann("admins", (A, A3, B), 2))
    assert sign and "admins set" in why


@pytest.mark.parametrize("members,t", [((A, A2, A3), 2), ((A, A3, B), 1)])
def test_admin_rotation_refused_without_b_or_below_two(members, t):
    sign, why = gate(CURRENT | {"admin": multi_address(list(members), t)}, ann("admins", members, t))
    assert not sign and "must include B" in why


def test_one_role_per_rotation_and_issuer_stays():
    sign, why = gate({"issuer": M_MINT, "admin": M_ADMIN2, "freezer": M_WATCH2}, ann())
    assert not sign and "both change" in why
    sign, why = gate(CURRENT | {"issuer": A}, ann())
    assert not sign and "issuer must stay" in why


def test_watcher_rotation_keeps_the_manifest_admin():
    current = CURRENT | {"admin": M_ADMIN2}  # on chain the admin already moved, the manifest still says M_ADMIN
    sign, why = rotation_gate(current, current | {"freezer": M_WATCH2}, breaker=7, m_mint=M_MINT, m_admin=M_ADMIN,
                              b=B, announcement=ann(), head=200, k=10)
    assert not sign and "admin must stay" in why


def test_announcement_texts_round_trip_and_reject_duplicates():
    a = ann()
    assert a.address == M_WATCH2 and a.members == (W1, W2, W3) and a.threshold == 1
    with pytest.raises(ValueError):
        announcement_text("watchers", 7, 1, [W1, W1])
    with pytest.raises(ValueError):
        announcement_text("owners", 7, 1, [W1])
    with pytest.raises(ValueError):
        announcement_of(posted(final_text(7, "0.5")))


# --- wind-down --------------------------------------------------------------------------------------------------
def rows(*spec):
    return [{"who": who, "balance": bal, "status": "Frozen" if fr else "Liquid", "frozen": fr} for who, bal, fr in spec]


def test_winddown_hold_only_when_every_holder_with_a_balance_is_frozen():
    assert winddown_hold(rows((J, 30, True), (P, 20, True), (W1, 0, False)))
    assert not winddown_hold(rows((J, 30, True), (P, 20, False)))
    assert not winddown_hold(rows((W1, 0, False)))


def wd(frozen=True, final=None, r=rows((J, 30, True), (P, 20, True)), freeze_block=50, w=20):
    final = posted(final_text(7, "0.7"), block=80) if final is None else final
    return winddown_gate(frozen, final, r, breaker=7, b=B, freeze_block=freeze_block, w=w)


def test_winddown_gate_signs_when_final_and_all_frozen():
    sign, why = wd()
    assert sign and "r=0.7000" in why and "2 holders" in why


@pytest.mark.parametrize("kw,needle", [
    ({"frozen": False}, "not frozen"),
    ({"r": rows((J, 30, True), (P, 20, False))}, "1 of 2 holders"),
    ({"final": posted(final_text(7, "0.7"), block=80, signer=A)}, "not signed by the bot"),
    ({"final": posted(final_text(8, "0.7"), block=80)}, "not a final remark for asset 7"),
    ({"w": 31}, "< W = 31"),
    ({"freeze_block": None}, "could not be located"),
    ({"r": rows((J, 0, False))}, "no holder has a balance"),
])
def test_winddown_gate_refusals(kw, needle):
    sign, why = wd(**kw)
    assert not sign and needle in why


def test_final_text_rejects_a_haircut_of_one_or_more():
    with pytest.raises(ValueError):
        final_text(7, Decimal("1"))
    assert final_text(7, "0.7") == "BALLAST/1|final|a=7|r=0.7000"


def rg(request=None, row=None, frozen=False, amount=30):
    request = posted(redeem_text(7, EVM), block=90, signer=J) if request is None else request
    row = rows((J, 30, True))[0] if row is None else row
    return redeem_gate(request, posted(final_text(7, "0.7"), block=80), row, frozen, breaker=7, b=B, holder=J,
                       amount=amount)


def test_redeem_gate_signs_a_holder_request_for_the_whole_balance():
    sign, why = rg()
    assert sign and "release r x amount = 21 to" in why


@pytest.mark.parametrize("kw,needle", [
    ({"request": posted(redeem_text(7, EVM), block=90, signer=P)}, "not signed by the holder"),
    ({"frozen": True}, "still frozen"),
    ({"amount": 10}, "whole balance"),
    ({"row": rows((J, 30, False))[0]}, "not individually frozen"),
    ({"row": rows((J, 0, True))[0]}, "holds nothing"),
    ({"request": posted(final_text(7, "0.7"), block=90, signer=J)}, "not a redeem request"),
])
def test_redeem_gate_refusals(kw, needle):
    sign, why = rg(**kw)
    assert not sign and needle in why


def test_redeem_id_is_32_bytes_and_bound_to_the_request():
    assert len(redeem_id("90-1")) == 32 and redeem_id("90-1") != redeem_id("90-2")
    with pytest.raises(ValueError):
        redeem_text(7, "0x1234")


def test_holders_reads_status_enums():
    sub = SimpleNamespace(query_map=lambda *a, **k: [
        (SimpleNamespace(value=J), SimpleNamespace(value={"balance": 5, "status": "Frozen"})),
        (SimpleNamespace(value=P), SimpleNamespace(value={"balance": 7, "status": {"Liquid": None}})),
    ])
    out = holders(sub, 7)
    assert [(h["who"], h["frozen"]) for h in out] == [(J, True), (P, False)]


# --- the role map after an admin rotation -----------------------------------------------------------------------
def test_role_map_takes_a_rotated_admin_set():
    rm = RoleMap(a=A, a2=A2, b=B, watchers=(W1, W2, W3), admins=(A, A3, B))
    assert rm.m_admin == M_ADMIN2 and rm.m_watch == M_WATCH2 and rm.admin_proposers == [A, A3]
    assert rm.as_dict()["admins"] == [A, A3, B] and rm.as_dict()["M_admin"]["signatories"] == ["A", A3, "B"]
    assert "admins" not in RoleMap(a=A, a2=A2, b=B, watchers=(W1,)).as_dict()


@pytest.mark.parametrize("admins,t", [((A, A2, A3), 2), ((A, B), 1), ((A, B), 3)])
def test_role_map_refuses_an_admin_set_without_b_or_two_keys(admins, t):
    with pytest.raises(ValueError):
        RoleMap(a=A, a2=A2, b=B, watchers=(W1,), admins=admins, admin_threshold=t)
