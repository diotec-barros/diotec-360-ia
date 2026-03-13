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
Unit Tests for atomic_batch Syntax - Synchrony Protocol v1.8.0

Tests parsing and execution of atomic_batch blocks.

Author: Diotec360 Team
Version: 1.8.0
Date: February 4, 2026
"""

import pytest
from diotec360.core.parser import DIOTEC360Parser, AtomicBatchNode
from diotec360.core.batch_processor import BatchProcessor


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def parser():
    """Create parser instance"""
    return DIOTEC360Parser()


@pytest.fixture
def batch_processor():
    """Create batch processor instance"""
    return BatchProcessor(num_threads=4)


# ============================================================================
# TEST: Parse Valid atomic_batch
# ============================================================================

def test_parse_valid_atomic_batch(parser):
    """
    Test parsing of valid atomic_batch block.
    
    Validates:
        Requirements 6.1, 6.2
    """
    code = """
    atomic_batch payroll {
        intent pay_alice(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 100;
            }
        }
        
        intent pay_bob(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 50;
            }
        }
    }
    """
    
    # Parse code
    result = parser.parse(code)
    
    # Verify result is list of AtomicBatchNode
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], AtomicBatchNode)
    
    # Verify batch name
    batch = result[0]
    assert batch.name == "payroll"
    
    # Verify intents
    assert "pay_alice" in batch.intents
    assert "pay_bob" in batch.intents
    assert len(batch.intents) == 2


# ============================================================================
# TEST: Reject Duplicate Intent Names
# ============================================================================

def test_reject_duplicate_intent_names(parser):
    """
    Test rejection of duplicate intent names in atomic_batch.
    
    Validates:
        Requirements 6.3
    """
    code = """
    atomic_batch payroll {
        intent pay_employee(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 100;
            }
        }
        
        intent pay_employee(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 50;
            }
        }
    }
    """
    
    # Should raise ValueError for duplicate name
    with pytest.raises(ValueError) as exc_info:
        parser.parse(code)
    
    assert "Duplicate intent name" in str(exc_info.value)
    assert "pay_employee" in str(exc_info.value)


# ============================================================================
# TEST: Parse Empty atomic_batch
# ============================================================================

def test_parse_empty_atomic_batch(parser):
    """
    Test parsing of empty atomic_batch block.
    
    Validates:
        Requirements 6.2
    """
    code = """
    atomic_batch empty {
    }
    """
    
    # Parse code
    result = parser.parse(code)
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) == 1
    
    batch = result[0]
    assert batch.name == "empty"
    assert len(batch.intents) == 0


# ============================================================================
# TEST: Convert atomic_batch to Transactions
# ============================================================================

def test_convert_atomic_batch_to_transactions(parser):
    """
    Test conversion of atomic_batch to transactions.
    
    Validates:
        Requirements 6.4
    """
    code = """
    atomic_batch payroll {
        intent pay_alice(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 100;
            }
        }
        
        intent pay_bob(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 50;
            }
        }
    }
    """
    
    # Parse code
    result = parser.parse(code)
    batch = result[0]
    
    # Convert to transactions
    transactions = batch.to_transactions()
    
    # Verify transactions
    assert len(transactions) == 2
    assert all(hasattr(tx, 'id') for tx in transactions)
    assert all(hasattr(tx, 'intent_name') for tx in transactions)


# ============================================================================
# TEST: Execute atomic_batch via BatchProcessor
# ============================================================================

def test_execute_atomic_batch_via_batch_processor(parser, batch_processor):
    """
    Test execution of atomic_batch via BatchProcessor.
    
    Validates:
        Requirements 6.4, 6.5
    """
    code = """
    atomic_batch payroll {
        intent pay_alice(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 100;
            }
        }
    }
    """
    
    # Parse code
    result = parser.parse(code)
    batch = result[0]
    
    # Execute via BatchProcessor
    batch_result = batch_processor.execute_atomic_batch(batch)
    
    # Verify result
    assert batch_result is not None
    assert hasattr(batch_result, 'success')
    assert hasattr(batch_result, 'transactions_executed')


# ============================================================================
# TEST: Multiple atomic_batch Blocks
# ============================================================================

def test_parse_multiple_atomic_batches(parser):
    """
    Test parsing of multiple atomic_batch blocks.
    
    Validates:
        Requirements 6.2
    """
    code = """
    atomic_batch payroll {
        intent pay_alice(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 100;
            }
        }
    }
    
    atomic_batch bonuses {
        intent bonus_bob(amount: int) {
            guard {
                amount > 0;
            }
            solve {
                priority: speed;
            }
            verify {
                amount == 50;
            }
        }
    }
    """
    
    # Parse code
    result = parser.parse(code)
    
    # Verify result
    assert isinstance(result, list)
    assert len(result) == 2
    
    assert result[0].name == "payroll"
    assert result[1].name == "bonuses"


# ============================================================================
# TEST: Backward Compatibility - Regular Intents
# ============================================================================

def test_backward_compatibility_regular_intents(parser):
    """
    Test that regular intents still parse correctly.
    
    Validates:
        Requirements 8.1, 8.3
    """
    code = """
    intent transfer(amount: int) {
        guard {
            amount > 0;
        }
        solve {
            priority: speed;
        }
        verify {
            amount == 100;
        }
    }
    """
    
    # Parse code
    result = parser.parse(code)
    
    # Verify result is dict (not list)
    assert isinstance(result, dict)
    assert "transfer" in result


# ============================================================================
# TEST: Intent Name Uniqueness Validation
# ============================================================================

def test_intent_name_uniqueness_validation(parser):
    """
    Test that intent names must be unique within atomic_batch.
    
    Validates:
        Requirements 6.3
    """
    code = """
    atomic_batch test {
        intent duplicate(x: int) {
            guard { x > 0; }
            solve { priority: speed; }
            verify { x == 1; }
        }
        
        intent duplicate(y: int) {
            guard { y > 0; }
            solve { priority: speed; }
            verify { y == 2; }
        }
    }
    """
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        parser.parse(code)
    
    assert "Duplicate" in str(exc_info.value)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
