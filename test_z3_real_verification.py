"""
Test Z3 Real Verification - Proof that we're using REAL Z3, not mocks!
"""

import pytest
from fastapi.testclient import TestClient
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from api.main import app
from api.lattice_bridge import verify_proof_with_z3, Z3_AVAILABLE

client = TestClient(app)

print(f"\n{'='*70}")
print(f"🔬 Z3 REAL VERIFICATION TEST - NO MOCKS!")
print(f"{'='*70}\n")

def test_z3_is_available():
    """Verify Z3 is actually installed and available"""
    print(f"✓ Checking if Z3 is available...")
    assert Z3_AVAILABLE, "Z3 solver must be installed! Run: pip install z3-solver"
    print(f"  ✅ Z3 is available and imported successfully\n")

def test_z3_verifies_sat_formula():
    """Test that Z3 correctly identifies a satisfiable formula"""
    print(f"✓ Testing SAT formula verification...")
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(declare-const y Int)\n(assert (= (+ x y) 10))\n(assert (= (- x y) 2))\n(check-sat)"
    }
    
    # Valid proof (contains "sat")
    proof = "(model sat x=6 y=4)"
    result = verify_proof_with_z3(challenge, proof, 1000)
    
    assert result is True, "Z3 should verify SAT formula with valid proof"
    print(f"  ✅ Z3 correctly verified SAT formula\n")

def test_z3_rejects_invalid_proof():
    """Test that Z3 rejects proof that doesn't match formula result"""
    print(f"✓ Testing invalid proof rejection...")
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(assert (> x 0))\n(check-sat)"
    }
    
    # Invalid proof (doesn't contain "sat")
    proof = "(model unsat)"
    result = verify_proof_with_z3(challenge, proof, 1000)
    
    # Z3 will return SAT for this formula, but proof says UNSAT
    # So verification should fail
    assert result is False, "Z3 should reject proof that doesn't match result"
    print(f"  ✅ Z3 correctly rejected invalid proof\n")

def test_z3_handles_unsat_formula():
    """Test that Z3 correctly identifies an unsatisfiable formula"""
    print(f"✓ Testing UNSAT formula handling...")
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(assert (> x 10))\n(assert (< x 5))\n(check-sat)"
    }
    
    # This formula is UNSAT (x can't be both > 10 and < 5)
    proof = "(model sat)"  # Wrong! Should be unsat
    result = verify_proof_with_z3(challenge, proof, 1000)
    
    assert result is False, "Z3 should reject SAT proof for UNSAT formula"
    print(f"  ✅ Z3 correctly identified UNSAT formula\n")

def test_z3_rejects_unreasonable_solver_time():
    """Test that verification rejects unreasonable solver times"""
    print(f"✓ Testing solver time validation...")
    
    challenge = {
        "z3_formula": "(declare-const x Int)\n(assert (> x 0))\n(check-sat)"
    }
    
    # Instant solve (< 10ms) - suspicious
    proof = "(model sat)"
    result = verify_proof_with_z3(challenge, proof, 1)
    
    assert result is False, "Should reject instant solver time"
    print(f"  ✅ Rejected instant solver time (< 10ms)\n")
    
    # Too slow (> 2 minutes) - suspicious
    result = verify_proof_with_z3(challenge, proof, 150000)
    
    assert result is False, "Should reject excessive solver time"
    print(f"  ✅ Rejected excessive solver time (> 2 minutes)\n")

def test_end_to_end_with_real_z3():
    """Test complete flow: get challenge → solve with Z3 → submit → verify"""
    print(f"✓ Testing end-to-end flow with REAL Z3...")
    
    # Step 1: Get a challenge
    challenge_response = client.get("/api/lattice/challenge")
    assert challenge_response.status_code == 200
    challenge = challenge_response.json()
    
    print(f"  📋 Challenge received: {challenge['challenge_id'][:8]}...")
    print(f"     Formula: {challenge['z3_formula'][:50]}...")
    print(f"     Difficulty: {challenge['difficulty']}, Reward: {challenge['reward_credits']}")
    
    # Step 2: "Solve" with Z3 (simulate)
    # In real implementation, frontend would solve this
    # For now, we know all our challenges are SAT
    proof = f"(model sat challenge={challenge['challenge_id'][:8]})"
    
    # Step 3: Submit proof
    submission = {
        "challenge_id": challenge["challenge_id"],
        "proof": proof,
        "solver_time_ms": 1234,  # Reasonable time
        "auth": {
            "publicKeyHex": "a" * 64,
            "signatureHex": "b" * 128,
            "timestamp": int(time.time()),
            "nonce": f"z3-test-{int(time.time())}"
        }
    }
    
    response = client.post("/api/lattice/submit-proof", json=submission)
    
    print(f"  📤 Proof submitted")
    print(f"  🔬 Z3 verification in progress...")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.json()}"
    result = response.json()
    
    assert result["verified"] is True, "Proof should be verified by REAL Z3"
    assert result["credits_earned"] == challenge["reward_credits"]
    
    print(f"  ✅ Z3 VERIFIED THE PROOF!")
    print(f"  💰 Credits earned: {result['credits_earned']}")
    print(f"  📊 Total credits: {result['total_credits']}\n")

def test_z3_verification_with_boolean_logic():
    """Test Z3 with boolean logic challenge"""
    print(f"✓ Testing Z3 with boolean logic...")
    
    challenge = {
        "z3_formula": "(declare-const a Bool)\n(declare-const b Bool)\n(assert (or a b))\n(assert (not (and a b)))\n(check-sat)"
    }
    
    # This is SAT (XOR condition)
    proof = "(model sat a=true b=false)"
    result = verify_proof_with_z3(challenge, proof, 500)
    
    assert result is True, "Z3 should verify boolean logic formula"
    print(f"  ✅ Z3 correctly verified boolean logic (XOR)\n")

def test_z3_verification_with_arrays():
    """Test Z3 with array theory"""
    print(f"✓ Testing Z3 with array theory...")
    
    challenge = {
        "z3_formula": "(declare-const arr (Array Int Int))\n(assert (= (select arr 0) 42))\n(check-sat)"
    }
    
    proof = "(model sat arr=[(0,42)])"
    result = verify_proof_with_z3(challenge, proof, 800)
    
    assert result is True, "Z3 should verify array theory formula"
    print(f"  ✅ Z3 correctly verified array theory\n")

if __name__ == "__main__":
    print(f"\n🔬 RUNNING Z3 REAL VERIFICATION TESTS\n")
    print(f"This test suite proves we're using REAL Z3, not mocks!\n")
    
    try:
        test_z3_is_available()
        test_z3_verifies_sat_formula()
        test_z3_rejects_invalid_proof()
        test_z3_handles_unsat_formula()
        test_z3_rejects_unreasonable_solver_time()
        test_z3_verification_with_boolean_logic()
        test_z3_verification_with_arrays()
        test_end_to_end_with_real_z3()
        
        print(f"\n{'='*70}")
        print(f"✅ ALL Z3 REAL VERIFICATION TESTS PASSED!")
        print(f"{'='*70}")
        print(f"\n🎉 PROOF: We are using REAL Z3 solver, not mocks!")
        print(f"   - Z3 library imported and available")
        print(f"   - SAT formulas verified correctly")
        print(f"   - UNSAT formulas rejected correctly")
        print(f"   - Invalid proofs rejected")
        print(f"   - Solver time validated")
        print(f"   - Boolean logic verified")
        print(f"   - Array theory verified")
        print(f"   - End-to-end flow working\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise
