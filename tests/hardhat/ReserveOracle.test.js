// ReserveOracle on Hardhat's local EVM (not Revive/PolkaVM: parity is checked when it is deployed on V3).
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

const S1 = 50_000_000n; // 50.00, 6 decimals
const S2 = 50_000_000n;
const SEP_HASH = "0x" + "ab".repeat(32);
const MAX_AGE = 3600n;

describe("ReserveOracle", function () {
  let oracle, attester, stranger, watcher, watcher2;

  // post(s1, s2, reserves, sepBlock, sepHash, pdBlock, frozen)
  const post = (who, { s1 = S1, s2 = S2, reserves = S1 + S2, sepBlock = 100n, pdBlock = 10n, frozen = false } = {}) =>
    oracle.connect(who).post(s1, s2, reserves, sepBlock, SEP_HASH, pdBlock, frozen);

  beforeEach(async function () {
    [attester, stranger, watcher, watcher2] = await ethers.getSigners();
    oracle = await ethers.deployContract("ReserveOracle", [attester.address, [watcher.address, watcher2.address]]);
  });

  it("stores the attester", async function () {
    expect(await oracle.attester()).to.equal(attester.address);
  });

  it("rejects a zero attester", async function () {
    const factory = await ethers.getContractFactory("ReserveOracle");
    await expect(factory.deploy(ethers.ZeroAddress, [])).to.be.revertedWithCustomError(oracle, "ZeroAddress");
  });

  it("is never backed before the first post", async function () {
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
    expect((await oracle.status()).updatedAt).to.equal(0n);
  });

  it("only the attester can post", async function () {
    await expect(post(stranger))
      .to.be.revertedWithCustomError(oracle, "NotAttester")
      .withArgs(stranger.address);
  });

  it("post stores the status and emits Posted", async function () {
    await expect(post(attester, { reserves: 100_000_000n, sepBlock: 7n, pdBlock: 42n }))
      .to.emit(oracle, "Posted")
      .withArgs(S1, S2, 100_000_000n, 7n, SEP_HASH, 42n, false);
    const s = await oracle.status();
    expect(s.s1).to.equal(S1);
    expect(s.s2).to.equal(S2);
    expect(s.reserves).to.equal(100_000_000n);
    expect(s.sepBlock).to.equal(7n);
    expect(s.sepHash).to.equal(SEP_HASH);
    expect(s.pdBlock).to.equal(42n);
    expect(s.frozen).to.equal(false);
    expect(s.updatedAt).to.equal(BigInt(await time.latest()));
  });

  it("is backed when reserves cover S1 + S2 exactly", async function () {
    await post(attester, { reserves: S1 + S2 });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
  });

  it("is not backed one unit short", async function () {
    await post(attester, { reserves: S1 + S2 - 1n });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
  });

  it("is not backed while the breaker asset is frozen, even with full reserves", async function () {
    await post(attester, { reserves: 10n * (S1 + S2), frozen: true });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
  });

  it("goes stale: not backed once older than maxAge", async function () {
    await post(attester);
    await time.increase(Number(MAX_AGE));
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true); // exactly maxAge old: still fresh
    await time.increase(1);
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
    expect(await oracle.isBacked(MAX_AGE * 2n)).to.equal(true); // the reader picks the tolerance
  });

  it("a newer post clears frozen and refreshes the age", async function () {
    await post(attester, { pdBlock: 10n, frozen: true });
    await time.increase(Number(MAX_AGE) + 10);
    await post(attester, { pdBlock: 11n, frozen: false });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
  });

  it("rejects an older or repeated Portaldot block (no replay, no reordering)", async function () {
    await post(attester, { pdBlock: 10n });
    await expect(post(attester, { pdBlock: 10n }))
      .to.be.revertedWithCustomError(oracle, "StalePost")
      .withArgs(10n, 10n);
    await expect(post(attester, { pdBlock: 9n })).to.be.revertedWithCustomError(oracle, "StalePost");
    await post(attester, { pdBlock: 11n });
    expect((await oracle.status()).pdBlock).to.equal(11n);
  });

  it("accepts pdBlock 0 as the first post, then only higher blocks", async function () {
    await post(attester, { pdBlock: 0n });
    expect((await oracle.status()).pdBlock).to.equal(0n);
    await expect(post(attester, { pdBlock: 0n })).to.be.revertedWithCustomError(oracle, "StalePost");
    await post(attester, { pdBlock: 1n });
  });

  it("a too-high pdBlock blocks later posts; the mirror then fails closed by age", async function () {
    await post(attester, { pdBlock: 2n ** 64n - 1n });
    await expect(post(attester, { pdBlock: 12n })).to.be.revertedWithCustomError(oracle, "StalePost");
    await time.increase(Number(MAX_AGE) + 1);
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
  });

  it("S1 + S2 cannot overflow the comparison", async function () {
    const max = 2n ** 128n - 1n;
    await post(attester, { s1: max, s2: max, reserves: 2n ** 256n - 1n });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
    await post(attester, { s1: max, s2: max, reserves: 2n * max - 1n, pdBlock: 11n });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
  });

  it("holds no value: plain ETH transfers revert", async function () {
    await expect(stranger.sendTransaction({ to: await oracle.getAddress(), value: 1n })).to.be.reverted;
  });

  // --- v2: trip() by a listed watcher ------------------------------------------------------------------------
  it("lists its watchers and rejects a zero or duplicate watcher", async function () {
    expect(await oracle.watchers()).to.deep.equal([watcher.address, watcher2.address]);
    expect(await oracle.isWatcher(watcher.address)).to.equal(true);
    expect(await oracle.isWatcher(stranger.address)).to.equal(false);
    const factory = await ethers.getContractFactory("ReserveOracle");
    await expect(factory.deploy(attester.address, [ethers.ZeroAddress])).to.be.revertedWithCustomError(oracle, "ZeroAddress");
    await expect(factory.deploy(attester.address, [watcher.address, watcher.address]))
      .to.be.revertedWithCustomError(oracle, "DuplicateWatcher")
      .withArgs(watcher.address);
  });

  it("only a listed watcher can trip, and the attester is not one", async function () {
    await expect(oracle.connect(stranger).trip()).to.be.revertedWithCustomError(oracle, "NotWatcher").withArgs(stranger.address);
    await expect(oracle.connect(attester).trip()).to.be.revertedWithCustomError(oracle, "NotWatcher").withArgs(attester.address);
  });

  it("a trip turns a backed mirror unbacked and changes nothing else", async function () {
    await post(attester, { pdBlock: 10n });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
    const before = await oracle.status();
    const tx = await oracle.connect(watcher).trip();
    const rcpt = await tx.wait();
    await expect(tx).to.emit(oracle, "Tripped").withArgs(watcher.address, BigInt(rcpt.blockNumber));
    const after = await oracle.status();
    expect(after.frozen).to.equal(true);
    expect([after.s1, after.s2, after.reserves, after.pdBlock, after.updatedAt])
      .to.deep.equal([before.s1, before.s2, before.reserves, before.pdBlock, before.updatedAt]);
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
    expect(await oracle.trippedBlock()).to.equal(BigInt(rcpt.blockNumber));
  });

  it("a trip is one-way: tripping again is harmless, a stale unfrozen post cannot clear it", async function () {
    await post(attester, { pdBlock: 1n });
    const rcpt = await (await oracle.connect(watcher).trip()).wait();
    await oracle.connect(watcher2).trip();
    const tripped = await oracle.trippedBlock();
    expect(tripped).to.be.greaterThan(BigInt(rcpt.blockNumber) - 1n);
    await expect(post(attester, { pdBlock: tripped }))
      .to.be.revertedWithCustomError(oracle, "TripNotCleared")
      .withArgs(tripped, tripped);
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
  });

  it("a frozen post may land at any later block; only a reading after the trip clears it", async function () {
    await post(attester, { pdBlock: 1n });
    await oracle.connect(watcher).trip();
    const tripped = await oracle.trippedBlock();
    await post(attester, { pdBlock: 2n, frozen: true }); // still frozen: no trip check needed
    await post(attester, { pdBlock: tripped + 1n });
    expect((await oracle.status()).frozen).to.equal(false);
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
  });

  it("a trip before the first post leaves it never-backed and still lets the first post through", async function () {
    await oracle.connect(watcher).trip();
    expect(await oracle.isBacked(MAX_AGE)).to.equal(false);
    await post(attester, { pdBlock: (await oracle.trippedBlock()) + 1n });
    expect(await oracle.isBacked(MAX_AGE)).to.equal(true);
  });
});
