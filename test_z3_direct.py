"""
Direct Z3 Verification Test - Proves we're using REAL Z3!
Tests the verify_proof_with_z3 function directly without FastAPI
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Z3 directly
try:
    from z3 import Solver, parse_smt2_string, sat, unsat
    print("✅ Z3 imported successfully from z3-solver library")
    Z3_AVAILABLE = True
except ImportError:
    print("❌ Z3 not available! Install with: pip install z3-solver")
    Z3_AVAILABLE = False
    sys.exit(1)

# Import our verification function
from api.lattice_bridge import verify_proof_with_z3, Z3_AVAILABLE as API_Z3_AVAILABLE

print(f"\n{'='*70}")
print(f"🔬 DIRECT Z3 VERIFICATION TEST - NO MOCKS!")
print(f"{'='*70}\n")

def test_z3_library_works():
    """Test that Z3 library itself works"""
    print("Test 1: Z3 Library Basic Functionality")
    print("-" * 50)
    
    solver = Solver()
    
    # Parse a simple formula
    formula = "(declare-const x Int)\n(assert (> x 5))\n(check-sat)"
    assertions = parse_smt2_string(formula)
    
    for assertion in assertions:
        solver.add(assertion)
    
    result = solver.check()
    
    print(f"  Formula: x > 5")
    print(f"  Z3 Result: {result}")
    print(f"  Expected: sat")
    
    assert result == sat, f"Expected SAT, got {result}"
    print(f"  ✅ Z3 library works correctly!\n")

def test_verify_function_with_sat():
    """Test our verify function with SAT formula"""
    print("Test 2: Verify Function with SAT Formula")
    print("-" * 50)
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(declare-const y Int)\n(assert (= (+ x y) 10))\n(assert (= (- x y) 2))\n(check-sat)"
    }
    
    proof = "(model sat x=6 y=4)"
    result = verify_proof_with_z3(challenge, proof, 1000)
    
    print(f"  Formula: x + y = 10, x - y = 2")
    print(f"  Proof: {proof}")
    print(f"  Verification Result: {result}")
    print(f"  Expected: True")
    
    assert result is True, "Should verify SAT formula"
    print(f"  ✅ SAT formula verified correctly!\n")

def test_verify_function_with_unsat():
    """Test our verify function with UNSAT formula"""
    print("Test 3: Verify Function with UNSAT Formula")
    print("-" * 50)
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(assert (> x 10))\n(assert (< x 5))\n(check-sat)"
    }
    
    proof = "(model sat)"  # Wrong! This formula is UNSAT
    result = verify_proof_with_z3(challenge, proof, 1000)
    
    print(f"  Formula: x > 10 AND x < 5 (impossible!)")
    print(f"  Proof: {proof}")
    print(f"  Verification Result: {result}")
    print(f"  Expected: False (formula is UNSAT)")
    
    assert result is False, "Should reject SAT proof for UNSAT formula"
    print(f"  ✅ UNSAT formula handled correctly!\n")

def test_verify_function_with_boolean():
    """Test with boolean logic"""
    print("Test 4: Verify Function with Boolean Logic")
    print("-" * 50)
    
    challenge = {
        "z3_formula": "(declare-const a Bool)\n(declare-const b Bool)\n(assert (or a b))\n(assert (not (and a b)))\n(check-sat)"
    }
    
    proof = "(model sat a=true b=false)"
    result = verify_proof_with_z3(challenge, proof, 500)
    
    print(f"  Formula: (a OR b) AND NOT(a AND b) [XOR]")
    print(f"  Proof: {proof}")
    print(f"  Verification Result: {result}")
    print(f"  Expected: True")
    
    assert result is True, "Should verify boolean XOR formula"
    print(f"  ✅ Boolean logic verified correctly!\n")

def test_verify_function_rejects_bad_time():
    """Test that unreasonable solver times are rejected"""
    print("Test 5: Reject Unreasonable Solver Times")
    print("-" * 50)
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(assert (> x 0))\n(check-sat)"
    }
    
    # Test instant solve (< 10ms)
    proof = "(model sat)"
    result = verify_proof_with_z3(challenge, proof, 1)
    
    print(f"  Solver Time: 1ms (too fast!)")
    print(f"  Verification Result: {result}")
    print(f"  Expected: False")
    
    assert result is False, "Should reject instant solver time"
    print(f"  ✅ Instant time rejected!\n")
    
    # Test too slow (> 2 minutes)
    result = verify_proof_with_z3(challenge, proof, 150000)
    
    print(f"  Solver Time: 150000ms (too slow!)")
    print(f"  Verification Result: {result}")
    print(f"  Expected: False")
    
    assert result is False, "Should reject excessive solver time"
    print(f"  ✅ Excessive time rejected!\n")

def test_verify_function_with_arrays():
    """Test with array theory"""
    print("Test 6: Verify Function with Array Theory")
    print("-" * 50)
    
    challenge = {
        "z3_formula": "(declare-const arr (Array Int Int))\n(assert (= (select arr 0) 42))\n(check-sat)"
    }
    
    proof = "(model sat arr=[(0,42)])"
    result = verify_proof_with_z3(challenge, proof, 800)
    
    print(f"  Formula: arr[0] = 42")
    print(f"  Proof: {proof}")
    print(f"  Verification Result: {result}")
    print(f"  Expected: True")
    
    assert result is True, "Should verify array theory formula"
    print(f"  ✅ Array theory verified correctly!\n")

def test_z3_api_availability():
    """Test that API reports Z3 as available"""
    print("Test 7: API Z3 Availability Flag")
    print("-" * 50)
    
    print(f"  Z3_AVAILABLE in api.lattice_bridge: {API_Z3_AVAILABLE}")
    print(f"  Expected: True")
    
    assert API_Z3_AVAILABLE is True, "API should report Z3 as available"
    print(f"  ✅ API correctly reports Z3 availability!\n")

if __name__ == "__main__":
    print(f"\n🔬 RUNNING DIRECT Z3 VERIFICATION TESTS\n")
    
    try:
        test_z3_library_works()
        test_verify_function_with_sat()
        test_verify_function_with_unsat()
        test_verify_function_with_boolean()
        test_verify_function_rejects_bad_time()
        test_verify_function_with_arrays()
        test_z3_api_availability()
        
        print(f"\n{'='*70}")
        print(f"✅ ALL TESTS PASSED - Z3 REAL VERIFICATION CONFIRMED!")
        print(f"{'='*70}")
        print(f"\n🎉 PROOF COMPLETE:")
        print(f"   ✓ Z3 library imported and functional")
        print(f"   ✓ SAT formulas verified correctly")
        print(f"   ✓ UNSAT formulas rejected correctly")
        print(f"   ✓ Boolean logic works")
        print(f"   ✓ Array theory works")
        print(f"   ✓ Solver time validation works")
        print(f"   ✓ API reports Z3 as available")
        print(f"\n🏛️ DIONÍSIO: WE ARE USING REAL Z3, NOT MOCKS! ⚡\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
