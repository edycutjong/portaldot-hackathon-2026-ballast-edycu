# Receipts

Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are
in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and
every drill reserve-chain tx from the local anvil. Read-only Sepolia reads are listed first.

## Sepolia reads (read-only — no Ballast contract is deployed on Sepolia yet)

- [`evidence/sepolia-crosscheck-2026-10-14.json`](../evidence/sepolia-crosscheck-2026-10-14.json) — read at 2026-10-14T11:41:44.199Z: finalized block #11912942 via 2 providers — AGREE (publicnode: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000, drpc: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia yet; this file shows the two-provider reader agreeing on one finalized block

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

Latest V3 reachability probe: [`evidence/v3-probe-2026-10-14-p3.txt`](../evidence/v3-probe-2026-10-14-p3.txt) (V3 reachability probe — 2026-10-14T11:41:33Z).

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2025 — 2026-10-14T12:04:38Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2025.json`](../evidence/drill-drain-standin-upstream-asset2025.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2025.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2025.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks)

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2025|why=deficit|s=100000000|r=70000000|p=anvil|eb=45|eh=0xf8fd1f78b1e31aea78f6006ef05d5aeb7a0432c0d756808ed54b86ab33bc47e5`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3352
- `freeze_block`: 3353
- `freeze_block_timestamp_ms`: 1791979512014
- `submit_to_inclusion_s`: 2.98
- `pd_head_before_drain`: 3350
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.43
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.41

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x99bbA657f2BbC93c02D617f8bA121cB8Fc104Acf`, token `0x4826533B4897376654Bb4d4AD88B7faFD0C98528`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 42 | `0xa695c32db960c585bb95111649e9825b59026b84787ca8abeb95cc99e87e28c4` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 43 | `0xfe515327e6656980a0867b4ebde9b7c64bef7df347fe1986d9587dabaf229fca` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 44 | `0xb8d6eba8d6f833ced7ae967c0308b1c1d2390a7bb1c84f76e17b6eef4b954f1d` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 45 | `0xff0bae3de6c9e40c5b47a980a1a62b13df522af7287b80a9dc9e3883db7d18f5` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3343-2` | Ok | ✅ Ok |
| 2 | create asset 2025 | `Assets.create` (A) | `3344-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3345-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2026 | `Assets.create` (A) | `3346-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3347-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2025: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3348-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2025 to the judge | `Assets.mint` (A) | `3349-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2026 to the peer | `Assets.mint` (A) | `3350-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2025 via M_watch, reason on chain (why=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3353-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3354-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3343-2 block 0x0b4ab68cb20646011f4f44e8c3da1bf1886330dc249eee7bf8dd77a98d65e3d4  tx 0x242f879cb7c2acb03207a68e6ca4a6da67840c024c02e6eaadb152717d11122d
 2    3344-2 block 0x47152379c721f211853055370c49d0c3f6aa8acf8e571895abeb8dc236513e1d  tx 0xae5c60387d11f087f907f9400c9ad9488912b81f9eceee5da300606e207841dd
 3    3345-2 block 0x97b737205f9f5c1a72ddb641a74213018a68de1b2b958a0fde6047b18b6bfb7d  tx 0x1d618202ffb7e2002088a8a22b7a62ecea51ff7235425ec44b6ba37c4a843e65
 4    3346-2 block 0x4d0f7774a7499c708fcaefc2e3de6bd19c4dc93b4943c2e5fc7545c65be6c60f  tx 0x6cb7680703c8097e5d3ab5013166beeacba0b714f359780fa509d8cb3cd4ec51
 5    3347-2 block 0xf04fa52d449d6fd20d77dcedff1fc69597797de36baa428eba6c536ecb8146fa  tx 0x438a154460c86a93b758a82d46a8f51458d06e7efa72657f9cd077d88780de7c
 6    3348-2 block 0xc53c5506964dea3c29c5f77e126dec24e2718cf750bcaa433d219be131487fbd  tx 0x793c522a280ad01706b6c2fbf2e3b6f7992bf7cea5fd3d3b1e2def8794df106d
 7    3349-2 block 0xaac05efdb277978559b8c3f0f4453c1caa00679d97a6ede2dc323e8b92530593  tx 0x8e8868161792a564af2b0ba4609134c3d8f69acadf3145f0e3f1a08cd5a1e7e1
 8    3350-2 block 0xaa3f318f728d741b8624745b28f2e3e29871b637acb9f2b8968902730acf6800  tx 0x824c19c34bdc1b804f3cbb40fcba6298591380dc5bdf42dd71c3112699d58b24
 9    3353-2 block 0x07110e71470770368a3c1759d2a6c81df8eb519765f70b8392e82fcb58026e76  tx 0xa7c7172dc3aef43d5d583dbfddec2c2d62731e0c2cfa4ac53fed347a8e7a22ad
10    3354-2 block 0xb43301259503757b94bc971a5586a1a8651be6c82e076384cdb3195218fb42a5  tx 0xea7a48acb7638cc7d8e40880124a5baa768ba149eea6f6e7676b1461eba2fd3d
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xaa3f318f728d741b8624745b28f2e3e29871b637acb9f2b8968902730acf6800`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0xf8fd1f78b1e31aea78f6006ef05d5aeb7a0432c0d756808ed54b86ab33bc47e5`
- ✅ the triggering check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2025).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x07110e71470770368a3c1759d2a6c81df8eb519765f70b8392e82fcb58026e76`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x2b177344d7127931fb3a71b88caa6fada84e69bf39852793ee5c6c566a5d9cb7`, observed `0x2b177344d7127931fb3a71b88caa6fada84e69bf39852793ee5c6c566a5d9cb7` at block `0x07110e71470770368a3c1759d2a6c81df8eb519765f70b8392e82fcb58026e76`
- ✅ control asset 2026 untouched (Live): expected `Live`, observed `Live` at block `0x07110e71470770368a3c1759d2a6c81df8eb519765f70b8392e82fcb58026e76`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xb43301259503757b94bc971a5586a1a8651be6c82e076384cdb3195218fb42a5`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2021 — 2026-10-14T12:02:37Z — PASS (14/14 steps as expected, 11/11 state checks) — [`evidence/drill-drain-standin-upstream-asset2021.json`](../evidence/drill-drain-standin-upstream-asset2021.json)
- asset 2017 — 2026-10-14T11:47:46Z — PASS (14/14 steps as expected, 11/11 state checks) — [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json)
- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json) — RuntimeError: no freeze in the watchdog log (exit 4)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json) — KeyError: 'partial_fee'
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2027 — 2026-10-14T12:05:17Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2027.json`](../evidence/drill-outage-standin-upstream-asset2027.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2027.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2027.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks)

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2027|why=fail-closed|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3369
- `freeze_block`: 3370
- `freeze_block_timestamp_ms`: 1791979563003
- `submit_to_inclusion_s`: 2.38
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.91
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x5eb3Bc0a489C5A8288765d2336659EbCA68FCd00`, token `0x9d4454B023096f34B160D6B654540c56A1F81688`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 46 | `0x52dd567c2d257712b512f3ca44a766f67b7ec36d7aa541cf4667a67bc53bb187` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 47 | `0x1da91637782f1f6b0b47202cb3ef117630051eb2d0b278873d2024bf2c896991` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 48 | `0x266f31f2751e77a2b18e53f3edfd070447bc88a7c621b6d7b942ced792855dc5` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3356-2` | Ok | ✅ Ok |
| 2 | create asset 2027 | `Assets.create` (A) | `3357-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3358-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2028 | `Assets.create` (A) | `3359-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3360-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2027: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3361-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2027 to the judge | `Assets.mint` (A) | `3362-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2028 to the peer | `Assets.mint` (A) | `3363-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2027 via M_watch, reason on chain (why=fail-closed) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3370-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3371-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3356-2 block 0x7cf0bb1bae0845b0fc4db8662316051b2eb4a03561cad64a717a185752c4ee2a  tx 0x9fec4fb3f7749738f2e7cb398a5792ae820ed7a30fe270fd27801bd75752fd3f
 2    3357-2 block 0x6898994542ea46ffe72693e3aa7a8960daa18d5dc06c3d83c48ddf99fe2579d5  tx 0xb5680fa1fe714540d486fdedba0400b85841f27328def5d375c7c8b923f04577
 3    3358-2 block 0x22251c66fd23e4fe9bc01413d5dc45f385ff0d6c32fc9b29922591a831ee02b7  tx 0xc421ceff5ef3f5079e4176635d652e67bafac59f6d2c31b75d8b60d41a5a56b1
 4    3359-2 block 0xb5ecf99c502380ed70b82a8ca0527c84329fd677934d002b6a70b990d809f831  tx 0x99889f38e8ab963d75fe8596b564b1d46c4c6f63a4eb5ab9ce80095f1a9ece94
 5    3360-2 block 0xcae55f5631473c3e3690e3d7e713ed7be036e96659d4e447d07d221cbd22ada9  tx 0x85cbe836cc9743b1ff0553baca348eee4d11fcc53d34d347a1fabc02a7c1d039
 6    3361-2 block 0x06b74ccb39f35ae930d682bb81070b8336935042d8d679055b01ad95a7492857  tx 0x6ef5d7bfb967349cda1f39b767061514a71780ce5041a73c46203d88a8093b47
 7    3362-2 block 0xc9fa70d2e7bf932e801de34fa731f28a1899b9608e0ed89aa5421c6ddd31e060  tx 0x9b7206fe7d5305e124c71ed5d54ab99152b6d85eaf93b45ed6e125989575bc00
 8    3363-2 block 0x8db37e9efe7eed812575a02336d459eee51c0cc4684dd7e61ecf1d18f244a91e  tx 0x4dc6ed169dbbd2f03e3336229a79dcdfe9379d0fe74409f755057c17f215475e
 9    3370-2 block 0x1e0e141262f7939eb22fc019dc456ecb79294f49351c56b920c9ee91a779558a  tx 0x6930e4ce1a6302e97aee85ea1aa7906753c2c5d431a9bbf9943c5178e0973352
