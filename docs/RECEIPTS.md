# Receipts

Every extrinsic row below is a real extrinsic, identified by extrinsic id (`block-index`); decoded events are
in the linked JSON. `python scripts/check_receipts.py` re-fetches every extrinsic from the chain it ran on and
every drill reserve-chain tx from the local anvil. An index comes first, then the read-only Sepolia section.

## At a glance

Three places, each labelled on every row: the Portaldot **stand-in** chain (not V3), the **local-anvil**
reserve chain (not Sepolia), and **Sepolia** (read-only so far — see its section).

| Run | Portaldot chain | Reserve chain | Newest clean result | Evidence |
|---|---|---|---|---|
| Breaker drill on the role-split asset 1 (gated mint, over-mint refused, freeze, gated thaw) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (22/22 steps as expected, 20/20 state checks) | [`roles-drill-standin-upstream-20261014T144419Z.json`](../evidence/roles-drill-standin-upstream-20261014T144419Z.json) |
| Attestations + ReserveOracle mirror + `ballast verify` (negative control REJECTED) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (15/15 steps as expected, 6/6 state checks) | [`roles-attest-standin-upstream-20261014T144603Z.json`](../evidence/roles-attest-standin-upstream-20261014T144603Z.json) |
| Role split: asset 1 owner/issuer M_mint, admin M_admin, freezer M_watch; asset 2 keyless | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (16/16 steps as expected, 5/5 state checks) | [`roles-setup-standin-upstream.json`](../evidence/roles-setup-standin-upstream.json) |
| Breaker drill, scratch asset: drain -> freeze | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (14/14 steps as expected, 11/11 state checks) | [`drill-drain-standin-upstream-asset2033.json`](../evidence/drill-drain-standin-upstream-asset2033.json) |
| Breaker drill, scratch asset: every provider down -> fail-closed freeze (I6) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 8/8 state checks) | [`drill-outage-standin-upstream-asset2035.json`](../evidence/drill-outage-standin-upstream-asset2035.json) |
| Breaker drill, scratch asset: bot silent for K blocks -> freeze (I8) | standin-upstream (stand-in, NOT V3) | local-anvil (not Sepolia) | PASS (13/13 steps as expected, 9/9 state checks) | [`drill-heartbeat-standin-upstream-asset2037.json`](../evidence/drill-heartbeat-standin-upstream-asset2037.json) |
| ReserveOracle on Revive, mirroring a drill | standin-upstream (stand-in, NOT V3) | — | PASS (5/5 steps as expected, 6/6 state checks) | [`oracle-revive-standin-upstream-20261014T123308Z.json`](../evidence/oracle-revive-standin-upstream-20261014T123308Z.json) |
| Assets spike: watcher-set freeze, freezer thaw refused | standin-upstream (stand-in, NOT V3) | — | PASS (11/11 steps as expected + 1 observation, 10/10 state checks) | [`spike-assets-standin-upstream-asset1008.json`](../evidence/spike-assets-standin-upstream-asset1008.json) |

## Sepolia (read-only — no Ballast contract is deployed on Sepolia yet)

The Sepolia `ReserveVault` deploy, its 100.00 USDC deposit and the real-Sepolia drill wait until the deployer wallet holds >= 100.00 Circle test USDC; the reads below show what it holds. Every drill above uses the local-anvil reserve instead, labelled as such.

- [`evidence/sepolia-crosscheck-2026-10-14-p4.json`](../evidence/sepolia-crosscheck-2026-10-14-p4.json) — read at 2026-10-14T13:01:33.877Z: finalized block #11913325 via 2 providers — AGREE (publicnode: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000, drpc: `0xa6dafd5bfb80b165a8d73274721d88e81b0e363af3cc2591d7a81139f7aa000d` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault. P4 row 3 gate (2026-10-14): the ReserveVault deploy + 100.00 USDC deposit need >= 100000000 (100.00 USDC, 6 decimals) in this wallet; the balance read here is lower, so no Sepolia vault was deployed (waiting on the Circle faucet)
- [`evidence/sepolia-crosscheck-2026-10-14.json`](../evidence/sepolia-crosscheck-2026-10-14.json) — read at 2026-10-14T11:41:44.199Z: finalized block #11912942 via 2 providers — AGREE (publicnode: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000, drpc: `0x3737ad092fc1a966eed28a5af84b1cf9e3e46ebabe2a36044ee050f209f39e7b` reserves 20000000). Note: holder = Ballast's Sepolia testnet deployer wallet, NOT a vault: no ReserveVault is deployed on Sepolia yet; this file shows the two-provider reader agreeing on one finalized block

