# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

### Spike run — asset 1007 — 2026-10-14T09:58:42Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `824-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `825-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `826-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `827-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `828-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `829-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `830-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `831-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `832-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `833-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `834-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `835-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1     824-2 block 0x51f172daa1e05481ea8cfb33fc9d03be4278e97d98dcd8f26d630891eb92ee48  tx 0xb6a49ea2d5c41e57962bf9404830b9bf205ca9e1ca55988827c254219dc44051
 2     825-2 block 0x1b3d5ffd9ce8ef570a7ddd2d63c89086ca2062551874e7f810d1c12c7a256248  tx 0xa65f5c468f82ab6645975ab186c1a89d2db860b8d00e24661f875cdd3beb6330
 3     826-2 block 0xd1355f3f142c3239f7aabe295e4984c9c0f84ebdef33ea8a5d7b73522ee83e21  tx 0x10c97a907e93ca6d0f227654d81e4d1119494655937a26a47754ce1f7747c5d0
 4     827-2 block 0x826fd485ddd60e906aa58d8a1770a50689fd1c9ef32025a603c9a3a6b197f31f  tx 0x80da93a9575a558c0140ad6bf2fd46a6787af86e0be6169dac844d472c966d6f
 5     828-2 block 0x130a295508b21a1f9ae80995f3420d1835d74686dce0ea3b3e6f3488bee46ae2  tx 0xfb6abb1cfac47ca34366599b671c916f31f2d258351b4c80b5ddfc7682056ea7
 6     829-2 block 0x4eeff6ce8c5f36ef5e779d0a577a07534297afc185d78f7c6bfb54a86a7e3ba1  tx 0xe7825c50d781a54b2f828ac679249f9a4b5beff7a0a08f80be6a7720b5c0ab5d
 7     830-2 block 0xfb7f16200fe9394bf2ebb4a5ad373c48fae22b36db743a7df43c9cf14bcbcbac  tx 0xd9a475b353205498ad3c7c6a69744d9f87e150e88407ef3538743731d5a16db5
 8     831-2 block 0x102b81a5632efd7b1e85e964d06e21f677e5332ff10535539df1fe37c851d8ef  tx 0xfaa83257d1358732111a0e9387b29f699ac7f2129e0d6d63c2efb070a837a0ea
 9     832-2 block 0xa5ec355b5590a68388d09d451ebeebb01264eb5a5bfea5613f356629a45bb4d0  tx 0xe6cf5e4c1f96fb59203026f8a6e2dc4d66f60f1fe74fe459bea8ea16a940f985
10     833-2 block 0x286a35e105c1f78c911717585431e0a3258d052f23d2fa77213afe249590d248  tx 0x13a7b1a4945267c1f4b577c7a1124f82904f0c7a87868461126c4f0a81ca0252
11     834-2 block 0xfafafde19d36c621a104a5955f820984c1e0ee5b4496e3daa682264d48e09da2  tx 0xb491c0c3333b873990a160d3a7af48c9fc2ca487c014447aff0b210c44827cb8
12     835-2 block 0x07f34f24550a8822a462c935799ea5335b97f9e689b223b27a24f5030839b356  tx 0x7eecf3789814303bb6f77cdd32f6bf74ab4e3fd753c97fc0b785e80136c3e039
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0x51f172daa1e05481ea8cfb33fc9d03be4278e97d98dcd8f26d630891eb92ee48`
- ✅ Asset(1007) freezer is M_watch: expected `True`, observed `True` at block `0x826fd485ddd60e906aa58d8a1770a50689fd1c9ef32025a603c9a3a6b197f31f`
- ✅ Asset(1007) issuer and admin are A: expected `True`, observed `True` at block `0x826fd485ddd60e906aa58d8a1770a50689fd1c9ef32025a603c9a3a6b197f31f`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0x130a295508b21a1f9ae80995f3420d1835d74686dce0ea3b3e6f3488bee46ae2`
- ✅ Asset(1007).status after freeze: expected `Frozen`, observed `Frozen` at block `0x4eeff6ce8c5f36ef5e779d0a577a07534297afc185d78f7c6bfb54a86a7e3ba1`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0x4eeff6ce8c5f36ef5e779d0a577a07534297afc185d78f7c6bfb54a86a7e3ba1`
- ✅ Asset(1007).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0xfb7f16200fe9394bf2ebb4a5ad373c48fae22b36db743a7df43c9cf14bcbcbac`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0x286a35e105c1f78c911717585431e0a3258d052f23d2fa77213afe249590d248`
- ✅ Asset(1007).status after admin thaw: expected `Live`, observed `Live` at block `0xfafafde19d36c621a104a5955f820984c1e0ee5b4496e3daa682264d48e09da2`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0x07f34f24550a8822a462c935799ea5335b97f9e689b223b27a24f5030839b356`

Earlier runs (full tables in the JSON):

- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
