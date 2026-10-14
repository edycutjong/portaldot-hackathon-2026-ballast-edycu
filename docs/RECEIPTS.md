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

### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2029 — 2026-10-14T12:19:51Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2029.json`](../evidence/drill-drain-standin-upstream-asset2029.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2029.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2029.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks) · source: `37acc11` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2029|reason=deficit|s=100000000|r=70000000|p=anvil|eb=52|eh=0x37915c827296ed31db1ec60f660159274f6cf1624c453e53a6c4beb8718ed7b3`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3656
- `freeze_block`: 3657
- `freeze_block_timestamp_ms`: 1791980424001
- `submit_to_inclusion_s`: 2.49
- `pd_head_before_drain`: 3654
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.85
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.34

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x4c5859f0F772848b2D91F1D83E2Fe57935348029`, token `0x809d550fca64d94Bd9F66E60752A544199cfAC3D`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 49 | `0x6dbad4a47a38b4d3b85453d634627eea25b635b0a3e7e8eb7aef70ac8e292919` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 50 | `0xce4cff0e29138ef7e252f1baeba3076b9dc8e1469566ecd6057fb35efd85146b` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 51 | `0x4dba3ae0f7ecaaaa4ae53c09fe9ed2ce813378ae9fc34d131b8418c1c3eb3352` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 52 | `0x3b0198b4ee8c19d3eb749d86d387310925b07547bd3db0b0f064fef783ec9383` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3647-2` | Ok | ✅ Ok |
| 2 | create asset 2029 | `Assets.create` (A) | `3648-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3649-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2030 | `Assets.create` (A) | `3650-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3651-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2029: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3652-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2029 to the judge | `Assets.mint` (A) | `3653-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2030 to the peer | `Assets.mint` (A) | `3654-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2029 via M_watch, reason on chain (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3657-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3658-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3647-2 block 0xc0841667edb8a3396ff64eae7627908c3e953f6d1a8b8a6d1eb06c7c73fd5b17  tx 0x22836d5a2e9d3d3d4d9b2031cf64f69142a42b628492a31487596509866f0b0e
 2    3648-2 block 0x8eeea6cfca30e0fa5c9bbf6df9e3c71b06fe0c4eb8ea5f0626fc775eb68facc2  tx 0xcb347c3d3150dc7271d661ef9731c9478e2ea6e77f447fcb5a379720f4b91a89
 3    3649-2 block 0xc301e9f055d1ce37bd5c17209ab157ce9bd43282e7a7f11ec3f116c03231dfd3  tx 0x976230e771eba98631bfeb2f90b0fa261cbef16172261b36730b1ba8fb00f183
 4    3650-2 block 0xe6ea0f2bd31bc94d807500007b7d80b9dd2b7e514dba8c156abb1a3c88301993  tx 0x976b76a318f0852be565535641b7c1ec18ad6ed9135e6e6c4c799f17254d69e0
 5    3651-2 block 0x3ad856a7346fab74a974f54305d11cf5c774f97bde3eeb15dce683364e59f151  tx 0x753f921906ca1fc4dfb4cc6bf5f7424daea186e8654f3f6446c2a2959d76b9fe
 6    3652-2 block 0xe5f119785023f37564ba20ba8010a39dfc701da41c0287f3492a7619e72a1af0  tx 0x30556aaac5f2d25e76bf3f20353f504a180edaf93f0b25ea8cb27ef4bbec58d3
 7    3653-2 block 0xf95e6fc01a1c44880a3927f769553aeec2b872590eb8b6f0c2c2ec41d4ed31b8  tx 0x0fb85cbc41b07c1d7987d44ed1ce40d572baf4e5e1a6bf4a8d92fcfa113c9e77
 8    3654-2 block 0x33ede41721003f4d1d6b876dbe87ec8856576dadb4ba8126c80c7399d4abb532  tx 0x16bf73f130ed63aa6fad9b92ab5a4215f9c82e93394a8a48e07e693570a4ff8b
 9    3657-2 block 0x8e02182fd4ec0988c42913d7a5a065759b0807b3edda9c778c28f221a6db9701  tx 0xab831e30cd43a1dbd3686a5333ccbe9b496bc082541fda1228de4f5768339e3e
10    3658-2 block 0xd5ca115dab4b1b4ab26263b56c66f8c05faa05c00fe88057a68c18af28947116  tx 0xae323f28ddb0eb11cc345411aae096d43694e3a2cfcc351ee74e374e008a608e
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x33ede41721003f4d1d6b876dbe87ec8856576dadb4ba8126c80c7399d4abb532`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0x37915c827296ed31db1ec60f660159274f6cf1624c453e53a6c4beb8718ed7b3`
- ✅ the triggering check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2029).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x8e02182fd4ec0988c42913d7a5a065759b0807b3edda9c778c28f221a6db9701`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xcba42b6e469c2e49bb3f3909ba940b4a26f7b3ca71335616ec55c2036f2ca8d2`, observed `0xcba42b6e469c2e49bb3f3909ba940b4a26f7b3ca71335616ec55c2036f2ca8d2` at block `0x8e02182fd4ec0988c42913d7a5a065759b0807b3edda9c778c28f221a6db9701`
- ✅ control asset 2030 untouched (Live): expected `Live`, observed `Live` at block `0x8e02182fd4ec0988c42913d7a5a065759b0807b3edda9c778c28f221a6db9701`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xd5ca115dab4b1b4ab26263b56c66f8c05faa05c00fe88057a68c18af28947116`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2025 — 2026-10-14T12:04:38Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `36450df` (clean) — [`evidence/drill-drain-standin-upstream-asset2025.json`](../evidence/drill-drain-standin-upstream-asset2025.json)
- asset 2021 — 2026-10-14T12:02:37Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-drain-standin-upstream-asset2021.json`](../evidence/drill-drain-standin-upstream-asset2021.json)
- asset 2017 — 2026-10-14T11:47:46Z — PASS (14/14 steps as expected, 11/11 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json)
- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json) — RuntimeError: no freeze in the watchdog log (exit 4) — failed: mint S1 = 50.00 of asset 2013 to the judge -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json) — KeyError: 'partial_fee'
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2031 — 2026-10-14T12:20:29Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2031.json`](../evidence/drill-outage-standin-upstream-asset2031.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2031.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2031.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `37acc11` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2031|reason=providers-down|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 3673
- `freeze_block`: 3674
- `freeze_block_timestamp_ms`: 1791980475005
- `submit_to_inclusion_s`: 2.73
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.82
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xCD8a1C3ba11CF5ECfa6267617243239504a98d90`, token `0xb7278A61aa25c888815aFC32Ad3cC52fF24fE575`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 53 | `0x74013fae655270a3496b3c4c787eefaa56f9bd2b35f94e96825b0041a0f79292` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 54 | `0x4e9eeb0bee23b112333976d273cc5c7d6d3a57083a4d62b06bcab86ec174632b` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 55 | `0xa202ac9fb0de790d1ea79e2b53e1e0f3de36f3414672be14837e2a7fcd7829f3` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3660-2` | Ok | ✅ Ok |
| 2 | create asset 2031 | `Assets.create` (A) | `3661-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `3662-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2032 | `Assets.create` (A) | `3663-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `3664-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2031: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `3665-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2031 to the judge | `Assets.mint` (A) | `3666-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2032 to the peer | `Assets.mint` (A) | `3667-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2031 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `3674-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `3675-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    3660-2 block 0xfe21326353af9b1d3018116b34456d653a2e39e7034d61aea992a6bac26eba83  tx 0x17e8629af714541350ffe43dc0ac0355e37bf56ed585d77a353637034ef3e371
 2    3661-2 block 0xec8ae3564e92ee89c3669a102aa082b75dff2705c9b972277920c3902c91ea3c  tx 0x599106f3496c8a944131e45289cc91109e754153a10e97972846d17e356fb37c
 3    3662-2 block 0x8eb1da311811531d78a1904bcb7b72f1a6153176284f3669c2dadc9f99f5eaed  tx 0x86789a8de9f465c517c7d911212668c1c974ee586f72a8744e40e69913583d91
 4    3663-2 block 0x013ef88b72153d5e15fc0c2a466f9713ef41d22c23c64f779462826d61d24b43  tx 0x5d92b4cb38021b1db1a6054363015917a854120083d3246a2731bb62c3c49f5a
 5    3664-2 block 0xf44d96f48a1ebc8d6e277eb175ae044b730f66b80a12b5ad13f469aa8565a8c6  tx 0x20854df996480ccfbe6314c9fb4a746b568a78c939cc1c07f1dd6871821f7b32
 6    3665-2 block 0xd6d355faf5e4d495d8432835ccfe19021ddaf9320b6e61fdb8f8fc5353ecf197  tx 0x54b81cf0994ff0b8108fe412ae7ef3d6e0366ea09e9a78cf2d6b68c9bbc06f28
 7    3666-2 block 0xf4fe7f80dd8a62b5323a585595900ea498cc9711853eb34896fac2e98c5b4cd9  tx 0xc38c39f5bb57c6cfab60496978b2287be31c824775a476b4c0bddf0656a669c0
 8    3667-2 block 0x9dab1809722152d64220dfae22b7a0f0f77272109c4000f115bc8910ce068732  tx 0xdda4651ce1ddb37b5da7d63692f3071e7b4be8a602b2aa840a213b0065434448
 9    3674-2 block 0xfc78ea63c65b7b3b511b15e5eb4a672708b1e7d59b4d2ba9fb5ed23f4317d811  tx 0x6f87f70e3c02b82f6aa24cb857a122a2b3c962e06e5df858fd8a6c582de6a5d7