## Stand-in receipts — standin-upstream (not V3)

Measured on a **local** stand-in chain while the Portaldot V3 testnet is unreachable. Nothing in this
section is a V3 measurement. The chain is a local `--dev` node: `scripts/check_receipts.py` re-fetches
these rows from that node only, there is no public explorer for it, and a fresh node + spike run
produces new hashes (same steps, same outcomes). Re-running them on V3 is planned for when V3 is reachable.

Latest V3 reachability probe: [`evidence/v3-probe-2026-10-14-p3.txt`](../evidence/v3-probe-2026-10-14-p3.txt) (V3 reachability probe — 2026-10-14T11:41:33Z).

### Role-split drill — gated mint, over-mint refused, drain -> freeze, gated thaw — 2026-10-14T14:44:19Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-drill-standin-upstream-20261014T144419Z.json`](../evidence/roles-drill-standin-upstream-20261014T144419Z.json) · result: **PASS** (22/22 steps as expected, 20/20 state checks) · source: `6c26862` (clean)

Role map: `M_mint` 5Db6UvShSCpfZVnEbY45a5pD8mrxJq9sDs5BJoMwP6MNyXjb (2-of-2 A, B) · `M_admin` 5F9C9ndpaBsuzoRS6kU7o7wYupydLTRoxBTGiWySyuuivFDM (2-of-3 A, A2, B) · `M_watch` 5CirPpif8EYwQgCQHjAiYzTFnsQoPtkVow9SkmWfHzbmwh4D (1-of-2 watchers).

