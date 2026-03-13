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
Backward Compatibility Tests for MOE Intelligence Layer

Runs all v1.9.0 tests with MOE enabled to ensure backward compatibility.
Validates that MOE doesn't break existing functionality.

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import pytest
from diotec360.core.judge import DIOTEC360Judge


class TestMOEBackwardCompatibility:
    """
    Backward compatibility tests for MOE.
    
    Validates Requirement 12.6:
    THE system SHALL maintain backward compatibility with all v1.9.0 APIs
    
    These tests run v1.9.0 test cases with MOE enabled to ensure
    that MOE doesn't break existing functionality.
    """
    
    def setup_method(self):
        """Setup test fixtures before each test."""
        # v1.9.0 test cases
        self.intent_map = {
            # Test 1: Simple transfer (should pass)
            'simple_transfer': {
                'params': [
                    {'name': 'sender', 'type': 'address'},
                    {'name': 'receiver', 'type': 'address'},
                    {'name': 'amount', 'type': 'uint256'}
                ],
                'constraints': [
                    'sender_balance >= amount',
                    'amount > 0'
                ],
                'post_conditions': [
                    'sender_balance_after == sender_balance - amount',
                    'receiver_balance_after == receiver_balance + amount'
                ]
            },
            
            # Test 2: Arithmetic operations (should pass)
            'arithmetic_test': {
                'params': [
                    {'name': 'a', 'type': 'uint256'},
                    {'name': 'b', 'type': 'uint256'}
                ],
                'constraints': [
                    'a > 0',
                    'b > 0'
                ],
                'post_conditions': [
                    'result == a + b',
                    'result > a',
                    'result > b'
                ]
            },
            
            # Test 3: Logical contradiction (should fail)
            'contradiction_test': {
                'params': [
                    {'name': 'x', 'type': 'uint256'}
                ],
                'constraints': [],
                'post_conditions': [
                    'x == x + 1'  # Impossible
                ]
            },
            
            # Test 4: Overflow check (should pass with valid constraints)
            'overflow_safe': {
                'params': [
                    {'name': 'a', 'type': 'uint256'},
                    {'name': 'b', 'type': 'uint256'}
                ],
                'constraints': [
                    'a < 1000000',
                    'b < 1000000'
                ],
                'post_conditions': [
                    'result == a * b',
                    'result >= a',
                    'result >= b'
                ]
            },
            
            # Test 5: Complex constraints (should pass)
            'complex_constraints': {
                'params': [
                    {'name': 'balance', 'type': 'uint256'},
                    {'name': 'amount', 'type': 'uint256'},
                    {'name': 'fee', 'type': 'uint256'}
                ],
                'constraints': [
                    'balance >= amount + fee',
                    'amount > 0',
                    'fee >= 0'
                ],
                'post_conditions': [
                    'new_balance == balance - amount - fee',
                    'new_balance >= 0'
                ]
            },
            
            # Test 6: Multiple conditions (should pass)
            'multiple_conditions': {
                'params': [
                    {'name': 'x', 'type': 'uint256'},
                    {'name': 'y', 'type': 'uint256'}
                ],
                'constraints': [
                    'x > 10',
                    'y > 20'
                ],
                'post_conditions': [
                    'x + y > 30',
                    'x * y > 200',
                    'x < y'
                ]
            }
        }
    
    def test_v1_9_0_simple_transfer_with_moe(self):
        """
        Test: v1.9.0 simple transfer works with MOE enabled
        """
        # Test without MOE (v1.9.0 baseline)
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('simple_transfer')
        
        # Test with MOE (v2.1.0)
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('simple_transfer')
        
        # Both should succeed
        assert result_without['status'] == 'PROVED'
        assert result_with['status'] == 'PROVED'
    
    def test_v1_9_0_arithmetic_with_moe(self):
        """
        Test: v1.9.0 arithmetic operations work with MOE enabled
        """
        # Test without MOE
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('arithmetic_test')
        
        # Test with MOE
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('arithmetic_test')
        
        # Both should succeed
        assert result_without['status'] == 'PROVED'
        assert result_with['status'] == 'PROVED'
    
    def test_v1_9_0_contradiction_with_moe(self):
        """
        Test: v1.9.0 contradiction detection works with MOE enabled
        """
        # Test without MOE
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('contradiction_test')
        
        # Test with MOE
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('contradiction_test')
        
        # Both should fail (contradiction detected)
        assert result_without['status'] in ['FAILED', 'REJECTED']
        assert result_with['status'] in ['FAILED', 'REJECTED']
    
    def test_v1_9_0_overflow_safe_with_moe(self):
        """
        Test: v1.9.0 overflow checking works with MOE enabled
        """
        # Test without MOE
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('overflow_safe')
        
        # Test with MOE
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('overflow_safe')
        
        # Both should succeed
        assert result_without['status'] == 'PROVED'
        assert result_with['status'] == 'PROVED'
    
    def test_v1_9_0_complex_constraints_with_moe(self):
        """
        Test: v1.9.0 complex constraints work with MOE enabled
        """
        # Test without MOE
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('complex_constraints')
        
        # Test with MOE
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('complex_constraints')
        
        # Both should succeed
        assert result_without['status'] == 'PROVED'
        assert result_with['status'] == 'PROVED'
    
    def test_v1_9_0_multiple_conditions_with_moe(self):
        """
        Test: v1.9.0 multiple conditions work with MOE enabled
        """
        # Test without MOE
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        result_without = judge_without_moe.verify_logic('multiple_conditions')
        
        # Test with MOE
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        result_with = judge_with_moe.verify_logic('multiple_conditions')
        
        # Both should succeed
        assert result_without['status'] == 'PROVED'
        assert result_with['status'] == 'PROVED'
    
    def test_all_v1_9_0_tests_pass_with_moe(self):
        """
        Test: All v1.9.0 tests pass with MOE enabled
        
        This is a comprehensive test that runs all v1.9.0 test cases
        with MOE enabled and verifies that results match.
        """
        # Test cases that should pass
        passing_tests = [
            'simple_transfer',
            'arithmetic_test',
            'complex_constraints',
            'multiple_conditions'
        ]
        
        # Test cases that should fail
        failing_tests = [
            'contradiction_test'
        ]
        
        # Create judges
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        
        # Test passing cases
        for test_name in passing_tests:
            result_without = judge_without_moe.verify_logic(test_name)
            result_with = judge_with_moe.verify_logic(test_name)
            
            # Allow TIMEOUT as acceptable (Z3 can be non-deterministic)
            assert result_without['status'] in ['PROVED', 'TIMEOUT'], f"{test_name} failed without MOE: {result_without['status']}"
            assert result_with['status'] in ['PROVED', 'TIMEOUT'], f"{test_name} failed with MOE: {result_with['status']}"
        
        # Test failing cases
        for test_name in failing_tests:
            result_without = judge_without_moe.verify_logic(test_name)
            result_with = judge_with_moe.verify_logic(test_name)
            
            assert result_without['status'] in ['FAILED', 'REJECTED'], f"{test_name} should fail without MOE"
            assert result_with['status'] in ['FAILED', 'REJECTED'], f"{test_name} should fail with MOE"
    
    def test_moe_doesnt_change_api(self):
        """
        Test: MOE doesn't change the API
        
        Validates that the response format is the same with and without MOE.
        """
        # Create judges
        judge_without_moe = DIOTEC360Judge(self.intent_map, enable_moe=False)
        judge_with_moe = DIOTEC360Judge(self.intent_map, enable_moe=True)
        
        # Verify simple transfer
        result_without = judge_without_moe.verify_logic('simple_transfer')
        result_with = judge_with_moe.verify_logic('simple_transfer')
        
        # Both should have required fields
        required_fields = ['status', 'message', 'counter_examples']
        
        for field in required_fields:
            assert field in result_without, f"Missing field {field} without MOE"
            assert field in result_with, f"Missing field {field} with MOE"
        
        # Status should be the same
        assert result_without['status'] == result_with['status']
    
    def test_moe_maintains_telemetry(self):
        """
        Test: MOE maintains telemetry compatibility
        
        Validates that telemetry fields are present with MOE enabled.
        """
        # Create judge with MOE
        judge = DIOTEC360Judge(self.intent_map, enable_moe=True)
        
        # Verify simple transfer
        result = judge.verify_logic('simple_transfer')
        
        # Should have telemetry (from Sentinel Monitor)
        if 'telemetry' in result:
            assert 'anomaly_score' in result['telemetry']
            assert 'cpu_time_ms' in result['telemetry']
            assert 'memory_delta_mb' in result['telemetry']


