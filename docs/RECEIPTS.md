# Receipts

Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are
in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and
every drill reserve-chain tx from the local anvil. An index comes first, then the read-only Sepolia section.

## At a glance

Four places, each labelled on every row: the **Portaldot V3 testnet** (profile v3, real tPOT — every V3
extrinsic is also listed in [`PROOF.md`](PROOF.md)), the Portaldot **stand-in** chain (not V3), the
**local-anvil** reserve chain (not Sepolia), and **Sepolia** (read-only so far — see its section).

| Run | Portaldot chain | Reserve chain | Newest result (clean source preferred) | Evidence |
|---|---|---|---|---|
| Breaker drill against a REAL Sepolia ReserveVault (100.00 test USDC): freeze on V3, thaw after Sepolia finality | v3 | Sepolia | PASS (8/8 steps as expected, 18/18 state checks) | [`sepolia-drill-20261030T220145Z.json`](../evidence/sepolia-drill-20261030T220145Z.json) |
| Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw, team gate) | v3 | local-anvil (not Sepolia) | PASS (22/22 steps as expected, 20/20 state checks) | [`roles-drill-v3-20261024T045513Z.json`](../evidence/roles-drill-v3-20261024T045513Z.json) |
| Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw, team gate) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (22/22 steps as expected, 20/20 state checks) | [`roles-drill-standin-upstream-20261014T150211Z.json`](../evidence/roles-drill-standin-upstream-20261014T150211Z.json) |
| Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED) | v3 | local-anvil (not Sepolia) | PASS (15/15 steps as expected, 6/6 state checks) | [`roles-attest-v3-20261024T050653Z.json`](../evidence/roles-attest-v3-20261024T050653Z.json) |
| Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (15/15 steps as expected, 6/6 state checks) | [`roles-attest-standin-upstream-20261014T150338Z.json`](../evidence/roles-attest-standin-upstream-20261014T150338Z.json) |
| Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless | v3 | local-anvil (not Sepolia) | PASS (16/16 steps as expected, 6/6 state checks) · ran from uncommitted changes | [`roles-setup-v3.json`](../evidence/roles-setup-v3.json) |
| Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (16/16 steps as expected, 5/5 state checks) | [`roles-setup-standin-upstream.json`](../evidence/roles-setup-standin-upstream.json) |
| Breaker drill, scratch asset: drain -> freeze | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (14/14 steps as expected, 11/11 state checks) | [`drill-drain-standin-upstream-asset2039.json`](../evidence/drill-drain-standin-upstream-asset2039.json) |
| Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6) | v3 | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 8/8 state checks) | [`drill-outage-v3-asset4501.json`](../evidence/drill-outage-v3-asset4501.json) |
| Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 8/8 state checks) | [`drill-outage-standin-upstream-asset2041.json`](../evidence/drill-outage-standin-upstream-asset2041.json) |
| Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8) | v3 | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 9/9 state checks) | [`drill-heartbeat-v3-asset4503.json`](../evidence/drill-heartbeat-v3-asset4503.json) |
| Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 9/9 state checks) | [`drill-heartbeat-standin-upstream-asset2043.json`](../evidence/drill-heartbeat-standin-upstream-asset2043.json) |
| ReserveOracle on Revive, mirroring a drill | standin-upstream (stand-in, NOT V3) | — | PASS (5/5 steps as expected, 6/6 state checks) | [`oracle-revive-standin-upstream-20261014T150859Z.json`](../evidence/oracle-revive-standin-upstream-20261014T150859Z.json) |
| Assets spike: watcher-set freeze, freezer thaw refused | standin-upstream (stand-in, NOT V3) | — | PASS (11/11 steps as expected + 1 observation, 10/10 state checks) | [`spike-assets-standin-upstream-asset1010.json`](../evidence/spike-assets-standin-upstream-asset1010.json) |

## Sepolia (read-only — no Ballast contract is deployed on Sepolia yet)

The Sepolia `ReserveVault` deploy, its 100.00 USDC deposit and the real-Sepolia drill wait until the deployer wallet holds >= 100.00 Circle test USDC; the reads below show what it holds. Every drill above uses the local-anvil reserve instead, labelled as such.

- [`evidence/sepolia-crosscheck-2026-10-14-p4.json`](../evidence/sepolia-crosscheck-2026-10-14-p4.json) — read at 2026-10-14T13:01:33.877Z: finalized block #11913325 via 2 providers — AGREE (publicnode: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000, drpc: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault. P4 row 3 gate (2026-10-14): the ReserveVault deploy + 100.00 USDC deposit need >= 100000000 (100.00 USDC, 6 decimals) in this wallet; the balance read here is lower, so no Sepolia vault was deployed (waiting on the Circle faucet)
- [`evidence/sepolia-crosscheck-2026-10-14-p5.json`](../evidence/sepolia-crosscheck-2026-10-14-p5.json) — read at 2026-10-14T14:59:47.420Z: finalized block #11913933 via 2 providers — AGREE (publicnode: `0x38042e59670bff3aeda838faba65592f918e0f75a96bde863fa410b582fc4bda` reserves 20000000, drpc: `0x38042e59670bff3aeda838faba65592f918e0f75a96bde863fa410b582fc4bda` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia (wallet below 100.00 USDC). P5 evidence refresh.
- [`evidence/sepolia-crosscheck-2026-10-14.json`](../evidence/sepolia-crosscheck-2026-10-14.json) — read at 2026-10-14T11:41:44.199Z: finalized block #11912942 via 2 providers — AGREE (publicnode: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000, drpc: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia yet; this file shows the two-provider reader agreeing on one finalized block

## V3 receipts — v3

Chain label: Portaldot V3 testnet

### Sepolia drill — real ReserveVault + 100.00 test USDC, drain -> freeze on V3, thaw only after Sepolia finality — 2026-10-30T22:01:45Z

Chain: **Portaldot V3 testnet** · reserve: **Sepolia** · raw JSON: [`evidence/sepolia-drill-20261030T220145Z.json`](../evidence/sepolia-drill-20261030T220145Z.json) · result: **PASS** (8/8 steps as expected, 18/18 state checks) · source: `2dbd35c` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

- owner before: {'address': '0xDEf7Cd11f524C2246571654110b43476C2BD9300', 'eth_wei': 199749845188377967, 'usdc': 19896195}
- vault: resumed 0x7ceB7c3EBDBCC75e585599e5dd944286F009357b
- other watcher: W2 saw asset 4401 already frozen at #258435 and stood down
- drain -> freeze included (wall clock, one machine; Sepolia reserve + V3): 10.26 s
- re-deposit sent -> finalized (wall clock, both providers): 1067 s
- owner after: {'eth_wei': 199749845184005899, 'usdc': 19896195, 'vault_reserves': 100000000}