- other watcher: W1 saw asset 1 already frozen at #6547 and stood down
- drain -> freeze included (wall clock, one machine; local anvil + stand-in): 7.92 s

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 604 | `0x76361cf142cd349c1859cec5b9beb7e0deed8de58a7f51e2fa6ffb2a841ecd60` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 605 | `0x870cde1be4f5d278acdf098bf729b9b76f3a2b3c738c7e6bc8af9b69bc3f002b` | ✅ status 1 |
| 3 | custodian drains 30% (31.80) — release() | 671 | `0xa998e067126c049e3d1359d8b506529afc7aa871260848081819d1810722a2ef` | ✅ status 1 |
| 4 | custodian re-deposits 31.80 | 672 | `0x27039fcc78b9c99de746d0596fe26f12c19e992eb2488f9013b24033fae41e8b` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | A proposes mint 1.00 to the judge through M_mint (first approval) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6537-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 2 | bot B co-signs: finalized reserves cover S1 + S2 + 1.00 -> mint executes | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6539-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 3 | A proposes 0.01 more (reserves cover S1 + S2 exactly) | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6540-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 4 | A cancels the refused proposal (deposit returned) | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6542-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 5 | watcher W2 freezes asset 1 through M_watch (reason=deficit) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2 (watcher)) | `6546-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 6 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `6548-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |
| 7 | watcher W1 tries to thaw through M_watch (freezer is inert) | `Multisig.as_multi_threshold_1(Assets.thaw_asset)` (W1 (watcher)) | `6549-2` | Err(Assets.NoPermission) | ✅ Err(Assets.NoPermission) |
| 8 | A proposes a mint while frozen | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6550-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 9 | A cancels it | `Multisig.cancel_as_multi(Assets.mint)` (A (operator)) | `6552-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 10 | A proposes thaw_asset through M_admin (first approval) | `Multisig.as_multi(Assets.thaw_asset) — first approval` (A (operator)) | `6554-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 11 | bot B co-signs the thaw: finalized reserves >= S1 + S2 past the drain | `Multisig.as_multi(Assets.thaw_asset) — final approval` (B (reserve bot)) | `6557-2` | Ok + inner Ok + Assets.AssetThawed | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.AssetThawed |
| 12 | judge transfer 1.00 after the thaw | `Assets.transfer` (Judge) | `6558-2` | Ok | ✅ Ok |
| 13 | A proposes set_team with the freezer moved to A (through M_mint) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6559-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 14 | A cancels the refused team change | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6561-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 15 | A proposes set_team making A the sole admin (could thaw without the bot) | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6562-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 16 | A cancels the refused admin swap | `Multisig.cancel_as_multi(Assets.set_team)` (A (operator)) | `6564-2` | Ok + Multisig.MultisigCancelled | ✅ Ok · Multisig.MultisigCancelled |
| 17 | A proposes set_team keeping issuer M_mint, admin M_admin, freezer M_watch | `Multisig.as_multi(Assets.set_team) — first approval` (A (operator)) | `6565-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 18 | bot co-signs the safe team change | `Multisig.as_multi(Assets.set_team) — final approval` (B (reserve bot)) | `6567-2` | Ok + inner Ok + Assets.TeamChanged | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.TeamChanged |

Block and transaction hashes (full):

```
 1    6537-2 block 0xa95be2bd45a0364d50bde7d0400e6b7315bed2983ffcf7c22fc3cb58897cea8f  tx 0xc7891210caa4ead6cf6bd2dad50bffc84d51f8bdc69d0e451b6abb3dd5bdfc80
 2    6539-2 block 0xaf797a087c2abbf5973f73cc6f480d1c3fd13c308f977d52110f43f598b76e46  tx 0x0edf62af4740bd3f45d526c083f8a5227acd0883b786088b7c4c27ddca4e74d0
 3    6540-2 block 0xb7b92429d6c4fef7cb4629a705f5441fd1b413afa7835cd9d1bab73f29047b03  tx 0xaeb62e8d3a6b0af7ecf712bb7fdf2b88ca0bcbf0bf01fd95723afe321091f1d9
 4    6542-2 block 0x3f27c3bc20b0676d4b580ba59f3ee0cb2505f68e4932ef5d82b289908b8b51e7  tx 0x1dc5a9c785f288182bd318809d7f67709f641caa07fcc05ad5e10e742b8ae811
 5    6546-2 block 0x74131772319a174ed2ddf3fa77bd7b7396363fe35721964779791b1a16a1307b  tx 0xff73958319f25305b1c68dadc4d76fa425e9471bd95c55f681e411f7bf7f4548
 6    6548-2 block 0x003a859ac496d8a102da23bc38a036c272dc30c3628b00220b193d02d215f6a7  tx 0xe87e380cc90d4a1b64bde7b2e3df2f9aae86dd96e93ebeb1ec4d48ab112e7cbf
 7    6549-2 block 0xd867a8d28f98738eb68c21fba796fb72b4ad226035a436318fddea7e1c53870a  tx 0x2e94d6f86324ff16e94af0f7ae526750f71f9d195d76e9cf95d74cb989789cf1
 8    6550-2 block 0xd930e0c9bcd699cd30b3d130b4f1d2cc22e42dec2e45bf260569b18090bbdd09  tx 0x800d3d880a7c10b58cbf329823e26b4f9bf663699d3aa607907c25848874b5ed
 9    6552-2 block 0x7eb04fec7d29bb5a1e61b1019dd4c7538292e9489eb2f0cd78710231cabe6390  tx 0xfcdf7354c0204b81250a541ec75922d019e6adda6d6f7363b69a60e05b62f9f5