10    3371-2 block 0xb6f89747693c479d437502921f008e051978477c76afb992dea4528b1617990c  tx 0x13f3a95c912c91ceff153d07763b0684d50e4566fd06093de638b5c1318ca9cf
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x8db37e9efe7eed812575a02336d459eee51c0cc4684dd7e61ecf1d18f244a91e`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2027).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x1e0e141262f7939eb22fc019dc456ecb79294f49351c56b920c9ee91a779558a`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xe86f613b93093d0023cc85477f7be391025a1505e840135548ffd77ab7cabda6`, observed `0xe86f613b93093d0023cc85477f7be391025a1505e840135548ffd77ab7cabda6` at block `0x1e0e141262f7939eb22fc019dc456ecb79294f49351c56b920c9ee91a779558a`
- ✅ control asset 2028 untouched (Live): expected `Live`, observed `Live` at block `0x1e0e141262f7939eb22fc019dc456ecb79294f49351c56b920c9ee91a779558a`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xb6f89747693c479d437502921f008e051978477c76afb992dea4528b1617990c`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2023 — 2026-10-14T12:03:14Z — PASS (13/13 steps as expected, 8/8 state checks) — [`evidence/drill-outage-standin-upstream-asset2023.json`](../evidence/drill-outage-standin-upstream-asset2023.json)
- asset 2019 — 2026-10-14T11:48:23Z — PASS (13/13 steps as expected, 7/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json)
- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json) — failed: mint S1 = 50.00 of asset 2015 to the judge; mint S2 = 50.00 of control asset 2016 to the peer; supply S1 + S2 == vault reserves (level); judge balance unchanged after the refused transfer
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json) — KeyError: 'partial_fee'
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### ReserveOracle on Revive — 2026-10-14T12:06:08Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0xa3273ebfccb127932935888c37028434bc50ec3c` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T120608Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120608Z.json) · result: **PASS** (5/5 steps as expected, 6/6 state checks)

