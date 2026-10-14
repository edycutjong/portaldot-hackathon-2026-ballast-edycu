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

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2033 — 2026-10-14T12:31:41Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2033.json`](../evidence/drill-drain-standin-upstream-asset2033.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2033.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2033.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks) · source: `dcf5f79` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2033|reason=deficit|s=100000000|r=70000000|p=anvil|eb=59|eh=0xd68646397b7b3ef3a136a96a154e7c5aca916a75f9d29928ef4faac1be7543e9` (`eb`/`eh` = the local-anvil block the watcher read, not Sepolia)

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3892
- `freeze_block`: 3893
- `freeze_block_timestamp_ms`: 1791981132004
- `submit_to_inclusion_s`: 2.91
- `pd_head_before_drain`: 3890
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.42
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.34

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x7969c5eD335650692Bc04293B07F5BF2e7A673C0`, token `0x2bdCC0de6bE1f7D2ee689a0342D76F52E8EFABa3`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 56 | `0x9a11cd564a71be6cf86f5f6e6ddc0bbcc4d2ca32206004edfd24eba085d683e7` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 57 | `0x37cf77b1d596ff3afe20653ade429b2c60976be2976171129996f3a220280102` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 58 | `0x07bdd193c099e0703e8c084754e38f97b5b23bbc02cd5fa193e11ef762ba272f` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 59 | `0x4dffe475c690e8733de6a81b370d913addd6edee736370130966464c63025a33` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3883-2` | Ok | ✅ Ok |
| 2 | create asset 2033 | `Assets.create` (A) | `3884-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3885-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2034 | `Assets.create` (A) | `3886-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3887-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2033: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3888-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2033 to the judge | `Assets.mint` (A) | `3889-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2034 to the peer | `Assets.mint` (A) | `3890-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2033 via M_watch, reason on chain (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3893-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3894-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3883-2 block 0x42174a3d9a6721f2b9b13464185f03f6a9dc3df9001d795aec8f4fa18f556193  tx 0x725e0c9dc2c88884a196c2e68096e9e2cdbebc425f191ba3a103a571299df92f
 2    3884-2 block 0x7a42291a107d4130eb2806768ff8bcd003cf947684e16e09f7c5cb1ac8045f51  tx 0xc11defab9904169e0c44fa849c6d775361fa0f118a993ddfbe4b7e77e37ab279
 3    3885-2 block 0x0dca13c79a490d973226da13c18908ad67b33cf92582680966a4368c95345a33  tx 0x6d0233a5ce1b141e2cd58c8def1ea47f445a86a948ff898dd6fb093b5e18e212
 4    3886-2 block 0x61c5e70092ee6018580c8709e6d0a0a0495644c8622accac44e90590ca41aad6  tx 0x0f8b0254b2f6552fb9418b27c9c406f3a38070267f05c17cc306a8d834bb274c
 5    3887-2 block 0x75059e9cce02d0c3b7269d5c013c79f27568a7ba460e373dd2c127b61254935c  tx 0x3fefe5d1d925f93ef0a4c634eede2474706562d571cc6326f2f1544764704bde
 6    3888-2 block 0x008b95438939e97d40078dff07cde2f0e4b9facc27cbd0577a41014fade95b9d  tx 0x4b22416969059ea88d73e433f9b8d417489f60845097c4e2e66034b38b1f1f5f
 7    3889-2 block 0x01edb69e95d4f6d17f2f10491c8e0999cc2b0825b4b89d5eddc344edc9b25992  tx 0x5ce4380f5eafcfe60b0dd676b15a25a207fb3e62f934950d6c427b69f41c400e
 8    3890-2 block 0x732dc7d76055c07f3d91bbf812351b50dba2ffe80b69fe6c3476afe84e2312e9  tx 0xded5cc18cc82b7d2709e180f2162ef647e40935d5f7ea5aeef7de64afa8a4604
 9    3893-2 block 0xc9e677993af4bef91bd2a6bc2e0c52877d164e729d1733e1242648fab1f4c0d1  tx 0x70db739490cb400214faf6ddb90a1d02604c3eaf9c687496193d6ac13c2e95f5
10    3894-2 block 0x03cf8bae482168439b5093f0428c6999e58f97f357686ace9892fd1bf23e4680  tx 0x3d5581f691038ef5f04fc669bdd5b5d5ccae0c869a691f76e208e145e6f5b5e4
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x732dc7d76055c07f3d91bbf812351b50dba2ffe80b69fe6c3476afe84e2312e9`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0xd68646397b7b3ef3a136a96a154e7c5aca916a75f9d29928ef4faac1be7543e9`
- ✅ the triggering check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2033).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc9e677993af4bef91bd2a6bc2e0c52877d164e729d1733e1242648fab1f4c0d1`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x1fadd6d089f72bac63d9f0bb21c03b602f16937c4606eef26c19b4bee0af5fb3`, observed `0x1fadd6d089f72bac63d9f0bb21c03b602f16937c4606eef26c19b4bee0af5fb3` at block `0xc9e677993af4bef91bd2a6bc2e0c52877d164e729d1733e1242648fab1f4c0d1`
- ✅ control asset 2034 untouched (Live): expected `Live`, observed `Live` at block `0xc9e677993af4bef91bd2a6bc2e0c52877d164e729d1733e1242648fab1f4c0d1`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x03cf8bae482168439b5093f0428c6999e58f97f357686ace9892fd1bf23e4680`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2029 — 2026-10-14T12:19:51Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `37acc11` (clean) — [`evidence/drill-drain-standin-upstream-asset2029.json`](../evidence/drill-drain-standin-upstream-asset2029.json)
- asset 2025 — 2026-10-14T12:04:38Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `36450df` (clean) — [`evidence/drill-drain-standin-upstream-asset2025.json`](../evidence/drill-drain-standin-upstream-asset2025.json)
- asset 2021 — 2026-10-14T12:02:37Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-drain-standin-upstream-asset2021.json`](../evidence/drill-drain-standin-upstream-asset2021.json)
- asset 2017 — 2026-10-14T11:47:46Z — PASS (14/14 steps as expected, 11/11 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json)
- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json) — RuntimeError: no freeze in the watchdog log (exit 4) — failed: mint S1 = 50.00 of asset 2013 to the judge -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json) — KeyError: 'partial_fee'
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2035 — 2026-10-14T12:32:17Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2035.json`](../evidence/drill-outage-standin-upstream-asset2035.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2035.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2035.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `dcf5f79` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2035|reason=providers-down|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3909
- `freeze_block`: 3910
- `freeze_block_timestamp_ms`: 1791981183003
- `submit_to_inclusion_s`: 2.83
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.94
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xcbEAF3BDe82155F56486Fb5a1072cb8baAf547cc`, token `0xFD471836031dc5108809D173A067e8486B9047A3`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 60 | `0xc812c597e17ca39c03c63419d231e4a3e44843decd4b960815b5c1311731aabd` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 61 | `0xe0a33c4160fecea49d38fc2e1fe0f11bf8d89e1f0ce4a1ddefed9910058b5402` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 62 | `0xc319e6c7a16f9bcfbf5322e399116ea788500670e4ca54931143e00b4f45edaa` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3896-2` | Ok | ✅ Ok |
| 2 | create asset 2035 | `Assets.create` (A) | `3897-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3898-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2036 | `Assets.create` (A) | `3899-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3900-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2035: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3901-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2035 to the judge | `Assets.mint` (A) | `3902-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2036 to the peer | `Assets.mint` (A) | `3903-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2035 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3910-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3911-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3896-2 block 0x1e05b9170c329bbe9d7b4cff51c677d3789395ab4316a839e7a42cb64fd8b6d1  tx 0xf955c653b52ce52017f655d28846244d1b20c161fe5396ce5a441558f35edf0a
 2    3897-2 block 0x9dc8188a129889b0fd54056da00bf74bfe7fade492962392baf76123edc99100  tx 0x63eef9e22a5b248ae82550104eeb9f7cb06eba75574971f6e580c4bb3761e87b
 3    3898-2 block 0x788817df70497c7ec30f05c40f714e3d2eebe39ecfc9edcc853e25551e4539a3  tx 0xdd5346044183fc5f8aaa2a836e79b1c147393c8f7c8e1f40a8e846b35f846a8b
 4    3899-2 block 0x779b7348d3ec5c4118920417aab41543393b275721fa4eb5136933b7b6306218  tx 0x0931c18e9ab5143145ef8376a3200f30974d43d18de98457eb531ea785422596
 5    3900-2 block 0x70d53f7fdb40ba5fbb2a713fdaf31240b796f97af7c15d9cadab8e0194e6b2be  tx 0x961f2a318dee351d7cfccbcf4d81fe90c50eb5f0a799d8d1478e97c3d87139f2
 6    3901-2 block 0xbf5cc187cfbe7831f615d1733ba8b6ce04941f5f1158eee40fde588d99d5b73d  tx 0x537ba868328c57064761d343b1fca2428899ddd77dd064a878854bb40a57649b
 7    3902-2 block 0x64a485836daefef6e6853467e4dc25cdd7f37435cb3282e6c50ae61673d1b3e5  tx 0xa7c15fe638a564af04310aacb68ec4506eb13512748a1fbcae775a0e7ead0fc4
 8    3903-2 block 0xcbef5be176cdeb0c8b9d8324bdd75c7dd68f364d2c651778d344285b9e295552  tx 0x895cc538bb9754ada2ec6526490c7a24c2f30e0fd3c38f393b6b46c85d0d89c6
 9    3910-2 block 0xb0de779a153663fed05f400731d49f601fba0b3b97e896cd96d27de33e6231e9  tx 0xd21dea8d586fae38d95f7d20655bf93d585519214700a80c773ca116ce1be5c5
10    3911-2 block 0x44ff3c1f882332309c24d21e21d8d87798db8c9652d2825147d12656ce137e1f  tx 0x2a48a1e4ac84aaf328e708da1636f71fe53f9e490c41251b17a497ed08938d41
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xcbef5be176cdeb0c8b9d8324bdd75c7dd68f364d2c651778d344285b9e295552`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2035).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xb0de779a153663fed05f400731d49f601fba0b3b97e896cd96d27de33e6231e9`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x02d2c8edcd168b0b148e86bdc5b448d66424d3587f8d1768b2fb70a010e0e0cf`, observed `0x02d2c8edcd168b0b148e86bdc5b448d66424d3587f8d1768b2fb70a010e0e0cf` at block `0xb0de779a153663fed05f400731d49f601fba0b3b97e896cd96d27de33e6231e9`
- ✅ control asset 2036 untouched (Live): expected `Live`, observed `Live` at block `0xb0de779a153663fed05f400731d49f601fba0b3b97e896cd96d27de33e6231e9`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x44ff3c1f882332309c24d21e21d8d87798db8c9652d2825147d12656ce137e1f`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2031 — 2026-10-14T12:20:29Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `37acc11` (clean) — [`evidence/drill-outage-standin-upstream-asset2031.json`](../evidence/drill-outage-standin-upstream-asset2031.json)
- asset 2027 — 2026-10-14T12:05:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `36450df` (clean) — [`evidence/drill-outage-standin-upstream-asset2027.json`](../evidence/drill-outage-standin-upstream-asset2027.json)
- asset 2023 — 2026-10-14T12:03:14Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-outage-standin-upstream-asset2023.json`](../evidence/drill-outage-standin-upstream-asset2023.json)
- asset 2019 — 2026-10-14T11:48:23Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json)
- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json) — failed: mint S1 = 50.00 of asset 2015 to the judge -> Err(Token.CannotCreate); mint S2 = 50.00 of control asset 2016 to the peer -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level); judge balance unchanged after the refused transfer
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json) — KeyError: 'partial_fee'
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### ReserveOracle on Revive — 2026-10-14T12:33:08Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0x51312c0ddcc67c279dc183a19d60e6d66a76b189` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T123308Z.json`](../evidence/oracle-revive-standin-upstream-20261014T123308Z.json) · result: **PASS** (5/5 steps as expected, 6/6 state checks) · source: `dcf5f79` (clean) · initcode sha256 `1ed85b9a1cd1dc07ec2759e5031088f40c89fd4c75f37ff4e27fec54a2b62cc9`