10    6554-2 block 0xafad06db02f5e405f774a8dda866c8b55afc0a60a5082aaace86f14f121d5c97  tx 0x8e07784e6364499302208d7fb60d01616dd94c62796bea43fe811831bea6dee7
11    6557-2 block 0x1b47b283a819a56fcdbd62980ad5ee9f708275966e8a2dda032d62e70a190562  tx 0xb0d4c1b6a3cc91b293f0f7ffa5bb29b2874a29c8e92576e117b548fc7ec1d63d
12    6558-2 block 0xfcff989631f430604b7feb8c3a26a942336c678eef7bea048ec838d6dda39ffe  tx 0x3d330f222c7db83a3712b3d0a0c3c4a77234d4d26780fcb6d40abcc4879d17bf
13    6559-2 block 0x769e146c58b107a35353a93e6fff614fcdcc9fb5ed016d8e2c5bf58662f6210c  tx 0x85047544884a6e0ed2080d61b43e049585bf27a1b0caa7d2358ed6d5d50981c0
14    6561-2 block 0x80949aaa3c5ff1137435ae02e07cc2cd3c71f405ac9c36236007d612c5294c25  tx 0x04819bd354086fe3111286901659207364e9d3b0db2812374285f4573936f3cf
15    6562-2 block 0xd74201eadcd7071320def68497dd1c6571d8687331803a87908434b50d5718a1  tx 0xcb1ac70fad7cde52c962f132356a817f35b717dea77be3a4b642e0a2be5d5cfd
16    6564-2 block 0xb7c6cdb3f0595867b67656db457f5739c800f6804cb8d7bf65237d00946ad63b  tx 0xd2138aad0783e9176c1868f7a6b0ee001478e1db5ef5e0ad5852ea5cb420dcce
17    6565-2 block 0x5646391efedbe1312dfd1af665ae973eaee2e6c225f82b2ed4d556bb8dcb2585  tx 0x99d0cdfa4ec89411ea19ec2de3990a8139c626aadf01c08119a7e283cc8711e2
18    6567-2 block 0x357ffb880669531d4582b11c6af8301093cadebdc1b5f98729dac49a6a29bbf5  tx 0xd3ba95d7605f8836215a048b4a78898187eeccfdc0500116ed41e1cd00afd6cc
```

State checks (storage/events read at the step's block):

- ✅ asset 1 team == role map before the drill (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ level before the drill: vault reserves == S1 + S2: expected `105000000`, observed `105000000` at block `head`
- ✅ S1 after the gated mint == S1 + 1.00: expected `56000000`, observed `56000000` at block `0xaf797a087c2abbf5973f73cc6f480d1c3fd13c308f977d52110f43f598b76e46`
- ✅ bot refuses the over-mint (exit 1, no signature): expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ over-mint still pending (no MultisigExecuted): approvals == [A]: expected `['A (operator)']`, observed `['A (operator)']` at block `0xe84d2a16b0cb97ea6e44391f4c3e79f3214f4472b94f64b4fe60fb114024869e`
- ✅ S1 unchanged by the refused over-mint: expected `56000000`, observed `56000000` at block `0xe84d2a16b0cb97ea6e44391f4c3e79f3214f4472b94f64b4fe60fb114024869e`
- ✅ no pending over-mint after the cancel: expected `None`, observed `None` at block `0x3f27c3bc20b0676d4b580ba59f3ee0cb2505f68e4932ef5d82b289908b8b51e7`
- ✅ both watchers armed and level (W1, W2 processes): expected `True`, observed `True` at block `watchdog logs`
- ✅ freeze remark eb == the drain's reserve-chain block: expected `671`, observed `671` at block `0x74131772319a174ed2ddf3fa77bd7b7396363fe35721964779791b1a16a1307b`
- ✅ trigger check ran after the drain was sent: expected `True`, observed `True` at block `watchdog log`
- ✅ asset 1 status after the freeze: expected `Frozen`, observed `Frozen` at block `0x74131772319a174ed2ddf3fa77bd7b7396363fe35721964779791b1a16a1307b`
- ✅ bot refuses any mint while frozen (I7): expected `I7`, observed `I7` at block `bot`
- ✅ vault reserves (latest) back to >= S1 + S2: expected `True`, observed `True` at block `evm latest`
- ✅ bot refuses the thaw: finality has not reached the drain block yet: expected `['refused', 671]`, observed `['refused', 671]` at block `bot`
- ✅ bot located the freeze (latest AssetFrozen, backward event scan) == the freeze receipt: expected `6546-2`, observed `6546-2` at block `0x74131772319a174ed2ddf3fa77bd7b7396363fe35721964779791b1a16a1307b`
- ✅ asset 1 status after the thaw: expected `Live`, observed `Live` at block `0x1b47b283a819a56fcdbd62980ad5ee9f708275966e8a2dda032d62e70a190562`
- ✅ asset 1 team unchanged (ARMED): expected `[]`, observed `[]` at block `head`
- ✅ bot refuses a set_team that changes the freezer: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ bot refuses a set_team that moves the admin off M_admin: expected `[1, 'refused']`, observed `[1, 'refused']` at block `bot`
- ✅ asset 1 team after the co-signed set_team (ARMED): expected `[]`, observed `[]` at block `head`

Other runs, newest first, any verdict (full tables in the JSON):

- asset 1 — 2026-10-14T14:30:22Z — PASS (20/20 steps as expected, 19/19 state checks) — source: `8665dda` (UNCOMMITTED CHANGES) — [`evidence/roles-drill-standin-upstream-20261014T143022Z.json`](../evidence/roles-drill-standin-upstream-20261014T143022Z.json)
- asset 1 — 2026-10-14T12:47:59Z — PASS (16/16 steps as expected, 17/17 state checks) — source: `25c6f22` (clean) — [`evidence/roles-drill-standin-upstream-20261014T124759Z.json`](../evidence/roles-drill-standin-upstream-20261014T124759Z.json)

### Attestations — BALLAST/1 remarks by B, ReserveOracle mirror, `ballast verify` + negative control — 2026-10-14T14:46:04Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/roles-attest-standin-upstream-20261014T144603Z.json`](../evidence/roles-attest-standin-upstream-20261014T144603Z.json) · result: **PASS** (15/15 steps as expected, 6/6 state checks) · source: `e70d2b0` (clean)

