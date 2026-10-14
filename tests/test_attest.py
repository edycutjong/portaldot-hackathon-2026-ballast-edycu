from ballast.attest import Snapshot, due, snapshot_from_fields
from ballast.remarks import MAX_BYTES, parse

H = "0x" + "ab" * 32


def snap(**kw) -> Snapshot:
    base = dict(a=1, a2=2, s=51_000_000, s2=50_000_000, frozen=False, pb=4300, ph=H, eb=201, eh=H, r=101_000_000)
    return Snapshot(**(base | kw))


def test_remark_round_trips_through_the_parser():
    text = snap().remark("attest")
    f = parse(text)
    assert f["type"] == "attest" and snapshot_from_fields(f) == snap()
    assert parse(snap(frozen=True).remark("heartbeat"))["f"] == "1"


def test_remark_fits_the_budget_at_u64_supplies_and_u128_reserves():
    big = snap(a=2**32 - 1, a2=2**32 - 2, s=2**64 - 1, s2=2**64 - 1, pb=99_999_999, eb=99_999_999, r=2**128 - 1)
    assert len(big.remark("heartbeat").encode()) <= MAX_BYTES


def test_first_post_and_every_change_is_an_attestation():
    assert due(None, None, snap(), 10, 200) == "attest"
    for change in ({"s": 1}, {"s2": 1}, {"frozen": True}, {"r": 1}):
        assert due(snap().key(), 10, snap(**change), 11, 200) == "attest"


def test_heartbeat_after_h_blocks_without_change_and_not_before():
    assert due(snap().key(), 100, snap(pb=299), 299, 200) is None
    assert due(snap().key(), 100, snap(pb=300), 300, 200) == "heartbeat"


def test_new_reserve_block_alone_is_not_a_change():
    # a new finalized checkpoint with the same balance waits for the heartbeat (no remark per Sepolia epoch)
    assert due(snap().key(), 100, snap(eb=999, eh="0x" + "cd" * 32), 101, 200) is None


def test_oracle_state_matches_the_post_signature_order():
    s = snap()
    assert s.oracle_state() == (s.s, s.s2, s.r, s.eb, s.eh, s.pb, s.frozen)


class Rx:
    def __init__(self, ok, xid, events):
        self.ok, self.extrinsic_id, self.block_number, self._events = ok, xid, int(xid.split("-")[0]), events

        class O:
            pass
        self.outcome = O()
        self.outcome.ok = ok

    def event_names(self):
        return self._events

    def as_dict(self):
        return {"extrinsic_id": self.extrinsic_id, "outcome": {"ok": self.ok, "text": "Ok" if self.ok else "Err"}}


def test_failed_oracle_mirror_keeps_the_remark_and_retries(monkeypatch, tmp_path):
    import ballast.attest as attest
    from ballast.store import Store

    calls = {"remark": 0, "oracle": 0}

    def submit(*a, **k):
        calls["remark"] += 1
        return Rx(True, f"{40 + calls['remark']}-2", ["System.Remarked"])

    def post(*a, **k):
        calls["oracle"] += 1
        if calls["oracle"] == 1:
            raise RuntimeError("revive dry-run failed")
        return Rx(True, "45-2", ["Revive.ContractEmitted"])

    monkeypatch.setattr(attest, "submit", submit)
    monkeypatch.setattr(attest.oracle_mod, "post", post)

    class P:
        name = "standin-upstream"

    store = Store(tmp_path / "a.db")
    logs = []
    att = attest.Attester(substrate=None, profile=P(), keypair=None, dep=None, providers=[], store=store,
                          log=lambda ev, **k: logs.append(ev) or {}, oracle="0x" + "ee" * 20)
    rec = att.post("attest", snap())
    assert rec["ok"] and rec["oracle_ok"] is False and att.last_key == snap().key() and att.posts == 1
    assert att.pending_mirror is not None and "mirror-failed" in logs
    # next round: the mirror is retried, the remark is NOT re-posted (no change -> due() is None)
    assert att.mirror()["oracle_ok"] and att.pending_mirror is None
    assert calls == {"remark": 1, "oracle": 2} and due(att.last_key, att.last_block, snap(), 42, 200) is None
    assert store.rows("attestation")[0]["oracle_tx"] == "45-2"


def test_announce_failure_does_not_raise():
    import ballast.attest as attest

    logs = []
    att = attest.Attester(substrate=None, profile=None, keypair=None, dep=None, providers=[], store=None,
                          log=lambda ev, **k: logs.append(ev) or {"event": ev}, oracle=None)
    out = att.announce(["5" * 400], 1)  # one remark cannot hold this watcher set
    assert out and logs == ["announce-failed"]
