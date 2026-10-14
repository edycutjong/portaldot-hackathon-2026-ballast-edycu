// ReserveOracle on Hardhat's local EVM (not Revive/PolkaVM: parity is checked when it is deployed on V3).
const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

const S1 = 50_000_000n; // 50.00, 6 decimals
const S2 = 50_000_000n;
const SEP_HASH = "0x" + "ab".repeat(32);
const MAX_AGE = 3600n;

describe("ReserveOracle", function () {
  let oracle, attester, stranger;

  // post(s1, s2, reserves, sepBlock, sepHash, pdBlock, frozen)
  const post = (who, { s1 = S1, s2 = S2, reserves = S1 + S2, sepBlock = 100n, pdBlock = 10n, frozen = false } = {}) =>
    oracle.connect(who).post(s1, s2, reserves, sepBlock, SEP_HASH, pdBlock, frozen);

  beforeEach(async function () {
    [attester, stranger] = await ethers.getSigners();
    oracle = await ethers.deployContract("ReserveOracle", [attester.address]);
  });

  it("stores the attester", async function () {
    expect(await oracle.attester()).to.equal(attester.address);
  });

  it("rejects a zero attester", async function () {
    const factory = await ethers.getContractFactory("ReserveOracle");
    await expect(factory.deploy(ethers.ZeroAddress)).to.be.revertedWithCustomError(oracle, "ZeroAddress");
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
});
