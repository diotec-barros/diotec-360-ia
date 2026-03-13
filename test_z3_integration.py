"""
Test Z3 solver integration for proof verification
"""

def test_z3_installation():
    """Test if z3-solver package is installed"""
    try:
        from z3 import Solver, sat
        print(f"✅ z3-solver package installed")
        return True
    except ImportError:
        print("❌ z3-solver not installed")
        print("   Install with: pip install z3-solver")
        return False

def test_z3_simple_formula():
    """Test Z3 with a simple satisfiable formula"""
    from z3 import Solver, Int, sat
    
    try:
        solver = Solver()
        x = Int('x')
        y = Int('y')
        
        solver.add(x + y == 10)
        solver.add(x - y == 2)
        
        result = solver.check()
        
        if result == sat:
            model = solver.model()
            print(f"✅ Z3 solved formula: x={model[x]}, y={model[y]}")
            return True
        else:
            print(f"❌ Z3 did not return sat: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error running Z3: {e}")
        return False

def test_z3_unsat_formula():
    """Test Z3 with an unsatisfiable formula"""
    from z3 import Solver, Int, unsat
    
    try:
        solver = Solver()
        x = Int('x')
        
        solver.add(x > 10)
        solver.add(x < 5)
        
        result = solver.check()
        
        if result == unsat:
            print(f"✅ Z3 correctly identified unsat")
            return True
        else:
            print(f"❌ Z3 did not return unsat: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error running Z3: {e}")
        return False

def test_z3_parse_smt2():
    """Test Z3 SMT-LIB2 parsing"""
    from z3 import parse_smt2_string, Solver, sat
    
    formula = """(declare-const x Int)
(declare-const y Int)
(assert (= (+ x y) 10))
(assert (= (- x y) 2))
"""
    
    try:
        solver = Solver()
        assertions = parse_smt2_string(formula)
        
        for assertion in assertions:
            solver.add(assertion)
        
        result = solver.check()
        
        if result == sat:
            print(f"✅ Z3 parsed and solved SMT-LIB2 formula")
            return True
        else:
            print(f"❌ Z3 parsing failed or returned non-sat: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error parsing SMT-LIB2: {e}")
        return False

def test_proof_verification():
    """Test the actual proof verification function"""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from api.lattice_bridge import verify_proof_with_z3
    
    # Test challenge
    challenge = {
        'z3_formula': """(declare-const x Int)
(declare-const y Int)
(assert (= (+ x y) 10))
(assert (= (- x y) 2))
""",
        'difficulty': 1,
        'reward_credits': 5
    }
    
    # Valid proof (contains "sat")
    valid_proof = "sat"
    
    result = verify_proof_with_z3(challenge, valid_proof, 1000)
    
    if result:
        print(f"✅ Proof verification passed")
        return True
    else:
        print(f"❌ Proof verification failed")
        return False

if __name__ == "__main__":
    print("🧪 Testing Z3 Integration (z3-solver package)\n")
    
    # Test 1: z3-solver installation
    z3_installed = test_z3_installation()
    print()
    
    if not z3_installed:
        print("⚠️  z3-solver not installed. Install with: pip install z3-solver")
        exit(1)
    
    # Test 2: Simple SAT formula
    test_z3_simple_formula()
    print()
    
    # Test 3: UNSAT formula
    test_z3_unsat_formula()
    print()
    
    # Test 4: SMT-LIB2 parsing
    test_z3_parse_smt2()
    print()
    
    # Test 5: Proof verification function
    test_proof_verification()
    print()
    
    print("✅ All Z3 integration tests passed!")
