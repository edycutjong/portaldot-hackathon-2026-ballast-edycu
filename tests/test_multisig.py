import pytest
from scalecodec.types import MultiAccountId
from scalecodec.utils.ss58 import ss58_encode
from substrateinterface import Keypair

from ballast.chain_profile import SHAPE_LEGACY_1002, SHAPE_WEIGHT_V2, ProfileUnverified
from ballast.multisig import (
    as_multi_params,
    multi_account_id,
    multi_address,
    other_signatories,
    public_key,
)

W1 = Keypair.create_from_uri("//BallastW1").ss58_address
W2 = Keypair.create_from_uri("//BallastW2").ss58_address
A = Keypair.create_from_uri("//BallastA").ss58_address
B = Keypair.create_from_uri("//BallastB").ss58_address
# M_watch as the standin-upstream runtime itself reported it (MultisigExecuted.multisig, evidence/spike-assets-*)
M_WATCH_ON_CHAIN = "5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D"


def test_watcher_multisig_matches_the_on_chain_account():
    assert multi_address([W1, W2], 1) == M_WATCH_ON_CHAIN


@pytest.mark.parametrize("signers,threshold", [([W1, W2], 1), ([A, B], 2), ([A, B, W1], 2)])
def test_derivation_matches_the_sdk(signers, threshold):
    sdk = MultiAccountId.create_from_account_list(signers, threshold)
    assert "0x" + multi_account_id(signers, threshold).hex() == sdk.value


def test_signer_order_does_not_matter_but_threshold_does():
    assert multi_address([W2, W1], 1) == multi_address([W1, W2], 1)
    assert multi_address([W1, W2], 2) != multi_address([W1, W2], 1)


def test_bad_signatory_sets_are_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        multi_account_id([W1, W1], 1)
    with pytest.raises(ValueError, match="threshold"):
        multi_account_id([W1, W2], 3)
    with pytest.raises(ValueError, match="threshold"):
        multi_account_id([W1, W2], 0)


def test_other_signatories_excludes_caller_and_sorts_by_public_key():
    others = other_signatories([A, B, W1], B)
    assert B not in others and set(others) == {A, W1}
    assert [public_key(o) for o in others] == sorted(public_key(o) for o in others)
    with pytest.raises(ValueError, match="not a signatory"):
        other_signatories([A, W1], B)


def test_public_key_accepts_ss58_hex_and_bytes():
    raw = public_key(A)
    assert public_key("0x" + raw.hex()) == raw == public_key(raw)
    assert ss58_encode(raw, ss58_format=42) == A


def test_as_multi_shape_weight_v2():
    p = as_multi_params(
        SHAPE_WEIGHT_V2, threshold=2, other_signatories=[B], maybe_timepoint=None, call="CALL",
        max_weight={"ref_time": 10, "proof_size": 20},
    )
    assert p["max_weight"] == {"ref_time": 10, "proof_size": 20} and "store_call" not in p
    with pytest.raises(ValueError, match="weight-v2"):
        as_multi_params(SHAPE_WEIGHT_V2, threshold=2, other_signatories=[B], maybe_timepoint=None, call="C", max_weight=5)


def test_as_multi_shape_legacy_1002():
    p = as_multi_params(
        SHAPE_LEGACY_1002, threshold=2, other_signatories=[B], maybe_timepoint={"height": 7, "index": 1},
        call="CALL", max_weight={"ref_time": 10, "proof_size": 20}, store_call=True,
    )
    assert p["max_weight"] == 10 and p["store_call"] is True and p["maybe_timepoint"] == {"height": 7, "index": 1}


def test_as_multi_shape_unverified_on_v3():
    with pytest.raises(ProfileUnverified):
        as_multi_params(None, threshold=2, other_signatories=[B], maybe_timepoint=None, call="C", max_weight=0)