Posted values mirror drill `drill-drain-standin-upstream-asset2025.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3372-2` | Ok | ✅ Ok |
| 2 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `3373-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 3 | B (reserve bot, attester) posts level state (pdBlock 3350) | `Revive.call` (B (reserve bot, attester)) | `3374-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 4 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `3375-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 5 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 3353) | `Revive.call` (B (reserve bot, attester)) | `3376-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    3372-2 block 0xf2118d77e2056302bc1a2c3f4bf0915fc537c109a5f8561da76e32f9d64f0f86  tx 0xe42c91e9deff4667a7aae89dd1dd914b3cca298006f066e104caf131b9830584
 2    3373-2 block 0x1cffb803653316ca4596ec0ec4e141df87a69bde38fa1c0a92f348148bb0c92d  tx 0x8979de6dc2e93c5dbdfdc549f355859b2c4e1b6815bd17cbea73b9dc478f1b62
 3    3374-2 block 0x1f1f6ff7b6b76c73d81e5f73aa2a51650338b4a2e3578fc35685ee886231b937  tx 0xba42097f686170281702f8319313665ecf93fd79e2b19f32a2cfb7e7720a0618
 4    3375-2 block 0x3720b42c2659d3457a21f441d29861aae8ea99ef53f1109e5ce85c9c75a8d6f8  tx 0x28763a16f4c79aaa9d19317a05e2898f0ba254fd96e09acd7eb78b13dd1fe1b8
 5    3376-2 block 0x7bc039e331dc1e7997c230b5e9da6582d42235db5fb60565edacec1644e09e8d  tx 0x406557780833e8cf089edbb6cbd3405d32e3344f3ce3c3f57871151a6f9bea66
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0x1cffb803653316ca4596ec0ec4e141df87a69bde38fa1c0a92f348148bb0c92d`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0x1cffb803653316ca4596ec0ec4e141df87a69bde38fa1c0a92f348148bb0c92d`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0x1f1f6ff7b6b76c73d81e5f73aa2a51650338b4a2e3578fc35685ee886231b937`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0x3720b42c2659d3457a21f441d29861aae8ea99ef53f1109e5ce85c9c75a8d6f8`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0x7bc039e331dc1e7997c230b5e9da6582d42235db5fb60565edacec1644e09e8d`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state: expected `[50000000, 50000000, 70000000, 45, '0xf8fd1f78b1e31aea78f6006ef05d5aeb7a0432c0d756808ed54b86ab33bc47e5', 3353, True]`, observed `[50000000, 50000000, 70000000, 45, '0xf8fd1f78b1e31aea78f6006ef05d5aeb7a0432c0d756808ed54b86ab33bc47e5', 3353, True]` at block `0x7bc039e331dc1e7997c230b5e9da6582d42235db5fb60565edacec1644e09e8d`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2021 — 2026-10-14T12:04:08Z — PASS (5/5 steps as expected, 6/6 state checks) — [`evidence/oracle-revive-standin-upstream-20261014T120408Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120408Z.json)
- asset 2001 — 2026-10-14T11:29:35Z — PASS (7/7 steps as expected, 6/6 state checks) — [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json)

