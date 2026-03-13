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
Test Overflow Sentinel v1.4.1 - Critical Fix Verification

Tests the fix for the bug where overflow detection checked individual values
but not the RESULT of operations.

The "Bit Apocalypse" case: balance = 9223372036854775800 + 100
- Individual values: both within limits
- Result: 9223372036854775900 > MAX_INT (9223372036854775807)
- Expected: ❌ OVERFLOW DETECTED
"""

from diotec360.core.overflow import OverflowSentinel, MAX_INT, MIN_INT


def test_literal_addition_overflow():
    """
    Test Case 1: Literal + Literal = Overflow
    
    balance == (9223372036854775800 + 100)
    Result: 9223372036854775900 > MAX_INT
    """
    print("\n" + "="*60)
    print("TEST 1: Literal Addition Overflow (Bit Apocalypse)")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    # Valor perto do MAX_INT
    near_max = MAX_INT - 7  # 9223372036854775800
    
    result = sentinel.check_intent({
        'verify': [f'balance == ({near_max} + 100)']
    })
    
    print(f"\nInput: balance == ({near_max} + 100)")
    print(f"MAX_INT: {MAX_INT}")
    print(f"Result value: {near_max + 100}")
    print(f"Overflow? {near_max + 100 > MAX_INT}")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    print(f"  message: {result.message}")
    
    if not result.is_safe:
        print(f"\n✅ PASS - Overflow correctly detected!")
        for v in result.violations:
            print(f"  Type: {v['type']}")
            print(f"  Operation: {v['operation']}")
            print(f"  Result: {v['result']}")
    else:
        print(f"\n❌ FAIL - Overflow NOT detected! This is the bug!")
    
    assert not result.is_safe, "Should detect overflow!"
    assert len(result.violations) == 1
    assert 'OVERFLOW' in result.violations[0]['type']


def test_literal_subtraction_underflow():
    """
    Test Case 2: Literal - Literal = Underflow
    
    balance == (-9223372036854775800 - 100)
    Result: -9223372036854775900 < MIN_INT
    """
    print("\n" + "="*60)
    print("TEST 2: Literal Subtraction Underflow")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    # Valor perto do MIN_INT
    near_min = MIN_INT + 7  # -9223372036854775801
    
    result = sentinel.check_intent({
        'verify': [f'balance == ({near_min} - 100)']
    })
    
    print(f"\nInput: balance == ({near_min} - 100)")
    print(f"MIN_INT: {MIN_INT}")
    print(f"Result value: {near_min - 100}")
    print(f"Underflow? {near_min - 100 < MIN_INT}")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    print(f"  message: {result.message}")
    
    if not result.is_safe:
        print(f"\n✅ PASS - Underflow correctly detected!")
        for v in result.violations:
            print(f"  Type: {v['type']}")
            print(f"  Operation: {v['operation']}")
    else:
        print(f"\n❌ FAIL - Underflow NOT detected!")
    
    assert not result.is_safe, "Should detect underflow!"
    assert len(result.violations) == 1
    assert 'UNDERFLOW' in result.violations[0]['type']


def test_literal_multiplication_overflow():
    """
    Test Case 3: Literal * Literal = Overflow
    
    balance == (1000000000000 * 10000000)
    Result: 10000000000000000000 > MAX_INT
    """
    print("\n" + "="*60)
    print("TEST 3: Literal Multiplication Overflow")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    result = sentinel.check_intent({
        'verify': ['balance == (1000000000000 * 10000000)']
    })
    
    print(f"\nInput: balance == (1000000000000 * 10000000)")
    print(f"MAX_INT: {MAX_INT}")
    print(f"Result value: {1000000000000 * 10000000}")
    print(f"Overflow? {1000000000000 * 10000000 > MAX_INT}")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    
    if not result.is_safe:
        print(f"\n✅ PASS - Overflow correctly detected!")
    else:
        print(f"\n❌ FAIL - Overflow NOT detected!")
    
    assert not result.is_safe, "Should detect overflow!"


def test_safe_literal_operation():
    """
    Test Case 4: Safe Literal Operation
    
    balance == (100 + 200)
    Result: 300 (safe)
    """
    print("\n" + "="*60)
    print("TEST 4: Safe Literal Operation")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    result = sentinel.check_intent({
        'verify': ['balance == (100 + 200)']
    })
    
    print(f"\nInput: balance == (100 + 200)")
    print(f"Result value: 300")
    print(f"Safe? {300 <= MAX_INT}")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    
    if result.is_safe:
        print(f"\n✅ PASS - Safe operation correctly allowed!")
    else:
        print(f"\n❌ FAIL - False positive!")
    
    assert result.is_safe, "Should allow safe operations!"


def test_variable_operation_risk():
    """
    Test Case 5: Variable Operation (Risk Detection)
    
    balance == old_balance + 10000
    Risk: old_balance might be near MAX_INT
    """
    print("\n" + "="*60)
    print("TEST 5: Variable Operation Risk")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    result = sentinel.check_intent({
        'verify': ['balance == old_balance + 10000']
    })
    
    print(f"\nInput: balance == old_balance + 10000")
    print(f"Risk: old_balance might be near MAX_INT")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    print(f"  message: {result.message}")
    
    if not result.is_safe:
        print(f"\n✅ PASS - Risk correctly detected!")
        for v in result.violations:
            print(f"  Type: {v['type']}")
            print(f"  Recommendation: {v['recommendation']}")
    else:
        print(f"\n⚠️  Variable operations with large values should warn about risk")
    
    # This should detect risk for large values
    assert not result.is_safe, "Should detect overflow risk for large additions!"


def test_division_by_zero():
    """
    Test Case 6: Division by Zero
    
    balance == (100 / 0)
    """
    print("\n" + "="*60)
    print("TEST 6: Division by Zero")
    print("="*60)
    
    sentinel = OverflowSentinel()
    
    result = sentinel.check_intent({
        'verify': ['balance == (100 / 0)']
    })
    
    print(f"\nInput: balance == (100 / 0)")
    
    print(f"\nSentinel Result:")
    print(f"  is_safe: {result.is_safe}")
    
    if not result.is_safe:
        print(f"\n✅ PASS - Division by zero detected!")
        for v in result.violations:
            print(f"  Type: {v['type']}")
    else:
        print(f"\n❌ FAIL - Division by zero NOT detected!")
    
    assert not result.is_safe, "Should detect division by zero!"
    assert 'DIVISION_BY_ZERO' in result.violations[0]['type']


if __name__ == '__main__':
    print("\n" + "="*60)
    print("OVERFLOW SENTINEL v1.4.1 - CRITICAL FIX VERIFICATION")
    print("="*60)
    print("\nTesting the fix for: Checking RESULT of operations, not just individual values")
    
    try:
        test_literal_addition_overflow()
        test_literal_subtraction_underflow()
        test_literal_multiplication_overflow()
        test_safe_literal_operation()
        test_variable_operation_risk()
        test_division_by_zero()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nThe Overflow Sentinel v1.4.1 correctly detects:")
        print("  ✓ Literal-to-literal overflow")
        print("  ✓ Literal-to-literal underflow")
        print("  ✓ Multiplication overflow")
        print("  ✓ Division by zero")
        print("  ✓ Variable operation risks")
        print("  ✓ Safe operations (no false positives)")
        print("\n🛡️ The Bit Apocalypse has been prevented! 🚀")
        
    except AssertionError as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        raise
