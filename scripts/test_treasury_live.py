#!/usr/bin/env python3
"""
DIOTEC 360 IA - Live Treasury Test
Tests the deployed Treasury API on Hugging Face
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

def test_health():
    """Test basic health endpoint"""
    print_header("TEST 1: HEALTH CHECK")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        success = response.status_code == 200
        
        print_test(
            "Health Endpoint",
            success,
            f"Status: {response.status_code}, Response: {response.text[:100]}"
        )
        
        return success
    except Exception as e:
        print_test("Health Endpoint", False, f"Error: {e}")
        return False

def test_treasury_health():
    """Test Treasury health endpoint"""
    print_header("TEST 2: TREASURY HEALTH")
    
    try:
        response = requests.get(f"{API_URL}/api/treasury/health", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test(
                "Treasury Health",
                True,
                f"Service: {data.get('service')}, Version: {data.get('version')}"
            )
            print(f"   PayPal Configured: {data.get('paypal_configured')}")
        else:
            print_test(
                "Treasury Health",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
        
        return success
    except Exception as e:
        print_test("Treasury Health", False, f"Error: {e}")
        return False

def test_balance_check():
    """Test balance check endpoint"""
    print_header("TEST 3: BALANCE CHECK")
    
    try:
        # Generate a test public key (mock for testing)
        test_public_key = "test_public_key_" + TEST_USER_ID
        
        response = requests.get(
            f"{API_URL}/api/treasury/balance",
            params={
                "user_id": TEST_USER_ID,
                "public_key": test_public_key
            },
            timeout=10
        )
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test(
                "Balance Check",
                True,
                f"User: {TEST_USER_ID}"
            )
            print(f"   Balance: {data.get('balance', 0)} credits")
            print(f"   Currency: {data.get('currency', 'USD')}")
        else:
            print_test(
                "Balance Check",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
        
        return success
    except Exception as e:
        print_test("Balance Check", False, f"Error: {e}")
        return False

def test_purchase_starter():
    """Test credit purchase flow (Starter package)"""
    print_header("TEST 4: CREDIT PURCHASE (STARTER)")
    
    try:
        # Generate test keys
        test_public_key = "test_public_key_" + TEST_USER_ID
        test_return_url = "https://example.com/payment/return"
        test_cancel_url = "https://example.com/payment/cancel"
        
        payload = {
            "package": "starter",
            "user_id": TEST_USER_ID,
            "user_public_key": test_public_key,
            "return_url": test_return_url,
            "cancel_url": test_cancel_url
        }
        
        print(f"   Requesting purchase: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{API_URL}/api/treasury/purchase",
            json=payload,
            timeout=15
        )
        
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test(
                "Purchase Request",
                True,
                f"Order ID: {data.get('order_id', 'N/A')}"
            )
            
            if 'approval_url' in data:
                print(f"   Approval URL: {data['approval_url'][:80]}...")
                print(f"   Amount: ${data.get('amount', 0)}")
                print(f"   Credits: {data.get('credits', 0)}")
            else:
                print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print_test(
                "Purchase Request",
                False,
                f"Status: {response.status_code}"
            )
            print(f"   Response: {response.text[:300]}")
        
        return success
    except Exception as e:
        print_test("Purchase Request", False, f"Error: {e}")
        return False

def test_api_status():
    """Test API status endpoint"""
    print_header("TEST 5: API STATUS")
    
    try:
        response = requests.get(f"{API_URL}/api/status", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            print_test("API Status", True, "System operational")
            print(f"   Production: {data.get('production')}")
            print(f"   Safe Mode: {data.get('safe_mode')}")
            print(f"   CORS Origins: {data.get('cors_origins')}")
            
            p2p = data.get('p2p', {})
            print(f"   P2P Enabled: {p2p.get('enabled')}")
            print(f"   P2P Started: {p2p.get('started')}")
        else:
            print_test(
                "API Status",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
        
        return success
    except Exception as e:
        print_test("API Status", False, f"Error: {e}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print_header("TEST 6: ROOT ENDPOINT")
    
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            name = data.get('name', 'N/A')
            version = data.get('version', 'N/A')
            release = data.get('release', 'N/A')
            status = data.get('status', 'N/A')
            
            print_test("Root Endpoint", True, f"Name: {name}")
            print(f"   Version: {version}")
            print(f"   Release: {release}")
            print(f"   Status: {status}")
            
            features = data.get('features', [])
            if features:
                print(f"   Features: {', '.join(features[:3])}")
        else:
            print_test(
                "Root Endpoint",
                False,
                f"Status: {response.status_code}, Response: {response.text[:200]}"
            )
        
        return success
    except Exception as e:
        print_test("Root Endpoint", False, f"Error: {e}")
        return False

def main():
    print("=" * 70)
    print("  DIOTEC 360 IA - LIVE TREASURY TEST SUITE")
    print("  v3.6.0 - Global Launch Activation")
    print("=" * 70)
    print(f"\nAPI URL: {API_URL}")
    print(f"Test User: {TEST_USER_ID}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    
    # Run all tests
    results = []
    
    results.append(("Health Check", test_health()))
    time.sleep(1)
    
    results.append(("Treasury Health", test_treasury_health()))
    time.sleep(1)
    
    results.append(("Balance Check", test_balance_check()))
    time.sleep(1)
    
    results.append(("Credit Purchase", test_purchase_starter()))
    time.sleep(1)
    
    results.append(("API Status", test_api_status()))
    time.sleep(1)
    
    results.append(("Root Endpoint", test_root_endpoint()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "-" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed*100//total}%)")
    print("-" * 70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🏛️ O TESOURO ESTÁ 100% OPERACIONAL! 💰🚀🇦🇴")
    elif passed >= total * 0.8:
        print("\n✅ MOST TESTS PASSED!")
        print("🏛️ O Tesouro está quase pronto! Alguns ajustes necessários.")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("🔧 Verificar logs e configuração do sistema.")
    
    print("\n" + "=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
