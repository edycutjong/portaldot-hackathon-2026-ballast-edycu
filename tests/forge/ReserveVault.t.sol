// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";
import {ReserveVault, IERC20} from "../../contracts/ReserveVault.sol";
import {MockUSDC} from "../../contracts/mocks/MockUSDC.sol";

/// @dev Returns nothing from `transfer` (USDT-style) — the vault must still accept it.
contract NoReturnToken {
    mapping(address => uint256) public balanceOf;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function transfer(address to, uint256 amount) external {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
    }
}

contract ReserveVaultTest is Test {
    event Released(address indexed to, uint256 amount, bytes32 indexed redeemId);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    uint256 constant S1 = 50_000_000; // 50.00 USDC (6 decimals) backing asset 1
    uint256 constant S2 = 50_000_000; // 50.00 USDC backing the control asset
    bytes32 constant DRILL = keccak256("drill-1");

    MockUSDC usdc;
    ReserveVault vault;
    address custodian = makeAddr("custodian");
    address stranger = makeAddr("stranger");
    address redeemer = makeAddr("redeemer");

    function setUp() public {
        usdc = new MockUSDC();
        vm.prank(custodian);
        vault = new ReserveVault(IERC20(address(usdc)));
        usdc.mint(address(vault), S1 + S2); // a deposit is a plain ERC-20 transfer/mint to the vault
    }

    function test_constructorSetsOwnerAndToken() public view {
        assertEq(vault.owner(), custodian);
        assertEq(address(vault.usdc()), address(usdc));
    }

    function test_constructorRejectsZeroToken() public {
        vm.expectRevert(ReserveVault.ZeroAddress.selector);
        new ReserveVault(IERC20(address(0)));
    }

    function test_constructorEmitsOwnership() public {
        vm.expectEmit(true, true, false, false);
        emit OwnershipTransferred(address(0), address(this));
        new ReserveVault(IERC20(address(usdc)));
    }

    function test_reservesTracksTokenBalance() public {
        assertEq(vault.reserves(), S1 + S2);
        usdc.mint(address(vault), 1);
        assertEq(vault.reserves(), S1 + S2 + 1);
        assertEq(vault.reserves(), usdc.balanceOf(address(vault)));
    }

    function test_plainTransferIsADeposit() public {
        usdc.mint(stranger, 30_000_000);
        vm.prank(stranger);
        usdc.transfer(address(vault), 30_000_000);
        assertEq(vault.reserves(), S1 + S2 + 30_000_000);
    }

    function test_ownerReleasesAndEmits() public {
        vm.expectEmit(true, true, false, true, address(vault));
        emit Released(redeemer, 30_000_000, DRILL);
        vm.prank(custodian);
        vault.release(redeemer, 30_000_000, DRILL);
        assertEq(usdc.balanceOf(redeemer), 30_000_000);
        assertEq(vault.reserves(), S1 + S2 - 30_000_000);
    }

    function test_drainBelowSupplyIsPossible() public {
        // The vault cannot protect holders from its owner: a 30% drain puts reserves under S1 + S2.
        vm.prank(custodian);
        vault.release(custodian, 30_000_000, DRILL);
        assertLt(vault.reserves(), S1 + S2);
    }

    function test_releaseWholeBalance() public {
        vm.prank(custodian);
        vault.release(redeemer, S1 + S2, DRILL);
        assertEq(vault.reserves(), 0);
    }

    function test_strangerCannotRelease() public {
        vm.expectRevert(abi.encodeWithSelector(ReserveVault.NotOwner.selector, stranger));
        vm.prank(stranger);
        vault.release(stranger, 1, DRILL);
        assertEq(vault.reserves(), S1 + S2);
    }

    function test_releaseToZeroAddressReverts() public {
        vm.expectRevert(ReserveVault.ZeroAddress.selector);
        vm.prank(custodian);
        vault.release(address(0), 1, DRILL);
    }

    function test_zeroAmountReverts() public {
        vm.expectRevert(ReserveVault.ZeroAmount.selector);
        vm.prank(custodian);
        vault.release(redeemer, 0, DRILL);
    }

    function test_overReleaseReverts() public {
        vm.expectRevert(abi.encodeWithSelector(ReserveVault.InsufficientReserves.selector, S1 + S2, S1 + S2 + 1));
        vm.prank(custodian);
        vault.release(redeemer, S1 + S2 + 1, DRILL);
    }

    function test_failedTokenTransferReverts() public {
        usdc.setFailTransfers(true);
        vm.expectRevert(ReserveVault.TransferFailed.selector);
        vm.prank(custodian);
        vault.release(redeemer, 1, DRILL);
        assertEq(vault.reserves(), S1 + S2);
    }

    function test_noReturnTokenIsAccepted() public {
        NoReturnToken token = new NoReturnToken();
        ReserveVault v = new ReserveVault(IERC20(address(token)));
        token.mint(address(v), 10);
        v.release(redeemer, 4, DRILL);
        assertEq(v.reserves(), 6);
        assertEq(token.balanceOf(redeemer), 4);
    }

    function test_transferOwnership() public {
        vm.expectEmit(true, true, false, false, address(vault));
        emit OwnershipTransferred(custodian, stranger);
        vm.prank(custodian);
        vault.transferOwnership(stranger);
        assertEq(vault.owner(), stranger);

        vm.expectRevert(abi.encodeWithSelector(ReserveVault.NotOwner.selector, custodian));
        vm.prank(custodian);
        vault.release(custodian, 1, DRILL);

        vm.prank(stranger);
        vault.release(stranger, 1, DRILL);
        assertEq(usdc.balanceOf(stranger), 1);
    }

    function test_strangerCannotTransferOwnership() public {
        vm.expectRevert(abi.encodeWithSelector(ReserveVault.NotOwner.selector, stranger));
        vm.prank(stranger);
        vault.transferOwnership(stranger);
    }

    function test_transferOwnershipToZeroReverts() public {
        vm.expectRevert(ReserveVault.ZeroAddress.selector);
        vm.prank(custodian);
        vault.transferOwnership(address(0));
    }

    /// Reserves accounting: any sequence of deposits and releases leaves reserves == deposits - releases.
    function testFuzz_reservesAccounting(uint96 deposit, uint96 releaseAmt) public {
        usdc.mint(address(vault), deposit);
        uint256 total = S1 + S2 + uint256(deposit);
        uint256 amount = bound(uint256(releaseAmt), 1, total);
        vm.prank(custodian);
        vault.release(redeemer, amount, DRILL);
        assertEq(vault.reserves(), total - amount);
        assertEq(usdc.balanceOf(redeemer), amount);
    }

    function testFuzz_onlyOwnerReleases(address caller) public {
        vm.assume(caller != custodian);
        vm.expectRevert(abi.encodeWithSelector(ReserveVault.NotOwner.selector, caller));
        vm.prank(caller);
        vault.release(caller, 1, DRILL);
    }
}