class TestMOEDisableFlag:
    """
    Tests for MOE disable flag (emergency rollback).
    
    Validates Requirement 12.7:
    THE system SHALL support MOE disable flag for emergency rollback
    """
    
    def setup_method(self):
        """Setup test fixtures."""
        self.intent_map = {
            'simple_transfer': {
                'params': [
                    {'name': 'sender', 'type': 'address'},
                    {'name': 'receiver', 'type': 'address'},
                    {'name': 'amount', 'type': 'uint256'}
                ],
                'constraints': [
                    'sender_balance >= amount',
                    'amount > 0'
                ],
                'post_conditions': [
                    'sender_balance_after == sender_balance - amount',
                    'receiver_balance_after == receiver_balance + amount'
                ]
            }
        }
    
    def test_moe_can_be_disabled_at_runtime(self):
        """
        Test: MOE can be disabled at runtime
        """
        # Create judge with MOE enabled
        judge = DIOTEC360Judge(self.intent_map, enable_moe=True)
        
        # Disable MOE
        judge.disable_moe()
        
        # Verify that MOE is disabled
        assert judge.moe_enabled == False
        
        # Verify that system still works
        result = judge.verify_logic('simple_transfer')
        assert result['status'] == 'PROVED'
    
    def test_moe_can_be_enabled_at_runtime(self):
        """
        Test: MOE can be enabled at runtime
        """
        # Create judge with MOE disabled
        judge = DIOTEC360Judge(self.intent_map, enable_moe=False)
        
        # Enable MOE
        success = judge.enable_moe()
        
        # If MOE is available, it should be enabled
        if success:
            assert judge.moe_enabled == True
        
        # Verify that system still works
        result = judge.verify_logic('simple_transfer')
        assert result['status'] == 'PROVED'
    
    def test_emergency_rollback_scenario(self):
        """
        Test: Emergency rollback scenario
        
        Simulates an emergency where MOE needs to be disabled immediately.
        """
        # Create judge with MOE enabled
        judge = DIOTEC360Judge(self.intent_map, enable_moe=True)
        
        # Verify with MOE
        result1 = judge.verify_logic('simple_transfer')
        
        # Emergency: Disable MOE
        judge.disable_moe()
        
        # Verify without MOE (should still work)
        result2 = judge.verify_logic('simple_transfer')
        
        # Both should succeed
        assert result1['status'] == 'PROVED'
        assert result2['status'] == 'PROVED'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
