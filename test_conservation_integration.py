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
Integration Tests for Conservation Checker v1.3

Tests the full integration with the Judge system:
- End-to-end verification flow
- Conservation check before Z3
- Error propagation
- Real-world scenarios

Author: Diotec360 Team
Version: 1.3.0
Date: February 3, 2026
"""

import pytest
from diotec360.core.judge import DIOTEC360Judge


class TestConservationIntegration:
    """Integration tests for Conservation Checker with Judge."""
    
    def test_valid_transfer_passes_conservation_and_z3(self):
        """Test that valid transfer passes both conservation and Z3 checks."""
        intent_map = {
            'secure_transfer': {
                'params': ['sender', 'receiver', 'amount'],
                'constraints': [
                    'old_sender_balance >= amount',
                    'amount > 0'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - amount',
                    'receiver_balance == old_receiver_balance + amount'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('secure_transfer')
        
        assert result['status'] == 'PROVED'
        assert 'matematicamente seguro' in result['message'].lower()
    
    def test_conservation_violation_fails_before_z3(self):
        """Test that conservation violation is caught before Z3 is called."""
        intent_map = {
            'money_printer': {
                'params': ['sender', 'receiver', 'amount'],
                'constraints': [
                    'amount > 0'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 100',
                    'receiver_balance == old_receiver_balance + 200'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('money_printer')
        
        assert result['status'] == 'FAILED'
        assert 'Conservation violation detected' in result['message']
        assert '100 units created from nothing' in result['message']
    
    def test_money_destruction_detected(self):
        """Test that money destruction is detected."""
        intent_map = {
            'money_destroyer': {
                'params': ['sender', 'receiver', 'amount'],
                'constraints': [
                    'amount > 0'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 200',
                    'receiver_balance == old_receiver_balance + 100'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('money_destroyer')
        
        assert result['status'] == 'FAILED'
        assert 'Conservation violation detected' in result['message']
        assert '100 units destroyed' in result['message']
    
    def test_multi_party_transfer_valid(self):
        """Test valid multi-party transfer (split payment)."""
        intent_map = {
            'split_payment': {
                'params': ['sender', 'receiver1', 'receiver2', 'receiver3'],
                'constraints': [
                    'old_sender_balance >= 300'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 300',
                    'receiver1_balance == old_receiver1_balance + 100',
                    'receiver2_balance == old_receiver2_balance + 100',
                    'receiver3_balance == old_receiver3_balance + 100'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('split_payment')
        
        assert result['status'] == 'PROVED'
    
    def test_multi_party_transfer_invalid(self):
        """Test invalid multi-party transfer (unbalanced split)."""
        intent_map = {
            'unbalanced_split': {
                'params': ['sender', 'receiver1', 'receiver2'],
                'constraints': [
                    'old_sender_balance >= 200'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 200',
                    'receiver1_balance == old_receiver1_balance + 100',
                    'receiver2_balance == old_receiver2_balance + 150'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('unbalanced_split')
        
        assert result['status'] == 'FAILED'
        assert 'Conservation violation detected' in result['message']
    
    def test_no_balance_changes_skips_conservation(self):
        """Test that intents without balance changes skip conservation check."""
        intent_map = {
            'simple_check': {
                'params': ['amount', 'balance'],
                'constraints': [
                    'amount > 0',
                    'balance >= 1000'
                ],
                'post_conditions': [
                    'amount > 0',
                    'balance >= amount'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('simple_check')
        
        # Should proceed to Z3 verification
        assert result['status'] in ['PROVED', 'FAILED']  # Depends on Z3 result
    
    def test_single_account_increase_fails(self):
        """Test that single account increase (money creation) fails."""
        intent_map = {
            'create_money': {
                'params': ['account'],
                'constraints': [],
                'post_conditions': [
                    'account_balance == old_account_balance + 1000'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('create_money')
        
        assert result['status'] == 'FAILED'
        assert 'Conservation violation detected' in result['message']
        assert '1000 units created from nothing' in result['message']
    
    def test_zero_amount_transfer_passes(self):
        """Test that zero amount transfer passes conservation."""
        intent_map = {
            'zero_transfer': {
                'params': ['sender', 'receiver'],
                'constraints': [],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 0',
                    'receiver_balance == old_receiver_balance + 0'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('zero_transfer')
        
        assert result['status'] == 'PROVED'


class TestRealWorldScenarios:
    """Test real-world financial scenarios."""
    
    def test_bank_transfer_with_fee(self):
        """Test bank transfer with fee (3-party transaction)."""
        intent_map = {
            'transfer_with_fee': {
                'params': ['sender', 'receiver', 'bank', 'amount', 'fee'],
                'constraints': [
                    'old_sender_balance >= amount',
                    'amount > 0',
                    'fee > 0'
                ],
                'post_conditions': [
                    'sender_balance == old_sender_balance - amount',
                    'receiver_balance == old_receiver_balance + amount - fee',
                    'bank_balance == old_bank_balance + fee'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('transfer_with_fee')
        
        assert result['status'] == 'PROVED'
    
    def test_consolidation_payment(self):
        """Test consolidation payment (multiple senders, one receiver)."""
        intent_map = {
            'consolidate': {
                'params': ['sender1', 'sender2', 'sender3', 'receiver'],
                'constraints': [
                    'old_sender1_balance >= 100',
                    'old_sender2_balance >= 100',
                    'old_sender3_balance >= 100'
                ],
                'post_conditions': [
                    'sender1_balance == old_sender1_balance - 100',
                    'sender2_balance == old_sender2_balance - 100',
                    'sender3_balance == old_sender3_balance - 100',
                    'receiver_balance == old_receiver_balance + 300'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('consolidate')
        
        assert result['status'] == 'PROVED'
    
    def test_escrow_release(self):
        """Test escrow release (3-party with conservation)."""
        intent_map = {
            'escrow_release': {
                'params': ['escrow', 'buyer', 'seller', 'amount'],
                'constraints': [
                    'old_escrow_balance >= amount',
                    'amount > 0'
                ],
                'post_conditions': [
                    'escrow_balance == old_escrow_balance - amount',
                    'seller_balance == old_seller_balance + amount',
                    'buyer_balance == old_buyer_balance'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('escrow_release')
        
        assert result['status'] == 'PROVED'


class TestErrorMessages:
    """Test error message quality and clarity."""
    
    def test_error_message_includes_all_changes(self):
        """Test that error message lists all balance changes."""
        intent_map = {
            'complex_violation': {
                'params': ['a', 'b', 'c'],
                'constraints': [],
                'post_conditions': [
                    'a_balance == old_a_balance - 100',
                    'b_balance == old_b_balance + 50',
                    'c_balance == old_c_balance + 100'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('complex_violation')
        
        assert result['status'] == 'FAILED'
        message = result['message']
        assert 'a_balance: -100' in message
        assert 'b_balance: +50' in message
        assert 'c_balance: +100' in message
        assert '50 units created from nothing' in message
    
    def test_error_message_includes_hint(self):
        """Test that error message includes helpful hint."""
        intent_map = {
            'simple_violation': {
                'params': ['sender', 'receiver'],
                'constraints': [],
                'post_conditions': [
                    'sender_balance == old_sender_balance - 100',
                    'receiver_balance == old_receiver_balance + 200'
                ]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic('simple_violation')
        
        assert 'Hint:' in result['message']
        assert 'sum of all balance' in result['message']
        assert 'must equal zero' in result['message']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
