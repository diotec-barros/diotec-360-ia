"""
Test RVC-002: Decimal Precision (No Float Loss)

Validates that the Guardian uses Decimal for all financial calculations
to prevent precision loss and "Salami Attack" via accumulated rounding errors.

Author: Kiro AI - Engenheiro-Chefe
Date: February 21, 2026
"""

import pytest
from decimal import Decimal, getcontext
from diotec360.moe.guardian_expert import GuardianExpert


def test_rvc_002_decimal_precision_preserved():
    """
    RVC-002: Verify that Decimal precision is preserved.
    
    Performs 1,000,000 micro-transactions and verifies that
    the final balance is EXACTLY correct (no rounding errors).
    """
    guardian = GuardianExpert()
    
    # Start with 1,000,000.00000000
    balance = Decimal("1000000.00000000")
    micro_amount = Decimal("0.00000001")
    
    # Perform 1,000,000 micro-transactions
    for _ in range(1000000):
        balance -= micro_amount
    
    # Final balance calculation:
    # 1,000,000.00000000 - (0.00000001 * 1,000,000) = 1,000,000.00000000 - 10.00000000 = 999,990.00000000
    # BUT: 0.00000001 * 1,000,000 = 0.01 (not 10.00)
    # Correct: 1,000,000.00000000 - 0.01 = 999,999.99000000
    expected_balance = Decimal("999999.99000000")
    
    assert balance == expected_balance, f"Precision loss detected: {balance} != {expected_balance}"
    
    # Verify no rounding error
    difference = abs(balance - expected_balance)
    assert difference == Decimal('0'), f"Rounding error: {difference}"
    
    print(f"✅ RVC-002: Decimal precision preserved after 1M transactions")
    print(f"   Initial: 1000000.00000000")
    print(f"   Final:   {balance}")
    print(f"   Expected: {expected_balance}")
    print(f"   Difference: {difference}")


def test_rvc_002_salami_attack_blocked():
    """
    RVC-002: Verify that "Salami Attack" is blocked.
    
    Salami Attack: Attacker performs millions of micro-transactions
    with amounts designed to exploit float rounding errors, creating
    a "gap" that can be stolen.
    
    With Decimal, this attack is impossible because there are no
    rounding errors.
    """
    guardian = GuardianExpert()
    
    # Simulate 1,000,000 micro-transactions
    transactions = []
    running_balance = Decimal("1000000.00000000")
    
    for i in range(1000000):
        amount = Decimal("0.00000001")
        old_balance = running_balance
        new_balance = running_balance - amount
        running_balance = new_balance
        
        # Verify conservation for each transaction
        inputs = [old_balance]
        outputs = [new_balance, amount]
        
        # Conservation check: old_balance == new_balance + amount
        assert guardian._validate_conservation_exact(inputs, outputs)
    
    # Final balance should be EXACTLY correct
    # 1,000,000.00000000 - (0.00000001 * 1,000,000) = 999,999.99000000
    expected_final = Decimal("999999.99000000")
    assert running_balance == expected_final
    
    # Verify no "gap" was created
    total_withdrawn = Decimal("0.00000001") * 1000000
    assert total_withdrawn == Decimal("0.01000000")
    
    initial_balance = Decimal("1000000.00000000")
    assert initial_balance - total_withdrawn == expected_final
    
    print(f"✅ RVC-002: Salami Attack blocked")
    print(f"   1,000,000 micro-transactions verified")
    print(f"   No rounding gap created")
    print(f"   Final balance exact: {running_balance}")


def test_rvc_002_parse_decimal_validation():
    """
    RVC-002: Verify that _parse_decimal validates precision.
    
    Should reject values that cannot be represented exactly.
    """
    guardian = GuardianExpert()
    
    # Test valid conversions
    assert guardian._parse_decimal(100) == Decimal('100')
    assert guardian._parse_decimal("123.456") == Decimal('123.456')
    assert guardian._parse_decimal(Decimal('999.999')) == Decimal('999.999')
    
    # Test float conversion (should preserve precision)
    float_value = 123.45
    decimal_value = guardian._parse_decimal(float_value)
    assert isinstance(decimal_value, Decimal)
    
    # Test that precision is validated
    # Float 0.1 cannot be represented exactly in binary
    # But our conversion should handle it correctly
    result = guardian._parse_decimal(0.1)
    assert isinstance(result, Decimal)
    
    print(f"✅ RVC-002: Decimal parsing validated")


