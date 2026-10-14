# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2005 — 2026-10-14T11:31:12Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2005.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2005.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 8/8 state checks)

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2005|why=deficit|s=100000000|r=70000000|p=anvil|eb=11|eh=0xf22b6b865fbda272a59d4e7a2b7af2652428dfd02bdb3d878b6624265309e360`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 2683
- `freeze_block`: 2684
- `freeze_block_timestamp_ms`: 1791977505000
- `submit_to_inclusion_s`: 2.0
- `pd_head_before_drain`: 2681
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 4.8
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.81

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6`, token `0xa513E6E4b8f2a923D98304ec87F64353C4D5C853`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 8 | `0xe94747559f196327653260ce1ae8b3fc1f10c5480d95ee2c3e139b494dd90d8d` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 9 | `0x373c26d28087af558fc9f6c5f7a31935f416ed572a14c5cf7b61b00c22fbdabe` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 10 | `0xf0f6493a4040fab9e1c0fc37437b38c24bf30e1a64bafd90cd07e10d6466533e` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 11 | `0x322a6733576ec9e192222c3f6267a85c46a1174d0ce26293e1f2e8c101647c2a` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `2674-2` | Ok | ✅ Ok |
| 2 | create asset 2005 | `Assets.create` (A) | `2675-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `2676-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2006 | `Assets.create` (A) | `2677-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `2678-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2005: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `2679-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2005 to the judge | `Assets.mint` (A) | `2680-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2006 to the peer | `Assets.mint` (A) | `2681-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2005 via M_watch, reason on chain (why=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `2684-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `2685-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    2674-2 block 0x02adc30574010ac4c176a620d5c1f37f90f3bbcd7b94dd269293aff350b73b4d  tx 0xa5f416567829f79079a67c7c4c865e553faf02636839a68ccbe989a06fbd3877
 2    2675-2 block 0x6287051e2ff8d02ec12d90d2f23838a486d767bf24bd851d7622eeaffea98b21  tx 0x18521372fad7d4725fedb41294c27497f9c9f3a5214616cae02c186bca4d4a6e
 3    2676-2 block 0x7162c86ac4465966f7fd1e61fb88e559260bf9a97544f811a713b5015b20665b  tx 0xa98efc11b95b7fd9be16235377bc3d0e74c30c3f18179a25e3ffd155f3b23844
 4    2677-2 block 0xfa838fb2ddcc62c9c3e1874eaea34245ed16fcdc8b747426ee393311c5fba783  tx 0x9422ab6122684c88fc79afbfe91bcbe36db31aed21d9bf1186d4b5569290a28d
 5    2678-2 block 0xea235c293ebbe3474684040be7733e5ab2cfe21a5aef2f5ad3a42ccff6a3540c  tx 0xfaf7550282523a938045454206cc1d81e2f3c1cd79ba1996a9d0becca587c174
 6    2679-2 block 0x79c808309b6e03bb1ce182b8312699061a933f539f89cbbf90357f8de29d5843  tx 0x6deca06c667c2e9cf3ac0ba43ecb78f2caa8436a2f6a3fad1b6c0848118dad18
 7    2680-2 block 0xd698228fa5d54a60c6ff6ceb869c0ecaa1bf2daecb5516afdbfda20a59b30612  tx 0x53c9565b3321dda42d60c4abc19b440a9e12cb0eaa442865ddcf590f8a65deff
 8    2681-2 block 0x0f7ec829e5724b00e9576d6604cd5710c6de4fc8811e0ed8455406d3c2a2b026  tx 0xed4e4a3031d5c2a928a6353ac702574133f868fbdd6ab89b23fbb4db5bf85e19
 9    2684-2 block 0xb26b558f45c19b07a3af7ad8b5f79a0797e2c887373be9b742a26dc1d121d902  tx 0x110e31d9408ffe51ad8454eac53bb409462b83d59a7791d1a415be039925c9b1
10    2685-2 block 0xba69078964bcb4db9f2956f2cba03af93f9ea5b27bf22a50fadee35684377d5c  tx 0x315eee88b6e721bab5f20c7b1e78b1f51caa39a4eb510adad878740c4fa05d48
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x0f7ec829e5724b00e9576d6604cd5710c6de4fc8811e0ed8455406d3c2a2b026`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0xf22b6b865fbda272a59d4e7a2b7af2652428dfd02bdb3d878b6624265309e360`
- ✅ Asset(2005).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xb26b558f45c19b07a3af7ad8b5f79a0797e2c887373be9b742a26dc1d121d902`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xb43b8213fe1d02947d87a9d32279248f321b97abf98d5d2d89549cb7352ee5b4`, observed `0xb43b8213fe1d02947d87a9d32279248f321b97abf98d5d2d89549cb7352ee5b4` at block `0xb26b558f45c19b07a3af7ad8b5f79a0797e2c887373be9b742a26dc1d121d902`
- ✅ control asset 2006 untouched (Live): expected `Live`, observed `Live` at block `0xb26b558f45c19b07a3af7ad8b5f79a0797e2c887373be9b742a26dc1d121d902`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xba69078964bcb4db9f2956f2cba03af93f9ea5b27bf22a50fadee35684377d5c`

