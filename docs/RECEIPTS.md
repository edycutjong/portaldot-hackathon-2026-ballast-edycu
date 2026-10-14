# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2017 — 2026-10-14T11:47:46Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2017.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2017.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks)

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2017|why=deficit|s=100000000|r=70000000|p=anvil|eb=31|eh=0xb395ea0e6f26af18e7d4c50926416f8614ab63882cc21588f2c05ee8d11905f4`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3014
- `freeze_block`: 3015
- `freeze_block_timestamp_ms`: 1791978498003
- `submit_to_inclusion_s`: 2.53
- `pd_head_before_drain`: 3012
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.76
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.29

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xc5a5C42992dECbae36851359345FE25997F5C42d`, token `0x09635F643e140090A9A8Dcd712eD6285858ceBef`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 28 | `0xcdb26a7cbbaeab9b98e0c2e4936af648a53a6658d47e72d1cc1e10abfb348843` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 29 | `0xa1b7509e2c4c7af2b6ee1fd7207fb2da209ff8e2eba8b4e84f53f3df08e2ab90` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 30 | `0x5c49ac5a986c68a85d1870a1c4b9a16489f200b625e9667bfdbde477169ee769` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 31 | `0xb4aadb79ec8a585e85b5e927d6c0cc0cb120ca88ef29f48afbc46fb93fe958ee` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3005-2` | Ok | ✅ Ok |
| 2 | create asset 2017 | `Assets.create` (A) | `3006-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3007-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2018 | `Assets.create` (A) | `3008-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3009-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2017: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3010-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2017 to the judge | `Assets.mint` (A) | `3011-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2018 to the peer | `Assets.mint` (A) | `3012-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2017 via M_watch, reason on chain (why=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3015-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3016-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3005-2 block 0x779767346a43bc4e0e720ea4352326b6563e51f409febdc6b6353b437b2f323c  tx 0x9f3049c9429a1602cd2f4070ddee9ea96f4202abbfbc23969ad923533496b775
 2    3006-2 block 0x78f50c7d8723f0db23e6aeeddaa1cafff42295c68434f7316a975218422e2ddd  tx 0x748f609fc708cd4f2dbc8976859c11d3f6ba013db43a6bc2b8886f0dd6375bd1
 3    3007-2 block 0x48d0587f3937e3313ab9d400100694fd8902ba4c1921145ee8911c502734574b  tx 0x3f155e94e8c132932672f5201eef2ea5210c498f982792c8cee1b97319ccf5db
 4    3008-2 block 0xe425e52e1f32e4d29a820dbf0123d9fe466c04be4d08c2da22fa53b0cfcc732a  tx 0x97d40a65c225060e475c0986d27db61cc6628bd53c88d4ae7317208e8a2a2f5f
 5    3009-2 block 0xc1a67a0445d7039744f1ee826f06cf1a12dafcbf7b634ac26fb8cdf174daf6de  tx 0x7a16f138adc317ab5931e4b70f16921724bc5aa747e057e14339a24f4f1e23b8
 6    3010-2 block 0x1ecc26c59d3a3b5a9d25cea662e42f4e595ad694536ba639b7a23ffef51e9c55  tx 0x50d2063d302077b23afdd5d6f7af25523d55e76c0551c38185c3f399c264afd6
 7    3011-2 block 0xc657bf29c69a416d541f6c04af0a38deffe78bb71a87b4f06c6dd4fdb298d4d1  tx 0x3d8c4b865266a0564105322af868d7cd31953652b72782ae8898f1d13b97c9be
 8    3012-2 block 0x2a85d9e6d952008adf3f187e49697ddcbcd80cdf797636f8375511f827af2e5e  tx 0x7e740288c6528b4666468f5e0288549fb6178ab4cd86b0e785b30eb95c4ca3db
 9    3015-2 block 0x0b90949ae3f3bac2981f58fa333c4d17a6ce79fecacf8fb86c82ab752ac5ded5  tx 0xb133f8d0e81b33e067befe07a12cddb2966c305b069360ea6bc85eca6feb4a33
10    3016-2 block 0x411d03071c67abb80205b42bb9bb65ee767ef8c2bffa02162d4ce19549579e8d  tx 0x9fa644080a177acb0ca6b65b8a784b17aba76b8519724cb28c7df610124bf457
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x2a85d9e6d952008adf3f187e49697ddcbcd80cdf797636f8375511f827af2e5e`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0xb395ea0e6f26af18e7d4c50926416f8614ab63882cc21588f2c05ee8d11905f4`
- ✅ the triggering check ran after the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2017).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x0b90949ae3f3bac2981f58fa333c4d17a6ce79fecacf8fb86c82ab752ac5ded5`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x8120332dc1997bef150193bbc815ea806f9258180fafac1487769d020f15f887`, observed `0x8120332dc1997bef150193bbc815ea806f9258180fafac1487769d020f15f887` at block `0x0b90949ae3f3bac2981f58fa333c4d17a6ce79fecacf8fb86c82ab752ac5ded5`
- ✅ control asset 2018 untouched (Live): expected `Live`, observed `Live` at block `0x0b90949ae3f3bac2981f58fa333c4d17a6ce79fecacf8fb86c82ab752ac5ded5`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x411d03071c67abb80205b42bb9bb65ee767ef8c2bffa02162d4ce19549579e8d`

