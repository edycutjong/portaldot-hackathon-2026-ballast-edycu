// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @dev The subset of ERC-20 the vault touches.
interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
}

/// @title ReserveVault
/// @notice Holds the USDC that backs pUSDC-test on Portaldot. Deposits are plain ERC-20 transfers into this
/// address; only the owner (the custodian) can move funds out, and every move emits `Released`. Watchers read
/// `reserves()` (or `balanceOf(vault)` on the token) and freeze the Portaldot asset when it falls below supply.
/// The vault does not, and cannot, stop the owner from draining it — the breaker on Portaldot is the guard.
contract ReserveVault {
    IERC20 public immutable usdc;
    address public owner;

    event Released(address indexed to, uint256 amount, bytes32 indexed redeemId);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    error NotOwner(address caller);
    error ZeroAddress();
    error ZeroAmount();
    error InsufficientReserves(uint256 available, uint256 requested);
    error TransferFailed();

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner(msg.sender);
        _;
    }

    constructor(IERC20 usdc_) {
        if (address(usdc_) == address(0)) revert ZeroAddress();
        usdc = usdc_;
        owner = msg.sender;
        emit OwnershipTransferred(address(0), msg.sender);
    }

    /// @notice USDC held by the vault right now (6 decimals for Circle USDC).
    function reserves() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }

    /// @notice Move `amount` USDC out of the vault. `redeemId` links the release to a redemption (or a drill).
    function release(address to, uint256 amount, bytes32 redeemId) external onlyOwner {
        if (to == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        uint256 available = usdc.balanceOf(address(this));
        if (amount > available) revert InsufficientReserves(available, amount);
        emit Released(to, amount, redeemId); // before the call: a failed transfer reverts the event too
        _safeTransfer(to, amount);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        if (newOwner == address(0)) revert ZeroAddress();
        address previous = owner;
        owner = newOwner;
        emit OwnershipTransferred(previous, newOwner);
    }

    /// @dev Accepts tokens that return `true` and tokens that return nothing; anything else reverts.
    function _safeTransfer(address to, uint256 amount) private {
        (bool ok, bytes memory data) = address(usdc).call(abi.encodeCall(IERC20.transfer, (to, amount)));
        if (!ok || (data.length != 0 && !abi.decode(data, (bool)))) revert TransferFailed();
    }
}
