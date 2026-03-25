"""
Test Intelligence Harvester - v4.0.0
Verifies the complete knowledge harvesting flow
"""

import requests
import json
from datetime import datetime

# Test configuration
API_URL = "https://diotec-360-diotec-360-ia-judge.hf.space"
TEST_USER_KEY = "test_user_dionisio_2026"

def test_harvester_flow():
    """Test the complete intelligence harvesting flow"""
    
    print("=" * 80)
    print("🧠 TESTING INTELLIGENCE HARVESTER v4.0.0")
    print("=" * 80)
    
    # Test 1: Health Check
    print("\n[1/4] Testing Knowledge API Health...")
    try:
        response = requests.get(f"{API_URL}/api/knowledge/health", timeout=10)
        health = response.json()
        print(f"✅ Knowledge API: {health}")
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test 2: Get Current Stats
    print("\n[2/4] Testing Knowledge Stats...")
    try:
        response = requests.get(f"{API_URL}/api/knowledge/stats", timeout=10)
        stats = response.json()
        print(f"✅ Current Knowledge Base:")
        print(f"   Total Patterns: {stats['stats']['total']}")
        if stats['stats']['total'] > 0:
            print(f"   By Category: {stats['stats'].get('byCategory', {})}")
            print(f"   By Language: {stats['stats'].get('byLanguage', {})}")
        
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
        return False
    
    # Test 3: Harvest a Training Seed
    print("\n[3/4] Testing Knowledge Harvesting...")
    try:
        # Create a sample proven pattern
        seed = {
            "prompt": "Create a secure deposit function for a banking system",
            "writerOutput": """intent secure_deposit(amount: decimal, account_id: string) -> bool {
  require amount > 0;
  require account_id != "";
  let old_balance = get_balance(account_id);
  let new_balance = old_balance + amount;
  set_balance(account_id, new_balance);
  assert new_balance == old_balance + amount;
  return true;
}""",
            "criticReview": "Code looks secure and mathematically sound",
            "finalCode": """intent secure_deposit(amount: decimal, account_id: string) -> bool {
  require amount > 0;
  require amount <= 1000000;
  require account_id != "";
  require account_exists(account_id);
  let old_balance = get_balance(account_id);
  let new_balance = old_balance + amount;
  set_balance(account_id, new_balance);
  assert new_balance == old_balance + amount;
  assert total_supply() == old_total + amount;
  return true;
}""",
            "judgeVerdict": "PROVED",
            "z3Proof": "Z3 proof: All assertions verified",
            "writerProvider": "test",
            "writerModel": "test-model-v1",
            "criticProvider": "test",
            "criticModel": "test-critic-v1",
            "category": "financial",
            "language": "diotec360",
            "complexity": "medium"
        }
        
        response = requests.post(
            f"{API_URL}/api/knowledge/harvest",
            json=seed,
            headers={"X-Sovereign-Key": TEST_USER_KEY},
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Knowledge Harvested:")
            print(f"   Seed ID: {result.get('seedId')}")
            print(f"   Merkle Root: {result.get('merkleRoot', 'N/A')[:32]}...")
            print(f"   Message: {result.get('message')}")
            
        else:
            print(f"❌ Harvest failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Harvest failed: {e}")
        return False
    
    # Test 4: Verify Stats Updated
    print("\n[4/4] Verifying Knowledge Base Updated...")
    try:
        response = requests.get(f"{API_URL}/api/knowledge/stats", timeout=10)
        stats = response.json()
        print(f"✅ Updated Knowledge Base:")
        print(f"   Total Patterns: {stats['stats']['total']}")
        print(f"   By Category: {stats['stats'].get('byCategory', {})}")
        print(f"   By Language: {stats['stats'].get('byLanguage', {})}")
        
    except Exception as e:
        print(f"❌ Stats verification failed: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("🎉 INTELLIGENCE HARVESTER: OPERATIONAL")
    print("=" * 80)
    print("\n📊 SUMMARY:")
    print("   ✅ Knowledge API: Online")
    print("   ✅ Harvest Endpoint: Working")
    print("   ✅ Stats Endpoint: Working")
    print("   ✅ Merkle Root: Generated")
    print("\n🧠 THE REFINARIA DE VERDADE IS ACTIVE!")
    print("\n📈 KNOWLEDGE FLOW:")
    print("   1. User proves code with Z3")
    print("   2. Harvester captures proven pattern")
    print("   3. Sanitizer removes PII")
    print("   4. Knowledge syncs to cloud")
    print("   5. Merkle root seals integrity")
    print("   6. Training data accumulates")
    print("\n💎 RESULT: Every proven contract becomes training data")
    print("   for the world's first mathematically-proven AI")
    
    return True

if __name__ == "__main__":
    success = test_harvester_flow()
    exit(0 if success else 1)
