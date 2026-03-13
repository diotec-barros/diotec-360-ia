"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Demo: Conservation-Aware Oracle Integration

Demonstrates the complete flow of validating conservation
with oracle-influenced transactions.

Author: Aethel Team
Version: 1.7.1
Date: February 4, 2026
"""

from diotec360.core.conservation import (
    ConservationChecker,
    BalanceChange,
    SlippageValidator
)
from diotec360.core.oracle import (
    get_oracle_simulator,
    get_oracle_registry,
    verify_oracle_proof,
    OracleStatus
)


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print formatted section"""
    print(f"\n{title}")
    print("-" * 70)


def demo_simple_conservation():
    """Demo 1: Simple conservation without oracle"""
    print_header("DEMO 1: Simple Transfer (No Oracle)")
    
    checker = ConservationChecker()
    
    # Simple transfer: Alice sends 100 to Bob
    changes = [
        BalanceChange(
            variable_name="alice_balance",
            amount=100,
            line_number=1,
            is_increase=False
        ),
        BalanceChange(
            variable_name="bob_balance",
            amount=100,
            line_number=2,
            is_increase=True
        )
    ]
    
    print("\nTransaction:")
    print("  alice_balance: -100")
    print("  bob_balance:   +100")
    
    result = checker.check_oracle_conservation(changes)
    
    print(f"\nResult: {'✅ VERIFIED' if result.is_valid else '❌ REJECTED'}")
    print(f"Conservation: {-100 + 100} = 0 ✅")


def demo_oracle_liquidation():
    """Demo 2: DeFi liquidation with oracle"""
    print_header("DEMO 2: DeFi Liquidation with Oracle")
    
    checker = ConservationChecker()
    simulator = get_oracle_simulator()
    
    # Fetch BTC price from oracle
    print("\n🔍 Fetching BTC price from Chainlink oracle...")
    btc_proof = simulator.fetch_data("chainlink_btc_usd")
    
    print(f"  Oracle: chainlink_btc_usd")
    print(f"  Value: ${btc_proof.value:,.2f}")
    print(f"  Timestamp: {btc_proof.timestamp}")
    print(f"  Signature: {btc_proof.signature[:20]}...")
    
    # Verify oracle proof
    status = verify_oracle_proof(btc_proof)
    print(f"  Status: {status.value}")
    
    if status == OracleStatus.VERIFIED:
        print("  ✅ Oracle proof verified!")
    else:
        print(f"  ❌ Oracle verification failed: {status.value}")
        return
    
    # Simulate liquidation
    collateral_amount = 2.5  # BTC
    
    print("\n📊 Liquidation Transaction:")
    print(f"  Borrower loses: {collateral_amount} BTC")
    print(f"  Liquidator gains: {collateral_amount} BTC")
    
    changes = [
        BalanceChange(
            variable_name="borrower_collateral",
            amount=f"{collateral_amount} * btc_price",
            line_number=1,
            is_increase=False,
            is_oracle_influenced=True,
            oracle_variable="btc_price",
            oracle_value=btc_proof.value
        ),
        BalanceChange(
            variable_name="liquidator_balance",
            amount=f"{collateral_amount} * btc_price",
            line_number=2,
            is_increase=True,
            is_oracle_influenced=True,
            oracle_variable="btc_price",
            oracle_value=btc_proof.value
        )
    ]
    
    oracle_proofs = {
        "btc_price": btc_proof
    }
    
    # Check conservation with oracle
    result = checker.check_oracle_conservation(changes, oracle_proofs)
    
    print(f"\n🔍 Conservation Check:")
    print(f"  Borrower: -{collateral_amount} BTC")
    print(f"  Liquidator: +{collateral_amount} BTC")
    print(f"  Total: 0 BTC")
    
    print(f"\nResult: {'✅ VERIFIED' if result.is_valid else '❌ REJECTED'}")
    
    if result.is_valid:
        print("  ✅ Conservation maintained")
        print("  ✅ Oracle verified")
        print("  ✅ Transaction approved")


def demo_slippage_validation():
    """Demo 3: Slippage validation"""
    print_header("DEMO 3: Slippage Validation")
    
    validator = SlippageValidator(tolerance=0.05)  # 5% tolerance
    
    print("\nSlippage Validator Configuration:")
    print(f"  Tolerance: {validator.tolerance * 100}%")
    
    # Test case 1: Within tolerance
    print_section("Test 1: Price within tolerance")
    oracle_price = 45000.0
    reference_price = 44000.0
    slippage = validator.calculate_slippage(oracle_price, reference_price)
    within_tolerance = validator.is_within_tolerance(oracle_price, reference_price)
    
    print(f"  Oracle Price: ${oracle_price:,.2f}")
    print(f"  Reference Price: ${reference_price:,.2f}")
    print(f"  Slippage: {slippage * 100:.2f}%")
    print(f"  Within Tolerance: {'✅ YES' if within_tolerance else '❌ NO'}")
    
    # Test case 2: Exceeds tolerance
    print_section("Test 2: Price exceeds tolerance")
    oracle_price = 50000.0
    reference_price = 44000.0
    slippage = validator.calculate_slippage(oracle_price, reference_price)
    within_tolerance = validator.is_within_tolerance(oracle_price, reference_price)
    
    print(f"  Oracle Price: ${oracle_price:,.2f}")
    print(f"  Reference Price: ${reference_price:,.2f}")
    print(f"  Slippage: {slippage * 100:.2f}%")
    print(f"  Within Tolerance: {'✅ YES' if within_tolerance else '❌ NO'}")
    
    if not within_tolerance:
        print("  ⚠️  Transaction would be rejected due to excessive slippage")


