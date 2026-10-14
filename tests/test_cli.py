import pytest

import ballast.sepolia
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


H1 = "0x" + "11" * 32
H2 = "0x" + "22" * 32


class Fake:
    def __init__(self, name, blocks=None, bal=100, down=False):
        self.name, self.blocks, self.bal, self.down = name, blocks or {"latest": (5, H1), "finalized": (3, H1)}, bal, down

    def call(self, method, params):
        if self.down:
            raise ballast.sepolia.ProviderError(f"{self.name}: down")
        if method == "eth_chainId":
            return hex(11155111)
        if method == "eth_getBlockByNumber":
            key = params[0] if not params[0].startswith("0x") else int(params[0], 16)
            n, h = self.blocks.get(key, (key, H1)) if isinstance(key, int) else self.blocks[key]
            return {"number": hex(n), "hash": h, "timestamp": "0x1"}
        return f"0x{self.bal:064x}"


@pytest.mark.parametrize("fakes,code", [
    ([Fake("a"), Fake("b")], 0),
    ([Fake("a"), Fake("b", bal=99)], 1),  # same block hash, different balance -> disagreement
    ([Fake("a", down=True), Fake("b", down=True)], 3),
    # latest answers but finalized fails everywhere: that tag is down -> 3
    ([Fake("a", blocks={"latest": (5, H1)}), Fake("b", blocks={"latest": (5, H1)})], 3),
])
def test_reserves_exit_codes(monkeypatch, capsys, fakes, code):
    monkeypatch.setattr(ballast.sepolia, "providers_from", lambda *a, **k: fakes)
    assert main(["reserves", "0x" + "ab" * 20]) == code


def test_reserves_cross_check_disagreement_exits_1(monkeypatch):
    fakes = [Fake("a", blocks={"latest": (5, H1), "finalized": (3, H1), 3: (3, H1)}),
             Fake("b", blocks={"latest": (5, H1), "finalized": (3, H1), 3: (3, H2)})]
    monkeypatch.setattr(ballast.sepolia, "providers_from", lambda *a, **k: fakes)
    assert main(["reserves", "0x" + "ab" * 20, "--tag", "latest", "--cross-check"]) == 1


def test_watch_bad_flags_exit_2_without_a_traceback(capsys):
    assert main(["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "watch", "--breaker", "1",
                 "--holder", "0x" + "00" * 20, "--supply-assets", "1,abc"]) == 2
    assert "ValueError" in capsys.readouterr().err
    assert main(["--profile", "standin-upstream", "watch", "--breaker", "1", "--holder", "0x" + "00" * 20,
                 "--supply-assets", "1,2", "--max-block-age", "-1"]) == 2
    assert main(["--profile", "standin-upstream", "watch", "--breaker", "1", "--holder", "0x" + "00" * 20,
                 "--supply-assets", "1,2", "--poll-interval", "-1"]) == 2
    # the breaker must be one of the backed assets, ids distinct, addresses well-formed
    for extra in (["--supply-assets", "2,3"], ["--supply-assets", "1,1"], ["--supply-assets", "1", "--holder", "0x01"]):
        args = ["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "watch", "--breaker", "1",
                "--holder", "0x" + "00" * 20, "--poll-blocks", "2", *extra]
        assert main(args) == 2, extra


def test_watch_unreachable_node_exits_3(capsys):
    assert main(["--profile", "standin-upstream", "--url", "ws://127.0.0.1:9", "watch", "--breaker", "1",
                 "--supply-assets", "1,2", "--holder", "0x" + "00" * 20, "--poll-blocks", "2"]) == 3


def test_watch_refuses_an_http_node_url_it_could_never_freeze_through(capsys):
    assert main(["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "watch", "--breaker", "1",
                 "--supply-assets", "1,2", "--holder", "0x" + "00" * 20, "--poll-blocks", "2"]) == 2
    assert "ws:// or wss://" in capsys.readouterr().err


def test_watch_refuses_poll_blocks_below_one(capsys):
    assert main(["--profile", "standin-upstream", "--url", "ws://127.0.0.1:9", "watch", "--breaker", "1",
                 "--supply-assets", "1", "--holder", "0x" + "00" * 20, "--poll-blocks", "0"]) == 2


def test_reserves_malformed_holder_is_a_usage_error_not_an_outage(capsys):
    assert main(["reserves", "0x1234"]) == 2
    assert "not an EVM address" in capsys.readouterr().err


def test_watch_bad_provider_name_exits_2(capsys):
    assert main(["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "watch", "--breaker", "1",
                 "--supply-assets", "1", "--holder", "0x" + "00" * 20, "--poll-blocks", "2",
                 "--provider", "a|b=http://x"]) == 2
    assert "provider name" in capsys.readouterr().err


def test_team_and_cosign_team_parse_and_reject_bad_input(capsys):
    from ballast.cli import build_parser

    a = build_parser().parse_args(["team", "--issuer", "x", "--admin", "y", "--freezer", "z", "--cancel"])
    assert a.command == "team" and a.cancel and a.freezer == "z"
    b = build_parser().parse_args(["bot", "cosign-team", "--issuer", "x", "--admin", "y", "--freezer", "z"])
    assert b.bot_command == "cosign-team" and b.max_finalized_age == 3600.0
    with pytest.raises(SystemExit):
        build_parser().parse_args(["bot", "cosign-team", "--issuer", "x"])  # admin + freezer required
    # unreachable node: a usage-time failure exits 2 without a traceback
    assert main(["--profile", "standin-upstream", "--url", "http://127.0.0.1:9", "bot", "cosign-thaw",
                 "--max-finalized-age", "-1"]) == 2
    assert "Traceback" not in capsys.readouterr().err
