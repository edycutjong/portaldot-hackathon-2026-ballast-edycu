// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @title MockUSDC
/// @notice Test-only 6-decimal ERC-20 with an open `mint`. Used by the forge tests and the local-anvil drill
/// (labelled "reserve: local-anvil (not Sepolia)"); the Sepolia vault holds Circle's real test USDC instead.
/// `failTransfers` makes `transfer` return false, to test the vault's failed-transfer path.
contract MockUSDC {
    string public constant name = "Mock USDC (test only)";
    string public constant symbol = "mUSDC";
    uint8 public constant decimals = 6;

    uint256 public totalSupply;
    bool public failTransfers;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    function mint(address to, uint256 amount) external {
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    function setFailTransfers(bool fail) external {
        failTransfers = fail;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        if (failTransfers) return false;
        _move(msg.sender, to, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        if (failTransfers) return false;
        allowance[from][msg.sender] -= amount;
        _move(from, to, amount);
        return true;
    }

    function _move(address from, address to, uint256 amount) private {
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        emit Transfer(from, to, amount);
    }
}
