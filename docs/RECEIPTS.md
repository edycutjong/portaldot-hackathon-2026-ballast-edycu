# Receipts

Every row below is a real extrinsic, identified by extrinsic id (`block-index`). Decoded events are
in the linked JSON; `python scripts/check_receipts.py` re-fetches every row from the chain it ran on.

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). These rows are re-run on V3 once V3 is reachable.

### Spike run — asset 1004 — 2026-10-14T09:40:39Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1004.json`](../evidence/spike-assets-standin-upstream-asset1004.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `463-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `464-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `465-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `466-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `467-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `468-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `469-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `470-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `471-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `472-2` | Err(Assets.AssetNotLive) or Err(Assets.Frozen) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `473-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `474-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1     463-2 block 0xeb59d77a41a77467d83b0fe7a752aab06947514441b3f46f29218a59827b6361  tx 0x702992276107ec02ce5eef8db5f32c66a306ce4b2bfb104ba52a91bea410760c
 2     464-2 block 0x37480e95c41cda606150df0de8e91b4c99bfd75d45a147877bf85053dc63d4fe  tx 0xc870ad7736129b757b7084e9ab354a5a943ea69f4b523b0c5698f60351e845a1
 3     465-2 block 0x63a9d715a9965e721a5794c9ce1d2abcc26c792d99a1143262520853317f7c27  tx 0xc0fb3391bb38300ef8130cc5765f39399b3bbba164697864cb81630aa46d2253
 4     466-2 block 0x0a34403f6db877e2656d683aa91b02e8f090152c50b17860f0db9e09c55601a2  tx 0x545ccc5073ab23cdbfbff54bba79570d8d18457b12b8e024cd08eb4651d73e21
 5     467-2 block 0x554c818b8e3f5b31a1139858006560fb83190a4dbc20337848bc5cdc93fc11e2  tx 0x0f52f2ea851bf5878f3b83d0c3322914dcf7c41a61f4bcc03d6957804aee6298
 6     468-2 block 0x4fd2f365a063e65951c053ce1235fb6db8d475d514fd3edf065eddbfeb5eeb65  tx 0x7841a37847bf518ec3e6e73701ecd0435aa4f2601f9a793ee8f282ae86318b08
 7     469-2 block 0x0c0e7a103fed68ab7c06f76297a3dc5269f74ffb80454f54dcb71d7501313c2a  tx 0xaa6db65adbb46e7ea7fb2e57605d792eee740c571252d9db5dc939bed37fed78
 8     470-2 block 0x6c95c273edbc09daa84cf3b8ee50ede3972a0ea06746db13eb2734cb45e03ade  tx 0xf04c436365625d2d8f61d9101f2d0c8b45a25511d4ed937f6c51664048f30963
 9     471-2 block 0x46c946954480bc14e57209a7c8177b13ecdc9c33f61995b421be49f6c6523373  tx 0x076f43262ad0edc165c9053a2a437600df7af444904cc02f26b0c66ecd801126
10     472-2 block 0x673b23b490d22042aec7cfeefb9096284900f0832db710feb9205245e8f2906f  tx 0x3dc2f40aeda783bbb568f38eae7ecf9225c8aa7b9e4ef15c8e085dd6109d22ac
11     473-2 block 0xfaf8d870bb1705ecbd83b058933149237eefeceb850a470ac1592525a340cadb  tx 0xa5405b70a74ac815d9f158b1a08a82a774fc771abfbb8094f559674e02155590
12     474-2 block 0x2e4c8d27fd4a875361bb76c41702cbfdd2c70783ba3c3ae9ad1e5dd87726a73b  tx 0xd1b3375ac2a6695364e53539b5a58b5845cccfb078da360428675314be24721a
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0xeb59d77a41a77467d83b0fe7a752aab06947514441b3f46f29218a59827b6361`
- ✅ Asset(1004) freezer is M_watch: expected `True`, observed `True` at block `0x0a34403f6db877e2656d683aa91b02e8f090152c50b17860f0db9e09c55601a2`
- ✅ Asset(1004) issuer and admin are A: expected `True`, observed `True` at block `0x0a34403f6db877e2656d683aa91b02e8f090152c50b17860f0db9e09c55601a2`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0x554c818b8e3f5b31a1139858006560fb83190a4dbc20337848bc5cdc93fc11e2`
- ✅ Asset(1004).status after freeze: expected `Frozen`, observed `Frozen` at block `0x4fd2f365a063e65951c053ce1235fb6db8d475d514fd3edf065eddbfeb5eeb65`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0x4fd2f365a063e65951c053ce1235fb6db8d475d514fd3edf065eddbfeb5eeb65`
- ✅ Asset(1004).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0x0c0e7a103fed68ab7c06f76297a3dc5269f74ffb80454f54dcb71d7501313c2a`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0x673b23b490d22042aec7cfeefb9096284900f0832db710feb9205245e8f2906f`
- ✅ Asset(1004).status after admin thaw: expected `Live`, observed `Live` at block `0xfaf8d870bb1705ecbd83b058933149237eefeceb850a470ac1592525a340cadb`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0x2e4c8d27fd4a875361bb76c41702cbfdd2c70783ba3c3ae9ad1e5dd87726a73b`
