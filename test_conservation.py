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
Unit Tests for Conservation Checker v1.3

Tests the core functionality of the Conservation Checker:
- Balance change detection
- Conservation validation
- Error reporting
- Judge integration

Author: Diotec360 Team
Version: 1.3.0
Date: February 3, 2026
"""

import pytest
from diotec360.core.conservation import ConservationChecker, BalanceChange, ConservationResult


class TestBalanceChange:
    """Unit tests for BalanceChange data structure."""
    
    def test_signed_amount_increase(self):
        """Test signed amount for balance increase."""
        change = BalanceChange(
            variable_name="receiver_balance",
            amount=100,
            line_number=1,
            is_increase=True
        )
        assert change.to_signed_amount() == 100
    
    def test_signed_amount_decrease(self):
        """Test signed amount for balance decrease."""
        change = BalanceChange(
            variable_name="sender_balance",
            amount=100,
            line_number=1,
            is_increase=False
        )
        assert change.to_signed_amount() == -100
    
    def test_signed_amount_symbolic(self):
        """Test signed amount for symbolic expressions."""
        change = BalanceChange(
            variable_name="balance",
            amount="amount",
            line_number=1,
            is_increase=True
        )
        assert change.to_signed_amount() == "amount"
        
        change_decrease = BalanceChange(
            variable_name="balance",
            amount="amount",
            line_number=1,
            is_increase=False
        )
        assert change_decrease.to_signed_amount() == "-(amount)"


class TestConservationResult:
    """Unit tests for ConservationResult data structure."""
    
    def test_format_error_valid(self):
        """Test error formatting for valid conservation."""
        result = ConservationResult(is_valid=True, changes=[])
        assert result.format_error() == "Conservation check passed"
    
    def test_format_error_violation_created(self):
        """Test error formatting when money is created."""
        changes = [
            BalanceChange("sender", 100, 1, False),
            BalanceChange("receiver", 200, 2, True)
        ]
        result = ConservationResult(
            is_valid=False,
            changes=changes,
            violation_amount=100
        )
        error = result.format_error()
        assert "❌ FAILED: Conservation violation detected" in error
        assert "sender: -100" in error
        assert "receiver: +200" in error
        assert "100 units created from nothing" in error
    
    def test_format_error_violation_destroyed(self):
        """Test error formatting when money is destroyed."""
        changes = [
            BalanceChange("sender", 200, 1, False),
            BalanceChange("receiver", 100, 2, True)
        ]
        result = ConservationResult(
            is_valid=False,
            changes=changes,
            violation_amount=-100
        )
        error = result.format_error()
        assert "100 units destroyed" in error


class TestConservationChecker:
    """Unit tests for ConservationChecker class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.checker = ConservationChecker()
    
    def test_extract_balance_change_increase(self):
        """Test extracting balance increase."""
        condition = "receiver_balance == old_receiver_balance + 100"
        change = self.checker._extract_balance_change(condition, 1)
        
        assert change is not None
        assert change.variable_name == "receiver_balance"
        assert change.amount == 100
        assert change.is_increase is True
        assert change.line_number == 1
    
    def test_extract_balance_change_decrease(self):
        """Test extracting balance decrease."""
        condition = "sender_balance == old_sender_balance - 100"
        change = self.checker._extract_balance_change(condition, 1)
        
        assert change is not None
        assert change.variable_name == "sender_balance"
        assert change.amount == 100
        assert change.is_increase is False
        assert change.line_number == 1
    
    def test_extract_balance_change_symbolic(self):
        """Test extracting symbolic balance change."""
        condition = "balance == old_balance + amount"
        change = self.checker._extract_balance_change(condition, 1)
        
        assert change is not None
        assert change.variable_name == "balance"
        assert change.amount == "amount"
        assert change.is_increase is True
    
    def test_extract_balance_change_no_old_prefix(self):
        """Test that conditions without old_ prefix are ignored."""
        condition = "balance == balance + 100"
        change = self.checker._extract_balance_change(condition, 1)
        
        assert change is None
    
    def test_extract_balance_change_no_equality(self):
        """Test that conditions without == are ignored."""
        condition = "balance > old_balance"
        change = self.checker._extract_balance_change(condition, 1)
        
        assert change is None
    
    def test_analyze_verify_block_simple_transfer(self):
        """Test analyzing a simple two-party transfer."""
        verify_block = [
            "sender_balance == old_sender_balance - 100",
            "receiver_balance == old_receiver_balance + 100"
        ]
        
        changes = self.checker.analyze_verify_block(verify_block)
        
        assert len(changes) == 2
        assert changes[0].variable_name == "sender_balance"
        assert changes[0].amount == 100
        assert changes[0].is_increase is False
        assert changes[1].variable_name == "receiver_balance"
        assert changes[1].amount == 100
        assert changes[1].is_increase is True
    
    def test_analyze_verify_block_no_changes(self):
        """Test analyzing verify block with no balance changes."""
        verify_block = [
            "amount > 0",
            "balance >= 1000"
        ]
        
        changes = self.checker.analyze_verify_block(verify_block)
        
        assert len(changes) == 0
    
    def test_validate_conservation_balanced(self):
        """Test validation of balanced transaction."""
        changes = [
            BalanceChange("sender", 100, 1, False),
            BalanceChange("receiver", 100, 2, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is True
        assert len(result.changes) == 2
    
    def test_validate_conservation_unbalanced_created(self):
        """Test validation when money is created."""
        changes = [
            BalanceChange("sender", 100, 1, False),
            BalanceChange("receiver", 200, 2, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is False
        assert result.violation_amount == 100
    
    def test_validate_conservation_unbalanced_destroyed(self):
        """Test validation when money is destroyed."""
        changes = [
            BalanceChange("sender", 200, 1, False),
            BalanceChange("receiver", 100, 2, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is False
        assert result.violation_amount == -100
    
    def test_validate_conservation_multi_party(self):
        """Test validation of multi-party transaction."""
        changes = [
            BalanceChange("sender", 300, 1, False),
            BalanceChange("receiver1", 100, 2, True),
            BalanceChange("receiver2", 100, 3, True),
            BalanceChange("receiver3", 100, 4, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is True
    
    def test_validate_conservation_empty(self):
        """Test validation with no changes."""
        result = self.checker.validate_conservation([])
        
        assert result.is_valid is True
        assert len(result.changes) == 0
    
    def test_check_intent_valid_transfer(self):
        """Test full intent check for valid transfer."""
        intent_data = {
            'verify': [
                "sender_balance == old_sender_balance - 200",
                "receiver_balance == old_receiver_balance + 200"
            ]
        }
        
        result = self.checker.check_intent(intent_data)
        
        assert result.is_valid is True
        assert len(result.changes) == 2
    
    def test_check_intent_invalid_transfer(self):
        """Test full intent check for invalid transfer."""
        intent_data = {
            'verify': [
                "sender_balance == old_sender_balance - 100",
                "receiver_balance == old_receiver_balance + 200"
            ]
        }
        
        result = self.checker.check_intent(intent_data)
        
        assert result.is_valid is False
        assert result.violation_amount == 100
    
    def test_check_intent_no_verify_block(self):
        """Test intent check with no verify block."""
        intent_data = {}
        
        result = self.checker.check_intent(intent_data)
        
        assert result.is_valid is True
        assert len(result.changes) == 0
    
    def test_check_intent_no_balance_changes(self):
        """Test intent check with verify block but no balance changes."""
        intent_data = {
            'verify': [
                "amount > 0",
                "balance >= 1000"
            ]
        }
        
        result = self.checker.check_intent(intent_data)
        
        assert result.is_valid is True
        assert len(result.changes) == 0


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.checker = ConservationChecker()
    
    def test_floating_point_amounts(self):
        """Test with floating point amounts."""
        changes = [
            BalanceChange("sender", 100.5, 1, False),
            BalanceChange("receiver", 100.5, 2, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is True
    
    def test_zero_amount_transfer(self):
        """Test transfer with zero amount."""
        changes = [
            BalanceChange("sender", 0, 1, False),
            BalanceChange("receiver", 0, 2, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is True
    
    def test_single_account_increase(self):
        """Test single account increase (money creation)."""
        changes = [
            BalanceChange("account", 100, 1, True)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is False
        assert result.violation_amount == 100
    
    def test_single_account_decrease(self):
        """Test single account decrease (money destruction)."""
        changes = [
            BalanceChange("account", 100, 1, False)
        ]
        
        result = self.checker.validate_conservation(changes)
        
        assert result.is_valid is False
        assert result.violation_amount == -100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
