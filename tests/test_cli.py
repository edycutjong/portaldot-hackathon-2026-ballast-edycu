from ballast.cli import main


def test_unknown_profile_exits_2_without_a_traceback(capsys):
    assert main(["--profile", "mainnet", "chain"]) == 2
    assert "unknown chain profile" in capsys.readouterr().err


def test_unreachable_node_exits_3(capsys):
    # nothing listens on localhost port 9; no network beyond loopback
    assert main(["--profile", "v3", "--url", "http://127.0.0.1:9", "chain", "--no-measure"]) == 3
    assert "[v3] node unreachable" in capsys.readouterr().err


def test_sample_below_minimum_is_refused_before_any_rpc(capsys):
    assert main(["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "chain", "--blocks", "5"]) == 2
    assert "--blocks must be >= 20" in capsys.readouterr().err