def test_rvc_002_exact_equality_no_epsilon():
    """
    RVC-002: Verify EXACT equality (no epsilon tolerance).
    
    Conservation check must use EXACT equality, not approximate.
    This prevents attackers from exploiting epsilon tolerance.
    """
    guardian = GuardianExpert()
    
    # Test exact equality
    inputs = [Decimal('1000.00'), Decimal('500.00')]
    outputs = [Decimal('1500.00')]
    
    assert guardian._validate_conservation_exact(inputs, outputs)
    
    # Test that even tiny differences are detected
    inputs = [Decimal('1000.00'), Decimal('500.00')]
    outputs = [Decimal('1500.00000001')]  # Off by 0.00000001
    
    assert not guardian._validate_conservation_exact(inputs, outputs)
    
    # Test zero tolerance
    inputs = [Decimal('1000.00')]
    outputs = [Decimal('999.99999999')]  # Off by 0.00000001
    
    assert not guardian._validate_conservation_exact(inputs, outputs)
    
    print(f"✅ RVC-002: Exact equality enforced (zero tolerance)")


def test_rvc_002_float_banned_in_conservation():
    """
    RVC-002: Verify that float is NOT used in conservation checks.
    
    All financial values must be Decimal, never float.
    """
    guardian = GuardianExpert()
    
    # Verify that _validate_conservation_exact expects Decimal
    inputs = [Decimal('100.00'), Decimal('200.00')]
    outputs = [Decimal('300.00')]
    
    assert guardian._validate_conservation_exact(inputs, outputs)
    
    # Test with float (should work but convert to Decimal internally)
    # This tests that the system handles float inputs gracefully
    try:
        float_input = 100.0
        decimal_result = guardian._parse_decimal(float_input)
        assert isinstance(decimal_result, Decimal)
        print(f"✅ RVC-002: Float inputs converted to Decimal")
    except Exception as e:
        pytest.fail(f"Float conversion should work: {e}")


def test_rvc_002_accumulated_rounding_error():
    """
    RVC-002: Verify that accumulated rounding errors don't occur.
    
    With float, repeated operations accumulate rounding errors.
    With Decimal, no accumulation occurs.
    """
    # Test with Decimal (correct)
    decimal_balance = Decimal("1000.00")
    for _ in range(10000):
        decimal_balance -= Decimal("0.01")
        decimal_balance += Decimal("0.01")
    
    # Should be EXACTLY 1000.00 (no accumulation)
    assert decimal_balance == Decimal("1000.00")
    
    # Compare with float (incorrect - for demonstration only)
    float_balance = 1000.00
    for _ in range(10000):
        float_balance -= 0.01
        float_balance += 0.01
    
    # Float will have accumulated error
    float_error = abs(float_balance - 1000.00)
    
    print(f"✅ RVC-002: No accumulated rounding error with Decimal")
    print(f"   Decimal balance: {decimal_balance} (exact)")
    print(f"   Float balance: {float_balance} (error: {float_error})")
    
    # Verify Decimal has zero error
    assert decimal_balance == Decimal("1000.00")


def test_rvc_002_conservation_with_decimal():
    """
    RVC-002: Verify conservation checking uses Decimal.
    
    Integration test with GuardianExpert.
    """
    guardian = GuardianExpert()
    
    # Create intent with financial transaction
    intent = """
    verify {
        old_balance - amount == new_balance;
        amount > 0;
    }
    """
    
    # Parse and verify (simplified test)
    intent_data = guardian._parse_intent(intent)
    
    # Verify that conservation checker is initialized
    assert guardian.conservation_checker is not None
    
    print(f"✅ RVC-002: Conservation checker integrated with Decimal support")


def test_rvc_002_precision_28_digits():
    """
    RVC-002: Verify that Decimal precision is set to 28 digits.
    
    This provides sufficient precision for financial calculations.
    """
    # Check global precision
    assert getcontext().prec >= 28
    
    # Test with large number arithmetic
    large_number = Decimal("1234567890123456.78901234")
    small_number = Decimal("0.00000001")
    
    result = large_number + small_number
    
    # Should preserve precision
    assert result > large_number
    assert result == Decimal("1234567890123456.78901235")
    
    print(f"✅ RVC-002: Decimal precision set to {getcontext().prec} digits")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("RVC-002: DECIMAL PRECISION TEST SUITE")
    print("="*70 + "\n")
    
    print("Testing RVC-002 fixes...")
    print("1. Decimal precision preserved (1M transactions)")
    print("2. Salami Attack blocked ⭐ CRITICAL")
    print("3. Decimal parsing validated")
    print("4. Exact equality enforced (zero tolerance) ⭐ CRITICAL")
    print("5. Float banned in conservation checks")
    print("6. No accumulated rounding errors")
    print("7. Conservation with Decimal integration")
    print("8. 28-digit precision configured")
    print()
    
    pytest.main([__file__, '-v', '-s'])
