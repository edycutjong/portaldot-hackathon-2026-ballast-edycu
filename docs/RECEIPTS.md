# Receipts

Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are
in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and
every drill reserve-chain tx from the local anvil. An index comes first, then the read-only Sepolia section.

## At a glance

Four places, each labelled on every row: the **Portaldot V3 testnet** (profile v3, real tPOT — every V3
extrinsic is also listed in [`PROOF.md`](PROOF.md)), the Portaldot **stand-in** chain (not V3), the
**local-anvil** reserve chain (not Sepolia), and **Sepolia** (read-only so far — see its section).

| Run | Portaldot chain | Reserve chain | Newest result (clean source preferred) | Evidence |
|---|---|---|---|---|
| Breaker drill against a REAL Sepolia ReserveVault (100.00 test USDC): freeze on V3, thaw after Sepolia finality | v3 | Sepolia | PASS (8/8 steps as expected, 18/18 state checks) | [`sepolia-drill-20261031T031516Z.json`](../evidence/sepolia-drill-20261031T031516Z.json) |
| Benchmark: back-to-back drain -> freeze -> thaw cycles on asset 4401 (local-anvil reserve), per-cycle latency | v3 | local-anvil (not Sepolia) | PASS (120/120 steps as expected, 50/50 state checks) | [`roles-bench-v3-20261031T020152Z.json`](../evidence/roles-bench-v3-20261031T020152Z.json) |
| Governance branches on a scratch asset: announced rotations, community watcher, wind-down, redemption | v3 | local-anvil (not Sepolia) | PASS (30/30 steps as expected, 16/16 state checks) | [`roles-governance-v3-20261031T012503Z.json`](../evidence/roles-governance-v3-20261031T012503Z.json) |
| Governance branches on a scratch asset: announced rotations, community watcher, wind-down, redemption | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (30/30 steps as expected, 16/16 state checks) | [`roles-governance-standin-upstream-20261031T012128Z.json`](../evidence/roles-governance-standin-upstream-20261031T012128Z.json) |
| ReserveOracle v2: trip() by a listed watcher, refused for others, cleared only by a later post | standin-upstream (stand-in, NOT V3) | none — the oracle mirrors B's attestation; this drill posts a fixed drill status | PASS (9/9 steps as expected, 9/9 state checks) | [`oracle-trip-standin-upstream-20261031T011758Z.json`](../evidence/oracle-trip-standin-upstream-20261031T011758Z.json) |
| Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw, team gate) | v3 | local-anvil (not Sepolia) | PASS (22/22 steps as expected, 20/20 state checks) | [`roles-drill-v3-20261024T045513Z.json`](../evidence/roles-drill-v3-20261024T045513Z.json) |
| Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw, team gate) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (22/22 steps as expected, 20/20 state checks) | [`roles-drill-standin-upstream-20261014T150211Z.json`](../evidence/roles-drill-standin-upstream-20261014T150211Z.json) |
| Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED) | v3 | local-anvil (not Sepolia) | PASS (15/15 steps as expected, 6/6 state checks) | [`roles-attest-v3-20261024T050653Z.json`](../evidence/roles-attest-v3-20261024T050653Z.json) |
| Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (15/15 steps as expected, 6/6 state checks) | [`roles-attest-standin-upstream-20261014T150338Z.json`](../evidence/roles-attest-standin-upstream-20261014T150338Z.json) |
| Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless | v3 | local-anvil (not Sepolia) | PASS (16/16 steps as expected, 6/6 state checks) · ran from uncommitted changes | [`roles-setup-v3.json`](../evidence/roles-setup-v3.json) |
| Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (16/16 steps as expected, 5/5 state checks) | [`roles-setup-standin-upstream.json`](../evidence/roles-setup-standin-upstream.json) |
| Breaker drill, scratch asset: drain -> freeze | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (14/14 steps as expected, 11/11 state checks) | [`drill-drain-standin-upstream-asset2039.json`](../evidence/drill-drain-standin-upstream-asset2039.json) |
| Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6) | v3 | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 8/8 state checks) | [`drill-outage-v3-asset4501.json`](../evidence/drill-outage-v3-asset4501.json) |
| Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 8/8 state checks) | [`drill-outage-standin-upstream-asset2041.json`](../evidence/drill-outage-standin-upstream-asset2041.json) |
| Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8) | v3 | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 9/9 state checks) | [`drill-heartbeat-v3-asset4503.json`](../evidence/drill-heartbeat-v3-asset4503.json) |
| Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 9/9 state checks) | [`drill-heartbeat-standin-upstream-asset2043.json`](../evidence/drill-heartbeat-standin-upstream-asset2043.json) |
| ReserveOracle on Revive, mirroring a drill | standin-upstream (stand-in, NOT V3) | — | PASS (5/5 steps as expected, 6/6 state checks) | [`oracle-revive-standin-upstream-20261014T150859Z.json`](../evidence/oracle-revive-standin-upstream-20261014T150859Z.json) |
| Assets spike: watcher-set freeze, freezer thaw refused | standin-upstream (stand-in, NOT V3) | — | PASS (11/11 steps as expected + 1 observation, 10/10 state checks) | [`spike-assets-standin-upstream-asset1010.json`](../evidence/spike-assets-standin-upstream-asset1010.json) |

## Sepolia (read-only — no Ballast contract is deployed on Sepolia yet)

The Sepolia `ReserveVault` deploy, its 100.00 USDC deposit and the real-Sepolia drill wait until the deployer wallet holds >= 100.00 Circle test USDC; the reads below show what it holds. Every drill above uses the local-anvil reserve instead, labelled as such.

- [`evidence/sepolia-crosscheck-2026-10-14-p4.json`](../evidence/sepolia-crosscheck-2026-10-14-p4.json) — read at 2026-10-14T13:01:33.877Z: finalized block #11913325 via 2 providers — AGREE (publicnode: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000, drpc: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault. P4 row 3 gate (2026-10-14): the ReserveVault deploy + 100.00 USDC deposit need >= 100000000 (100.00 USDC, 6 decimals) in this wallet; the balance read here is lower, so no Sepolia vault was deployed (waiting on the Circle faucet)
- [`evidence/sepolia-crosscheck-2026-10-14-p5.json`](../evidence/sepolia-crosscheck-2026-10-14-p5.json) — read at 2026-10-14T14:59:47.420Z: finalized block #11913933 via 2 providers — AGREE (publicnode: `0x38042e59670bff3aeda838faba65592f918e0f75a96bde863fa410b582fc4bda` reserves 20000000, drpc: `0x38042e59670bff3aeda838faba65592f918e0f75a96bde863fa410b582fc4bda` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia (wallet below 100.00 USDC). P5 evidence refresh.
- [`evidence/sepolia-crosscheck-2026-10-14.json`](../evidence/sepolia-crosscheck-2026-10-14.json) — read at 2026-10-14T11:41:44.199Z: finalized block #11912942 via 2 providers — AGREE (publicnode: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000, drpc: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia yet; this file shows the two-provider reader agreeing on one finalized block

## V3 receipts — v3

Chain label: Portaldot V3 testnet

### Sepolia drill — real ReserveVault + 100.00 test USDC, drain -> freeze on V3, thaw only after Sepolia finality — 2026-10-31T03:15:17Z

Chain: **Portaldot V3 testnet** · reserve: **Sepolia** · raw JSON: [`evidence/sepolia-drill-20261031T031516Z.json`](../evidence/sepolia-drill-20261031T031516Z.json) · result: **PASS** (8/8 steps as expected, 18/18 state checks) · source: `94e5377` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

