// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title ReserveOracle
/// @notice EVM-readable mirror of Ballast's breaker state, for Portaldot V3's Revive (target; deploy pending the
/// V3 day-0 gate). The reserve bot's EVM key (`attester`) posts each attestation AFTER the matching BALLAST/1
/// remark is included on Portaldot; any EVM dApp reads `status()` / `isBacked(maxAge)`.
/// It never holds or moves value and cannot freeze the asset: the freeze lives in the Assets pallet. A stale
/// mirror reads as NOT backed (`isBacked` fails closed on age), and a never-posted oracle is never backed.
/// v2: any listed watcher H160 can `trip()` it — one-way, like the pallet freezer: it sets `frozen` and nothing else.
/// Only the attester clears it, with a post whose Portaldot block is AFTER the trip's block (on Revive,
/// `block.number` is the Portaldot block), i.e. a pallet reading taken after the trip.
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
    mapping(address => bool) public isWatcher;
    address[] private _watchers;
    uint64 public trippedBlock; // block of the latest trip (0 = never tripped)

    event Posted(
        uint128 s1, uint128 s2, uint256 reserves, uint64 indexed sepBlock, bytes32 sepHash, uint64 indexed pdBlock,
        bool frozen
    );

    error NotAttester(address caller);
    error ZeroAddress();
    event Tripped(address indexed watcher, uint64 blockNumber);

    error StalePost(uint64 pdBlock, uint64 latestPdBlock);
    error NotWatcher(address caller);
    error DuplicateWatcher(address watcher);
    error TripNotCleared(uint64 pdBlock, uint64 trippedBlock);

    constructor(address attester_, address[] memory watchers_) {
        if (attester_ == address(0)) revert ZeroAddress();
        attester = attester_;
        for (uint256 i = 0; i < watchers_.length; i++) {
            address w = watchers_[i];
            if (w == address(0)) revert ZeroAddress();
            if (isWatcher[w]) revert DuplicateWatcher(w);
            isWatcher[w] = true;
            _watchers.push(w);
        }
    }

    /// @notice Any listed watcher marks the mirror frozen (one-way). It changes nothing else and moves no value.
    function trip() external {
        if (!isWatcher[msg.sender]) revert NotWatcher(msg.sender);
        _status.frozen = true;
        // forge-lint: disable-next-line(unsafe-typecast) — a uint64 block number outlasts the chain
        trippedBlock = uint64(block.number);
        emit Tripped(msg.sender, trippedBlock);
    }

    function watchers() external view returns (address[] memory) {
        return _watchers;
    }

    /// @notice Mirror one attestation. Portaldot blocks only move forward: an older or repeated pdBlock reverts.
    /// Accepted trade-off: there is no reset, so a post with a wrong (too high) pdBlock blocks later posts; the mirror
    /// then goes stale and `isBacked` fails closed. Recovery = deploy a new oracle (the address is announced by remark).
    function post(uint128 s1, uint128 s2, uint256 reserves, uint64 sepBlock, bytes32 sepHash, uint64 pdBlock, bool frozen)
        external
    {
        if (msg.sender != attester) revert NotAttester(msg.sender);
        if (_status.updatedAt != 0 && pdBlock <= _status.pdBlock) revert StalePost(pdBlock, _status.pdBlock);
        if (!frozen && trippedBlock != 0 && pdBlock <= trippedBlock) revert TripNotCleared(pdBlock, trippedBlock);
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
