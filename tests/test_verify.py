"""`ballast verify` rules (offline): per-type signers (I5), thaw / team / owner flags (I4), oracle mirror (I10)."""

from substrateinterface import Keypair

from ballast.attest import Snapshot
from ballast.multisig import multi_address
from ballast.remarks import parse
from ballast.verify import Roles, Verifier, signer_verdict, summary

K = {n: Keypair.create_from_uri(f"//Ballast{n}").ss58_address for n in ("A", "A2", "B", "W1", "W2", "Judge")}
ROLES = Roles(b=K["B"], a=K["A"], a2=K["A2"], m_mint=multi_address([K["A"], K["B"]], 2),
              m_admin=multi_address([K["A"], K["A2"], K["B"]], 2), m_watch=multi_address([K["W1"], K["W2"]], 1),
              watchers=[K["W1"], K["W2"]], breaker=1, control=2, oracle="0x" + "ee" * 20)
H = "0x" + "ab" * 32


def test_attestations_only_from_b():
    assert signer_verdict("attest", K["B"], ROLES, lambda: False)[0]
    assert signer_verdict("heartbeat", K["B"], ROLES, lambda: False)[0]
    for who in ("A", "W1", "Judge"):
        assert not signer_verdict("attest", K[who], ROLES, lambda: False)[0]


def test_per_type_signers():
    assert signer_verdict("freeze", K["W2"], ROLES, lambda: False)[0]
    assert not signer_verdict("freeze", K["B"], ROLES, lambda: False)[0]
    assert signer_verdict("override", K["A2"], ROLES, lambda: False)[0]
    assert signer_verdict("override", ROLES.m_admin, ROLES, lambda: False)[0]
    assert not signer_verdict("override", K["B"], ROLES, lambda: False)[0]
    assert signer_verdict("redeem", K["Judge"], ROLES, lambda: True)[0]
    assert not signer_verdict("redeem", K["Judge"], ROLES, lambda: False)[0]
    assert not signer_verdict("mint", K["B"], ROLES, lambda: True)[0]  # unknown type


def verifier() -> Verifier:
    return Verifier(substrate=None, roles=ROLES, providers=[], vault="0x" + "11" * 20, erc20="0x" + "22" * 20)


def test_forged_attestation_is_rejected_not_counted():
    v = verifier()
    snap = Snapshot(a=1, a2=2, s=5, s2=5, frozen=False, pb=10, ph=H, eb=3, eh=H, r=10)
    rem = {"extrinsic_id": "11-1", "block_number": 11, "block_hash": H, "sender": K["Judge"],
           "text": snap.remark("attest")}
    f = v.check_remark(rem)
    assert f.verdict == "REJECTED" and "I5" in f.detail
    s = summary([f])
    # nothing counted -> EMPTY, never a PASS (M5)
    assert s["rejected"] == 1 and s["attestations_counted"] == 0 and s["verdict"] == "EMPTY"


def test_other_assets_are_ignored():
    rem = {"extrinsic_id": "11-1", "block_number": 11, "block_hash": H, "sender": K["W2"],
           "text": "BALLAST/1|freeze|a=2037|reason=no-heartbeat"}
    assert verifier().check_remark(rem).verdict == "IGNORED"


def thaw(approving, overrides=()):
    v = verifier()
    v.overrides = list(overrides)
    execs = [{"multisig": ROLES.m_admin, "approving": approving, "result": {"Ok": []}}]
    v._asset_event("20-2", 20, "AssetThawed", {"asset_id": 1}, execs)
    return v.findings[-1]


def test_malformed_remark_from_b_fails_from_others_is_rejected():
    rem = {"extrinsic_id": "11-1", "block_number": 11, "block_hash": H, "sender": K["B"], "text": "BALLAST/1|attest|s"}
    assert verifier().check_remark(rem).verdict == "FAIL"
    assert verifier().check_remark(rem | {"sender": K["Judge"]}).verdict == "REJECTED"


def test_summary_verdicts():
    from ballast.verify import Finding

    ok = Finding("12-1", 12, "attest", "PASS", "")
    assert summary([ok])["verdict"] == "PASS"
    assert summary([ok, Finding("13-1", 13, "thaw", "FLAGGED", "")])["verdict"] == "FAIL"
    assert summary([Finding("13-1", 13, "team", "OK", "")])["verdict"] == "EMPTY"


