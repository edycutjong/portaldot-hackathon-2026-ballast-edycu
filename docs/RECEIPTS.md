# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). These rows are re-run on V3 once V3 is reachable.

### Spike run — asset 1006 — 2026-10-14T09:52:49Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `706-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `707-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `708-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `709-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `710-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `711-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `712-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `713-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `714-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `715-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `716-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `717-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1     706-2 block 0x51c6a53bd028a1db40332516e53914dd21c53f75d25a9fdbb5d41d7f3f583461  tx 0x7dfa33396df4fa2a510d661b32798e73b1b79376ede102eb7ee84b2916cf5fed
 2     707-2 block 0x0f0cb6cc21adb6e18274ff54ec99f77db2e72645ad6a0c6d05f6d335b23cd320  tx 0xa0b4f1e01579e8b9e01a9a06725f1f6f5f5388fcf3dbb055f12bc43496c33f3d
 3     708-2 block 0x273d65c289d57a0d18f4251c94af5289e7e8930e71c55d4d1728592f1af631bb  tx 0x703af6a80bb7a2a331b2925d54fd019a1d9af51c27dce611710d1eff4f302088
 4     709-2 block 0x599415517c3b3d4709c45adef104060f8e895ec404950c99252a26a28e4a1e4c  tx 0xd937d30db008d92c32fff50380d2eacc31464589ff61a44ad498e00ff500f1b4
 5     710-2 block 0x4cbc25d2d4cc20c9a819d3ab38c42eb668180e7047cd43f0f4486cff968c4162  tx 0xcd809c67b4a4cb5fc59387bfb87bac8898840acbd36e5da3b453d1aada038edc
 6     711-2 block 0xb6cbafec0b1029dcd24e6859b87747651c45e50991321c49335661831f2abb11  tx 0xad518681c4b6277793861563648212def87423cbfd932d2f8ed79d840a6622fb
 7     712-2 block 0xc84aa2e318f6cc35cd93212940741cc86fce659cc7080d3222bad3cbef27c897  tx 0xbe0d79fb7189356ab684f9e726f8af7e90c62d1301fcef3b20372428854f1be8
 8     713-2 block 0x7e59e5203e3e82f177eff830c0cfddedc0344e591efd332d3ae36ea217f50b31  tx 0x3ec6526a05a3ce724516da317cf5b758f448e63f4c22f9132962e3b77c5d39e8
 9     714-2 block 0x64cd84bf13db054a3dfdb7ad4c42b2aca4165526a1d76f250522dea53a4ab313  tx 0xe27388ddb1864c436636e18338df8fa086c47a16a26303ff88c163564526dc50
10     715-2 block 0x4996cedc6c81d5c75819e0ac4340c0f0e16ffef15b64dff6ae000aa5d6f6de24  tx 0x2fdac925dfe4af53325a8c4ca1ddc160ccccce12ec6ddb278dcd8054e6e09834
11     716-2 block 0x3fae9d9298d1f641a83b1cd41cfeb8a3a619b0f187c6ac171b3819e19914730f  tx 0xea5ffab0d987233675253b9b2b92f1c7efe39ec384929639269f627f58046055
12     717-2 block 0x23a4a08c619b1fd3cc9b256faf229131feaf68229b77b6776a4d22004c54a04e  tx 0x7a01fdf5b9b295f05e2d49ca65bfb31825caa4147a05a91b8b7f7f3836545f8b
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0x51c6a53bd028a1db40332516e53914dd21c53f75d25a9fdbb5d41d7f3f583461`
- ✅ Asset(1006) freezer is M_watch: expected `True`, observed `True` at block `0x599415517c3b3d4709c45adef104060f8e895ec404950c99252a26a28e4a1e4c`
- ✅ Asset(1006) issuer and admin are A: expected `True`, observed `True` at block `0x599415517c3b3d4709c45adef104060f8e895ec404950c99252a26a28e4a1e4c`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0x4cbc25d2d4cc20c9a819d3ab38c42eb668180e7047cd43f0f4486cff968c4162`
- ✅ Asset(1006).status after freeze: expected `Frozen`, observed `Frozen` at block `0xb6cbafec0b1029dcd24e6859b87747651c45e50991321c49335661831f2abb11`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0xb6cbafec0b1029dcd24e6859b87747651c45e50991321c49335661831f2abb11`
- ✅ Asset(1006).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0xc84aa2e318f6cc35cd93212940741cc86fce659cc7080d3222bad3cbef27c897`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0x4996cedc6c81d5c75819e0ac4340c0f0e16ffef15b64dff6ae000aa5d6f6de24`
- ✅ Asset(1006).status after admin thaw: expected `Live`, observed `Live` at block `0x3fae9d9298d1f641a83b1cd41cfeb8a3a619b0f187c6ac171b3819e19914730f`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0x23a4a08c619b1fd3cc9b256faf229131feaf68229b77b6776a4d22004c54a04e`

Earlier runs (full tables in the JSON):

- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
