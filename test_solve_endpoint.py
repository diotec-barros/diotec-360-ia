"""
Test the /api/lattice/solve endpoint with real Z3
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_solve_sat_formula():
    """Test solving a satisfiable formula"""
    response = client.post("/api/lattice/solve", json={
        "formula": "(declare-const x Int)\n(assert (> x 0))\n(assert (< x 10))\n(check-sat)",
        "timeout_ms": 5000
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["proof"] is not None
    assert "sat" in data["proof"].lower()
    assert data["solver_time_ms"] > 0
    assert data["solver_time_ms"] < 5000
    assert data["error"] is None

def test_solve_unsat_formula():
    """Test solving an unsatisfiable formula"""
    response = client.post("/api/lattice/solve", json={
        "formula": "(declare-const x Int)\n(assert (> x 10))\n(assert (< x 5))\n(check-sat)",
        "timeout_ms": 5000
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is False
    assert data["proof"] is None
    assert "unsatisfiable" in data["error"].lower()
    assert data["solver_time_ms"] > 0

def test_solve_invalid_formula():
    """Test solving an invalid formula"""
    response = client.post("/api/lattice/solve", json={
        "formula": "this is not valid Z3 syntax",
        "timeout_ms": 5000
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is False
    assert data["proof"] is None
    assert "parse" in data["error"].lower()

def test_solve_timeout_validation():
    """Test timeout validation"""
    # Too short timeout
    response = client.post("/api/lattice/solve", json={
        "formula": "(declare-const x Int)\n(assert (> x 0))\n(check-sat)",
        "timeout_ms": 50  # Less than 100ms minimum
    })
    
    assert response.status_code == 422  # Validation error

def test_solve_complex_formula():
    """Test solving a more complex formula"""
    response = client.post("/api/lattice/solve", json={
        "formula": """
(declare-const a Int)
(declare-const b Int)
(assert (= (+ a b) 10))
(assert (= (- a b) 2))
(check-sat)
""",
        "timeout_ms": 10000
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["proof"] is not None
    assert "sat" in data["proof"].lower()
    # Should find a=6, b=4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
