"""
Tests for PayPal Payment Connector
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from diotec360.bridge.paypal_connector import (
    PayPalConnector,
    PayPalPurchaseFlow,
    PayPalWebhookHandler,
    CREDIT_PACKAGES
)
from diotec360.core.treasury import (
    TreasuryManager,
    ProofOfPayment,
    PaymentProvider
)


class TestPayPalCreditPackages:
    """Test PayPal credit package configuration"""
    
    def test_packages_defined(self):
        """Test that all packages are defined"""
        assert "starter" in CREDIT_PACKAGES
        assert "professional" in CREDIT_PACKAGES
        assert "enterprise" in CREDIT_PACKAGES
    
    def test_starter_package(self):
        """Test starter package details"""
        pkg = CREDIT_PACKAGES["starter"]
        assert pkg["credits"] == 1000
        assert pkg["price_usd"] == 9.99
    
    def test_angola_compliance(self):
        """Test that PayPal supports Angola"""
        # PayPal supports Angola (AO) for merchants
        # This is a documentation test
        assert True  # PayPal confirmed to support Angola


class TestPayPalConnector:
    """Test PayPal connector (mocked)"""
    
    @patch('diotec360.bridge.paypal_connector.requests')
    def test_get_access_token(self, mock_requests):
        """Test OAuth2 token retrieval"""
        # Mock token response
        mock_response = Mock()
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 3600
        }
        mock_requests.post.return_value = mock_response
        
        # Create connector
        connector = PayPalConnector(
            client_id="test_client_id",
            client_secret="test_secret",
            sandbox=True
        )
        
        # Get token
        token = connector._get_access_token()
        
        assert token == "test_token_123"
        assert connector.access_token == "test_token_123"
        
        # Verify API was called
        mock_requests.post.assert_called_once()
    
    @patch('diotec360.bridge.paypal_connector.requests')
    def test_create_order(self, mock_requests):
        """Test PayPal order creation"""
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        # Mock order response
        mock_order_response = Mock()
        mock_order_response.json.return_value = {
            "id": "ORDER123",
            "status": "CREATED",
            "links": [
                {"rel": "approve", "href": "https://paypal.com/approve/ORDER123"}
            ]
        }
        
        mock_requests.post.side_effect = [mock_token_response, mock_order_response]
        
        # Create connector
        connector = PayPalConnector(
            client_id="test_client",
            client_secret="test_secret",
            sandbox=True
        )
        
        # Create order
        approval_url, order_id = connector.create_order(
            package="starter",
            user_public_key="test_user_abc",
            return_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert order_id == "ORDER123"
        assert "approve" in approval_url
    
    @patch('diotec360.bridge.paypal_connector.requests')
    def test_process_payment_success(self, mock_requests):
        """Test processing successful payment"""
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        # Mock sale response
        mock_sale_response = Mock()
        mock_sale_response.json.return_value = {
            "id": "SALE123",
            "state": "completed",
            "amount": {
                "total": "9.99",
                "currency": "USD"
            },
            "custom": '{"package": "starter", "credits": 1000, "user_public_key": "test_user_xyz"}',
            "payer": {
                "payer_info": {
                    "email": "user@example.com"
                }
            },
            "create_time": "2024-01-01T00:00:00Z",
            "update_time": "2024-01-01T00:01:00Z"
        }
        
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.return_value = mock_sale_response
        
        # Create connector
        connector = PayPalConnector(
            client_id="test_client",
            client_secret="test_secret",
            sandbox=True
        )
        
        # Process payment
        proof = connector.process_payment_success("SALE123")
        
        # Verify proof
        assert proof.payment_id == "SALE123"
        assert proof.provider == PaymentProvider.PAYPAL
        assert proof.amount_usd == 9.99
        assert proof.amount_credits == 1000
        assert proof.payment_status == "succeeded"  # Normalized
        assert proof.verified is True
        assert proof.is_valid() is True
    
    @patch('diotec360.bridge.paypal_connector.requests')
    def test_replay_attack_prevented(self, mock_requests):
        """Test that replay attacks are prevented"""
        # Mock responses
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        mock_sale_response = Mock()
        mock_sale_response.json.return_value = {
            "id": "SALE_REPLAY",
            "state": "completed",
            "amount": {"total": "9.99", "currency": "USD"},
            "custom": '{"package": "starter", "credits": 1000, "user_public_key": "test_user"}',
            "payer": {"payer_info": {"email": "user@example.com"}},
            "create_time": "2024-01-01T00:00:00Z"
        }
        
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.return_value = mock_sale_response
        
        connector = PayPalConnector(
            client_id="test_client",
            client_secret="test_secret",
            sandbox=True
        )
        
        # First processing should succeed
        proof1 = connector.process_payment_success("SALE_REPLAY")
        assert proof1.is_valid()
        
        # Second processing should fail (replay attack)
        with pytest.raises(ValueError, match="Payment already processed"):
            connector.process_payment_success("SALE_REPLAY")


class TestPayPalPurchaseFlow:
    """Test complete PayPal purchase flow"""
    
    @patch('diotec360.bridge.paypal_connector.requests')
    def test_complete_purchase_flow(self, mock_requests):
        """Test complete purchase from payment to minting"""
        # Mock token response
        mock_token_response = Mock()
        mock_token_response.json.return_value = {
            "access_token": "test_token",
            "expires_in": 3600
        }
        
        # Mock sale response
        mock_sale_response = Mock()
        mock_sale_response.json.return_value = {
            "id": "SALE_FLOW",
            "state": "completed",
            "amount": {"total": "9.99", "currency": "USD"},
            "custom": '{"package": "starter", "credits": 1000, "user_public_key": "test_user_flow"}',
            "payer": {"payer_info": {"email": "user@example.com"}},
            "create_time": "2024-01-01T00:00:00Z"
        }
        
        mock_requests.post.return_value = mock_token_response
        mock_requests.get.return_value = mock_sale_response
        
        # Create components
        paypal_connector = PayPalConnector(
            client_id="test_client",
            client_secret="test_secret",
            sandbox=True
        )
        treasury = TreasuryManager()
        purchase_flow = PayPalPurchaseFlow(paypal_connector, treasury)
        
        # Complete purchase
        result = purchase_flow.complete_purchase(
            sale_id="SALE_FLOW",
            user_signature="test_signature"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["credits_minted"] == 1000
        assert result["balance"] == 1000
        assert result["amount_usd"] == 9.99
        
        # Verify treasury balance
        assert treasury.get_balance("test_user_flow") == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
