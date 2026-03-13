#!/usr/bin/env python3
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
Quick Triangle Verification Script
Verifies all 3 nodes are synchronized with the same Merkle Root
"""

import requests
import sys

def verify_triangle():
    """Verify the Triangle of Truth is operational"""
    
    nodes = [
        ("Node 1 (Hugging Face)", "http://localhost:8001"),
        ("Node 2 (diotec360)", "http://localhost:8000"),
        ("Node 3 (Backup)", "http://localhost:8002")
    ]
    
    print("=" * 60)
    print("🔺 TRIANGLE OF TRUTH - VERIFICATION")
    print("=" * 60)
    print()
    
    merkle_roots = []
    all_healthy = True
    
    for name, url in nodes:
        print(f"[TEST] {name}: {url}")
        
        try:
            # Check health
            health_response = requests.get(f"{url}/health", timeout=5)
            if health_response.status_code != 200:
                print(f"  ❌ Health check failed: {health_response.status_code}")
                all_healthy = False
                continue
            
            # Get state
            state_response = requests.get(f"{url}/api/lattice/state", timeout=5)
            if state_response.status_code != 200:
                print(f"  ❌ State check failed: {state_response.status_code}")
                all_healthy = False
                continue
            
            state = state_response.json()
            merkle_root = state.get('merkle_root', 'N/A')
            merkle_roots.append(merkle_root)
            
            print(f"  ✅ Healthy")
            print(f"  📊 Merkle Root: {merkle_root[:16]}...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            all_healthy = False
        
        print()
    
    # Verify synchronization
    print("=" * 60)
    print("SYNCHRONIZATION CHECK")
    print("=" * 60)
    
    if len(set(merkle_roots)) == 1 and len(merkle_roots) == 3:
        print("✅ ALL NODES SYNCHRONIZED")
        print(f"📊 Shared Merkle Root: {merkle_roots[0]}")
        print()
        print("🔺 TRIANGLE OF TRUTH IS OPERATIONAL 🔺")
        return True
    else:
        print("❌ NODES ARE NOT SYNCHRONIZED")
        print(f"Found {len(set(merkle_roots))} different Merkle Roots:")
        for i, root in enumerate(merkle_roots):
            print(f"  Node {i+1}: {root}")
        return False

if __name__ == "__main__":
    success = verify_triangle()
    sys.exit(0 if success else 1)