### Spike run — asset 1008 — 2026-10-14T10:01:43Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1008.json`](../evidence/spike-assets-standin-upstream-asset1008.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `884-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `885-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `886-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `887-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `888-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `889-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `890-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `891-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `892-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `893-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `894-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `895-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1     884-2 block 0x1962fcffcaef8f072b93815e07dec7f968e797f43217a3ff3b81003b6878a576  tx 0x984211c22fa29c2584425ae51c2e5acf5a672b7dcde41155ed1bec7035c77b1b
 2     885-2 block 0x9eb44f4645479abfcc83b3c2c04868de603bc329a23acbc61c0a2f86198e2fbc  tx 0x7eeccfebff15c90195d011de9e00f20cf62e8b097bb7ce3aa6f6e5fe947962b3
 3     886-2 block 0x7bc2c0fb063f33f9618fd67f4d2c8732accec5280f19f48ebfbd33a96dc3378f  tx 0x1b18af7dd6bdddce0bb99aac6e57fc9cf3eb941d6b7d420dc8a5ef07f320823d
 4     887-2 block 0x3aa5bc2583a7c959a9b0ea40585ca702f773a33abfd2fb3820634be1d7e0616c  tx 0xe3a665db5c20155bcb01f4e9e8b2ce91eaf83e46a3de65e44ac97e8736b3fe9b
 5     888-2 block 0xb10ae8f0bb4815cc4c478ffcc5a2ece4af8b2d5a4faf4c4fd3ad2d12d69d4a1f  tx 0x17d90062272898c5a4a0dd6206815460df1f645d9e50310e6b117240ff8b69e0
 6     889-2 block 0x3ed1b3e3f435a940082e9eba9c0884c8c163a3fe85873aab82f934e856e85df4  tx 0xbc344aa950d01c2ac1945a64264148daa3d76ff8cb3bd5663ca4032d9fbaee7d
 7     890-2 block 0xa6ecf9048f60e53d02608168930dfa14350419e225776d882e1ff73341c376a6  tx 0xa59a1fca55d80b19c095d3eb83af4cd8e054c80bb3c09c44732c6fdfbe22c379
 8     891-2 block 0x9ac5bc5b41a0bbb9e0e7e18381483ddbc3f7c06943adb82e8ff9d1ce8ad745c8  tx 0x6020e78ea7c5adb2a79a6fff5fef255b50b6ef571513fd5fc95ef4539510b829
 9     892-2 block 0x7a5450741a943e8530dfe355cce906a7ba0fc728c0b8cbd4c4345aa4f56a2004  tx 0x272c939359991b0d99a5e2126795dbad2fd8dbe91367c2960ce254f75a431d2d
