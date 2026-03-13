"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Test script for Hugging Face Space deployment
Tests all API endpoints to ensure proper functionality
"""

import requests
import json
import time

# Base URL - update after deployment
BASE_URL = "https://diotec-Diotec360-judge.hf.space"
# For local testing: BASE_URL = "http://localhost:7860"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"API Name: {data.get('name')}")
        print(f"Version: {data.get('version')}")
        print(f"Endpoints: {list(data.get('endpoints', {}).keys())}")
        assert response.status_code == 200
        print("✅ Root endpoint passed")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def test_examples():
    """Test examples endpoint"""
    print("\n🔍 Testing examples endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/examples", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Examples count: {data.get('count')}")
        if data.get('examples'):
            print(f"First example: {data['examples'][0]['name']}")
        assert response.status_code == 200
        assert data.get('success') == True
        print("✅ Examples endpoint passed")
        return True
    except Exception as e:
        print(f"❌ Examples endpoint failed: {e}")
        return False

def test_verify():
    """Test verification endpoint"""
    print("\n🔍 Testing verification endpoint...")
    
    # Simple transfer intent
    code = """intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        sender_balance >= amount;
        amount > 0;
        old_sender_balance == sender_balance;
        old_receiver_balance == receiver_balance;
        old_total_supply == total_supply;
    }
    
    solve {
        priority: security;
        target: secure_ledger;
    }
    
    verify {
        sender_balance == old_sender_balance - amount;
        receiver_balance == old_receiver_balance + amount;
        total_supply == old_total_supply;
    }
}"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/verify",
            json={"code": code},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('intents'):
            for intent in data['intents']:
                print(f"  - {intent['name']}: {intent['status']}")
        
        assert response.status_code == 200
        print("✅ Verification endpoint passed")
        return True
    except Exception as e:
        print(f"❌ Verification endpoint failed: {e}")
        return False

def test_ghost_predict():
    """Test Ghost-Runner prediction endpoint"""
    print("\n🔍 Testing Ghost-Runner prediction...")
    
    code = """intent check_balance(account: Account) {
    guard {
        account_balance >= 0;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        account_balance >= 0;
    }
}"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ghost/predict",
            json={"code": code},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Status: {data.get('status')}")
        print(f"Confidence: {data.get('confidence')}")
        print(f"Latency: {data.get('latency')}")
        
        assert response.status_code == 200
        print("✅ Ghost-Runner endpoint passed")
        return True
    except Exception as e:
        print(f"❌ Ghost-Runner endpoint failed: {e}")
        return False

def test_vault_list():
    """Test vault list endpoint"""
    print("\n🔍 Testing vault list endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/vault/list", timeout=10)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Functions count: {data.get('count')}")
        assert response.status_code == 200
        print("✅ Vault list endpoint passed")
        return True
    except Exception as e:
        print(f"❌ Vault list endpoint failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Diotec360 Judge - Hugging Face Deployment Tests")
    print("=" * 60)
    print(f"\nTesting: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Examples", test_examples),
        ("Verification", test_verify),
        ("Ghost-Runner", test_ghost_predict),
        ("Vault List", test_vault_list),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
        time.sleep(1)  # Rate limiting
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Deployment successful!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the logs above.")
        return False

if __name__ == "__main__":
    import sys
    
    # Allow custom URL via command line
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Using custom URL: {BASE_URL}")
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
