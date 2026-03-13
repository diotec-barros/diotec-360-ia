#!/usr/bin/env python3
"""
DIOTEC 360 IA - Treasury Endpoints Test
Tests all Treasury API endpoints on Hugging Face
"""

import requests
import json
import time

# Configuration
API_URL = "https://diotec-360-diotec-360-ia-judge.hf.space"
TEST_USER_ID = "test_user_dionisio_001"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_test(name, status, details=""):
    icon = "✅" if status else "❌"
    print(f"\n{icon} {name}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Test basic health check"""
    print_header("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        success = response.status_code == 200
        print_test("Health Endpoint", success, f"Status: {response.status_code}")
        if success:
            print(f"   Response: {response.json()}")
        return success
    except Exception as e:
        print_test("Health Endpoint", False, f"Error: {e}")
        return False

def test_treasury_health():
    """Test Treasury health endpoint"""
    print_header("2. TREASURY HEALTH")
    
    try:
        response = requests.get(f"{API_URL}/api/treasury/health", timeout=10)
        success = response.status_code == 200
        print_test("Treasury Health", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            
            # Check PayPal configuration
            paypal_configured = data.get("paypal_configured", False)
            print_test("PayPal Configured", paypal_configured, 
                      "PayPal is ready" if paypal_configured else "PayPal needs configuration")
        
        return success
    except Exception as e:
        print_test("Treasury Health", False, f"Error: {e}")
        return False

def test_balance_check():
    """Test balance check endpoint"""
    print_header("3. BALANCE CHECK")
    
    try:
        response = requests.get(
            f"{API_URL}/api/treasury/balance",
            params={"user_public_key": "test_pubkey_" + TEST_USER_ID},
            timeout=10
        )
        success = response.status_code == 200
        print_test("Balance Check", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            print(f"   User: {TEST_USER_ID}")
            print(f"   Balance: {data.get('balance', 0)} credits")
            print(f"   Response: {json.dumps(data, indent=2)}")
        elif response.status_code == 422:
            print(f"   Schema validation error (expected for new endpoint)")
            print(f"   Response: {response.text[:200]}")
        
        return success
    except Exception as e:
        print_test("Balance Check", False, f"Error: {e}")
        return False

def test_purchase_starter():
    """Test credit purchase - Starter package"""
    print_header("4. CREDIT PURCHASE - STARTER PACKAGE")
    
    try:
        payload = {
            "user_public_key": "test_pubkey_" + TEST_USER_ID,
            "package": "starter",
            "return_url": "https://diotec360.com/payment/success",
            "cancel_url": "https://diotec360.com/payment/cancel"
        }
        
        print(f"   Requesting purchase...")
        print(f"   Package: Starter ($9.99 - 1,000 credits)")
        print(f"   User: {TEST_USER_ID}")
        
        response = requests.post(
            f"{API_URL}/api/treasury/purchase",
            json=payload,
            timeout=15
        )
        
        success = response.status_code == 200
        print_test("Purchase Request", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            print(f"\n   Response:")
            print(f"   {json.dumps(data, indent=2)}")
            
            if "approval_url" in data:
                print(f"\n   ✅ PayPal Approval URL Generated!")
                print(f"   URL: {data['approval_url']}")
                print(f"\n   📋 Next Steps:")
                print(f"   1. Open the approval URL in browser")
                print(f"   2. Login to PayPal Sandbox")
                print(f"   3. Complete payment")
                print(f"   4. Webhook will notify backend")
                print(f"   5. Credits will be added automatically")
            
            if "order_id" in data:
                print(f"\n   Order ID: {data['order_id']}")
        else:
            print(f"   Error Response: {response.text[:500]}")
        
        return success
    except Exception as e:
        print_test("Purchase Request", False, f"Error: {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    print_header("5. API STATUS")
    
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=10)
        success = response.status_code == 200
        print_test("API Status", success, f"Status: {response.status_code}")
        
        if success:
            data = response.json()
            print(f"\n   Environment: {data.get('production', 'unknown')}")
            print(f"   Safe Mode: {data.get('safe_mode', 'unknown')}")
            print(f"   CORS Origins: {data.get('cors_origins', [])}")
            print(f"\n   Full Response:")
            print(f"   {json.dumps(data, indent=2)}")
        
        return success
    except Exception as e:
        print_test("API Status", False, f"Error: {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("  DIOTEC 360 IA - TREASURY ENDPOINTS TEST")
    print("  v3.6.0 - Global Launch Activation")
    print("=" * 70)
    print(f"\n  API URL: {API_URL}")
    print(f"  Test User: {TEST_USER_ID}")
    print(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    time.sleep(1)
    
    results.append(("Treasury Health", test_treasury_health()))
    time.sleep(1)
    
    results.append(("Balance Check", test_balance_check()))
    time.sleep(1)
    
    results.append(("Credit Purchase", test_purchase_starter()))
    time.sleep(1)
    
    results.append(("API Status", test_api_status()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n  Tests Passed: {passed}/{total}")
    print(f"  Success Rate: {(passed/total)*100:.1f}%")
    print()
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED!")
        print("  🏛️ O TESOURO ESTÁ 100% OPERACIONAL! 💰🚀🇦🇴")
    else:
        print(f"  ⚠️ {total - passed} test(s) failed")
        print("  Check the logs above for details")
    
    print("=" * 70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