Earlier runs (full tables in the JSON):

- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2007 — 2026-10-14T11:31:50Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2007.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2007.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 7/7 state checks)

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2007|why=fail-closed|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 2700
- `freeze_block`: 2701
- `freeze_block_timestamp_ms`: 1791977556009
- `submit_to_inclusion_s`: 2.75
- `fail_closed_after_s`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.88
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0`, token `0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 12 | `0x5a903edd69d8edaebef816bbb4b92e59997882c38d07f3adcd815e511ee8a3c3` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 13 | `0x77a7f9b3836ca3cf52d4b7f29f058e030590186f03cf588fa501231b1e33177d` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 14 | `0x84f43cf2cd41ea8cbf2d8f394ee9915a88d74bf8c24fd9df0dc9a6253d0aedc8` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `2687-2` | Ok | ✅ Ok |
| 2 | create asset 2007 | `Assets.create` (A) | `2688-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `2689-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2008 | `Assets.create` (A) | `2690-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `2691-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2007: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `2692-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2007 to the judge | `Assets.mint` (A) | `2693-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2008 to the peer | `Assets.mint` (A) | `2694-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2007 via M_watch, reason on chain (why=fail-closed) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `2701-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `2702-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    2687-2 block 0x51ece34cbd289d99d68cdbf23d461f0212643e104c02e6dfa32a82ee91731634  tx 0x306b2245ecc81932254a76d0cecb2c1ccc6474803e480b267235babd013671cc
 2    2688-2 block 0x69f3758b240f315ee2b21ff31df29aa27cd013a4e655ab324519d2f6af9007e7  tx 0x03540c4830294ccad0fb83835c8ea1048ac2f559bba79f86a06f5213dfb7f9ff
 3    2689-2 block 0x0cf5b6d8b6eecee76ee85290d3343210c3368cc09418e94b09f325c66f0421b8  tx 0x5bddd8a0f17a5c8d09d73973bc34747c119aa4b7ca31dd3a32340d655083e1fa
 4    2690-2 block 0xf359422cc92c3baff702f5eb03ba92fc00c11afc522327eb388f8ef6f66cb14d  tx 0xcecda345ef55ac54635c394cd3fb521d5f9785e2e88b89149ba94053f493df68
 5    2691-2 block 0x269b3d39e48a97fd24f80fac3a4b5ef60c7e15fb9770613665a9b1dc1b87167a  tx 0xab3ae247b12a41b8db11173f7019956f5576aee439362424bb8c26dee4130389
 6    2692-2 block 0xac084248a0d781abba812a276e788485f14f03606a4a31c3ec63c3834a5c2ce2  tx 0x68f242554843bc772965ee0f7a71bd69c45fe8df30569200289937741e4ce9a7
 7    2693-2 block 0xfe9a84e64a3b8de8051ac4e2f9a92fc1e9b19e93c5f20c4fb99e2e134c0721f8  tx 0x1675688284e4c051cfcd662b8ca09b38edfb6a7841bdd10dbfe2edf32d4a63c4
 8    2694-2 block 0x7cc7cacc583570e12867edcee5c0394fb1e75ed4bc0c4a6daa7cc87ec5b3699c  tx 0xc928bc3bd14b34161482660b272467f23dc588112eb9bc4c541986378c382355
 9    2701-2 block 0xdab67923247de195d0b20b73cf93b219f623e768e3e4805e6d77696f4c9f3d74  tx 0x81c8f5ffdb20b1a613e24b0914b92b32a7784b1a779370f0ef80c82b092595ac
10    2702-2 block 0x5d8082b59be39d14b11b5d30713b6ec1b05c22aeefd9bbab6dec9e80b5c35b85  tx 0xd762262233382b042f62e8cf4c9d35f54eb44c0964ebc4c66cb9cd48ac83f720
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x7cc7cacc583570e12867edcee5c0394fb1e75ed4bc0c4a6daa7cc87ec5b3699c`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2007).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xdab67923247de195d0b20b73cf93b219f623e768e3e4805e6d77696f4c9f3d74`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x0fa9eb311cdba00128c68dd54ef23de376f5fec7af367d595fe2aec56d839f8d`, observed `0x0fa9eb311cdba00128c68dd54ef23de376f5fec7af367d595fe2aec56d839f8d` at block `0xdab67923247de195d0b20b73cf93b219f623e768e3e4805e6d77696f4c9f3d74`
- ✅ control asset 2008 untouched (Live): expected `Live`, observed `Live` at block `0xdab67923247de195d0b20b73cf93b219f623e768e3e4805e6d77696f4c9f3d74`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x5d8082b59be39d14b11b5d30713b6ec1b05c22aeefd9bbab6dec9e80b5c35b85`

Earlier runs (full tables in the JSON):

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