`ballast verify` blocks #6570..#6608 ([`evidence/verify-standin-upstream-20261014T144603Z.json`](../evidence/verify-standin-upstream-20261014T144603Z.json)): **PASS** — 4/4 B attestations PASS on both chains, 1 REJECTED (not counted), 0 FAIL/FLAGGED.

Heartbeat H = 20 blocks (drill override; production H = 200, K = 600 on this profile).

- finality (anvil): mined 65 blocks: finalized = latest − 64

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x162A433068F51e18b7d13932F27e66a3f99E6890`):

| # | Step | Block | Tx hash | Observed |
|---|---|---|---|---|
| 1 | custodian receives 1.00 test token | 738 | `0xaad9eeebab4230445adff5fce1c2e5fc6f7d1d694f10821647f28e758d136b3c` | ✅ status 1 |
| 2 | custodian deposits 1.00 into the vault | 739 | `0x7bc23158277750494b57ef60019b37b4aa7e5c8aac025da0fa1aafd053a1850a` | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | bot announces watchers (BALLAST/1|watchers|t=1|m=5C7iVxxiAvdPFuddh1UmsNiCLmz91wQMXhR…) | `System.remark_with_event(BALLAST/1|watchers)` (B (reserve bot)) | `6572-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 2 | bot announces evm-attester (BALLAST/1|evm-attester|h160=0x4dc969838572d068ead3ab83139904…) | `System.remark_with_event(BALLAST/1|evm-attester)` (B (reserve bot)) | `6573-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 3 | bot posts attest (pb 6570) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6574-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 4 | bot mirrors 6574-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6575-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 5 | bot posts attest (pb 6573) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6576-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 6 | A proposes mint 1.00 through M_mint | `Multisig.as_multi(Assets.mint) — first approval` (A (operator)) | `6577-2` | Ok + Multisig.NewMultisig | ✅ Ok · Multisig.NewMultisig |
| 7 | bot mirrors 6576-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6577-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 8 | bot B co-signs (finalized reserves cover it) | `Multisig.as_multi(Assets.mint) — final approval` (B (reserve bot)) | `6579-2` | Ok + inner Ok + Assets.Issued | ✅ Ok · inner Ok · Multisig.MultisigExecuted, Assets.Issued |
| 9 | bot posts attest (pb 6579) | `System.remark_with_event(BALLAST/1|attest)` (B (reserve bot)) | `6582-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 10 | bot mirrors 6582-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6583-2` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |
| 11 | bot posts heartbeat (pb 6603) | `System.remark_with_event(BALLAST/1|heartbeat)` (B (reserve bot)) | `6606-2` | Ok + System.Remarked | ✅ Ok · System.Remarked |
| 12 | negative control: the judge key posts a copy of the bot's attestation | `System.remark_with_event(BALLAST/1|attest) — forged by a non-bot key` (Judge (negative control)) | `6607-2` | Ok + System.Remarked (included — verify must REJECT it) | ✅ Ok · System.Remarked |
| 13 | bot mirrors 6606-2 to ReserveOracle (after inclusion, I10) | `Revive.call(ReserveOracle.post)` (B (reserve bot)) | `6607-3` | Ok + Revive.ContractEmitted(Posted) | ✅ Ok · Revive.ContractEmitted |

Block and transaction hashes (full):

```
 1    6572-2 block 0x9b16cc1b6ddbb86051e0048d3afa2e36220d73bfbc76dbb9429d679cd849729b  tx 0x0c4f5a8cc0279f717bf52d8e297c860466a6f460783a7d4a942388a347450ae7
 2    6573-2 block 0xe9cb086383400f0f1629f2475645b9c2fc1058aab4bc6c7a96a8600e526a6aa9  tx 0xfec5d8f3cd8b6b06b1987c6246fce9e3e7540f34f2e98f5a48d8aa9269998c84
 3    6574-2 block 0x6aca692838c81c00d53e45fe18fe93aac3a131783c3e2da8e707da99ab6a8337  tx 0x9fe59719a556e9ba50e5cb38c16869b55c0118fbefcca6547aa9e1dc7b1b09bf
 4    6575-2 block 0x597b1e1931fda671ed52731d543edbdcf9e78c1b009510b4a5a98f8c72983d22  tx 0x17292243d57e78c6dbad392c02f1258cf1edc4d48de9997b39bf6d9ef3f10525
 5    6576-2 block 0xdc21508404e17b7712933d62cc3e3194b2b4e571cc58026cdb9b5bb4f307b132  tx 0xd5e5a34ffbf5a9e3ea704583473717150e05bb05e517d37d9220e3c01832012a
 6    6577-2 block 0xc8186222f8d98348ba918e4c86a059e967881dbcdc16294f94b9255d05837b71  tx 0xa170d5db82a89c245fc1f096830d96b80134d715893d3d379517130cc19a8294
 7    6577-3 block 0xc8186222f8d98348ba918e4c86a059e967881dbcdc16294f94b9255d05837b71  tx 0xd36eabf50ffbcae898642471810cc3e4bc1c55dad953e8da1165cc469639f014
 8    6579-2 block 0x1e3b1c0fa33d94d44cc206fc42b701050da71448a7260665116743e56c8a250b  tx 0xd17801ce67a58870c97f4736dae180c983e0d43b437879f19dbb20b2b3d112ca
 9    6582-2 block 0xff3f929a0cbc15fcf025b54023e0ea7c1a7107e94d1deefe87e241942b389fdf  tx 0xc9adb432477e069e31e2cda60b7ef42f9283fa3f7fbf7cdef771e2bcdc053c68
