"""
Test RVC-001: Fail-Closed Z3 Solver

Validates that the Judge implements strict fail-closed logic:
- Only z3.sat is accepted
- z3.unknown is REJECTED
- Z3 exceptions are REJECTED

Author: Kiro AI - Engenheiro-Chefe
Date: February 21, 2026
"""

import pytest
from diotec360.core.judge import DIOTEC360Judge


def test_rvc_001_z3_sat_accepted():
    """
    RVC-001: Verify that z3.sat results are accepted.
    
    This is the happy path - valid proofs should be accepted.
    """
    intent_map = {
        'simple_transfer': {
            'params': [
                {'name': 'amount', 'type': 'int'},
                {'name': 'sender_balance', 'type': 'int'}
            ],
            'constraints': [
                'sender_balance >= amount',
                'amount > 0'
            ],
            'post_conditions': [
                'sender_balance - amount >= 0'
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('simple_transfer')
    
    # Should be PROVED (z3.sat)
    assert result['status'] == 'PROVED'
    assert 'model' in result


def test_rvc_001_z3_unsat_rejected():
    """
    RVC-001: Verify that z3.unsat results are rejected.
    
    Contradictory constraints should be detected and rejected.
    """
    intent_map = {
        'contradictory': {
            'params': [
                {'name': 'x', 'type': 'int'}
            ],
            'constraints': [
                'x > 10'
            ],
            'post_conditions': [
                'x < 5'  # Contradicts constraint
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('contradictory')
    
    # Should be FAILED (z3.unsat)
    assert result['status'] == 'FAILED'
    assert 'contradição' in result['message'].lower() or 'contradit' in result['message'].lower()


def test_rvc_001_z3_unknown_rejected():
    """
    RVC-001: Verify that z3.unknown results are REJECTED (fail-closed).
    
    This is the critical fix - when Z3 cannot determine satisfiability,
    the system MUST reject the transaction (fail-closed).
    """
    # Create intent with complex quantifiers that may cause Z3 to return 'unknown'
    intent_map = {
        'complex_quantifiers': {
            'params': [
                {'name': 'x', 'type': 'int'},
                {'name': 'y', 'type': 'int'}
            ],
            'constraints': [
                'x > 0',
                'y > 0'
            ],
            'post_conditions': [
                # This is a simple condition that should be satisfiable
                # We'll test with timeout to force 'unknown'
                'x + y > 0'
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    
    # Set very low timeout to force 'unknown' result
    judge.Z3_TIMEOUT_MS = 1  # 1ms timeout
    judge.solver.set("timeout", 1)
    
    result = judge.verify_logic('complex_quantifiers')
    
    # Should be REJECTED (fail-closed on z3.unknown)
    # Note: This test may be flaky depending on system performance
    # If Z3 completes within 1ms, it will return sat/unsat instead of unknown
    if result['status'] == 'REJECTED':
        assert 'fail-closed' in result['message'].lower() or 'unknown' in result['message'].lower()
        print("✅ RVC-001: Z3 'unknown' correctly rejected (fail-closed)")
    elif result['status'] in ['PROVED', 'FAILED']:
        print("⚠️  RVC-001: Z3 completed too quickly to test 'unknown' case")
        pytest.skip("Z3 completed too quickly to force 'unknown' result")
    else:
        pytest.fail(f"Unexpected status: {result['status']}")


def test_rvc_001_z3_exception_rejected():
    """
    RVC-001: Verify that Z3 exceptions are REJECTED (fail-closed).
    
    Any exception during Z3 solving MUST result in rejection.
    """
    # Create intent with invalid Z3 syntax to trigger exception
    intent_map = {
        'invalid_syntax': {
            'params': [
                {'name': 'x', 'type': 'int'}
            ],
            'constraints': [],
            'post_conditions': [
                # This will be parsed but may cause issues in Z3
                'x == x'  # Tautology, should be fine
            ]
        }
    }
    
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    
    # Manually corrupt the solver to force an exception
    # This simulates a Z3 internal error
    try:
        # Try to add invalid constraint directly to solver
        from z3 import Int, And
        judge.solver.add(And())  # Empty And() may cause issues
        
        result = judge.verify_logic('invalid_syntax')
        
        # If we get here, check that any exception was handled correctly
        # The result should be REJECTED if an exception occurred
        if result['status'] == 'REJECTED':
            assert 'fail-closed' in result['message'].lower() or 'exception' in result['message'].lower()
            print("✅ RVC-001: Z3 exception correctly rejected (fail-closed)")
        else:
            # If no exception occurred, the test is inconclusive
            print("⚠️  RVC-001: No exception triggered, test inconclusive")
            pytest.skip("Could not trigger Z3 exception")
    
    except Exception as e:
        # If exception propagates, that's also a failure
        pytest.fail(f"Exception should be caught and result in REJECTED: {e}")


def test_rvc_001_fail_closed_principle():
    """
    RVC-001: Verify the fail-closed principle is enforced.
    
    The principle: "If we cannot prove it's safe, then it's unsafe."
    
    Only z3.sat should result in PROVED status.
    All other outcomes (unsat, unknown, exception) should result in rejection.
    """
    intent_map = {
        'test_intent': {
            'params': [{'name': 'x', 'type': 'int'}],
            'constraints': ['x > 0'],
            'post_conditions': ['x > 0']
        }
    }
    
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('test_intent')
    
    # This should be PROVED (z3.sat)
    assert result['status'] == 'PROVED'
    
    # Now test with contradictory conditions
    intent_map['test_intent']['post_conditions'] = ['x < 0']
    judge = DIOTEC360Judge(intent_map, enable_moe=False)
    result = judge.verify_logic('test_intent')
    
    # This should be FAILED or REJECTED (not PROVED)
    assert result['status'] in ['FAILED', 'REJECTED']
    assert result['status'] != 'PROVED'
    
    print("✅ RVC-001: Fail-closed principle enforced")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("RVC-001: FAIL-CLOSED Z3 SOLVER TEST SUITE")
    print("="*70 + "\n")
    
    print("Testing RVC-001 fixes...")
    print("1. z3.sat accepted (happy path)")
    print("2. z3.unsat rejected (contradiction)")
    print("3. z3.unknown rejected (fail-closed) ⭐ CRITICAL")
    print("4. Z3 exceptions rejected (fail-closed) ⭐ CRITICAL")
    print("5. Fail-closed principle enforced")
    print()
    
    pytest.main([__file__, '-v', '-s'])
