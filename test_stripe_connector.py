"""
Tests for Stripe Payment Connector
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from diotec360.bridge.stripe_connector import (
    StripeConnector,
    StripePurchaseFlow,
    StripeWebhookHandler,
    CREDIT_PACKAGES
)
from diotec360.core.treasury import (
    TreasuryManager,
    ProofOfPayment,
    PaymentProvider
)


class TestCreditPackages:
    """Test credit package configuration"""
    
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
    
    def test_professional_package(self):
        """Test professional package with bonus"""
        pkg = CREDIT_PACKAGES["professional"]
        assert pkg["credits"] == 6000  # 20% bonus
        assert pkg["price_usd"] == 49.99
    
    def test_enterprise_package(self):
        """Test enterprise package with bonus"""
        pkg = CREDIT_PACKAGES["enterprise"]
        assert pkg["credits"] == 30000  # 50% bonus
        assert pkg["price_usd"] == 199.99


@pytest.mark.skipif(
    not hasattr(StripeConnector, '__init__'),
    reason="Stripe not available"
)
class TestStripeConnector:
    """Test Stripe connector (mocked)"""
    
    @patch('diotec360.bridge.stripe_connector.stripe')
    def test_create_checkout_session(self, mock_stripe):
        """Test checkout session creation"""
        # Mock Stripe API
        mock_session = Mock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/test"
        mock_stripe.checkout.Session.create.return_value = mock_session
        
        # Create connector
        connector = StripeConnector(api_key="sk_test_123")
        
        # Create checkout session
        url, session_id = connector.create_checkout_session(
            package="starter",
            user_public_key="test_user_abc",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel"
        )
        
        assert url == "https://checkout.stripe.com/test"
        assert session_id == "cs_test_123"
        
        # Verify Stripe API was called
        mock_stripe.checkout.Session.create.assert_called_once()
    
    @patch('diotec360.bridge.stripe_connector.stripe')
    def test_create_checkout_invalid_package(self, mock_stripe):
        """Test checkout with invalid package"""
        connector = StripeConnector(api_key="sk_test_123")
        
        with pytest.raises(ValueError, match="Invalid package"):
            connector.create_checkout_session(
                package="invalid_package",
                user_public_key="test_user",
                success_url="https://example.com/success",
                cancel_url="https://example.com/cancel"
            )
    
    @patch('diotec360.bridge.stripe_connector.stripe')
    def test_process_payment_success(self, mock_stripe):
        """Test processing successful payment"""
        # Mock PaymentIntent
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test_456"
        mock_payment_intent.status = "succeeded"
        mock_payment_intent.amount = 999  # $9.99 in cents
        mock_payment_intent.currency = "usd"
        mock_payment_intent.metadata = {
            "package": "starter",
            "credits": "1000",
            "user_public_key": "test_user_xyz"
        }
        mock_payment_intent.charges = Mock()
        mock_payment_intent.charges.data = []
        mock_payment_intent.customer = "cus_test"
        mock_payment_intent.payment_method = "pm_test"
        mock_payment_intent.created = 1234567890
        
        mock_stripe.PaymentIntent.retrieve.return_value = mock_payment_intent
        
        # Create connector
        connector = StripeConnector(api_key="sk_test_123")
        
        # Process payment
        proof = connector.process_payment_success("pi_test_456")
        
        # Verify proof
        assert proof.payment_id == "pi_test_456"
        assert proof.provider == PaymentProvider.STRIPE
        assert proof.amount_usd == 9.99
        assert proof.amount_credits == 1000
        assert proof.payment_status == "succeeded"
        assert proof.verified is True
        assert proof.is_valid() is True
    
    @patch('diotec360.bridge.stripe_connector.stripe')
    def test_process_payment_replay_attack_prevented(self, mock_stripe):
        """Test that replay attacks are prevented"""
        # Mock PaymentIntent
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_replay_test"
        mock_payment_intent.status = "succeeded"
        mock_payment_intent.amount = 999
        mock_payment_intent.metadata = {
            "package": "starter",
            "credits": "1000",
            "user_public_key": "test_user"
        }
        mock_payment_intent.charges = Mock()
        mock_payment_intent.charges.data = []
        mock_payment_intent.customer = "cus_test"
        mock_payment_intent.payment_method = "pm_test"
        mock_payment_intent.created = 1234567890
        
        mock_stripe.PaymentIntent.retrieve.return_value = mock_payment_intent
        
        connector = StripeConnector(api_key="sk_test_123")
        
        # First processing should succeed
        proof1 = connector.process_payment_success("pi_replay_test")
        assert proof1.is_valid()
        
        # Second processing should fail (replay attack)
        with pytest.raises(ValueError, match="Payment already processed"):
            connector.process_payment_success("pi_replay_test")


@pytest.mark.skipif(
    not hasattr(StripeConnector, '__init__'),
    reason="Stripe not available"
)
class TestStripePurchaseFlow:
    """Test complete purchase flow"""
    
    @patch('diotec360.bridge.stripe_connector.stripe')
    def test_complete_purchase_flow(self, mock_stripe):
        """Test complete purchase from payment to minting"""
        # Mock PaymentIntent
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_flow_test"
        mock_payment_intent.status = "succeeded"
        mock_payment_intent.amount = 999
        mock_payment_intent.metadata = {
            "package": "starter",
            "credits": "1000",
            "user_public_key": "test_user_flow"
        }
        mock_payment_intent.charges = Mock()
        mock_payment_intent.charges.data = []
        mock_payment_intent.customer = "cus_test"
        mock_payment_intent.payment_method = "pm_test"
        mock_payment_intent.created = 1234567890
        
        mock_stripe.PaymentIntent.retrieve.return_value = mock_payment_intent
        
        # Create components
        stripe_connector = StripeConnector(api_key="sk_test_123")
        treasury = TreasuryManager()
        purchase_flow = StripePurchaseFlow(stripe_connector, treasury)
        
        # Complete purchase
        result = purchase_flow.complete_purchase(
            payment_intent_id="pi_flow_test",
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
