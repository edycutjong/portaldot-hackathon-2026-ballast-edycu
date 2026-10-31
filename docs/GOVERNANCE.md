# Governance branches: rotations, community watcher, wind-down, `trip()`

This page covers what Ballast does after the first freeze: replacing the watcher set or the admin set, letting
someone outside the team watch the reserve, ending a shortfall, and tripping the EVM mirror. The code is in
`ballast/governance.py`, `ballast/watchdog.py` (`--community`), `ballast/bot.py`, and `contracts/ReserveOracle.sol`.
The drills are `scripts/governance_drill.py` and `scripts/trip_drill.py`.

## What ran where

| Branch | Where it ran | Evidence |
|---|---|---|
| Watcher-set rotation, `M_admin` rotation, community watcher, wind-down, redemption | **Portaldot V3 testnet**, scratch asset 4601 (not the demo asset 4401). Reserve: a **local anvil** vault (not Sepolia) | [`evidence/roles-governance-v3-20261031T012503Z.json`](../evidence/roles-governance-v3-20261031T012503Z.json), PASS 30/30 steps + 16/16 state checks |
| The same drill, rehearsal | stand-in `standin-upstream` (not V3), asset 3001 | [`evidence/roles-governance-standin-upstream-20261031T012128Z.json`](../evidence/roles-governance-standin-upstream-20261031T012128Z.json), PASS 30/30 + 16/16 |
| `ReserveOracle` v2 with `trip()` | stand-in `standin-upstream` only (**not V3**, see below) | [`evidence/oracle-trip-standin-upstream-20261031T011758Z.json`](../evidence/oracle-trip-standin-upstream-20261031T011758Z.json), PASS 9/9 + 9/9 |

Both drill runs started from committed code (`source.dirty: false`). `python scripts/check_receipts.py --profile v3`
re-queried all V3 extrinsics, 165 of them, at finalized head #260355
([`evidence/check-receipts-v3-20261031T013443Z.txt`](../evidence/check-receipts-v3-20261031T013443Z.txt)). One
row, 260287-1, was re-included in the canonical block at the same height after a short fork. The V3 rows are also in
[`PROOF.md`](PROOF.md).

**Drill overrides** are recorded in the evidence under `overrides`. The announcement age K and the wind-down
trigger W were both set to **5 blocks** for the drill. In production, K = 3 × H blocks and W is about 24 h, both
derived from the measured block time. The community watcher's two providers were the same local anvil under two
URLs. So the drill ran the same-block confirmation, but the two providers could not disagree. The unit tests cover
the case where one provider reads short and the other does not. W1, W2 and W3 all ran on one machine, and W3 played
the community watcher. No outside operator has joined yet.

## 1. Rotations are announced first

The bot co-signs a `set_team` that moves the freezer or the admin only when all of these hold:

- B announced the new set on chain first, with a `BALLAST/1|watchers|a=<asset>|t=<t>|m=<members>` or a
  `BALLAST/1|admins|…` remark that B signed itself.
- The announcement is at least K blocks old.
- The proposed account is exactly that set's multisig address.
- Only one role moves per proposal, and the issuer stays `M_mint`.
- A new admin set contains B and has a threshold of at least 2.

Holders get K blocks to see a change coming before it can take effect.

| V3 step | Extrinsic | Outcome |
|---|---|---|
| A proposes freezer → `M_watch'` {W1, W2, W3} through `M_mint` | 260278-1 | Ok. Bot **refused**: no announcement |
| B announces the watcher set (1-of-3) | 260279-1 | Ok. Bot **refused**: 0 blocks old, below K = 5 |
| Bot co-signs after K | 260285-1 | Ok, `TeamChanged` |
| W1 tries to freeze through the **old** `M_watch` {W1, W2} | 260286-1 | `Err(Assets.NoPermission)` |
| B announces the admin set {A, A3, B} 2-of-3 (A2 retired) | 260287-1 | Ok |
| A proposes admin → `M_admin'`, bot co-signs after K | 260288-1, 260293-1 | Ok, `TeamChanged` |

## 2. Community-watcher mode