Earlier runs (full tables in the JSON):

- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json)
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2019 — 2026-10-14T11:48:23Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2019.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2019.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 7/7 state checks)

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2019|why=fail-closed|s=100000000|down=18s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3032
- `freeze_block`: 3033
- `freeze_block_timestamp_ms`: 1791978552001
- `submit_to_inclusion_s`: 2.28
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 20.39
- `down_for_s_in_remark`: 18s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x84eA74d481Ee0A5332c457a4d796187F6Ba67fEB`, token `0xc3e53F4d16Ae77Db1c982e75a937B9f60FE63690`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 32 | `0x64613eadf9a2c0f937d5a31ff276de7723e026b011c74ed6da4e007b3b4524f4` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 33 | `0x4ccb4eb4ff3194ffa04415b2dadf874cc216c7d0f05e603c0a0cb4f8eca4b8ef` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 34 | `0x7d59f777b855fb5b672fc6976bf52e50716151351072b58cf0d8639a64e999c5` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3018-2` | Ok | ✅ Ok |
| 2 | create asset 2019 | `Assets.create` (A) | `3019-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3020-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2020 | `Assets.create` (A) | `3021-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3022-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2019: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3023-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2019 to the judge | `Assets.mint` (A) | `3024-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2020 to the peer | `Assets.mint` (A) | `3025-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2019 via M_watch, reason on chain (why=fail-closed) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3033-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3034-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3018-2 block 0x93ad14fdbd847992286e143bc7c7e276556710c39bde96a6b0a672fd011334a1  tx 0x801aca45122f75288b50e352b06a38de7727b50db3c63548f8abf50ff985c16d
 2    3019-2 block 0x5694092299b97ae13854ab863b8f1da42575c9556a23fbb9420b74e4cc74373a  tx 0x2cd976c7eb350c69d84fa5adcb2bbe3d226ce94055b2e42504c106206eaca7d7
 3    3020-2 block 0xe1e4ec8b79d9b247d054947cc752d4a42bf0453248d8726169fec5c839197f35  tx 0xf3d84e2025b7644d30a49a73294885e5e10e6cd2579c4e27c9b7839c7c1d59f9
 4    3021-2 block 0xe0edc67a15d82f5d1f7ca6390a8bdd6caf218c237be6140312451c87dd151d12  tx 0xef5456fc67dd9511b95d58feef56cb30c667d0dd0c88624b83bf5c97f7749df6
 5    3022-2 block 0x5ba7be3cf2cf8505564c3947563e266f6447d0f58be41b973afb6b73782a331c  tx 0x34cc1c148937e5a3d08876dcd923cdd806c47d9b604d87a9029730d0bff5385f
 6    3023-2 block 0x3bf086d121cc1e23b65eccab2af8cfe7995753440d8eb24dcea2e3f56e5222e6  tx 0x4cd629f598554500276e6ef45769aa8f4a612dbcd8c0b31bb31cf7315361d7c5
 7    3024-2 block 0xf6e021232773745a4598bee4484ac5eea36e0c77837cae0c8a9eabfc7d15819b  tx 0x3f779e32f32b1821021ff4d9e3557a9134a47a3d945b8ab0a240e7ae25557379
 8    3025-2 block 0xc847eb87a451e4a2c7dc583077b036e674b2f8729d58eb6ac4bd53d1a13e4c3e  tx 0x43d4824670ffc30bb978599e9210d5f503a2cef42c2d898fee3ff7f53b321843
 9    3033-2 block 0x9430fc29fa73a0725b50303ffa4e7037fc6c0eeb7b11ab2d7843d0e13560da35  tx 0x0cffd77d535cd1383531db3fa5ae2bacc32f2425b44c36804b05a71ed30487ca
