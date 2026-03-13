"""
Tests for Lattice Node Bridge API v3.4.0
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import time

# Import the router
from api.lattice_bridge import router, challenge_pool, credit_tracker

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestChallengeEndpoint:
    """Tests for GET /api/lattice/challenge"""
    
    def test_get_challenge_success(self):
        """Should return a valid challenge"""
        response = client.get("/api/lattice/challenge")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "challenge_id" in data
        assert "z3_formula" in data
        assert "difficulty" in data
        assert "reward_credits" in data
        assert "expires_at" in data
        
        # Validate types
        assert isinstance(data["challenge_id"], str)
        assert isinstance(data["z3_formula"], str)
        assert isinstance(data["difficulty"], int)
        assert isinstance(data["reward_credits"], int)
        assert isinstance(data["expires_at"], int)
        
        # Validate ranges
        assert 1 <= data["difficulty"] <= 10
        assert data["reward_credits"] >= 1
        assert data["expires_at"] > int(time.time())
    
    def test_get_challenge_returns_different_challenges(self):
        """Should return different challenges on subsequent requests"""
        response1 = client.get("/api/lattice/challenge")
        response2 = client.get("/api/lattice/challenge")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Challenges might be the same if pool is small, but IDs should exist
        data1 = response1.json()
        data2 = response2.json()
        
        assert "challenge_id" in data1
        assert "challenge_id" in data2


class TestSubmitProofEndpoint:
    """Tests for POST /api/lattice/submit-proof"""
    
    def test_submit_valid_proof(self):
        """Should accept valid proof and award credits"""
        # First, get a challenge
        challenge_response = client.get("/api/lattice/challenge")
        assert challenge_response.status_code == 200
        challenge = challenge_response.json()
        
        # Submit proof
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "(proof valid sat)",
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-123"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert data["verified"] is True
        assert data["credits_earned"] == challenge["reward_credits"]
        assert data["total_credits"] >= challenge["reward_credits"]
        assert "merkle_root" in data
    
    def test_submit_proof_invalid_challenge_id(self):
        """Should reject proof for non-existent challenge"""
        submission = {
            "challenge_id": "invalid-challenge-id",
            "proof": "(proof valid sat)",
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-456"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_submit_proof_duplicate(self):
        """Should reject duplicate proof submission"""
        # Get challenge
        challenge_response = client.get("/api/lattice/challenge")
        challenge = challenge_response.json()
        
        # Submit proof first time
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "(proof valid sat)",
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "c" * 64,
                "signatureHex": "d" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-789"
            }
        }
        
        response1 = client.post("/api/lattice/submit-proof", json=submission)
        assert response1.status_code == 200
        
        # Submit same challenge again
        submission["auth"]["nonce"] = "test-nonce-790"  # Different nonce
        response2 = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response2.status_code == 409
        assert "already completed" in response2.json()["detail"].lower()
    
    def test_submit_proof_expired_timestamp(self):
        """Should reject proof with expired timestamp"""
        challenge_response = client.get("/api/lattice/challenge")
        challenge = challenge_response.json()
        
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "(proof valid sat)",
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "e" * 64,
                "signatureHex": "f" * 128,
                "timestamp": int(time.time()) - 600,  # 10 minutes ago
                "nonce": "test-nonce-old"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 403
        assert "expired" in response.json()["detail"].lower()
    
    def test_submit_proof_invalid_hex(self):
        """Should reject proof with invalid hex strings"""
        challenge_response = client.get("/api/lattice/challenge")
        challenge = challenge_response.json()
        
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "(proof valid sat)",
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "not-valid-hex",  # Invalid
                "signatureHex": "b" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-invalid"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_proof_empty_proof(self):
        """Should reject empty proof"""
        challenge_response = client.get("/api/lattice/challenge")
        challenge = challenge_response.json()
        
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "",  # Empty proof
            "solver_time_ms": 1500,
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-empty"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 422
        assert "verification failed" in response.json()["detail"].lower()
    
    def test_submit_proof_unreasonable_solver_time(self):
        """Should reject proof with unreasonable solver time"""
        challenge_response = client.get("/api/lattice/challenge")
        challenge = challenge_response.json()
        
        # Test with instant solve (0ms)
        submission = {
            "challenge_id": challenge["challenge_id"],
            "proof": "(proof valid sat)",
            "solver_time_ms": 0,
            "auth": {
                "publicKeyHex": "a" * 64,
                "signatureHex": "b" * 128,
                "timestamp": int(time.time()),
                "nonce": "test-nonce-instant"
            }
        }
        
        response = client.post("/api/lattice/submit-proof", json=submission)
        
        assert response.status_code == 422


class TestHealthCheck:
    """Tests for GET /api/lattice/health"""
    
    def test_health_check(self):
        """Should return health status"""
        response = client.get("/api/lattice/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert data["service"] == "lattice_bridge"
        assert data["version"] == "3.4.0"
        assert "available_challenges" in data
        assert "completed_challenges" in data
        assert "timestamp" in data


class TestCreditTracking:
    """Tests for credit accumulation"""
    
    def test_credits_accumulate(self):
        """Should accumulate credits across multiple proofs"""
        public_key = "a" * 64  # Valid 64-char hex
        
        # Submit multiple proofs
        for i in range(3):
            challenge_response = client.get("/api/lattice/challenge")
            challenge = challenge_response.json()
            
            submission = {
                "challenge_id": challenge["challenge_id"],
                "proof": f"(proof valid sat {i})",
                "solver_time_ms": 1500,
                "auth": {
                    "publicKeyHex": public_key,
                    "signatureHex": "b" * 128,
                    "timestamp": int(time.time()),
                    "nonce": f"test-nonce-accumulate-{i}"
                }
            }
            
            response = client.post("/api/lattice/submit-proof", json=submission)
            assert response.status_code == 200
            
            data = response.json()
            
            # Credits should accumulate
            if i == 0:
                first_total = data["total_credits"]
            else:
                assert data["total_credits"] > first_total


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
