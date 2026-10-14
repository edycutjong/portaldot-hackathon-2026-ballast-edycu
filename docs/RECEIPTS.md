# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). These rows are re-run on V3 once V3 is reachable.

### Spike run — asset 1005 — 2026-10-14T09:46:51Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `587-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `588-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `589-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `590-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `591-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `592-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `593-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `594-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `595-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `596-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `597-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `598-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1     587-2 block 0xd342f93b1999b5778bb9b4a9c27600023e8d42423be30e0a80d524a62f1a7eb8  tx 0x1e97c920112b965547ee15314ab61a1457276b33f9c73d15539b1e73394bd257
 2     588-2 block 0x76f7071901025ed7c5403ac1c6924b83b083b06e7c0516b08d9b0a3bee538702  tx 0x1ccee659535a34e4d82011015c3791406f2e3f681301da87e87d0eae1fe135b6
 3     589-2 block 0xdac479f602033e4e7aad655ffb531e78fa45594e6a2bfe511d9e2db76e34f0e2  tx 0xa84c3a300beb72ef1e29daba0bd08172e759a77c45a0adaf76e2ca595a90e6a4
 4     590-2 block 0xc904ee1a8b22051717c5d67276c5b0488ea0a28d296787f3dcbcc835fe8a411e  tx 0x64352dcd3a4469a08570d8a644f4fb07b9f3f0b8031b9af60414d61b06a65351
 5     591-2 block 0xc6e50b5821fbdfe117252c449d6e693b6dddb7e02909711e0e3bf17aab59da32  tx 0x706bd8abcc5cb95f429acf68883370e66526b5dacda1b42bb555a0113a975758
 6     592-2 block 0xcfbd258b41d9d90fadb250bd2036aacac7f022bd6a25311fab7a88e44934f3e2  tx 0xda3a7219e6fc518e5ba76adebf4a6bc020669304da7790701e1417be77f11852
 7     593-2 block 0x212923c4f5aef4dcac20fe36ee632582f97932fd59659422f7a66461f5e1d5a2  tx 0xee83201b2a1ab8f602ab18ccb465d63c4fd7fee782b6fb349f71aa2940049329
 8     594-2 block 0x2fe4fb41b413c83e89ddfe1ed6691fd8152130a7bb704268328cb98a37f0bfdf  tx 0xbd634714be223e69c26151e4ebdbea0672a46a46f5867501389595af0bb0bf5f
 9     595-2 block 0x53e3e2e64c019686c8eb55e6ddb44ed06f383648b398622d2ada19bc3d64b749  tx 0x0c73af4bbd63bca731d07c622f35f302bb655bb55adf5edb5837b33c0092b100
10     596-2 block 0x6610b4f598a95892e67ae7f94a220a34dc02694e522ad80daa4cc64b39855be4  tx 0xa673ef6d231d24ca7f5ba2ce104e5927bb9bd7299c0f23a2d5823375f85fa59c
11     597-2 block 0x9fefb6580ac09d60ab7b8586b6baad7b7ceb0bc876b311c84ea1c10d0eaf0953  tx 0x1462576ca5f52e11585145aecee471beb2035167186041d83c9d9cb86da84cb4
12     598-2 block 0x865874b599df19e436afdfd3c117dce7b9aed9e57e0cc17833caa8632526e3b4  tx 0x07bf1f06db9f5062e571c5dd4d95602660e2df608db101eba77f5199a4f27fef
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0xd342f93b1999b5778bb9b4a9c27600023e8d42423be30e0a80d524a62f1a7eb8`
- ✅ Asset(1005) freezer is M_watch: expected `True`, observed `True` at block `0xc904ee1a8b22051717c5d67276c5b0488ea0a28d296787f3dcbcc835fe8a411e`
- ✅ Asset(1005) issuer and admin are A: expected `True`, observed `True` at block `0xc904ee1a8b22051717c5d67276c5b0488ea0a28d296787f3dcbcc835fe8a411e`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0xc6e50b5821fbdfe117252c449d6e693b6dddb7e02909711e0e3bf17aab59da32`
- ✅ Asset(1005).status after freeze: expected `Frozen`, observed `Frozen` at block `0xcfbd258b41d9d90fadb250bd2036aacac7f022bd6a25311fab7a88e44934f3e2`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0xcfbd258b41d9d90fadb250bd2036aacac7f022bd6a25311fab7a88e44934f3e2`
- ✅ Asset(1005).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0x212923c4f5aef4dcac20fe36ee632582f97932fd59659422f7a66461f5e1d5a2`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0x6610b4f598a95892e67ae7f94a220a34dc02694e522ad80daa4cc64b39855be4`
- ✅ Asset(1005).status after admin thaw: expected `Live`, observed `Live` at block `0x9fefb6580ac09d60ab7b8586b6baad7b7ceb0bc876b311c84ea1c10d0eaf0953`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0x865874b599df19e436afdfd3c117dce7b9aed9e57e0cc17833caa8632526e3b4`

Earlier runs (full tables in the JSON):

- asset 1004 — 2026-10-14T09:40:39Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1004.json`](../evidence/spike-assets-standin-upstream-asset1004.json)
