"""
Test RVC2-004: Error Message Shows Node Type and Supported Alternatives

Validates that UnsupportedConstraintError provides clear, actionable error messages
that show both the unsupported node type and the list of supported alternatives.
"""

import pytest
from diotec360.core.judge import DIOTEC360Judge
from diotec360.core.integrity_panic import UnsupportedConstraintError


def test_error_message_shows_node_type():
    """Test that error message clearly shows the unsupported node type"""
    intent_map = {
        "test_bitwise": {
            "constraints": [
                "balance >= (amount | 0xFF)"  # BitOr operation
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_bitwise")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    
    # Verify node type is in details
    assert 'details' in violation
    assert 'node_type' in violation['details']
    assert violation['details']['node_type'] == "BitOr"
    
    # Verify recovery hint is present
    assert 'recovery_hint' in violation
    assert "BitOr" in violation['recovery_hint']
    assert "Unsupported operation: BitOr" in violation['recovery_hint']
    
    print(f"✅ Error message shows unsupported node type: {violation['details']['node_type']}")


def test_error_message_shows_supported_alternatives():
    """Test that error message shows list of supported alternatives"""
    intent_map = {
        "test_power": {
            "constraints": [
                "balance >= (amount ** 2)"  # Pow operation
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_power")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    
    # Verify supported_types is in details
    assert 'details' in violation
    assert 'supported_types' in violation['details']
    supported_types = violation['details']['supported_types']
    assert isinstance(supported_types, list)
    assert len(supported_types) > 0
    
    # Verify recovery hint contains formatted alternatives
    assert 'recovery_hint' in violation
    assert "Supported AST node types:" in violation['recovery_hint']
    
    # Check that key supported operations are mentioned
    recovery_hint = violation['recovery_hint']
    assert "Add" in recovery_hint or "Add" in str(supported_types)
    assert "Sub" in recovery_hint or "Sub" in str(supported_types)
    assert "Mult" in recovery_hint or "Mult" in str(supported_types)
    
    print(f"✅ Error message shows {len(supported_types)} supported alternatives")


def test_error_message_categorizes_alternatives():
    """Test that error message categorizes supported alternatives for readability"""
    intent_map = {
        "test_shift": {
            "constraints": [
                "balance >= (amount << 2)"  # LShift operation
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_shift")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    recovery_hint = violation['recovery_hint']
    
    # Check for category headers
    assert "Arithmetic:" in recovery_hint or "Add, Sub, Mult" in recovery_hint
    assert "Comparison:" in recovery_hint or "Eq, NotEq" in recovery_hint
    
    print("✅ Error message categorizes alternatives for readability")


def test_error_message_provides_actionable_guidance():
    """Test that error message provides actionable guidance for fixing the issue"""
    intent_map = {
        "test_bitand": {
            "constraints": [
                "balance >= (amount & 0xFF)"  # BitAnd operation
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_bitand")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    recovery_hint = violation['recovery_hint']
    
    # Verify actionable guidance is present
    assert "Rewrite using supported operations" in recovery_hint
    assert "Consult documentation" in recovery_hint
    assert "docs/language-reference/conservation-laws.md" in recovery_hint
    
    # Verify examples of supported operations
    assert "Arithmetic:" in recovery_hint or "+, -, *, /" in recovery_hint
    assert "Comparison:" in recovery_hint or "==, !=, <, <=" in recovery_hint
    
    print("✅ Error message provides actionable guidance")


def test_error_message_explains_security_rationale():
    """Test that error message explains the security rationale for rejection"""
    intent_map = {
        "test_xor": {
            "constraints": [
                "balance >= (amount ^ 0xFF)"  # BitXor operation
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_xor")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    recovery_hint = violation['recovery_hint']
    
    # Verify security explanation is present
    assert "SECURITY NOTE" in recovery_hint or "fail-closed" in recovery_hint
    assert "security" in recovery_hint.lower()
    
    print("✅ Error message explains security rationale")


def test_error_message_full_format():
    """Test the complete error message format"""
    intent_map = {
        "test_complete": {
            "constraints": [
                "balance >= (amount | 0xFF)"
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map)
    result = judge.verify_logic("test_complete")
    
    # Verify transaction was rejected
    assert result['status'] == 'REJECTED'
    assert 'constraint_violation' in result
    
    violation = result['constraint_violation']
    
    # Print the complete error message for manual inspection
    print("\n" + "="*70)
    print("COMPLETE ERROR MESSAGE:")
    print("="*70)
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Violation Type: {violation['violation_type']}")
    print(f"Details: {violation['details']}")
    print("="*70)
    print("\nRECOVERY HINT:")
    print("="*70)
    print(violation['recovery_hint'])
    print("="*70 + "\n")
    
    # Verify all key components are present
    assert violation['violation_type'] == "UNSUPPORTED_AST_NODE"
    assert 'node_type' in violation['details']
    assert 'supported_types' in violation['details']
    assert violation['recovery_hint'] is not None
    assert len(violation['recovery_hint']) > 100  # Should be comprehensive
    
    print("✅ Complete error message format verified")


def test_multiple_unsupported_operations():
    """Test error messages for different unsupported operations"""
    unsupported_operations = [
        ("BitOr", "balance >= (amount | 0xFF)"),
        ("BitAnd", "balance >= (amount & 0xFF)"),
        ("BitXor", "balance >= (amount ^ 0xFF)"),
        ("LShift", "balance >= (amount << 2)"),
        ("RShift", "balance >= (amount >> 2)"),
        ("Pow", "balance >= (amount ** 2)"),
    ]
    
    for expected_node, constraint in unsupported_operations:
        intent_map = {
            "test": {
                "constraints": [constraint]
            }
        }
        
        judge = DIOTEC360Judge(intent_map)
        result = judge.verify_logic("test")
        
        # Verify transaction was rejected
        assert result['status'] == 'REJECTED'
        assert 'constraint_violation' in result
        
        violation = result['constraint_violation']
        
        # Verify node type is correctly identified
        assert expected_node in violation['details']['node_type']
        
        # Verify error message contains node type
        assert expected_node in violation['recovery_hint']
        
        print(f"✅ Error message correct for {expected_node}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("RVC2-004: Error Message Format Validation Tests")
    print("="*70 + "\n")
    
    # Run tests
    test_error_message_shows_node_type()
    test_error_message_shows_supported_alternatives()
    test_error_message_categorizes_alternatives()
    test_error_message_provides_actionable_guidance()
    test_error_message_explains_security_rationale()
    test_error_message_full_format()
    test_multiple_unsupported_operations()
    
    print("\n" + "="*70)
    print("✅ ALL ERROR MESSAGE FORMAT TESTS PASSED")
    print("="*70 + "\n")