Posted values mirror drill `drill-drain-standin-upstream-asset2033.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3912-2` | Ok | ✅ Ok |
| 2 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `3913-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 3 | B (reserve bot, attester) posts level state (pdBlock 3890) | `Revive.call` (B (reserve bot, attester)) | `3914-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 4 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `3915-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 5 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 3893) | `Revive.call` (B (reserve bot, attester)) | `3916-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    3912-2 block 0xb2451d1779bf95ea7d90b8904f5d29a636e1dd898f8d53749784ef6d3cda07f9  tx 0x940a67b7070dda175af78915cc8e88741b071230bb05c6342777414b5e03d4d7
 2    3913-2 block 0xaaefc004404b1df54906d128fe72cb73cb034dcc66aa0df75bf31298e614afd2  tx 0x3601bd951867cb4482fe4e6c31455ed00af8d464e686f9a7f9465f58428b11e1
 3    3914-2 block 0xbc5d0cfa2d41a936f17754b5c541dde35c61b057d8ae666654f714d5808df98c  tx 0x9f8ee5341bc6dd5ee66dd5af8cf48341dd9a8226d16ebfc0eb39f6c73c79d938
 4    3915-2 block 0x66a7cc65eb6f1e67fecb4f9aefebb74956a38ecc38dc43d9a771bc1b2fa780cf  tx 0x3c81f06f4d16451605df6ecda1cab453e04f1f21733ef3c64f4b6303232ba6b1
 5    3916-2 block 0xc6c5c902bbea0a3d75e16deb270ec1dd7784d17ed8e219109ae13cc24cca4978  tx 0xb0638e736c66c7d30e63a24cac9bb521627650641e57b6cb05e1ebf0e5a510f0
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0xaaefc004404b1df54906d128fe72cb73cb034dcc66aa0df75bf31298e614afd2`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0xaaefc004404b1df54906d128fe72cb73cb034dcc66aa0df75bf31298e614afd2`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0xbc5d0cfa2d41a936f17754b5c541dde35c61b057d8ae666654f714d5808df98c`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0x66a7cc65eb6f1e67fecb4f9aefebb74956a38ecc38dc43d9a771bc1b2fa780cf`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0xc6c5c902bbea0a3d75e16deb270ec1dd7784d17ed8e219109ae13cc24cca4978`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state (sepBlock/sepHash = local-anvil block, not Sepolia): expected `[50000000, 50000000, 70000000, 59, '0xd68646397b7b3ef3a136a96a154e7c5aca916a75f9d29928ef4faac1be7543e9', 3893, True]`, observed `[50000000, 50000000, 70000000, 59, '0xd68646397b7b3ef3a136a96a154e7c5aca916a75f9d29928ef4faac1be7543e9', 3893, True]` at block `0xc6c5c902bbea0a3d75e16deb270ec1dd7784d17ed8e219109ae13cc24cca4978`

Other runs, newest first, any verdict (full tables in the JSON):

- contract `0x7199a20b12ad30c6292715f5cfec363a2b8691a2` — 2026-10-14T12:21:20Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `37acc11` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T122120Z.json`](../evidence/oracle-revive-standin-upstream-20261014T122120Z.json)
- contract `0xa3273ebfccb127932935888c37028434bc50ec3c` — 2026-10-14T12:06:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `36450df` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T120608Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120608Z.json)
- contract `0x4d172b86f422339b99da9b0d291767a668d19c4f` — 2026-10-14T12:04:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/oracle-revive-standin-upstream-20261014T120408Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120408Z.json)
- contract `0x97f0eea7d362977202c05f85cd9b8307623981ae` — 2026-10-14T11:29:35Z — PASS (7/7 steps as expected, 6/6 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json)

### Spike run — asset 1008 — 2026-10-14T10:01:43Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1008.json`](../evidence/spike-assets-standin-upstream-asset1008.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks) · source: not pinned (recorded before pinning existed)

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

- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
