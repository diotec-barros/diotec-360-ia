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
Genesis Node Deployment Script
Automates deployment of Aethel nodes to production
"""

import os
import sys
import subprocess
import time
import requests
import argparse
from pathlib import Path

class GenesisNodeDeployer:
    def __init__(self, node_name: str, env_file: str):
        self.node_name = node_name
        self.env_file = env_file
        self.base_dir = Path(__file__).parent.parent
        
    def load_env(self):
        """Load environment variables from .env file"""
        env_path = self.base_dir / self.env_file
        if not env_path.exists():
            print(f"[ERROR] Environment file not found: {self.env_file}")
            return False
            
        print(f"[INFO] Loading environment from {self.env_file}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
        return True
    
    def check_dependencies(self):
        """Verify all dependencies are installed"""
        print("[INFO] Checking dependencies...")
        try:
            import fastapi
            import uvicorn
            import httpx
            print("[OK] All dependencies installed")
            return True
        except ImportError as e:
            print(f"[ERROR] Missing dependency: {e}")
            print("[INFO] Run: pip install -r requirements.txt")
            return False
    
    def get_peer_id(self):
        """Extract peer ID from P2P initialization"""
        print("[INFO] Starting temporary server to get Peer ID...")
        
        # Start server in background
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.main:app", 
             "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.base_dir
        )
        
        # Wait for startup and capture peer ID
        time.sleep(5)
        
        # Read logs to find peer ID
        # In production, this would parse actual logs
        print("[INFO] Check server logs for Peer ID")
        print("[INFO] Look for: [P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        
        # Stop temporary server
        proc.terminate()
        proc.wait()
        
        return "QmPeerIDPlaceholder"
    
    def verify_health(self, url: str = "http://localhost:8000"):
        """Verify node is healthy"""
        print(f"[INFO] Checking health at {url}")
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{url}/", timeout=5)
                if response.status_code == 200:
                    print("[OK] Node is healthy")
                    return True
            except requests.exceptions.RequestException:
                print(f"[INFO] Waiting for node to start... ({i+1}/{max_retries})")
                time.sleep(2)
        
        print("[ERROR] Node failed health check")
        return False
    
    def verify_p2p_status(self, url: str = "http://localhost:8000"):
        """Check P2P status"""
        print(f"[INFO] Checking P2P status at {url}")
        
        try:
            response = requests.get(f"{url}/api/lattice/p2p/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                print(f"[INFO] P2P Status:")
                print(f"  - Started: {status.get('started')}")
                print(f"  - Peer Count: {status.get('peer_count')}")
                print(f"  - Has Peers: {status.get('has_peers')}")
                print(f"  - Sync Mode: {status.get('sync_mode')}")
                print(f"  - HTTP Sync: {status.get('http_sync_enabled')}")
                print(f"  - Heartbeat: {status.get('heartbeat_active')}")
                return True
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to check P2P status: {e}")
            return False
    
    def deploy(self):
        """Execute full deployment"""
        print(f"\n{'='*60}")
        print(f"DEPLOYING GENESIS NODE: {self.node_name}")
        print(f"{'='*60}\n")
        
        # Step 1: Load environment
        if not self.load_env():
            return False
        
        # Step 2: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 3: Get peer ID (for first-time setup)
        # peer_id = self.get_peer_id()
        # print(f"[INFO] Peer ID: {peer_id}")
        
        # Step 4: Start the server
        print(f"\n[INFO] Starting {self.node_name}...")
        print("[INFO] Run manually:")
        print(f"  cp {self.env_file} .env")
        print("  python -m uvicorn api.main:app --host 0.0.0.0 --port 8000")
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Deploy Aethel Genesis Node')
    parser.add_argument('node', choices=['node1', 'node2', 'node3'],
                       help='Node to deploy (node1=HuggingFace, node2=diotec360, node3=backup)')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify existing deployment')
    
    args = parser.parse_args()
    
    # Map node names to env files
    env_files = {
        'node1': '.env.node1.huggingface',
        'node2': '.env.node2.diotec360',
        'node3': '.env.node3.backup'
    }
    
    deployer = GenesisNodeDeployer(args.node, env_files[args.node])
    
    if args.verify_only:
        # Just verify health
        url = input("Enter node URL (default: http://localhost:8000): ").strip()
        if not url:
            url = "http://localhost:8000"
        
        deployer.verify_health(url)
        deployer.verify_p2p_status(url)
    else:
        # Full deployment
        success = deployer.deploy()
        if success:
            print(f"\n[SUCCESS] {args.node} deployment prepared")
            print("[INFO] Follow the manual steps above to complete deployment")
        else:
            print(f"\n[FAILED] {args.node} deployment failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
