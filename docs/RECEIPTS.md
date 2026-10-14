# Receipts

Every row below is a real extrinsic: re-fetch it by extrinsic id (`block-index`) with
`python scripts/check_receipts.py`. Full hashes and decoded events are in the linked JSON.

## Stand-in receipts — standin-upstream (not V3)

Measured on a local stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement; it is re-run on V3 once V3 is reachable.

### Spike run — asset 1002 — 2026-10-14T09:24:56Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1002.json`](../evidence/spike-assets-standin-upstream-asset1002.json) · result: **PASS** (12/12 steps as expected)

| # | Step | Call (signer) | Extrinsic id | Block hash | Tx hash | Expected | Observed |
|---|---|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x transfer_keep_alive]` (Alice, stand-in funder) | `200-2` | `0x455344d7…123766` | `0x857a1f13…22c482` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `201-2` | `0x648c9045…d12e96` | `0x7fd439d1…38ede0` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `202-2` | `0x18ed5249…549a71` | `0xdda65aec…68de42` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `203-2` | `0x7b4a02db…5ac068` | `0x1adcb91f…4a611e` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `204-2` | `0xe0afd0c0…790584` | `0x01032a2f…330d18` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `205-2` | `0xc3fff41c…2e7551` | `0x6800689b…e7d4c4` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `206-2` | `0x44637d1e…f48d84` | `0x197e859c…c8881e` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `207-2` | `0x922ff737…4b1534` | `0x86580cca…c7010d` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `208-2` | `0x9474b70e…e3601b` | `0x0db4fe8a…5771dc` | observe (I7 refuses in the bot) | ✅ Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `209-2` | `0xb13c6b60…2fa1cc` | `0xa7f6a46f…b6905f` | Err(Assets.*) — name pinned from metadata | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `210-2` | `0x4243aa30…804473` | `0xc662ffee…f11d74` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `211-2` | `0x2d5b932c…f77f9c` | `0x7c5154c0…587624` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

State checks (storage reads at the step's block):

- Asset(1002) freezer == M_watch: `True` at block `0x7b4a02db…5ac068`
- Asset(1002).status after freeze: `Frozen` at block `0xc3fff41c…2e7551`
- MultisigExecuted.multisig == locally derived M_watch: `True` at block `0xc3fff41c…2e7551`
- Peer balance after the frozen transfer: `0` at block `0xb13c6b60…2fa1cc`
- Asset(1002).status after admin thaw: `Live` at block `0x4243aa30…804473`
- Peer balance after the level transfer: `1000000` at block `0x2d5b932c…f77f9c`