Reserve-chain transactions (Sepolia; vault `0x7ceB7c3EBDBCC75e585599e5dd944286F009357b`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | vault owner drains 30% (30.00) — release() | 12029614 | [`0x6e5f5421a52a5d999d61c25b8bf29c64563a3cd81a10e8761c0dd49424d5e256`](https://sepolia.etherscan.io/tx/0x6e5f5421a52a5d999d61c25b8bf29c64563a3cd81a10e8761c0dd49424d5e256) | ✅ status 1 |
| 2 | vault owner re-deposits 30.00 | 12029618 | [`0xd39d7f8f72572af30521ae7cde8f6a59291c27bcf6ce7bd002a16af182d540d5`](https://sepolia.etherscan.io/tx/0xd39d7f8f72572af30521ae7cde8f6a59291c27bcf6ce7bd002a16af182d540d5) | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | watcher W1 freezes asset 4401 on V3 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W1 (watcher)) | `258434-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 2 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `258436-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 3 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `258437-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 4 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `258443-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 5 | bot B co-signs the thaw: finalized Sepolia reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `258627-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 6 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `258628-1` | Ok | ✅ Ok |

Block and transaction hashes (full):

```
 1  258434-1 block 0xce45219122924516d8e2f7ea79a3a0b88b3919f08ee8585621495db19b3ea889  tx 0xd8a3b88fc3fe186ac598f0ef7680a13446107152d5cb50c5737d893c639995cf
 2  258436-1 block 0x464470e6afdaad2dfa4ae75fdcff1bc001758ec9d11c54ce2ca7b1ba44ff6ae2  tx 0xe2d3d7947351e275c35ddc8f1fdfdc26ba48de8211480a7b01ae503f474cd01e
 3  258437-1 block 0x6e41dd3845c09604ffbf6b8d29a751c7e49b59aa8964135b2407785ec365f828  tx 0x6797da4fa957d4522887181d1b03fd1f6500e4b8d63046181f178222f8665279
 4  258443-1 block 0x2a56b11336dfad9928b37273c29b81ff703c84ecfeeddcf0f256296a8e2c3ac8  tx 0xdaf303f85c0f203b1aa42acb28f5738e1af9183b8cf34b4b10fb799a3583afcd
 5  258627-1 block 0x6d82138a1e0e6b4bf5a70188262d7cde147da3861e29e6db852ccd3bf889e582  tx 0xa81af085af7d572bbf5d274e81c13735723f81ee7dd1a63f733d84770b5ba34d
 6  258628-1 block 0x1a6b01d5fdf5bbc9d469dec6c32108c3e06af41ca5630dfcbf477b95decafdd0  tx 0xf7bccc7003c1f1ec919c9c866e3fd313b39b16b64a0a6af772a336bfa6183a73
```

State checks (storage/events read at the step's block):

- ✅ asset 4401 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ vault holds the 100.00 deposit and the owner holds gas (the drain pays the refill): expected `True`, observed `True` at block `sepolia latest`
- ✅ S1 + S2 == 100.00 before the deposit: expected `100000000`, observed `100000000` at block `head`
- ✅ vault.owner() == the Sepolia deployer: expected `0xDEf7Cd11f524C2246571654110b43476C2BD9300`, observed `0xDEf7Cd11f524C2246571654110b43476C2BD9300` at block `sepolia latest`
- ✅ vault.usdc() == Circle test USDC: expected `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238`, observed `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238` at block `sepolia latest`
- ✅ vault.reserves() == 100.00: expected `100000000`, observed `100000000` at block `sepolia latest`
- ✅ [publicnode] vault.reserves() at the finalized head #12029545 == 100.00: expected `100000000`, observed `100000000` at block `sepolia finalized #12029545`
- ✅ [tenderly] vault.reserves() at the finalized head #12029545 == 100.00: expected `100000000`, observed `100000000` at block `sepolia finalized #12029545`
- ✅ both watchers armed and level on the Sepolia reserve (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's Sepolia block: expected `12029614`, observed `12029614` at block `0xce45219122924516d8e2f7ea79a3a0b88b3919f08ee8585621495db19b3ea889`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 4401 status after the freeze: expected `Frozen`, observed `Frozen` at block `0xce45219122924516d8e2f7ea79a3a0b88b3919f08ee8585621495db19b3ea889`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `sepolia latest`
- ✅ bot refuses the thaw: Sepolia finality has not reached the drain block yet: expected `['refused', 12029614]`, observed `['refused', 12029614]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `258434-1`, observed `258434-1` at block `0xce45219122924516d8e2f7ea79a3a0b88b3919f08ee8585621495db19b3ea889`
- ✅ asset 4401 status after the thaw: expected `Live`, observed `Live` at block `0x6d82138a1e0e6b4bf5a70188262d7cde147da3861e29e6db852ccd3bf889e582`
- ✅ asset 4401 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ all 2 Sepolia txs re-read from both providers: status 1, same block, <= finalized {'publicnode': 12029641, 'tenderly': 12029641}: expected `True`, observed `True` at block `sepolia finalized`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-31T00:08:05Z — ERROR (4/4 steps as expected, 12/12 state checks) — source: `fc371f3` (clean) — [`evidence/sepolia-drill-20261031T000804Z.json`](../evidence/sepolia-drill-20261031T000804Z.json) — ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
- asset 4401 — 2026-10-30T23:16:33Z — FAIL (7/8 steps as expected, 17/18 state checks) — source: `b77e02f` (clean) — [`evidence/sepolia-drill-20261030T231633Z.json`](../evidence/sepolia-drill-20261030T231633Z.json) — failed: watcher W2 freezes asset 4401 on V3 through M_watch (reason=deficit) -> Ok; freeze remark eb == the drain's Sepolia block
- asset 4401 — 2026-10-30T21:23:30Z — FAIL (8/8 steps as expected, 17/18 state checks) — source: `9c2112e` (clean) — [`evidence/sepolia-drill-20261030T212330Z.json`](../evidence/sepolia-drill-20261030T212330Z.json) — failed: vault holds the 100.00 deposit; owner holds gas and >= the refill (30%)
- asset 4401 — 2026-10-30T20:46:14Z — FAIL (8/8 steps as expected, 17/18 state checks) — source: `1328f88` (clean) — [`evidence/sepolia-drill-20261030T204614Z.json`](../evidence/sepolia-drill-20261030T204614Z.json) — failed: owner holds >= 100.00 test USDC and gas
- asset 4401 — 2026-10-30T20:09:23Z — PASS (12/12 steps as expected, 18/18 state checks) — source: `cff62bc` (UNCOMMITTED CHANGES) — [`evidence/sepolia-drill-20261030T200923Z.json`](../evidence/sepolia-drill-20261030T200923Z.json)

### Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw — 2026-10-24T04:55:14Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-drill-v3-20261024T045513Z.json`](../evidence/roles-drill-v3-20261024T045513Z.json) · result: **PASS** (22/22 steps as expected, 20/20 state checks) · source: `04a1de4` (clean)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

- other watcher: W1 saw asset 4401 already frozen at #170113 and stood down
- drain -> freeze included (wall clock, one machine; local anvil + stand-in): 12.22 s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x22753E4264FDDc6181dc7cce468904A80a363E44`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1555 | `0xc9c30aabd8707442ac5037666a6a91889d3ad8f393449fbb497634a8e1185385` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1556 | `0x531062078693c9552dc07d82a098cccbdf3822e31b1d25e84cfb9eddceffae0f` | ✅ status 1 |
| 3 | custodian drains 30% (31.20) — release() | 1622 | `0xec4b585e18bb55d8b8c9a117b9e2b54790d63e0d98982f6e5935a1933bc482c0` | ✅ status 1 |
| 4 | custodian re-deposits 31.20 | 1623 | `0xd07e14157791ef65b12811161b63181745f66c110bb4046017e4d7940a8deb50` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | A proposes mint 1.00 to the judge through M_mint (first approval) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170095-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 2 | bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `170098-1` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 3 | A proposes 0.01 more (reserves cover S1 + S2 exactly) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170100-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 4 | A cancels the refused proposal (deposit returned) | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `170105-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 5 | watcher W2 freezes asset 1 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `170112-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 6 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `170114-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 7 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `170115-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | A proposes a mint while frozen | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170117-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | A cancels it | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `170122-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 10 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `170125-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 11 | bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `170133-1` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 12 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `170134-1` | Ok | ✅ Ok |
| 13 | A proposes set_team with the freezer moved to A (through M_mint) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170137-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | A cancels the refused team change | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `170142-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 15 | A proposes set_team making A the sole admin (could thaw without the bot) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170145-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 16 | A cancels the refused admin swap | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `170150-1` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 17 | A proposes set_team keeping issuer M_mint, admin M_admin, freezer M_watch | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `170153-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | bot co-signs the safe team change | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `170156-1` | Ok + inner Ok + Assets.TeamChanged | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.TeamChanged |

Block and transaction hashes (full):

```
 1  170095-1 block 0xa1b86ec21d400d31f26081c7f6d35475dd1eb457541f521cedf2cb8660e646ba  tx 0x79fa8945cfcd5e6c700ef88342447cedb84b148849d531237100df6a9819bbec
 2  170098-1 block 0xfb7fb01bf22f668170ba5ff05be91e6f22c5b3e4edc87773dc5b0bfc69087408  tx 0xe274c22b2988acc530ca2cd77e212cb1f10c60256b5506e9d4d66b3eb49fae72
 3  170100-1 block 0x984ecaa0618540d951e95043fe363b59ae034a53ca14194faa5c14bd797c997a  tx 0x6d9d6f7c61d342e563156aa9a848711bb4c724132e79e6824cf1468b306e08b5
 4  170105-1 block 0xfff8dbd612f8b7e5d8d0655dfb92c1e37f5efd3d610fbecf6a101c165d0fc69e  tx 0x20b102c0fd1b2bf7bcafa4cdafde7644322836e1642a5e75c5056977e1e8e2a0
 5  170112-1 block 0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624  tx 0xffe640fc27e08c3bede83e1172bf077c244ba0b183f3ef3436b7103f8d2e78dc
 6  170114-1 block 0x9d34fa883f7993a8a44d74e4864afad56ab6075379e70b3694c0be620f7fc0a3  tx 0x01bedef89109fc0e0a14857c83e452927e0b43d84b9485a38b63c1423b39f83c
 7  170115-1 block 0x4fabb599f4c828fdd8055d3e1a904ea08a70d29a7b0593201bee1a46374f341d  tx 0x52629a74f9cbe18fef752bd5f49e5842ff9729c29ac62511e81a3a29858587a4
 8  170117-1 block 0xd23f13fe567c3173aa4a4a84a06c25d9e4a4a0705984507f1f3f3ce11d780239  tx 0x92448dd6d3b5bfc44dfd056c9261e54fdf653ab2dc400e3469557ca40f4d5082
 9  170122-1 block 0x94da049932c6f2cd214c423a0d0f34517faaab961bb3f69646fd9f9b027714e2  tx 0x65a7e30f27095a9ac77f01bc66d468746016f6493ccbf2fbb6bda31d8f710c0e
10  170125-1 block 0x63a4ba67dee18befcdab2e70390173e7bed78dcaf3406ae3a8a76ac832fcb398  tx 0xe24d8263bcc6840669e1a1875b638cf7030dab8f2b08990e8d436780d71c740c
11  170133-1 block 0xaa1fae018db52208466a9f4abf26890b3130cae019428438a551289da040110b  tx 0x992761a1faa4f3ef53b72f5e2a13e1bceb13c7badecf795d4573cb09dfc75893
12  170134-1 block 0xc78172b6a6dbbd6ea7483b3315587d24b390b0958247c04ed092018fed3d6000  tx 0xb2a98606ba0458ac43bc32e88862a377d8ea3e0c9cb2beca5bd3d8060b3bccda
13  170137-1 block 0xfbfde0de3232e12cfde1986fe28a0e44874079ecdf0c8bc74f92cbb04c30ca2d  tx 0xde7106b296eb5005c415b5bf55f26f59a5f7d48d6cb3e29ef1b1f231ac28325b
14  170142-1 block 0x8790daa5fd43fc45a2e407ef26c47dc7d1b32229599023c46eb6129785dbbabc  tx 0x1ec5950da440fb7e690bb636711cd04f52701ad4f4d00d8bcf2eec10db8d9eae
15  170145-1 block 0x3f3907da00159edbd8e6456682974f13bccf8216611badfb56700bdc91c0a802  tx 0x5a030cdc8ee3e91affb569b187ce3de99147e7e0241d3019edbb8cb1bdf1b4c0
16  170150-1 block 0xc27c53b0979ad62c83bdd2c64d3e5fe46f8365cd4b5d6e320d3b5bbf36e08c94  tx 0x72993cc27837580b8aa721e8a8641bdcb86b5a62800641c7b3ceb883d2651ab8
17  170153-1 block 0x2d126c6a06729c943ae91ee1fa5f39fe2352b5b3ce52390ebb7bb2e68c863903  tx 0x4ece343e5601b4e5e460f29b2cb1e51f760a4ddcf987d578bdf01f2d11f88d8e
18  170156-1 block 0xb82d68a566fac58fefe36d0c30638a84f00bb353499b65316d05c01f87057724  tx 0x81a1afb210f40bf65fec0c4b9007c8757852e2bd5933525b7b573dcea0e5a837
```

State checks (storage/events read at the step's block):

- ✅ asset 1 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the drill: vault reserves == S1 + S2: expected `103000000`, observed `103000000` at block `head`
- ✅ S1 after the gated mint == S1 + 1.00: expected `54000000`, observed `54000000` at block `0xfb7fb01bf22f668170ba5ff05be91e6f22c5b3e4edc87773dc5b0bfc69087408`
- ✅ bot refuses the over-mint (exit 1, no signature): expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ over-mint still pending (no MultisigExecuted): approvals == [A]: expected `['A (operator)']`, observed `['A (operator)']` at block `0xb15bd3765288f68e395a55247fa0af0eea5d0625554ba7b1daa34a6110b16018`
- ✅ S1 unchanged by the refused over-mint: expected `54000000`, observed `54000000` at block `0xb15bd3765288f68e395a55247fa0af0eea5d0625554ba7b1daa34a6110b16018`
- ✅ no pending over-mint after the cancel: expected `None`, observed `None` at block `0xfff8dbd612f8b7e5d8d0655dfb92c1e37f5efd3d610fbecf6a101c165d0fc69e`
- ✅ both watchers armed and level (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's reserve-chain block: expected `1622`, observed `1622` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 1 status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ bot refuses any mint while frozen (I7): expected `I7`, observed `I7` at block `bot`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `evm latest`
- ✅ bot refuses the thaw: finality has not reached the drain block yet: expected `['refused', 1622]`, observed `['refused', 1622]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `170112-1`, observed `170112-1` at block `0xc79cc70675b5486c51e0409cc5f74b5d1608ee4f30fc45d5971754c65e39f624`
- ✅ asset 1 status after the thaw: expected `Live`, observed `Live` at block `0xaa1fae018db52208466a9f4abf26890b3130cae019428438a551289da040110b`
- ✅ asset 1 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ bot refuses a set_team that changes the freezer: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ bot refuses a set_team that moves the admin off M_admin: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ asset 1 team after the co-signed set_team (ARMED): expected `[]`, observed `[]` at block `head`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-24T04:47:34Z — ERROR (24/24 steps as expected, 20/20 state checks) — source: `26e345b` (clean) — [`evidence/roles-drill-v3-20261024T044734Z.json`](../evidence/roles-drill-v3-20261024T044734Z.json) — JSONDecodeError: Expecting value: line 1 column 1 (char 0)
- asset 4401 — 2026-10-24T04:45:14Z — ERROR (5/5 steps as expected, 3/4 state checks) — source: `586d6ef` (UNCOMMITTED CHANGES) — [`evidence/roles-drill-v3-20261024T044514Z.json`](../evidence/roles-drill-v3-20261024T044514Z.json) — AttributeError: 'NoneType' object has no attribute 'approvals' — failed: bot refuses the over-mint (exit 1, no signature)
- asset 4401 — 2026-10-24T04:42:42Z — ERROR (3/3 steps as expected, 2/2 state checks) — source: `586d6ef` (clean) — [`evidence/roles-drill-v3-20261024T044242Z.json`](../evidence/roles-drill-v3-20261024T044242Z.json) — RuntimeError: bot did not co-sign the covered mint: reserves unreadable: finalized: no provider answered a finalized reading; latest: no provider answered a lat

### Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control — 2026-10-24T05:06:53Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-attest-v3-20261024T050653Z.json`](../evidence/roles-attest-v3-20261024T050653Z.json) · result: **PASS** (15/15 steps as expected, 6/6 state checks) · source: `6eceb6e` (clean)

`ballast verify` blocks #170208..#170253 ([`evidence/verify-v3-20261024T050653Z.json`](../evidence/verify-v3-20261024T050653Z.json)): **PASS** — 4/4 B attestations PASS on both chains, 1 REJECTED (not counted), 0 FAIL/FLAGGED.

Heartbeat H = 20 blocks (drill override; production H = 100, K = 300 on this profile).

- finality (anvil): mined 65 blocks: finalized = latest − 64

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x22753E4264FDDc6181dc7cce468904A80a363E44`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1756 | `0x3931541bf6beeaa9df046c0d6d2e4ee137d0744444ef9294264736542e5dadd6` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1757 | `0xec30f111a44ea7f1a2625feeeae406a372dfbb7395a54f0c8d1ca373f0a379b1` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | bot announces watchers (BALLAST/1|watchers|t=1|m=5DG4akHnFL58yotBXtZ1tiqXeWASRh5em1i…) | `System.remark_with_event(BALLAST/1|watchers)` (B (reserve bot)) | `170214-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 2 | bot announces evm-attester (BALLAST/1|evm-attester|h160=0xc81ab822279e828b16a2be9a55520e…) | `System.remark_with_event(BALLAST/1|evm-attester)` (B (reserve bot)) | `170215-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 3 | bot posts attest (pb 170212) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170216-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 4 | bot mirrors 170216-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170217-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 5 | bot posts attest (pb 170215) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170218-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 6 | bot mirrors 170218-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170219-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 7 | A proposes mint 1.00 through M_mint | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `170221-1` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 8 | bot B co-signs (finalized reserves cover it) | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `170224-1` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 9 | bot posts attest (pb 170225) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `170228-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot mirrors 170228-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170229-1` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 11 | bot posts heartbeat (pb 170249) | `System.remark_with_event(BALLAST/1|heartbeat)` (B (reserve bot)) | `170252-1` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 12 | negative control: the judge key posts a copy of the bot's attestation | `System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key` (Judge (negative control)) | `170253-1` | Ok + System.Remarked (included — verify must REJECT it) | ✅ Ok · System.Remarked |
| 13 | bot mirrors 170252-1 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `170253-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1  170214-1 block 0x0d4b761d645cb956f512dae0b97ef1fb72ffb44c24f3d6ab165657f5493180c6  tx 0x4c3562e9c701a4edd830af7420176596967eff5ea7bfa1150553a7f73d8746e2
 2  170215-1 block 0x96991d27f8a61aceb62e40fb10a2dc03827449cb6955e2b4b1d463bd2f99c4be  tx 0x1414a8921508ffff6c51c0f120c520338dcb93f11447bfac38b21a0018aad941
 3  170216-1 block 0x4b0ef2aa7787bed5365b5ab8b9dad840a9864a4178e8fd7cb65908f4227a760d  tx 0x625dcab0755317249606b5da8fe6b9315d83ff5703381d0a499bc653ce0beac4
 4  170217-1 block 0x40d35c389ba40456b65d27b4e5fc8921b403260a941ef8adca73df0cf8854d3f  tx 0xcb7095e3e87e53ef696407f8f7408b66597bc0dfe38146df8b75e105c09a3bac
 5  170218-1 block 0x010714a3243c38051bdaacc19d32c09f5e1755fb394836c626561891a8a1e7c9  tx 0xd882062f40fe5e83717f5b1fc7bb9ff6ef2e83f8f59cce0b48fbc95a65f2e70e
 6  170219-1 block 0x054f7d0af02aa4f4c19c868a79782da0a778d0a85e88bf3073bfa6427df7accf  tx 0xc8c8fd0d94d952fbae91f265e5895f1093e6f421f39f2d8ddeb1f58f9d24f565
 7  170221-1 block 0xe41b1aa65e5470deca1a2fc70c7f4e9cdbe66f50f7c566cede4ee273329749a5  tx 0xa1b93e2dd5d209c6e97d4a4dd1602675ba1b9f88a98dea755a445bcead3b93c7
 8  170224-1 block 0x7e53c4a58a901a96ad7317aaf74eab431d331a9e4da0a4ddf5bc1a18435c9ad9  tx 0xcb397679122a845819ea39d870c1fc996e720955cada011965dee97e74c308c9
 9  170228-1 block 0x28f7c2e671a2fff6e2b83aff45270d0afc304b3a24e71ffaae80a228701970b7  tx 0xe6365fdf3cb3b1e3a90377deb14e63b067a7467cdff6bdfc53e0e16a90dc94d9
10  170229-1 block 0x7fff3f07e4559f35e26d94733599aaccd29819f267ae0f9f0d675f38a3adec3c  tx 0xa6b855491413d8c650ad0cc22197dbabb23fffa6a05de8e7770d88765af49798
11  170252-1 block 0x34517cc1bda8ce103f045715a68a3c12b3f74f764ee9584657071e8a684a8908  tx 0xb35393c9def9e5c4a9530363fa7dccd5755dfe1f4d88b029da7dc8c485945aca
12  170253-1 block 0x515f1c6dcf46d0b648cd49e2b2f76261b577f8b0c1d14b1e9afd5ecfecab5fca  tx 0x6d4fa93541f1b25e83f0829ff02f2e32ecd5c3bbe8995e97bb34e69c8831ae21
13  170253-2 block 0x515f1c6dcf46d0b648cd49e2b2f76261b577f8b0c1d14b1e9afd5ecfecab5fca  tx 0x35c3b47ca3b75457eca093bec34be339a366a1db7affbb911249b05de5438e3b
```

State checks (storage/events read at the step's block):

- ✅ the post after H quiet blocks is a heartbeat: expected `heartbeat`, observed `heartbeat` at block `0x34517cc1bda8ce103f045715a68a3c12b3f74f764ee9584657071e8a684a8908`
- ✅ verify exit 0 and verdict PASS: expected `[0, 'PASS']`, observed `[0, 'PASS']` at block `verify`
- ✅ every bot attestation/heartbeat PASSes on both chains: expected `4`, observed `4` at block `verify`
- ✅ every oracle post matches a PASSing remark (I10): expected `4`, observed `4` at block `verify`
- ✅ the forged remark is listed REJECTED (not counted): expected `['170253-1']`, observed `['170253-1']` at block `verify`
- ✅ watcher-set and evm-attester announcements PASS: expected `[1, 1]`, observed `[1, 1]` at block `verify`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 4401 — 2026-10-24T05:01:57Z — ERROR (13/13 steps as expected, 1/1 state checks) — source: `8ee7557` (clean) — [`evidence/roles-attest-v3-20261024T050157Z.json`](../evidence/roles-attest-v3-20261024T050157Z.json) — JSONDecodeError: Expecting value: line 1 column 1 (char 0)

### Role split — asset 1 (breaker) + asset 2 (control), reserve vault, ReserveOracle — 2026-10-24T04:41:31Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-setup-v3.json`](../evidence/roles-setup-v3.json) · result: **PASS** (16/16 steps as expected, 6/6 state checks) · source: `775e97c` (UNCOMMITTED CHANGES)

Role map: `M_mint` 5Gs33AvvC3XAZC6nJoRg2ybLbrUiNKSiFu78u1r13J3L2sUb (2-of-2 A, B) · `M_admin` 5HZshac58eX5TC2AErdfvU2m4rHVtoQUv31479nd1jaHbGRg (2-of-3 A, A2, B) · `M_watch` 5CpFnhgHCreAk1bvwHJTxsQoDu6N7eivEBANZH44JqwJCK5c (1-of-2 watchers).

Reserve-chain transactions (local-anvil (not Sepolia); vault `None`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1217 | `0xcdef806dd63f8366afaf0576375093f6299df8aac2d740ccf3654edac098cdb7` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1218 | `0x286bb9ad4e337c2d68d29fc6a5fc83508ef63f86c21a1cc879f81874a823d1c7` | ✅ status 1 |
| 3 | custodian receives 100.00 test tokens | 1219 | `0xe9627e59bcf7e5538d47024bafab02ab2d873045493abd973859e6f0f99a2d53` | ✅ status 1 |
| 4 | deposit S1 + S2 = 100.00 — plain ERC-20 transfer into the vault | 1220 | `0x1457a7d9311d1136f9f82ebe6de5eb16afa1cd266ba7d1dc23edef933b0619a4` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, A2, B, W1, W2, judge, peer, M_mint, M_admin, M_watch, asset-2 keyless owner (>= ED) | `Utility.batch_all[11 x Balances.transfer_keep_alive]` (funder (human-funded)) | `169920-1` | Ok | ✅ Ok |
| 2 | A creates asset 4401 | `Assets.create` (A) | `169921-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `169922-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A creates asset 4402 | `Assets.create` (A) | `169923-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `169924-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | A mints S2 = 50.00 of control asset 4402 to the peer (its only mint) | `Assets.mint` (A) | `169925-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 7 | asset 4401 set_team(issuer=M_mint, admin=M_admin, freezer=M_watch) | `Assets.set_team` (A) | `169926-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 8 | asset 4401 transfer_ownership(M_mint 2-of-2 {A, B}) | `Assets.transfer_ownership` (A) | `169927-1` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 9 | asset 4402 set_team(keyless issuer, admin, freezer) | `Assets.set_team` (A) | `169957-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 10 | asset 4402 transfer_ownership(keyless owner) | `Assets.transfer_ownership` (A) | `169958-1` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 11 | A alone tries to mint asset 4401 (issuer is M_mint) | `Assets.mint` (A) | `169959-1` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B deploys ReserveOracle(attester = 0xc81ab822279e828b16a2be9a55520e475fa98678) | `Revive.instantiate_with_code(ReserveOracle)` (B) | `169960-1` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |

Block and transaction hashes (full):

```
 1  169920-1 block 0xea492def23d67d425450ee027f28afa8edefb39cdf8a6f0593bfd9729c1b207a  tx 0x570c3ba215c66071a8b5022c0997365bb2dd23bfe420d428d92761c8a8daa843
 2  169921-1 block 0xb133784fdabeb45d87876758c037968dab8546a8861ef08ea64cf5c8ec73d687  tx 0x24dc146315456dfa14072e86df72bf041344fd9c5f7f408baf455f2718fbf996
 3  169922-1 block 0xeb348b8e9ffc6dc28d351b8bf7f4a8d3bf8933fbfe004fb0909e91d738bb8b52  tx 0xb82458706e543a051ee0b51090df052fba28d52c94497959d9927af3fb51bc5d
 4  169923-1 block 0xbb856146bc8e4ff9efbe4a98f03eb34fab13539d42ee3c03bf03e63519d8bb9d  tx 0xe638b768f30432387b6691707b3c4c4ffdfc4e8ca7b5e635027d8e3d913d92a4
 5  169924-1 block 0x71c5d6740f3440157f4b412193d24e2f6156a9f1fff06a9ed2652239cd3ccbed  tx 0x36e7a73d522a15f17f2c582e1013b6124841a4124612141167ff19de0488d659
 6  169925-1 block 0x15bb692aaed874918cd048e82155490e326780b565cdf27dadfc183158df44d8  tx 0x60ee01d6bd5a7da766393bc3b529ddb77a7103197bdf11a147b507352b947472
 7  169926-1 block 0x19957ce710fd64082c8c454aad7479d40a0e98d9442e2fa657a2d1db4302f95a  tx 0x1e9dc3660f13efb29b28223cd2e88852a565dc48947b94464b9ea640065cf206
 8  169927-1 block 0xa4f52bc314c19f34bb0ee49dcf9f7a7cd1f9a56dc5402a060aedfcd3bf31b11f  tx 0x068aebe8fb136523fb6ab19f09e6073b7c5869982eaf08dd6bb7329cc573b5e7
 9  169957-1 block 0x10a90c345e560952ee6baa65993de08c5c4bc348e28916b8ad953cd7b25ed8ab  tx 0xe57be6e7ec3166ee92ab1ba20503d250e7e4f653722a4eb646ebc2edb1563a26
10  169958-1 block 0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3  tx 0xe0c32994b778fc51ddcc6d8d038177ef05bb81f879e6554ceff8d24ff174c952
11  169959-1 block 0x078f168764203e0c076de640e1ab233236b4fbf8ac5c1a0bd16a38b7e0d90e9f  tx 0x158e4d7b115230664149d6318f23bb1fe85f89ea87640e24a9f0b5c877775427
12  169960-1 block 0xe94805cffe1a16d9351b858dcb4f227d65da58f1054212e3e3c21da218096d9b  tx 0x625a2b66602be315de99809a64a73e6db88f1cbb698b935e80728ad4a1478e97
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after the deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ vault reserves() on resume (same local anvil vault): expected `100000000`, observed `100000000` at block `evm latest`
- ✅ asset 4401 team == role map (owner/issuer = M_mint, admin = M_admin, freezer = M_watch): expected `[]`, observed `[]` at block `0xa4f52bc314c19f34bb0ee49dcf9f7a7cd1f9a56dc5402a060aedfcd3bf31b11f`
- ✅ asset 4402 team == keyless accounts (S2 can never change): expected `[]`, observed `[]` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`
- ✅ supply S1 (asset 4401) before the gated mint: expected `0`, observed `0` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`
- ✅ supply S2 (asset 4402): expected `50000000`, observed `50000000` at block `0x9bcca0a7841dc7c33a66e443e163e2519e83789f47d0b3f7e6944de5564600c3`


### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 4501 — 2026-10-30T22:47:55Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-v3-asset4501.json`](../evidence/drill-outage-v3-asset4501.json) · watchdog log: [`evidence/drill-outage-v3-asset4501.watchdog.jsonl`](../evidence/drill-outage-v3-asset4501.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `15d40cd` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=4501|reason=providers-down|s=100000000|down=20s|p=down-1,down-2`

Timing (wall-clock on one machine; Portaldot V3 testnet + local anvil reserve (not Sepolia)):

- `trigger_head`: 258719
- `freeze_block`: 258720
- `freeze_block_timestamp_ms`: 1793400570000
- `submit_to_inclusion_s`: 5.64
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 26.42
- `down_for_s_in_remark`: 20s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x40918Ba7f132E0aCba2CE4de4c4baF9BD2D7D849`, token `0x8A93d247134d91e0de6f96547cB0204e5BE8e5D8`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1824 | `0x98e94ae1321d3b8e04ae15df249e8c9756d4cda09ac83427b96def0f7b47d724` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1825 | `0x71bc9611ce77ce454890f2ad4d7ff005bafcc189edc4cb2c9d76feedaceed6ad` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1826 | `0xa4996647b58f0393e389cf5e0fc62756552a19417d842ad143b9f70e42c36dae` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund the accounts below their working balance (A, W1, W2, judge, peer, M_watch) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (funder (Alice on a stand-in)) | `258706-1` | Ok | ✅ Ok |
| 2 | create asset 4501 | `Assets.create` (A) | `258707-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `258708-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 4502 | `Assets.create` (A) | `258709-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `258710-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 4501: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `258711-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 4501 to the judge | `Assets.mint` (A) | `258712-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 4502 to the peer | `Assets.mint` (A) | `258713-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 4501 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `258720-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `258721-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1  258706-1 block 0x0e43dff970c683280c3e63950402350cd5711cddb781152be7abaf89a9189780  tx 0xb9e27cf830ac38165c15e6e61b015fbd5d71e3f18034af7a568f1cd232389ac5
 2  258707-1 block 0x67c678637d4dea7eabc6b4a6cf46d8561006d92146b66ece396f2b8438781e0b  tx 0xd78a24326a66e00feb5a00049c7cb7c281c420def6709a3c986d8a6617ff8368
 3  258708-1 block 0xc9e8f8302c89bc4e1a994018633b0d6fd2fe57170c93c7936ded9ad7dc86486d  tx 0x56d7a745a50eef46206a4370c81c3999fe6bec0fc881bb025dbe52b23b34ffb6
 4  258709-1 block 0x9063938ba249d494d04cd4d311315765a509f63622dfecf158be251bac3d1b54  tx 0x5931607e13934af799087ff97e227a4228064237a621e4d1119c3bd181e1359c
 5  258710-1 block 0xc35b231803a12f1fd362022e1d7ba10cd990dfa93351f5844506d5dfa881283b  tx 0xe72b4212d7616c7071c8e86dbef433ff6955688241a75275b41413b9cc363cd1
 6  258711-1 block 0xb6e89d8349349d4fd06cd097a3077ae401c4e327db83a6959cacfe8e89a5cac3  tx 0x046f81185bfd7ba18d7612647e6ddaf935dda626e3699d2056b9bac43328067f
 7  258712-1 block 0x935de390b07150d0b44ba8cbea96372306069ef5361e0f0ff1453e285bdc8bf8  tx 0x6a7663349901517353d5e38af08afbea30c13bfb52be43c13a4d22e83562dedd
 8  258713-1 block 0xeb2e493d6a0f797ff04641873c1e98ceb7ce80437213cde823dfb39cef163951  tx 0x576ac822aff509221699da0fb54032bfb7173f8f38d29afde2dbe1974204da2e
 9  258720-1 block 0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c  tx 0xd21e2d8ad22305bd6f63b883e5cd5de473dd8dffb57ab8eeaa8df69474bb65a8
10  258721-1 block 0xcb0cd004500b5dc128f57ed3acf06adbb713ec44c7d3332755696732ab054a97  tx 0xa079bad02d1b9f40b045e83293b567174d46f513f081cafba59def9951263c81
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0xeb2e493d6a0f797ff04641873c1e98ceb7ce80437213cde823dfb39cef163951`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(4501).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x388e7b8238abc434264932518ae8d105ca5cd879f5c8024baea3dba28c37420d`, observed `0x388e7b8238abc434264932518ae8d105ca5cd879f5c8024baea3dba28c37420d` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ control asset 4502 untouched (Live): expected `Live`, observed `Live` at block `0x73189b2a2d4ba18f33cfc526af0a0780214bd821e3fa8a5ad3a860280a525d7c`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xcb0cd004500b5dc128f57ed3acf06adbb713ec44c7d3332755696732ab054a97`


### Breaker drill (heartbeat: no bot heartbeat for K blocks -> freeze (I8)) — asset 4503 — 2026-10-30T22:49:54Z

Chain: **Portaldot V3 testnet** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-heartbeat-v3-asset4503.json`](../evidence/drill-heartbeat-v3-asset4503.json) · watchdog log: [`evidence/drill-heartbeat-v3-asset4503.watchdog.jsonl`](../evidence/drill-heartbeat-v3-asset4503.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 9/9 state checks) · source: `15d40cd` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`, `--heartbeat-k 10`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=4503|reason=no-heartbeat|s=100000000|b=5FepBwxQ2eEeXht8594bJkVep9CTEBua3Abf4rgph7FMjjtg|n=0|since=258734|k=10`

Timing (wall-clock on one machine; Portaldot V3 testnet + local anvil reserve (not Sepolia)):

- `trigger_head`: 258744
- `freeze_block`: 258745
- `freeze_block_timestamp_ms`: 1793400720004
- `submit_to_inclusion_s`: 4.95
- `heartbeat_k (drill override; production K = 300 on this profile)`: 10
- `nonce_first_seen_block`: 258734
- `blocks_nonce_still_to_freeze_included`: 11

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x99dBE4AEa58E518C50a1c04aE9b48C9F6354612f`, token `0xd6e1afe5cA8D00A2EFC01B89997abE2De47fdfAf`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1827 | `0xdc102b390e9746061dfe5620168a911da3277295bca5147f8ff7e1c8efe454ee` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1828 | `0xe4c0347b26657f8ff41def740d52ca6113c747506da1cfa1cc7391837a9cfdaa` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1829 | `0x5b579ade4470bc111748bf88b4ed0f2c0e4ff5b4a0f91bac3147842fae4ee67f` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund the accounts below their working balance (A, W1, W2, judge, peer, M_watch) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (funder (Alice on a stand-in)) | `258725-1` | Ok | ✅ Ok |
| 2 | create asset 4503 | `Assets.create` (A) | `258726-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `258727-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 4504 | `Assets.create` (A) | `258728-1` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `258729-1` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 4503: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `258730-1` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 4503 to the judge | `Assets.mint` (A) | `258731-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 4504 to the peer | `Assets.mint` (A) | `258732-1` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 4503 via M_watch, reason on chain (reason=no-heartbeat) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `258745-1` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `258746-1` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1  258725-1 block 0xa4f7698fa9114133de78b1efec4149a21c8b19bd3236ce7b911785870e96c596  tx 0xbb8255872f98ec108af20dc3f800797b0c51021fb0374d484eab793e5ae9c277
 2  258726-1 block 0xc05b9a96827fda3291fb1fa3f17d97f72e9d10dd453c66303870e86619a8b803  tx 0x65331727feb169853f727bf9b689b13c02d8a56a6e893cd50a95c9919a3aea1a
 3  258727-1 block 0xa6f135545e47505a4935b59c0983bf3c1d3f7752b3cdf47754eda5da6260ff21  tx 0x31e1cfff29b741240b700aa093f7e3602a75083bd0e1f1e90c6ba1b590a14f50
 4  258728-1 block 0x6490f88c48a273d329f928cd9e2bfbb1b88a98215e8c06f481a71d68d8bb157c  tx 0x61d20055979d7bca119c38ced921d5cbda8a7b1cb7720de5c826762a8555c787
 5  258729-1 block 0x41d1cdb71463f2faee0150af94b0854a3208923a267ceb48b8615c703d81693b  tx 0xa261f31a598144e157e0b0f35a3f1d08a8ac963d5d27e709554376d3e17197a1
 6  258730-1 block 0x598985bd794b4f8f26c260dff8a2ca99ade3b2653fd857e6dbd81c1ab19d3c34  tx 0x8712809721d9e33f43fda8d7b7b773b6d4c3ee6b237399858ad0e36d5b3d34f4
 7  258731-1 block 0x04234e67ddeaebe6efb3d7583973842c63fd87109ce5cd39b0ce98d29f62dd12  tx 0x7734e77ffdfbbc632cfa1aca79e450f7636e8b13013467d18598eff1de2adb8f
 8  258732-1 block 0x97b7732ba768dfa846b5401c7d38e425cf26f888055089b34e3dfea410485fe3  tx 0x75a90709a50c7d032b49bfebd6edeeb0f1293ce0a219ba0f882f34460d68df79
 9  258745-1 block 0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d  tx 0x9e3d2d078aa7e270c9dd8fd31b91769fe7666b49a7d4f2d007380d7d9b56535d
10  258746-1 block 0x7a74bead3a76815fc03101511fd55fcd0285737060e2fc825d9b19b664b25e54  tx 0xeb76558759ae4019a88bffb48ad70baf1aafa8d5236efc2a1497492f8cbad18d
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x97b7732ba768dfa846b5401c7d38e425cf26f888055089b34e3dfea410485fe3`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(4503).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x9763564d95f5f31100b81512a28eccdc5c37f82afb32e4f7f0ab94bc19511473`, observed `0x9763564d95f5f31100b81512a28eccdc5c37f82afb32e4f7f0ab94bc19511473` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ control asset 4504 untouched (Live): expected `Live`, observed `Live` at block `0xd517a2e9f9d75bbd0aef5673e04cf7c83a1e931c02d71ffb7dcae699ec42346d`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x7a74bead3a76815fc03101511fd55fcd0285737060e2fc825d9b19b664b25e54`
- ✅ the triggering check saw the bot nonce unchanged for >= K blocks: expected `True`, observed `True` at block `watchdog log`
- ✅ reserves were level at the trigger (the freeze is the heartbeat rule alone): expected `[]`, observed `[]` at block `watchdog log`


## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain (before the Portaldot V3 testnet was reachable). Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). V3 runs, once funded, are listed in `docs/PROOF.md`.

Earlier V3 reachability probe (the old DNS names): [`evidence/v3-probe-2026-10-14-p5.txt`](../evidence/v3-probe-2026-10-14-p5.txt) (V3 reachability probe — 2026-10-14T14:59:52Z (P5)).
Current V3 identity (read-only day-0 check): [`evidence/v3-day0-20261020T152616Z.json`](../evidence/v3-day0-20261020T152616Z.json).

### Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw — 2026-10-14T15:02:11Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-drill-standin-upstream-20261014T150211Z.json`](../evidence/roles-drill-standin-upstream-20261014T150211Z.json) · result: **PASS** (22/22 steps as expected, 20/20 state checks) · source: `1f8e351` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

- other watcher: W1 saw asset 1 already frozen at #6902 and stood down
- drain -> freeze included (wall clock, one machine; local anvil + stand-in): 5.48 s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1006 | `0xae18933879519e8b137e166d09cb2058511c831ad8e4cc10afd07e8fa8c392cc` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1007 | `0x9ba4145e34f883cd763ce305c7f51f6be31bbb4cb1b9c754cf18247f333d37f5` | ✅ status 1 |
| 3 | custodian drains 30% (33.00) — release() | 1073 | `0xcb98e7e298af7f520c56441990a28eaa7e43691215cb146fae9da34bfeeed7e1` | ✅ status 1 |
| 4 | custodian re-deposits 33.00 | 1074 | `0x842c2450a059d3bb5812aa4b4d01f7131bc8b13ebe2d31e80267dafbbd631e8a` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | A proposes mint 1.00 to the judge through M_mint (first approval) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6894-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 2 | bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6895-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 3 | A proposes 0.01 more (reserves cover S1 + S2 exactly) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6896-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 4 | A cancels the refused proposal (deposit returned) | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6898-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 5 | watcher W2 freezes asset 1 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `6901-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 6 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6903-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 7 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `6904-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | A proposes a mint while frozen | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6905-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | A cancels it | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6907-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 10 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `6908-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 11 | bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `6910-2` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 12 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `6911-2` | Ok | ✅ Ok |
| 13 | A proposes set_team with the freezer moved to A (through M_mint) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6912-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | A cancels the refused team change | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6914-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 15 | A proposes set_team making A the sole admin (could thaw without the bot) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6915-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 16 | A cancels the refused admin swap | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6917-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 17 | A proposes set_team keeping issuer M_mint, admin M_admin, freezer M_watch | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6918-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | bot co-signs the safe team change | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `6920-2` | Ok + inner Ok + Assets.TeamChanged | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.TeamChanged |

Block and transaction hashes (full):

```
 1    6894-2 block 0x56824cf364f515bebfddfb0af7a2c5c2111ed4e664c40fe443b13c47a137697a  tx 0x893b2ff5cf15d431698688b5066430cb7aca5514acd12d424d316968b8b85001
 2    6895-2 block 0x83e6b95a19cd4a9d8dff976df821a2d19c3c47eaa5c380f80856fa7c3f2e15a6  tx 0xa44b3e7f322b9e4d46ba623e80f3d717feb35ea814f41369ceab32d3f847adac
 3    6896-2 block 0x275348a1cb414c173d942a34ae61ad98e922eab93226a541549ebe97d61a7b0f  tx 0xf2cef65e7a90444520fa0c4473dfd44e93696fd65320a809a6147bda79c6b778
 4    6898-2 block 0xb4392cabad007144430484c57d3bdd297fb8dd5afb0875118570b2bd9bad765b  tx 0xcd5f8c89b63aa64ac1b858e4f50501cd88a56220fdeffb3bc3db0276a2b33f33
 5    6901-2 block 0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9  tx 0xcfd0948f09e9954330c58760633e8bc13b77d710a624ec23aec4cf71a81d955f
 6    6903-2 block 0x2b3b1664a54f62a183e2af6b2c67b4af6cfa06f478d1f3bd8c6c97c6c632cdcd  tx 0x7d07763a2b486963d56891415cc56e507f9cc5a829bd4d3add1b52c3b8e59626
 7    6904-2 block 0xfcd7c0bec0d8d002e6e332ef3fbfb57b4e2407aaaa4bbda3f4dd706df56e47d8  tx 0x2a3ddbb73ee928cf604ae5ee0a6323ccdd0ac83f52f8bbee427aa19078abc17f
 8    6905-2 block 0x3c108663459cd1fe3612092f7a9a8962bb81ae686643528390bce4e565cad317  tx 0x9010707f9eb3314e61d499a12c4dbc3707f61c6a39cdecc6b43e89bdfef02972
 9    6907-2 block 0xc25f6f1d1e8b0cd51a8586871974b482ca9218a8841835db65ece52a35197088  tx 0xee409e8a32d0ff7649b8ec740561997b47bbab06983bbac041764e18778117f5
10    6908-2 block 0x7c6ad10e79531ed4425362b5b8ca681d21329e5ae20badbf018706c82bce84b3  tx 0xc3625afc94de1ba163047d446c3c6ae6d3e30f8cc028acdb15038de879ad56ae
11    6910-2 block 0x03a5c2ca30611e39160a35330cf6853df1900cd76e2602bf26338f1b155c14e2  tx 0x45bbe3540313e9a73c31856508fafffa08547ac6c0b62cb34cc32775dda629ea
12    6911-2 block 0x63abdadbe942fe97855957bc9d06315709709c9a3a369ff2d682100508cfeaf7  tx 0xa328006f4d07278d52f6d7957faa8f77a286a96b5e0f5266fb1625e58046acef
13    6912-2 block 0x9aead98bbde73b54e6c329fd6adf032ef56cf0f3e7966eae7670e5ad8ab7332c  tx 0xe2bd6f667028cc8cf6d8884beed38a8faa2171345e681d91fa0c63545456003c
14    6914-2 block 0x0391791a896c05eac8beca7289307e4b42d0454db387d7545045ed127ef6246b  tx 0x5c6ad14e437c910bec6d6e39b026d7c8eb793d752056156d5974783ea9cff897
15    6915-2 block 0x5c53f4ccf9df925ed77a30aaa4e851b083aaf2bcee5839a205c5791cea9e70e1  tx 0x64d96f0b7dadcdef9b4f9ea50fd6b8eba6cdf7f19049ce72dcfe423c6a38bd6d
16    6917-2 block 0x9a412d7f5e50fd1e314baedca20c7009419728cadfe7ff48cc214a7fdb2ff07f  tx 0x8e1c2b5aa5b5199ba66b706474cb5a2fd3336dd083c648bb74ca27c916e107f0
17    6918-2 block 0x51f0185f904497ecca69b39588e81996d5ca0a3c96bb107984a3516ddf2ef6b6  tx 0x21e6483895d1e32c4619de709ab90ec449972ff4e21ea917c71445f4b2179fa1
18    6920-2 block 0x9841403b1dbcce4e7ff5797545098e8e86a1668389a68e62e192fd5ffb63a7a1  tx 0x41a24279d446395f827846480ce1ebbff40b2edcad34bf26855275104214838f
```

State checks (storage/events read at the step's block):

- ✅ asset 1 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the drill: vault reserves == S1 + S2: expected `109000000`, observed `109000000` at block `head`
- ✅ S1 after the gated mint == S1 + 1.00: expected `60000000`, observed `60000000` at block `0x83e6b95a19cd4a9d8dff976df821a2d19c3c47eaa5c380f80856fa7c3f2e15a6`
- ✅ bot refuses the over-mint (exit 1, no signature): expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ over-mint still pending (no MultisigExecuted): approvals == [A]: expected `['A (operator)']`, observed `['A (operator)']` at block `0x65271d159370087e24439f0f3eeab5cc37bc4428ed555010740d0be4708d49ca`
- ✅ S1 unchanged by the refused over-mint: expected `60000000`, observed `60000000` at block `0x65271d159370087e24439f0f3eeab5cc37bc4428ed555010740d0be4708d49ca`
- ✅ no pending over-mint after the cancel: expected `None`, observed `None` at block `0xb4392cabad007144430484c57d3bdd297fb8dd5afb0875118570b2bd9bad765b`
- ✅ both watchers armed and level (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's reserve-chain block: expected `1073`, observed `1073` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 1 status after the freeze: expected `Frozen`, observed `Frozen` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ bot refuses any mint while frozen (I7): expected `I7`, observed `I7` at block `bot`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `evm latest`
- ✅ bot refuses the thaw: finality has not reached the drain block yet: expected `['refused', 1073]`, observed `['refused', 1073]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `6901-2`, observed `6901-2` at block `0x4bf063fbe2bb812675abe297b707572e5c3418974b4159816d5775e50c7ebba9`
- ✅ asset 1 status after the thaw: expected `Live`, observed `Live` at block `0x03a5c2ca30611e39160a35330cf6853df1900cd76e2602bf26338f1b155c14e2`
- ✅ asset 1 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ bot refuses a set_team that changes the freezer: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ bot refuses a set_team that moves the admin off M_admin: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ asset 1 team after the co-signed set_team (ARMED): expected `[]`, observed `[]` at block `head`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1 — 2026-10-14T14:53:40Z — PASS (22/22 steps as expected, 20/20 state checks) — source: `a4bdcfa` (clean) — [`evidence/roles-drill-standin-upstream-20261014T145340Z.json`](../evidence/roles-drill-standin-upstream-20261014T145340Z.json)
- asset 1 — 2026-10-14T14:44:19Z — PASS (22/22 steps as expected, 20/20 state checks) — source: `6c26862` (clean) — [`evidence/roles-drill-standin-upstream-20261014T144419Z.json`](../evidence/roles-drill-standin-upstream-20261014T144419Z.json)
- asset 1 — 2026-10-14T14:30:22Z — PASS (20/20 steps as expected, 19/19 state checks) — source: `8665dda` (UNCOMMITTED CHANGES) — [`evidence/roles-drill-standin-upstream-20261014T143022Z.json`](../evidence/roles-drill-standin-upstream-20261014T143022Z.json)
- asset 1 — 2026-10-14T12:47:59Z — PASS (16/16 steps as expected, 17/17 state checks) — source: `25c6f22` (clean) — [`evidence/roles-drill-standin-upstream-20261014T124759Z.json`](../evidence/roles-drill-standin-upstream-20261014T124759Z.json)

### Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control — 2026-10-14T15:03:38Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-attest-standin-upstream-20261014T150338Z.json`](../evidence/roles-attest-standin-upstream-20261014T150338Z.json) · result: **PASS** (15/15 steps as expected, 6/6 state checks) · source: `1f8e351` (clean)

`ballast verify` blocks #6921..#6960 ([`evidence/verify-standin-upstream-20261014T150338Z.json`](../evidence/verify-standin-upstream-20261014T150338Z.json)): **PASS** — 4/4 B attestations PASS on both chains, 1 REJECTED (not counted), 0 FAIL/FLAGGED.

Heartbeat H = 20 blocks (drill override; production H = 200, K = 600 on this profile).

- finality (anvil): mined 65 blocks: finalized = latest − 64

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 1140 | `0x32d2e53eb849de0086fccb17c2796fd95c1eb43a4c43f4f18304bf3c7e1430ce` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 1141 | `0xb7d32330bbaaaeb6dc985bbe10889f2beb32f18d946fb88097fed396301ce970` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | bot announces watchers (BALLAST/1|watchers|t=1|m=5C7iVxxiAvdPFuddh1UmsNiCLmz91wQMXhR…) | `System.remark_with_event(BALLAST/1|watchers)` (B (reserve bot)) | `6923-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 2 | bot announces evm-attester (BALLAST/1|evm-attester|h160=0x4dc969838572d068ead3ab83139904…) | `System.remark_with_event(BALLAST/1|evm-attester)` (B (reserve bot)) | `6924-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 3 | bot posts attest (pb 6921) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6925-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 4 | bot mirrors 6925-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6926-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 5 | bot posts attest (pb 6923) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6927-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 6 | A proposes mint 1.00 through M_mint | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6928-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 7 | bot mirrors 6927-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6928-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 8 | bot B co-signs (finalized reserves cover it) | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6930-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 9 | bot posts attest (pb 6931) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6934-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot mirrors 6934-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6935-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 11 | bot posts heartbeat (pb 6955) | `System.remark_with_event(BALLAST/1|heartbeat)` (B (reserve bot)) | `6958-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 12 | negative control: the judge key posts a copy of the bot's attestation | `System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key` (Judge (negative control)) | `6959-2` | Ok + System.Remarked (included — verify must REJECT it) | ✅ Ok · System.Remarked |
| 13 | bot mirrors 6958-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6959-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    6923-2 block 0xe4eef06ed4bfd26c75d9598bcaa5d803c910a27a0221f8cf96c8c20d6b3ae02a  tx 0xb12a93fd10546e6be1ebb32cfaab9afb49f19e1f283e6e494657495e753365d9
 2    6924-2 block 0xadfc91d37c4aa8edc205139edf95cf7ca6c1de5527746b3a0696fefa218af642  tx 0x798b0ea4c168917b4683052152053531de8d07aeaa9be8e59ca258c19cdb8fd2
 3    6925-2 block 0x5204f824c79d0a3d6a33196a9f558bbb9f851c3743e9f0d8c18bb83c97992039  tx 0xace91796b9b678309b70653547dd5abe03c1ac9d041de7a2bfbbe59b1e20cd1d
 4    6926-2 block 0x9a7e151685870fc30f4de67d171adde516062b5478b7897b3daf2295f84c3bef  tx 0x9dadb7ab722f73590648fcfc5629052524ae5d47d6b974714d15d41d78b0f582
 5    6927-2 block 0xeef72f26b7eb4197ea7b5d0b0048ba7b54be57b0265c907e2dd8b09d5d0f979d  tx 0xf6d888bd64ecb9067a25280b1c8ab7127555575668db3f3303767207886bac5b
 6    6928-2 block 0x3d9dce0e04d77adbaa512a5b0b9ee4d8e9d9e1e51456c3a23f580f911cdad050  tx 0xbf10363845c9815debd039a98a8e257096b92f6831bd8f7f6fa89aea14f6b64e
 7    6928-3 block 0x3d9dce0e04d77adbaa512a5b0b9ee4d8e9d9e1e51456c3a23f580f911cdad050  tx 0xb4918a1df79a51ef10ca519864061d73827cf66864b06d1b2f6ffddaf8663c80
 8    6930-2 block 0x6794c5322c57e2df3a802e00ae81cb0be6aa307bac30523da17647926a10ce4b  tx 0xacbfba1d033fc46f01c1f1678797dbe3acef5b80f226c7e31d66aaf6c6b2c2e6
 9    6934-2 block 0x10b87ce2871950433542dc1daac6aed458245381f879da33aa2ade99148ed49b  tx 0xee0244b229a54c9b9a17d6fa1eb30c14a0d4c0eda2883c4a709ca4fafb944b00
10    6935-2 block 0xd6fbe6e9a95e9b4bd1f0f602e235aa13b77964d211550a29ee4e01711661ae5a  tx 0x33c762f4ff7ab573ce08ddaab9906846c8459c13e56ebb52e2da74ad413f03e1
11    6958-2 block 0xcd110faf998506a594b6f333e075deffbf47f26a84d683e8313b3ccdf8d8b632  tx 0xb77d96eb59db0793be2a476f9fcd64f8eadae824df3b9c6fa401af90d41b5e5a
12    6959-2 block 0xe1438821093ea1a4cf6641cbf32efea70ae702beff55edccd309cd900643da9e  tx 0x6c4cb3fb3da670e7d33616b3d032c564cec573c4393a198c9cd3a58232b6ca3f
13    6959-3 block 0xe1438821093ea1a4cf6641cbf32efea70ae702beff55edccd309cd900643da9e  tx 0x0ec3bf8aa3bf90ec9b90c7d411a3ba0fa8f3be126bfc65eef8005074a045712e
```

State checks (storage/events read at the step's block):

- ✅ the post after H quiet blocks is a heartbeat: expected `heartbeat`, observed `heartbeat` at block `0xcd110faf998506a594b6f333e075deffbf47f26a84d683e8313b3ccdf8d8b632`
- ✅ verify exit 0 and verdict PASS: expected `[0, 'PASS']`, observed `[0, 'PASS']` at block `verify`
- ✅ every bot attestation/heartbeat PASSes on both chains: expected `4`, observed `4` at block `verify`
- ✅ every oracle post matches a PASSing remark (I10): expected `4`, observed `4` at block `verify`
- ✅ the forged remark is listed REJECTED (not counted): expected `['6959-2']`, observed `['6959-2']` at block `verify`
- ✅ watcher-set and evm-attester announcements PASS: expected `[1, 1]`, observed `[1, 1]` at block `verify`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1 — 2026-10-14T14:55:18Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `8dabe45` (clean) — [`evidence/roles-attest-standin-upstream-20261014T145518Z.json`](../evidence/roles-attest-standin-upstream-20261014T145518Z.json)
- asset 1 — 2026-10-14T14:46:04Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `e70d2b0` (clean) — [`evidence/roles-attest-standin-upstream-20261014T144603Z.json`](../evidence/roles-attest-standin-upstream-20261014T144603Z.json)
- asset 1 — 2026-10-14T14:34:22Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `7b6a2f8` (UNCOMMITTED CHANGES) — [`evidence/roles-attest-standin-upstream-20261014T143422Z.json`](../evidence/roles-attest-standin-upstream-20261014T143422Z.json)
- asset 1 — 2026-10-14T14:32:00Z — FAIL (11/11 steps as expected, 5/6 state checks) — source: `7b6a2f8` (UNCOMMITTED CHANGES) — [`evidence/roles-attest-standin-upstream-20261014T143200Z.json`](../evidence/roles-attest-standin-upstream-20261014T143200Z.json) — failed: every oracle post matches a PASSing remark (I10)
- asset 1 — 2026-10-14T12:58:10Z — PASS (15/15 steps as expected, 6/6 state checks) — source: `aa9c877` (clean) — [`evidence/roles-attest-standin-upstream-20261014T125810Z.json`](../evidence/roles-attest-standin-upstream-20261014T125810Z.json)

### Role split — asset 1 (breaker) + asset 2 (control), reserve vault, ReserveOracle — 2026-10-14T12:41:19Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-setup-standin-upstream.json`](../evidence/roles-setup-standin-upstream.json) · result: **PASS** (16/16 steps as expected, 5/5 state checks) · source: `ab1f8ec` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 63 | `0xe00ac22a2c1f1bf0a3e8ef4eb9a793a8cafb68602ce22692d74ecffa6ddf9d1e` | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 64 | `0x82dadc4280284e643a4839bf5da3a7dc02efc1e74b8e9699d34d995c0c76a563` | ✅ status 1 |
| 3 | custodian receives 100.00 test tokens | 65 | `0x785762434c611f99f46a0c78b6a649650bda7148169be5c487523ca50fd69277` | ✅ status 1 |
| 4 | deposit S1 + S2 = 100.00 — plain ERC-20 transfer into the vault | 66 | `0xf1da59fad3ca75e30a44f5b4a2d3cd4fdf39a094b3a8481ef3a716292e8b3220` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, A2, B, W1, W2, judge, peer, M_mint, M_admin, M_watch, asset-2 keyless owner (>= ED) | `Utility.batch_all[11 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `4076-2` | Ok | ✅ Ok |
| 2 | A creates asset 1 | `Assets.create` (A) | `4077-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `4078-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | A creates asset 2 | `Assets.create` (A) | `4079-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `4080-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | A mints S2 = 50.00 of control asset 2 to the peer (its only mint) | `Assets.mint` (A) | `4081-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 7 | asset 1 set_team(issuer=M_mint, admin=M_admin, freezer=M_watch) | `Assets.set_team` (A) | `4082-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 8 | asset 1 transfer_ownership(M_mint 2-of-2 {A, B}) | `Assets.transfer_ownership` (A) | `4083-2` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 9 | asset 2 set_team(keyless issuer, admin, freezer) | `Assets.set_team` (A) | `4084-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 10 | asset 2 transfer_ownership(keyless owner) | `Assets.transfer_ownership` (A) | `4085-2` | Ok + Assets.OwnerChanged | ✅ Ok · Assets.OwnerChanged |
| 11 | A alone tries to mint asset 1 (issuer is M_mint) | `Assets.mint` (A) | `4086-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 12 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code(ReserveOracle)` (B) | `4087-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |

Block and transaction hashes (full):

```
 1    4076-2 block 0x8df7c2a28d7ca19100c3c7d51c9c044a0c66471113aad6a7a1c51c2bd2953ec6  tx 0xaf93ba8ab28866b3dce2492c5842ad8b482637bf48e6cf60eb087636d69fd983
 2    4077-2 block 0x492d86548766cebaf57255fd36c03044ab3b6636c6c22280640f0624b1e7b58c  tx 0xcec83e4a3bce176388f694e68a6c373285f55800bd882e7ed3ba99271ef736ca
 3    4078-2 block 0xd9dbce30b43e2deaa95db5095d34ecde0777649273a57164472debad1ce0350d  tx 0x0602b692fa2c7443efa1d5217624814b4ef214f74e56cf30c7440d4bf2ee82f4
 4    4079-2 block 0x7f01336b9dedc370d5828ce63f0f20184eb7a14d951df4155bb07e6e52aafa3a  tx 0xb1b6ec65a4d241136ffda5023d4edcfcb6427df26a4996e5d597fbd2d592363c
 5    4080-2 block 0x13e9dad55fa76696a0ff6e2a99909ece5c5a9925c0a381c6a5c64124557cae03  tx 0xd77d491b7af413d632380168d03a4652af2ad5d954b81c3db06fc633fb6468c8
 6    4081-2 block 0x724e3c74b0b3488a3ae86157858ee810e61bbbbb15d09ecb0b878e21677f8e43  tx 0xa3cbed237fd533f72bf12f3fe05ece2b6220914ae3e0f5f883fe14f3ac68b3f9
 7    4082-2 block 0x4477ceef7b4b10e0abc2f65dac6f5b6fb081f982615ddf3687f222235ec1ddab  tx 0xf23dbf683afe144c11d2c2628c862c6310721c86ac88c8eec5e83dadd2d938a0
 8    4083-2 block 0xd59a7db0824e014cfd7a1d08403173ff9717cd7336b29c35c19885a239566b8a  tx 0xfe987c4935e7a86049f76d822d7be1264275c2dcf119c2fbaced978c587da14e
 9    4084-2 block 0xcc1903a5d556c56220844e855aa1800ae2ae1231f62d1a8bdcbdbfea9d20c935  tx 0xcd6ec237e6f521b2add36bad464a698eeab95dc1d15a6800cf66c180dd8a7dbc
10    4085-2 block 0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048  tx 0x46b9237746c4ed7c8905c59f67ae430be80750df0a71fd41ed01fdac05303453
11    4086-2 block 0x51cf9f432445e3ffca8673815799398dd86025ff2c63cfe0d6b917a13f80d518  tx 0xb519db098c3136a036dd5e2106a076a48c8373606737b17a9aea6aea1d0f8140
12    4087-2 block 0x4c72df62a469758668e9a1dc10496327771ec2342594f6cb034df9549914ea4f  tx 0x2186574442b0b2fe6c5376e9e842690cb92d776f4a5b91e035f3b1a6f7be9a05
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after the deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ asset 1 team == role map (owner/issuer = M_mint, admin = M_admin, freezer = M_watch): expected `[]`, observed `[]` at block `0xd59a7db0824e014cfd7a1d08403173ff9717cd7336b29c35c19885a239566b8a`
- ✅ asset 2 team == keyless accounts (S2 can never change): expected `[]`, observed `[]` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`
- ✅ supply S1 (asset 1) before the gated mint: expected `0`, observed `0` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`
- ✅ supply S2 (asset 2): expected `50000000`, observed `50000000` at block `0x3cd76a562645d4dc2cb81268408578693c68a1f336e19627493109989d09c048`


### Breaker drill (drain: reserve drained -> watchdog freezes) — asset 2039 — 2026-10-14T15:05:39Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-drain-standin-upstream-asset2039.json`](../evidence/drill-drain-standin-upstream-asset2039.json) · watchdog log: [`evidence/drill-drain-standin-upstream-asset2039.watchdog.jsonl`](../evidence/drill-drain-standin-upstream-asset2039.watchdog.jsonl) · result: **PASS** (14/14 steps as expected, 11/11 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2039|reason=deficit|s=100000000|r=70000000|p=anvil|eb=1210|eh=0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397` (`eb`/`eh` = the local-anvil block the watcher read, not Sepolia)

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 6972
- `freeze_block`: 6973
- `freeze_block_timestamp_ms`: 1791990372001
- `submit_to_inclusion_s`: 2.7
- `pd_head_before_drain`: 6970
- `blocks_head_before_drain_to_freeze`: 3
- `drain_to_deficit_seen_s`: 3.63
- `deficit_seen_to_submit_s`: 0.0
- `drain_to_freeze_included_s`: 6.33

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x18E317A7D70d8fBf8e6E893616b52390EbBdb629`, token `0x5067457698Fd6Fa1C6964e416b3f42713513B3dD`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1207 | `0x6b8b2b1f948fe2995ce7d93e7088108e2038e69880e0acf4c345134e08a65e72` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1208 | `0x1c69403fb5cd57bf95adc7ef4c422e121956d977c3424a364d0a7c6af605c11f` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1209 | `0xdec6a7764a1f267e1f056c4a7de10f4e0671380d96658bf1cf63f1ce7fde0fc9` | status 1 | ✅ status 1 |
| 4 | custodian drains 30% (30.00) — release() | 1210 | `0xa97df79a6b8f1226af098ed142aa8e72b0c4bd5c1e84de641b7432532bd5d20d` | status 1 + Released | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6963-2` | Ok | ✅ Ok |
| 2 | create asset 2039 | `Assets.create` (A) | `6964-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6965-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2040 | `Assets.create` (A) | `6966-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6967-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2039: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6968-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2039 to the judge | `Assets.mint` (A) | `6969-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2040 to the peer | `Assets.mint` (A) | `6970-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2039 via M_watch, reason on chain (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `6973-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6974-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6963-2 block 0xf671cd0d596acd6387eb6a1b823733c4a0d722ec1e42575c67de2bab2be023ae  tx 0xef920211f53b61c108a5c17e65627670d5e4b7b80a4c560022f321aebce8acc7
 2    6964-2 block 0xeea85253927342620554e67edfdc5ad9a693f1d9ea3de2718cc12f812c3f2f99  tx 0x456daa216694ae357c71540f1007b6aad3897b712d137ea4bfbbcf18a29c2adf
 3    6965-2 block 0x158b0f004c39511c3ee9c93aa4e29db266ac0b716236c8a0f017402ff006000b  tx 0x68163c43ad4d2cdc8fe802695bcbb39259203c700fb2ac050c5c6e6ff13be73b
 4    6966-2 block 0x4a55a4eeca6a41f25020ef409537c2fcfd9c50a6a3d242a50e274fb2125d99ac  tx 0x015708bbc9bbbb9b684785288a98b67012366988cafd06c7a6fdf3500cd5e351
 5    6967-2 block 0x5f07a88c4d034492ef6ea0999d56288d632b5a2e637fe5c98a0ccc947dd5e781  tx 0xedc137e35907340d2be868e9790605012d567c4dc95c5bbc370c880f020bb937
 6    6968-2 block 0x207ccf12e16d84985876ab43ba8c8b4dfbf81fb87959de8813c4debc25570c5d  tx 0x59d3e53756932654d8378b83bde3cd15cfc0b35afb3e6af5fa3993956c5c00a4
 7    6969-2 block 0x5abad424265615fac6e8f5ede537fbb1d65eeb033eed005daa63323978c093e7  tx 0x4a41dd2aae10cebc443f83dffdc5c9b847d775cddc0a51bbae82ae8ae214961b
 8    6970-2 block 0x9c40d5175aa1d623ce188263b64a951a830b62d063b3084c0f3ec3b1e9e24074  tx 0x4fd541ccb4de326ace24e154f7f283737d9e8b1c27d82987008729027313218e
 9    6973-2 block 0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e  tx 0x067b5f36de9b3a88022dac88c843f6e3b1f44351730f097c1254ad3f497d6603
10    6974-2 block 0x1287a37af758ad6ca43b4ffef09185e4ac705d0caaf164cfc9c65dfe8a0ed25c  tx 0x295b425d5540ebe99ad6d27aec6ab5e1f15ade0b63a45b4b84846dca099ce155
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x9c40d5175aa1d623ce188263b64a951a830b62d063b3084c0f3ec3b1e9e24074`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ vault reserves() after the drain < S1 + S2: expected `70000000`, observed `70000000` at block `0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397`
- ✅ the triggering check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ the triggering reading == post-drain reserves: expected `70000000`, observed `70000000` at block `watchdog log`
- ✅ the watcher read level before the drain: expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2039).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x9c83dc6cd0b9f8de460fa68a329b121ffcb7c866ee1246dbc45c68faf1158414`, observed `0x9c83dc6cd0b9f8de460fa68a329b121ffcb7c866ee1246dbc45c68faf1158414` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ control asset 2040 untouched (Live): expected `Live`, observed `Live` at block `0xc22425dbe47971690515ed2e528c54f798082453eaa8b547be9cb6ee3c39fe7e`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x1287a37af758ad6ca43b4ffef09185e4ac705d0caaf164cfc9c65dfe8a0ed25c`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2033 — 2026-10-14T12:31:41Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `dcf5f79` (clean) — [`evidence/drill-drain-standin-upstream-asset2033.json`](../evidence/drill-drain-standin-upstream-asset2033.json)
- asset 2029 — 2026-10-14T12:19:51Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `37acc11` (clean) — [`evidence/drill-drain-standin-upstream-asset2029.json`](../evidence/drill-drain-standin-upstream-asset2029.json)
- asset 2025 — 2026-10-14T12:04:38Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `36450df` (clean) — [`evidence/drill-drain-standin-upstream-asset2025.json`](../evidence/drill-drain-standin-upstream-asset2025.json)
- asset 2021 — 2026-10-14T12:02:37Z — PASS (14/14 steps as expected, 11/11 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-drain-standin-upstream-asset2021.json`](../evidence/drill-drain-standin-upstream-asset2021.json)
- asset 2017 — 2026-10-14T11:47:46Z — PASS (14/14 steps as expected, 11/11 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2017.json`](../evidence/drill-drain-standin-upstream-asset2017.json)
- asset 2013 — 2026-10-14T11:43:02Z — ERROR (11/12 steps as expected, 3/4 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2013.json`](../evidence/drill-drain-standin-upstream-asset2013.json) — RuntimeError: no freeze in the watchdog log (exit 4) — failed: mint S1 = 50.00 of asset 2013 to the judge -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level)
- asset 2009 — 2026-10-14T11:41:46Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2009.json`](../evidence/drill-drain-standin-upstream-asset2009.json) — KeyError: 'partial_fee'
- asset 2005 — 2026-10-14T11:31:12Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2005.json`](../evidence/drill-drain-standin-upstream-asset2005.json)
- asset 2001 — 2026-10-14T11:20:47Z — PASS (14/14 steps as expected, 8/8 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-drain-standin-upstream-asset2001.json`](../evidence/drill-drain-standin-upstream-asset2001.json)

### Breaker drill (outage: every provider down -> fail-closed freeze) — asset 2041 — 2026-10-14T15:06:21Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-outage-standin-upstream-asset2041.json`](../evidence/drill-outage-standin-upstream-asset2041.json) · watchdog log: [`evidence/drill-outage-standin-upstream-asset2041.watchdog.jsonl`](../evidence/drill-outage-standin-upstream-asset2041.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 8/8 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher reserve reads: none: the watcher's providers are unreachable by design (down-1=http://127.0.0.1:9, down-2=http://127.0.0.1:10); the vault was never read.

Watcher parameters: `--timeout 3`, `--fail-closed-after 15.0`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2041|reason=providers-down|s=100000000|down=16s|p=down-1,down-2`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 6990
- `freeze_block`: 6991
- `freeze_block_timestamp_ms`: 1791990426010
- `submit_to_inclusion_s`: 2.59
- `fail_closed_after_s (drill override; production default 300)`: 15.0
- `first_outage_seen_to_freeze_included_s`: 18.81
- `down_for_s_in_remark`: 16s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0xF8e31cb472bc70500f08Cd84917E5A1912Ec8397`, token `0xD5ac451B0c50B9476107823Af206eD814a2e2580`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1211 | `0x404e76974fbda64cfec4d4cbbf6479cb3302b33500f773b73f12a2b1432debc7` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1212 | `0x04d69a463a7fe8884277bc4051007d5aa533929eb5c78b4e642783f3e9d16c18` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1213 | `0xd044e42266cbf8be955d6ad4ace0cfaa718c81e952c3e3de9b44c77a3db7c8db` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6977-2` | Ok | ✅ Ok |
| 2 | create asset 2041 | `Assets.create` (A) | `6978-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6979-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2042 | `Assets.create` (A) | `6980-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6981-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2041: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6982-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2041 to the judge | `Assets.mint` (A) | `6983-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2042 to the peer | `Assets.mint` (A) | `6984-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2041 via M_watch, reason on chain (reason=providers-down) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `6991-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6992-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6977-2 block 0x013890781a0f77752096e8220cea0fdab97aa5bfc59924c357f8a4530b11a1b8  tx 0x30ba1f16d3489c2a0da5b3db56e2400a0c370658bda3b43b847472f536a600e5
 2    6978-2 block 0x029754eb754d7a86d9ef9d3c7d59a8d74e0541678c811098eff48af0303e0464  tx 0x93b7bd5cc9cedca81299aa899efe7d9b9b807fb3b512ae215d18b51a63c53cb9
 3    6979-2 block 0x8db1bed930864d643699517eb78348a31f0763960c55efe44caf7df356f2db91  tx 0x9e462769c0a8580600ee0d1e638a7d5b914560823f2faaa756b9e3a19e6c42e1
 4    6980-2 block 0x54572fbd9d1940305a78fe1f87cad1712c90b0c5fb06144af1bbfba283a0b691  tx 0x8fccd68cfb0692def750467070f50b84a0de917206bc13853e82f64ff10a3a3f
 5    6981-2 block 0x1b083be596d29be5eaee939a3c8bc75a5fff7ca959040ade3704bc11a738152d  tx 0xf633b3152e11b319e133b5dbe098c9bc60a643a07320a0896f4b86d2978f6b08
 6    6982-2 block 0x2fe6d0a8ab5cd55e1efbbebdb504184d9614b18461eae3f1f4a9869171f92db2  tx 0x8a2a679b35099be5c9e2569761188c6c0355352ed061cba23a743e28e8d9667f
 7    6983-2 block 0xeae7d6b9e97728221c1b0da31d84155811b951a4ebe6c54cce4a8d70e18670a5  tx 0x7e2a34bef19cb95306362e4b6050285786f13d48d4fd5efc19d705efe89271a0
 8    6984-2 block 0x7fef674570eb5870cb0b3a33865d53a15125c94a0d13e1b9146366df5e91454f  tx 0x4bb812bbd344c7d5868bcfea3b680ba81b6a8645da787549f804969de2d31971
 9    6991-2 block 0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b  tx 0x0c4b7df8778ea293d75410b1ba8b9fe6dd21e86e4dd7e7efba0a3b01ac30030d
10    6992-2 block 0xfe588a90a65462f0fc914ee906bd608069fe50ac82c6d74308c4447ff031a4ed  tx 0x2277c926c9bcba4e3260d0117e1c52104da5f889882c795494c8e68c502931a8
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x7fef674570eb5870cb0b3a33865d53a15125c94a0d13e1b9146366df5e91454f`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ every watcher reading failed (providers unreachable by design): expected `True`, observed `True` at block `watchdog log`
- ✅ Asset(2041).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xa80b5136f8694b2f68b11dbecb9c1c65f0cbb7e6231dce3e84d8656c5166e622`, observed `0xa80b5136f8694b2f68b11dbecb9c1c65f0cbb7e6231dce3e84d8656c5166e622` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ control asset 2042 untouched (Live): expected `Live`, observed `Live` at block `0x4a6f2aa6d8dd304ee24924f13f0222d20d88335a1db04577a8bdf9305609990b`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0xfe588a90a65462f0fc914ee906bd608069fe50ac82c6d74308c4447ff031a4ed`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2035 — 2026-10-14T12:32:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `dcf5f79` (clean) — [`evidence/drill-outage-standin-upstream-asset2035.json`](../evidence/drill-outage-standin-upstream-asset2035.json)
- asset 2031 — 2026-10-14T12:20:29Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `37acc11` (clean) — [`evidence/drill-outage-standin-upstream-asset2031.json`](../evidence/drill-outage-standin-upstream-asset2031.json)
- asset 2027 — 2026-10-14T12:05:17Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `36450df` (clean) — [`evidence/drill-outage-standin-upstream-asset2027.json`](../evidence/drill-outage-standin-upstream-asset2027.json)
- asset 2023 — 2026-10-14T12:03:14Z — PASS (13/13 steps as expected, 8/8 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/drill-outage-standin-upstream-asset2023.json`](../evidence/drill-outage-standin-upstream-asset2023.json)
- asset 2019 — 2026-10-14T11:48:23Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2019.json`](../evidence/drill-outage-standin-upstream-asset2019.json)
- asset 2015 — 2026-10-14T11:46:32Z — FAIL (11/13 steps as expected, 5/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2015.json`](../evidence/drill-outage-standin-upstream-asset2015.json) — failed: mint S1 = 50.00 of asset 2015 to the judge -> Err(Token.CannotCreate); mint S2 = 50.00 of control asset 2016 to the peer -> Err(Token.CannotCreate); supply S1 + S2 == vault reserves (level); judge balance unchanged after the refused transfer
- asset 2011 — 2026-10-14T11:42:14Z — ERROR (11/11 steps as expected, 2/2 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2011.json`](../evidence/drill-outage-standin-upstream-asset2011.json) — KeyError: 'partial_fee'
- asset 2007 — 2026-10-14T11:31:50Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2007.json`](../evidence/drill-outage-standin-upstream-asset2007.json)
- asset 2003 — 2026-10-14T11:21:35Z — PASS (13/13 steps as expected, 7/7 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/drill-outage-standin-upstream-asset2003.json`](../evidence/drill-outage-standin-upstream-asset2003.json)

### Breaker drill (heartbeat: no bot heartbeat for K blocks -> freeze (I8)) — asset 2043 — 2026-10-14T15:07:11Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-heartbeat-standin-upstream-asset2043.json`](../evidence/drill-heartbeat-standin-upstream-asset2043.json) · watchdog log: [`evidence/drill-heartbeat-standin-upstream-asset2043.watchdog.jsonl`](../evidence/drill-heartbeat-standin-upstream-asset2043.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 9/9 state checks) · source: `1f8e351` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`, `--heartbeat-k 10`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2043|reason=no-heartbeat|s=100000000|b=5EEzv6QYKv8bzUtnTWgE7Whi769FLXn2CdfbPZg8YU9s3dpb|n=0|since=7001|k=10`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 7011
- `freeze_block`: 7012
- `freeze_block_timestamp_ms`: 1791990489006
- `submit_to_inclusion_s`: 2.5
- `heartbeat_k (drill override; production K = 600 on this profile)`: 10
- `nonce_first_seen_block`: 7001
- `blocks_nonce_still_to_freeze_included`: 11

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x34B40BA116d5Dec75548a9e9A8f15411461E8c70`, token `0xc96304e3c037f81dA488ed9dEa1D8F2a48278a75`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 1214 | `0x68cd440d56f742303c177859e44ef5d7ad888085b9c66d7f6658746ebf40ab48` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 1215 | `0x9d7bacad67cb0bc8e4cbf6f2fbbc33e42aba4062c2a7d19c4eb662353faa8384` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 1216 | `0xf19934e3e1af93a0d684ce78c3266e18a1932ab9674507909023ea341b286c16` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `6994-2` | Ok | ✅ Ok |
| 2 | create asset 2043 | `Assets.create` (A) | `6995-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `6996-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2044 | `Assets.create` (A) | `6997-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `6998-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2043: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `6999-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2043 to the judge | `Assets.mint` (A) | `7000-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2044 to the peer | `Assets.mint` (A) | `7001-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2043 via M_watch, reason on chain (reason=no-heartbeat) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `7012-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `7013-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    6994-2 block 0x09bf2ec4b29d5b3da30d6f2e3025f5be258afcd92d535dcd173c92d0ff109104  tx 0x7f21fb5611faaf442452fc428b64e3acb71d1ca544537d12cc6cc3e0dccaadd3
 2    6995-2 block 0x70a06249342c375cf3ca0efe6643904b0de6f03b932b03c4a15b2a622e58ee98  tx 0x60fc48a73bc69c23ea91ccd19ff8fd0a3af7b7cdc9fee2637273304ccee45fb3
 3    6996-2 block 0xab504c41fce574efd19655c33cd2684bf2ef75b29bbf3653f07d3124b38c06f3  tx 0x57f019b203f4867e051929d7768b10cc910f1d62c5436dbba8c7dcd6993a3a47
 4    6997-2 block 0xef6bac4f8c68ed68b0c1c934fcc8240a04d00b370650c75ef6a725104cf24436  tx 0x5913358fbabf6c4add95419eb2ec5ae1eede91f6555c491ce04dbce71e72ca2d
 5    6998-2 block 0x9115c585822743afa5ddeb58c291a175a5e6c15b64a9e2498f9e93d75c1682d4  tx 0xcefa7932478b67c99a91fc35d3535c6ab35d065a8ae5f49b7993beb6186dfaeb
 6    6999-2 block 0x084f83c3b51fa74b9f79cd8e2104f23a6a3551120d7867e4aa81a913c3761765  tx 0xc2591e9b451b7172c04b797b98adfca10e9af83fa630f4599090648f442b2cdf
 7    7000-2 block 0x20828be3697981dc6b3e96057cc9b1cecddd08f4b240c4a2cbcf2fcfd82ea707  tx 0x34d5e23ce613fb673e493edc1ddf09e7112d24aa651c20cbab36957d85cbb948
 8    7001-2 block 0x65ee024d066104247ffdfec76f6b03707a4f63ccf0a4187f748eff0466a74246  tx 0xa3c2eb356e339600d1e3eea0db57bc77f482e630e507f03a486f8f1c78976634
 9    7012-2 block 0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a  tx 0x5d19cd99fe5dcdc6e27b61e34028af223efe28e0ecca214af306e634dd57236b