10    3034-2 block 0x64fb3893cfc76ac0ec33933507a96eba5920e0db68d0514fbdb46da50b362b82  tx 0x2af910f4f700119defb84fcd5ddfcef62102dba7ba8dc7b2969acc244fb1d1ba
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xc847eb87a451e4a2c7dc583077b036e674b2f8729d58eb6ac4bd53d1a13e4c3e`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2019).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x9430fc29fa73a0725b50303ffa4e7037fc6c0eeb7b11ab2d7843d0e13560da35`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x9f5b7d619800f684743b33d7e9f6be58a3c07341985476831d8b1ed0b1249090`, observed `0x9f5b7d619800f684743b33d7e9f6be58a3c07341985476831d8b1ed0b1249090` at block `0x9430fc29fa73a0725b50303ffa4e7037fc6c0eeb7b11ab2d7843d0e13560da35`
- ✅ control asset 2020 untouched (Live): expected `Live`, observed `Live` at block `0x9430fc29fa73a0725b50303ffa4e7037fc6c0eeb7b11ab2d7843d0e13560da35`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x64fb3893cfc76ac0ec33933507a96eba5920e0db68d0514fbdb46da50b362b82`

Earlier runs (full tables in the JSON):

- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json)
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json)
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### ReserveOracle on Revive — 2026-10-14T11:29:35Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0x97f0eea7d362977202c05f85cd9b8307623981ae` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json) · result: **PASS** (7/7 steps as expected, 6/6 state checks)

Posted values mirror drill `drill-drain-standin-upstream-asset2001.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `2641-2` | Ok | ✅ Ok |
| 2 | Revive.map_account (B (reserve bot, attester)) | `Revive.map_account` (B (reserve bot, attester)) | `2642-2` | Ok | ✅ Ok |
| 3 | Revive.map_account (Judge (stranger)) | `Revive.map_account` (Judge (stranger)) | `2643-2` | Ok | ✅ Ok |
| 4 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `2644-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 5 | B (reserve bot, attester) posts level state (pdBlock 2473) | `Revive.call` (B (reserve bot, attester)) | `2645-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 6 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `2646-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 7 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 2476) | `Revive.call` (B (reserve bot, attester)) | `2647-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    2641-2 block 0x57b92359e9627c21a691aee5632ba28024eca94e4b2766019a37daaabc488cd3  tx 0x553051f5be01c14b304ac0089d24bce4cf7145d522f962ea592995fef9eaf9bd
 2    2642-2 block 0xc488be7852c98c4f5639cf4bec7b92b3f21415f50b47c582f9ab9e714d307e3d  tx 0xb883a834127910a8249211232f4caecc2d567c245ff5016ea7f3678bda1cf27d
 3    2643-2 block 0x935ef32f27681406e9f285f70335762f3da57ed68d2666dcd96bde0778fc3c98  tx 0xd743c16627a6490b5d67212c8fe039196a49f6c5b0bd2748b0c151dd75758192
 4    2644-2 block 0x5a30ab4bec21d657ac00e8b17342b8cb8d71b435ee5566f07fbd4c9804b4fc33  tx 0x1279344b10e5a1ac721183aa5d8eb0ee9eea05c91f2e0b4b1f5aaba0b7338d25
 5    2645-2 block 0x972c2060c1efecb687b7d79088a090c2a202090353ae6145c9ad050495217e74  tx 0x6fbc669805cd1267803b79235be2ead3a17fc047936f8b7e2d51fc8e2af67c5f
 6    2646-2 block 0xaadec935cca8c2bd5ea02a01a09b0f2f0495509ed5d8f59b054fd9f5adf8957f  tx 0xbe0167df629ede7e4c5d555bab0e9c85817783209798512bba0552be9aa8b8c3
 7    2647-2 block 0xb6b070787fd5510aa020c8a50f39c106d35649aea466625e9d96041f6f30b2fa  tx 0xf49edc6d94e3bbd2990131b16aa2983184a1c51ad06874c7554b7c1a25b898c2
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0x5a30ab4bec21d657ac00e8b17342b8cb8d71b435ee5566f07fbd4c9804b4fc33`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0x5a30ab4bec21d657ac00e8b17342b8cb8d71b435ee5566f07fbd4c9804b4fc33`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0x972c2060c1efecb687b7d79088a090c2a202090353ae6145c9ad050495217e74`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0xaadec935cca8c2bd5ea02a01a09b0f2f0495509ed5d8f59b054fd9f5adf8957f`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0xb6b070787fd5510aa020c8a50f39c106d35649aea466625e9d96041f6f30b2fa`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state: expected `[50000000, 50000000, 70000000, 4, '0x56c447a205b3bce3ffeee23c57f8e221c56d4df5386c1218abd018cd0484c6dc', 2476, True]`, observed `[50000000, 50000000, 70000000, 4, '0x56c447a205b3bce3ffeee23c57f8e221c56d4df5386c1218abd018cd0484c6dc', 2476, True]` at block `0xb6b070787fd5510aa020c8a50f39c106d35649aea466625e9d96041f6f30b2fa`


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

Earlier runs (full tables in the JSON):

- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