10    6583-2 block 0x8bcfa71b3ccae33d882f8d9f54617e12e476b6083a830e17aa282fa989b3d1ae  tx 0x822f03639c6c29c44da50be65ab888a0c28b0233584bcf7efc6c624b80cf6268
11    6606-2 block 0xbe4b57c6073c87b8c26367d6fe1a1880472f7c9dd495c67905b7176618dba2d9  tx 0x8388a5e45b7a9fb9e0996de75f53ac9bc91e097c1f423afb9c1ad13e9b00aee9
12    6607-2 block 0xfccbc7cde875ec6700f7d5eac1109bd3833959f3d1bf25dd1485f8208ce60b98  tx 0xf1744f2802f14fd6f218d3dfa5b7a5cfacdf938c272bc9f84b42ec5f51b06970
13    6607-3 block 0xfccbc7cde875ec6700f7d5eac1109bd3833959f3d1bf25dd1485f8208ce60b98  tx 0xe1e1c40d9b5dd0a9b4ec311daa570f65a30ea8d939efe531704cc4cb8788a0fa
```

State checks (storage/events read at the step's block):

- ✅ the post after H quiet blocks is a heartbeat: expected `heartbeat`, observed `heartbeat` at block `0xbe4b57c6073c87b8c26367d6fe1a1880472f7c9dd495c67905b7176618dba2d9`
- ✅ verify exit 0 and verdict PASS: expected `[0, 'PASS']`, observed `[0, 'PASS']` at block `verify`
- ✅ every bot attestation/heartbeat PASSes on both chains: expected `4`, observed `4` at block `verify`
- ✅ every oracle post matches a PASSing remark (I10): expected `4`, observed `4` at block `verify`
- ✅ the forged remark is listed REJECTED (not counted): expected `['6607-2']`, observed `['6607-2']` at block `verify`
- ✅ watcher-set and evm-attester announcements PASS: expected `[1, 1]`, observed `[1, 1]` at block `verify`

Other runs, newest first, any verdict (full tables in the JSON):

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

### Breaker drill (heartbeat: no bot heartbeat for K blocks -> freeze (I8)) — asset 2037 — 2026-10-14T12:53:39Z

Chain: **standin-upstream (polkadot-sdk substrate-node --dev, NOT V3)** · reserve: **local-anvil (not Sepolia)** · raw JSON: [`evidence/drill-heartbeat-standin-upstream-asset2037.json`](../evidence/drill-heartbeat-standin-upstream-asset2037.json) · watchdog log: [`evidence/drill-heartbeat-standin-upstream-asset2037.watchdog.jsonl`](../evidence/drill-heartbeat-standin-upstream-asset2037.watchdog.jsonl) · result: **PASS** (13/13 steps as expected, 9/9 state checks) · source: `fd9e593` (clean)

Deployed initcode sha256: ReserveVault `2b03363cd765b37e0cf9a1a81ed60ec0a6ef8c4c91a0c03eadd56f8247a4c911`, MockUSDC `ca848fc1870c675c7a4fbd40a0a43439e013cb21268dc3b770d3b22745879753`.

Watcher parameters: `--timeout 3`, `--fail-closed-after 300`, `--max-block-age 0 (stale-block check off: anvil mines only when a tx lands)`, `--heartbeat-k 10`.

Reason remark (in the freeze extrinsic): `BALLAST/1|freeze|a=2037|reason=no-heartbeat|s=100000000|b=5CV5Em12kiJkzxePKai4aaNBkueyq2bL6j7QLM8mJ9Xw46x9|n=0|since=4331|k=10`

Timing (wall-clock on one machine; stand-in chain + local anvil reserve (not V3, not Sepolia)):

- `trigger_head`: 4341
- `freeze_block`: 4342
- `freeze_block_timestamp_ms`: 1791982479004
- `submit_to_inclusion_s`: 2.66
- `heartbeat_k (drill override; production K = 600 on this profile)`: 10
- `nonce_first_seen_block`: 4331
- `blocks_nonce_still_to_freeze_included`: 11

Reserve-chain transactions (local-anvil (not Sepolia); vault `0x2E2Ed0Cfd3AD2f1d34481277b3204d807Ca2F8c2`, token `0x21dF544947ba3E8b3c32561399E88B52Dc8b2823`):

| # | Step | Block | Tx hash | Expected | Observed |
|---|---|---|---|---|---|
| 1 | deploy MockUSDC (test-only token) | 266 | `0x1b09b89d5f8a813ecfb1c6266891d39a9e995605e209f6cf6514a033ba0e37b9` | status 1 | ✅ status 1 |
| 2 | deploy ReserveVault(usdc) — owner = custodian | 267 | `0x84ad630d081fcff35629f6b1126fa02cffddaccdf772354383538044d8d8529e` | status 1 | ✅ status 1 |
| 3 | deposit S1 + S2 = 100.00 into the vault | 268 | `0x168a377b497c789de83b4a43c0881568a31b640f607fee9eeb59f3dc8dc4b1f6` | status 1 | ✅ status 1 |

Portaldot extrinsics:

| # | Step | Call (signer) | Extrinsic id | Expected | Observed |
|---|---|---|---|---|---|
| 1 | fund A, W1, W2, judge, peer, M_watch (>= ED) | `Utility.batch_all[6 x Balances.transfer_keep_alive]` (Alice, stand-in funder) | `4323-2` | Ok | ✅ Ok |
| 2 | create asset 2037 | `Assets.create` (A) | `4324-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 3 | set_metadata pUSDC-test (6 decimals) | `Assets.set_metadata` (A) | `4325-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 4 | create asset 2038 | `Assets.create` (A) | `4326-2` | Ok + Assets.Created | ✅ Ok · Assets.Created |
| 5 | set_metadata pUSDC-ctl (6 decimals) | `Assets.set_metadata` (A) | `4327-2` | Ok + Assets.MetadataSet | ✅ Ok · Assets.MetadataSet |
| 6 | set_team asset 2037: freezer = M_watch (1-of-2 watchers) | `Assets.set_team` (A) | `4328-2` | Ok + Assets.TeamChanged | ✅ Ok · Assets.TeamChanged |
| 7 | mint S1 = 50.00 of asset 2037 to the judge | `Assets.mint` (A) | `4330-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 8 | mint S2 = 50.00 of control asset 2038 to the peer | `Assets.mint` (A) | `4331-2` | Ok + Assets.Issued | ✅ Ok · Assets.Issued |
| 9 | watchdog (W2) freezes asset 2037 via M_watch, reason on chain (reason=no-heartbeat) | `Utility.batch_all[System.remark_with_event, Multisig.as_multi_threshold_1(Assets.freeze_asset)]` (W2) | `4342-2` | Ok + inner Ok + Assets.AssetFrozen + System.Remarked | ✅ Ok · inner Ok · Assets.AssetFrozen, System.Remarked, Multisig.MultisigExecuted |
| 10 | judge transfer 1.00 while frozen is refused | `Assets.transfer` (Judge) | `4343-2` | Err(Assets.AssetNotLive) | ✅ Err(Assets.AssetNotLive) |

