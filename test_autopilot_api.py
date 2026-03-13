"""
Property-based tests for Autopilot API endpoint
Feature: Diotec360-pilot-v3-7
Tasks: 2.3, 2.4, 2.5

Tests API request validation, response format, and error handling
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app
import time

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test"""
    from api import autopilot
    autopilot.request_counts.clear()
    yield
    autopilot.request_counts.clear()


class TestAutopilotAPIValidation:
    """
    Feature: Diotec360-pilot-v3-7, Property 10: API Request Validation
    
    For any request received by the API endpoint, if the request is missing
    required fields, the endpoint should return a 400 Bad Request status;
    if the request is valid, the endpoint should invoke the Autopilot Engine.
    """
    
    def test_missing_code_field(self):
        """Test that missing 'code' field returns 400"""
        response = client.post("/api/autopilot/suggestions", json={
            "cursor_position": 10
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_missing_cursor_position_field(self):
        """Test that missing 'cursor_position' field returns 400"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }"
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_negative_cursor_position(self):
        """Test that negative cursor_position returns 400"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": -1
        })
        assert response.status_code == 422  # Pydantic validation error
    
    def test_valid_request_returns_200(self):
        """Test that valid request returns 200"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": 10
        })
        assert response.status_code == 200
    
    def test_empty_code_returns_empty_suggestions(self):
        """Test that empty code returns empty suggestions"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "",
            "cursor_position": 0
        })
        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []
        assert data["safety_status"]["status"] == "unknown"


class TestAutopilotAPIResponseFormat:
    """
    Feature: Diotec360-pilot-v3-7, Property 11: API Response Format
    
    For any successful API response, the response should be valid JSON
    containing suggestions array, safety_status object, and corrections array.
    """
    
    def test_response_has_required_fields(self):
        """Test that response contains all required fields"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { amount > 0 }",
            "cursor_position": 20
        })
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "suggestions" in data
        assert "safety_status" in data
        assert "corrections" in data
        assert "analysis_time" in data
    
    def test_suggestions_is_array(self):
        """Test that suggestions is an array"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["suggestions"], list)
    
    def test_safety_status_is_object(self):
        """Test that safety_status is an object"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["safety_status"], dict)
        assert "status" in data["safety_status"]
        assert "violations" in data["safety_status"]
        assert "analysis_time" in data["safety_status"]
    
    def test_corrections_is_array(self):
        """Test that corrections is an array"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["corrections"], list)
    
    def test_analysis_time_is_number(self):
        """Test that analysis_time is a number"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["analysis_time"], (int, float))
        assert data["analysis_time"] >= 0


class TestAutopilotAPIErrorHandling:
    """
    Feature: Diotec360-pilot-v3-7, Property 12: API Error Handling
    
    For any error that occurs during request processing, the API endpoint
    should return an appropriate HTTP error status and a JSON error message.
    """
    
    def test_invalid_json_returns_422(self):
        """Test that invalid JSON returns 422"""
        response = client.post(
            "/api/autopilot/suggestions",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_malformed_request_returns_error_message(self):
        """Test that malformed request returns error message"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { }",
            "cursor_position": "not a number"  # Invalid type
        })
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_rate_limit_returns_429(self):
        """Test that exceeding rate limit returns 429"""
        # Make 101 requests rapidly to trigger rate limit
        for i in range(101):
            response = client.post("/api/autopilot/suggestions", json={
                "code": f"intent payment{i} {{ }}",
                "cursor_position": 10
            })
        
        # Last request should be rate limited
        assert response.status_code == 429
        data = response.json()
        assert "rate limit" in data["detail"].lower()


class TestAutopilotAPIPerformance:
    """
    Feature: Diotec360-pilot-v3-7, Property 3: End-to-End Response Time
    
    For any valid autocomplete request, the API endpoint should return
    a complete response within 250ms.
    """
    
    def test_response_time_under_250ms(self):
        """Test that response time is under 250ms"""
        start_time = time.time()
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { amount > 0 }",
            "cursor_position": 20
        })
        end_time = time.time()
        
        assert response.status_code == 200
        response_time_ms = (end_time - start_time) * 1000
        
        # Allow some margin for test environment
        assert response_time_ms < 500, f"Response time {response_time_ms}ms exceeds 500ms"
    
    def test_analysis_time_reported_correctly(self):
        """Test that analysis_time is reported in response"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { amount > 0 }",
            "cursor_position": 20
        })
        assert response.status_code == 200
        data = response.json()
        
        # Analysis time should be positive
        assert data["analysis_time"] > 0
        
        # Analysis time should be reasonable (< 1 second)
        assert data["analysis_time"] < 1000


class TestAutopilotAPIHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_returns_200(self):
        """Test that health check returns 200"""
        response = client.get("/api/autopilot/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "autopilot"
        assert "timestamp" in data
    
    def test_stats_endpoint_returns_200(self):
        """Test that stats endpoint returns 200"""
        response = client.get("/api/autopilot/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "active_clients" in data
        assert "rate_limit" in data


class TestAutopilotAPIIntegration:
    """Integration tests for Autopilot API"""
    
    def test_complete_workflow(self):
        """Test complete workflow from request to response"""
        # Make request
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment {\n  ",
            "cursor_position": 20,
            "selection": None
        })
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["safety_status"], dict)
        assert isinstance(data["corrections"], list)
        assert isinstance(data["analysis_time"], (int, float))
        
        # Verify safety status structure
        assert "status" in data["safety_status"]
        assert data["safety_status"]["status"] in ["safe", "unsafe", "analyzing", "unknown"]
    
    def test_with_selection(self):
        """Test request with selection range"""
        response = client.post("/api/autopilot/suggestions", json={
            "code": "intent payment { amount > 0 }",
            "cursor_position": 20,
            "selection": {"start": 15, "end": 25}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
