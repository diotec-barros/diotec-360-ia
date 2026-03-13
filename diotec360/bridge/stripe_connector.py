"""
Stripe Payment Connector - v3.5.2
Bridge between Stripe payments and DIOTEC 360 Treasury

This connector transforms real money (USD/EUR) into Aethel Credits
with mathematical proof of payment.

CRITICAL SECURITY:
1. All payments verified with Stripe API
2. Webhook signatures validated
3. Replay attacks prevented
4. Double-spending impossible
"""

import os
import time
import logging
import hashlib
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("stripe package not installed. Install with: pip install stripe")

from ..core.treasury import (
    ProofOfPayment,
    PaymentProvider,
    TreasuryManager
)

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

# Credit packages (aligned with requirements.md)
CREDIT_PACKAGES = {
    "starter": {
        "credits": 1000,
        "price_usd": 9.99,
        "name": "Starter Package",
        "description": "1,000 Aethel Credits"
    },
    "professional": {
        "credits": 6000,
        "price_usd": 49.99,
        "name": "Professional Package",
        "description": "6,000 Aethel Credits (20% bonus)"
    },
    "enterprise": {
        "credits": 30000,
        "price_usd": 199.99,
        "name": "Enterprise Package",
        "description": "30,000 Aethel Credits (50% bonus)"
    }
}


# ============================================================================
# STRIPE CONNECTOR
# ============================================================================

