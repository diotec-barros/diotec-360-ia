"""
Test Treasury API - v3.6.0
Tests for credit purchase and balance endpoints
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.treasury_api import router, CREDIT_PACKAGES
from fastapi import FastAPI

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_health_check():
    """Test treasury health endpoint"""
    response = client.get("/api/treasury/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "treasury"
    assert data["version"] == "3.6.0"


def test_get_balance():
    """Test balance retrieval"""
    response = client.get("/api/treasury/balance?public_key=test_user_123")
    assert response.status_code == 200
    
    data = response.json()
    assert data["ok"] is True
    assert "credits" in data
    assert data["public_key"] == "test_user_123"
    assert isinstance(data["credits"], int)


def test_create_purchase_invalid_package():
    """Test purchase with invalid package"""
    response = client.post("/api/treasury/purchase", json={
        "package": "invalid_package",
        "user_public_key": "test_user_123",
        "payment_method": "paypal",
        "return_url": "http://localhost/success",
        "cancel_url": "http://localhost/cancel"
    })
    
    assert response.status_code == 400
    assert "Invalid package" in response.json()["detail"]


def test_credit_packages_structure():
    """Test that credit packages are properly structured"""
    assert "starter" in CREDIT_PACKAGES
    assert "professional" in CREDIT_PACKAGES
    assert "enterprise" in CREDIT_PACKAGES
    
    for key, package in CREDIT_PACKAGES.items():
        assert "credits" in package
        assert "price" in package
        assert "currency" in package
        assert "name" in package
        assert isinstance(package["credits"], int)
        assert isinstance(package["price"], (int, float))
        assert package["currency"] == "USD"


def test_purchase_request_validation():
    """Test purchase request validation"""
    # Missing required fields
    response = client.post("/api/treasury/purchase", json={
        "package": "starter"
    })
    
    assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
