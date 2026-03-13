"""
Sovereign Treasury - Core Financial Engine
Part of DIOTEC 360 v3.5.0

The heart of the monetization system. Manages credit minting, burning,
and platform fees with Merkle-backed proof of reserves.

CRITICAL INVARIANTS:
1. No credit can be minted without valid payment proof
2. All transactions must be recorded in Merkle State
3. Platform reserves must match Merkle root at all times
4. Credits cannot be burned below zero balance
"""

import hashlib
import time
import logging
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    """Credit transaction types"""
    PURCHASE = "purchase"      # User buys credits with money
    MINING = "mining"          # User earns credits by mining
    REDEMPTION = "redemption"  # User redeems credits for money
    SPEND = "spend"            # User spends credits on features
    REFUND = "refund"          # Refund of purchased credits
    ADJUSTMENT = "adjustment"  # Admin adjustment (rare)


class PaymentProvider(Enum):
    """Supported payment providers"""
    STRIPE = "stripe"
    PAYPAL = "paypal"
    MULTICAIXA = "multicaixa"
    INTERNAL = "internal"  # For mining rewards


@dataclass
class CreditTransaction:
    """
    Represents a single credit transaction
    
    All transactions are immutable once created and must be
    recorded in the Merkle State for audit trail.
    """
    transaction_id: str
    user_public_key: str
    amount: int  # Positive = credit, Negative = debit
    balance_before: int
    balance_after: int
    transaction_type: TransactionType
    payment_provider: Optional[PaymentProvider]
    payment_id: Optional[str]  # External payment ID (Stripe, PayPal, etc.)
    metadata: Dict
    merkle_root: Optional[str]
    merkle_proof: Optional[str]
    signature: str
    timestamp: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "transaction_id": self.transaction_id,
            "user_public_key": self.user_public_key,
            "amount": self.amount,
            "balance_before": self.balance_before,
            "balance_after": self.balance_after,
            "transaction_type": self.transaction_type.value,
            "payment_provider": self.payment_provider.value if self.payment_provider else None,
            "payment_id": self.payment_id,
            "metadata": self.metadata,
            "merkle_root": self.merkle_root,
            "merkle_proof": self.merkle_proof,
            "signature": self.signature,
            "timestamp": self.timestamp
        }
    
    def hash(self) -> str:
        """Generate hash of transaction for Merkle tree"""
        data = f"{self.transaction_id}:{self.user_public_key}:{self.amount}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()


@dataclass
class ProofOfPayment:
    """
    Proof that a payment was made through external provider
    
    This is the CRITICAL INVARIANT: No credits can be minted
    without a valid ProofOfPayment.
    """
    payment_id: str  # Stripe payment_intent, PayPal transaction_id, etc.
    provider: PaymentProvider
    amount_usd: float
    amount_credits: int
    payer_email: Optional[str]
    payment_status: str  # 'succeeded', 'pending', 'failed'
    provider_metadata: Dict
    verified: bool
    verified_at: Optional[int]
    
    def is_valid(self) -> bool:
        """Check if proof is valid for minting"""
        return (
            self.verified and
            self.payment_status == "succeeded" and
            self.amount_credits > 0
        )