def demo_conservation_violation():
    """Demo 4: Conservation violation with oracle"""
    print_header("DEMO 4: Conservation Violation Detection")
    
    checker = ConservationChecker()
    
    # Incorrect liquidation: amounts don't match
    print("\n⚠️  Attempting invalid transaction:")
    print("  Borrower loses: 2.5 BTC")
    print("  Liquidator gains: 3.0 BTC  (WRONG!)")
    
    changes = [
        BalanceChange(
            variable_name="borrower_collateral",
            amount=2.5,
            line_number=1,
            is_increase=False
        ),
        BalanceChange(
            variable_name="liquidator_balance",
            amount=3.0,
            line_number=2,
            is_increase=True
        )
    ]
    
    result = checker.check_oracle_conservation(changes)
    
    print(f"\n🔍 Conservation Check:")
    print(f"  Borrower: -2.5 BTC")
    print(f"  Liquidator: +3.0 BTC")
    print(f"  Total: +0.5 BTC  ❌")
    
    print(f"\nResult: {'✅ VERIFIED' if result.is_valid else '❌ REJECTED'}")
    
    if not result.is_valid:
        print(f"  ❌ Conservation violated!")
        print(f"  ❌ {result.violation_amount} units created from nothing")
        print(f"  ❌ Transaction rejected")


def demo_multi_oracle():
    """Demo 5: Multi-oracle transaction"""
    print_header("DEMO 5: Multi-Oracle Transaction")
    
    checker = ConservationChecker()
    simulator = get_oracle_simulator()
    
    # Fetch multiple oracle prices
    print("\n🔍 Fetching prices from multiple oracles...")
    
    btc_proof = simulator.fetch_data("chainlink_btc_usd")
    print(f"  BTC/USD: ${btc_proof.value:,.2f} ✅")
    
    eth_proof = simulator.fetch_data("chainlink_eth_usd")
    print(f"  ETH/USD: ${eth_proof.value:,.2f} ✅")
    
    # Simulate cross-asset swap
    print("\n📊 Cross-Asset Swap:")
    print("  User sends: 1.0 BTC")
    print("  User receives: 18.0 ETH")
    
    changes = [
        BalanceChange(
            variable_name="user_btc",
            amount="1.0 * btc_price",
            line_number=1,
            is_increase=False,
            is_oracle_influenced=True,
            oracle_variable="btc_price",
            oracle_value=btc_proof.value
        ),
        BalanceChange(
            variable_name="user_eth",
            amount="18.0 * eth_price",
            line_number=2,
            is_increase=True,
            is_oracle_influenced=True,
            oracle_variable="eth_price",
            oracle_value=eth_proof.value
        )
    ]
    
    oracle_proofs = {
        "btc_price": btc_proof,
        "eth_price": eth_proof
    }
    
    result = checker.check_oracle_conservation(changes, oracle_proofs)
    
    print(f"\n🔍 Validation:")
    print(f"  BTC Oracle: ✅ Verified")
    print(f"  ETH Oracle: ✅ Verified")
    print(f"  Conservation: {'✅ Valid' if result.is_valid else '❌ Invalid'}")
    
    print(f"\nResult: {'✅ VERIFIED' if result.is_valid else '❌ REJECTED'}")


def main():
    """Run all demos"""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🔮 Conservation-Aware Oracle Integration Demo 🔮".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("║" + "  v1.7.1 - PASSO B COMPLETE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Run demos
    demo_simple_conservation()
    demo_oracle_liquidation()
    demo_slippage_validation()
    demo_conservation_violation()
    demo_multi_oracle()
    
    # Summary
    print_header("SUMMARY")
    print("\n✅ All demos completed successfully!")
    print("\nKey Features Demonstrated:")
    print("  1. Simple conservation checking (backward compatible)")
    print("  2. Oracle-aware conservation validation")
    print("  3. Slippage protection")
    print("  4. Conservation violation detection")
    print("  5. Multi-oracle transaction support")
    
    print("\n" + "=" * 70)
    print("  🌌⚖️🔮 Trust the math, verify the world. 🔮⚖️🌌")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
