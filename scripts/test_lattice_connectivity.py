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
Real Lattice Connectivity Test
Tests P2P and HTTP connectivity between all genesis nodes
"""

import requests
import time
import sys
from typing import List, Dict, Any
from datetime import datetime

class LatticeConnectivityTester:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.results = {
            'p2p_connectivity': {},
            'http_connectivity': {},
            'state_sync': {},
            'overall_health': {}
        }
    
    def test_node_health(self, node_url: str) -> Dict[str, Any]:
        """Test basic health of a node"""
        print(f"\n[TEST] Checking health: {node_url}")
        try:
            response = requests.get(f"{node_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Node is healthy - Version: {data.get('version')}")
                return {'healthy': True, 'data': data}
            else:
                print(f"[FAIL] Unexpected status code: {response.status_code}")
                return {'healthy': False, 'error': f"Status {response.status_code}"}
        except Exception as e:
            print(f"[FAIL] Health check failed: {e}")
            return {'healthy': False, 'error': str(e)}
    
    def test_p2p_status(self, node_url: str) -> Dict[str, Any]:
        """Test P2P status of a node"""
        print(f"\n[TEST] Checking P2P status: {node_url}")
        try:
            response = requests.get(f"{node_url}/api/lattice/p2p/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"[INFO] P2P Status:")
                print(f"  - Started: {status.get('started')}")
                print(f"  - Peer Count: {status.get('peer_count')}")
                print(f"  - Has Peers: {status.get('has_peers')}")
                print(f"  - Sync Mode: {status.get('sync_mode')}")
                print(f"  - HTTP Sync: {status.get('http_sync_enabled')}")
                
                if status.get('peer_count', 0) > 0:
                    print(f"[OK] Node has {status['peer_count']} peer(s)")
                    return {'connected': True, 'status': status}
                else:
                    print(f"[WARN] Node has no peers")
                    return {'connected': False, 'status': status}
            else:
                print(f"[FAIL] P2P status check failed: {response.status_code}")
                return {'connected': False, 'error': f"Status {response.status_code}"}
        except Exception as e:
            print(f"[FAIL] P2P status check failed: {e}")
            return {'connected': False, 'error': str(e)}
    
    def test_state_sync(self, node_url: str) -> Dict[str, Any]:
        """Test state synchronization"""
        print(f"\n[TEST] Checking state: {node_url}")
        try:
            response = requests.get(f"{node_url}/api/lattice/state", timeout=5)
            if response.status_code == 200:
                state = response.json()
                merkle_root = state.get('merkle_root', 'N/A')
                print(f"[INFO] Merkle Root: {merkle_root}")
                return {'synced': True, 'merkle_root': merkle_root, 'state': state}
            else:
                print(f"[FAIL] State check failed: {response.status_code}")
                return {'synced': False, 'error': f"Status {response.status_code}"}
        except Exception as e:
            print(f"[FAIL] State check failed: {e}")
            return {'synced': False, 'error': str(e)}
    
    def test_http_sync(self, node_url: str) -> Dict[str, Any]:
        """Test HTTP sync capability"""
        print(f"\n[TEST] Testing HTTP sync: {node_url}")
        try:
            # Try to trigger manual HTTP sync
            response = requests.post(
                f"{node_url}/api/lattice/sync/switch?mode=http",
                timeout=5
            )
            if response.status_code == 200:
                result = response.json()
                print(f"[OK] HTTP sync test: {result.get('message')}")
                
                # Switch back to auto
                requests.post(f"{node_url}/api/lattice/sync/switch?mode=auto", timeout=5)
                
                return {'http_capable': True, 'result': result}
            else:
                print(f"[WARN] HTTP sync test returned: {response.status_code}")
                return {'http_capable': False, 'error': f"Status {response.status_code}"}
        except Exception as e:
            print(f"[FAIL] HTTP sync test failed: {e}")
            return {'http_capable': False, 'error': str(e)}
    
    def verify_state_consistency(self) -> bool:
        """Verify all nodes have the same state"""
        print(f"\n{'='*60}")
        print("VERIFYING STATE CONSISTENCY ACROSS ALL NODES")
        print(f"{'='*60}")
        
        merkle_roots = []
        for node_url in self.nodes:
            result = self.test_state_sync(node_url)
            if result.get('synced'):
                merkle_roots.append(result.get('merkle_root'))
        
        if len(set(merkle_roots)) == 1:
            print(f"\n[SUCCESS] All nodes have consistent state")
            print(f"[INFO] Merkle Root: {merkle_roots[0]}")
            return True
        else:
            print(f"\n[FAIL] State divergence detected!")
            print(f"[INFO] Different Merkle Roots found:")
            for i, root in enumerate(merkle_roots):
                print(f"  Node {i+1}: {root}")
            return False
    
    def run_full_test(self):
        """Run complete connectivity test suite"""
        print(f"\n{'='*60}")
        print("DIOTEC360 REAL LATTICE CONNECTIVITY TEST")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Testing {len(self.nodes)} nodes")
        print(f"{'='*60}")
        
        # Test 1: Health checks
        print(f"\n{'='*60}")
        print("TEST 1: NODE HEALTH CHECKS")
        print(f"{'='*60}")
        
        healthy_nodes = 0
        for node_url in self.nodes:
            result = self.test_node_health(node_url)
            self.results['overall_health'][node_url] = result
            if result.get('healthy'):
                healthy_nodes += 1
        
        print(f"\n[RESULT] {healthy_nodes}/{len(self.nodes)} nodes are healthy")
        
        # Test 2: P2P Connectivity
        print(f"\n{'='*60}")
        print("TEST 2: P2P CONNECTIVITY")
        print(f"{'='*60}")
        
        connected_nodes = 0
        for node_url in self.nodes:
            result = self.test_p2p_status(node_url)
            self.results['p2p_connectivity'][node_url] = result
            if result.get('connected'):
                connected_nodes += 1
        
        print(f"\n[RESULT] {connected_nodes}/{len(self.nodes)} nodes have P2P peers")
        
        # Test 3: HTTP Sync Capability
        print(f"\n{'='*60}")
        print("TEST 3: HTTP SYNC CAPABILITY")
        print(f"{'='*60}")
        
        http_capable_nodes = 0
        for node_url in self.nodes:
            result = self.test_http_sync(node_url)
            self.results['http_connectivity'][node_url] = result
            if result.get('http_capable'):
                http_capable_nodes += 1
        
        print(f"\n[RESULT] {http_capable_nodes}/{len(self.nodes)} nodes support HTTP sync")
        
        # Test 4: State Consistency
        print(f"\n{'='*60}")
        print("TEST 4: STATE CONSISTENCY")
        print(f"{'='*60}")
        
        state_consistent = self.verify_state_consistency()
        
        # Final Report
        print(f"\n{'='*60}")
        print("FINAL TEST REPORT")
        print(f"{'='*60}")
        
        print(f"\nHealth:        {healthy_nodes}/{len(self.nodes)} nodes healthy")
        print(f"P2P:           {connected_nodes}/{len(self.nodes)} nodes connected")
        print(f"HTTP Sync:     {http_capable_nodes}/{len(self.nodes)} nodes capable")
        print(f"State Sync:    {'CONSISTENT' if state_consistent else 'DIVERGENT'}")
        
        # Overall verdict
        all_tests_passed = (
            healthy_nodes == len(self.nodes) and
            connected_nodes >= len(self.nodes) - 1 and  # Allow 1 node without peers
            http_capable_nodes == len(self.nodes) and
            state_consistent
        )
        
        if all_tests_passed:
            print(f"\n[SUCCESS] Real Lattice is fully operational!")
            print("[INFO] The Unstoppable Ledger is breathing with both lungs")
            return True
        else:
            print(f"\n[WARN] Some tests failed - review results above")
            print("[INFO] System may still be operational with degraded performance")
            return False

def main():
    # Default genesis nodes
    nodes = [
        "https://huggingface.co/spaces/diotec/aethel",
        "https://api.diotec360.com",
        "https://backup.diotec360.com"
    ]
    
    # Allow custom nodes via command line
    if len(sys.argv) > 1:
        nodes = sys.argv[1:]
    
    print(f"[INFO] Testing nodes:")
    for i, node in enumerate(nodes, 1):
        print(f"  {i}. {node}")
    
    tester = LatticeConnectivityTester(nodes)
    success = tester.run_full_test()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