`ballast watch --community` freezes on a deficit only when every provider answers and reads short. It then reads
every provider again, pinned to one Sepolia block (the lowest latest block among them), and requires the same hash
everywhere. If only one provider reads short, the result is `one-short` and nothing is frozen. A total outage is
`outage` and never triggers fail-closed, because one community member's bad network must not freeze the asset for
every holder. Fail-closed (I6) stays operator-only. The heartbeat rule (I8) applies in both modes.

On V3, with every provider unreachable for 30 s, W3 exited without freezing, and every check read `outage`. After
the custodian drained 30.00 of the 100.00 reserve, W3 froze asset 4601 through `M_watch'` in **260304-1**, about
7.01 s after the drain was sent (one sample, polling every block). The judge's transfer was then refused with
`Err(Assets.AssetNotLive)` in 260305-1.

## 3. Wind-down and redemption

This follows spec "Shortfall end state" for when the reserve stays short.

| V3 step | Extrinsic | Outcome |
|---|---|---|
| W3 freezes the judge's account (after W blocks frozen) | 260310-1 | Ok, `Assets.Frozen` |
| B posts `final` r = 70.00 / 100.00 = 0.7000 | 260311-1 | Ok |
| A proposes `thaw_asset` through `M_admin'`. Bot **refused**: 1 of 2 holders still open | 260312-1 | Ok (proposal) |
| W3 freezes the peer's account | 260313-1 | Ok, `Assets.Frozen` |
| Bot co-signs the thaw (wind-down branch) | 260314-1 | Ok, asset live again |
| Judge tries a transfer: its account is still frozen | 260324-1 | `Err(Assets.Frozen)` |
| Judge asks first: `BALLAST/1|redeem|a=4601|evm=0x90F7…b906` | 260325-1 | Ok |
| A proposes `batch_all([thaw(judge), burn(judge, 30.00)])`, bot co-signs | 260326-1, 260327-1 | Ok: `Thawed` + `Burned` in one extrinsic |
| Custodian releases r × 30.00 = 21.00, `redeemId = redeem_id(260325-1)` | anvil block 1839 | status 1 |

After the thaw, a community watcher still saw the deficit but logged `winddown-hold` and did not freeze. Every holder
with a balance was individually frozen, so re-freezing the asset would change nothing. After the redemption,
S1 = 20.00 and the reserves were 49.00, so r stayed 0.7000.

## 4. `ReserveOracle.trip()` (v2, stand-in only)

Version 2 of the contract adds a watcher H160 list to the constructor. Any listed watcher can call `trip()`, which
sets `frozen` and records `trippedBlock`. That is all it does: it is one-way, like the pallet freezer. Only the
attester can clear the trip, by posting a reading whose Portaldot block is after `trippedBlock`. On Revive,
`block.number` is the Portaldot block. The stand-in drill measured this: `trippedBlock` 8879 matched the trip
extrinsic's block. The Hardhat suite has 6 tests for `trip()`, 21 in total.

On the stand-in, a non-watcher's `trip()` reverted, W1's `trip()` turned `isBacked` false, and a post with
`pdBlock = trippedBlock` reverted (`TripNotCleared`). A post from a later block cleared the trip.

**Not on V3 yet.** The v1 mirror on V3 (`0x4832…155e`) needed a 138.53 tPOT storage deposit, and the v2 initcode
is larger at 2,960 bytes. All of Ballast's V3 keys together hold 83.13 tPOT free, and a deploy dry-run from B fails
([`evidence/v3-oracle-v2-sizing-20261031.json`](../evidence/v3-oracle-v2-sizing-20261031.json), read-only,
`scripts/oracle_v2_sizing.py`). The v1 mirror stays live and has no `trip()`. Deploying v2 on V3 is
`python scripts/trip_drill.py --profile v3 --allow-v3` once the funder is topped up.

## Tests

`tests/test_governance.py` covers the rotation, wind-down and redemption gates, plus the role map with a rotated
admin set. `tests/test_watchdog.py` covers the community rule and the wind-down hold.
`tests/hardhat/ReserveOracle.test.js` covers `trip()`. The full run is pytest 296, forge 20, Hardhat 21
([`evidence/test-run-2026-10-31-p24.txt`](../evidence/test-run-2026-10-31-p24.txt)).
