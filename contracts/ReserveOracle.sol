// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title ReserveOracle
/// @notice EVM-readable mirror of Ballast's breaker state, for Portaldot V3's Revive (target; deploy pending the
/// V3 day-0 gate). The reserve bot's EVM key (`attester`) posts each attestation AFTER the matching BALLAST/1
/// remark is included on Portaldot; any EVM dApp reads `status()` / `isBacked(maxAge)`.
/// It never holds or moves value and cannot freeze the asset: the freeze lives in the Assets pallet. A stale
/// mirror reads as NOT backed (`isBacked` fails closed on age), and a never-posted oracle is never backed.
contract ReserveOracle {
    struct Status {
        uint128 s1; // supply of the wrapped asset (asset 1)
        uint128 s2; // supply of the control asset
        uint256 reserves; // vault USDC (6 decimals) read at sepBlock
        uint64 sepBlock; // Sepolia block the reserves were read at
        bytes32 sepHash; // that block's hash
        uint64 pdBlock; // Portaldot block of the attestation remark
        bool frozen; // breaker asset frozen at pdBlock
        uint64 updatedAt; // EVM block.timestamp of the post
    }

    address public immutable attester;
    Status private _status;

    event Posted(
        uint128 s1, uint128 s2, uint256 reserves, uint64 indexed sepBlock, bytes32 sepHash, uint64 indexed pdBlock,
        bool frozen
    );

    error NotAttester(address caller);
    error ZeroAddress();
    error StalePost(uint64 pdBlock, uint64 latestPdBlock);

    constructor(address attester_) {
        if (attester_ == address(0)) revert ZeroAddress();
        attester = attester_;
    }

    /// @notice Mirror one attestation. Portaldot blocks only move forward: an older or repeated pdBlock reverts.
    function post(uint128 s1, uint128 s2, uint256 reserves, uint64 sepBlock, bytes32 sepHash, uint64 pdBlock, bool frozen)
        external
    {
        if (msg.sender != attester) revert NotAttester(msg.sender);
        if (_status.updatedAt != 0 && pdBlock <= _status.pdBlock) revert StalePost(pdBlock, _status.pdBlock);
        // forge-lint: disable-next-line(unsafe-typecast) — a uint64 of seconds outlasts the chain
        _status = Status(s1, s2, reserves, sepBlock, sepHash, pdBlock, frozen, uint64(block.timestamp));
        emit Posted(s1, s2, reserves, sepBlock, sepHash, pdBlock, frozen);
    }

    function status() external view returns (Status memory) {
        return _status;
    }

    /// @notice True only if posted, not frozen, reserves cover S1 + S2, and the post is at most `maxAge` seconds old.
    function isBacked(uint256 maxAge) external view returns (bool) {
        Status memory s = _status;
        if (s.updatedAt == 0 || s.frozen) return false;
        // forge-lint: disable-next-line(block-timestamp) — maxAge is minutes; producer clock drift is seconds
        if (block.timestamp - s.updatedAt > maxAge) return false;
        return s.reserves >= uint256(s.s1) + uint256(s.s2);
    }
}
