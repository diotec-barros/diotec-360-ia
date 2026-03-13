"""
Treasury API - v3.6.0
Credit Purchase and Balance Management

Part of DIOTEC 360 Sovereign Treasury
Angola Compliant - PayPal Integration
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diotec360.core.treasury import TreasuryManager, ProofOfPayment
from diotec360.bridge.paypal_connector import PayPalConnector

router = APIRouter(prefix="/api/treasury", tags=["treasury"])

# Initialize treasury and PayPal connector
treasury = TreasuryManager()
paypal_connector: Optional[PayPalConnector] = None

# Try to initialize PayPal connector at startup
try:
    paypal_connector = PayPalConnector(
        client_id=os.getenv("PAYPAL_CLIENT_ID"),
        client_secret=os.getenv("PAYPAL_SECRET"),
        webhook_id=os.getenv("PAYPAL_WEBHOOK_ID"),
        sandbox=(os.getenv("PAYPAL_MODE", "sandbox") == "sandbox")
    )
    print("[TREASURY API] PayPal connector initialized successfully")
except Exception as e:
    print(f"[TREASURY API] Warning: PayPal connector initialization failed: {e}")
    paypal_connector = None

# Credit packages (must match frontend)
CREDIT_PACKAGES = {
    "starter": {
        "credits": 1000,
        "price": 9.99,
        "currency": "USD",
        "name": "Starter Package"
    },
    "professional": {
        "credits": 6000,
        "price": 49.99,
        "currency": "USD",
        "name": "Professional Package"
    },
    "enterprise": {
        "credits": 30000,
        "price": 199.99,
        "currency": "USD",
        "name": "Enterprise Package"
    }
}


class PurchaseRequest(BaseModel):
    """Credit purchase request"""
    package: str = Field(..., description="Package ID (starter, professional, enterprise)")
    user_public_key: str = Field(..., description="User's sovereign identity public key")
    payment_method: str = Field(default="paypal", description="Payment method")
    return_url: str = Field(..., description="URL to return after successful payment")
    cancel_url: str = Field(..., description="URL to return if payment is cancelled")


class BalanceResponse(BaseModel):
    """Credit balance response"""
    ok: bool
    credits: int
    public_key: str


class PurchaseResponse(BaseModel):
    """Purchase response with PayPal checkout URL"""
    ok: bool
    order_id: str
    approval_url: str
    package: str
    credits: int
    price: float


@router.post("/purchase", response_model=PurchaseResponse)
async def create_purchase(request: PurchaseRequest):
    """
    Create a credit purchase order
    
    This endpoint:
    1. Validates the package
    2. Creates a PayPal order
    3. Returns the approval URL for checkout
    """
    global paypal_connector
    
    # Validate package
    if request.package not in CREDIT_PACKAGES:
        raise HTTPException(status_code=400, detail=f"Invalid package: {request.package}")
    
    package = CREDIT_PACKAGES[request.package]
    
    # Check if PayPal connector is initialized
    if paypal_connector is None:
        raise HTTPException(
            status_code=500,
            detail="PayPal connector not initialized. Check environment variables."
        )
    
    try:
        # Create PayPal order using the correct method signature
        print(f"[TREASURY API] Creating PayPal order for package: {request.package}")
        print(f"[TREASURY API] User: {request.user_public_key[:16]}...")
        print(f"[TREASURY API] Amount: ${package['price']} USD")
        
        approval_url, order_id = paypal_connector.create_order(
            package=request.package,
            user_public_key=request.user_public_key,
            return_url=request.return_url,
            cancel_url=request.cancel_url
        )
        
        print(f"[TREASURY API] ✅ PayPal order created: {order_id}")
        print(f"[TREASURY API] Approval URL: {approval_url[:50]}...")
        
        return PurchaseResponse(
            ok=True,
            order_id=order_id,
            approval_url=approval_url,
            package=request.package,
            credits=package["credits"],
            price=package["price"]
        )
        
    except ValueError as e:
        # PayPal connector raised a validation error
        print(f"[TREASURY API] ❌ PayPal validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"PayPal validation error: {str(e)}"
        )
    except Exception as e:
        # Unexpected error - log details
        print(f"[TREASURY API] ❌ PayPal order creation failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create PayPal order: {type(e).__name__}: {str(e)}"
        )


@router.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    """
    PayPal webhook handler
    
    This endpoint:
    1. Verifies the webhook signature
    2. Processes payment completion
    3. Mints credits to user's account
    """
    global paypal_connector
    
    if paypal_connector is None:
        raise HTTPException(status_code=500, detail="PayPal connector not initialized")
    
    try:
        # Get webhook data
        body = await request.body()
        headers = dict(request.headers)
        
        # Verify webhook signature
        event_data = paypal_connector.verify_webhook(body, headers)
        
        # Handle payment completion
        if event_data["event_type"] == "PAYMENT.CAPTURE.COMPLETED":
            capture = event_data["resource"]
            
            # Extract payment details
            amount = float(capture["amount"]["value"])
            currency = capture["amount"]["currency_code"]
            transaction_id = capture["id"]
            custom_id = capture.get("custom_id", "")  # User public key
            
            # Find matching package
            package_key = None
            for key, pkg in CREDIT_PACKAGES.items():
                if abs(pkg["price"] - amount) < 0.01 and pkg["currency"] == currency:
                    package_key = key
                    break
            
            if not package_key:
                raise HTTPException(
                    status_code=400,
                    detail=f"No package found for amount {amount} {currency}"
                )
            
            package = CREDIT_PACKAGES[package_key]
            
            # Create proof of payment
            proof = ProofOfPayment(
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                payment_method="paypal",
                timestamp=capture.get("create_time", ""),
                payer_id=capture.get("payer", {}).get("payer_id", ""),
                metadata={"package": package_key, "custom_id": custom_id}
            )
            
            # Mint credits
            user_id = custom_id if custom_id else f"paypal_{proof.payer_id}"
            treasury.mint_credits(user_id, package["credits"], proof)
            
            return {"ok": True, "message": "Credits minted successfully"}
        
        return {"ok": True, "message": "Event processed"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Webhook processing failed: {str(e)}"
        )


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(user_public_key: str):
    """
    Get credit balance for a user
    
    Args:
        user_public_key: User's sovereign identity public key
    """
    try:
        balance = treasury.get_balance(user_public_key)
        
        return BalanceResponse(
            ok=True,
            credits=balance,
            public_key=user_public_key
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get balance: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "ok": True,
        "service": "treasury",
        "version": "3.6.0",
        "paypal_configured": paypal_connector is not None
    }
