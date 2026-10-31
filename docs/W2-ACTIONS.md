# W2 on GitHub Actions

The second watcher of the `M_watch` 1-of-2 set runs on GitHub's infrastructure instead of the operator's machine.
Workflow: [`.github/workflows/watcher-w2.yml`](../.github/workflows/watcher-w2.yml). Offline checks of the workflow file:
`tests/test_workflow_w2.py` (8 tests).

## What it does

- Trigger: `schedule: */5 * * * *` and `workflow_dispatch`. GitHub starts scheduled runs on a best-effort basis and may delay or skip
  them. **No schedule-triggered run has fired yet** (see Limits); every run so far was a manual dispatch. This is **not** a real-time watcher.
- Each run installs the package, then runs `ballast watch` for a 240 s window (a dispatch can set `max_seconds`): it checks the Sepolia
  `ReserveVault` (`0x7ceB…357b`, two providers, publicnode and Tenderly) against the V3 supply of assets 4401 + 4402 every 2 V3 blocks, and signs
  the `M_watch` freeze (`Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]`) when a provider reads
  less reserve than supply.
- Idempotent: `--until-frozen` exits 0 without a transaction when the asset is already frozen; reserves level for the whole window is a no-op (exit 4, treated as success).
- `concurrency: group: watcher-w2, cancel-in-progress: false`: two runs never overlap, the next queues.
- Deficit only. The provider-outage fail-closed rule and the heartbeat rule stay with the operator's own watcher: a runner with a flaky network must
  not freeze the asset, and the reserve bot does not run on the runner (`--fail-closed-after 86400`, no `--bot`).
- Secret: `BALLAST_W2_SEED` (set with `gh secret set BALLAST_W2_SEED < ~/.config/ballast/v3-w2.seed`). The step reads it into
  `BALLAST_WATCHER_SURI`, masks it with `::add-mask::`, and never prints it. The runner holds W2's seed only; the watcher set is given as the public
  addresses from `deployments/v3.json`. The workflow's token is `contents: read`.

## Evidence

| What | Result | Where |
|---|---|---|
| Healthy reserves, manual dispatch (no-op) | 8 checks, every one `level` (100.00 reserve >= 100.00 supply), no freeze, exit 4 after the 90 s window | [run 41143052046](https://github.com/edycutjong/portaldot-hackathon-2026-ballast-edycu/actions/runs/41143052046), log `evidence/w2-actions-noop-20261030T231100Z.jsonl` |
| W1 off, Sepolia drain 30.00, freeze by W2 on Actions | PASS 8/8 steps, 18/18 state checks | [run 41150496088](https://github.com/edycutjong/portaldot-hackathon-2026-ballast-edycu/actions/runs/41150496088), `evidence/sepolia-drill-20261031T002936Z.json`, Actions log `evidence/sepolia-drill-20261031T002936Z.w2-actions.jsonl` |
| The freeze | V3 extrinsic `259731-1`, signer W2 `5HmY…Sf39` through `M_watch`, remark `reason=deficit s=100000000 r=70000000` (eb = a Sepolia block at or after the drain) | `docs/PROOF.md` (sepolia-drill 20261031T002936Z) |
| Rest of the drill | judge transfer refused `Err(Assets.AssetNotLive)` (259735-1), W1 thaw refused `Err(Assets.NoPermission)` (259736-1), bot refused the thaw until Sepolia finality passed, then co-signed (259895-1), judge transfer OK (259896-1) | same |
| Drain to freeze included | 64.44 s, one sample (this machine's drain, the runner's clock; the drill dispatched the workflow right after the drain, so this includes queue, runner start and install and is **not** the latency of a scheduled run; the other attempts took 53.77 s, 70.73 s and, in a later run on 2026-10-31, 60.88 s) | the drill JSON, `notes` |

"W1 off" means a `ps` snapshot taken just before the drain, logged as a state check, showed no `python -m ballast.cli … watch` process on the
operator's machine. The freeze itself is W2's: it was signed by W2's key (read back from the V3 chain) and the Actions log carries it. The drain was a
`ReserveVault.release` sent by the drill script from the testnet owner key.

Two earlier attempts of the same drill are kept as history in `docs/PROOF.md`: `sepolia-drill-20261030T231633Z` (FAIL: the harness demanded the
freeze remark's block equal the drain block, but the runner starts after the drain, so its first reading is a later block; the freeze itself,
`259196-1`, was correct) and `sepolia-drill-20261031T000804Z` (ERROR: the public Sepolia RPC dropped a connection while sending the refill; the
freeze `259520-1` by W2 on Actions had landed; the harness now retries). After that second run the refill and the thaw were done by hand
(`ballast thaw` + `ballast bot cosign-thaw` against the finalized reserve), so the refill (Sepolia) and the two thaw extrinsics (V3 blocks 259700 and 259711) are in no evidence JSON.

## Limits

- Scheduled runs depend on GitHub. As of 2026-10-31 00:54 UTC no `schedule`-triggered run of this workflow had occurred (`gh run list --workflow watcher-w2.yml`: 5 runs, all `workflow_dispatch`, the first of them a failed setup run that needed the public watcher addresses). The cron is configured and the workflow is active; the proof above is dispatch-driven.
- The runner and the operator's machine are two clocks; the latency above is a wall-clock figure across both.
- The uploaded log artifacts are kept for 30 days; the evidence copies in `evidence/` are the durable ones.