10    7013-2 block 0x0ea28a62c9895ab8ec98122569fb7cbba70f26cd822e5a68b49e6077209cdc91  tx 0x2b339fabd2605a6ff5202d3fa62f3223d4e8cb8a6ddca986599d6ac2d6fe9ba3
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x65ee024d066104247ffdfec76f6b03707a4f63ccf0a4187f748eff0466a74246`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2043).status after the freeze: expected `Frozen`, observed `Frozen` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0x7534ac43a69adb345e7e0e30862cf7ae40c1c52a0aca7f9aba742b2938cc742a`, observed `0x7534ac43a69adb345e7e0e30862cf7ae40c1c52a0aca7f9aba742b2938cc742a` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ control asset 2044 untouched (Live): expected `Live`, observed `Live` at block `0x50269117c89f057abf06f85a06fc3fc9d555e760bee91bd2e8f9c43f5be53c2a`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x0ea28a62c9895ab8ec98122569fb7cbba70f26cd822e5a68b49e6077209cdc91`
- ✅ the triggering check saw the bot nonce unchanged for >= K blocks: expected `True`, observed `True` at block `watchdog log`
- ✅ reserves were level at the trigger (the freeze is the heartbeat rule alone): expected `[]`, observed `[]` at block `watchdog log`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 2037 — 2026-10-14T12:53:39Z — PASS (13/13 steps as expected, 9/9 state checks) — source: `fd9e593` (clean) — [`evidence/drill-heartbeat-standin-upstream-asset2037.json`](../evidence/drill-heartbeat-standin-upstream-asset2037.json)

### ReserveOracle on Revive — 2026-10-14T15:08:59Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** (Revive accepts EVM bytecode on this stand-in; V3 deploy pending) · contract `0x4f445370d66c1322025f40f0cec0fd4e814cc840` · attester `0x4dc969838572d068ead3ab831399049dd2269b13` · raw JSON: [`evidence/oracle-revive-standin-upstream-20261014T150859Z.json`](../evidence/oracle-revive-standin-upstream-20261014T150859Z.json) · result: **PASS** (5/5 steps as expected, 6/6 state checks) · source: `1f8e351` (clean) · initcode sha256 `1ed85b9a1cd1dc07ec2759e5031088f40c89fd4c75f37ff4e27fec54a2b62cc9`

Posted values mirror drill `drill-drain-standin-upstream-asset2039.json` (reserve: local-anvil (not Sepolia)); posted values copied from that drill's evidence; posted by this script, not by a bot.

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund B and the stranger (deposits + fees) | `Utility.batch_all[2 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `7029-2` | Ok | ✅ Ok |
| 2 | B deploys ReserveOracle(attester = 0x4dc969838572d068ead3ab831399049dd2269b13) | `Revive.instantiate_with_code` (B (reserve bot, attester)) | `7030-2` | Ok + Revive.Instantiated | ✅ Ok · Revive.Instantiated |
| 3 | B (reserve bot, attester) posts level state (pdBlock 6970) | `Revive.call` (B (reserve bot, attester)) | `7031-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 4 | stranger's post is refused (onlyAttester) | `Revive.call` (Judge (stranger)) | `7032-2` | Err(Revive.ContractReverted) | ✅ Err(Revive.ContractReverted) |
| 5 | B (reserve bot, attester) posts FROZEN/drained state (pdBlock 6973) | `Revive.call` (B (reserve bot, attester)) | `7033-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    7029-2 block 0x1401e3e8a062d0c173becc28018fbb6d6b4b6b3bbeb0adf5d395510f103b8880  tx 0x42553139df1a888d86da5664e62f8c359187fc643e42c302abed967329376964
 2    7030-2 block 0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39  tx 0x62bac6f9551165082b55ab434888de0ee11d9eda11fccb9d00d010b51a202ffc
 3    7031-2 block 0x27932316c032ce50050be214019d67ca30fc301579ccf42ace843d153652739f  tx 0x788b7ad9e0c9b99557d8061c0a37e1cefb6bc7d4722266a90d6fe2c5842737a8
 4    7032-2 block 0x1a21d0d9fea4232cd2b6e8e2f2f16e899449e601fea46f8a070ce4cbccce87e4  tx 0xaad168a99f10338251970c6bcf4525171d49ca8e58d2130fa56352cbd5cf0804
 5    7033-2 block 0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23  tx 0x9a91e6af8fb3b8dba3f241f45d2cb09a523c508894926f4ff258c67f40dd5625
```

State checks (storage/events read at the step's block):

- ✅ attester() == B's H160: expected `0x4dc969838572d068ead3ab831399049dd2269b13`, observed `0x4dc969838572d068ead3ab831399049dd2269b13` at block `0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39`
- ✅ isBacked(3600) before any post: expected `False`, observed `False` at block `0x105df1f1969c62393ce5177d2a386f882c6f994ff3b8c7b437af3a8e00a6ec39`
- ✅ isBacked(3600) after the level post: expected `True`, observed `True` at block `0x27932316c032ce50050be214019d67ca30fc301579ccf42ace843d153652739f`
- ✅ isBacked(3600) unchanged by the refused post: expected `True`, observed `True` at block `0x1a21d0d9fea4232cd2b6e8e2f2f16e899449e601fea46f8a070ce4cbccce87e4`
- ✅ isBacked(3600) after the frozen/drained post: expected `False`, observed `False` at block `0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23`
- ✅ status() = (S1, S2, reserves, sepBlock, sepHash, pdBlock, frozen) of the drained drill state (sepBlock/sepHash = local-anvil block, not Sepolia): expected `[50000000, 50000000, 70000000, 1210, '0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397', 6973, True]`, observed `[50000000, 50000000, 70000000, 1210, '0x1f764c209b2ba55340fa96fc843657be412c19c2828cb29227139ae3d1153397', 6973, True]` at block `0x2d53d1f5baf09dc0ee7f8dab68c347febbb57c29a77862514366a4727c12eb23`

Other runs, newest first, any verdict (full tables in the JSON):

- contract `0x51312c0ddcc67c279dc183a19d60e6d66a76b189` — 2026-10-14T12:33:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `dcf5f79` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T123308Z.json`](../evidence/oracle-revive-standin-upstream-20261014T123308Z.json)
- contract `0x7199a20b12ad30c6292715f5cfec363a2b8691a2` — 2026-10-14T12:21:20Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `37acc11` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T122120Z.json`](../evidence/oracle-revive-standin-upstream-20261014T122120Z.json)
- contract `0xa3273ebfccb127932935888c37028434bc50ec3c` — 2026-10-14T12:06:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `36450df` (clean) — [`evidence/oracle-revive-standin-upstream-20261014T120608Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120608Z.json)
- contract `0x4d172b86f422339b99da9b0d291767a668d19c4f` — 2026-10-14T12:04:08Z — PASS (5/5 steps as expected, 6/6 state checks) — source: `d20a276` (UNCOMMITTED CHANGES) — [`evidence/oracle-revive-standin-upstream-20261014T120408Z.json`](../evidence/oracle-revive-standin-upstream-20261014T120408Z.json)
- contract `0x97f0eea7d362977202c05f85cd9b8307623981ae` — 2026-10-14T11:29:35Z — PASS (7/7 steps as expected, 6/6 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/oracle-revive-standin-upstream-20261014T112935Z.json`](../evidence/oracle-revive-standin-upstream-20261014T112935Z.json)

### Spike run — asset 1010 — 2026-10-14T15:09:36Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · genesis `0x0c4402ef4ccc34d28b16523e1cf26831716527c61a65d8e0840ab26e1636c8a2` · spec `node/268` · raw JSON: [`evidence/spike-assets-standin-upstream-asset1010.json`](../evidence/spike-assets-standin-upstream-asset1010.json) · result: **PASS** (11/11 steps as expected + 1 observation, 10/10 state checks) · source: not pinned (recorded before pinning existed)

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `7042-2` | Ok | ✅ Ok |
| 2 | create the asset | `Assets.create` (A) | `7043-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test | `Assets.set_metadata` (A) | `7044-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | set_team(issuer=A, admin=A, freezer=M_watch) | `Assets.set_team` (A) | `7045-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 5 | mint 50.00 to the holder | `Assets.mint` (A) | `7046-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 6 | W2 freezes via M_watch (1-of-2) | `Multisig.as_multi_threshold_1(Assets.freeze_asset)` (W2) | `7047-2` | Ok + Assets.AssetFrozen | ✅ Ok · inner Ok · Assets.AssetFrozen |
| 7 | watcher thaw_asset via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1) | `7048-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | watcher thaw(holder) via M_watch is refused | `Multisig.as_multi_threshold_1(Assets.thaw)` (W1) | `7049-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 9 | observation: issuer mints 0.01 while frozen | `Assets.mint` (A) | `7050-2` | observation only (not counted) | — Err(Assets.AssetNotLive) |
| 10 | holder transfer 1.00 while frozen fails | `Assets.transfer` (Judge) | `7051-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 11 | control: admin A thaws | `Assets.thaw_asset` (A) | `7052-2` | Ok + Assets.AssetThawed | ✅ Ok · Assets.AssetThawed |
| 12 | control: the same transfer succeeds | `Assets.transfer` (Judge) | `7053-2` | Ok + Assets.Transferred | ✅ Ok · Assets.Transferred |

Block and transaction hashes (full):

```
 1    7042-2 block 0xc252aabb427361e10679adde5e987fe8ef43dd0c9b2fcdc06db870aae032d4a7  tx 0x6170351fb900ccee32365cc0308c2e8b83a619470b2291fe1a123019a23ec9a5
 2    7043-2 block 0xd7c8c01f582fba8c2fae62eee62facac6931043f0ba5824def5f2444c0c19ae0  tx 0x9c9b4ff97e85402f71d772553c3f3518b10ae600c289fca320099676930e0251
 3    7044-2 block 0x663f16f1bbf704f14908ad6d9d74862df422dd06272711b447f09cb4b48e696a  tx 0xc0b6e55fbb87004d7c2b588e9e48f05dae14d1ad34d4fe4c57391aa1bca150d0
 4    7045-2 block 0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4  tx 0x5ae05d11689d8c6d513f8823a070b2c5788d0066a6d6d27682fdb9b37414ef63
 5    7046-2 block 0x43ccfec52c480d7ba01055c7ff7ea17c6feef954119274b04c880d4d7f21831b  tx 0x98f31cfa8305869fd3fd67214271b9bed147a781ec5461530b3ea0cc6797a30a
 6    7047-2 block 0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18  tx 0xc52966c2433fa9ac9038c4a1a7b2128c26aefe9dd4ff4018eea0ea05be0567dd
 7    7048-2 block 0x395b259c03b0944959a64e8b5e025f7f5c3eddac027812b40934a48ad3f32a9d  tx 0xf049a77b43b1a8339651a4c50276d6b0f35761a8c075c2fb3059480a72228875
 8    7049-2 block 0x41a7339e0ebb8d37c33f9cd19b6e361d64e33364298ec5b2fd90dc71355216d4  tx 0x241024e192de37d69e458518b27f62be6c717a5be24ebdd2b288fd404e225efe
 9    7050-2 block 0xf587caacf90c2903eaba69d4aacf987c443642cba4fc448f7d506db0b95154b8  tx 0xf5a2675fc59b744ee1238c0c26993fdc627d9bf028c84b4c687bd18121cceb06
10    7051-2 block 0xf633b886c782ff7da2331a820fbe3d9aa4437e6de11a2910a44801f86367b7f5  tx 0xae8432041892d2b0c23b683471684aba0952242b76f882c93fbd2487e76397f7
11    7052-2 block 0xe44832234f95d156964c4b98362d2cd44f828ef04c1f4017fea37e6de033087c  tx 0xe85c0c9926ed98bc3b60f2dc4d23157ef1b1ff0896ee1f9a1ea070ef49ee5dd8
12    7053-2 block 0xd8c4f705abfaf3c2bb63e8f8237b66f59ac6f75700452c8dacc0ab05f4d24ae9  tx 0xa4bb9c07f80f75f6cdb3800eb612d4c3594e793a7e4f18fbc91cb019a51feb7e
```

State checks (storage/events read at the step's block):

- ✅ M_watch native balance >= ED: expected `True`, observed `True` at block `0xc252aabb427361e10679adde5e987fe8ef43dd0c9b2fcdc06db870aae032d4a7`
- ✅ Asset(1010) freezer is M_watch: expected `True`, observed `True` at block `0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4`
- ✅ Asset(1010) issuer and admin are A: expected `True`, observed `True` at block `0xbad02fdf105de07e00f138d32170ebe2a15716621dee9252c89da1c3759cf7d4`
- ✅ holder balance after mint: expected `50000000`, observed `50000000` at block `0x43ccfec52c480d7ba01055c7ff7ea17c6feef954119274b04c880d4d7f21831b`
- ✅ Asset(1010).status after freeze: expected `Frozen`, observed `Frozen` at block `0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18`
- ✅ MultisigExecuted.multisig is the locally derived M_watch: expected `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D`, observed `5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D` at block `0x4867c025721291bc7229fa41c531a1bd02eec90410d222dc0c91e94a8e0eda18`
- ✅ Asset(1010).status after the refused thaw: expected `Frozen`, observed `Frozen` at block `0x395b259c03b0944959a64e8b5e025f7f5c3eddac027812b40934a48ad3f32a9d`
- ✅ peer balance after the frozen transfer: expected `0`, observed `0` at block `0xf633b886c782ff7da2331a820fbe3d9aa4437e6de11a2910a44801f86367b7f5`
- ✅ Asset(1010).status after admin thaw: expected `Live`, observed `Live` at block `0xe44832234f95d156964c4b98362d2cd44f828ef04c1f4017fea37e6de033087c`
- ✅ peer balance after the level transfer: expected `1000000`, observed `1000000` at block `0xd8c4f705abfaf3c2bb63e8f8237b66f59ac6f75700452c8dacc0ab05f4d24ae9`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1009 — 2026-10-14T15:08:21Z — FAIL (9/11 steps as expected + 1 observation, 8/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1009.json`](../evidence/spike-assets-standin-upstream-asset1009.json) — failed: mint 50.00 to the holder -> Err(Token.CannotCreate); control: the same transfer succeeds -> Err(Assets.NoAccount); holder balance after mint; peer balance after the level transfer
- asset 1008 — 2026-10-14T10:01:43Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1008.json`](../evidence/spike-assets-standin-upstream-asset1008.json)
- asset 1007 — 2026-10-14T09:58:42Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1007.json`](../evidence/spike-assets-standin-upstream-asset1007.json)
- asset 1006 — 2026-10-14T09:52:49Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1006.json`](../evidence/spike-assets-standin-upstream-asset1006.json)
- asset 1005 — 2026-10-14T09:46:51Z — PASS (11/11 steps as expected + 1 observation, 10/10 state checks) — source: not pinned (recorded before pinning existed) — [`evidence/spike-assets-standin-upstream-asset1005.json`](../evidence/spike-assets-standin-upstream-asset1005.json)