def test_each_override_justifies_one_thaw():
    v = verifier()
    v.overrides = [15]
    execs = [{"multisig": ROLES.m_admin, "approving": K["A2"], "result": {"Ok": []}}]
    v._asset_event("20-2", 20, "AssetThawed", {"asset_id": 1}, execs)
    v._asset_event("30-2", 30, "AssetThawed", {"asset_id": 1}, execs)
    assert [f.verdict for f in v.findings] == ["OK", "FLAGGED"] and v.overrides == []


def test_admin_change_is_disarmed():
    v = verifier()
    v._asset_event("5-2", 5, "TeamChanged", {"asset_id": 1, "issuer": ROLES.m_mint, "admin": K["A"],
                                              "freezer": ROLES.m_watch}, [])
    assert v.findings[-1].verdict == "FLAGGED" and "admin" in v.findings[-1].detail


def test_control_asset_changes_flagged_only_after_setup():
    v = Verifier(substrate=None, roles=ROLES, providers=[], vault="0x" + "11" * 20, erc20="0x" + "22" * 20,
                 control_settled_at=100)
    ev = [{"module_id": "Assets", "event_id": "Issued", "attributes": {"asset_id": 2}, "extrinsic_idx": 1}]
    v.check_events(90, H, ev, [])
    assert v.findings == []  # the setup's own S2 mint
    v.check_events(150, H, ev, [])
    assert v.findings[-1].verdict == "FLAGGED" and v.findings[-1].kind == "control"


class Rpc:
    def __init__(self, name, number, balance):
        self.name, self.number, self.balance = name, number, balance

    def call(self, method, params):
        if method == "eth_getBlockByHash":
            return {"number": hex(self.number)}
        return f"0x{self.balance:064x}"


def test_reserve_at_asks_every_provider():
    v = Verifier(substrate=None, roles=ROLES, providers=[Rpc("a", 3, 10), Rpc("b", 3, 10)], vault="0x" + "11" * 20,
                 erc20="0x" + "22" * 20)
    assert v.reserve_at(H) == (3, 10, "a+b")
    v.providers = [Rpc("a", 3, 10), Rpc("b", 3, 11)]
    n, b, why = v.reserve_at(H)
    assert n is None and why.startswith("DISAGREE")


def test_thaw_ok_only_with_the_bot_or_an_override():
    assert thaw(K["B"]).verdict == "OK"
    assert thaw(K["A2"]).verdict == "FLAGGED"  # A + A2 emergency path, silent
    assert thaw(K["A2"], overrides=[15]).verdict == "OK"
    v = verifier()
    v._asset_event("20-2", 20, "AssetThawed", {"asset_id": 1}, [])  # not through M_admin at all
    assert v.findings[-1].verdict == "FLAGGED"


def test_team_and_owner_flagged_on_what_changed():
    v = verifier()
    v._asset_event("5-2", 5, "TeamChanged", {"asset_id": 1, "issuer": ROLES.m_mint, "admin": ROLES.m_admin,
                                              "freezer": ROLES.m_watch}, [])
    v._asset_event("6-2", 6, "TeamChanged", {"asset_id": 1, "issuer": ROLES.m_mint, "admin": ROLES.m_admin,
                                              "freezer": K["A"]}, [])
    v._asset_event("7-2", 7, "OwnerChanged", {"asset_id": 1, "owner": K["A"]}, [])
    assert [f.verdict for f in v.findings] == ["OK", "FLAGGED", "FLAGGED"]
    assert "DISARMED" in v.findings[1].detail


def posted(**kw):
    p = {"s1": 5, "s2": 5, "reserves": 10, "sep_block": 3, "sep_hash": H, "pd_block": 10, "frozen": False}
    return p | kw


def test_oracle_post_must_follow_a_matching_attestation():
    v = verifier()
    snap = Snapshot(a=1, a2=2, s=5, s2=5, frozen=False, pb=10, ph=H, eb=3, eh=H, r=10)
    v.attested[10] = {"fields": parse(snap.remark("attest")), "block": 11, "extrinsic_id": "11-2"}
    v.check_posted([("12-2", 12, posted()), ("13-2", 13, posted(reserves=11)), ("10-2", 10, posted()),
                    ("14-2", 14, posted(pd_block=99))])
    assert [f.verdict for f in v.findings] == ["OK", "FLAGGED", "FLAGGED", "FLAGGED"]
    assert "leads" in v.findings[2].detail and "I10" in v.findings[3].detail
