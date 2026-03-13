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
Test Diotec360 v1.4.1 in Production - Overflow Sentinel Fix Verification

This test verifies that the critical overflow bug fix is working in production
on the Hugging Face Space.

The "Bit Apocalypse" test: balance = (MAX_INT - 7) + 100
- v1.4.0: Would pass (BUG!)
- v1.4.1: Should detect overflow (FIXED!)
"""

import requests
import json

API_URL = "https://diotec360-judge.hf.space/api"

def test_bit_apocalypse():
    """
    Test the critical overflow fix: near-MAX_INT addition
    
    This was the bug that v1.4.1 fixed!
    """
    print("\n" + "="*60)
    print("TEST 1: Bit Apocalypse (Near-MAX_INT Overflow)")
    print("="*60)
    
    # MAX_INT for 64-bit signed: 9223372036854775807
    # We'll use MAX_INT - 7 = 9223372036854775800
    
    code = """
intent test_overflow(account: Account) {
    guard {
        old_balance == balance;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        balance == (9223372036854775800 + 100);
    }
}
"""
    
    print(f"\nSending code to {API_URL}/verify")
    print(f"\nCode:")
    print(code)
    
    response = requests.post(
        f"{API_URL}/verify",
        json={"code": code},
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(json.dumps(result, indent=2))
        
        # Check if overflow was detected
        if result.get('success') == False:
            intent_result = result.get('intents', [{}])[0]
            status = intent_result.get('status', '')
            message = intent_result.get('message', '')
            
            if 'OVERFLOW' in message or 'overflow' in message.lower():
                print("\n✅ PASS - Overflow correctly detected in production!")
                print(f"   Status: {status}")
                print(f"   Message: {message[:200]}...")
                return True
            else:
                print(f"\n⚠️  FAILED but not due to overflow")
                print(f"   Status: {status}")
                print(f"   Message: {message[:200]}...")
                return False
        else:
            print("\n❌ FAIL - Code was PROVED (should have detected overflow!)")
            return False
    else:
        print(f"\n❌ FAIL - HTTP Error: {response.status_code}")
        print(response.text)
        return False


def test_safe_operation():
    """
    Test that safe operations still pass (no false positives)
    """
    print("\n" + "="*60)
    print("TEST 2: Safe Operation (No False Positives)")
    print("="*60)
    
    code = """
intent test_safe(account: Account) {
    guard {
        old_balance == balance;
        balance >= 0;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        balance == (100 + 200);
    }
}
"""
    
    print(f"\nSending code to {API_URL}/verify")
    print(f"\nCode:")
    print(code)
    
    response = requests.post(
        f"{API_URL}/verify",
        json={"code": code},
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nResult:")
        print(json.dumps(result, indent=2))
        
        # This should pass (safe operation)
        if result.get('success') == True:
            intent_result = result.get('intents', [{}])[0]
            status = intent_result.get('status', '')
            print("\n✅ PASS - Safe operation correctly allowed!")
            print(f"   Status: {status}")
            return True
        else:
            print("\n❌ FAIL - Safe operation was blocked (false positive!)")
            return False
    else:
        print(f"\n❌ FAIL - HTTP Error: {response.status_code}")
        return False


def test_multiplication_overflow():
    """
    Test multiplication overflow detection
    """
    print("\n" + "="*60)
    print("TEST 3: Multiplication Overflow")
    print("="*60)
    
    code = """
intent test_mult_overflow(account: Account) {
    guard {
        old_balance == balance;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        balance == (1000000000000 * 10000000);
    }
}
"""
    
    print(f"\nSending code to {API_URL}/verify")
    
    response = requests.post(
        f"{API_URL}/verify",
        json={"code": code},
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success') == False:
            intent_result = result.get('intents', [{}])[0]
            message = intent_result.get('message', '')
            if 'OVERFLOW' in message or 'overflow' in message.lower():
                print("\n✅ PASS - Multiplication overflow detected!")
                return True
        
        print("\n❌ FAIL - Multiplication overflow not detected")
        return False
    else:
        print(f"\n❌ FAIL - HTTP Error: {response.status_code}")
        return False


def test_division_by_zero():
    """
    Test division by zero detection
    """
    print("\n" + "="*60)
    print("TEST 4: Division by Zero")
    print("="*60)
    
    code = """
intent test_div_zero(account: Account) {
    guard {
        old_balance == balance;
    }
    
    solve {
        priority: security;
    }
    
    verify {
        balance == (100 / 0);
    }
}
"""
    
    print(f"\nSending code to {API_URL}/verify")
    
    response = requests.post(
        f"{API_URL}/verify",
        json={"code": code},
        timeout=30
    )
    
    print(f"\nResponse Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success') == False:
            intent_result = result.get('intents', [{}])[0]
            message = intent_result.get('message', '')
            if 'DIVISION' in message or 'division' in message.lower():
                print("\n✅ PASS - Division by zero detected!")
                return True
        
        print("\n❌ FAIL - Division by zero not detected")
        return False
    else:
        print(f"\n❌ FAIL - HTTP Error: {response.status_code}")
        return False


if __name__ == '__main__':
    print("\n" + "="*60)
    print("DIOTEC360 v1.4.1 PRODUCTION VERIFICATION")
    print("="*60)
    print(f"\nAPI: {API_URL}")
    print("Testing critical overflow bug fix...")
    
    results = []
    
    try:
        # Test 1: The critical bug fix
        results.append(("Bit Apocalypse", test_bit_apocalypse()))
        
        # Test 2: No false positives
        results.append(("Safe Operation", test_safe_operation()))
        
        # Test 3: Multiplication overflow
        results.append(("Multiplication Overflow", test_multiplication_overflow()))
        
        # Test 4: Division by zero
        results.append(("Division by Zero", test_division_by_zero()))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n" + "="*60)
            print("🎉 ALL TESTS PASSED!")
            print("="*60)
            print("\n✅ v1.4.1 is working correctly in production!")
            print("✅ The Bit Apocalypse has been prevented!")
            print("✅ Overflow Sentinel is operational!")
            print("\n🛡️ The hardware is protected! 🚀")
        else:
            print("\n" + "="*60)
            print("⚠️ SOME TESTS FAILED")
            print("="*60)
            print(f"\n{total - passed} test(s) failed")
            print("Please check the logs above for details")
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ ERROR")
        print("="*60)
        print(f"\nException: {e}")
        import traceback
        traceback.print_exc()