Block and transaction hashes (full):

```
 1    4323-2 block 0xd299e6b52ca0232e4ccb7328c957a8e60c17bfb030f66c1ebf0e29e38484ab80  tx 0xae597c53e791f9788aac421737ec49662f35673dbac0f42cd3fff30d6109b4a3
 2    4324-2 block 0xa4116b21250928fb2051f229465c8123d4d3b0c5c1fd30619476c69c439120ed  tx 0xf60a890d3f08fa3e4eabe8bc529a02076976f577245c567d2ee0796c642f7955
 3    4325-2 block 0x5d085469bc1b78cb5ce0734df89d714f16b21eff73b681e570aeb89bd812aed7  tx 0x58921c6eaea825cc2b725ab2ca10660d9af03c36866d261ae9f20b8b27dae5f8
 4    4326-2 block 0x2ecb43c2a33141fc556bf4795a25d612f44179f34496c898345bb1eb56b31708  tx 0xf0f673e0ea969c0b17797d23108e20aaad2725f23c4936d6ce834a1cd76fbde7
 5    4327-2 block 0x015b2cc3cc13bf6f84e32c3afb6420813597a8b03e9626b62531191089d951bd  tx 0x7a513b397579935a2847b2233f7359a20f6558bc41ac4d7526ba8fca95f95500
 6    4328-2 block 0x27d4dc3647b0202256f94f05d8aebdb6c1dcf70120676198442a2a451931e924  tx 0xddb8006c59904c8f8ebde329184d96c6c7b57a06cccd998635a4d442d6b6c4bd
 7    4330-2 block 0x2cf44f6509379d645e18dabd8b904412922dc0d14211fa58c3537859a78a11f1  tx 0xc3c05eb1ceb3b1d9950951a37c5d647509fe6001d4a7591cb2b5316d7ed6df40
 8    4331-2 block 0x50fde574e8726e3bdf6f659a2c3376d56b13acdd0e967b878cb6e85590ca145d  tx 0x5e494ea3be89d82689005580d891d57ae720e91e031f3b40623dc8bc5cea539f
 9    4342-2 block 0xb07b11ad7bb28b444f04691b02f6d3685db532b2b09f40f6920457b98f196013  tx 0xd5770aabce7b43adcd9868a21ade5952fa00aae5f2bc509198dbb1ce27387356
10    4343-2 block 0x999f56d81cb67ab7dced9fbbf8b49e171d3ce932213dd73089979854da3172e6  tx 0xa3336f12a160a1f8b4c0bc39fb05669543c416d4d0ac5609e50bd3bf6fa0cf36
```

