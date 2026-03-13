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
Property-Based Tests for Autonomous Sentinel Backward Compatibility

Tests that v1.9.0 Autonomous Sentinel maintains backward compatibility
with v1.8.0 Synchrony Protocol test suite.

Author: Diotec360 Team
Version: 1.9.0
Date: February 5, 2026
"""

import pytest
from hypothesis import given, strategies as st, settings
import time
from diotec360.core.synchrony import Transaction, BatchResult
from diotec360.core.batch_processor import BatchProcessor


# ============================================================================
# STRATEGIES
# ============================================================================

@st.composite
def v180_transaction_strategy(draw):
    """Generate random Transaction objects compatible with v1.8.0"""
    tx_id = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    intent_name = draw(st.sampled_from(['transfer', 'check_balance', 'deposit', 'withdraw', 'swap']))
    
    # Generate accounts
    num_accounts = draw(st.integers(min_value=0, max_value=5))
    accounts = {}
    for i in range(num_accounts):
        account_id = f"account_{i}"
        balance = draw(st.integers(min_value=0, max_value=10000))
        accounts[account_id] = {"balance": balance}
    
    # Generate operations
    num_operations = draw(st.integers(min_value=0, max_value=10))
    operations = []
    for _ in range(num_operations):
        op_type = draw(st.sampled_from(['debit', 'credit', 'check']))
        if accounts:
            account = draw(st.sampled_from(list(accounts.keys())))
            amount = draw(st.integers(min_value=1, max_value=100))
            operations.append({
                "type": op_type,
                "account": account,
                "amount": amount
            })
    
    # Generate verify conditions
    num_conditions = draw(st.integers(min_value=0, max_value=3))
    verify_conditions = []
    for _ in range(num_conditions):
        if accounts:
            account = draw(st.sampled_from(list(accounts.keys())))
            verify_conditions.append(f"{account}.balance >= 0")
    
    return Transaction(
        id=tx_id,
        intent_name=intent_name,
        accounts=accounts,
        operations=operations,
        verify_conditions=verify_conditions
    )


@st.composite
def v180_batch_strategy(draw):
    """Generate random batch of transactions compatible with v1.8.0"""
    batch_size = draw(st.integers(min_value=1, max_value=20))
    transactions = []
    
    for i in range(batch_size):
        tx = draw(v180_transaction_strategy())
        # Ensure unique IDs
        tx.id = f"{tx.id}_{i}"
        transactions.append(tx)
    
    return transactions


# ============================================================================
# PROPERTY 49: BACKWARD COMPATIBILITY
# ============================================================================

@settings(max_examples=100, deadline=10000)
@given(tx=v180_transaction_strategy())
def test_property_49_backward_compatibility_single_transaction(tx):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7
    
    Property: For any test case from the v1.8.0 Synchrony Protocol test suite,
    it should pass without modification when run against v1.9.0.
    
    This test verifies that single transaction execution from v1.8.0
    continues to work identically in v1.9.0 with Autonomous Sentinel enabled.
    """
    processor = BatchProcessor()
    
    # Execute transaction (should work exactly as in v1.8.0)
    result = processor.execute_single_transaction(tx)
    
    # Verify v1.8.0 API contract is preserved
    assert isinstance(result, BatchResult), \
        "Result must be BatchResult instance (v1.8.0 compatibility)"
    
    # Verify all v1.8.0 fields are present
    required_fields = [
        'success',
        'transactions_executed',
        'transactions_parallel',
        'execution_time',
        'throughput_improvement'
    ]
    
    for field in required_fields:
        assert hasattr(result, field), \
            f"Result must have '{field}' field (v1.8.0 compatibility)"
    
    # Verify field types match v1.8.0
    assert isinstance(result.success, bool), \
        "success must be bool (v1.8.0 compatibility)"
    
    assert isinstance(result.transactions_executed, int), \
        "transactions_executed must be int (v1.8.0 compatibility)"
    
    assert isinstance(result.transactions_parallel, int), \
        "transactions_parallel must be int (v1.8.0 compatibility)"
    
    assert isinstance(result.execution_time, float), \
        "execution_time must be float (v1.8.0 compatibility)"
    
    assert isinstance(result.throughput_improvement, float), \
        "throughput_improvement must be float (v1.8.0 compatibility)"
    
    # Verify value constraints from v1.8.0
    assert result.transactions_executed >= 0, \
        "transactions_executed must be non-negative"
    
    assert result.transactions_parallel >= 0, \
        "transactions_parallel must be non-negative"
    
    assert result.execution_time >= 0, \
        "execution_time must be non-negative"
    
    assert result.throughput_improvement >= 0, \
        "throughput_improvement must be non-negative"


