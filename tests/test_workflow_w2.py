"""The W2-on-Actions workflow (.github/workflows/watcher-w2.yml): static checks, offline.

The seed is a secret: the workflow must read it only from `secrets.BALLAST_W2_SEED`, mask it, and never print it.
"""

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "watcher-w2.yml"
TEXT = WORKFLOW.read_text()


def test_triggers_are_schedule_and_manual_dispatch_only():
    assert re.search(r'^on:\n  schedule:\n    - cron: "\*/5 \* \* \* \*"\n  workflow_dispatch:', TEXT, re.M)
    for forbidden in ("pull_request", "push:", "pull_request_target", "workflow_run"):
        assert forbidden not in TEXT


def test_runs_never_overlap_and_are_not_cancelled():
    assert "concurrency:\n  group: watcher-w2\n  cancel-in-progress: false" in TEXT


def test_token_is_read_only():
    assert "permissions:\n  contents: read" in TEXT
    assert "write" not in TEXT.split("jobs:")[0].replace("workflow_dispatch", "")


def test_seed_comes_from_the_secret_and_is_masked_never_printed():
    assert TEXT.count("secrets.BALLAST_W2_SEED") == 1
    assert 'echo "::add-mask::$BALLAST_WATCHER_SURI"' in TEXT
    assert "set -x" not in TEXT and "xtrace" not in TEXT
    for line in TEXT.splitlines():  # an echo may name the variable in prose, but never expand it (bar the mask)
        if "echo" in line and "add-mask" not in line:
            assert "$BALLAST_WATCHER_SURI" not in line and "secrets." not in line, line
    assert "printenv" not in TEXT and "env |" not in TEXT


def test_watch_command_is_idempotent_and_deficit_only():
    assert "--until-frozen" in TEXT  # an already-frozen asset exits 0 without a transaction
    assert '--breaker "$BREAKER"' in TEXT and "4401,4402" in TEXT
    assert "--fail-closed-after 86400" in TEXT  # a runner outage must not freeze the asset
    assert "--bot" not in TEXT  # no heartbeat watch: the reserve bot does not run on the runner


def test_exit_codes_zero_and_four_are_the_two_good_outcomes():
    assert '[ "$rc" -ne 0 ] && [ "$rc" -ne 4 ]' in TEXT


def test_vault_matches_the_committed_sepolia_manifest():
    import json

    manifest = json.loads((WORKFLOW.parent.parent.parent / "deployments" / "v3-sepolia.json").read_text())
    assert f'VAULT: "{manifest["reserve"]["vault"]}"' in TEXT
    assert f'USDC: "{manifest["reserve"]["erc20"]}"' in TEXT


def test_watcher_set_is_public_addresses_matching_the_manifest():
    import json

    manifest = json.loads((WORKFLOW.parent.parent.parent / "deployments" / "v3.json").read_text())
    assert f'WATCHERS: "{",".join(manifest["roles"]["watchers"])}"' in TEXT
    assert '--watchers "$WATCHERS"' in TEXT and "//Ballast" not in TEXT  # no seed file other than W2's is needed
