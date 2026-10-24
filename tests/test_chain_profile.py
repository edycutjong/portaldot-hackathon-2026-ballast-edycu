import pytest
from substrateinterface.utils.hasher import xxh128

from ballast.chain import dev_keypair
from ballast.chain_profile import (
    PROFILES,
    TIMESTAMP_NOW,
    UNVERIFIED,
    ChainFacts,
    ProfileError,
    ProfileMismatch,
    UnknownChain,
    UnknownProfile,
    blake2_256,
    classify,
    derive_block_counts,
    get_profile,
    observe,
    require_multisig_shape,
    require_standin,
)
from ballast.config import load_chain_config

UPSTREAM = PROFILES["standin-upstream"]
P1002 = PROFILES["standin-1002"]


def facts(profile=UPSTREAM, **over):
    base = dict(
        genesis_hash=profile.genesis_hash or "0x" + "ab" * 32,
        code_hash=profile.code_hash or "0x" + "cd" * 32,
        spec_name=profile.spec_name,
        spec_version=profile.spec_version or 1,
        token_decimals=profile.decimals,
        head=500,
        block_time_ms=3000.0,
        mean_block_time_ms=3000.0,
        sample_blocks=20,
    )
    base.update(over)
    return ChainFacts(**base)


class FakeRpc:
    """A node with fixed facts and a per-block timestamp table."""

    def __init__(self, f: ChainFacts, stamps: dict[int, int], code: bytes = b"code"):
        self.f, self.stamps, self.code = f, stamps, code

    def call(self, method, params=None):
        params = params or []
        if method == "chain_getBlockHash":
            n = params[0]
            return self.f.genesis_hash if n == 0 else f"0x{n:064x}"
        if method == "state_getStorage":
            if params[0] == "0x3a636f6465":
                return "0x" + self.code.hex()
            assert params[0] == TIMESTAMP_NOW
            return "0x" + self.stamps[int(params[1], 16)].to_bytes(8, "little").hex()
        if method == "state_getRuntimeVersion":
            return {"specName": self.f.spec_name, "specVersion": self.f.spec_version}
        if method == "system_properties":
            return {"tokenDecimals": [self.f.token_decimals]} if self.f.token_decimals is not None else {}
        if method == "chain_getHeader":
            return {"number": hex(self.f.head)}
        raise AssertionError(method)


def test_block_counts_6s_blocks():
    c = derive_block_counts(6000)
    assert (c.heartbeat_h, c.heartbeat_freeze_k, c.wind_down_w, c.poll_n) == (100, 300, 14_400, 2)


def test_block_counts_3s_standin_upstream():
    c = derive_block_counts(3000)
    assert (c.heartbeat_h, c.heartbeat_freeze_k, c.wind_down_w, c.poll_n) == (200, 600, 28_800, 2)
    assert c.heartbeat_freeze_k == 3 * c.heartbeat_h


def test_block_counts_reject_nonpositive_block_time():
    with pytest.raises(ValueError):
        derive_block_counts(0)


def test_classify_standin_upstream_is_labelled_not_v3():
    ident = classify(facts(), "standin-upstream")
    assert ident.profile.is_standin
    assert "NOT V3" in ident.banner() and "standin-upstream" in ident.banner()
    assert ident.as_dict()["block_counts"]["H"] == 200


def test_classify_profile_mismatch_fails_loudly():
    with pytest.raises(ProfileMismatch, match="standin-1002"):
        classify(facts(), "standin-1002")
    with pytest.raises(ProfileMismatch):
        classify(facts(P1002, token_decimals=None), "standin-upstream")


def test_v3_profile_pointed_at_a_standin_is_refused():
    with pytest.raises(ProfileMismatch, match="configured profile is 'v3', the node is 'standin-upstream'"):
        classify(facts(), "v3")


def test_classify_unknown_chain():
    with pytest.raises(UnknownChain):
        classify(facts(genesis_hash="0x" + "11" * 32, spec_name="something"), "standin-upstream")


def test_classify_code_hash_mismatch_means_different_runtime():
    with pytest.raises(ProfileMismatch, match=":code"):
        classify(facts(code_hash="0x" + "00" * 32), "standin-upstream")


def test_classify_standin_decimals_and_spec_version_are_checked():
    with pytest.raises(ProfileMismatch, match="tokenDecimals"):
        classify(facts(token_decimals=18), "standin-upstream")
    with pytest.raises(ProfileMismatch, match="spec_version"):
        classify(facts(spec_version=269), "standin-upstream")