@settings(max_examples=50, deadline=15000)
@given(batch=v180_batch_strategy())
def test_property_49_backward_compatibility_batch_execution(batch):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7
    
    Property: For any batch execution from v1.8.0, the result structure
    and behavior should be identical in v1.9.0.
    
    This test verifies that batch processing from v1.8.0 continues
    to work with the same API and semantics in v1.9.0.
    """
    processor = BatchProcessor()
    
    # Execute batch (should work exactly as in v1.8.0)
    result = processor.execute_batch(batch)
    
    # Verify v1.8.0 API contract
    assert isinstance(result, BatchResult), \
        "Result must be BatchResult instance"
    
    # Verify all required fields exist
    assert hasattr(result, 'success')
    assert hasattr(result, 'transactions_executed')
    assert hasattr(result, 'transactions_parallel')
    assert hasattr(result, 'execution_time')
    assert hasattr(result, 'throughput_improvement')
    
    # Verify execution count matches batch size (if successful)
    if result.success:
        assert result.transactions_executed == len(batch), \
            f"Should execute all {len(batch)} transactions"
    
    # Verify execution time is recorded
    assert result.execution_time > 0, \
        "Execution time must be recorded"
    
    # Verify throughput improvement is calculated
    assert result.throughput_improvement >= 0, \
        "Throughput improvement must be non-negative"


@settings(max_examples=50, deadline=10000)
@given(
    tx1=v180_transaction_strategy(),
    tx2=v180_transaction_strategy()
)
def test_property_49_backward_compatibility_determinism(tx1, tx2):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7
    
    Property: Deterministic execution from v1.8.0 is preserved in v1.9.0.
    
    Executing the same transaction multiple times should produce
    the same success/failure result, maintaining v1.8.0 determinism.
    """
    processor = BatchProcessor()
    
    # Ensure unique IDs
    tx1.id = f"tx1_{tx1.id}"
    tx2.id = f"tx2_{tx2.id}"
    
    # Execute tx1 twice
    result1_a = processor.execute_single_transaction(tx1)
    result1_b = processor.execute_single_transaction(tx1)
    
    # Results should be deterministic
    assert result1_a.success == result1_b.success, \
        "Execution should be deterministic (v1.8.0 guarantee)"
    
    assert result1_a.transactions_executed == result1_b.transactions_executed, \
        "Transaction count should be deterministic"


@settings(max_examples=30, deadline=10000)
@given(batch=v180_batch_strategy())
def test_property_49_backward_compatibility_no_exceptions(batch):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7
    
    Property: v1.8.0 error handling is preserved - no unexpected exceptions.
    
    All errors should be returned in the result structure, not raised
    as exceptions (v1.8.0 behavior).
    """
    processor = BatchProcessor()
    
    # Should not raise exceptions (v1.8.0 behavior)
    try:
        result = processor.execute_batch(batch)
        
        # Result should always be returned
        assert isinstance(result, BatchResult), \
            "Result must be returned even on errors (v1.8.0 behavior)"
        
        # Success field indicates outcome
        assert isinstance(result.success, bool), \
            "Success field must indicate outcome"
        
    except Exception as e:
        # If an exception is raised, it violates v1.8.0 contract
        pytest.fail(f"Unexpected exception raised (violates v1.8.0 contract): {e}")


@settings(max_examples=30, deadline=10000)
@given(tx=v180_transaction_strategy())
def test_property_49_backward_compatibility_transaction_id_preservation(tx):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7
    
    Property: Transaction IDs are preserved through execution (v1.8.0 guarantee).
    
    Transaction tracking and debugging capabilities from v1.8.0 must be maintained.
    """
    processor = BatchProcessor()
    
    # Store original ID
    original_id = tx.id
    
    # Execute transaction
    result = processor.execute_single_transaction(tx)
    
    # Transaction ID should be unchanged
    assert tx.id == original_id, \
        "Transaction ID must not be modified (v1.8.0 guarantee)"
    
    # If successful, should have executed 1 transaction
    if result.success:
        assert result.transactions_executed == 1, \
            "Should execute exactly 1 transaction"


@settings(max_examples=30, deadline=10000)
@given(batch=v180_batch_strategy())
def test_property_49_backward_compatibility_execution_time_bounds(batch):
    """
    Feature: autonomous-sentinel, Property 49: Backward compatibility
    
    Validates: Requirements 9.7, 10.8
    
    Property: Execution time characteristics from v1.8.0 are preserved.
    
    Transactions should complete within reasonable time bounds,
    maintaining v1.8.0 performance characteristics.
    """
    processor = BatchProcessor()
    
    # Execute batch
    start_time = time.time()
    result = processor.execute_batch(batch)
    wall_time = time.time() - start_time
    
    # Should complete within reasonable time
    # Allow 10 seconds for property tests (more lenient than unit tests)
    assert wall_time < 10.0, \
        f"Batch should complete in < 10s (took {wall_time:.2f}s)"
    
    # Recorded execution time should be reasonable
    assert result.execution_time < 10.0, \
        f"Recorded execution time should be < 10s (was {result.execution_time:.2f}s)"
    
    # Recorded time should be close to wall time (within 3x for property tests)
    if result.execution_time > 0:
        time_ratio = wall_time / result.execution_time
        assert 0.3 <= time_ratio <= 3.0, \
            f"Recorded time should match wall time (ratio: {time_ratio:.2f})"


def run_all_property_tests():
    """Run all backward compatibility property tests"""
    print("\n" + "="*80)
    print("🧪 AUTONOMOUS SENTINEL v1.9.0 - BACKWARD COMPATIBILITY PROPERTY TESTS")
    print("="*80 + "\n")
    
    test_functions = [
        test_property_49_backward_compatibility_single_transaction,
        test_property_49_backward_compatibility_batch_execution,
        test_property_49_backward_compatibility_determinism,
        test_property_49_backward_compatibility_no_exceptions,
        test_property_49_backward_compatibility_transaction_id_preservation,
        test_property_49_backward_compatibility_execution_time_bounds
    ]
    
    total_tests = len(test_functions)
    passed_tests = 0
    
    for test_func in test_functions:
        print(f"\n📋 {test_func.__name__}")
        print("-" * 80)
        
        try:
            test_func()
            passed_tests += 1
            print(f"✅ PASSED")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "="*80)
    print(f"📊 RESULTS: {passed_tests}/{total_tests} property tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL BACKWARD COMPATIBILITY PROPERTY TESTS PASSED")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
    
    print("="*80 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_property_tests()
    exit(0 if success else 1)