class StripeConnector:
    """
    Stripe Payment Gateway Connector
    
    Handles:
    - Payment Intent creation
    - Webhook verification
    - Payment confirmation
    - ProofOfPayment generation
    
    SECURITY FEATURES:
    - Webhook signature verification
    - Replay attack prevention
    - Double-spending detection
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        webhook_secret: Optional[str] = None
    ):
        """
        Initialize Stripe connector
        
        Args:
            api_key: Stripe secret API key (or from env STRIPE_SECRET_KEY)
            webhook_secret: Stripe webhook secret (or from env STRIPE_WEBHOOK_SECRET)
        """
        if not STRIPE_AVAILABLE:
            raise ImportError("stripe package not installed")
        
        self.api_key = api_key or os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = webhook_secret or os.getenv("STRIPE_WEBHOOK_SECRET")
        
        if not self.api_key:
            raise ValueError("Stripe API key not provided")
        
        stripe.api_key = self.api_key
        
        # Track processed payment intents (prevent replay attacks)
        self.processed_payments: set = set()
        
        logger.info("[STRIPE] Connector initialized")
    
    def create_checkout_session(
        self,
        package: str,
        user_public_key: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict] = None
    ) -> Tuple[str, str]:
        """
        Create Stripe Checkout Session for credit purchase
        
        Args:
            package: Package name (starter, professional, enterprise)
            user_public_key: User's ED25519 public key
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            metadata: Additional metadata
            
        Returns:
            Tuple of (checkout_url, session_id)
            
        Raises:
            ValueError: If package is invalid
            stripe.error.StripeError: If Stripe API fails
        """
        # Validate package
        if package not in CREDIT_PACKAGES:
            raise ValueError(f"Invalid package: {package}")
        
        pkg = CREDIT_PACKAGES[package]
        
        # Generate unique client reference ID
        client_reference_id = self._generate_reference_id(user_public_key, package)
        
        # Prepare metadata
        session_metadata = {
            "user_public_key": user_public_key,
            "package": package,
            "credits": pkg["credits"],
            "client_reference_id": client_reference_id
        }
        
        if metadata:
            session_metadata.update(metadata)
        
        try:
            # Create Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": pkg["name"],
                            "description": pkg["description"],
                            "images": ["https://diotec360.com/assets/aethel-credits.png"]
                        },
                        "unit_amount": int(pkg["price_usd"] * 100)  # Cents
                    },
                    "quantity": 1
                }],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=client_reference_id,
                metadata=session_metadata,
                payment_intent_data={
                    "metadata": session_metadata
                }
            )
            
            logger.info(
                f"[STRIPE] Checkout session created: {session.id}",
                extra={
                    "session_id": session.id,
                    "package": package,
                    "credits": pkg["credits"],
                    "user": user_public_key[:16]
                }
            )
            
            return session.url, session.id
            
        except stripe.error.StripeError as e:
            logger.error(
                f"[STRIPE] Failed to create checkout session: {e}",
                exc_info=True
            )
            raise
    
    def verify_webhook(self, payload: bytes, signature: str) -> Dict:
        """
        Verify Stripe webhook signature and parse event
        
        CRITICAL SECURITY: This prevents attackers from sending fake
        webhook events to mint credits without payment.
        
        Args:
            payload: Raw webhook payload (bytes)
            signature: Stripe-Signature header value
            
        Returns:
            Parsed webhook event
            
        Raises:
            ValueError: If signature is invalid
            stripe.error.SignatureVerificationError: If verification fails
        """
        if not self.webhook_secret:
            raise ValueError("Webhook secret not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            
            logger.info(
                f"[STRIPE] Webhook verified: {event['type']}",
                extra={
                    "event_id": event["id"],
                    "event_type": event["type"]
                }
            )
            
            return event
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(
                f"[STRIPE] Webhook signature verification failed: {e}",
                exc_info=True
            )
            raise
    
    def process_payment_success(
        self,
        payment_intent_id: str
    ) -> ProofOfPayment:
        """
        Process successful payment and generate ProofOfPayment
        
        This is the CRITICAL FUNCTION that transforms real money
        into Aethel Credits with mathematical proof.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            
        Returns:
            ProofOfPayment for Treasury minting
            
        Raises:
            ValueError: If payment is invalid or already processed
            stripe.error.StripeError: If Stripe API fails
        """
        # SECURITY: Prevent replay attacks
        if payment_intent_id in self.processed_payments:
            raise ValueError(
                f"Payment already processed: {payment_intent_id}"
            )
        
        try:
            # Retrieve PaymentIntent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Validate payment status
            if payment_intent.status != "succeeded":
                raise ValueError(
                    f"Payment not succeeded: {payment_intent.status}"
                )
            
            # Extract metadata
            metadata = payment_intent.metadata
            package = metadata.get("package")
            credits = int(metadata.get("credits", 0))
            user_public_key = metadata.get("user_public_key")
            
            # Validate metadata
            if not package or not credits or not user_public_key:
                raise ValueError(
                    f"Invalid payment metadata: {metadata}"
                )
            
            # Calculate amount in USD
            amount_usd = payment_intent.amount / 100.0  # Convert cents to dollars
            
            # Get payer email (if available)
            payer_email = None
            if payment_intent.charges and payment_intent.charges.data:
                charge = payment_intent.charges.data[0]
                if charge.billing_details:
                    payer_email = charge.billing_details.email
            
            # Create ProofOfPayment
            proof = ProofOfPayment(
                payment_id=payment_intent_id,
                provider=PaymentProvider.STRIPE,
                amount_usd=amount_usd,
                amount_credits=credits,
                payer_email=payer_email,
                payment_status="succeeded",
                provider_metadata={
                    "package": package,
                    "stripe_customer": payment_intent.customer,
                    "payment_method": payment_intent.payment_method,
                    "created": payment_intent.created,
                    "currency": payment_intent.currency
                },
                verified=True,
                verified_at=int(time.time())
            )
            
            # Mark as processed (prevent replay)
            self.processed_payments.add(payment_intent_id)
            
            logger.info(
                f"[STRIPE] Payment processed: {payment_intent_id} "
                f"({credits} credits for {user_public_key[:16]}...)",
                extra={
                    "payment_intent_id": payment_intent_id,
                    "credits": credits,
                    "amount_usd": amount_usd,
                    "user": user_public_key[:16]
                }
            )
            
            return proof
            
        except stripe.error.StripeError as e:
            logger.error(
                f"[STRIPE] Failed to process payment: {e}",
                exc_info=True
            )
            raise
    
    def _generate_reference_id(self, user_public_key: str, package: str) -> str:
        """Generate unique client reference ID"""
        timestamp = int(time.time() * 1000000)  # Microseconds
        data = f"{user_public_key}:{package}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]


# ============================================================================
# INTEGRATED PURCHASE FLOW
# ============================================================================

class StripePurchaseFlow:
    """
    Complete purchase flow: Stripe → ProofOfPayment → Treasury Minting
    
    This orchestrates the entire flow from payment to credit minting
    with full security and audit trail.
    """
    
    def __init__(
        self,
        stripe_connector: StripeConnector,
        treasury_manager: TreasuryManager
    ):
        """
        Initialize purchase flow
        
        Args:
            stripe_connector: Stripe connector instance
            treasury_manager: Treasury manager instance
        """
        self.stripe = stripe_connector
        self.treasury = treasury_manager
        
        logger.info("[PURCHASE FLOW] Initialized")
    
    def initiate_purchase(
        self,
        package: str,
        user_public_key: str,
        success_url: str,
        cancel_url: str
    ) -> Tuple[str, str]:
        """
        Initiate credit purchase
        
        Args:
            package: Package name
            user_public_key: User's public key
            success_url: Success redirect URL
            cancel_url: Cancel redirect URL
            
        Returns:
            Tuple of (checkout_url, session_id)
        """
        return self.stripe.create_checkout_session(
            package=package,
            user_public_key=user_public_key,
            success_url=success_url,
            cancel_url=cancel_url
        )
    
    def complete_purchase(
        self,
        payment_intent_id: str,
        user_signature: str
    ) -> Dict:
        """
        Complete purchase after successful payment
        
        This is the CRITICAL FUNCTION that mints credits after
        verifying payment with Stripe.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID
            user_signature: User's ED25519 signature
            
        Returns:
            Dict with transaction details
            
        Raises:
            ValueError: If payment is invalid
        """
        # Step 1: Process payment and get proof
        proof = self.stripe.process_payment_success(payment_intent_id)
        
        # Step 2: Extract user public key from proof metadata
        user_public_key = proof.provider_metadata.get("user_public_key")
        if not user_public_key:
            # Fallback: extract from payment intent metadata
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            user_public_key = payment_intent.metadata.get("user_public_key")
        
        if not user_public_key:
            raise ValueError("User public key not found in payment metadata")
        
        # Step 3: Mint credits in Treasury
        transaction = self.treasury.mint_credits(
            user_public_key=user_public_key,
            amount=proof.amount_credits,
            proof_of_payment=proof,
            signature=user_signature
        )
        
        logger.info(
            f"[PURCHASE FLOW] Purchase completed: {transaction.transaction_id}",
            extra={
                "transaction_id": transaction.transaction_id,
                "payment_intent_id": payment_intent_id,
                "credits": proof.amount_credits,
                "user": user_public_key[:16]
            }
        )
        
        return {
            "success": True,
            "transaction_id": transaction.transaction_id,
            "credits_minted": proof.amount_credits,
            "balance": transaction.balance_after,
            "amount_usd": proof.amount_usd,
            "payment_id": payment_intent_id,
            "merkle_root": transaction.merkle_root
        }


# ============================================================================
# WEBHOOK HANDLER
# ============================================================================

class StripeWebhookHandler:
    """
    Handles Stripe webhook events
    
    Processes:
    - checkout.session.completed
    - payment_intent.succeeded
    - payment_intent.payment_failed
    """
    
    def __init__(
        self,
        stripe_connector: StripeConnector,
        purchase_flow: StripePurchaseFlow
    ):
        """
        Initialize webhook handler
        
        Args:
            stripe_connector: Stripe connector instance
            purchase_flow: Purchase flow instance
        """
        self.stripe = stripe_connector
        self.purchase_flow = purchase_flow
        
        logger.info("[WEBHOOK HANDLER] Initialized")
    
    def handle_webhook(
        self,
        payload: bytes,
        signature: str
    ) -> Dict:
        """
        Handle incoming Stripe webhook
        
        Args:
            payload: Raw webhook payload
            signature: Stripe-Signature header
            
        Returns:
            Dict with processing result
        """
        # Verify webhook signature
        event = self.stripe.verify_webhook(payload, signature)
        
        event_type = event["type"]
        
        # Handle different event types
        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(event)
        
        elif event_type == "payment_intent.succeeded":
            return self._handle_payment_succeeded(event)
        
        elif event_type == "payment_intent.payment_failed":
            return self._handle_payment_failed(event)
        
        else:
            logger.info(f"[WEBHOOK] Unhandled event type: {event_type}")
            return {"handled": False, "event_type": event_type}
    
    def _handle_checkout_completed(self, event: Dict) -> Dict:
        """Handle checkout.session.completed event"""
        session = event["data"]["object"]
        payment_intent_id = session.get("payment_intent")
        
        if not payment_intent_id:
            logger.warning("[WEBHOOK] No payment_intent in checkout session")
            return {"handled": False, "reason": "no_payment_intent"}
        
        logger.info(
            f"[WEBHOOK] Checkout completed: {session['id']} "
            f"(payment_intent: {payment_intent_id})"
        )
        
        # Payment will be processed in payment_intent.succeeded event
        return {"handled": True, "event_type": "checkout.session.completed"}
    
    def _handle_payment_succeeded(self, event: Dict) -> Dict:
        """Handle payment_intent.succeeded event"""
        payment_intent = event["data"]["object"]
        payment_intent_id = payment_intent["id"]
        
        try:
            # Complete purchase (mint credits)
            result = self.purchase_flow.complete_purchase(
                payment_intent_id=payment_intent_id,
                user_signature="webhook_auto_signature"  # TODO: Get from metadata
            )
            
            logger.info(
                f"[WEBHOOK] Credits minted: {result['credits_minted']} "
                f"(transaction: {result['transaction_id']})"
            )
            
            return {
                "handled": True,
                "event_type": "payment_intent.succeeded",
                "result": result
            }
            
        except Exception as e:
            logger.error(
                f"[WEBHOOK] Failed to process payment: {e}",
                exc_info=True
            )
            return {
                "handled": False,
                "event_type": "payment_intent.succeeded",
                "error": str(e)
            }
    
    def _handle_payment_failed(self, event: Dict) -> Dict:
        """Handle payment_intent.payment_failed event"""
        payment_intent = event["data"]["object"]
        
        logger.warning(
            f"[WEBHOOK] Payment failed: {payment_intent['id']} "
            f"(reason: {payment_intent.get('last_payment_error', {}).get('message', 'unknown')})"
        )
        
        return {"handled": True, "event_type": "payment_intent.payment_failed"}
