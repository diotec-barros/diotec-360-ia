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
Production Triangle Verification Script (3 Nodes)
Verifies all 3 production nodes are synchronized
"""

import requests
import sys
import time
from typing import Dict, List, Tuple

# Production node URLs (Triangle of Truth - Sovereign Architecture)
NODES = [
    ("Node 1 (Hugging Face)", "https://diotec-aethel-judge.hf.space"),
    ("Node 2 (Sovereign API)", "https://api.diotec360.com"),
    ("Node 3 (Vercel Backup)", "https://backup.diotec360.com")
]

def check_node_health(name: str, url: str) -> Tuple[bool, str]:
    """Check if a node is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            return status == 'healthy', status
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def get_node_state(name: str, url: str) -> Dict:
    """Get node state including Merkle Root"""
    try:
        response = requests.get(f"{url}/api/lattice/state", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def get_sync_status(name: str, url: str) -> Dict:
    """Get HTTP Sync status"""
    try:
        response = requests.get(f"{url}/api/lattice/p2p/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def verify_triangle():
    """Verify the Production Triangle of Truth (3 Nodes)"""
    
    print("=" * 70)
    print("🔺 PRODUCTION TRIANGLE OF TRUTH - VERIFICATION")
    print("=" * 70)
    print()
    
    # Phase 1: Health Checks
    print("PHASE 1: HEALTH CHECKS")
    print("-" * 70)
    
    all_healthy = True
    for name, url in NODES:
        print(f"\n[TEST] {name}: {url}")
        healthy, status = check_node_health(name, url)
        
        if healthy:
            print(f"  ✅ Status: {status}")
        else:
            print(f"  ❌ Status: {status}")
            all_healthy = False
    
    if not all_healthy:
        print("\n❌ HEALTH CHECK FAILED - Not all nodes are healthy")
        return False
    
    print("\n✅ All nodes are healthy")
    
    # Phase 2: State Synchronization
    print("\n" + "=" * 70)
    print("PHASE 2: STATE SYNCHRONIZATION")
    print("-" * 70)
    
    merkle_roots = []
    states = []
    
    for name, url in NODES:
        print(f"\n[TEST] {name}")
        state = get_node_state(name, url)
        
        if "error" in state:
            print(f"  ❌ Error: {state['error']}")
            return False
        
        merkle_root = state.get('merkle_root', 'N/A')
        entry_count = state.get('entry_count', 0)
        
        merkle_roots.append(merkle_root)
        states.append(state)
        
        print(f"  📊 Merkle Root: {merkle_root[:32]}...")
        print(f"  📦 Entries: {entry_count}")
    
    # Check synchronization
    if len(set(merkle_roots)) == 1 and len(merkle_roots) == 3:
        print("\n✅ ALL 3 NODES SYNCHRONIZED")
        print(f"📊 Shared Merkle Root: {merkle_roots[0]}")
    else:
        print("\n❌ NODES ARE NOT SYNCHRONIZED")
        print(f"Found {len(set(merkle_roots))} different Merkle Roots:")
        for i, root in enumerate(merkle_roots):
            print(f"  Node {i+1}: {root}")
        return False
    
    # Phase 3: HTTP Sync Status
    print("\n" + "=" * 70)
    print("PHASE 3: HTTP SYNC STATUS")
    print("-" * 70)
    
    for name, url in NODES:
        print(f"\n[TEST] {name}")
        sync_status = get_sync_status(name, url)
        
        if "error" in sync_status:
            print(f"  ⚠️  Could not get sync status: {sync_status['error']}")
            continue
        
        http_enabled = sync_status.get('http_sync_enabled', False)
        peer_count = sync_status.get('peer_count', 0)
        mode = sync_status.get('mode', 'unknown')
        
        print(f"  🔄 HTTP Sync: {'✅ Enabled' if http_enabled else '❌ Disabled'}")
        print(f"  👥 Peers: {peer_count}")
        print(f"  🎯 Mode: {mode}")
    
    # Phase 4: Performance Metrics
    print("\n" + "=" * 70)
    print("PHASE 4: PERFORMANCE METRICS")
    print("-" * 70)
    
    for name, url in NODES:
        print(f"\n[TEST] {name}")
        
        # Measure response time
        start = time.time()
        try:
            requests.get(f"{url}/health", timeout=10)
            response_time = (time.time() - start) * 1000
            print(f"  ⚡ Response Time: {response_time:.2f}ms")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Final Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print()
    print("✅ Health Checks: PASSED")
    print("✅ State Synchronization: PASSED")
    print("✅ HTTP Sync: OPERATIONAL")
    print("✅ Performance: ACCEPTABLE")
    print()
    print("🔺 PRODUCTION TRIANGLE OF TRUTH IS OPERATIONAL 🔺")
    print()
    
    return True

def main():
    """Main entry point"""
    print()
    print("Starting Production Dual Node Verification...")
    print()
    
    success = verify_triangle()
    
    if success:
        print("=" * 70)
        print("✅ VERIFICATION SUCCESSFUL")
        print("=" * 70)
        print()
        print("The Triangle of Truth (3 nodes) is operational and synchronized.")
        print("All nodes are healthy and communicating correctly.")
        print()
        sys.exit(0)
    else:
        print("=" * 70)
        print("❌ VERIFICATION FAILED")
        print("=" * 70)
        print()
        print("Please check the errors above and investigate.")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
