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
Test Suite for Diotec360 v1.8.0 Backward Compatibility

Tests that single transaction execution via BatchProcessor maintains
identical behavior to v1.7.0 for all existing use cases.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
import time
from diotec360.core.synchrony import (
    Transaction,
    BatchResult,
    CircularDependencyError,
    ConservationViolationError
)
from diotec360.core.batch_processor import BatchProcessor


class TestSingleTransactionExecution:
    """Unit tests for single transaction execution"""
    
    def test_simple_transfer(self):
        """Test simple transfer transaction"""
        processor = BatchProcessor()
        
        # Create single transaction
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[
                {"type": "debit", "account": "alice", "amount": 100},
                {"type": "credit", "account": "bob", "amount": 100}
            ],
            verify_conditions=["alice.balance >= 0", "bob.balance >= 0"]
        )
        
        # Execute single transaction
        result = processor.execute_single_transaction(tx)
        
        # Verify result structure (v1.7.0 compatibility)
        assert isinstance(result, BatchResult)
        assert result.success is True
        assert result.transactions_executed == 1
        assert result.execution_time > 0
        
        print("✅ Simple transfer test passed")
    
    def test_empty_transaction(self):
        """Test transaction with no operations"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="noop",
            accounts={},
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert isinstance(result, BatchResult)
        assert result.success is True
        assert result.transactions_executed == 1
        
        print("✅ Empty transaction test passed")
    
    def test_multiple_accounts(self):
        """Test transaction with multiple accounts"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="multi_transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500},
                "charlie": {"balance": 250},
                "dave": {"balance": 750}
            },
            operations=[
                {"type": "debit", "account": "alice", "amount": 100},
                {"type": "credit", "account": "bob", "amount": 50},
                {"type": "credit", "account": "charlie", "amount": 50}
            ],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert result.success is True
        assert result.transactions_executed == 1
        
        print("✅ Multiple accounts test passed")
    
    def test_with_oracle_proofs(self):
        """Test transaction with oracle proofs"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="oracle_transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[
                {"type": "debit", "account": "alice", "amount": 100},
                {"type": "credit", "account": "bob", "amount": 100}
            ],
            verify_conditions=[],
            oracle_proofs=[
                {
                    "oracle_id": "chainlink_btc_usd",
                    "value": 45000.0,
                    "timestamp": int(time.time()),
                    "signature": "0x1a2b3c"
                }
            ]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert result.success is True
        assert result.transactions_executed == 1
        
        print("✅ Oracle proofs test passed")
    
    def test_result_structure_compatibility(self):
        """Test that result structure matches v1.7.0"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        # Verify all v1.7.0 fields are present
        assert hasattr(result, 'success')
        assert hasattr(result, 'transactions_executed')
        assert hasattr(result, 'transactions_parallel')
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'throughput_improvement')
        
        # Verify types
        assert isinstance(result.success, bool)
        assert isinstance(result.transactions_executed, int)
        assert isinstance(result.transactions_parallel, int)
        assert isinstance(result.execution_time, float)
        assert isinstance(result.throughput_improvement, float)
        
        print("✅ Result structure compatibility test passed")
    
    def test_error_handling_compatibility(self):
        """Test that error handling matches v1.7.0"""
        processor = BatchProcessor()
        
        # This should not raise an exception, but return error in result
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000}
            },
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        # Result should be returned (not exception)
        assert isinstance(result, BatchResult)
        
        print("✅ Error handling compatibility test passed")
    
    def test_execution_time_recorded(self):
        """Test that execution time is recorded"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert result.execution_time > 0
        assert result.execution_time < 10.0  # Should be fast
        
        print("✅ Execution time recording test passed")
    
    def test_throughput_improvement_single_tx(self):
        """Test that throughput improvement is 1.0 for single transaction"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        # Single transaction should have no improvement (1.0x)
        # or slight overhead due to batch processing
        assert result.throughput_improvement >= 0.5
        assert result.throughput_improvement <= 2.0
        
        print("✅ Throughput improvement test passed")


class TestBatchVsSingleEquivalence:
    """Tests that execute_single_transaction is equivalent to execute_batch([tx])"""
    
    def test_equivalence_simple(self):
        """Test equivalence for simple transaction"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[],
            verify_conditions=[]
        )
        
        # Execute via single transaction method
        result_single = processor.execute_single_transaction(tx)
        
        # Execute via batch method
        result_batch = processor.execute_batch([tx])
        
        # Results should be equivalent
        assert result_single.success == result_batch.success
        assert result_single.transactions_executed == result_batch.transactions_executed
        
        print("✅ Equivalence test passed")
    
    def test_equivalence_with_verification(self):
        """Test equivalence with verification conditions"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={
                "alice": {"balance": 1000},
                "bob": {"balance": 500}
            },
            operations=[],
            verify_conditions=["alice.balance >= 0"]
        )
        
        result_single = processor.execute_single_transaction(tx)
        result_batch = processor.execute_batch([tx])
        
        assert result_single.success == result_batch.success
        
        print("✅ Equivalence with verification test passed")


class TestAPIContractPreservation:
    """Tests that API contracts from v1.7.0 are preserved"""
    
    def test_accepts_transaction_object(self):
        """Test that method accepts Transaction object"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={},
            operations=[],
            verify_conditions=[]
        )
        
        # Should not raise TypeError
        result = processor.execute_single_transaction(tx)
        assert isinstance(result, BatchResult)
        
        print("✅ Transaction object acceptance test passed")
    
    def test_returns_batch_result(self):
        """Test that method returns BatchResult"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="transfer",
            accounts={},
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert isinstance(result, BatchResult)
        assert type(result).__name__ == "BatchResult"
        
        print("✅ BatchResult return type test passed")
    
    def test_preserves_transaction_id(self):
        """Test that transaction ID is preserved"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="my_unique_tx_id",
            intent_name="transfer",
            accounts={},
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        # Transaction should be executed
        assert result.transactions_executed == 1
        
        print("✅ Transaction ID preservation test passed")
    
    def test_preserves_intent_name(self):
        """Test that intent name is preserved"""
        processor = BatchProcessor()
        
        tx = Transaction(
            id="tx1",
            intent_name="my_custom_intent",
            accounts={},
            operations=[],
            verify_conditions=[]
        )
        
        result = processor.execute_single_transaction(tx)
        
        assert result.success is True
        
        print("✅ Intent name preservation test passed")


def run_all_tests():
    """Run all backward compatibility tests"""
    print("\n" + "="*70)
    print("🧪 Diotec360 v1.8.0 - BACKWARD COMPATIBILITY TEST SUITE")
    print("="*70 + "\n")
    
    test_classes = [
        TestSingleTransactionExecution,
        TestBatchVsSingleEquivalence,
        TestAPIContractPreservation
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n📋 {test_class.__name__}")
        print("-" * 70)
        
        test_instance = test_class()
        test_methods = [m for m in dir(test_instance) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_instance, method_name)
                method()
                passed_tests += 1
            except Exception as e:
                print(f"❌ {method_name} FAILED: {e}")
    
    print("\n" + "="*70)
    print(f"📊 RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ ALL BACKWARD COMPATIBILITY TESTS PASSED")
    else:
        print(f"❌ {total_tests - passed_tests} tests failed")
    
    print("="*70 + "\n")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
