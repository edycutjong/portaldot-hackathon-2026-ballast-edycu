# Receipts

Every row below is a real extrinsic: re-fetch it by extrinsic id (`block-index`) with
`python scripts/check_receipts.py`. Full hashes and decoded events are in the linked JSON.

## Stand-in receipts — standin-upstream (not V3)

Measured on a local stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement; it is re-run on V3 once V3 is reachable.

### Spike run — asset 1003 — 2026-10-14T09:28:03Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1003.json`](../evidence/spike-assets-standin-upstream-asset1003.json) · result: **PASS** (12/12 steps as expected)

| # | Step | Call (signer) | Extrinsic id | Block hash | Tx hash | Expected | Observed |
|---|---|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x transfer_keep_alive]` (Alice, stand-in funder) | `263-2` | `0x9022e3cd…3adf05` | `0x3662d1d1…32910c` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `264-2` | `0xf2169c3b…75450f` | `0xdc2d825b…2c1242` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `265-2` | `0x75df6b12…fed1b5` | `0xc2c1a310…20891f` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `266-2` | `0x612f5164…6a6e16` | `0x61cd8cb7…686c5f` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `267-2` | `0x1f13c8eb…b6e38b` | `0x1aefacab…4ac852` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `268-2` | `0x85945c08…eba609` | `0x7c8232f5…a68972` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `269-2` | `0xa7696b95…818d4d` | `0xe87acb32…f10dee` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `270-2` | `0x0219417d…00f5c6` | `0x26b55556…01e3a6` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `271-2` | `0xd81160de…190b64` | `0x58e3990f…7e851e` | observe (I7 refuses in the bot) | ✅ Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `272-2` | `0xe09dbd51…fd9c53` | `0x0175bd96…f0c7d9` | Err(Assets.*) — name pinned from metadata | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `273-2` | `0x27182f4f…c990a9` | `0xdc23afa6…2d80c1` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `274-2` | `0x06cab951…c557bd` | `0x2ba64551…93c636` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

State checks (storage reads at the step's block):

- Asset(1003) freezer == M_watch: `True` at block `0x612f5164…6a6e16`
- Asset(1003).status after freeze: `Frozen` at block `0x85945c08…eba609`
- MultisigExecuted.multisig == locally derived M_watch: `True` at block `0x85945c08…eba609`
- Peer balance after the frozen transfer: `0` at block `0xe09dbd51…fd9c53`
- Asset(1003).status after admin thaw: `Live` at block `0x27182f4f…c990a9`
- Peer balance after the level transfer: `1000000` at block `0x06cab951…c557bd`

Earlier runs (full tables in the JSON):

- asset 1002 — 2026-10-14T09:24:56Z — PASS (12/12) — [`evidence/spike-assets-standin-upstream-asset1002.json`](../evidence/spike-assets-standin-upstream-asset1002.json)
