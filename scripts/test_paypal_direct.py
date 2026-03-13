"""
Test PayPal API directly to diagnose 422 error
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment
load_dotenv()

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
SECRET = os.getenv("PAYPAL_SECRET")
MODE = os.getenv("PAYPAL_MODE", "sandbox")

API_BASE = "https://api-m.sandbox.paypal.com" if MODE == "sandbox" else "https://api-m.paypal.com"

print("=" * 70)
print("PAYPAL DIRECT API TEST - Diagnosing 422 Error")
print("=" * 70)
print(f"Mode: {MODE}")
print(f"API Base: {API_BASE}")
print(f"Client ID: {CLIENT_ID[:20]}...")
print()

# Step 1: Get Access Token
print("Step 1: Getting Access Token...")
auth_url = f"{API_BASE}/v1/oauth2/token"
auth_response = requests.post(
    auth_url,
    headers={"Accept": "application/json", "Accept-Language": "en_US"},
    auth=(CLIENT_ID, SECRET),
    data={"grant_type": "client_credentials"}
)

if auth_response.status_code != 200:
    print(f"❌ Authentication failed: {auth_response.status_code}")
    print(auth_response.text)
    exit(1)

token = auth_response.json()["access_token"]
print(f"✅ Access token obtained: {token[:20]}...")
print()

# Step 2: Create Order with minimal payload
print("Step 2: Creating Order with MINIMAL payload...")
order_data = {
    "intent": "CAPTURE",
    "purchase_units": [{
        "amount": {
            "currency_code": "USD",
            "value": "9.99"
        }
    }]
}

print("Payload:")
print(json.dumps(order_data, indent=2))
print()

order_url = f"{API_BASE}/v2/checkout/orders"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

order_response = requests.post(order_url, headers=headers, json=order_data)

print(f"Response Status: {order_response.status_code}")
print("Response Body:")
print(json.dumps(order_response.json(), indent=2))
print()

if order_response.status_code == 201:
    print("✅ Order created successfully!")
    order_id = order_response.json()["id"]
    print(f"Order ID: {order_id}")
else:
    print(f"❌ Order creation failed: {order_response.status_code}")
    
print("=" * 70)


# Step 3: Test with additional fields
print("\nStep 3: Testing with additional fields...")
order_data_full = {
    "intent": "CAPTURE",
    "purchase_units": [{
        "reference_id": "test_ref_123",
        "description": "DIOTEC 360 IA - Starter Package (1,000 credits)",
        "custom_id": "test_custom_123",
        "amount": {
            "currency_code": "USD",
            "value": "9.99"
        }
    }],
    "application_context": {
        "return_url": "https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/success",
        "cancel_url": "https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/cancel",
        "brand_name": "DIOTEC 360 IA",
        "landing_page": "LOGIN",
        "user_action": "PAY_NOW",
        "shipping_preference": "NO_SHIPPING"
    }
}

print("Full Payload:")
print(json.dumps(order_data_full, indent=2))
print()

order_response_full = requests.post(order_url, headers=headers, json=order_data_full)

print(f"Response Status: {order_response_full.status_code}")
print("Response Body:")
print(json.dumps(order_response_full.json(), indent=2))
print()

if order_response_full.status_code == 201:
    print("✅ Full order created successfully!")
    order_id = order_response_full.json()["id"]
    print(f"Order ID: {order_id}")
else:
    print(f"❌ Full order creation failed: {order_response_full.status_code}")
    
print("=" * 70)
