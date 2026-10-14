import pytest

from ballast.remarks import encode, parse, remarks_in_call, walk


def test_encode_parse_round_trip():
    text = encode("attest", a=1, s=5, s2=6, pb=10, ph="0x" + "ab" * 32)
    assert text.startswith("BALLAST/1|attest|a=1|")
    assert parse(text) == {"type": "attest", "a": "1", "s": "5", "s2": "6", "pb": "10", "ph": "0x" + "ab" * 32}


def test_encode_refuses_separators_and_oversize():
    with pytest.raises(ValueError):
        encode("attest", note="a|b")
    with pytest.raises(ValueError):
        encode("attest", x="9" * 400)


@pytest.mark.parametrize("bad", ["hello", "BALLAST/2|attest", "BALLAST/1|", "BALLAST/1|a=1", "BALLAST/1|attest|x",
                                 "BALLAST/1|attest|a=1|a=2"])
def test_parse_rejects(bad):
    with pytest.raises(ValueError):
        parse(bad)


def _call(module, function, **args):
    return {"call_module": module, "call_function": function,
            "call_args": [{"name": k, "value": v} for k, v in args.items()]}


def test_remarks_found_inside_batch_and_multisig():
    inner = _call("Multisig", "as_multi_threshold_1", other_signatories=[],
                  call=_call("System", "remark_with_event", remark="BALLAST/1|freeze|a=1"))
    batch = _call("Utility", "batch_all", calls=[_call("System", "remark_with_event", remark="0x" + b"hi".hex()), inner])
    paths = [p for p, _ in walk(batch)]
    assert paths[-1] == "Utility.batch_all>Multisig.as_multi_threshold_1>System.remark_with_event"
    assert remarks_in_call(batch) == [("Utility.batch_all>System.remark_with_event", "hi"),
                                      ("Utility.batch_all>Multisig.as_multi_threshold_1>System.remark_with_event",
                                       "BALLAST/1|freeze|a=1")]