- owner before: {'address': '0xDEf7Cd11f524C2246571654110b43476C2BD9300', 'eth_wei': 199749845168052139, 'usdc': 19896195}
- vault: resumed 0x7ceB7c3EBDBCC75e585599e5dd944286F009357b
- W1: OFF for the whole drill (no `ballast watch` process before the drain; the freeze is W2's, from GitHub Actions)
- W2 on Actions: run https://github.com/edycutjong/portaldot-hackathon-2026-ballast-edycu/actions/runs/41163591577 (dispatched 2026-10-31T03:15:39Z)
- drain -> freeze included (wall clock: this machine's drain, the Actions runner's clock; includes workflow queue + runner startSepolia reserve + V3): 60.88 s
- re-deposit sent -> finalized (wall clock, both providers): 961 s
- owner after: {'eth_wei': 199749845165098039, 'usdc': 19896195, 'vault_reserves': 100000000}

Reserve-chain transactions (Sepolia; vault `0x7ceB7c3EBDBCC75e585599e5dd944286F009357b`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | vault owner drains 30% (30.00) — release() | 12031085 | [`0xa3c2bf9a757eb3d0af238db4a21f5bc678d939d9d44aa75ff5c6faa025c9fff1`](https://sepolia.etherscan.io/tx/0xa3c2bf9a757eb3d0af238db4a21f5bc678d939d9d44aa75ff5c6faa025c9fff1) | ✅ status 1 |
| 2 | vault owner re-deposits 30.00 | 12031092 | [`0xac818dcd3605e2652142b393d7fe6e1baad26f89051c31c18755d47d0a2aca29`](https://sepolia.etherscan.io/tx/0xac818dcd3605e2652142b393d7fe6e1baad26f89051c31c18755d47d0a2aca29) | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | watcher W2 freezes asset 4401 on V3 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `261379-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 2 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `261381-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 3 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `261382-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 4 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `261386-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 5 | bot B co-signs the thaw: finalized Sepolia reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `261553-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 6 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `261554-1` | Ok | ✅ Ok |

Block and transaction hashes (full):

```
 1  261379-1 block 0xe61e4df7a25774c2b413842eb3ab86acbdf4009a9b1944f10eb56f8623c2a949  tx 0xc3a3eebe2f19533d11cda41eb476e54dec70677f6d7cf9cdde9fc932a80c8a2b
 2  261381-1 block 0xaa1e957dcca115d16035b67a10f191af5b39ef6e519763a3a2f543604c81680e  tx 0x06e2f0b70c7e39c422906ea7ef52dce0021a0af40b94f94358bd994bb5f9a94c
 3  261382-1 block 0x60066d7e19cc01f81a50efdb899ae236cc9da8b265eeb3bfa8b567b53ce03382  tx 0x718cd9788790ced97bef37bc89b333f76a1156eaa140afd32755a61367994e64
 4  261386-1 block 0x46ada3b6753dba4c53636af6a52e955356299fa9040b719a38d7914e1a801463  tx 0xc68c4e0eac8696aab49834aef591cf7fed320c259321036ebad1f960e420b378
 5  261553-1 block 0xc72f177e17429af5b154562224a91e8049bf8cf2103ec7f693e09f6984efae1c  tx 0xa386871ce63a95579845d4be4bfce52cbb3481f4348f4cdb91f5979915923ba8
 6  261554-1 block 0x1db4401f22997db5493fce89dd96a8dea3476dc4da5c42a178b8014c4f6b11a7  tx 0xfbe0f166fae1c8de861d41d4d533448068c9515f86b053cea6fb39d8f88458a0
```

State checks (storage/events read at the step's block):

- ✅ asset 4401 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ vault holds the 100.00 deposit and the owner holds gas (the drain pays the refill): expected `True`, observed `True` at block `sepolia latest`
- ✅ S1 + S2 == 100.00 before the deposit: expected `100000000`, observed `100000000` at block `head`
- ✅ vault.owner() == the Sepolia deployer: expected `0xDEf7Cd11f524C2246571654110b43476C2BD9300`, observed `0xDEf7Cd11f524C2246571654110b43476C2BD9300` at block `sepolia latest`
- ✅ vault.usdc() == Circle test USDC: expected `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238`, observed `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` at block `sepolia latest`
- ✅ vault.reserves() == 100.00: expected `100000000`, observed `100000000` at block `sepolia latest`
- ✅ [publicnode] vault.reserves() at the finalized head #12031011 == 100.00: expected `100000000`, observed `100000000` at block `sepolia finalized #12031011`
- ✅ [tenderly] vault.reserves() at the finalized head #12031011 == 100.00: expected `100000000`, observed `100000000` at block `sepolia finalized #12031011`
- ✅ W1 is OFF: no `ballast watch` process on this machine: expected `[]`, observed `[]` at block `ps`
- ✅ freeze remark eb is at or after the drain's Sepolia block and r is the post-drain reserve: expected `[True, '70000000']`, observed `[True, '70000000']` at block `0xe61e4df7a25774c2b413842eb3ab86acbdf4009a9b1944f10eb56f8623c2a949`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 4401 status after the freeze: expected `Frozen`, observed `Frozen` at block `0xe61e4df7a25774c2b413842eb3ab86acbdf4009a9b1944f10eb56f8623c2a949`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `sepolia latest`
- ✅ bot refuses the thaw: Sepolia finality has not reached the drain block yet: expected `['refused', 12031085]`, observed `['refused', 12031088]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `261379-1`, observed `261379-1` at block `0xe61e4df7a25774c2b413842eb3ab86acbdf4009a9b1944f10eb56f8623c2a949`
- ✅ asset 4401 status after the thaw: expected `Live`, observed `Live` at block `0xc72f177e17429af5b154562224a91e8049bf8cf2103ec7f693e09f6984efae1c`
- ✅ asset 4401 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ all 2 Sepolia txs re-read from both providers: status 1, same block, <= finalized {'publicnode': 12031106, 'tenderly': 12031106}: expected `True`, observed `True` at block `sepolia finalized`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-31T02:56:14Z — PASS (8/8 steps as expected, 18/18 state checks) — source: `94e5377` (clean) — [`evidence/sepolia-drill-20261031T025614Z.json`](../evidence/sepolia-drill-20261031T025614Z.json)
- asset 4401 — 2026-10-31T02:36:22Z — PASS (8/8 steps as expected, 18/18 state checks) — source: `94e5377` (clean) — [`evidence/sepolia-drill-20261031T023622Z.json`](../evidence/sepolia-drill-20261031T023622Z.json)
- asset 4401 — 2026-10-31T00:29:36Z — PASS (8/8 steps as expected, 18/18 state checks) — source: `3555312` (clean) — [`evidence/sepolia-drill-20261031T002936Z.json`](../evidence/sepolia-drill-20261031T002936Z.json)
- asset 4401 — 2026-10-31T00:08:05Z — ERROR (4/4 steps as expected, 12/12 state checks) — source: `fc371f3` (clean) — [`evidence/sepolia-drill-20261031T000804Z.json`](../evidence/sepolia-drill-20261031T000804Z.json) — ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
- asset 4401 — 2026-10-30T23:16:33Z — FAIL (7/8 steps as expected, 17/18 state checks) — source: `b77e02f` (clean) — [`evidence/sepolia-drill-20261030T231633Z.json`](../evidence/sepolia-drill-20261030T231633Z.json) — failed: watcher W2 freezes asset 4401 on V3 through M_watch (reason=deficit) -> Ok; freeze remark eb == the drain's Sepolia block
- asset 4401 — 2026-10-30T22:01:45Z — PASS (8/8 steps as expected, 18/18 state checks) — source: `2dbd35c` (clean) — [`evidence/sepolia-drill-20261030T220145Z.json`](../evidence/sepolia-drill-20261030T220145Z.json)
- asset 4401 — 2026-10-30T21:23:30Z — FAIL (8/8 steps as expected, 17/18 state checks) — source: `9c2112e` (clean) — [`evidence/sepolia-drill-20261030T212330Z.json`](../evidence/sepolia-drill-20261030T212330Z.json) — failed: vault holds the 100.00 deposit; owner holds gas and >= the refill (30%)
- asset 4401 — 2026-10-30T20:46:14Z — FAIL (8/8 steps as expected, 17/18 state checks) — source: `1328f88` (clean) — [`evidence/sepolia-drill-20261030T204614Z.json`](../evidence/sepolia-drill-20261030T204614Z.json) — failed: owner holds >= 100.00 test USDC and gas
- asset 4401 — 2026-10-30T20:09:23Z — PASS (12/12 steps as expected, 18/18 state checks) — source: `cff62bc` (UNCOMMITTED CHANGES) — [`evidence/sepolia-drill-20261030T200923Z.json`](../evidence/sepolia-drill-20261030T200923Z.json)

### Benchmark — back-to-back drain -> freeze -> thaw cycles on asset 4401 (local-anvil reserve), latency per cycle — 2026-10-31T02:01:52Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-bench-v3-20261031T020152Z.json`](../evidence/roles-bench-v3-20261031T020152Z.json) · result: **PASS** (120/120 steps as expected, 50/50 state checks) · source: `ca893a3` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x22753E4264FDDc6181dc7cce468904A80a363E44`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | iter 1: custodian drains 10% (10.60) — release() | 1974 | `0x02aa6dbab13f7b8e0ea783d7f69f638c77cf936a998cc5b592b0fb17ac1b45a9` | ✅ status 1 |
| 2 | iter 1: custodian re-deposits 10.60 | 1975 | `0xba4bd543c325c5219474db7d60a440999f61dd1f74b75a3dd42d48c940dbc32f` | ✅ status 1 |
| 3 | iter 2: custodian drains 10% (10.60) — release() | 2041 | `0x30e06635ead2e7999e0bad7b4ab85a43f39efb57e6dc47c1da1b4fc5e35b43a0` | ✅ status 1 |
| 4 | iter 2: custodian re-deposits 10.60 | 2042 | `0x011f220b45852d71e36b1021688d515b5036e0f78879e3715dfb8b3c6de5bc3c` | ✅ status 1 |
| 5 | iter 3: custodian drains 10% (10.60) — release() | 2108 | `0x92e2a5e10ebf46d089b175261356a1e28b0bfc8a3f526d4f1d175783be168952` | ✅ status 1 |
| 6 | iter 3: custodian re-deposits 10.60 | 2109 | `0x46e42c80f40ada672f236bac126fccac39217183c6356163afc6ac8c99c9ebfd` | ✅ status 1 |
| 7 | iter 4: custodian drains 10% (10.60) — release() | 2175 | `0x459ff4e770559fea915b44c53fd8bf5bcbcf1956e6539b2ec7e3bb9656475a23` | ✅ status 1 |
| 8 | iter 4: custodian re-deposits 10.60 | 2176 | `0x1249248bec45dd7d2125df1087e1628e2028e9f1208f87dec2db4353a6b380a6` | ✅ status 1 |
| 9 | iter 5: custodian drains 10% (10.60) — release() | 2242 | `0x59f690ec1917d9109ac897f6915dc9a513388d7a0ac7b68b59fe57a055aa415f` | ✅ status 1 |
| 10 | iter 5: custodian re-deposits 10.60 | 2243 | `0x24ed1bec666441a5cad8ea147fa8b0d475b3244a02f9181efb24f02f52636be5` | ✅ status 1 |
| 11 | iter 6: custodian drains 10% (10.60) — release() | 2309 | `0x5facca67d3c2c66a8b223fdb68e0cc3ae40beadd1c6344fc2b24fbc9bd376f8b` | ✅ status 1 |
| 12 | iter 6: custodian re-deposits 10.60 | 2310 | `0x9a1c7b3f9e48ede5133cb4952852a6d8f7e067542c111fa57a98775482ec4455` | ✅ status 1 |
| 13 | iter 7: custodian drains 10% (10.60) — release() | 2376 | `0x2acc02e0289d9fd40c03c434bc15dd0185392a946afe6477bdf37a0814f8d192` | ✅ status 1 |
| 14 | iter 7: custodian re-deposits 10.60 | 2377 | `0x1eedd1cdefa0a35a4747afa398fce905a67cfb107b903b35195fc011a1b2e1ae` | ✅ status 1 |
| 15 | iter 8: custodian drains 10% (10.60) — release() | 2443 | `0xcc9883c4acc16ad188de49d7454b149b1b5839dc3c9ba786e5ebd51841a19002` | ✅ status 1 |
| 16 | iter 8: custodian re-deposits 10.60 | 2444 | `0x9a7eea5953c11f339010e8f3ee14a8381325e8136bc6f50828649cb16abc839e` | ✅ status 1 |
| 17 | iter 9: custodian drains 10% (10.60) — release() | 2510 | `0x37521511186844199d60b9f7d4c4cd7e4e2fefa0f940dd8059bd514500584f9c` | ✅ status 1 |
| 18 | iter 9: custodian re-deposits 10.60 | 2511 | `0x124777349125498aecb830b1e4ac46c6afab55ae8469863acaf1c3971e6b16aa` | ✅ status 1 |
| 19 | iter 10: custodian drains 10% (10.60) — release() | 2577 | `0x84a0ccacdcad310311169f73b56d0d7c9820af6b871a2ecfd70c7c3833dbacf7` | ✅ status 1 |
| 20 | iter 10: custodian re-deposits 10.60 | 2578 | `0x6c08e367d4f2036bfa2365a6ac03d58520cee699cab83904a8e40f845c746e8c` | ✅ status 1 |
| 21 | iter 11: custodian drains 10% (10.60) — release() | 2644 | `0xc45e39f55e428ea9ee7abd4dec3418e9917f1c4144f98c4eb4206b7f84e015f7` | ✅ status 1 |
| 22 | iter 11: custodian re-deposits 10.60 | 2645 | `0xb17713389a8c5096ae7055af7506bb8814dbb5460e6b9aac633ae49a1e3e02d5` | ✅ status 1 |
| 23 | iter 12: custodian drains 10% (10.60) — release() | 2711 | `0x98908455468b1978f550eb1263818dd36ab28afecea826e76742914aee5e76f8` | ✅ status 1 |
| 24 | iter 12: custodian re-deposits 10.60 | 2712 | `0xe13c041a46e4a97211ed398f2b75fb35c5b15261076882036c707c83e811b0b5` | ✅ status 1 |
| 25 | iter 13: custodian drains 10% (10.60) — release() | 2778 | `0xa8d0bb285c0a2ba2febb6fe5f5d66d4cdfe039df0f39436f5a5c00bfc0ad1557` | ✅ status 1 |
| 26 | iter 13: custodian re-deposits 10.60 | 2779 | `0x148a244febd9dff6261c3d1b42c7b3fb7c4f320f6d6439049af58d2a4d54f18b` | ✅ status 1 |
| 27 | iter 14: custodian drains 10% (10.60) — release() | 2845 | `0xb30abaaf49bc475fc2e7b496197c9b9d5e36420c8e774aef1213959a6190ea6a` | ✅ status 1 |
| 28 | iter 14: custodian re-deposits 10.60 | 2846 | `0x8fc9ece3f55c2e04fb1db5418379f5462e1986647517686ece7c9c57129b9471` | ✅ status 1 |
| 29 | iter 15: custodian drains 10% (10.60) — release() | 2912 | `0xedf337a702f3825c2422699fdf2cd87a97cbcb57ab1aef4c9d7413ab7793919b` | ✅ status 1 |
| 30 | iter 15: custodian re-deposits 10.60 | 2913 | `0xceed83f54a5611fe77077443705e31df100ba86c9b787aa481ebfc7aace19016` | ✅ status 1 |
| 31 | iter 16: custodian drains 10% (10.60) — release() | 2979 | `0x1dfa89fbd4d0fa2e8b97ba33b75caed96cbbac1b12793733d7e7d60daafc6416` | ✅ status 1 |
| 32 | iter 16: custodian re-deposits 10.60 | 2980 | `0xd4d483d9c37894d9a9c650413b5c89e2e77451679abbf8b8647d325666a63cf1` | ✅ status 1 |
| 33 | iter 17: custodian drains 10% (10.60) — release() | 3046 | `0xa03fac71dce4afbf9cf04701f1a7216bbcc7414e9e323542ccbaad7e119201da` | ✅ status 1 |
| 34 | iter 17: custodian re-deposits 10.60 | 3047 | `0x77ee16c0629beeac203fb1fbbc3e86823df20989400f2389b3b09454d4cf6265` | ✅ status 1 |
| 35 | iter 18: custodian drains 10% (10.60) — release() | 3113 | `0x02e395377060287bd55541b0099bbcacc1470ef8076a1c94eaa0556530416e9b` | ✅ status 1 |
| 36 | iter 18: custodian re-deposits 10.60 | 3114 | `0x04720d3a93b276a686184c7dd931585012a35dfd9db7d334df5ef752497532cc` | ✅ status 1 |
| 37 | iter 19: custodian drains 10% (10.60) — release() | 3180 | `0xe7f32b6a2e47429b535185f342ee559d4eafc723035e1d824702168326c13ac9` | ✅ status 1 |
| 38 | iter 19: custodian re-deposits 10.60 | 3181 | `0x876d7d6ed9b81fd920a96a07f67242e8b1a1c878a9d63c15198d84159b646bb3` | ✅ status 1 |
| 39 | iter 20: custodian drains 10% (10.60) — release() | 3247 | `0x32cd5369105f87eb2169cc206eb6fdda264027abce8a893b9934e187bc8b6bad` | ✅ status 1 |
| 40 | iter 20: custodian re-deposits 10.60 | 3248 | `0xfb2b03e5598a5bcbf7e064cf12ebb0bb90fb8631cfaff04a408a1f35829e1b15` | ✅ status 1 |
| 41 | iter 21: custodian drains 10% (10.60) — release() | 3314 | `0xb8c2ee102955bfe0593aefacd6603a63ccb72ba0725e9e28f779b5e29c0d25bd` | ✅ status 1 |
| 42 | iter 21: custodian re-deposits 10.60 | 3315 | `0xc7e4099a543d59f76430f550698580c857d63d49841c9fedb28904eb3ef62a48` | ✅ status 1 |
| 43 | iter 22: custodian drains 10% (10.60) — release() | 3381 | `0xd4373a69c87eda150d8df7a92e2ea2f215fab97c03edb9102d8c7d3e71b67cb3` | ✅ status 1 |
| 44 | iter 22: custodian re-deposits 10.60 | 3382 | `0x482e61f62d0fe68d8a370b4b3dc028f9ceef1f47f77cdd72b49ee177ba18d05f` | ✅ status 1 |
| 45 | iter 23: custodian drains 10% (10.60) — release() | 3448 | `0xf1b0c46f5fc9b4141024c918c528fac288f740961ee240555327baf9f30b95f9` | ✅ status 1 |
| 46 | iter 23: custodian re-deposits 10.60 | 3449 | `0xa799bee3c5aeb6a975de36e726bbe4105ad206b645d0b61cb0b8d22ea9313df3` | ✅ status 1 |
| 47 | iter 24: custodian drains 10% (10.60) — release() | 3515 | `0xdc821e28e1d3d30b8cc08ea549b78d55fa158936924d24096ce86c5292925eda` | ✅ status 1 |
| 48 | iter 24: custodian re-deposits 10.60 | 3516 | `0x8a9548e4dc7ef455bd69ebe3b8cba7743397e31b5198bf666db2ad087ea19a1a` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | iter 1: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260640-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 2 | iter 1: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260643-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 3 | iter 1: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260647-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 4 | iter 2: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260652-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 5 | iter 2: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260655-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 6 | iter 2: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260660-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 7 | iter 3: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260666-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 8 | iter 3: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260669-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | iter 3: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260673-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 10 | iter 4: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260679-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 11 | iter 4: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260682-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 12 | iter 4: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260686-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 13 | iter 5: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260692-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 14 | iter 5: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260695-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 15 | iter 5: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260699-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 16 | iter 6: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260705-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 17 | iter 6: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260709-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | iter 6: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260714-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 19 | iter 7: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260720-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 20 | iter 7: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260723-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 21 | iter 7: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260727-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 22 | iter 8: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260733-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 23 | iter 8: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260736-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 24 | iter 8: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260740-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 25 | iter 9: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260745-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 26 | iter 9: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260748-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 27 | iter 9: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260752-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 28 | iter 10: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260758-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 29 | iter 10: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260761-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 30 | iter 10: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260765-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 31 | iter 11: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260771-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 32 | iter 11: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260775-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 33 | iter 11: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260780-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 34 | iter 12: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260786-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 35 | iter 12: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260789-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 36 | iter 12: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260793-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 37 | iter 13: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260798-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 38 | iter 13: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260801-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 39 | iter 13: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260805-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 40 | iter 14: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260812-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 41 | iter 14: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260815-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 42 | iter 14: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260819-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 43 | iter 15: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260824-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 44 | iter 15: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260827-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 45 | iter 15: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260831-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 46 | iter 16: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260836-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 47 | iter 16: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260839-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 48 | iter 16: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260844-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 49 | iter 17: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260850-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 50 | iter 17: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260853-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 51 | iter 17: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260857-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 52 | iter 18: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260862-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 53 | iter 18: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260865-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 54 | iter 18: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260869-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 55 | iter 19: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260874-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 56 | iter 19: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260877-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 57 | iter 19: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260881-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 58 | iter 20: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260886-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 59 | iter 20: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260889-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 60 | iter 20: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260893-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 61 | iter 21: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260898-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 62 | iter 21: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260901-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 63 | iter 21: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260905-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 64 | iter 22: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260910-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 65 | iter 22: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260913-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 66 | iter 22: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260917-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 67 | iter 23: watcher W1 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `260922-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 68 | iter 23: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260925-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 69 | iter 23: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260929-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 70 | iter 24: watcher W2 freezes asset 4401 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `260934-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 71 | iter 24: A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `260937-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 72 | iter 24: bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260941-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |

Block and transaction hashes (full):

```
 1  260640-1 block 0xcda7434dee5be74b0671140eb00550fdf7759ea74fd505f7a3f6699c99c0709d  tx 0xd871df7719b175c2492666e81ebceb4467d141aa205569956ebdcb9fabedfc43
 2  260643-1 block 0x3dc6015826eda8ac931333cba537804327013658c63b2fb3795061c636783f2f  tx 0x9d1800eda036ffd0ee3365946adb81ba809a3675d575b71c35527c690527c588
 3  260647-1 block 0x33b0caba3dbf1cd70d5a356e71be012074590f1551ef63c03f863140485927b8  tx 0x9d446bdf71f84a0901a1c06bf90b95c98a5066eb88d94d647db2c0b21fbd3328
 4  260652-1 block 0xaea64da8b7f9866d357ee290756cf8e0ceaddb4bc0bca8766037f996b4590932  tx 0x9e2e834318742806857cc657ec204b963da8a4d22819006e97d6c0e6eb3a2185
 5  260655-1 block 0x2e91a7cd79d9553159ad53174bf16fbffc4ae2e1af637f8e35c57da8d9cc758e  tx 0xf00b0241b57be9fce317138514345133a6e9dd3f9e24fca2ac7c607b7840d319
 6  260660-1 block 0xa652798c28d029b7b500e0d8c425bda2e8df0f135cbf29a53e9319563bbf62ee  tx 0xfebf85a7dcd08aeb3664ee4fad9426f0c6b10b1f0e17fc34731853507ba2e6f7
 7  260666-1 block 0xdae2d951f3b7b3e03c2d116f849b0de58d393d0c43b5a1b7df076dc3c1d537db  tx 0x876e8da53e377d819c30b8e69ed00d7e9fb91e9b659cd8f988439a9d617a5e94
 8  260669-1 block 0x36191e7ffa545a7ff6009959ca190526876131d7e5b9bc4cc575973c94b5a5ba  tx 0xe97d7f2cd7393747337d8651e227f7131258429e40511b2b85cb72e2c9cae22d
 9  260673-1 block 0xaf96611d672c9713b87a88f7d315882e538342b4a1e2bfcab68540358bbe4213  tx 0x12ca6dac6d90c20f22dd421a1b240584d4fb7a7f570c2f2179c55c6316e9a956
10  260679-1 block 0x35394c0ac688de792c93e01f00865dd553326ce046ba0b95fdb7b28ca90ad7c7  tx 0xdd2af16c658c61c438d783ae5d478637c8bdb56956e57aaa7a5df0367536dea2
11  260682-1 block 0x08bc18af45976728861618c7073256248f118c6876b4c5e0c7035473d62bf4d9  tx 0xae0580bf892b8a15e37629101ec4bbb51cc4947ccb1cbc1c8d438811b8f9dab1
12  260686-1 block 0x36e82b4ec69e56780002dbdf34b8a9ace4bf6a59edbe61ff84eff17c189f3162  tx 0xe0fdca5d6b09813417d76d88c55993f2eb3cdfdd0ed284e0a024e75a48b8652d
13  260692-1 block 0xab8fbea3fdae25d7f7f0b1a8b4eda223d96ef2ae74fcf38aeceb14e66610b41c  tx 0x59b9f751457dca579060a5812e4bf965d64fe9ea09d63d6aad135b6ee245982c
14  260695-1 block 0xc42af7e26cc4c9c45485cd04e5efc2d5e24823d9fb29e53bec8b49b94045392b  tx 0x3f7d9e050d8ee0b6a2eafa48998bee1b73b05f9d0b35861f37b685edf25ec37f
15  260699-1 block 0x726333ffdaa6ced17b9d845d7352a1190c57f41a71a48ea358868cff2428a416  tx 0x65d646717a66c477172b6c31b444119f446687691ff722aa6995179f9211a041
16  260705-1 block 0x44259041ccf753ad4c244ad00d44e9b5d8b9b2c81f934a82eeaab2c565764308  tx 0x9dfc6f72f26c912c9590d3045c89a289bd71c4e97380dbcccb4e62bbd12256dd
17  260709-1 block 0xc2e74428c3749403d4529a2077657f0f54ce26577ffa7c37fa30b34b1892eb4d  tx 0x6111d8688df6dea3ffc1a31991eca84f631fbc12e86712eccac0241e0bb3eddd
18  260714-1 block 0xf6869af65aa8ddde2fadfdfe8141c111f3b850c19ce8d4ca0b9c4c9899772736  tx 0x29391017a309ed3330f3aefd96a62fb25876f9b8d71265f5b4aad422861be881
19  260720-1 block 0xb80474e394128955b4f11b2296a55e42cd47cc6281ffe1e7df2abe11560d3761  tx 0x92fb0e5a166219644c58af17c1d2aeef47d6f8da1538b235d19d0bce013bb903
20  260723-1 block 0xfb95c6ff3d0e7a8ee18ae41d0e8c967a7d1a040306045cce6e5543a6dc03ac7e  tx 0xfb9b2e75f1a89173a9440a9208a52987c4e33107a965ad068958bc142f1dbd98
21  260727-1 block 0x32a176cf7439934997e02dfa2bb1cd188519f06f40a29d4e9578a801c552782f  tx 0xb32d2fd0f023deb4257e591a2e19f89b529f9ddec14f8e610483f53c409552c2
22  260733-1 block 0x41084ddfca3c089cf7f1d0be969651542e92b49a942000e33e3ffa4f925f4e57  tx 0xddf905b786350f968417b38f623f68d37e09c165f927ed4053e20bb0751c8d59
23  260736-1 block 0xdb3fd0070178e4b9ad795d40ad65f377c45e123be3e29e2d9a95df279865dc78  tx 0x30b7291a7e1c6c64357f7258a59941aedbadd4e60b3152a96c340d41c1c2697d
24  260740-1 block 0x6c7ce71d3a9018aba4e4b86d0529b269463d7caf30584892254f95d43b059af6  tx 0x31593bef76e62c7b527f07c2f0aa763e54230a36d44662e914b088e90e67fdd2
25  260745-1 block 0x7849ae6c90ac9363c207b177bb5599ae7ec3afd7e6cde3c2156713275ec35e28  tx 0xc712b63ac93c2d7a1eeb08bce3b48a9e0f38ec09085fa710718929c6fa9a2d30
26  260748-1 block 0x2fe1fbc5dfbf9861ff0740f7ef944358f26bed624bf769482fb806a90e100895  tx 0x8abde43801079da792cd05cf46e73117746a04a452e162c0aebf5ffea435f971
27  260752-1 block 0x80dbad4f9d876166af24d8bcab0fedf4b1f4b5b44803dc73ef73d96b6e4080f0  tx 0x2dec673b54bce7f037991c5c4c9e2d2576cf44f6536df9fcdba40bc7c7ca6bb4
28  260758-1 block 0x0a439efc6f77ea3933b05c706116f9def5501e82c1c148949faca30b6b78024e  tx 0x79f6d0c5d3a9f91146df8782bade6299a716304bc6ce2077549d88424ef7eed1
29  260761-1 block 0xd3322711c44825d8fabf3350c073f54e3eaf0350396f7e4fcc4cca233580b1ca  tx 0x49fc2c34cd2042909c67cc39c08345db79f78ba657a8a33e8bf3e73f68df53f7
30  260765-1 block 0x25ab2f7aedc584ed3ed4ea30844e51de49782d5bb1adc327ca1c036e3e346e30  tx 0x68a0f490857af73cab7f343b895af510cb5c4b84f8c954a8e6d38c065e90321a
31  260771-1 block 0xf1dfae4c8f870c719857c7529fd40019f1c628424567a767442aae7d1c6430d5  tx 0x963ed3639e5b86ae058dbc7878a6b2664491d70d2fe11dfe925721781832d015
32  260775-1 block 0x004a5dc10ef458d4a6007516f807223ec8bb6773bece27fd0fc459babc31e61e  tx 0x57e7a341473c9e8eacde02d7da3b2eac1f86e062f75a7edcb628ee48492ebfcd
33  260780-1 block 0xf520e4feae13315e69a1de97dd1d2c91a69f05a14d20712b9d0abfcd7d2038bf  tx 0x0307fe056c197c29846ee3d5d9c7fe171e7d1f385c839dcd7c7fd01887cf4e36
34  260786-1 block 0xb4495d5704c952f756a997cb821e34b7c461cb94c10e2530a70abed1ebe208fd  tx 0x527d76b0e4993c32350c922edb9b3feffb0a594d42d32dba9531f631bdd57a1c
35  260789-1 block 0x488fbb0afb2d22e9823adcafa3486b098d576143632da1ce1e2afe541f15302b  tx 0x3f356a4da447818337ef0b63339adccab1aafbbb11f28d97d3a616a2c6fd43aa
36  260793-1 block 0x1216bc8b9ed3c6b726f821617c5d532ffd9f484201254b1e5d2c24e0a4e062a5  tx 0x8a581ba38485f1fd0d5a00683eb09b4d669709c8737beff574276208a9923753
37  260798-1 block 0xadb3f49ddabee36a851da31271d6f69c9f57535348ff05a19ab7bdfca68734b1  tx 0x5cbcde3ed2e88323b37c0dea4609886002d59564315144ee1c253b48a4d58d7a
38  260801-1 block 0xe3b08cfee0f4add3408467d1d1af332cf12bbdfa08bffd6979eb1923cbd9f507  tx 0x6f1756d26d0baf61cd05a09696fa0d6e82bfc2c7c4d4658eec9ff659a813ca71
39  260805-1 block 0xd74195c8e00928ec200545b0cabbf2031bc245d7a94ac90beab2c80a4b68d935  tx 0x0d653808a63eae9793141eb68f837222896dcf42d6c08d6a514ff055491373f7
40  260812-1 block 0xbffbe3b18b0f14abd08aec3bde11620e950169ccae0812f223ea336b4fbf4e84  tx 0xd8f3127fc39a25957f4a971b56f5d06e25941bacdd68d3ea1adbc22f14bbcda4
41  260815-1 block 0x186005720306f2bd25e329ab06b50e90bba712437a13001f6cf9c6660bf9f87e  tx 0x28ed9645849761dbfb3ff8e9cfe6aa9019dc69948d722783a0cd7a35e1ebb9f1
42  260819-1 block 0x2ad17bf48e2bf92bc8a01337cf5ddf59e29429a0fe44e2ba96eab23d7ceac7a4  tx 0x946bfa757df2b3b3c58ffb5fe84ef019baa8bdf591fd641c1582836405ee199f
43  260824-1 block 0xa35b88c036e9ddda280210118f8b615b870e689580cf96741427f2b9b92f54f6  tx 0xd585233fa15099e4dadeff28751de1be1bf3d687d49f9fc82862b33d626e2674
44  260827-1 block 0x1e71e3fdbda0129fcacd4e0ed73e2c56c032b85074bd451b3150ac393b243851  tx 0xc9a417e5d21b6c4298b4c1f3f14e8dc03603452d92fa573e76f3580769d7f6fe
45  260831-1 block 0x365a92b07640df196a9702580322479241622f1a51ab16201a7daa0aab45ee06  tx 0xd8ead2e9fad3e59d20515a6c6097054d3ef0125e395084552239141b9551736a
46  260836-1 block 0xcad411285617b0d94b3915c22b2bb4d112ffe17d8d460088ecdf48290947005b  tx 0x704dc556a7d9e554a64fedabe068ae097fe210d39e8c6cf604b5db3616faf3c1
47  260839-1 block 0x062a44c9b93f7b43684ce7b0acf756490d80efa8792e0e98b5bf9632c157d426  tx 0xba87f9da4ad71e73f767b2bbc84535fd855294181e22ee33e37e43b73f2b8aa9
48  260844-1 block 0x94ad935e43fae2be4c60c973706d70bacc69f95819329e3a542c570792d97292  tx 0xca32ddd08ea7dc85bdefb8a0b84687c373ef7455ba2b6031728e171d77c254c2
49  260850-1 block 0x5d3e4f5af46ebb5da6f67aaa06159f50d9cd030591e58340aad096f1e7da58ff  tx 0xc9765dd5120fa1cfb59e8e6b8a2d89c95e037556339cf86c5a3c1f8446d35446
50  260853-1 block 0x70418eb2edba9b17b333727939ccae91330b714ee2720cdcf47d7d8e25090dea  tx 0x6614e8eb8f409bc009ad77888bc6e7a6b1dec54aa06082025cdf387a6b2e7df9
51  260857-1 block 0x9b6123c92ca6c366b832ee531054d7db221f3062f8d2008d370ea30045a0452a  tx 0x09afc460f3366b7105cd741aa2d37d47a4390ea742fb6d9f98137c475fe47db4
52  260862-1 block 0xd1597d5ba2da6cc21b568c879e968ad5d839300811e96aaa78682eb66d802fc1  tx 0xc66623f6e54a7655bfaa6c51ab82fafb1443c65f411f9ce7d7954ba254d06381
53  260865-1 block 0x8bcbc4aec2e764290dc958a3c91bd423a8d804f09f18f8fefa0e148254cf7f94  tx 0x8fdd9ff818168bdf65d70a9a2978b4e0ed83694736177028c9f4e9df208d3b0c
54  260869-1 block 0xd3976bb0cb659421c590c1c1ee2161100da50326d4347eec17f3172fc15757cb  tx 0xa12226cf09d97b3f4c5ac0bbf465b7eb7301bb4e1eaeea4bd9b40a8ba1da2cf4
55  260874-1 block 0x23b7f3b1bcb9f12f2b18e6bb0a4245be1554c685e6be632faec7d216a6ce0c94  tx 0xbf7c2bf3fafc65c0df7ca336be79dc4bceaa8a272ef87f5815508c5911790a03
56  260877-1 block 0x83e427e6606fcdfc705bbf43aa7a366f08ea6eafecc0c4872e5e2d97191e86f9  tx 0x16174e57f61956ab5ec581cbd8cb2e2586f41084bd8d4da2cd6051e84fa753de
57  260881-1 block 0x015d993e84c75e08b3fcee2a2599070d155d3b8ffbed46ae332be55ef6803aa5  tx 0x8eb606a7e56cf2b19ae5c9c4a01ef37526ffc1d0a210e40285d7df53690db8fc
58  260886-1 block 0x28547557cbb872c719ec79a80f47aa1d64f6f576361f45a0df2fbed980550c97  tx 0x8d14a9d0e8941227c93d44598be60cc2116d4fcc41a8912d37ae39aa354abd6d
59  260889-1 block 0x5169cfe93ac88ee163fa25f9a6e4ad4397f1f737bda240c006e7953ef0e6745e  tx 0x17b3e18d98c7c7043f287b10e92d8d9e6ee962d6f869db7747396d9b7af5c57e
60  260893-1 block 0x9e3df647af467babf649d1a0380affe0da7d06a156af150acfce1346995c14b3  tx 0x193c89dce577c22f6bb703cac5f0bc4d14fb2d1eee71e6f2a3ab4c897abc8cc8
61  260898-1 block 0x32c982d426e5f3f44eebab08f4e588fe6721ecbfcef1837ed8ac1385a4afd2df  tx 0x3ed7acb363c1694bfbe33a0859450321a7b0f438089729a923589555d5ba6c83
62  260901-1 block 0xf77aaa4e58cbb65a31f869a780d24ae7863f59caa73d5251a1b78419dfcc54b7  tx 0x60954d6b57c7a984b33eba7ba8c692d2c80b7275995d98eb88f3b53c8f6f72f7
63  260905-1 block 0xfda099182c635d121de8b08e2e64cd65949e9c6f07c3959735efffaafb73cc0a  tx 0xc3a8211e22d93b7ed2bdf6b190aeb8c9505ffb3853cccc96ebd586af9ffb2ca8
64  260910-1 block 0xe5f3d4946a88dff0e269fa706c958b1743701b0702a07573e36a6626c878e19c  tx 0x9291007e8c5c600fd72fa4699d6f4a09c1e08970b00d8d7e8fbda2a07b5c2fd6
65  260913-1 block 0x11ba3bdb9f8aa7794c24d796a29b98785d8e67b7de6b641064bf8676bdaddfaf  tx 0x5c34790a97e0b8df38cb3d96876ef0ffecee6b0dac73f78c2362557ce5381050
66  260917-1 block 0x1e23b4190682001278867cd4b384b5d1aa0608911dd64999ac4988e87f8a2fff  tx 0xd5f19170e7ed089d9286604ca1b3615f8dbaab4f952f676b603e5e73d9eca980
67  260922-1 block 0x20ddac447db2c565f3b0a906d227ad0c119d347fb6c25d2bcd4c194bb89d937b  tx 0xbd89c361516108250fb0d87f15c7fc4367ae96f58cc311d6f5577e86fc9200c7
68  260925-1 block 0x7ef3ca40bfd5a45b06ab062a94875b1f2331b34ab1068bcfc710166d1ca83062  tx 0xfd254aa5854d36f44707f33120448a7e372b07be7acaca832f802dbe34f6ad0e
69  260929-1 block 0x02159a01254763fbd716fd36125c00ef21ce30c3c324c20665a8e56e390e27f1  tx 0x7ae7518868acfbc7c69049ac9741a22030865cabe252774c53a5fed83558e87c
70  260934-1 block 0x6c13f38b914953203b43abc9c93601afb7ef6ce2023fbac14ebceb9604588601  tx 0x4430272df1ae6d5eb03a67faae6172f812e7c5342bf5949fa9d06636a42baac4
71  260937-1 block 0x3d676c96eef3262de97c164cc1db0e71147b10b2b7c1d6cf6c6cdc3f88b15e21  tx 0xf4fe85fad6ee65ea261eaa3a9d949b8eeb49f19d37d012c4bbaf4623ed69a686
72  260941-1 block 0xda1a8b1f30994bc9b0d6e2e79145e7e23f188ef928bbb3ebec43fe012992b831  tx 0x6837f1ccbd50accc0a3a91c4196f8b13428b660fbd4556d76a34df238e9da0c2
```

State checks (storage/events read at the step's block):

- ✅ asset 4401 team == role map before the bench (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the bench: vault reserves >= S1 + S2 (a surplus is not a deficit): expected `True`, observed `True` at block `head`
- ✅ iter 1: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xcda7434dee5be74b0671140eb00550fdf7759ea74fd505f7a3f6699c99c0709d`
- ✅ iter 1: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x33b0caba3dbf1cd70d5a356e71be012074590f1551ef63c03f863140485927b8`
- ✅ iter 2: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xaea64da8b7f9866d357ee290756cf8e0ceaddb4bc0bca8766037f996b4590932`
- ✅ iter 2: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xa652798c28d029b7b500e0d8c425bda2e8df0f135cbf29a53e9319563bbf62ee`
- ✅ iter 3: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xdae2d951f3b7b3e03c2d116f849b0de58d393d0c43b5a1b7df076dc3c1d537db`
- ✅ iter 3: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xaf96611d672c9713b87a88f7d315882e538342b4a1e2bfcab68540358bbe4213`
- ✅ iter 4: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x35394c0ac688de792c93e01f00865dd553326ce046ba0b95fdb7b28ca90ad7c7`
- ✅ iter 4: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x36e82b4ec69e56780002dbdf34b8a9ace4bf6a59edbe61ff84eff17c189f3162`
- ✅ iter 5: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xab8fbea3fdae25d7f7f0b1a8b4eda223d96ef2ae74fcf38aeceb14e66610b41c`
- ✅ iter 5: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x726333ffdaa6ced17b9d845d7352a1190c57f41a71a48ea358868cff2428a416`
- ✅ iter 6: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x44259041ccf753ad4c244ad00d44e9b5d8b9b2c81f934a82eeaab2c565764308`
- ✅ iter 6: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xf6869af65aa8ddde2fadfdfe8141c111f3b850c19ce8d4ca0b9c4c9899772736`
- ✅ iter 7: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xb80474e394128955b4f11b2296a55e42cd47cc6281ffe1e7df2abe11560d3761`
- ✅ iter 7: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x32a176cf7439934997e02dfa2bb1cd188519f06f40a29d4e9578a801c552782f`
- ✅ iter 8: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x41084ddfca3c089cf7f1d0be969651542e92b49a942000e33e3ffa4f925f4e57`
- ✅ iter 8: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x6c7ce71d3a9018aba4e4b86d0529b269463d7caf30584892254f95d43b059af6`
- ✅ iter 9: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x7849ae6c90ac9363c207b177bb5599ae7ec3afd7e6cde3c2156713275ec35e28`
- ✅ iter 9: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x80dbad4f9d876166af24d8bcab0fedf4b1f4b5b44803dc73ef73d96b6e4080f0`
- ✅ iter 10: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x0a439efc6f77ea3933b05c706116f9def5501e82c1c148949faca30b6b78024e`
- ✅ iter 10: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x25ab2f7aedc584ed3ed4ea30844e51de49782d5bb1adc327ca1c036e3e346e30`
- ✅ iter 11: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xf1dfae4c8f870c719857c7529fd40019f1c628424567a767442aae7d1c6430d5`
- ✅ iter 11: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xf520e4feae13315e69a1de97dd1d2c91a69f05a14d20712b9d0abfcd7d2038bf`
- ✅ iter 12: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xb4495d5704c952f756a997cb821e34b7c461cb94c10e2530a70abed1ebe208fd`
- ✅ iter 12: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x1216bc8b9ed3c6b726f821617c5d532ffd9f484201254b1e5d2c24e0a4e062a5`
- ✅ iter 13: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xadb3f49ddabee36a851da31271d6f69c9f57535348ff05a19ab7bdfca68734b1`
- ✅ iter 13: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xd74195c8e00928ec200545b0cabbf2031bc245d7a94ac90beab2c80a4b68d935`
- ✅ iter 14: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xbffbe3b18b0f14abd08aec3bde11620e950169ccae0812f223ea336b4fbf4e84`
- ✅ iter 14: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x2ad17bf48e2bf92bc8a01337cf5ddf59e29429a0fe44e2ba96eab23d7ceac7a4`
- ✅ iter 15: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xa35b88c036e9ddda280210118f8b615b870e689580cf96741427f2b9b92f54f6`
- ✅ iter 15: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x365a92b07640df196a9702580322479241622f1a51ab16201a7daa0aab45ee06`
- ✅ iter 16: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xcad411285617b0d94b3915c22b2bb4d112ffe17d8d460088ecdf48290947005b`
- ✅ iter 16: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x94ad935e43fae2be4c60c973706d70bacc69f95819329e3a542c570792d97292`
- ✅ iter 17: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x5d3e4f5af46ebb5da6f67aaa06159f50d9cd030591e58340aad096f1e7da58ff`
- ✅ iter 17: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x9b6123c92ca6c366b832ee531054d7db221f3062f8d2008d370ea30045a0452a`
- ✅ iter 18: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xd1597d5ba2da6cc21b568c879e968ad5d839300811e96aaa78682eb66d802fc1`
- ✅ iter 18: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xd3976bb0cb659421c590c1c1ee2161100da50326d4347eec17f3172fc15757cb`
- ✅ iter 19: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x23b7f3b1bcb9f12f2b18e6bb0a4245be1554c685e6be632faec7d216a6ce0c94`
- ✅ iter 19: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x015d993e84c75e08b3fcee2a2599070d155d3b8ffbed46ae332be55ef6803aa5`
- ✅ iter 20: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x28547557cbb872c719ec79a80f47aa1d64f6f576361f45a0df2fbed980550c97`
- ✅ iter 20: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x9e3df647af467babf649d1a0380affe0da7d06a156af150acfce1346995c14b3`
- ✅ iter 21: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x32c982d426e5f3f44eebab08f4e588fe6721ecbfcef1837ed8ac1385a4afd2df`
- ✅ iter 21: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xfda099182c635d121de8b08e2e64cd65949e9c6f07c3959735efffaafb73cc0a`
- ✅ iter 22: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0xe5f3d4946a88dff0e269fa706c958b1743701b0702a07573e36a6626c878e19c`
- ✅ iter 22: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x1e23b4190682001278867cd4b384b5d1aa0608911dd64999ac4988e87f8a2fff`
- ✅ iter 23: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x20ddac447db2c565f3b0a906d227ad0c119d347fb6c25d2bcd4c194bb89d937b`
- ✅ iter 23: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0x02159a01254763fbd716fd36125c00ef21ce30c3c324c20665a8e56e390e27f1`
- ✅ iter 24: asset status after the freeze: expected `Frozen`, observed `Frozen` at block `0x6c13f38b914953203b43abc9c93601afb7ef6ce2023fbac14ebceb9604588601`
- ✅ iter 24: asset status after the thaw (Live) and level (reserves == supply): expected `['Live', True, 100000000]`, observed `['Live', True, 100000000]` at block `0xda1a8b1f30994bc9b0d6e2e79145e7e23f188ef928bbb3ebec43fe012992b831`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-31T01:58:42Z — FAIL (10/10 steps as expected, 5/6 state checks) — source: `71cb007` (clean) — [`evidence/roles-bench-v3-20261031T015842Z.json`](../evidence/roles-bench-v3-20261031T015842Z.json) — failed: level before the bench: vault reserves == S1 + S2

### Governance drill — announced watcher-set + M_admin rotations, community watcher, wind-down, redemption — 2026-10-31T01:25:03Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-governance-v3-20261031T012503Z.json`](../evidence/roles-governance-v3-20261031T012503Z.json) · result: **PASS** (30/30 steps as expected, 16/16 state checks) · source: `1e28678` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

- watchers: W1, W2 and W3 run on ONE machine; W3 plays the community watcher (no separate operator yet)
- funding: {'wanted': {'A (operator)': '1537000000000000', 'W1 (watcher)': '50000000000000', 'W3 (community watcher)': '100000000000000', 'Judge (holder)': '50000000000000', 'Peer (holder)': '30000000000000', 'B (reserve bot)': '200000000000000'}, 'topped_up': 3, 'ed': '10000000000000', 'multisig_deposit': '1119000000000000'}
- community_freeze_seconds_after_drain_sent (one sample, poll every block): 7.01

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xfcDB4564c18A9134002b9771816092C9693622e3`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1835 | `0x57f68abf941884296661f39f0c6ba9887f46a403487d021391a510412deca49e` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc), owner = custodian | 1836 | `0x6287296955333828da0515aff7063a6ab82741ba46ebd08e49a34c99d3b3c365` | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 | 1837 | `0x96b6fe173c4da57b7ebbf014b8a9b1743e7019ab036a7f5b1850078f3d962aa7` | ✅ status 1 |
| 4 | custodian drains 30.00 (30%) from the vault | 1838 | `0xce8879224fcb330f6d715ecc647c33b621eba61764fd69934c5877e36f004877` | ✅ status 1 |
| 5 | custodian releases r x 30.00 = 21.00 to the judge's EVM address, redeemId = redeem_id(260325-1) | 1839 | `0x8209e93eaa34aee9f40ea732e6a58dffc904c0e710e7b46b95af5a6357a0b465` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | funder tops up the accounts below their working balance | `Utility.batch_all[3 x Balances.transfer_keep_alive]` (5Fk6ZzKT5EcWHV3RZkYjgi7EEA1JT3aHaEhkSP2gGyv3DP96) | `260271-1` | Ok | ✅ Ok |
| 2 | A creates scratch asset 4601 | `Assets.create` (A (operator)) | `260272-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-gov (6 decimals) | `Assets.set_metadata` (A (operator)) | `260273-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A mints 30.00 to the judge (scratch S1, before the team hand-over) | `Assets.mint` (A (operator)) | `260274-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 5 | A mints 20.00 to the peer (scratch S1, before the team hand-over) | `Assets.mint` (A (operator)) | `260275-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | A hands the team over: issuer M_mint, admin M_admin, freezer M_watch {W1, W2} | `Assets.set_team` (A (operator)) | `260276-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | A transfers ownership to M_mint | `Assets.transfer_ownership` (A (operator)) | `260277-1` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 8 | A proposes set_team(freezer = M_watch' {W1, W2, W3}) through M_mint | `Multisig.as_multi(Assets.set_team(freezer=M_watch')) — first approval` (A (operator)) | `260278-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | B announces the watcher set {W1, W2, W3} 1-of-3 (BALLAST/1|watchers) | `System.remark_with_event` (B (reserve bot)) | `260279-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot co-signs (cosign-team --announcement (after K)) | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `260285-1` | Ok, executed | ✅ Ok · inner Ok |
| 11 | W1 tries to freeze through the OLD M_watch {W1, W2} | `Multisig.as_multi_threshold_1(Assets.freeze_asset) via old M_watch` (W1 (watcher)) | `260286-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B announces the admin set {A, A3, B} 2-of-3 (A2 retired; BALLAST/1|admins) | `System.remark_with_event` (B (reserve bot)) | `260287-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 13 | A proposes set_team(admin = M_admin' {A, A3, B}) through M_mint | `Multisig.as_multi(Assets.set_team(admin=M_admin')) — first approval` (A (operator)) | `260288-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | bot co-signs (cosign-team --announcement (admins, after K)) | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `260293-1` | Ok, executed | ✅ Ok · inner Ok |
| 15 | W3 (community watcher) freezes through M_watch' once every provider reads short at one block | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W3 (community watcher)) | `260304-1` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 16 | judge transfers 1.00 while the asset is frozen | `Assets.transfer` (Judge (holder)) | `260305-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 17 | W3 freezes the judge's account through M_watch' (wind-down step 1) | `Multisig.as_multi_threshold_1(Assets.freeze)` (W3 (community watcher)) | `260310-1` | Ok + Assets.Frozen | ✅ Ok · inner Ok · Assets.Frozen |
| 18 | B posts final r = 70.00 / 100.00 = 0.7000 (BALLAST/1|final) | `System.remark_with_event` (B (reserve bot)) | `260311-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 19 | A proposes thaw_asset through M_admin' | `Multisig.as_multi(Assets.thaw_asset via M_admin') — first approval` (A (operator)) | `260312-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 20 | W3 freezes the peer's account through M_watch' (wind-down step 1) | `Multisig.as_multi_threshold_1(Assets.freeze)` (W3 (community watcher)) | `260313-1` | Ok + Assets.Frozen | ✅ Ok · inner Ok · Assets.Frozen |
| 21 | bot co-signs (cosign-thaw --final (all holders frozen)) | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `260314-1` | Ok, executed | ✅ Ok · inner Ok |
| 22 | judge transfers 1.00 after the thaw (account still frozen) | `Assets.transfer` (Judge (holder)) | `260324-1` | Err(Assets.Frozen) | ✅ Err(Assets.Frozen) |
| 23 | judge asks first: BALLAST/1|redeem with its EVM address | `System.remark_with_event` (Judge (holder)) | `260325-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 24 | A proposes batch_all([thaw(judge), burn(judge, 30.00)]) through M_admin' | `Multisig.as_multi(Utility.batch_all[thaw(judge), burn(judge, 30.00)] via M_admin') — first approval` (A (operator)) | `260326-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 25 | bot co-signs (cosign_redeem) | `Multisig.as_multi(Utility.batch_all) — final approval` (B (reserve bot)) | `260327-1` | Ok, executed | ✅ Ok · inner Ok |

Block and transaction hashes (full):

```
 1  260271-1 block 0x36639f28d4f2b248be108abc613f9c16ebf65341a3aa2304f752ce15c6fc26a7  tx 0x7d2eb007a9fa13e849e3cb2236bb02d540dbd2aa645e2a88b453a729f3940491
 2  260272-1 block 0xc94986df365c41c7a06b694237416c771df22041b299edce3262908a1d2a20b1  tx 0x2d1eb8870a1f30ce139a7b52781a40992081ca86c9036061cb734ac310d9c519
 3  260273-1 block 0x099f3c96145224978be83b9796358f892abe5b12eba6e50f51a588601598073e  tx 0x5754cac9bbdf8a9b46daee101c1bd2909614f5111af84a9b9c3d91914e0d7bb0
 4  260274-1 block 0x581e826e4b3b83f0626fbffe293f36a10462c69aeb7d59ef26b0c751bc5db02d  tx 0xeebc622cb783d8c420e2c80c3d411a1e7dadae1c84b56d6e9ba6d031262c5a6a
 5  260275-1 block 0xf2ebf95f910eb45866780ea860e832622c97e92211236517186c9d15d1231144  tx 0x96a5131bdf6a59efa71bf743123d3ae1f4112db534e37266b9df1882e3a652ec
 6  260276-1 block 0xc70ae7d4b4c4ae1610b704709f7a3c7890709f82278536ebe090cb625099eca6  tx 0x1b4102f7eebcc06fba7a5b305d6da7edbaac5b8f3258ac211a8ac8aaa81850bd
 7  260277-1 block 0x6eefd9ec69ca0b616c2006faa37f6549ddf49b46ec8927022226cb3338299113  tx 0xf0d21ba6e54aaeed6ffc49341a64c8e07e9bd4668f6276bdb385bae5799f216e
 8  260278-1 block 0x97432b08a6191e7f952cf9834e24d3fd6ca07c3101c4e26c363ba9beb046ed61  tx 0x3958290eea29f88b117ef4b07efb650c886cb50d6e4f55289072ab5d070ba613
 9  260279-1 block 0x92633917514c885996d0f0c9a3d7a6a38bd25053c3d551e06476407a5acb7cdf  tx 0x7419a5e58f3f2f519627859cf25a6b54c4848036cfcfb536706ecdc0c405e656
10  260285-1 block 0x5e8af1f8b55ae7c357003a05f3bdb90f8e9491c635f2e1680e2b8dd755b7c746  tx 0x6ae47cb874e95c029b18195394f833969061fa4421f156601d8dc8d4c8cfeb63
11  260286-1 block 0x92b96844671b665b24f9c8d7060066454f4fed3122a94d874bf2082f64894dfa  tx 0x575a4aa82bb1efcf42e77965a48fc27f2cd660b6bd73351dae1380ba667ddfc4
12  260287-1 block 0xb489f912934e73dd59a252c745b4636927ae9d2322ac673ff7dcecec3b7974c9  tx 0x6a2b168c3cc8a265afdf2dc99aa0c3cd87a8f344f531aa4c73e20c4e3dc11314
13  260288-1 block 0x89a5382b2bcd659b68d201f03a9902197a89450e1ea786874580f05a3e62fad7  tx 0xe544e492587fc2147d52ec917191bb9533489050248b36dcfa8e53a6e05e6af2
14  260293-1 block 0x49febe672afe0011fe98c3046cb6610d5ea3430ee8b92d5d0aca9e0101070520  tx 0xa5c900635f2f4c41c20cec38589d08ca0da8263b8b46ead94985c6a1225dee35
15  260304-1 block 0x254c60932cea8088ccab8459c15802dc7c63e1b0e03ab209a713fcf6f14b5461  tx 0xe2e4adcdf156698f0161bc0019309a6fcbb32abfdb6c67e9e1cc25c3fdaa7f87
16  260305-1 block 0x90956ff2adc25c652ee217d7500c2bee32caabf207b043f1bdb26c9c94090022  tx 0xbe6d7818d56e09d35ab134ba6fe3ce8e2ce839c25700ee15c5cbb3cd4074f7d8
17  260310-1 block 0x42e94bbf3dc65c62022b10355f9d33a191983f9c34f8bb2b5b0add8e662ac757  tx 0x50b0e5c30c2954d961e771ca1e646862a91669e060b3978b97ba236993af2ed2
18  260311-1 block 0xb4e1153c9232c1e1f921599e05a63335c1659463b18503096c5527e26b177e42  tx 0xb39b835304598dbc617d032654c96795ab25e50018ef753b5e30010a3e5e5b4f
19  260312-1 block 0x8a01d64b67362719d660343331ca8d4ade802fc9bc281719085222394627019f  tx 0x173ae306a31aa7f60d8ab5f83ece715b4a37d49450b9d73747c0c504152eb09b
20  260313-1 block 0x19aa51f227d9ac4c7e1d3f143a3d7e4df934e6d4899bbe6470786041a8c9f3e8  tx 0xeba6e56b6c3d92605128aea1a19ea704fbc4201916816f5ee979d151653d28c6
21  260314-1 block 0xbc0aa49465068badaccdb1463c6ab0591968fbbaa8fec30334415d077e0f7563  tx 0xffaf338f0c8caab70f54ee114621767c817c94b2cee5684eb3e212526f5cae50
22  260324-1 block 0x17552de979c917fc55cf1a57ef8576c17bdde528557df1c4efa5f5e83e48c330  tx 0x10b8e388c00d34ad39c6e0da5483db43de4afcc4ea8bfcfa91edf069f754fd0a
23  260325-1 block 0x82f960a817db4f0ef63f64c898fc800ec6012290c1e26056e546cc0746d6547d  tx 0xc2d2143e09b7a596cf34eeba7a75c4916d177a14b3608bbb83d55b8678bbbec2
24  260326-1 block 0x8c9913a7506488897258d7c2e47d84bd9887898e0af5054c93e85d9f21dea3e5  tx 0x83c8da1d948af2b3d80645523af2cee39ef612607cb7ce3e31a8b839a9522d25
25  260327-1 block 0x145900ca5039ab4e0af5e09d91a1d74b5a44c342ea8e3dcabfd22df50cc4fd4b  tx 0x2a489f5499dfe7fa259ba9027e05bfdcb3fe4f8d5f808da584c0a5a61373ceae
```

State checks (storage/events read at the step's block):

- ✅ scratch team == role map (owner/issuer M_mint, admin M_admin, freezer M_watch): expected `['5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb', '5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb', '5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg', '5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c']`, observed `['5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb', '5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb', '5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg', '5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c']` at block `0x6eefd9ec69ca0b616c2006faa37f6549ddf49b46ec8927022226cb3338299113`
- ✅ bot refuses an unannounced watcher rotation: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ bot refuses before the announcement is K blocks old: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ freezer after the co-signed rotation == M_watch': expected `5FmRH9FrR8GZxFnwAYUccEQfVYSnacGbJtri4W4tL87qRUH3`, observed `5FmRH9FrR8GZxFnwAYUccEQfVYSnacGbJtri4W4tL87qRUH3` at block `head`
- ✅ asset frozen after the old set's attempt (must stay false): expected `False`, observed `False` at block `head`
- ✅ admin after the co-signed rotation == M_admin': expected `5E1pU3Ur1Rfwpd3eMqCmN3KuTc9stK7Hf4TFZGHNuvgHAc1Z`, observed `5E1pU3Ur1Rfwpd3eMqCmN3KuTc9stK7Hf4TFZGHNuvgHAc1Z` at block `head`
- ✅ community watcher, every provider down for 30 s: exit 4 (not frozen), no freeze submitted: expected `[4, False]`, observed `[4, False]` at block `watcher log`
- ✅ …its checks all read 'outage' with 'never fail-closed': expected `True`, observed `True` at block `watcher log`
- ✅ the freeze's trigger: community mode, pinned block, every provider short: expected `['community', True, 2]`, observed `['community', True, 2]` at block `watcher log`
- ✅ bot refuses the wind-down thaw while a holder is open: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ asset frozen after the wind-down thaw (must be false): expected `False`, observed `False` at block `head`
- ✅ every holder with a balance individually frozen: expected `[['Judge (holder)', True], ['Peer (holder)', True]]`, observed `[['Judge (holder)', True], ['Peer (holder)', True]]` at block `head`
- ✅ community watcher after the thaw: deficit but winddown-hold, no freeze (exit 4): expected `[True, False, 4]`, observed `[True, False, 4]` at block `watcher log`
- ✅ the redemption executed atomically: Thawed + Burned in one extrinsic: expected `[True, True]`, observed `[True, True]` at block `receipt`
- ✅ after the redemption: S1, reserves, and r unchanged: expected `[20000000, 49000000, '0.7000']`, observed `[20000000, 49000000, '0.7000']` at block `head + evm latest`
- ✅ the judge's EVM address received r x 30.00: expected `21000000`, observed `21000000` at block `evm latest`


### Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw — 2026-10-24T04:55:14Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-drill-v3-20261024T045513Z.json`](../evidence/roles-drill-v3-20261024T045513Z.json) · result: **PASS** (22/22 steps as expected, 20/20 state checks) · source: `04a1de4` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

- other watcher: W1 saw asset 4401 already frozen at #170113 and stood down
- drain -> freeze included (wall clock, one machine; local anvil + stand-in): 12.22 s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x22753E4264FDDc6181dc7cce468904A80a363E44`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1555 | `0xc9c30aabd8707442ac5037666a6a91889d3ad8f393449fbb497634a8e1185385` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1556 | `0x531062078693c9552dc07d82a098cccbdf3822e31b1d25e84cfb9eddceffae0f` | ✅ status 1 |
| 3 | custodian drains 30% (31.20) — release() | 1622 | `0xec4b585e18bb55d8b8c9a117b9e2b54790d63e0d98982f6e5935a1933bc482c0` | ✅ status 1 |
| 4 | custodian re-deposits 31.20 | 1623 | `0xd07e14157791ef65b12811161b63181745f66c110bb4046017e4d7940a8deb50` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | A proposes mint 1.00 to the judge through M_mint (first approval) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170095-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 2 | bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `170098-1` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 3 | A proposes 0.01 more (reserves cover S1 + S2 exactly) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170100-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 4 | A cancels the refused proposal (deposit returned) | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `170105-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 5 | watcher W2 freezes asset 1 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `170112-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 6 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `170114-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 7 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `170115-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | A proposes a mint while frozen | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170117-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | A cancels it | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `170122-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 10 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `170125-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 11 | bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `170133-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 12 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `170134-1` | Ok | ✅ Ok |
| 13 | A proposes set_team with the freezer moved to A (through M_mint) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170137-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | A cancels the refused team change | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `170142-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 15 | A proposes set_team making A the sole admin (could thaw without the bot) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170145-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 16 | A cancels the refused admin swap | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `170150-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 17 | A proposes set_team keeping issuer M_mint, admin M_admin, freezer M_watch | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170153-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | bot co-signs the safe team change | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `170156-1` | Ok + inner Ok + Assets.TeamChanged | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.TeamChanged |

Block and transaction hashes (full):

```
 1  170095-1 block 0xa1b86ec21d400d31f26081c7f6d35475dd1eb457541f521cedf2cb8660e646ba  tx 0x79fa8945cfcd5e6c700ef88342447cedb84b148849d531237100df6a9819bbec
 2  170098-1 block 0xfb7fb01bf22f668170ba5ff05be91e6f22c5b3e4edc87773dc5b0bfc69087408  tx 0xe274c22b2988acc530ca2cd77e212cb1f10c60256b5506e9d4d66b3eb49fae72
 3  170100-1 block 0x984ecaa0618540d951e95043fe363b59ae034a53ca14194faa5c14bd797c997a  tx 0x6d9d6f7c61d342e563156aa9a848711bb4c724132e79e6824cf1468b306e08b5
 4  170105-1 block 0xfff8dbd612f8b7e5d8d0655dfb92c1e37f5efd3d610fbecf6a101c165d0fc69e  tx 0x20b102c0fd1b2bf7bcafa4cdafde7644322836e1642a5e75c5056977e1e8e2a0
 5  170112-1 block 0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624  tx 0xffe640fc27e08c3bede83e1172bf077c244ba0b183f3ef3436b7103f8d2e78dc
 6  170114-1 block 0x9d34fa883f7993a8a44d74e4864afad56ab6075379e70b3694c0be620f7fc0a3  tx 0x01bedef89109fc0e0a14857c83e452927e0b43d84b9485a38b63c1423b39f83c
 7  170115-1 block 0x4fabb599f4c828fdd8055d3e1a904ea08a70d29a7b0593201bee1a46374f341d  tx 0x52629a74f9cbe18fef752bd5f49e5842ff9729c29ac62511e81a3a29858587a4
 8  170117-1 block 0xd23f13fe567c3173aa4a4a84a06c25d9e4a4a0705984507f1f3f3ce11d780239  tx 0x92448dd6d3b5bfc44dfd056c9261e54fdf653ab2dc400e3469557ca40f4d5082
 9  170122-1 block 0x94da049932c6f2cd214c423a0d0f34517faaab961bb3f69646fd9f9b027714e2  tx 0x65a7e30f27095a9ac77f01bc66d468746016f6493ccbf2fbb6bda31d8f710c0e
10  170125-1 block 0x63a4ba67dee18befcdab2e70390173e7bed78dcaf3406ae3a8a76ac832fcb398  tx 0xe24d8263bcc6840669e1a1875b638cf7030dab8f2b08990e8d436780d71c740c
11  170133-1 block 0xaa1fae018db52208466a9f4abf26890b3130cae019428438a551289da040110b  tx 0x992761a1faa4f3ef53b72f5e2a13e1bceb13c7badecf795d4573cb09dfc75893
12  170134-1 block 0xc78172b6a6dbbd6ea7483b3315587d24b390b0958247c04ed092018fed3d6000  tx 0xb2a98606ba0458ac43bc32e88862a377d8ea3e0c9cb2beca5bd3d8060b3bccda
13  170137-1 block 0xfbfde0de3232e12cfde1986fe28a0e44874079ecdf0c8bc74f92cbb04c30ca2d  tx 0xde7106b296eb5005c415b5bf55f26f59a5f7d48d6cb3e29ef1b1f231ac28325b
14  170142-1 block 0x8790daa5fd43fc45a2e407ef26c47dc7d1b32229599023c46eb6129785dbbabc  tx 0x1ec5950da440fb7e690bb636711cd04f52701ad4f4d00d8bcf2eec10db8d9eae
15  170145-1 block 0x3f3907da00159edbd8e6456682974f13bccf8216611badfb56700bdc91c0a802  tx 0x5a030cdc8ee3e91affb569b187ce3de99147e7e0241d3019edbb8cb1bdf1b4c0
16  170150-1 block 0xc27c53b0979ad62c83bdd2c64d3e5fe46f8365cd4b5d6e320d3b5bbf36e08c94  tx 0x72993cc27837580b8aa721e8a8641bdcb86b5a62800641c7b3ceb883d2651ab8
17  170153-1 block 0x2d126c6a06729c943ae91ee1fa5f39fe2352b5b3ce52390ebb7bb2e68c863903  tx 0x4ece343e5601b4e5e460f29b2cb1e51f760a4ddcf987d578bdf01f2d11f88d8e
18  170156-1 block 0xb82d68a566fac58fefe36d0c30638a84f00bb353499b65316d05c01f87057724  tx 0x81a1afb210f40bf65fec0c4b9007c8757852e2bd5933525b7b573dcea0e5a837
```

State checks (storage/events read at the step's block):

- ✅ asset 1 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the drill: vault reserves == S1 + S2: expected `103000000`, observed `103000000` at block `head`
- ✅ S1 after the gated mint == S1 + 1.00: expected `54000000`, observed `54000000` at block `0xfb7fb01bf22f668170ba5ff05be91e6f22c5b3e4edc87773dc5b0bfc69087408`
- ✅ bot refuses the over-mint (exit 1, no signature): expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ over-mint still pending (no MultisigExecuted): approvals == [A]: expected `['A (operator)']`, observed `['A (operator)']` at block `0xb15bd3765288f68e395a55247fa0af0eea5d0625554ba7b1daa34a6110b16018`
- ✅ S1 unchanged by the refused over-mint: expected `54000000`, observed `54000000` at block `0xb15bd3765288f68e395a55247fa0af0eea5d0625554ba7b1daa34a6110b16018`
- ✅ no pending over-mint after the cancel: expected `None`, observed `None` at block `0xfff8dbd612f8b7e5d8d0655dfb92c1e37f5efd3d610fbecf6a101c165d0fc69e`
- ✅ both watchers armed and level (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's reserve-chain block: expected `1622`, observed `1622` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 1 status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ bot refuses any mint while frozen (I7): expected `I7`, observed `I7` at block `bot`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `evm latest`
- ✅ bot refuses the thaw: finality has not reached the drain block yet: expected `['refused', 1622]`, observed `['refused', 1622]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `170112-1`, observed `170112-1` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ asset 1 status after the thaw: expected `Live`, observed `Live` at block `0xaa1fae018db52208466a9f4abf26890b3130cae019428438a551289da040110b`
- ✅ asset 1 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ bot refuses a set_team that changes the freezer: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ bot refuses a set_team that moves the admin off M_admin: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ asset 1 team after the co-signed set_team (ARMED): expected `[]`, observed `[]` at block `head`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-24T04:47:34Z — ERROR (24/24 steps as expected, 20/20 state checks) — source: `26e345b` (clean) — [`evidence/roles-drill-v3-20261024T044734Z.json`](../evidence/roles-drill-v3-20261024T044734Z.json) — JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- asset 4401 — 2026-10-24T04:45:14Z — ERROR (5/5 steps as expected, 3/4 state checks) — source: `586d6ef` (UNCOMMITTED CHANGES) — [`evidence/roles-drill-v3-20261024T044514Z.json`](../evidence/roles-drill-v3-20261024T044514Z.json) — AttributeError: 'NoneType' object has no attribute 'approvals' — failed: bot refuses the over-mint (exit 1, no signature)
- asset 4401 — 2026-10-24T04:42:42Z — ERROR (3/3 steps as expected, 2/2 state checks) — source: `586d6ef` (clean) — [`evidence/roles-drill-v3-20261024T044242Z.json`](../evidence/roles-drill-v3-20261024T044242Z.json) — RuntimeError: bot did not co-sign the covered mint: reserves unreadable: finalized: no provider answered a finalized reading; latest: no provider answered a lat

### Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control — 2026-10-24T05:06:53Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-attest-v3-20261024T050653Z.json`](../evidence/roles-attest-v3-20261024T050653Z.json) · result: **PASS** (15/15 steps as expected, 6/6 state checks) · source: `6eceb6e` (clean)

`ballast verify` blocks #170208..#170253 ([`evidence/verify-v3-20261024T050653Z.json`](../evidence/verify-v3-20261024T050653Z.json)): **PASS** — 4/4 B attestations PASS on both chains, 1 REJECTED (not counted), 0 FAIL/FLAGGED.

Heartbeat H = 20 blocks (drill override; production H = 100, K = 300 on this profile).

- finality (anvil): mined 65 blocks: finalized = latest − 64

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x22753E4264FDDc6181dc7cce468904A80a363E44`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1756 | `0x3931541bf6beeaa9df046c0d6d2e4ee137d0744444ef9294264736542e5dadd6` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1757 | `0xec30f111a44ea7f1a2625feeeae406a372dfbb7395a54f0c8d1ca373f0a379b1` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | bot announces watchers (BALLAST/1|watchers|t=1|m=5DG4akHnFL58yotBXtZ1tiqXeWASRh5em1i…) | `System.remark_with_event(BALLAST/1|watchers)` (B (reserve bot)) | `170214-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 2 | bot announces evm-attester (BALLAST/1|evm-attester|h160=0xc81ab822279e828b16a2be9a55520e…) | `System.remark_with_event(BALLAST/1|evm-attester)` (B (reserve bot)) | `170215-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 3 | bot posts attest (pb 170212) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170216-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 4 | bot mirrors 170216-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170217-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 5 | bot posts attest (pb 170215) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170218-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 6 | bot mirrors 170218-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170219-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 7 | A proposes mint 1.00 through M_mint | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170221-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 8 | bot B co-signs (finalized reserves cover it) | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `170224-1` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 9 | bot posts attest (pb 170225) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170228-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot mirrors 170228-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170229-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 11 | bot posts heartbeat (pb 170249) | `System.remark_with_event(BALLAST/1|heartbeat)` (B (reserve bot)) | `170252-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 12 | negative control: the judge key posts a copy of the bot's attestation | `System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key` (Judge (negative control)) | `170253-1` | Ok + System.Remarked (included — verify must REJECT it) | ✅ Ok · System.Remarked |
| 13 | bot mirrors 170252-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170253-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1  170214-1 block 0x0d4b761d645cb956f512dae0b97ef1fb72ffb44c24f3d6ab165657f5493180c6  tx 0x4c3562e9c701a4edd830af7420176596967eff5ea7bfa1150553a7f73d8746e2
 2  170215-1 block 0x96991d27f8a61aceb62e40fb10a2dc03827449cb6955e2b4b1d463bd2f99c4be  tx 0x1414a8921508ffff6c51c0f120c520338dcb93f11447bfac38b21a0018aad941
 3  170216-1 block 0x4b0ef2aa7787bed5365b5ab8b9dad840a9864a4178e8fd7cb65908f4227a760d  tx 0x625dcab0755317249606b5da8fe6b9315d83ff5703381d0a499bc653ce0beac4
 4  170217-1 block 0x40d35c389ba40456b65d27b4e5fc8921b403260a941ef8adca73df0cf8854d3f  tx 0xcb7095e3e87e53ef696407f8f7408b66597bc0dfe38146df8b75e105c09a3bac
 5  170218-1 block 0x010714a3243c38051bdaacc19d32c09f5e1755fb394836c626561891a8a1e7c9  tx 0xd882062f40fe5e83717f5b1fc7bb9ff6ef2e83f8f59cce0b48fbc95a65f2e70e
 6  170219-1 block 0x054f7d0af02aa4f4c19c868a79782da0a778d0a85e88bf3073bfa6427df7accf  tx 0xc8c8fd0d94d952fbae91f265e5895f1093e6f421f39f2d8ddeb1f58f9d24f565
 7  170221-1 block 0xe41b1aa65e5470deca1a2fc70c7f4e9cdbe66f50f7c566cede4ee273329749a5  tx 0xa1b93e2dd5d209c6e97d4a4dd1602675ba1b9f88a98dea755a445bcead3b93c7
 8  170224-1 block 0x7e53c4a58a901a96ad7317aaf74eab431d331a9e4da0a4ddf5bc1a18435c9ad9  tx 0xcb397679122a845819ea39d870c1fc996e720955cada011965dee97e74c308c9
 9  170228-1 block 0x28f7c2e671a2fff6e2b83aff45270d0afc304b3a24e71ffaae80a228701970b7  tx 0xe6365fdf3cb3b1e3a90377deb14e63b067a7467cdff6bdfc53e0e16a90dc94d9
10  170229-1 block 0x7fff3f07e4559f35e26d94733599aaccd29819f267ae0f9f0d675f38a3adec3c  tx 0xa6b855491413d8c650ad0cc22197dbabb23fffa6a05de8e7770d88765af49798
11  170252-1 block 0x34517cc1bda8ce103f045715a68a3c12b3f74f764ee9584657071e8a684a8908  tx 0xb35393c9def9e5c4a9530363fa7dccd5755dfe1f4d88b029da7dc8c485945aca
12  170253-1 block 0x515f1c6dcf46d0b648cd49e2b2f76261b577f8b0c1d14b1e9afd5ecfecab5fca  tx 0x6d4fa93541f1b25e83f0829ff02f2e32ecd5c3bbe8995e97bb34e69c8831ae21
13  170253-2 block 0x515f1c6dcf46d0b648cd49e2b2f76261b577f8b0c1d14b1e9afd5ecfecab5fca  tx 0x35c3b47ca3b75457eca093bec34be339a366a1db7affbb911249b05de5438e3b
```

State checks (storage/events read at the step's block):

- ✅ the post after H quiet blocks is a heartbeat: expected `heartbeat`, observed `heartbeat` at block `0x34517cc1bda8ce103f045715a68a3c12b3f74f764ee9584657071e8a684a8908`
- ✅ verify exit 0 and verdict PASS: expected `[0, 'PASS']`, observed `[0, 'PASS']` at block `verify`
- ✅ every bot attestation/heartbeat PASSes on both chains: expected `4`, observed `4` at block `verify`
- ✅ every oracle post matches a PASSing remark (I10): expected `4`, observed `4` at block `verify`
- ✅ the forged remark is listed REJECTED (not counted): expected `['170253-1']`, observed `['170253-1']` at block `verify`
- ✅ watcher-set and evm-attester announcements PASS: expected `[1, 1]`, observed `[1, 1]` at block `verify`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-24T05:01:57Z — ERROR (13/13 steps as expected, 1/1 state checks) — source: `8ee7557` (clean) — [`evidence/roles-attest-v3-20261024T050157Z.json`](../evidence/roles-attest-v3-20261024T050157Z.json) — JSONDecodeError: Expecting value: line 1 column 1 (char 0)

### Role split — asset 1 (breaker) + asset 2 (control), reserve vault, ReserveOracle — 2026-10-24T04:41:31Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-setup-v3.json`](../evidence/roles-setup-v3.json) · result: **PASS** (16/16 steps as expected, 6/6 state checks) · source: `775e97c` (UNCOMMITTED CHANGES)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

Reserve-chain transactions (local-anvil (not Sepolia); vault `None`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1217 | `0xcdef806dd63f8366afaf0576375093f6299df8aac2d740ccf3654edac098cdb7` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1218 | `0x286bb9ad4e337c2d68d29fc6a5fc83508ef63f86c21a1cc879f81874a823d1c7` | ✅ status 1 |
| 3 | custodian receives 100.00 test tokens | 1219 | `0xe9627e59bcf7e5538d47024bafab02ab2d873045493abd973859e6f0f99a2d53` | ✅ status 1 |
| 4 | deposit S1 + S2 = 100.00 — plain ERC-20 transfer into the vault | 1220 | `0x1457a7d9311d1136f9f82ebe6de5eb16afa1cd266ba7d1dc23edef933b0619a4` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, A2, B, W1, W2, judge, peer, M_mint, M_admin, M_watch, asset-2 keyless owner (>= ED) | `Utility.batch_all[11 x Balances.transfer_keep_alive]` (funder (human-funded)) | `169920-1` | Ok | ✅ Ok |
| 2 | A creates asset 4401 | `Assets.create` (A) | `169921-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `169922-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A creates asset 4402 | `Assets.create` (A) | `169923-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `169924-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | A mints S2 = 50.00 of control asset 4402 to the peer (its only mint) | `Assets.mint` (A) | `169925-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 7 | asset 4401 set_team(issuer=M_mint, admin=M_admin, freezer=M_watch) | `Assets.set_team` (A) | `169926-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 8 | asset 4401 transfer_ownership(M_mint 2-of-2 {A, B}) | `Assets.transfer_ownership` (A) | `169927-1` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 9 | asset 4402 set_team(keyless issuer, admin, freezer) | `Assets.set_team` (A) | `169957-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 10 | asset 4402 transfer_ownership(keyless owner) | `Assets.transfer_ownership` (A) | `169958-1` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 11 | A alone tries to mint asset 4401 (issuer is M_mint) | `Assets.mint` (A) | `169959-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B deploys ReserveOracle(attester = 0xc81ab822279e828b16a2be9a55520e475fa98678) | `Revive.instantiate_with_code(ReserveOracle)` (B) | `169960-1` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |

Block and transaction hashes (full):

```
 1  169920-1 block 0xea492def23d67d425450ee027f28afa8edefb39cdf8a6f0593bfd9729c1b207a  tx 0x570c3ba215c66071a8b5022c0997365bb2dd23bfe420d428d92761c8a8daa843
 2  169921-1 block 0xb133784fdabeb45d87876758c037968dab8546a8861ef08ea64cf5c8ec73d687  tx 0x24dc146315456dfa14072e86df72bf041344fd9c5f7f408baf455f2718fbf996
 3  169922-1 block 0xeb348b8e9ffc6dc28d351b8bf7f4a8d3bf8933fbfe004fb0909e91d738bb8b52  tx 0xb82458706e543a051ee0b51090df052fba28d52c94497959d9927af3fb51bc5d
 4  169923-1 block 0xbb856146bc8e4ff9efbe4a98f03eb34fab13539d42ee3c03bf03e63519d8bb9d  tx 0xe638b768f30432387b6691707b3c4c4ffdfc4e8ca7b5e635027d8e3d913d92a4
 5  169924-1 block 0x71c5d6740f3440157f4b412193d24e2f6156a9f1fff06a9ed2652239cd3ccbed  tx 0x36e7a73d522a15f17f2c582e1013b6124841a4124612141167ff19de0488d659
 6  169925-1 block 0x15bb692aaed874918cd048e82155490e326780b565cdf27dadfc183158df44d8  tx 0x60ee01d6bd5a7da766393bc3b529ddb77a7103197bdf11a147b507352b947472
 7  169926-1 block 0x19957ce710fd64082c8c454aad7479d40a0e98d9442e2fa657a2d1db4302f95a  tx 0x1e9dc3660f13efb29b28223cd2e88852a565dc48947b94464b9ea640065cf206
 8  169927-1 block 0xa4f52bc314c19f34bb0ee49dcf9f7a7cd1f9a56dc5402a060aedfcd3bf31b11f  tx 0x068aebe8fb136523fb6ab19f09e6073b7c5869982eaf08dd6bb7329cc573b5e7
 9  169957-1 block 0x10a90c345e560952ee6baa65993de08c5c4bc348e28916b8ad953cd7b25ed8ab  tx 0xe57be6e7ec3166ee92ab1ba20503d250e7e4f653722a4eb646ebc2edb1563a26
10  169958-1 block 0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3  tx 0xe0c32994b778fc51ddcc6d8d038177ef05bb81f879e6554ceff8d24ff174c952
11  169959-1 block 0x078f168764203e0c076de640e1ab233236b4fbf8ac5c1a0bd16a38b7e0d90e9f  tx 0x158e4d7b115230664149d6318f23bb1fe85f89ea87640e24a9f0b5c877775427
12  169960-1 block 0xe94805cffe1a16d9351b858dcb4f227d65da58f1054212e3e3c21da218096d9b  tx 0x625a2b66602be315de99809a64a73e6db88f1cbb698b935e80728ad4a1478e97
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after the deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ vault reserves() on resume (same local anvil vault): expected `100000000`, observed `100000000` at block `evm latest`
- ✅ asset 4401 team == role map (owner/issuer = M_mint, admin = M_admin, freezer = M_watch): expected `[]`, observed `[]` at block `0xa4f52bc314c19f34bb0ee49dcf9f7a7cd1f9a56dc5402a060aedfcd3bf31b11f`
- ✅ asset 4402 team == keyless accounts (S2 can never change): expected `[]`, observed `[]` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`
- ✅ supply S1 (asset 4401) before the gated mint: expected `0`, observed `0` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`
- ✅ supply S2 (asset 4402): expected `50000000`, observed `50000000` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`


### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 4501 — 2026-10-30T22:47:55Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-v3-asset4501.json`](../evidence/drill-outage-v3-asset4501.json) · watchdog log: [`evidence/drill-outage-v3-asset4501.watchdog.jsonl`](../evidence/drill-outage-v3-asset4501.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `15d40cd` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=4501|reason=providers-down|s=100000000|down=20s|p=down-1,down-2`

Timing (wall-clock on one machine; Portaldot V3 testnet + local anvil reserve (not Sepolia)):

- `trigger_head`: 258719
- `freeze_block`: 258720
- `freeze_block_timestamp_ms`: 1793400570000
- `submit_to_inclusion_s`: 5.64
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 26.42
- `down_for_s_in_remark`: 20s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x40918Ba7f132E0aCba2CE4de4c4baF9BD2D7D849`, token `0x8A93d247134d91e0de6f96547cB0204e5BE8e5D8`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1824 | `0x98e94ae1321d3b8e04ae15df249e8c9756d4cda09ac83427b96def0f7b47d724` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1825 | `0x71bc9611ce77ce454890f2ad4d7ff005bafcc189edc4cb2c9d76feedaceed6ad` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1826 | `0xa4996647b58f0393e389cf5e0fc62756552a19417d842ad143b9f70e42c36dae` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund the accounts below their working balance (A, W1, W2, judge, peer, M_watch) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (funder (Alice on a stand-in)) | `258706-1` | Ok | ✅ Ok |
| 2 | create asset 4501 | `Assets.create` (A) | `258707-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `258708-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 4502 | `Assets.create` (A) | `258709-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `258710-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 4501: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `258711-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 4501 to the judge | `Assets.mint` (A) | `258712-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 4502 to the peer | `Assets.mint` (A) | `258713-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 4501 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `258720-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `258721-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1  258706-1 block 0x0e43dff970c683280c3e63950402350cd5711cddb781152be7abaf89a9189780  tx 0xb9e27cf830ac38165c15e6e61b015fbd5d71e3f18034af7a568f1cd232389ac5
 2  258707-1 block 0x67c678637d4dea7eabc6b4a6cf46d8561006d92146b66ece396f2b8438781e0b  tx 0xd78a24326a66e00feb5a00049c7cb7c281c420def6709a3c986d8a6617ff8368
 3  258708-1 block 0xc9e8f8302c89bc4e1a994018633b0d6fd2fe57170c93c7936ded9ad7dc86486d  tx 0x56d7a745a50eef46206a4370c81c3999fe6bec0fc881bb025dbe52b23b34ffb6
 4  258709-1 block 0x9063938ba249d494d04cd4d311315765a509f63622dfecf158be251bac3d1b54  tx 0x5931607e13934af799087ff97e227a4228064237a621e4d1119c3bd181e1359c
 5  258710-1 block 0xc35b231803a12f1fd362022e1d7ba10cd990dfa93351f5844506d5dfa881283b  tx 0xe72b4212d7616c7071c8e86dbef433ff6955688241a75275b41413b9cc363cd1
 6  258711-1 block 0xb6e89d8349349d4fd06cd097a3077ae401c4e327db83a6959cacfe8e89a5cac3  tx 0x046f81185bfd7ba18d7612647e6ddaf935dda626e3699d2056b9bac43328067f
 7  258712-1 block 0x935de390b07150d0b44ba8cbea96372306069ef5361e0f0ff1453e285bdc8bf8  tx 0x6a7663349901517353d5e38af08afbea30c13bfb52be43c13a4d22e83562dedd
 8  258713-1 block 0xeb2e493d6a0f797ff04641873c1e98ceb7ce80437213cde823dfb39cef163951  tx 0x576ac822aff509221699da0fb54032bfb7173f8f38d29afde2dbe1974204da2e
 9  258720-1 block 0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c  tx 0xd21e2d8ad22305bd6f63b883e5cd5de473dd8dffb57ab8eeaa8df69474bb65a8
10  258721-1 block 0xcb0cd004500b5dc128f57ed3acf06adbb713ec44c7d3332755696732ab054a97  tx 0xa079bad02d1b9f40b045e83293b567174d46f513f081cafba59def9951263c81
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xeb2e493d6a0f797ff04641873c1e98ceb7ce80437213cde823dfb39cef163951`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(4501).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x388e7b8238abc434264932518ae8d105ca5cd879f5c8024baea3dba28c37420d`, observed `0x388e7b8238abc434264932518ae8d105ca5cd879f5c8024baea3dba28c37420d` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ control asset 4502 untouched (Live): expected `Live`, observed `Live` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xcb0cd004500b5dc128f57ed3acf06adbb713ec44c7d3332755696732ab054a97`


### Breaker drill (heartbeat: no bot heartbeat for K blocks -> freeze (I8)) — asset 4503 — 2026-10-30T22:49:54Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-heartbeat-v3-asset4503.json`](../evidence/drill-heartbeat-v3-asset4503.json) · watchdog log: [`evidence/drill-heartbeat-v3-asset4503.watchdog.jsonl`](../evidence/drill-heartbeat-v3-asset4503.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 9/9 state checks) · source: `15d40cd` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`, `--heartbeat-k 10`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=4503|reason=no-heartbeat|s=100000000|b=5FepBwxQ2eEeXht8594bJkVep9CTEBua3Abf4rgph7FMjjtg|n=0|since=258734|k=10`

Timing (wall-clock on one machine; Portaldot V3 testnet + local anvil reserve (not Sepolia)):

- `trigger_head`: 258744
- `freeze_block`: 258745
- `freeze_block_timestamp_ms`: 1793400720004
- `submit_to_inclusion_s`: 4.95
- `heartbeat_k (drill override; production K = 300 on this profile)`: 10
- `nonce_first_seen_block`: 258734
- `blocks_nonce_still_to_freeze_included`: 11

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x99dBE4AEa58E518C50a1c04aE9b48C9F6354612f`, token `0xd6e1afe5cA8D00A2EFC01B89997abE2De47fdfAf`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1827 | `0xdc102b390e9746061dfe5620168a911da3277295bca5147f8ff7e1c8efe454ee` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1828 | `0xe4c0347b26657f8ff41def740d52ca6113c747506da1cfa1cc7391837a9cfdaa` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1829 | `0x5b579ade4470bc111748bf88b4ed0f2c0e4ff5b4a0f91bac3147842fae4ee67f` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund the accounts below their working balance (A, W1, W2, judge, peer, M_watch) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (funder (Alice on a stand-in)) | `258725-1` | Ok | ✅ Ok |
| 2 | create asset 4503 | `Assets.create` (A) | `258726-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `258727-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 4504 | `Assets.create` (A) | `258728-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `258729-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 4503: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `258730-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 4503 to the judge | `Assets.mint` (A) | `258731-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 4504 to the peer | `Assets.mint` (A) | `258732-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 4503 via M_watch, reason on chain (reason=no-heartbeat) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `258745-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `258746-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1  258725-1 block 0xa4f7698fa9114133de78b1efec4149a21c8b19bd3236ce7b911785870e96c596  tx 0xbb8255872f98ec108af20dc3f800797b0c51021fb0374d484eab793e5ae9c277
 2  258726-1 block 0xc05b9a96827fda3291fb1fa3f17d97f72e9d10dd453c66303870e86619a8b803  tx 0x65331727feb169853f727bf9b689b13c02d8a56a6e893cd50a95c9919a3aea1a
 3  258727-1 block 0xa6f135545e47505a4935b59c0983bf3c1d3f7752b3cdf47754eda5da6260ff21  tx 0x31e1cfff29b741240b700aa093f7e3602a75083bd0e1f1e90c6ba1b590a14f50
 4  258728-1 block 0x6490f88c48a273d329f928cd9e2bfbb1b88a98215e8c06f481a71d68d8bb157c  tx 0x61d20055979d7bca119c38ced921d5cbda8a7b1cb7720de5c826762a8555c787
 5  258729-1 block 0x41d1cdb71463f2faee0150af94b0854a3208923a267ceb48b8615c703d81693b  tx 0xa261f31a598144e157e0b0f35a3f1d08a8ac963d5d27e709554376d3e17197a1
 6  258730-1 block 0x598985bd794b4f8f26c260dff8a2ca99ade3b2653fd857e6dbd81c1ab19d3c34  tx 0x8712809721d9e33f43fda8d7b7b773b6d4c3ee6b237399858ad0e36d5b3d34f4
 7  258731-1 block 0x04234e67ddeaebe6efb3d7583973842c63fd87109ce5cd39b0ce98d29f62dd12  tx 0x7734e77ffdfbbc632cfa1aca79e450f7636e8b13013467d18598eff1de2adb8f
 8  258732-1 block 0x97b7732ba768dfa846b5401c7d38e425cf26f888055089b34e3dfea410485fe3  tx 0x75a90709a50c7d032b49bfebd6edeeb0f1293ce0a219ba0f882f34460d68df79
 9  258745-1 block 0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d  tx 0x9e3d2d078aa7e270c9dd8fd31b91769fe7666b49a7d4f2d007380d7d9b56535d
10  258746-1 block 0x7a74bead3a76815fc03101511fd55fcd0285737060e2fc825d9b19b664b25e54  tx 0xeb76558759ae4019a88bffb48ad70baf1aafa8d5236efc2a1497492f8cbad18d
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x97b7732ba768dfa846b5401c7d38e425cf26f888055089b34e3dfea410485fe3`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(4503).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x9763564d95f5f31100b81512a28eccdc5c37f82afb32e4f7f0ab94bc19511473`, observed `0x9763564d95f5f31100b81512a28eccdc5c37f82afb32e4f7f0ab94bc19511473` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ control asset 4504 untouched (Live): expected `Live`, observed `Live` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x7a74bead3a76815fc03101511fd55fcd0285737060e2fc825d9b19b664b25e54`
- ✅ the triggering check saw the bot nonce unchanged for >= K blocks: expected `True`, observed `True` at block `watchdog log`
- ✅ reserves were level at the trigger (the freeze is the heartbeat rule alone): expected `[]`, observed `[]` at block `watchdog log`


## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain (before the Portaldot V3 testnet was reachable). Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). V3 runs, once funded, are listed in `docs/PROOF.md`.

Earlier V3 reachability probe (the old DNS names): [`evidence/v3-probe-2026-10-14-p5.txt`](../evidence/v3-probe-2026-10-14-p5.txt) (V3 reachability probe — 2026-10-14T14:59:52Z (P5)).
Current V3 identity (read-only day-0 check): [`evidence/v3-day0-20261020T152616Z.json`](../evidence/v3-day0-20261020T152616Z.json).

### Governance drill — announced watcher-set + M_admin rotations, community watcher, wind-down, redemption — 2026-10-31T01:21:28Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-governance-standin-upstream-20261031T012128Z.json`](../evidence/roles-governance-standin-upstream-20261031T012128Z.json) · result: **PASS** (30/30 steps as expected, 16/16 state checks) · source: `d296528` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

- watchers: W1, W2 and W3 run on ONE machine; W3 plays the community watcher (no separate operator yet)
- funding: {'wanted': {'A (operator)': '15919000000000000', 'W1 (watcher)': '500000000000000', 'W3 (community watcher)': '1000000000000000', 'Judge (holder)': '500000000000000', 'Peer (holder)': '300000000000000', 'B (reserve bot)': '2000000000000000'}, 'topped_up': 1, 'ed': '100000000000000', 'multisig_deposit': '1119000000000000'}
- community_freeze_seconds_after_drain_sent (one sample, poll every block): 3.72

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xB0f05d25e41FbC2b52013099ED9616f1206Ae21B`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1830 | `0xd3f049a1cadc663a175a4434f141fb23f35b94b3500072d32601d74f14724078` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc), owner = custodian | 1831 | `0x5c1999dea676c727482dc16a8c4c32a4ba73b447c8d5ef6a49cecb3b5a3b09c5` | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 | 1832 | `0xaa656cd944cabe5693bfe0627ff34e26db8d875e82631347c934777e675a83f0` | ✅ status 1 |
| 4 | custodian drains 30.00 (30%) from the vault | 1833 | `0x93266a7aeed015b75ae5cc28b73053e0f2664760cd52f582573bb809db0ad711` | ✅ status 1 |
| 5 | custodian releases r x 30.00 = 21.00 to the judge's EVM address, redeemId = redeem_id(9004-2) | 1834 | `0x17215858d3b3a28147525fb7930f23ad59f23f7cf28d246244edac0a828636b9` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | funder tops up the accounts below their working balance | `Utility.batch_all[1 x Balances.transfer_keep_alive]` (5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY) | `8943-2` | Ok | ✅ Ok |
| 2 | A creates scratch asset 3001 | `Assets.create` (A (operator)) | `8944-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-gov (6 decimals) | `Assets.set_metadata` (A (operator)) | `8945-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A mints 30.00 to the judge (scratch S1, before the team hand-over) | `Assets.mint` (A (operator)) | `8946-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 5 | A mints 20.00 to the peer (scratch S1, before the team hand-over) | `Assets.mint` (A (operator)) | `8947-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | A hands the team over: issuer M_mint, admin M_admin, freezer M_watch {W1, W2} | `Assets.set_team` (A (operator)) | `8948-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | A transfers ownership to M_mint | `Assets.transfer_ownership` (A (operator)) | `8949-2` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 8 | A proposes set_team(freezer = M_watch' {W1, W2, W3}) through M_mint | `Multisig.as_multi(Assets.set_team(freezer=M_watch')) — first approval` (A (operator)) | `8950-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | B announces the watcher set {W1, W2, W3} 1-of-3 (BALLAST/1|watchers) | `System.remark_with_event` (B (reserve bot)) | `8951-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot co-signs (cosign-team --announcement (after K)) | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `8957-2` | Ok, executed | ✅ Ok · inner Ok |
| 11 | W1 tries to freeze through the OLD M_watch {W1, W2} | `Multisig.as_multi_threshold_1(Assets.freeze_asset) via old M_watch` (W1 (watcher)) | `8958-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B announces the admin set {A, A3, B} 2-of-3 (A2 retired; BALLAST/1|admins) | `System.remark_with_event` (B (reserve bot)) | `8959-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 13 | A proposes set_team(admin = M_admin' {A, A3, B}) through M_mint | `Multisig.as_multi(Assets.set_team(admin=M_admin')) — first approval` (A (operator)) | `8960-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | bot co-signs (cosign-team --announcement (admins, after K)) | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `8965-2` | Ok, executed | ✅ Ok · inner Ok |
| 15 | W3 (community watcher) freezes through M_watch' once every provider reads short at one block | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W3 (community watcher)) | `8978-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 16 | judge transfers 1.00 while the asset is frozen | `Assets.transfer` (Judge (holder)) | `8979-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 17 | W3 freezes the judge's account through M_watch' (wind-down step 1) | `Multisig.as_multi_threshold_1(Assets.freeze)` (W3 (community watcher)) | `8984-2` | Ok + Assets.Frozen | ✅ Ok · inner Ok · Assets.Frozen |
| 18 | B posts final r = 70.00 / 100.00 = 0.7000 (BALLAST/1|final) | `System.remark_with_event` (B (reserve bot)) | `8985-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 19 | A proposes thaw_asset through M_admin' | `Multisig.as_multi(Assets.thaw_asset via M_admin') — first approval` (A (operator)) | `8986-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 20 | W3 freezes the peer's account through M_watch' (wind-down step 1) | `Multisig.as_multi_threshold_1(Assets.freeze)` (W3 (community watcher)) | `8987-2` | Ok + Assets.Frozen | ✅ Ok · inner Ok · Assets.Frozen |
| 21 | bot co-signs (cosign-thaw --final (all holders frozen)) | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `8988-2` | Ok, executed | ✅ Ok · inner Ok |
| 22 | judge transfers 1.00 after the thaw (account still frozen) | `Assets.transfer` (Judge (holder)) | `9003-2` | Err(Assets.Frozen) | ✅ Err(Assets.Frozen) |
| 23 | judge asks first: BALLAST/1|redeem with its EVM address | `System.remark_with_event` (Judge (holder)) | `9004-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 24 | A proposes batch_all([thaw(judge), burn(judge, 30.00)]) through M_admin' | `Multisig.as_multi(Utility.batch_all[thaw(judge), burn(judge, 30.00)] via M_admin') — first approval` (A (operator)) | `9005-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 25 | bot co-signs (cosign_redeem) | `Multisig.as_multi(Utility.batch_all) — final approval` (B (reserve bot)) | `9006-2` | Ok, executed | ✅ Ok · inner Ok |

Block and transaction hashes (full):

```
 1    8943-2 block 0xb6ba808b9d4eb9938b5a78afee1daa9321b7242ce1cdeb989468921f18e5ee82  tx 0xddb0d1928c41d91c75f338a63bcda678e28cb875921500cc9dc061cd113c2c0e
 2    8944-2 block 0x3e5e06e083c32446bca051f9e4416acd09272629913ca00d7a9c4fe32db44cc0  tx 0xf5af6f159c24780baea182a72056d2032e48709685ffd203f31193991426b560
 3    8945-2 block 0xf470671c5941710dcfb1b2c1cd36739c4f06e43fee2861c965ff643dfae5b118  tx 0xbeb6ff99e14ef8ea1ad6a3e6a47ea582c928cfd56c139a03061d580ae5e5711b
 4    8946-2 block 0x7ca71e98f46a9daa5fb06743f13bd38738db17f80dcd1335fe717145efdabe61  tx 0x9cae62be6c746ded2380ce05d7da45b1961e202ee022d94c5c0e2c4bc8e6b04b
 5    8947-2 block 0x238fb1376624b87e72e5397c8738efbb8a3aa102daee4de5ea04d1b7125c7c9a  tx 0xf92700402da7f431421097cb39dff5b294aa90fa745a6d2f9659ff86478d552b
 6    8948-2 block 0xa29f741093c78a9282b90aa022b12659ec71a4844b645449b922ac8a667d8549  tx 0x64abc37f46af73c5e5eab681cb117d2685fc675844419d4fa038022f13782ec5
 7    8949-2 block 0x8f91eaa5808dc097afa437470fd81ec12960041d2bcde1ff16a4773ac8b74884  tx 0x7169d35670f4b4cb008812fab8440f2d75ce4bc1207f5981bce6b1cc2c884eba
 8    8950-2 block 0x6991091cc60d01cd1a4a1098a75cbda200cb11044bf736b572052755b3b52b05  tx 0x8bcf997b09b4e0cf92cc32b51492bd95ed5850eb9156f26f48926a9ea358f79b
 9    8951-2 block 0xf4ecfbfc243a2ba5e1c7bb57a6147c64913e1c85f760f3b56f96f07c7945029f  tx 0x28810a6c673e7ad35ff4593fb43ec107ac06e82d44a70def208379e5f9fd5921
10    8957-2 block 0x191fed26d77e0d6096a8de377360584dee6d2cfc1313fcf12c16ce502e9ebd15  tx 0x270d18fd9f8e479c315726aca23312417d8a485ed6ecace264336624b77d2da8
11    8958-2 block 0x41351ece5a3996a6fa9b02e0ee736183de3682f2af3053426edcbd61ea6d224c  tx 0xeb646ae3989c4d3efc7fee1c441d2ddf0d17ebe1565946ede1dd455416a87296
12    8959-2 block 0x63d2e607177ba200ec07cfe3867439ef9f0b11c37c9db0e05306f57b3d38abb2  tx 0x0d5a683c674ebb13542dc1028adbe867c5fc11b0decbc1b673ed6ffe6d67a246
13    8960-2 block 0x4dace1ce0bf37d2e1c958aa312e801d3614b12726e08df32a08896bb5b724a13  tx 0xcf713b28c442062b1786e47829929b1dec22b18d2c5b040877b228ce00140693
14    8965-2 block 0x2b64ba40eeaaf91ea3699e283c5f1e8341ff47c025297902febe2952708e6a36  tx 0xd6608a04bd3379ea4d1c4e8d2f8600c22ddeb9dd8992ae633030e813c9efc063
15    8978-2 block 0xc2f79eadeda4f06f7cd872dd4f49ad5ee42e99a79260c437e1c8e264316dda74  tx 0xca594ba44626772a25b755c072022885437e7d0cf4deb4ea4a4e08aa1317f354
16    8979-2 block 0x668fbbe5eb9e9ecbc3adcadf28b4a218a5c86931bc7854b4b8d89d305c5a1ce4  tx 0x3189606be5b73c5dcad0d58e94e2f897206de306b42c14df5a335db3b8d2ca7c
17    8984-2 block 0x954bb22f1b0ead10d3b8e8b78df0141d72e7362fef1444bcb4b65e0572af8497  tx 0xe479a94173a0a94a74e298d4760f6f88ff6eba9e686a34c4bf9047d4dcc1ce2a
18    8985-2 block 0x767fcd7073ee75cf14395b1efc5c12ac4d0d4c63e013e48fb93b2227c3ef712b  tx 0x6e3f6317c527377528ca33997571cb855f8152e672aa781e9e7a6becf243e37f
19    8986-2 block 0x499d188b9e9bbdd0319f067a1427b6f241ee3055f6bf261e2121778592c2f964  tx 0x543e977ca7eb136f87dc014633bd521754ec34eb51adc5d4c4b6a3117c99531e
20    8987-2 block 0xd7860dd65d1cf1384d176cbfa2503fd47ed824bdf99850c44147f3f8cfbd573f  tx 0x22af2e295b3be94b673dbcf86e84b82e7554747c74b11589a22a6c3f88dd270d
21    8988-2 block 0x4c1e356452ad2ce3482622abeb5d782f89eb51b8678c326063c2ed3933c587fb  tx 0x712338d2e5173827434439327da4fe9850f34caf8ef04c3459c92818a5b02392
22    9003-2 block 0xb0465431123c2776ddb939ffc374627e806a29c4c4f89fb459698d3c8f50c4d7  tx 0xa93db25e7f3c4f4e9e9abebb20f7ce50ccf4b4b95fb2daa505a5ae535b201c1e
23    9004-2 block 0xe22f48813d99a67107f3b5906fe7c5cb4ddbfaa0868eeb182d2d7d61aaf1042d  tx 0xa2622da69d9f46d46f80b8a10492ddf158cb92960df1a4eda50b3419ab3fe19d
24    9005-2 block 0x8e52968f00b80eea780498287cb3e728d3210cc40dcfd618818b788353780ea1  tx 0x464a8cf533bd249515be921a9f8bcd71bb8e68c119d4b7f74633e8442687e88b
25    9006-2 block 0x081cc662d20bf082fae62678b35191ac5a5d518a5012f6332e1bdef87c44a39c  tx 0x7e76d85e16bfd30335d29b5d286e88870642bdc2f2e055454d14c661d4dba44b
```

State checks (storage/events read at the step's block):

- ✅ scratch team == role map (owner/issuer M_mint, admin M_admin, freezer M_watch): expected `['5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb', '5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb', '5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM', '5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D']`, observed `['5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb', '5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb', '5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM', '5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D']` at block `0x8f91eaa5808dc097afa437470fd81ec12960041d2bcde1ff16a4773ac8b74884`
- ✅ bot refuses an unannounced watcher rotation: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ bot refuses before the announcement is K blocks old: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ freezer after the co-signed rotation == M_watch': expected `5D7DdmaALPZvdHJWgYPMz5v4S1mArz8dMGQQPU7iBaiiosiK`, observed `5D7DdmaALPZvdHJWgYPMz5v4S1mArz8dMGQQPU7iBaiiosiK` at block `head`
- ✅ asset still live after the old set's attempt: expected `False`, observed `False` at block `head`
- ✅ admin after the co-signed rotation == M_admin': expected `5H1nwMQ7pu98XrgqoxY84uTacpKxEohv9MJsq6HPyoyJCcGq`, observed `5H1nwMQ7pu98XrgqoxY84uTacpKxEohv9MJsq6HPyoyJCcGq` at block `head`
- ✅ community watcher, every provider down for 30 s: exit 4 (not frozen), no freeze submitted: expected `[4, False]`, observed `[4, False]` at block `watcher log`
- ✅ …its checks all read 'outage' with 'never fail-closed': expected `True`, observed `True` at block `watcher log`
- ✅ the freeze's trigger: community mode, pinned block, every provider short: expected `['community', True, 2]`, observed `['community', True, 2]` at block `watcher log`
- ✅ bot refuses the wind-down thaw while a holder is open: expected `['refused', True]`, observed `['refused', True]` at block `bot`
- ✅ asset live after the wind-down thaw: expected `False`, observed `False` at block `head`
- ✅ every holder with a balance individually frozen: expected `[['Judge (holder)', True], ['Peer (holder)', True]]`, observed `[['Judge (holder)', True], ['Peer (holder)', True]]` at block `head`
- ✅ community watcher after the thaw: deficit but winddown-hold, no freeze (exit 4): expected `[True, False, 4]`, observed `[True, False, 4]` at block `watcher log`
- ✅ the redemption executed atomically: Thawed + Burned in one extrinsic: expected `[True, True]`, observed `[True, True]` at block `receipt`
- ✅ after the redemption: S1, reserves, and r unchanged: expected `[20000000, 49000000, '0.7000']`, observed `[20000000, 49000000, '0.7000']` at block `head + evm latest`
- ✅ the judge's EVM address received r x 30.00: expected `21000000`, observed `21000000` at block `evm latest`


### ReserveOracle v2 — trip() by a listed watcher, cleared only by a later post — 2026-10-31T01:17:58Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **none — the oracle mirrors B's attestation; this drill posts a fixed drill status** · raw JSON: [`evidence/oracle-trip-standin-upstream-20261031T011758Z.json`](../evidence/oracle-trip-standin-upstream-20261031T011758Z.json) · result: **PASS** (9/9 steps as expected, 9/9 state checks) · source: `910048a` (clean)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | W1 maps its account in Revive | `Revive.map_account` (W1 (watcher)) | `8873-2` | Ok | ✅ Ok |
| 2 | W2 maps its account in Revive | `Revive.map_account` (W2 (watcher)) | `8874-2` | Ok | ✅ Ok |
| 3 | Judge maps its account in Revive | `Revive.map_account` (Judge (not a watcher)) | `8875-2` | Ok | ✅ Ok |
| 4 | B deploys ReserveOracle v2 (attester = B, watchers = W1, W2) | `Revive.instantiate_with_code(ReserveOracle)` (B (reserve bot)) | `8876-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 5 | B posts a backed drill status (pdBlock #8876) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `8877-2` | Ok + Revive.ContractEmitted | ✅ Ok · Revive.ContractEmitted |
| 6 | Judge (not a listed watcher) calls trip() | `Revive.call(ReserveOracle.trip)` (Judge (not a watcher)) | `8878-2` | Err (NotWatcher revert) | ✅ Err(Revive.ContractReverted) |
| 7 | W1 (listed watcher) calls trip() | `Revive.call(ReserveOracle.trip)` (W1 (watcher)) | `8879-2` | Ok + Revive.ContractEmitted (Tripped) | ✅ Ok · Revive.ContractEmitted |
| 8 | B posts frozen=false with pdBlock = trippedBlock #8879 (a reading not after the trip) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `8880-2` | Err (TripNotCleared revert) | ✅ Err(Revive.ContractReverted) |
| 9 | B posts frozen=false with pdBlock #8880 > trippedBlock | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `8881-2` | Ok + Revive.ContractEmitted | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    8873-2 block 0xb354ebd0a7c657a4586236f7b234426b3462345f79559bf9194018400fae6bc9  tx 0xd4a5287291ba867ce1e88f5e46ddbab1e7bd9061a3c29d81a178d2474d24e61d
 2    8874-2 block 0xf64f36e4043e0e7dc9792616242902ac469f12d723aa712887bdca5573ede46b  tx 0xca36feb8775974b0f3a6b499990ec5b03fb36f55b3150e03f11addd84741173a
 3    8875-2 block 0xca4fbeb0e95321d2d5fe958d8cb126f0a31ccefec6044906d72c473419b02773  tx 0xf609f9e7f7340113bc006684ecf59ee50df61e10f42407e384389d6d74c25dbd
 4    8876-2 block 0x4e06f8092ce6a60977acc605e7a52703f86093bfef7bcd47141d390cd2262801  tx 0xc956f1c675ef449f9eb7e614e672a9a4b73db7b3f173c2b2f8e00b7ae3edd7ae
 5    8877-2 block 0xe759abc314dbef318caebbf912abd16fd71f4a492a7d04fa5690f17da2f3fbdf  tx 0xea6042f09df3ec0e823793fd652ab71ae0d59347087276b38596a133537a5b50
 6    8878-2 block 0x7e9fbb48caae21e08209e50fd013b4feed3a25133a689d3608ec7d5e4f382521  tx 0xdab257a0b4229d2d10b2e6f33c64d78fc3994c7375941d2c71c0185c9f690e74
 7    8879-2 block 0xa957d224bbad7bc348cedaff1cddcbd8630bc753f3f478d1bba160d7a1f6b01d  tx 0xc2ff4fa9bacfea722b701ccd2026f8936784a09e086186527378f2fc20c758fd
 8    8880-2 block 0xbbaa2a9e211c3e4d6bcc8ac65bf34db5e9f470c581ef1c7707d57f3c5e94dd92  tx 0xa96f7b37dbb5215f182ebb96c8f2034f363570a67282512df9e0a27ef2979bae
 9    8881-2 block 0x30b567b75e8ac914499dd94cdcaa39d9c552e6cac4c3ca009e272dc08c09451c  tx 0x1fa823380e9368307d7c2eb3d4e05a6a95cc6651b673af42c40adf3c5a05dcad
```

State checks (storage/events read at the step's block):

- ✅ watchers() == [W1, W2] H160: expected `['0x8bc7fdbd3f6c91b9f622f8c4c20ae7050ca1d9e8', '0x04c14605607939412a6e0d191d52d573bc6ffc41']`, observed `['0x8bc7fdbd3f6c91b9f622f8c4c20ae7050ca1d9e8', '0x04c14605607939412a6e0d191d52d573bc6ffc41']` at block `0x4e06f8092ce6a60977acc605e7a52703f86093bfef7bcd47141d390cd2262801`
- ✅ isBacked(3600) after the backed post: expected `True`, observed `True` at block `0xe759abc314dbef318caebbf912abd16fd71f4a492a7d04fa5690f17da2f3fbdf`
- ✅ isBacked(3600) unchanged after the refused trip: expected `True`, observed `True` at block `0x7e9fbb48caae21e08209e50fd013b4feed3a25133a689d3608ec7d5e4f382521`
- ✅ trippedBlock() == the trip extrinsic's Portaldot block (Revive block.number): expected `8879`, observed `8879` at block `0xa957d224bbad7bc348cedaff1cddcbd8630bc753f3f478d1bba160d7a1f6b01d`
- ✅ status().frozen after the trip: expected `True`, observed `True` at block `0xa957d224bbad7bc348cedaff1cddcbd8630bc753f3f478d1bba160d7a1f6b01d`
- ✅ status().reserves / pdBlock unchanged by the trip: expected `[100000000, 8876]`, observed `[100000000, 8876]` at block `0xa957d224bbad7bc348cedaff1cddcbd8630bc753f3f478d1bba160d7a1f6b01d`
- ✅ isBacked(3600) after the trip: expected `False`, observed `False` at block `0xa957d224bbad7bc348cedaff1cddcbd8630bc753f3f478d1bba160d7a1f6b01d`
- ✅ isBacked(3600) still false: expected `False`, observed `False` at block `0xbbaa2a9e211c3e4d6bcc8ac65bf34db5e9f470c581ef1c7707d57f3c5e94dd92`
- ✅ isBacked(3600) after a post from after the trip: expected `True`, observed `True` at block `0x30b567b75e8ac914499dd94cdcaa39d9c552e6cac4c3ca009e272dc08c09451c`


### Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw — 2026-10-14T15:02:11Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-drill-standin-upstream-20261014T150211Z.json`](../evidence/roles-drill-standin-upstream-20261014T150211Z.json) · result: **PASS** (22/22 steps as expected, 20/20 state checks) · source: `1f8e351` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

- other watcher: W1 saw asset 1 already frozen at #6902 and stood down
- drain -> freeze included (wall clock, one machine; local anvil + stand-in): 5.48 s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1006 | `0xae18933879519e8b137e166d09cb2058511c831ad8e4cc10afd07e8fa8c392cc` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1007 | `0x9ba4145e34f883cd763ce305c7f51f6be31bbb4cb1b9c754cf18247f333d37f5` | ✅ status 1 |
| 3 | custodian drains 30% (33.00) — release() | 1073 | `0xcb98e7e298af7f520c56441990a28eaa7e43691215cb146fae9da34bfeeed7e1` | ✅ status 1 |
| 4 | custodian re-deposits 33.00 | 1074 | `0x842c2450a059d3bb5812aa4b4d01f7131bc8b13ebe2d31e80267dafbbd631e8a` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | A proposes mint 1.00 to the judge through M_mint (first approval) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6894-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 2 | bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6895-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 3 | A proposes 0.01 more (reserves cover S1 + S2 exactly) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6896-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 4 | A cancels the refused proposal (deposit returned) | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6898-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 5 | watcher W2 freezes asset 1 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `6901-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 6 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6903-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 7 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `6904-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | A proposes a mint while frozen | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6905-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | A cancels it | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6907-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 10 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `6908-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 11 | bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `6910-2` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 12 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `6911-2` | Ok | ✅ Ok |
| 13 | A proposes set_team with the freezer moved to A (through M_mint) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6912-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | A cancels the refused team change | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6914-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 15 | A proposes set_team making A the sole admin (could thaw without the bot) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6915-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 16 | A cancels the refused admin swap | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6917-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 17 | A proposes set_team keeping issuer M_mint, admin M_admin, freezer M_watch | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6918-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | bot co-signs the safe team change | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `6920-2` | Ok + inner Ok + Assets.TeamChanged | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.TeamChanged |

Block and transaction hashes (full):

```
 1    6894-2 block 0x56824cf364f515bebfddfb0af7a2c5c2111ed4e664c40fe443b13c47a137697a  tx 0x893b2ff5cf15d431698688b5066430cb7aca5514acd12d424d316968b8b85001
 2    6895-2 block 0x83e6b95a19cd4a9d8dff976df821a2d19c3c47eaa5c380f80856fa7c3f2e15a6  tx 0xa44b3e7f322b9e4d46ba623e80f3d717feb35ea814f41369ceab32d3f847adac
 3    6896-2 block 0x275348a1cb414c173d942a34ae61ad98e922eab93226a541549ebe97d61a7b0f  tx 0xf2cef65e7a90444520fa0c4473dfd44e93696fd65320a809a6147bda79c6b778
 4    6898-2 block 0xb4392cabad007144430484c57d3bdd297fb8dd5afb0875118570b2bd9bad765b  tx 0xcd5f8c89b63aa64ac1b858e4f50501cd88a56220fdeffb3bc3db0276a2b33f33
 5    6901-2 block 0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9  tx 0xcfd0948f09e9954330c58760633e8bc13b77d710a624ec23aec4cf71a81d955f
 6    6903-2 block 0x2b3b1664a54f62a183e2af6b2c67b4af6cfa06f478d1f3bd8c6c97c6c632cdcd  tx 0x7d07763a2b486963d56891415cc56e507f9cc5a829bd4d3add1b52c3b8e59626
 7    6904-2 block 0xfcd7c0bec0d8d002e6e332ef3fbfb57b4e2407aaaa4bbda3f4dd706df56e47d8  tx 0x2a3ddbb73ee928cf604ae5ee0a6323ccdd0ac83f52f8bbee427aa19078abc17f
 8    6905-2 block 0x3c108663459cd1fe3612092f7a9a8962bb81ae686643528390bce4e565cad317  tx 0x9010707f9eb3314e61d499a12c4dbc3707f61c6a39cdecc6b43e89bdfef02972
 9    6907-2 block 0xc25f6f1d1e8b0cd51a8586871974b482ca9218a8841835db65ece52a35197088  tx 0xee409e8a32d0ff7649b8ec740561997b47bbab06983bbac041764e18778117f5
10    6908-2 block 0x7c6ad10e79531ed4425362b5b8ca681d21329e5ae20badbf018706c82bce84b3  tx 0xc3625afc94de1ba163047d446c3c6ae6d3e30f8cc028acdb15038de879ad56ae
11    6910-2 block 0x03a5c2ca30611e39160a35330cf6853df1900cd76e2602bf26338f1b155c14e2  tx 0x45bbe3540313e9a73c31856508fafffa08547ac6c0b62cb34cc32775dda629ea
12    6911-2 block 0x63abdadbe942fe97855957bc9d06315709709c9a3a369ff2d682100508cfeaf7  tx 0xa328006f4d07278d52f6d7957faa8f77a286a96b5e0f5266fb1625e58046acef
13    6912-2 block 0x9aead98bbde73b54e6c329fd6adf032ef56cf0f3e7966eae7670e5ad8ab7332c  tx 0xe2bd6f667028cc8cf6d8884beed38a8faa2171345e681d91fa0c63545456003c
14    6914-2 block 0x0391791a896c05eac8beca7289307e4b42d0454db387d7545045ed127ef6246b  tx 0x5c6ad14e437c910bec6d6e39b026d7c8eb793d752056156d5974783ea9cff897
15    6915-2 block 0x5c53f4ccf9df925ed77a30aaa4e851b083aaf2bcee5839a205c5791cea9e70e1  tx 0x64d96f0b7dadcdef9b4f9ea50fd6b8eba6cdf7f19049ce72dcfe423c6a38bd6d
16    6917-2 block 0x9a412d7f5e50fd1e314baedca20c7009419728cadfe7ff48cc214a7fdb2ff07f  tx 0x8e1c2b5aa5b5199ba66b706474cb5a2fd3336dd083c648bb74ca27c916e107f0
17    6918-2 block 0x51f0185f904497ecca69b39588e81996d5ca0a3c96bb107984a3516ddf2ef6b6  tx 0x21e6483895d1e32c4619de709ab90ec449972ff4e21ea917c71445f4b2179fa1
18    6920-2 block 0x9841403b1dbcce4e7ff5797545098e8e86a1668389a68e62e192fd5ffb63a7a1  tx 0x41a24279d446395f827846480ce1ebbff40b2edcad34bf26855275104214838f
```

State checks (storage/events read at the step's block):

- ✅ asset 1 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the drill: vault reserves == S1 + S2: expected `109000000`, observed `109000000` at block `head`
- ✅ S1 after the gated mint == S1 + 1.00: expected `60000000`, observed `60000000` at block `0x83e6b95a19cd4a9d8dff976df821a2d19c3c47eaa5c380f80856fa7c3f2e15a6`
- ✅ bot refuses the over-mint (exit 1, no signature): expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ over-mint still pending (no MultisigExecuted): approvals == [A]: expected `['A (operator)']`, observed `['A (operator)']` at block `0x65271d159370087e24439f0f3eeab5cc37bc4428ed555010740d0be4708d49ca`
- ✅ S1 unchanged by the refused over-mint: expected `60000000`, observed `60000000` at block `0x65271d159370087e24439f0f3eeab5cc37bc4428ed555010740d0be4708d49ca`
- ✅ no pending over-mint after the cancel: expected `None`, observed `None` at block `0xb4392cabad007144430484c57d3bdd297fb8dd5afb0875118570b2bd9bad765b`
- ✅ both watchers armed and level (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's reserve-chain block: expected `1073`, observed `1073` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 1 status after the freeze: expected `Frozen`, observed `Frozen` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ bot refuses any mint while frozen (I7): expected `I7`, observed `I7` at block `bot`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `evm latest`
- ✅ bot refuses the thaw: finality has not reached the drain block yet: expected `['refused', 1073]`, observed `['refused', 1073]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `6901-2`, observed `6901-2` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ asset 1 status after the thaw: expected `Live`, observed `Live` at block `0x03a5c2ca30611e39160a35330cf6853df1900cd76e2602bf26338f1b155c14e2`
- ✅ asset 1 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ bot refuses a set_team that changes the freezer: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ bot refuses a set_team that moves the admin off M_admin: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ asset 1 team after the co-signed set_team (ARMED): expected `[]`, observed `[]` at block `head`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1 — 2026-10-14T14:53:40Z — PASS (22/22 steps as expected, 20/20 state checks) — source: `a4bdcfa` (clean) — [`evidence/roles-drill-standin-upstream-20261014T145340Z.json`](../evidence/roles-drill-standin-upstream-20261014T145340Z.json)
- asset 1 — 2026-10-14T14:44:19Z — PASS (22/22 steps as expected, 20/20 state checks) — source: `6c26862` (clean) — [`evidence/roles-drill-standin-upstream-20261014T144419Z.json`](../evidence/roles-drill-standin-upstream-20261014T144419Z.json)
- asset 1 — 2026-10-14T14:30:22Z — PASS (20/20 steps as expected, 19/19 state checks) — source: `8665dda` (UNCOMMITTED CHANGES) — [`evidence/roles-drill-standin-upstream-20261014T143022Z.json`](../evidence/roles-drill-standin-upstream-20261014T143022Z.json)
- asset 1 — 2026-10-14T12:47:59Z — PASS (16/16 steps as expected, 17/17 state checks) — source: `25c6f22` (clean) — [`evidence/roles-drill-standin-upstream-20261014T124759Z.json`](../evidence/roles-drill-standin-upstream-20261014T124759Z.json)

### Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control — 2026-10-14T15:03:38Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-attest-standin-upstream-20261014T150338Z.json`](../evidence/roles-attest-standin-upstream-20261014T150338Z.json) · result: **PASS** (15/15 steps as expected, 6/6 state checks) · source: `1f8e351` (clean)

`ballast verify` blocks #6921..#6960 ([`evidence/verify-standin-upstream-20261014T150338Z.json`](../evidence/verify-standin-upstream-20261014T150338Z.json)): **PASS** — 4/4 B attestations PASS on both chains, 1 REJECTED (not counted), 0 FAIL/FLAGGED.

Heartbeat H = 20 blocks (drill override; production H = 200, K = 600 on this profile).

- finality (anvil): mined 65 blocks: finalized = latest − 64

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1140 | `0x32d2e53eb849de0086fccb17c2796fd95c1eb43a4c43f4f18304bf3c7e1430ce` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1141 | `0xb7d32330bbaaaeb6dc985bbe10889f2beb32f18d946fb88097fed396301ce970` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | bot announces watchers (BALLAST/1|watchers|t=1|m=5C7iVxxiAvdPFuddh1UmsNiCLmz91wQMXhR…) | `System.remark_with_event(BALLAST/1|watchers)` (B (reserve bot)) | `6923-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 2 | bot announces evm-attester (BALLAST/1|evm-attester|h160=0x4dc969838572d068ead3ab83139904…) | `System.remark_with_event(BALLAST/1|evm-attester)` (B (reserve bot)) | `6924-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 3 | bot posts attest (pb 6921) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6925-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 4 | bot mirrors 6925-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6926-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 5 | bot posts attest (pb 6923) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6927-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 6 | A proposes mint 1.00 through M_mint | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6928-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 7 | bot mirrors 6927-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6928-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 8 | bot B co-signs (finalized reserves cover it) | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6930-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 9 | bot posts attest (pb 6931) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6934-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot mirrors 6934-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6935-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 11 | bot posts heartbeat (pb 6955) | `System.remark_with_event(BALLAST/1|heartbeat)` (B (reserve bot)) | `6958-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 12 | negative control: the judge key posts a copy of the bot's attestation | `System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key` (Judge (negative control)) | `6959-2` | Ok + System.Remarked (included — verify must REJECT it) | ✅ Ok · System.Remarked |
| 13 | bot mirrors 6958-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6959-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    6923-2 block 0xe4eef06ed4bfd26c75d9598bcaa5d803c910a27a0221f8cf96c8c20d6b3ae02a  tx 0xb12a93fd10546e6be1ebb32cfaab9afb49f19e1f283e6e494657495e753365d9
 2    6924-2 block 0xadfc91d37c4aa8edc205139edf95cf7ca6c1de5527746b3a0696fefa218af642  tx 0x798b0ea4c168917b4683052152053531de8d07aeaa9be8e59ca258c19cdb8fd2
 3    6925-2 block 0x5204f824c79d0a3d6a33196a9f558bbb9f851c3743e9f0d8c18bb83c97992039  tx 0xace91796b9b678309b70653547dd5abe03c1ac9d041de7a2bfbbe59b1e20cd1d
 4    6926-2 block 0x9a7e151685870fc30f4de67d171adde516062b5478b7897b3daf2295f84c3bef  tx 0x9dadb7ab722f73590648fcfc5629052524ae5d47d6b974714d15d41d78b0f582
 5    6927-2 block 0xeef72f26b7eb4197ea7b5d0b0048ba7b54be57b0265c907e2dd8b09d5d0f979d  tx 0xf6d888bd64ecb9067a25280b1c8ab7127555575668db3f3303767207886bac5b
 6    6928-2 block 0x3d9dce0e04d77adbaa512a5b0b9ee4d8e9d9e1e51456c3a23f580f911cdad050  tx 0xbf10363845c9815debd039a98a8e257096b92f6831bd8f7f6fa89aea14f6b64e
 7    6928-3 block 0x3d9dce0e04d77adbaa512a5b0b9ee4d8e9d9e1e51456c3a23f580f911cdad050  tx 0xb4918a1df79a51ef10ca519864061d73827cf66864b06d1b2f6ffddaf8663c80
 8    6930-2 block 0x6794c5322c57e2df3a802e00ae81cb0be6aa307bac30523da17647926a10ce4b  tx 0xacbfba1d033fc46f01c1f1678797dbe3acef5b80f226c7e31d66aaf6c6b2c2e6
 9    6934-2 block 0x10b87ce2871950433542dc1daac6aed458245381f879da33aa2ade99148ed49b  tx 0xee0244b229a54c9b9a17d6fa1eb30c14a0d4c0eda2883c4a709ca4fafb944b00
10    6935-2 block 0xd6fbe6e9a95e9b4bd1f0f602e235aa13b77964d211550a29ee4e01711661ae5a  tx 0x33c762f4ff7ab573ce08ddaab9906846c8459c13e56ebb52e2da74ad413f03e1
11    6958-2 block 0xcd110faf998506a594b6f333e075deffbf47f26a84d683e8313b3ccdf8d8b632  tx 0xb77d96eb59db0793be2a476f9fcd64f8eadae824df3b9c6fa401af90d41b5e5a
12    6959-2 block 0xe1438821093ea1a4cf6641cbf32efea70ae702beff55edccd309cd900643da9e  tx 0x6c4cb3fb3da670e7d33616b3d032c564cec573c4393a198c9cd3a58232b6ca3f
13    6959-3 block 0xe1438821093ea1a4cf6641cbf32efea70ae702beff55edccd309cd900643da9e  tx 0x0ec3bf8aa3bf90ec9b90c7d411a3ba0fa8f3be126bfc65eef8005074a045712e
```

State checks (storage/events read at the step's block):

- ✅ the post after H quiet blocks is a heartbeat: expected `heartbeat`, observed `heartbeat` at block `0xcd110faf998506a594b6f333e075deffbf47f26a84d683e8313b3ccdf8d8b632`
- ✅ verify exit 0 and verdict PASS: expected `[0, 'PASS']`, observed `[0, 'PASS']` at block `verify`
- ✅ every bot attestation/heartbeat PASSes on both chains: expected `4`, observed `4` at block `verify`
- ✅ every oracle post matches a PASSing remark (I10): expected `4`, observed `4` at block `verify`
- ✅ the forged remark is listed REJECTED (not counted): expected `['6959-2']`, observed `['6959-2']` at block `verify`
- ✅ watcher-set and evm-attester announcements PASS: expected `[1, 1]`, observed `[1, 1]` at block `verify`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1 — 2026-10-14T14:55:18Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `8dabe45` (clean) — [`evidence/roles-attest-standin-upstream-20261014T145518Z.json`](../evidence/roles-attest-standin-upstream-20261014T145518Z.json)
- asset 1 — 2026-10-14T14:46:04Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `e70d2b0` (clean) — [`evidence/roles-attest-standin-upstream-20261014T144603Z.json`](../evidence/roles-attest-standin-upstream-20261014T144603Z.json)
- asset 1 — 2026-10-14T14:34:22Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `7b6a2f8` (UNCOMMITTED CHANGES) — [`evidence/roles-attest-standin-upstream-20261014T143422Z.json`](../evidence/roles-attest-standin-upstream-20261014T143422Z.json)
- asset 1 — 2026-10-14T14:32:00Z — FAIL (11/11 steps as expected, 5/6 state checks) — source: `7b6a2f8` (UNCOMMITTED CHANGES) — [`evidence/roles-attest-standin-upstream-20261014T143200Z.json`](../evidence/roles-attest-standin-upstream-20261014T143200Z.json) — failed: every oracle post matches a PASSing remark (I10)
- asset 1 — 2026-10-14T12:58:10Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `aa9c877` (clean) — [`evidence/roles-attest-standin-upstream-20261014T125810Z.json`](../evidence/roles-attest-standin-upstream-20261014T125810Z.json)

### Role split — asset 1 (breaker) + asset 2 (control), reserve vault, ReserveOracle — 2026-10-14T12:41:19Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-setup-standin-upstream.json`](../evidence/roles-setup-standin-upstream.json) · result: **PASS** (16/16 steps as expected, 5/5 state checks) · source: `ab1f8ec` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 63 | `0xe00ac22a2c1f1bf0a3e8ef4eb9a793a8cafb68602ce22692d74ecffa6ddf9d1e` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 64 | `0x82dadc4280284e643a4839bf5da3a7dc02efc1e74b8e9699d34d995c0c76a563` | ✅ status 1 |
| 3 | custodian receives 100.00 test tokens | 65 | `0x785762434c611f99f46a0c78b6a649650bda7148169be5c487523ca50fd69277` | ✅ status 1 |
| 4 | deposit S1 + S2 = 100.00 — plain ERC-20 transfer into the vault | 66 | `0xf1da59fad3ca75e30a44f5b4a2d3cd4fdf39a094b3a8481ef3a716292e8b3220` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, A2, B, W1, W2, judge, peer, M_mint, M_admin, M_watch, asset-2 keyless owner (>= ED) | `Utility.batch_all[11 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `4076-2` | Ok | ✅ Ok |
| 2 | A creates asset 1 | `Assets.create` (A) | `4077-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `4078-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A creates asset 2 | `Assets.create` (A) | `4079-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `4080-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | A mints S2 = 50.00 of control asset 2 to the peer (its only mint) | `Assets.mint` (A) | `4081-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 7 | asset 1 set_team(issuer=M_mint, admin=M_admin, freezer=M_watch) | `Assets.set_team` (A) | `4082-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 8 | asset 1 transfer_ownership(M_mint 2-of-2 {A, B}) | `Assets.transfer_ownership` (A) | `4083-2` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 9 | asset 2 set_team(keyless issuer, admin, freezer) | `Assets.set_team` (A) | `4084-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 10 | asset 2 transfer_ownership(keyless owner) | `Assets.transfer_ownership` (A) | `4085-2` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 11 | A alone tries to mint asset 1 (issuer is M_mint) | `Assets.mint` (A) | `4086-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code(ReserveOracle)` (B) | `4087-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |

Block and transaction hashes (full):

```
 1    4076-2 block 0x8df7c2a28d7ca19100c3c7d51c9c044a0c66471113aad6a7a1c51c2bd2953ec6  tx 0xaf93ba8ab28866b3dce2492c5842ad8b482637bf48e6cf60eb087636d69fd983
 2    4077-2 block 0x492d86548766cebaf57255fd36c03044ab3b6636c6c22280640f0624b1e7b58c  tx 0xcec83e4a3bce176388f694e68a6c373285f55800bd882e7ed3ba99271ef736ca
 3    4078-2 block 0xd9dbce30b43e2deaa95db5095d34ecde0777649273a57164472debad1ce0350d  tx 0x0602b692fa2c7443efa1d5217624814b4ef214f74e56cf30c7440d4bf2ee82f4
 4    4079-2 block 0x7f01336b9dedc370d5828ce63f0f20184eb7a14d951df4155bb07e6e52aafa3a  tx 0xb1b6ec65a4d241136ffda5023d4edcfcb6427df26a4996e5d597fbd2d592363c
 5    4080-2 block 0x13e9dad55fa76696a0ff6e2a99909ece5c5a9925c0a381c6a5c64124557cae03  tx 0xd77d491b7af413d632380168d03a4652af2ad5d954b81c3db06fc633fb6468c8
 6    4081-2 block 0x724e3c74b0b3488a3ae86157858ee810e61bbbbb15d09ecb0b878e21677f8e43  tx 0xa3cbed237fd533f72bf12f3fe05ece2b6220914ae3e0f5f883fe14f3ac68b3f9
 7    4082-2 block 0x4477ceef7b4b10e0abc2f65dac6f5b6fb081f982615ddf3687f222235ec1ddab  tx 0xf23dbf683afe144c11d2c2628c862c6310721c86ac88c8eec5e83dadd2d938a0
 8    4083-2 block 0xd59a7db0824e014cfd7a1d08403173ff9717cd7336b29c35c19885a239566b8a  tx 0xfe987c4935e7a86049f76d822d7be1264275c2dcf119c2fbaced978c587da14e
 9    4084-2 block 0xcc1903a5d556c56220844e855aa1800ae2ae1231f62d1a8bdcbdbfea9d20c935  tx 0xcd6ec237e6f521b2add36bad464a698eeab95dc1d15a6800cf66c180dd8a7dbc
10    4085-2 block 0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048  tx 0x46b9237746c4ed7c8905c59f67ae430be80750df0a71fd41ed01fdac05303453
11    4086-2 block 0x51cf9f432445e3ffca8673815799398dd86025ff2c63cfe0d6b917a13f80d518  tx 0xb519db098c3136a036dd5e2106a076a48c8373606737b17a9aea6aea1d0f8140
12    4087-2 block 0x4c72df62a469758668e9a1dc10496327771ec2342594f6cb034df9549914ea4f  tx 0x2186574442b0b2fe6c5376e9e842690cb92d776f4a5b91e035f3b1a6f7be9a05
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after the deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ asset 1 team == role map (owner/issuer = M_mint, admin = M_admin, freezer = M_watch): expected `[]`, observed `[]` at block `0xd59a7db0824e014cfd7a1d08403173ff9717cd7336b29c35c19885a239566b8a`
- ✅ asset 2 team == keyless accounts (S2 can never change): expected `[]`, observed `[]` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`
- ✅ supply S1 (asset 1) before the gated mint: expected `0`, observed `0` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`
- ✅ supply S2 (asset 2): expected `50000000`, observed `50000000` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`


### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2039 — 2026-10-14T15:05:39Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2039.json`](../evidence/drill-drain-standin-upstream-asset2039.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2039.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2039.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2039|reason=deficit|s=100000000|r=70000000|p=anvil|eb=1210|eh=0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397` (`eb`/`eh` = the local-anvil block the watcher read, not Sepolia)

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 6972
- `freeze_block`: 6973
- `freeze_block_timestamp_ms`: 1791990372001
- `submit_to_inclusion_s`: 2.7
- `pd_head_before_drain`: 6970
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.63
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.33

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x18E317A7D70d8fBf8e6E893616b52390EbBdb629`, token `0x5067457698Fd6Fa1C6964e416b3f42713513B3dD`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1207 | `0x6b8b2b1f948fe2995ce7d93e7088108e2038e69880e0acf4c345134e08a65e72` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1208 | `0x1c69403fb5cd57bf95adc7ef4c422e121956d977c3424a364d0a7c6af605c11f` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1209 | `0xdec6a7764a1f267e1f056c4a7de10f4e0671380d96658bf1cf63f1ce7fde0fc9` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 1210 | `0xa97df79a6b8f1226af098ed142aa8e72b0c4bd5c1e84de641b7432532bd5d20d` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6963-2` | Ok | ✅ Ok |
| 2 | create asset 2039 | `Assets.create` (A) | `6964-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6965-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2040 | `Assets.create` (A) | `6966-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6967-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2039: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6968-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2039 to the judge | `Assets.mint` (A) | `6969-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2040 to the peer | `Assets.mint` (A) | `6970-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2039 via M_watch, reason on chain (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `6973-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6974-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6963-2 block 0xf671cd0d596acd6387eb6a1b823733c4a0d722ec1e42575c67de2bab2be023ae  tx 0xef920211f53b61c108a5c17e65627670d5e4b7b80a4c560022f321aebce8acc7
 2    6964-2 block 0xeea85253927342620554e67edfdc5ad9a693f1d9ea3de2718cc12f812c3f2f99  tx 0x456daa216694ae357c71540f1007b6aad3897b712d137ea4bfbbcf18a29c2adf
 3    6965-2 block 0x158b0f004c39511c3ee9c93aa4e29db266ac0b716236c8a0f017402ff006000b  tx 0x68163c43ad4d2cdc8fe802695bcbb39259203c700fb2ac050c5c6e6ff13be73b
 4    6966-2 block 0x4a55a4eeca6a41f25020ef409537c2fcfd9c50a6a3d242a50e274fb2125d99ac  tx 0x015708bbc9bbbb9b684785288a98b67012366988cafd06c7a6fdf3500cd5e351
 5    6967-2 block 0x5f07a88c4d034492ef6ea0999d56288d632b5a2e637fe5c98a0ccc947dd5e781  tx 0xedc137e35907340d2be868e9790605012d567c4dc95c5bbc370c880f020bb937
 6    6968-2 block 0x207ccf12e16d84985876ab43ba8c8b4dfbf81fb87959de8813c4debc25570c5d  tx 0x59d3e53756932654d8378b83bde3cd15cfc0b35afb3e6af5fa3993956c5c00a4
 7    6969-2 block 0x5abad424265615fac6e8f5ede537fbb1d65eeb033eed005daa63323978c093e7  tx 0x4a41dd2aae10cebc443f83dffdc5c9b847d775cddc0a51bbae82ae8ae214961b
 8    6970-2 block 0x9c40d5175aa1d623ce188263b64a951a830b62d063b3084c0f3ec3b1e9e24074  tx 0x4fd541ccb4de326ace24e154f7f283737d9e8b1c27d82987008729027313218e
 9    6973-2 block 0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e  tx 0x067b5f36de9b3a88022dac88c843f6e3b1f44351730f097c1254ad3f497d6603
10    6974-2 block 0x1287a37af758ad6ca43b4ffef09185e4ac705d0caaf164cfc9c65dfe8a0ed25c  tx 0x295b425d5540ebe99ad6d27aec6ab5e1f15ade0b63a45b4b84846dca099ce155
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x9c40d5175aa1d623ce188263b64a951a830b62d063b3084c0f3ec3b1e9e24074`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397`
- ✅ the triggering check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2039).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x9c83dc6cd0b9f8de460fa68a329b121ffcb7c866ee1246dbc45c68faf1158414`, observed `0x9c83dc6cd0b9f8de460fa68a329b121ffcb7c866ee1246dbc45c68faf1158414` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ control asset 2040 untouched (Live): expected `Live`, observed `Live` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x1287a37af758ad6ca43b4ffef09185e4ac705d0caaf164cfc9c65dfe8a0ed25c`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2033 — 2026-10-14T12:31:41Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `dcf5f79` (clean) — [`evidence/drill-drain-standin-upstream-asset2033.json`](../evidence/drill-drain-standin-upstream-asset2033.json)
- asset 2029 — 2026-10-14T12:19:51Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `37acc11` (clean) — [`evidence/drill-drain-standin-upstream-asset2029.json`](../evidence/drill-drain-standin-upstream-asset2029.json)
- asset 2025 — 2026-10-14T12:04:38Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `36450df` (clean) — [`evidence/drill-drain-standin-upstream-asset2025.json`](../evidence/drill-drain-standin-upstream-asset2025.json)
- asset 2021 — 2026-10-14T12:02:37Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-drain-standin-upstream-asset2021.json`](../evidence/drill-drain-standin-upstream-asset2021.json)
- asset 2017 — 2026-10-14T11:47:46Z — PASS (14/14 steps as expected, 11/11 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json)
- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json) — RuntimeError: no freeze in the watchdog log (exit 4) — failed: mint S1 = 50.00 of asset 2013 to the judge -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json) — KeyError: 'partial_fee'
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2041 — 2026-10-14T15:06:21Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2041.json`](../evidence/drill-outage-standin-upstream-asset2041.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2041.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2041.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2041|reason=providers-down|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 6990
- `freeze_block`: 6991
- `freeze_block_timestamp_ms`: 1791990426010
- `submit_to_inclusion_s`: 2.59
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.81
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xF8e31cb472bc70500f08Cd84917E5A1912Ec8397`, token `0xD5ac451B0c50B9476107823Af206eD814a2e2580`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1211 | `0x404e76974fbda64cfec4d4cbbf6479cb3302b33500f773b73f12a2b1432debc7` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1212 | `0x04d69a463a7fe8884277bc4051007d5aa533929eb5c78b4e642783f3e9d16c18` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1213 | `0xd044e42266cbf8be955d6ad4ace0cfaa718c81e952c3e3de9b44c77a3db7c8db` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6977-2` | Ok | ✅ Ok |
| 2 | create asset 2041 | `Assets.create` (A) | `6978-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6979-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2042 | `Assets.create` (A) | `6980-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6981-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2041: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6982-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2041 to the judge | `Assets.mint` (A) | `6983-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2042 to the peer | `Assets.mint` (A) | `6984-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2041 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `6991-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6992-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6977-2 block 0x013890781a0f77752096e8220cea0fdab97aa5bfc59924c357f8a4530b11a1b8  tx 0x30ba1f16d3489c2a0da5b3db56e2400a0c370658bda3b43b847472f536a600e5
 2    6978-2 block 0x029754eb754d7a86d9ef9d3c7d59a8d74e0541678c811098eff48af0303e0464  tx 0x93b7bd5cc9cedca81299aa899efe7d9b9b807fb3b512ae215d18b51a63c53cb9
 3    6979-2 block 0x8db1bed930864d643699517eb78348a31f0763960c55efe44caf7df356f2db91  tx 0x9e462769c0a8580600ee0d1e638a7d5b914560823f2faaa756b9e3a19e6c42e1
 4    6980-2 block 0x54572fbd9d1940305a78fe1f87cad1712c90b0c5fb06144af1bbfba283a0b691  tx 0x8fccd68cfb0692def750467070f50b84a0de917206bc13853e82f64ff10a3a3f
 5    6981-2 block 0x1b083be596d29be5eaee939a3c8bc75a5fff7ca959040ade3704bc11a738152d  tx 0xf633b3152e11b319e133b5dbe098c9bc60a643a07320a0896f4b86d2978f6b08
 6    6982-2 block 0x2fe6d0a8ab5cd55e1efbbebdb504184d9614b18461eae3f1f4a9869171f92db2  tx 0x8a2a679b35099be5c9e2569761188c6c0355352ed061cba23a743e28e8d9667f
 7    6983-2 block 0xeae7d6b9e97728221c1b0da31d84155811b951a4ebe6c54cce4a8d70e18670a5  tx 0x7e2a34bef19cb95306362e4b6050285786f13d48d4fd5efc19d705efe89271a0
 8    6984-2 block 0x7fef674570eb5870cb0b3a33865d53a15125c94a0d13e1b9146366df5e91454f  tx 0x4bb812bbd344c7d5868bcfea3b680ba81b6a8645da787549f804969de2d31971
 9    6991-2 block 0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b  tx 0x0c4b7df8778ea293d75410b1ba8b9fe6dd21e86e4dd7e7efba0a3b01ac30030d
10    6992-2 block 0xfe588a90a65462f0fc914ee906bd608069fe50ac82c6d74308c4447ff031a4ed  tx 0x2277c926c9bcba4e3260d0117e1c52104da5f889882c795494c8e68c502931a8
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x7fef674570eb5870cb0b3a33865d53a15125c94a0d13e1b9146366df5e91454f`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2041).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xa80b5136f8694b2f68b11dbecb9c1c65f0cbb7e6231dce3e84d8656c5166e622`, observed `0xa80b5136f8694b2f68b11dbecb9c1c65f0cbb7e6231dce3e84d8656c5166e622` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ control asset 2042 untouched (Live): expected `Live`, observed `Live` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xfe588a90a65462f0fc914ee906bd608069fe50ac82c6d74308c4447ff031a4ed`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2035 — 2026-10-14T12:32:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `dcf5f79` (clean) — [`evidence/drill-outage-standin-upstream-asset2035.json`](../evidence/drill-outage-standin-upstream-asset2035.json)
- asset 2031 — 2026-10-14T12:20:29Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `37acc11` (clean) — [`evidence/drill-outage-standin-upstream-asset2031.json`](../evidence/drill-outage-standin-upstream-asset2031.json)
- asset 2027 — 2026-10-14T12:05:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `36450df` (clean) — [`evidence/drill-outage-standin-upstream-asset2027.json`](../evidence/drill-outage-standin-upstream-asset2027.json)
- asset 2023 — 2026-10-14T12:03:14Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-outage-standin-upstream-asset2023.json`](../evidence/drill-outage-standin-upstream-asset2023.json)
- asset 2019 — 2026-10-14T11:48:23Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json)
- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json) — failed: mint S1 = 50.00 of asset 2015 to the judge -> Err(Token.CannotCreate); mint S2 = 50.00 of control asset 2016 to the peer -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level); judge balance unchanged after the refused transfer
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json) — KeyError: 'partial_fee'
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### Breaker drill (heartbeat: no bot heartbeat for K blocks -> freeze (I8)) — asset 2043 — 2026-10-14T15:07:11Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-heartbeat-standin-upstream-asset2043.json`](../evidence/drill-heartbeat-standin-upstream-asset2043.json) · watchdog log: [`evidence/drill-heartbeat-standin-upstream-asset2043.watchdog.jsonl`](../evidence/drill-heartbeat-standin-upstream-asset2043.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 9/9 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`, `--heartbeat-k 10`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2043|reason=no-heartbeat|s=100000000|b=5EEzv6QYKv8bzUtnTWgE7Whi769FLXn2CdfbPZg8YU9s3dpb|n=0|since=7001|k=10`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 7011
- `freeze_block`: 7012
- `freeze_block_timestamp_ms`: 1791990489006
- `submit_to_inclusion_s`: 2.5
- `heartbeat_k (drill override; production K = 600 on this profile)`: 10
- `nonce_first_seen_block`: 7001
- `blocks_nonce_still_to_freeze_included`: 11

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x34B40BA116d5Dec75548a9e9A8f15411461E8c70`, token `0xc96304e3c037f81dA488ed9dEa1D8F2a48278a75`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1214 | `0x68cd440d56f742303c177859e44ef5d7ad888085b9c66d7f6658746ebf40ab48` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1215 | `0x9d7bacad67cb0bc8e4cbf6f2fbbc33e42aba4062c2a7d19c4eb662353faa8384` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1216 | `0xf19934e3e1af93a0d684ce78c3266e18a1932ab9674507909023ea341b286c16` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6994-2` | Ok | ✅ Ok |
| 2 | create asset 2043 | `Assets.create` (A) | `6995-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6996-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2044 | `Assets.create` (A) | `6997-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6998-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2043: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6999-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2043 to the judge | `Assets.mint` (A) | `7000-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2044 to the peer | `Assets.mint` (A) | `7001-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2043 via M_watch, reason on chain (reason=no-heartbeat) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `7012-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `7013-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6994-2 block 0x09bf2ec4b29d5b3da30d6f2e3025f5be258afcd92d535dcd173c92d0ff109104  tx 0x7f21fb5611faaf442452fc428b64e3acb71d1ca544537d12cc6cc3e0dccaadd3
 2    6995-2 block 0x70a06249342c375cf3ca0efe6643904b0de6f03b932b03c4a15b2a622e58ee98  tx 0x60fc48a73bc69c23ea91ccd19ff8fd0a3af7b7cdc9fee2637273304ccee45fb3
 3    6996-2 block 0xab504c41fce574efd19655c33cd2684bf2ef75b29bbf3653f07d3124b38c06f3  tx 0x57f019b203f4867e051929d7768b10cc910f1d62c5436dbba8c7dcd6993a3a47
 4    6997-2 block 0xef6bac4f8c68ed68b0c1c934fcc8240a04d00b370650c75ef6a725104cf24436  tx 0x5913358fbabf6c4add95419eb2ec5ae1eede91f6555c491ce04dbce71e72ca2d
 5    6998-2 block 0x9115c585822743afa5ddeb58c291a175a5e6c15b64a9e2498f9e93d75c1682d4  tx 0xcefa7932478b67c99a91fc35d3535c6ab35d065a8ae5f49b7993beb6186dfaeb
 6    6999-2 block 0x084f83c3b51fa74b9f79cd8e2104f23a6a3551120d7867e4aa81a913c3761765  tx 0xc2591e9b451b7172c04b797b98adfca10e9af83fa630f4599090648f442b2cdf
 7    7000-2 block 0x20828be3697981dc6b3e96057cc9b1cecddd08f4b240c4a2cbcf2fcfd82ea707  tx 0x34d5e23ce613fb673e493edc1ddf09e7112d24aa651c20cbab36957d85cbb948
 8    7001-2 block 0x65ee024d066104247ffdfec76f6b03707a4f63ccf0a4187f748eff0466a74246  tx 0xa3c2eb356e339600d1e3eea0db57bc77f482e630e507f03a486f8f1c78976634
 9    7012-2 block 0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a  tx 0x5d19cd99fe5dcdc6e27b61e34028af223efe28e0ecca214af306e634dd57236b
10    7013-2 block 0x0ea28a62c9895ab8ec98122569fb7cbba70f26cd822e5a68b49e6077209cdc91  tx 0x2b339fabd2605a6ff5202d3fa62f3223d4e8cb8a6ddca986599d6ac2d6fe9ba3
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x65ee024d066104247ffdfec76f6b03707a4f63ccf0a4187f748eff0466a74246`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2043).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x7534ac43a69adb345e7e0e30862cf7ae40c1c52a0aca7f9aba742b2938cc742a`, observed `0x7534ac43a69adb345e7e0e30862cf7ae40c1c52a0aca7f9aba742b2938cc742a` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ control asset 2044 untouched (Live): expected `Live`, observed `Live` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x0ea28a62c9895ab8ec98122569fb7cbba70f26cd822e5a68b49e6077209cdc91`
- ✅ the triggering check saw the bot nonce unchanged for >= K blocks: expected `True`, observed `True` at block `watchdog log`
- ✅ reserves were level at the trigger (the freeze is the heartbeat rule alone): expected `[]`, observed `[]` at block `watchdog log`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2037 — 2026-10-14T12:53:39Z — PASS (13/13 steps as expected, 9/9 state checks) — source: `fd9e593` (clean) — [`evidence/drill-heartbeat-standin-upstream-asset2037.json`](../evidence/drill-heartbeat-standin-upstream-asset2037.json)

### ReserveOracle on Revive — 2026-10-14T15:08:59Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0x4f445370d66c1322025f40f0cec0fd4e814cc840` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T150859Z.json`](../evidence/oracle-revive-standin-upstream-20261014T150859Z.json) · result: **PASS** (5/5 steps as expected, 6/6 state checks) · source: `1f8e351` (clean) · initcode sha256 `1ed85b9a1cd1dc07ec2759e5031088f40c89fd4c75f37ff4e27fec54a2b62cc9`

Posted values mirror drill `drill-drain-standin-upstream-asset2039.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `7029-2` | Ok | ✅ Ok |
| 2 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `7030-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 3 | B (reserve bot, attester) posts level state (pdBlock 6970) | `Revive.call` (B (reserve bot, attester)) | `7031-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 4 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `7032-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 5 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 6973) | `Revive.call` (B (reserve bot, attester)) | `7033-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    7029-2 block 0x1401e3e8a062d0c173becc28018fbb6d6b4b6b3bbeb0adf5d395510f103b8880  tx 0x42553139df1a888d86da5664e62f8c359187fc643e42c302abed967329376964
 2    7030-2 block 0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39  tx 0x62bac6f9551165082b55ab434888de0ee11d9eda11fccb9d00d010b51a202ffc
 3    7031-2 block 0x27932316c032ce50050be214019d67ca30fc301579ccf42ace843d153652739f  tx 0x788b7ad9e0c9b99557d8061c0a37e1cefb6bc7d4722266a90d6fe2c5842737a8
 4    7032-2 block 0x1a21d0d9fea4232cd2b6e8e2f2f16e899449e601fea46f8a070ce4cbccce87e4  tx 0xaad168a99f10338251970c6bcf4525171d49ca8e58d2130fa56352cbd5cf0804
 5    7033-2 block 0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23  tx 0x9a91e6af8fb3b8dba3f241f45d2cb09a523c508894926f4ff258c67f40dd5625
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0x27932316c032ce50050be214019d67ca30fc301579ccf42ace843d153652739f`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0x1a21d0d9fea4232cd2b6e8e2f2f16e899449e601fea46f8a070ce4cbccce87e4`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state (sepBlock/sepHash = local-anvil block, not Sepolia): expected `[50000000, 50000000, 70000000, 1210, '0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397', 6973, True]`, observed `[50000000, 50000000, 70000000, 1210, '0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397', 6973, True]` at block `0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23`

Other runs, newest first, any verdict (full tables in the JSON):

- contract `0x51312c0ddcc67c279dc183a19d60e6d66a76b189` — 2026-10-14T12:33:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `dcf5f79` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T123308Z.json`](../evidence/oracle-revive-standin-upstream-20261014T123308Z.json)
- contract `0x7199a20b12ad30c6292715f5cfec363a2b8691a2` — 2026-10-14T12:21:20Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `37acc11` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T122120Z.json`](../evidence/oracle-revive-standin-upstream-20261014T122120Z.json)
- contract `0xa3273ebfccb127932935888c37028434bc50ec3c` — 2026-10-14T12:06:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `36450df` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T120608Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120608Z.json)
- contract `0x4d172b86f422339b99da9b0d291767a668d19c4f` — 2026-10-14T12:04:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/oracle-revive-standin-upstream-20261014T120408Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120408Z.json)
- contract `0x97f0eea7d362977202c05f85cd9b8307623981ae` — 2026-10-14T11:29:35Z — PASS (7/7 steps as expected, 6/6 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json)

### Spike run — asset 1010 — 2026-10-14T15:09:36Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1010.json`](../evidence/spike-assets-standin-upstream-asset1010.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks) · source: not pinned (recorded before pinning existed)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `7042-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `7043-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `7044-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `7045-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `7046-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `7047-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `7048-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `7049-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `7050-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `7051-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `7052-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `7053-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1    7042-2 block 0xc252aabb427361e10679adde5e987fe8ef43dd0c9b2fcdc06db870aae032d4a7  tx 0x6170351fb900ccee32365cc0308c2e8b83a619470b2291fe1a123019a23ec9a5
 2    7043-2 block 0xd7c8c01f582fba8c2fae62eee62facac6931043f0ba5824def5f2444c0c19ae0  tx 0x9c9b4ff97e85402f71d772553c3f3518b10ae600c289fca320099676930e0251
 3    7044-2 block 0x663f16f1bbf704f14908ad6d9d74862df422dd06272711b447f09cb4b48e696a  tx 0xc0b6e55fbb87004d7c2b588e9e48f05dae14d1ad34d4fe4c57391aa1bca150d0
 4    7045-2 block 0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4  tx 0x5ae05d11689d8c6d513f8823a070b2c5788d0066a6d6d27682fdb9b37414ef63
 5    7046-2 block 0x43ccfec52c480d7ba01055c7ff7ea17c6feef954119274b04c880d4d7f21831b  tx 0x98f31cfa8305869fd3fd67214271b9bed147a781ec5461530b3ea0cc6797a30a
 6    7047-2 block 0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18  tx 0xc52966c2433fa9ac9038c4a1a7b2128c26aefe9dd4ff4018eea0ea05be0567dd
 7    7048-2 block 0x395b259c03b0944959a64e8b5e025f7f5c3eddac027812b40934a48ad3f32a9d  tx 0xf049a77b43b1a8339651a4c50276d6b0f35761a8c075c2fb3059480a72228875
 8    7049-2 block 0x41a7339e0ebb8d37c33f9cd19b6e361d64e33364298ec5b2fd90dc71355216d4  tx 0x241024e192de37d69e458518b27f62be6c717a5be24ebdd2b288fd404e225efe
 9    7050-2 block 0xf587caacf90c2903eaba69d4aacf987c443642cba4fc448f7d506db0b95154b8  tx 0xf5a2675fc59b744ee1238c0c26993fdc627d9bf028c84b4c687bd18121cceb06
10    7051-2 block 0xf633b886c782ff7da2331a820fbe3d9aa4437e6de11a2910a44801f86367b7f5  tx 0xae8432041892d2b0c23b683471684aba0952242b76f882c93fbd2487e76397f7
11    7052-2 block 0xe44832234f95d156964c4b98362d2cd44f828ef04c1f4017fea37e6de033087c  tx 0xe85c0c9926ed98bc3b60f2dc4d23157ef1b1ff0896ee1f9a1ea070ef49ee5dd8
12    7053-2 block 0xd8c4f705abfaf3c2bb63e8f8237b66f59ac6f75700452c8dacc0ab05f4d24ae9  tx 0xa4bb9c07f80f75f6cdb3800eb612d4c3594e793a7e4f18fbc91cb019a51feb7e
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0xc252aabb427361e10679adde5e987fe8ef43dd0c9b2fcdc06db870aae032d4a7`
- ✅ Asset(1010) freezer is M_watch: expected `True`, observed `True` at block `0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4`
- ✅ Asset(1010) issuer and admin are A: expected `True`, observed `True` at block `0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0x43ccfec52c480d7ba01055c7ff7ea17c6feef954119274b04c880d4d7f21831b`
- ✅ Asset(1010).status after freeze: expected `Frozen`, observed `Frozen` at block `0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18`
- ✅ Asset(1010).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0x395b259c03b0944959a64e8b5e025f7f5c3eddac027812b40934a48ad3f32a9d`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0xf633b886c782ff7da2331a820fbe3d9aa4437e6de11a2910a44801f86367b7f5`
- ✅ Asset(1010).status after admin thaw: expected `Live`, observed `Live` at block `0xe44832234f95d156964c4b98362d2cd44f828ef04c1f4017fea37e6de033087c`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0xd8c4f705abfaf3c2bb63e8f8237b66f59ac6f75700452c8dacc0ab05f4d24ae9`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1009 — 2026-10-14T15:08:21Z — FAIL (9/11 steps as expected + 1 observation, 8/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1009.json`](../evidence/spike-assets-standin-upstream-asset1009.json) — failed: mint 50.00 to the holder -> Err(Token.CannotCreate); control: the same transfer succeeds -> Err(Assets.NoAccount); holder balance after mint; peer balance after the level transfer
- asset 1008 — 2026-10-14T10:01:43Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1008.json`](../evidence/spike-assets-standin-upstream-asset1008.json)
- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