def test_v3_profile_is_pinned_to_the_live_chain():
    v3 = get_profile("v3")
    # values from Ballast's V3 day-0 check (evidence/v3-day0-20261020T131224Z.json)
    assert v3.genesis_hash == "0xd4f9acbcf7f52388d8b095abe3c198d19fc510e0343e643e87cfbccb155283bd"
    assert v3.code_hash == "0xedc03c9dc81d39fea5c02893cc34cf2ec898d55d7ee8f8e89eb27597a724c7c2"
    assert (v3.spec_name, v3.spec_version, v3.decimals) == ("portaldot-v3", 3002, 14)
    assert v3.default_url == "wss://test-node-v3.portaldot.dev" and not v3.is_standin
    ident = classify(facts(v3, token_decimals=14, block_time_ms=6000.0, mean_block_time_ms=6000.0), "v3")
    data = ident.as_dict()
    assert data["genesis_pinned"] and data["multisig_shape"] == "weight-v2"
    assert data["block_counts"]["H"] == 100 and data["block_counts"]["W"] == 14400
    assert ident.banner().startswith("[v3 | V3]") and UNVERIFIED not in ident.banner()
    assert require_multisig_shape(v3) == "weight-v2"


def test_v3_genesis_running_other_code_is_refused():
    v3 = get_profile("v3")
    with pytest.raises(ProfileMismatch, match=":code"):
        classify(facts(v3, code_hash="0x" + "00" * 32), "v3")
    with pytest.raises(ProfileMismatch, match="tokenDecimals"):
        classify(facts(v3, token_decimals=12), "v3")


def test_pre_launch_v3_identity_is_no_longer_recognised():
    # what the retired feso-apps endpoint was documented to report: portaldotV3/3000, unknown genesis
    with pytest.raises(UnknownChain):
        classify(facts(get_profile("v3"), genesis_hash="0x" + "ab" * 32, spec_name="portaldotV3", spec_version=3000), "v3")


def test_standin_without_a_block_sample_says_not_measured():
    ident = classify(facts(block_time_ms=None, mean_block_time_ms=None), "standin-upstream")
    assert ident.as_dict()["block_counts"] == "not measured"


def test_block_time_is_rounded_so_jitter_does_not_move_the_counts():
    a = classify(facts(block_time_ms=2999.0), "standin-upstream").counts
    b = classify(facts(block_time_ms=3001.0), "standin-upstream").counts
    assert a == b and a.wind_down_w == 28_800


def test_unknown_profile_name():
    with pytest.raises(UnknownProfile):
        get_profile("mainnet")


def test_dev_keys_refused_off_standin():
    with pytest.raises(ProfileError):
        require_standin(get_profile("v3"))
    with pytest.raises(ProfileError):
        dev_keypair(get_profile("v3"), "//BallastA")
    assert dev_keypair(UPSTREAM, "//BallastA").ss58_address


def test_timestamp_storage_key_matches_sdk_hasher():
    assert TIMESTAMP_NOW == "0x" + xxh128(b"Timestamp").hex() + xxh128(b"Now").hex()


def test_observe_measures_median_block_time_through_a_restart_gap():
    head = 500
    stamps, t = {}, 1_000_000
    for n in range(head - 20, head + 1):
        stamps[n] = t
        t += 60_000 if n == head - 10 else 3_000  # one 60 s gap: the node was restarted
    observed = observe(FakeRpc(facts(head=head), stamps, code=b"code"))
    assert observed.code_hash == blake2_256(b"code")
    assert observed.block_time_ms == 3000.0
    assert observed.mean_block_time_ms == pytest.approx((57_000 + 3_000 * 20) / 20)
    assert observed.token_decimals == 12 and observed.sample_blocks == 20


def test_observe_refuses_too_short_a_chain():
    with pytest.raises(ProfileError, match="too low"):
        observe(FakeRpc(facts(head=10), {}))


def test_config_explicit_profile_wins_and_url_defaults(tmp_path):
    cfg_file = tmp_path / "ballast.toml"
    cfg_file.write_text('[chain]\nprofile = "standin-1002"\nurl = "ws://127.0.0.1:49944"\n')
    assert load_chain_config(cfg_file).profile.name == "standin-1002"
    cfg = load_chain_config(cfg_file, profile="v3", url="wss://example.invalid")
    assert cfg.profile.name == "v3" and cfg.url == "wss://example.invalid"
    assert load_chain_config(tmp_path / "missing.toml", profile="v3").url == get_profile("v3").default_url
    # the file's localhost URL is the stand-in's; --profile v3 alone goes to the V3 endpoint
    assert load_chain_config(cfg_file, profile="v3").url == "wss://test-node-v3.portaldot.dev"
    assert load_chain_config(cfg_file, profile="standin-1002").url == "ws://127.0.0.1:49944"