10     893-2 block 0x13a7ca3b282969ba33f2c00891d1baf1507969b65696202a2da8d1499a21699a  tx 0x182487980571cea4f508c11a9a0612a3f11c081ac29f28da9f658ae605777bd6
11     894-2 block 0xd9dc0cc87c74ccd7b96e9158849daf37a3b0bbb66ef462eb37e8e5b496d64b8e  tx 0x06bb2b633c83a35fabd290ddb9372cbcab956b9b2ce595f0cb2b2d1bdd02bc89
12     895-2 block 0xfdeddd627ac556b15359d0210675cfe13d9a791ff2ba1c52a71c15e7ff99aa96  tx 0xe05f796bd856d7755282ddca6994dc1b93b09bd30a0b277dc4d01a705d21d7f6
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0x1962fcffcaef8f072b93815e07dec7f968e797f43217a3ff3b81003b6878a576`
- ✅ Asset(1008) freezer is M_watch: expected `True`, observed `True` at block `0x3aa5bc2583a7c959a9b0ea40585ca702f773a33abfd2fb3820634be1d7e0616c`
- ✅ Asset(1008) issuer and admin are A: expected `True`, observed `True` at block `0x3aa5bc2583a7c959a9b0ea40585ca702f773a33abfd2fb3820634be1d7e0616c`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0xb10ae8f0bb4815cc4c478ffcc5a2ece4af8b2d5a4faf4c4fd3ad2d12d69d4a1f`
- ✅ Asset(1008).status after freeze: expected `Frozen`, observed `Frozen` at block `0x3ed1b3e3f435a940082e9eba9c0884c8c163a3fe85873aab82f934e856e85df4`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0x3ed1b3e3f435a940082e9eba9c0884c8c163a3fe85873aab82f934e856e85df4`
- ✅ Asset(1008).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0xa6ecf9048f60e53d02608168930dfa14350419e225776d882e1ff73341c376a6`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0x13a7ca3b282969ba33f2c00891d1baf1507969b65696202a2da8d1499a21699a`
- ✅ Asset(1008).status after admin thaw: expected `Live`, observed `Live` at block `0xd9dc0cc87c74ccd7b96e9158849daf37a3b0bbb66ef462eb37e8e5b496d64b8e`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0xfdeddd627ac556b15359d0210675cfe13d9a791ff2ba1c52a71c15e7ff99aa96`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
