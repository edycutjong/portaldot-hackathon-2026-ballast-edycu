// Hardhat: ReserveOracle tests on Hardhat's local EVM. The V3 deploy target (Revive, chain id 420420777 per the
// V3 testnet guide) is added once the V3 day-0 gate passes; PolkaVM/Revive parity is not assumed here.
require("@nomicfoundation/hardhat-ethers");
require("@nomicfoundation/hardhat-chai-matchers");

module.exports = {
  solidity: { version: "0.8.24", settings: { optimizer: { enabled: true, runs: 200 }, evmVersion: "cancun" } },
  paths: { sources: "./contracts", tests: "./tests/hardhat", cache: "./cache/hardhat", artifacts: "./artifacts" },
};
