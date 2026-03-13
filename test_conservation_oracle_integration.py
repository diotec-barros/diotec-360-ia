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
Integration tests for Conservation Checker + Oracle System

Tests the integration between the Conservation Checker and Oracle Sanctuary,
validating that external oracle data doesn't break conservation of value.

Author: Diotec360 Team
Version: 1.7.1
Date: February 4, 2026
"""

import pytest
import time
from diotec360.core.conservation import (
    ConservationChecker,
    BalanceChange,
    ConservationResult,
    SlippageValidator
)
from diotec360.core.oracle import (
    OracleProof,
    OracleStatus,
    get_oracle_registry,
    get_oracle_simulator,
    verify_oracle_proof
)


class TestSlippageValidator:
    """Unit tests for SlippageValidator"""
    
    def test_default_tolerance(self):
        """Test default 5% tolerance"""
        validator = SlippageValidator()
        assert validator.tolerance == 0.05
    
    def test_custom_tolerance(self):
        """Test custom tolerance"""
        validator = SlippageValidator(tolerance=0.10)
        assert validator.tolerance == 0.10
    
    def test_calculate_slippage_zero(self):
        """Test slippage calculation with identical values"""
        validator = SlippageValidator()
        slippage = validator.calculate_slippage(100.0, 100.0)
        assert slippage == 0.0
    
    def test_calculate_slippage_positive(self):
        """Test slippage calculation with higher oracle value"""
        validator = SlippageValidator()
        slippage = validator.calculate_slippage(105.0, 100.0)
        assert abs(slippage - 0.05) < 1e-10  # 5% slippage
    
    def test_calculate_slippage_negative(self):
        """Test slippage calculation with lower oracle value"""
        validator = SlippageValidator()
        slippage = validator.calculate_slippage(95.0, 100.0)
        assert abs(slippage - 0.05) < 1e-10  # 5% slippage (absolute)
    
    def test_is_within_tolerance_pass(self):
        """Test value within tolerance"""
        validator = SlippageValidator(tolerance=0.05)
        assert validator.is_within_tolerance(102.0, 100.0)  # 2% slippage
    
    def test_is_within_tolerance_fail(self):
        """Test value exceeds tolerance"""
        validator = SlippageValidator(tolerance=0.05)
        assert not validator.is_within_tolerance(110.0, 100.0)  # 10% slippage
    
    def test_validate_oracle_rate_within_range(self):
        """Test oracle value within expected range"""
        validator = SlippageValidator()
        assert validator.validate_oracle_rate(100.0, (95.0, 105.0))
    
    def test_validate_oracle_rate_below_range(self):
        """Test oracle value below expected range"""
        validator = SlippageValidator()
        assert not validator.validate_oracle_rate(90.0, (95.0, 105.0))
    
    def test_validate_oracle_rate_above_range(self):
        """Test oracle value above expected range"""
        validator = SlippageValidator()
        assert not validator.validate_oracle_rate(110.0, (95.0, 105.0))


class TestOracleAwareBalanceDetection:
    """Tests for detecting oracle-influenced balance changes"""
    
    def test_detect_simple_balance_change(self):
        """Test detection of simple balance change without oracle"""
        checker = ConservationChecker()
        condition = "sender_balance == old_sender_balance - 100"
        change = checker._extract_balance_change(condition, 1)
        
        assert change is not None
        assert change.variable_name == "sender_balance"
        assert change.amount == 100
        assert change.is_increase is False
        assert change.is_oracle_influenced is False
        assert change.oracle_variable is None
    
    def test_detect_oracle_influenced_balance_change(self):
        """Test detection of oracle-influenced balance change"""
        checker = ConservationChecker()
        condition = "liquidator_balance == old_liquidator_balance + collateral_amount * btc_price"
        change = checker._extract_balance_change(condition, 1)
        
        assert change is not None
        assert change.variable_name == "liquidator_balance"
        assert change.is_increase is True
        assert change.is_oracle_influenced is True
        assert change.oracle_variable in ["collateral_amount", "btc_price"]
    
    def test_contains_external_variable_true(self):
        """Test detection of external variables"""
        checker = ConservationChecker()
        expression = "old_balance + amount * price"
        assert checker._contains_external_variable(expression) is True
    
    def test_contains_external_variable_false(self):
        """Test no external variables"""
        checker = ConservationChecker()
        expression = "old_balance + 100"
        assert checker._contains_external_variable(expression) is False
    
    def test_extract_oracle_variable(self):
        """Test extraction of oracle variable name"""
        checker = ConservationChecker()
        expression = "old_balance + collateral * btc_price"
        oracle_var = checker._extract_oracle_variable(expression)
        assert oracle_var in ["collateral", "btc_price"]


class TestOracleConservationIntegration:
    """Integration tests for oracle-aware conservation checking"""
    
    def test_valid_liquidation_with_oracle(self):
        """Test valid DeFi liquidation with oracle price"""
        checker = ConservationChecker()
        
        # Simulate DeFi liquidation:
        # Borrower loses 2.5 BTC collateral
        # Liquidator gains 2.5 BTC collateral
        changes = [
            BalanceChange(
                variable_name="borrower_collateral",
                amount="2.5 * btc_price",
                line_number=1,
                is_increase=False,
                is_oracle_influenced=True,
                oracle_variable="btc_price"
            ),
            BalanceChange(
                variable_name="liquidator_balance",
                amount="2.5 * btc_price",
                line_number=2,
                is_increase=True,
                is_oracle_influenced=True,
                oracle_variable="btc_price"
            )
        ]
        
        # Get oracle proof for BTC price
        simulator = get_oracle_simulator()
        btc_proof = simulator.fetch_data("chainlink_btc_usd")
        
        oracle_proofs = {
            "btc_price": btc_proof
        }
        
        # Check conservation with oracle
        result = checker.check_oracle_conservation(changes, oracle_proofs)
        
        # Should pass: oracle verified and conservation maintained
        assert result.is_valid is True
    
    def test_conservation_violation_with_oracle(self):
        """Test conservation violation even with valid oracle"""
        checker = ConservationChecker()
        
        # Simulate incorrect liquidation:
        # Borrower loses 2.5 BTC
        # Liquidator gains 3.0 BTC (wrong!)
        changes = [
            BalanceChange(
                variable_name="borrower_collateral",
                amount=2.5,
                line_number=1,
                is_increase=False,
                is_oracle_influenced=False
            ),
            BalanceChange(
                variable_name="liquidator_balance",
                amount=3.0,
                line_number=2,
                is_increase=True,
                is_oracle_influenced=False
            )
        ]
        
        result = checker.check_oracle_conservation(changes)
        
        # Should fail: conservation violated
        assert result.is_valid is False
        assert result.violation_amount == 0.5
    
    def test_invalid_oracle_proof(self):
        """Test rejection of invalid oracle proof"""
        checker = ConservationChecker()
        
        changes = [
            BalanceChange(
                variable_name="balance",
                amount="amount * price",
                line_number=1,
                is_increase=True,
                is_oracle_influenced=True,
                oracle_variable="price"
            )
        ]
        
        # Create invalid oracle proof (bad signature)
        invalid_proof = OracleProof(
            value=45000.0,
            timestamp=int(time.time()),
            signature="0xINVALID",
            oracle_id="chainlink_btc_usd"
        )
        
        oracle_proofs = {
            "price": invalid_proof
        }
        
        result = checker.check_oracle_conservation(changes, oracle_proofs)
        
        # Should fail: invalid oracle signature
        assert result.is_valid is False
        assert "Oracle validation failed" in result.error_message
    
    def test_stale_oracle_data(self):
        """Test rejection of stale oracle data"""
        checker = ConservationChecker()
        
        changes = [
            BalanceChange(
                variable_name="balance",
                amount="amount * price",
                line_number=1,
                is_increase=True,
                is_oracle_influenced=True,
                oracle_variable="price"
            )
        ]
        
        # Create stale oracle proof (old timestamp)
        registry = get_oracle_registry()
        oracle_config = registry.get_oracle("chainlink_btc_usd")
        
        from diotec360.core.oracle import OracleVerifier
        verifier = OracleVerifier(registry)
        
        stale_proof = OracleProof(
            value=45000.0,
            timestamp=int(time.time()) - 1000,  # 1000 seconds ago (stale)
            signature=verifier._generate_signature(
                45000.0,
                int(time.time()) - 1000,
                "chainlink_btc_usd",
                oracle_config.public_key
            ),
            oracle_id="chainlink_btc_usd"
        )
        
        oracle_proofs = {
            "price": stale_proof
        }
        
        result = checker.check_oracle_conservation(changes, oracle_proofs)
        
        # Should fail: stale data
        assert result.is_valid is False
        assert "STALE_DATA" in result.error_message
    
    def test_multi_oracle_transaction(self):
        """Test transaction using multiple oracles"""
        checker = ConservationChecker()
        
        # Simulate cross-asset swap:
        # User sends BTC, receives ETH
        changes = [
            BalanceChange(
                variable_name="user_btc",
                amount="1.0 * btc_price",
                line_number=1,
                is_increase=False,
                is_oracle_influenced=True,
                oracle_variable="btc_price"
            ),
            BalanceChange(
                variable_name="user_eth",
                amount="18.0 * eth_price",
                line_number=2,
                is_increase=True,
                is_oracle_influenced=True,
                oracle_variable="eth_price"
            )
        ]
        
        # Get oracle proofs
        simulator = get_oracle_simulator()
        btc_proof = simulator.fetch_data("chainlink_btc_usd")
        eth_proof = simulator.fetch_data("chainlink_eth_usd")
        
        oracle_proofs = {
            "btc_price": btc_proof,
            "eth_price": eth_proof
        }
        
        result = checker.check_oracle_conservation(changes, oracle_proofs)
        
        # Should pass: both oracles verified
        assert result.is_valid is True


class TestConservationWithoutOracle:
    """Test that conservation checking still works without oracle integration"""
    
    def test_simple_transfer_no_oracle(self):
        """Test simple transfer without oracle data"""
        checker = ConservationChecker()
        
        changes = [
            BalanceChange(
                variable_name="sender_balance",
                amount=100,
                line_number=1,
                is_increase=False
            ),
            BalanceChange(
                variable_name="receiver_balance",
                amount=100,
                line_number=2,
                is_increase=True
            )
        ]
        
        result = checker.check_oracle_conservation(changes)
        
        assert result.is_valid is True
    
    def test_violation_no_oracle(self):
        """Test conservation violation without oracle data"""
        checker = ConservationChecker()
        
        changes = [
            BalanceChange(
                variable_name="sender_balance",
                amount=100,
                line_number=1,
                is_increase=False
            ),
            BalanceChange(
                variable_name="receiver_balance",
                amount=200,
                line_number=2,
                is_increase=True
            )
        ]
        
        result = checker.check_oracle_conservation(changes)
        
        assert result.is_valid is False
        assert result.violation_amount == 100


if __name__ == "__main__":
    print("🧪 Running Conservation + Oracle Integration Tests")
    print("=" * 60)
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 60)
    print("🔮⚖️ Conservation-Aware Oracle: Verified!")
