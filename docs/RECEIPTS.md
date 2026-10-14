# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2001 — 2026-10-14T11:20:47Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2001.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2001.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 8/8 state checks)

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2001|why=deficit|s=100000000|r=70000000|p=anvil|eb=4|eh=0x56c447a205b3bce3ffeee23c57f8e221c56d4df5386c1218abd018cd0484c6dc`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `deficit_seen_head`: 2475
- `freeze_block`: 2476
- `freeze_block_timestamp_ms`: 1791976881004
- `submit_to_inclusion_s`: 2.93
- `pd_head_at_drain`: 2473
- `blocks_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.9
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.84

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512`, token `0x5FbDB2315678afecb367f032d93F642f64180aa3`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1 | `0x008aedaf7899009cc29ade804ba62b53d0e7bef7e8f2da11dd0483898b33b810` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 2 | `0x45aef6a56e11e8376da1b7362f308fbaace482f185e51d5d5748ef9b666a6dff` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 3 | `0xfac2106498c35efd8c2441bcfd1374472a5c76feb1118fd544e0d787aa82af4b` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 4 | `0xb256d4784847d70aeadfc99733842d334d27894a23acadbea8bfe9c692a3af8d` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `2466-2` | Ok | ✅ Ok |
| 2 | create asset 2001 | `Assets.create` (A) | `2467-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `2468-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2002 | `Assets.create` (A) | `2469-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `2470-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2001: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `2471-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2001 to the judge | `Assets.mint` (A) | `2472-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2002 to the peer | `Assets.mint` (A) | `2473-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2001 via M_watch, reason on chain (why=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `2476-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `2477-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    2466-2 block 0x44616a727de6f14a9a1fbd3b77cb0b0d3025dbb15756a85f56c0e930416d0447  tx 0x443537661ee82bbae0d235f7c3dfd7446d84212863795938cac90b41c157529a
 2    2467-2 block 0xd494ab9c7f029e15fe7395acf9fd4a9ae26b6dce895f42ccf6b0018a300bd5e6  tx 0x263c064b774cddc4672bdea2058a18267500f628010a420f49c20c2504ba368b
 3    2468-2 block 0x12ce2ac9e07831e9631fb4775a6929db138dbea6490c19ef253cbc56ac31185f  tx 0x37ef61fb5df0f13a02d0290170ec90a5adf4c8a1e9d238e8ce88f6588fa847fe
 4    2469-2 block 0x158369d51d382bd3777a99269948afc5de114682369114f233d04c2ea4036d0b  tx 0x902d1c406f459c42ee5dbc8100e558938c4172d7975d51383038337716040218
 5    2470-2 block 0x130888dc36529634c89ecd8529a1ea7aec930733b5b2cb57135fef3fc9727803  tx 0xefe1f0ccdecd7936ff73fd5413c1ab842e042c152998e4cdb28cb354ad9723a0
 6    2471-2 block 0x0ed574827eac1fc20a8673e3e820e9e654a6909f2193b7f02a3187c3be021918  tx 0xf9489261cc37e7b9f4ecd812a48182e09ac95f3dfe4d981783bf15968859d9ac
 7    2472-2 block 0x67b47c7c74caecf4b0335ce3fa5e9b34c11e6fc206c55f6d1bbb4c70d042d274  tx 0x91eb210c74559174cc3347c63288ae981dc8c5ecdc2f0604a10d9aa276578dc8
 8    2473-2 block 0xa5a2319d2a84973e35ce85a1a7e79f826dc3b6bd7011e59bb8e00ebfd041099b  tx 0xdc91d1addb1051cb76992509390026ed5a05a6157e55b527d5646bcdc8c8d4d6
 9    2476-2 block 0x088f5244f0d92884b08837c64c62162b49eeb59683f588a0fd5431dc86948546  tx 0x198df9e363007c4e000385a137914529d464c5fc64e9c4d9438777541b494fff
10    2477-2 block 0x91ffb1b7ec5f588e7188f08d04339dae10f5d1f81efbec91f5e731d59da263a6  tx 0xcd857f175a95ecd8857b0261d704617e26787f293ee51f600af3c66b063913b0
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xa5a2319d2a84973e35ce85a1a7e79f826dc3b6bd7011e59bb8e00ebfd041099b`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0x56c447a205b3bce3ffeee23c57f8e221c56d4df5386c1218abd018cd0484c6dc`
- ✅ Asset(2001).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x088f5244f0d92884b08837c64c62162b49eeb59683f588a0fd5431dc86948546`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x957910856543fd8cef9a34d918278a0092828413384229054a87fe38480f877a`, observed `0x957910856543fd8cef9a34d918278a0092828413384229054a87fe38480f877a` at block `0x088f5244f0d92884b08837c64c62162b49eeb59683f588a0fd5431dc86948546`
- ✅ control asset 2002 untouched (Live): expected `Live`, observed `Live` at block `0x088f5244f0d92884b08837c64c62162b49eeb59683f588a0fd5431dc86948546`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x91ffb1b7ec5f588e7188f08d04339dae10f5d1f81efbec91f5e731d59da263a6`


### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2003 — 2026-10-14T11:21:35Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2003.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2003.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 7/7 state checks)

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2003|why=fail-closed|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `deficit_seen_head`: 2495
- `freeze_block`: 2496
- `freeze_block_timestamp_ms`: 1791976941002
- `submit_to_inclusion_s`: 2.8
- `fail_closed_after_s`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.94
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x5FC8d32690cc91D4c39d9d3abcBD16989F875707`, token `0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 5 | `0xffea3c4d2c966395afcac88a9cdce14b19d9ff2e00261ef4fd8f7b6f55d8fda9` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 6 | `0x45fcb0f0c7783e554a5b32ff76ec79c7dd5bf92c251517689c328cbb42a70289` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 7 | `0x490d5ab528acf1f457b1aff56450095205d936efcfb92e0df710c0e8c9c3b4c6` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `2482-2` | Ok | ✅ Ok |
| 2 | create asset 2003 | `Assets.create` (A) | `2483-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `2484-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2004 | `Assets.create` (A) | `2485-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `2486-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2003: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `2487-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2003 to the judge | `Assets.mint` (A) | `2488-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2004 to the peer | `Assets.mint` (A) | `2489-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2003 via M_watch, reason on chain (why=fail-closed) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `2496-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `2497-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    2482-2 block 0x19614e01786937d70ec2f1daabea2da5b8768a793f9050d7741c5262a3df5226  tx 0xf288719c371ab75ba0726e73964a5abd018b1a308f4fcfa6b3918f5dbc55ccc0
 2    2483-2 block 0x7784d21a88b4faf9b6230b390d8bc1e5ce53acb89c6ca84a4088b8b901fcad68  tx 0x15db8dcce6a45f4bb04dbe262dc9e72d60b7115bd89a03cc9f1c1bca1cb9f72b
 3    2484-2 block 0xeaff8c5ddceb57fcc6cb386c7c4e354ef4ef244e218c1eb771ca95d71f84ef93  tx 0xc053fe754776cf0bae8f222d2d4f2d4d3fb99661dc1632f4fc53aa5ca40e8f03
 4    2485-2 block 0xc0113aeb48c3c26dfd6fc9cf0451bf494341d372c6088b29acc36a1fee6c2f38  tx 0x309e9e8c6aad320a4729bed30aa38d1f64347326312eb9eeb79533087f569fd0
 5    2486-2 block 0x3ea89d3ba3955ada9764b46a14dc9980d556e5a79daf702ab0d7738251234371  tx 0xe2d5d0b7221d5128bce35e0b443a3c86617ea1883ae66abb6bdd2b50efb9cb51
 6    2487-2 block 0x6bb2206bc1646598e7a3086c6580c7c62ff8787d1d19ed22943d827a7a888b07  tx 0xa901413a4f6e5a4a15e8d49e006890887c3626cc9c7df1964556154ea591bac4
 7    2488-2 block 0x015c95431d7df05b32dd850ef9e266ed7155556d1bad07e17ab1caf3523eb28d  tx 0x9bc474d9518df33ddd78520ab1de2f03af8fcea1db40422a43130c5017e61c47
 8    2489-2 block 0x37ee491eadfeed25775af6f4c4b3ac0f4b3fdbbc936afafd89055364c0758eff  tx 0x716ed467f080aea3d197631d62d254c2443fff3b4d4152593885c06f686be812
 9    2496-2 block 0xc8e48bf66c07a4a260c11640bab8b532c5763b8b7fbf1538d3f5e31be9433d23  tx 0x2721a5190cf7a3e94f3e63e23ce87d7acd8bbcdd7c993d9c6b205d287dc41367
10    2497-2 block 0x3e95ad7fc43888095fc1971fe80f475cbaad61e2a41b13544a817c15d86727df  tx 0xa086e1d37d47ddd36cb7ff895b735408581042dfeb064cd29ac5665e47fd244d
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x37ee491eadfeed25775af6f4c4b3ac0f4b3fdbbc936afafd89055364c0758eff`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2003).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc8e48bf66c07a4a260c11640bab8b532c5763b8b7fbf1538d3f5e31be9433d23`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x910038230489a298a53d24da9a998aeefae3370c65d7970114f320465c493927`, observed `0x910038230489a298a53d24da9a998aeefae3370c65d7970114f320465c493927` at block `0xc8e48bf66c07a4a260c11640bab8b532c5763b8b7fbf1538d3f5e31be9433d23`
- ✅ control asset 2004 untouched (Live): expected `Live`, observed `Live` at block `0xc8e48bf66c07a4a260c11640bab8b532c5763b8b7fbf1538d3f5e31be9433d23`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x3e95ad7fc43888095fc1971fe80f475cbaad61e2a41b13544a817c15d86727df`


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