State checks (storage/events read at the step's block):

- ✅ vault reserves() after deposit: expected `100000000`, observed `100000000` at block `evm latest`
- ✅ supply S1 + S2 == vault reserves (level): expected `100000000`, observed `100000000` at block `0x50fde574e8726e3bdf6f659a2c3376d56b13acdd0e967b878cb6e85590ca145d`
- ✅ watchdog armed: its M_watch == the breaker's freezer: expected `True`, observed `True` at block `watchdog start record`
- ✅ Asset(2037).status after the freeze: expected `Frozen`, observed `Frozen` at block `0xb07b11ad7bb28b444f04691b02f6d3685db532b2b09f40f6920457b98f196013`
- ✅ System.Remarked hash == blake2_256(the reason remark): expected `0xfce102a7bd1b9623e075aabf273cffb71f1235d9dc36614c00700d2a66897900`, observed `0xfce102a7bd1b9623e075aabf273cffb71f1235d9dc36614c00700d2a66897900` at block `0xb07b11ad7bb28b444f04691b02f6d3685db532b2b09f40f6920457b98f196013`
- ✅ control asset 2038 untouched (Live): expected `Live`, observed `Live` at block `0xb07b11ad7bb28b444f04691b02f6d3685db532b2b09f40f6920457b98f196013`
- ✅ judge balance unchanged after the refused transfer: expected `50000000`, observed `50000000` at block `0x999f56d81cb67ab7dced9fbbf8b49e171d3ce932213dd73089979854da3172e6`
- ✅ the triggering check saw the bot nonce unchanged for >= K blocks: expected `True`, observed `True` at block `watchdog log`
- ✅ reserves were level at the trigger (the freeze is the heartbeat rule alone): expected `[]`, observed `[]` at block `watchdog log`


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
