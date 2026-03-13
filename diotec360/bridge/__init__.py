"""
Payment Gateway Bridges
Connectors for external payment providers
"""

from .stripe_connector import (
    StripeConnector,
    StripePurchaseFlow,
    StripeWebhookHandler,
    CREDIT_PACKAGES as STRIPE_PACKAGES
)

from .paypal_connector import (
    PayPalConnector,
    PayPalPurchaseFlow,
    PayPalWebhookHandler,
    CREDIT_PACKAGES as PAYPAL_PACKAGES
)

# Use PayPal packages as default (Angola compliance)
CREDIT_PACKAGES = PAYPAL_PACKAGES

__all__ = [
    # Stripe
    "StripeConnector",
    "StripePurchaseFlow",
    "StripeWebhookHandler",
    # PayPal (Primary for Angola)
    "PayPalConnector",
    "PayPalPurchaseFlow",
    "PayPalWebhookHandler",
    # Packages
    "CREDIT_PACKAGES",
    "STRIPE_PACKAGES",
    "PAYPAL_PACKAGES"
]