10    3675-2 block 0xb6c136a7a520ceb9246d18ff173499523141ae8c4cdc3061fa17a90097af0908  tx 0xf3776ca75827244002eac0eb6c3d0f89bf44fa6adafea73f61a0c29233d7f3a4
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x9dab1809722152d64220dfae22b7a0f0f77272109c4000f115bc8910ce068732`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2031).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xfc78ea63c65b7b3b511b15e5eb4a672708b1e7d59b4d2ba9fb5ed23f4317d811`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xb9e3a42e55d9700af7ea42f7bc92e18a4017de690422b92fe202de5746ba4bb1`, observed `0xb9e3a42e55d9700af7ea42f7bc92e18a4017de690422b92fe202de5746ba4bb1` at block `0xfc78ea63c65b7b3b511b15e5eb4a672708b1e7d59b4d2ba9fb5ed23f4317d811`
- ✅ control asset 2032 untouched (Live): expected `Live`, observed `Live` at block `0xfc78ea63c65b7b3b511b15e5eb4a672708b1e7d59b4d2ba9fb5ed23f4317d811`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xb6c136a7a520ceb9246d18ff173499523141ae8c4cdc3061fa17a90097af0908`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2027 — 2026-10-14T12:05:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `36450df` (clean) — [`evidence/drill-outage-standin-upstream-asset2027.json`](../evidence/drill-outage-standin-upstream-asset2027.json)
- asset 2023 — 2026-10-14T12:03:14Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-outage-standin-upstream-asset2023.json`](../evidence/drill-outage-standin-upstream-asset2023.json)
- asset 2019 — 2026-10-14T11:48:23Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json)
- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json) — failed: mint S1 = 50.00 of asset 2015 to the judge -> Err(Token.CannotCreate); mint S2 = 50.00 of control asset 2016 to the peer -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level); judge balance unchanged after the refused transfer
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json) — KeyError: 'partial_fee'
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### ReserveOracle on Revive — 2026-10-14T12:21:20Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0x7199a20b12ad30c6292715f5cfec363a2b8691a2` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T122120Z.json`](../evidence/oracle-revive-standin-upstream-20261014T122120Z.json) · result: **PASS** (5/5 steps as expected, 6/6 state checks) · source: `37acc11` (clean) · initcode sha256 `1ed85b9a1cd1dc07ec2759e5031088f40c89fd4c75f37ff4e27fec54a2b62cc9`

Posted values mirror drill `drill-drain-standin-upstream-asset2029.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `3676-2` | Ok | ✅ Ok |
| 2 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `3677-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 3 | B (reserve bot, attester) posts level state (pdBlock 3654) | `Revive.call` (B (reserve bot, attester)) | `3678-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 4 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `3679-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 5 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 3657) | `Revive.call` (B (reserve bot, attester)) | `3680-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    3676-2 block 0x1ff534bc67c3bef5c2e434b06c0b3654cc8385b268fa8bf1c5c1fbb590d5864e  tx 0x3a99d5f9743bf3d36d1e6fa7516b45573b3f3c304b5939143921639a995884ac
 2    3677-2 block 0x60a845115022f47cbbc5cbdaf44ee574ac43b0ba429fc01a126f28e1deaf6e0f  tx 0x0a761ffa07baef7a2af77195d0e6847c7ff71f8398672757f3dbc600c791cbb3
 3    3678-2 block 0x014796d9495aad774e7cf33e8556ef4c18bdb4704bc5fb2f0c9ec10b810f60e2  tx 0x77b5e30967fe7bf9868bdd57da837ae6336b8507a821f5f5f8db4aad588bce20
 4    3679-2 block 0x383609502102887a94f2916c4a4ad020157f965d63517e5b5ae0efd27c0d3df9  tx 0x96f483c710a6a6e16d9b098a9637aa54d9fc28798e80888ca62595ae0281bb2c
 5    3680-2 block 0x44610479df11f56b007450ade20f08b35ec60fc3ab167376d484cac5865e7fbf  tx 0x26c5726a8bee150444a51b2552230977f345788cb3e62fe0cf9cc363beee5052
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0x60a845115022f47cbbc5cbdaf44ee574ac43b0ba429fc01a126f28e1deaf6e0f`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0x60a845115022f47cbbc5cbdaf44ee574ac43b0ba429fc01a126f28e1deaf6e0f`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0x014796d9495aad774e7cf33e8556ef4c18bdb4704bc5fb2f0c9ec10b810f60e2`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0x383609502102887a94f2916c4a4ad020157f965d63517e5b5ae0efd27c0d3df9`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0x44610479df11f56b007450ade20f08b35ec60fc3ab167376d484cac5865e7fbf`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state: expected `[50000000, 50000000, 70000000, 52, '0x37915c827296ed31db1ec60f660159274f6cf1624c453e53a6c4beb8718ed7b3', 3657, True]`, observed `[50000000, 50000000, 70000000, 52, '0x37915c827296ed31db1ec60f660159274f6cf1624c453e53a6c4beb8718ed7b3', 3657, True]` at block `0x44610479df11f56b007450ade20f08b35ec60fc3ab167376d484cac5865e7fbf`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2025 — 2026-10-14T12:06:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `36450df` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T120608Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120608Z.json)
- asset 2021 — 2026-10-14T12:04:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/oracle-revive-standin-upstream-20261014T120408Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120408Z.json)
- asset 2001 — 2026-10-14T11:29:35Z — PASS (7/7 steps as expected, 6/6 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json)

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

- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
