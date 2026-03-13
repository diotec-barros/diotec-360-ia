"""
Tests for Sovereign Treasury Core
"""

import pytest
from diotec360.core.treasury import (
    TreasuryManager,
    ProofOfPayment,
    PaymentProvider,
    TransactionType,
    PaymentVerifier,
    calculate_treasury_stats
)


class TestTreasuryManager:
    """Test Treasury Manager core functionality"""
    
    def test_initial_balance_is_zero(self):
        """Test that new users start with zero balance"""
        treasury = TreasuryManager()
        balance = treasury.get_balance("test_public_key_123")
        
        assert balance == 0
    
    def test_mint_credits_with_valid_proof(self):
        """Test minting credits with valid payment proof"""
        treasury = TreasuryManager()
        
        # Create valid proof of payment
        proof = ProofOfPayment(
            payment_id="pi_test_123",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        # Mint credits
        transaction = treasury.mint_credits(
            user_public_key="test_user_abc",
            amount=1000,
            proof_of_payment=proof,
            signature="test_signature"
        )
        
        # Verify transaction
        assert transaction.amount == 1000
        assert transaction.balance_before == 0
        assert transaction.balance_after == 1000
        assert transaction.transaction_type == TransactionType.PURCHASE
        assert transaction.payment_id == "pi_test_123"
        
        # Verify balance updated
        assert treasury.get_balance("test_user_abc") == 1000
    
    def test_mint_credits_fails_with_invalid_proof(self):
        """Test that minting fails with invalid proof"""
        treasury = TreasuryManager()
        
        # Create invalid proof (not verified)
        proof = ProofOfPayment(
            payment_id="pi_test_456",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="pending",  # Not succeeded
            provider_metadata={},
            verified=False,  # Not verified
            verified_at=None
        )
        
        # Attempt to mint should fail
        with pytest.raises(ValueError, match="Invalid proof of payment"):
            treasury.mint_credits(
                user_public_key="test_user_xyz",
                amount=1000,
                proof_of_payment=proof,
                signature="test_signature"
            )
    
    def test_mint_credits_fails_with_amount_mismatch(self):
        """Test that minting fails if amount doesn't match proof"""
        treasury = TreasuryManager()
        
        proof = ProofOfPayment(
            payment_id="pi_test_789",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,  # Proof says 1000
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        # Try to mint different amount
        with pytest.raises(ValueError, match="Amount mismatch"):
            treasury.mint_credits(
                user_public_key="test_user_xyz",
                amount=2000,  # Requesting 2000 (mismatch!)
                proof_of_payment=proof,
                signature="test_signature"
            )
    
    def test_burn_credits_success(self):
        """Test burning credits (spending/redemption)"""
        treasury = TreasuryManager()
        
        # First mint some credits
        proof = ProofOfPayment(
            payment_id="pi_test_burn",
            provider=PaymentProvider.STRIPE,
            amount_usd=49.99,
            amount_credits=5000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        treasury.mint_credits(
            user_public_key="test_user_burn",
            amount=5000,
            proof_of_payment=proof,
            signature="sig1"
        )
        
        # Now burn some credits
        transaction = treasury.burn_credits(
            user_public_key="test_user_burn",
            amount=2000,
            transaction_type=TransactionType.SPEND,
            signature="sig2",
            metadata={"feature_id": "premium_access"}
        )
        
        # Verify transaction
        assert transaction.amount == -2000  # Negative for debit
        assert transaction.balance_before == 5000
        assert transaction.balance_after == 3000
        assert transaction.transaction_type == TransactionType.SPEND
        
        # Verify balance updated
        assert treasury.get_balance("test_user_burn") == 3000
    
    def test_burn_credits_fails_insufficient_balance(self):
        """Test that burning fails with insufficient balance"""
        treasury = TreasuryManager()
        
        # Try to burn credits without having any
        with pytest.raises(ValueError, match="Insufficient balance"):
            treasury.burn_credits(
                user_public_key="test_user_poor",
                amount=1000,
                transaction_type=TransactionType.SPEND,
                signature="sig"
            )
    
    def test_calculate_platform_fee(self):
        """Test platform fee calculation"""
        treasury = TreasuryManager()
        
        # PayPal: 20% fee
        net, fee = treasury.calculate_platform_fee(1000, PaymentProvider.PAYPAL)
        assert net == 800
        assert fee == 200
        
        # Multicaixa: 10% fee
        net, fee = treasury.calculate_platform_fee(1000, PaymentProvider.MULTICAIXA)
        assert net == 900
        assert fee == 100
        
        # Internal: 0% fee
        net, fee = treasury.calculate_platform_fee(1000, PaymentProvider.INTERNAL)
        assert net == 1000
        assert fee == 0
    
    def test_calculate_usd_value(self):
        """Test USD value calculation"""
        treasury = TreasuryManager()
        
        # 1000 credits = $10.00
        assert treasury.calculate_usd_value(1000) == 10.00
        
        # 5000 credits = $50.00
        assert treasury.calculate_usd_value(5000) == 50.00
        
        # 500 credits = $5.00
        assert treasury.calculate_usd_value(500) == 5.00
    
    def test_transaction_history(self):
        """Test transaction history retrieval"""
        treasury = TreasuryManager()
        
        # Create multiple transactions
        proof1 = ProofOfPayment(
            payment_id="pi_1",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        proof2 = ProofOfPayment(
            payment_id="pi_2",
            provider=PaymentProvider.STRIPE,
            amount_usd=49.99,
            amount_credits=5000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567891
        )
        
        treasury.mint_credits("user_history", 1000, proof1, "sig1")
        treasury.mint_credits("user_history", 5000, proof2, "sig2")
        treasury.burn_credits("user_history", 2000, TransactionType.SPEND, "sig3")
        
        # Get history
        history = treasury.get_transaction_history("user_history")
        
        assert len(history) == 3
        # Transactions exist (order may vary due to timestamp precision)
        amounts = [tx.amount for tx in history]
        assert -2000 in amounts  # Burn transaction
        assert 1000 in amounts   # First mint
        assert 5000 in amounts   # Second mint
    
    def test_verify_reserves(self):
        """Test reserve verification (Proof of Reserves)"""
        treasury = TreasuryManager()
        
        # Add some transactions
        proof1 = ProofOfPayment(
            payment_id="pi_reserves_1",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        proof2 = ProofOfPayment(
            payment_id="pi_reserves_2",
            provider=PaymentProvider.STRIPE,
            amount_usd=19.99,
            amount_credits=2000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567891
        )
        
        treasury.mint_credits("user1", 1000, proof1, "sig1")
        treasury.mint_credits("user2", 2000, proof2, "sig2")
        treasury.burn_credits("user1", 500, TransactionType.SPEND, "sig3")
        
        # Verify reserves
        assert treasury.verify_reserves() is True
        
        # Total should be 2500 (1000 + 2000 - 500)
        total = sum(treasury.balances.values())
        assert total == 2500


class TestProofOfPayment:
    """Test ProofOfPayment validation"""
    
    def test_valid_proof(self):
        """Test that valid proof passes validation"""
        proof = ProofOfPayment(
            payment_id="pi_valid",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        assert proof.is_valid() is True
    
    def test_invalid_proof_not_verified(self):
        """Test that unverified proof fails validation"""
        proof = ProofOfPayment(
            payment_id="pi_invalid",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=False,  # Not verified
            verified_at=None
        )
        
        assert proof.is_valid() is False
    
    def test_invalid_proof_not_succeeded(self):
        """Test that non-succeeded payment fails validation"""
        proof = ProofOfPayment(
            payment_id="pi_pending",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="pending",  # Not succeeded
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        assert proof.is_valid() is False


class TestTreasuryStats:
    """Test treasury statistics calculation"""
    
    def test_calculate_stats(self):
        """Test statistics calculation"""
        treasury = TreasuryManager()
        
        # Add transactions
        proof1 = ProofOfPayment(
            payment_id="pi_stats_1",
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567890
        )
        
        proof2 = ProofOfPayment(
            payment_id="pi_stats_2",
            provider=PaymentProvider.STRIPE,
            amount_usd=49.99,
            amount_credits=5000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=1234567891
        )
        
        treasury.mint_credits("user1", 1000, proof1, "sig1")
        treasury.mint_credits("user2", 5000, proof2, "sig2")
        treasury.burn_credits("user1", 500, TransactionType.SPEND, "sig3")
        
        # Calculate stats
        stats = calculate_treasury_stats(treasury)
        
        assert stats.total_credits_minted == 6000  # 1000 + 5000
        assert stats.total_credits_burned == 500
        assert stats.total_credits_in_circulation == 5500  # 6000 - 500
        assert abs(stats.total_usd_received - 59.98) < 0.01  # Float comparison
        assert stats.total_users == 2
        assert stats.total_transactions == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