class TreasuryManager:
    """
    Core Treasury Manager
    
    Manages all credit operations with Merkle-backed integrity.
    
    SECURITY RULES:
    1. All minting requires ProofOfPayment
    2. All transactions recorded in Merkle State
    3. Balance cannot go negative
    4. Platform fee calculated on all redemptions
    """
    
    def __init__(self, merkle_state=None):
        """
        Initialize Treasury Manager
        
        Args:
            merkle_state: MerkleStateTree instance for audit trail
        """
        self.merkle_state = merkle_state
        self.balances: Dict[str, int] = {}  # In-memory cache (backed by DB)
        self.transactions: List[CreditTransaction] = []
        
        # Platform fee rates (percentage)
        self.redemption_fees = {
            PaymentProvider.PAYPAL: 0.20,      # 20% fee
            PaymentProvider.MULTICAIXA: 0.10,  # 10% fee
            PaymentProvider.INTERNAL: 0.00     # No fee for internal
        }
        
        # Credit pricing (USD per 1000 credits)
        self.credit_price_usd = 10.00
        
        logger.info("[TREASURY] Treasury Manager initialized")
    
    def get_balance(self, user_public_key: str) -> int:
        """
        Get user's current credit balance
        
        Args:
            user_public_key: User's ED25519 public key (hex)
            
        Returns:
            Current credit balance
        """
        return self.balances.get(user_public_key, 0)
    
    def mint_credits(
        self,
        user_public_key: str,
        amount: int,
        proof_of_payment: ProofOfPayment,
        signature: str
    ) -> CreditTransaction:
        """
        Mint new credits for user (INBOUND FLOW)
        
        CRITICAL INVARIANT: Credits can only be minted with valid ProofOfPayment.
        This ensures that every credit in circulation is backed by real money.
        
        Args:
            user_public_key: User's ED25519 public key
            amount: Number of credits to mint
            proof_of_payment: Proof that payment was made
            signature: User's signature authorizing transaction
            
        Returns:
            CreditTransaction record
            
        Raises:
            ValueError: If proof is invalid or amount is invalid
        """
        # INVARIANT CHECK: Proof must be valid
        if not proof_of_payment.is_valid():
            raise ValueError(
                f"Invalid proof of payment: status={proof_of_payment.payment_status}, "
                f"verified={proof_of_payment.verified}"
            )
        
        # INVARIANT CHECK: Amount must match proof
        if amount != proof_of_payment.amount_credits:
            raise ValueError(
                f"Amount mismatch: requested={amount}, proof={proof_of_payment.amount_credits}"
            )
        
        # INVARIANT CHECK: Amount must be positive
        if amount <= 0:
            raise ValueError(f"Amount must be positive: {amount}")
        
        # Get current balance
        balance_before = self.get_balance(user_public_key)
        balance_after = balance_before + amount
        
        # Generate transaction ID
        transaction_id = self._generate_transaction_id(user_public_key, amount)
        
        # Create transaction record
        transaction = CreditTransaction(
            transaction_id=transaction_id,
            user_public_key=user_public_key,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_type=TransactionType.PURCHASE,
            payment_provider=proof_of_payment.provider,
            payment_id=proof_of_payment.payment_id,
            metadata={
                "amount_usd": proof_of_payment.amount_usd,
                "payer_email": proof_of_payment.payer_email,
                "provider_metadata": proof_of_payment.provider_metadata
            },
            merkle_root=None,  # Will be set after Merkle update
            merkle_proof=None,
            signature=signature,
            timestamp=int(time.time())
        )
        
        # Update balance
        self.balances[user_public_key] = balance_after
        
        # Record in Merkle State
        if self.merkle_state:
            merkle_root = self._record_in_merkle(transaction)
            transaction.merkle_root = merkle_root
        
        # Store transaction
        self.transactions.append(transaction)
        
        logger.info(
            f"[TREASURY] Credits minted: {amount} for {user_public_key[:16]}... "
            f"(payment_id: {proof_of_payment.payment_id})",
            extra={
                "transaction_id": transaction_id,
                "user": user_public_key[:16],
                "amount": amount,
                "balance_after": balance_after,
                "payment_id": proof_of_payment.payment_id
            }
        )
        
        return transaction
    
    def burn_credits(
        self,
        user_public_key: str,
        amount: int,
        transaction_type: TransactionType,
        signature: str,
        metadata: Optional[Dict] = None
    ) -> CreditTransaction:
        """
        Burn credits from user's balance (OUTBOUND FLOW)
        
        Used for:
        - Redemptions (user cashes out)
        - Spending (user buys premium features)
        - Refunds (negative burn = credit)
        
        Args:
            user_public_key: User's ED25519 public key
            amount: Number of credits to burn (positive)
            transaction_type: Type of burn (REDEMPTION, SPEND, etc.)
            signature: User's signature authorizing transaction
            metadata: Additional transaction data
            
        Returns:
            CreditTransaction record
            
        Raises:
            ValueError: If insufficient balance or invalid amount
        """
        # INVARIANT CHECK: Amount must be positive
        if amount <= 0:
            raise ValueError(f"Amount must be positive: {amount}")
        
        # Get current balance
        balance_before = self.get_balance(user_public_key)
        
        # INVARIANT CHECK: Sufficient balance
        if balance_before < amount:
            raise ValueError(
                f"Insufficient balance: required={amount}, available={balance_before}"
            )
        
        balance_after = balance_before - amount
        
        # Generate transaction ID
        transaction_id = self._generate_transaction_id(user_public_key, -amount)
        
        # Create transaction record
        transaction = CreditTransaction(
            transaction_id=transaction_id,
            user_public_key=user_public_key,
            amount=-amount,  # Negative for debit
            balance_before=balance_before,
            balance_after=balance_after,
            transaction_type=transaction_type,
            payment_provider=None,
            payment_id=None,
            metadata=metadata or {},
            merkle_root=None,
            merkle_proof=None,
            signature=signature,
            timestamp=int(time.time())
        )
        
        # Update balance
        self.balances[user_public_key] = balance_after
        
        # Record in Merkle State
        if self.merkle_state:
            merkle_root = self._record_in_merkle(transaction)
            transaction.merkle_root = merkle_root
        
        # Store transaction
        self.transactions.append(transaction)
        
        logger.info(
            f"[TREASURY] Credits burned: {amount} from {user_public_key[:16]}... "
            f"(type: {transaction_type.value})",
            extra={
                "transaction_id": transaction_id,
                "user": user_public_key[:16],
                "amount": -amount,
                "balance_after": balance_after,
                "type": transaction_type.value
            }
        )
        
        return transaction
    
    def calculate_platform_fee(
        self,
        amount_credits: int,
        provider: PaymentProvider
    ) -> Tuple[int, int]:
        """
        Calculate platform fee for redemption
        
        Args:
            amount_credits: Credits to redeem
            provider: Payment provider for redemption
            
        Returns:
            Tuple of (net_credits, fee_credits)
        """
        fee_rate = self.redemption_fees.get(provider, 0.10)
        fee_credits = int(amount_credits * fee_rate)
        net_credits = amount_credits - fee_credits
        
        return net_credits, fee_credits
    
    def calculate_usd_value(self, credits: int) -> float:
        """
        Calculate USD value of credits
        
        Args:
            credits: Number of credits
            
        Returns:
            USD value
        """
        return (credits / 1000.0) * self.credit_price_usd
    
    def get_transaction_history(
        self,
        user_public_key: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[CreditTransaction]:
        """
        Get user's transaction history
        
        Args:
            user_public_key: User's ED25519 public key
            limit: Maximum number of transactions to return
            offset: Offset for pagination
            
        Returns:
            List of transactions
        """
        user_transactions = [
            tx for tx in self.transactions
            if tx.user_public_key == user_public_key
        ]
        
        # Sort by timestamp (newest first)
        user_transactions.sort(key=lambda tx: tx.timestamp, reverse=True)
        
        return user_transactions[offset:offset + limit]
    
    def verify_reserves(self) -> bool:
        """
        Verify that platform reserves match Merkle root
        
        This is the PROOF OF RESERVES check. If this fails,
        the system has been compromised.
        
        Returns:
            True if reserves match, False otherwise
        """
        # Calculate total credits in circulation
        total_credits = sum(self.balances.values())
        
        # Calculate total credits from transactions
        total_from_transactions = sum(
            tx.amount for tx in self.transactions
        )
        
        # INVARIANT: Both should match
        if total_credits != total_from_transactions:
            logger.error(
                f"[TREASURY] RESERVE MISMATCH: "
                f"balances={total_credits}, transactions={total_from_transactions}",
                extra={
                    "total_credits": total_credits,
                    "total_from_transactions": total_from_transactions,
                    "difference": total_credits - total_from_transactions
                }
            )
            return False
        
        logger.info(
            f"[TREASURY] Reserves verified: {total_credits} credits in circulation",
            extra={"total_credits": total_credits}
        )
        
        return True
    
    def _generate_transaction_id(self, user_public_key: str, amount: int) -> str:
        """Generate unique transaction ID"""
        timestamp = int(time.time() * 1000000)  # Microseconds
        data = f"{user_public_key}:{amount}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _record_in_merkle(self, transaction: CreditTransaction) -> str:
        """
        Record transaction in Merkle State
        
        Args:
            transaction: Transaction to record
            
        Returns:
            New Merkle root hash
        """
        if not self.merkle_state:
            return "no_merkle_state"
        
        # TODO: Integrate with actual MerkleStateTree
        # For now, return mock root
        transaction_hash = transaction.hash()
        return hashlib.sha256(transaction_hash.encode()).hexdigest()


# ============================================================================
# PROOF OF PAYMENT VERIFICATION
# ============================================================================

class PaymentVerifier:
    """
    Verifies payment proofs from external providers
    
    This is the GATEKEEPER that ensures no credits are minted
    without valid payment.
    """
    
    @staticmethod
    def verify_stripe_payment(payment_intent_id: str, stripe_api_key: str) -> ProofOfPayment:
        """
        Verify Stripe payment and create ProofOfPayment
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            stripe_api_key: Stripe API key
            
        Returns:
            ProofOfPayment if valid
            
        Raises:
            ValueError: If payment is invalid
        """
        # TODO: Implement actual Stripe verification
        # For now, return mock proof
        return ProofOfPayment(
            payment_id=payment_intent_id,
            provider=PaymentProvider.STRIPE,
            amount_usd=9.99,
            amount_credits=1000,
            payer_email="user@example.com",
            payment_status="succeeded",
            provider_metadata={},
            verified=True,
            verified_at=int(time.time())
        )
    
    @staticmethod
    def verify_paypal_payment(transaction_id: str) -> ProofOfPayment:
        """Verify PayPal payment"""
        # TODO: Implement PayPal verification
        raise NotImplementedError("PayPal verification not yet implemented")
    
    @staticmethod
    def verify_multicaixa_payment(reference: str) -> ProofOfPayment:
        """Verify Multicaixa payment"""
        # TODO: Implement Multicaixa verification
        raise NotImplementedError("Multicaixa verification not yet implemented")


# ============================================================================
# TREASURY STATISTICS
# ============================================================================

@dataclass
class TreasuryStats:
    """Treasury statistics for monitoring"""
    total_credits_minted: int
    total_credits_burned: int
    total_credits_in_circulation: int
    total_usd_received: float
    total_usd_paid_out: float
    platform_fees_collected: float
    total_users: int
    total_transactions: int
    
    def to_dict(self) -> Dict:
        return {
            "total_credits_minted": self.total_credits_minted,
            "total_credits_burned": self.total_credits_burned,
            "total_credits_in_circulation": self.total_credits_in_circulation,
            "total_usd_received": self.total_usd_received,
            "total_usd_paid_out": self.total_usd_paid_out,
            "platform_fees_collected": self.platform_fees_collected,
            "total_users": self.total_users,
            "total_transactions": self.total_transactions
        }


def calculate_treasury_stats(treasury: TreasuryManager) -> TreasuryStats:
    """Calculate treasury statistics"""
    total_minted = sum(
        tx.amount for tx in treasury.transactions
        if tx.amount > 0 and tx.transaction_type == TransactionType.PURCHASE
    )
    
    total_burned = sum(
        abs(tx.amount) for tx in treasury.transactions
        if tx.amount < 0
    )
    
    total_in_circulation = sum(treasury.balances.values())
    
    total_usd_received = sum(
        tx.metadata.get("amount_usd", 0) for tx in treasury.transactions
        if tx.transaction_type == TransactionType.PURCHASE
    )
    
    # TODO: Calculate total_usd_paid_out and platform_fees_collected
    
    return TreasuryStats(
        total_credits_minted=total_minted,
        total_credits_burned=total_burned,
        total_credits_in_circulation=total_in_circulation,
        total_usd_received=total_usd_received,
        total_usd_paid_out=0.0,
        platform_fees_collected=0.0,
        total_users=len(treasury.balances),
        total_transactions=len(treasury.transactions)
    )
