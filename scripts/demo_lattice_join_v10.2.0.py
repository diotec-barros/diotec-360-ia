"""
DIOTEC 360 IA - Lattice Join Demo v10.2.0
==========================================
Sovereign Creator: Dionísio Sebastião Barros

Demonstration script showing how a new user joins the DIOTEC 360 network
and begins mining logic proofs for rewards

"From Zero to Mining in 60 Seconds"
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nexo.lattice_discovery import LatticeDiscovery
import time


def print_banner():
    """Print demo banner"""
    print("\n" + "="*70)
    print("   DIOTEC 360 IA - LATTICE DISCOVERY DEMO v10.2.0")
    print("="*70)
    print("   Sovereign Creator: Dionísio Sebastião Barros")
    print("   Genesis Merkle Root: 782708...df94b84")
    print("="*70 + "\n")


def simulate_user_journey():
    """
    Simulate a new user joining the DIOTEC 360 network
    
    Steps:
    1. Discover master server
    2. Verify Genesis Merkle Root
    3. Register node with network
    4. Discover peer nodes
    5. Start mining session
    """
    print_banner()
    
    print("🚀 SCENARIO: New user wants to join DIOTEC 360 network\n")
    time.sleep(1)
    
    # Step 1: Initialize discovery client
    print("STEP 1: Initialize Lattice Discovery Client")
    print("-" * 70)
    discovery = LatticeDiscovery(node_identity="USER_DEMO_NODE_001")
    print(f"✅ Client initialized with identity: {discovery.node_identity}\n")
    time.sleep(1)
    
    # Step 2: Discover master server
    print("STEP 2: Discover DIOTEC 360 Master Server")
    print("-" * 70)
    try:
        master = discovery.discover_master()
        print(f"✅ Master server discovered!")
        print(f"   Host: {master.host}")
        print(f"   Status: {master.status}")
        print(f"   Genesis Merkle Root: {master.genesis_merkle_root[:16]}...")
        print(f"   Verification: {'PASSED ✅' if master.genesis_merkle_root == discovery.GENESIS_MERKLE_ROOT else 'FAILED ❌'}\n")
    except Exception as e:
        print(f"❌ Failed to discover master: {e}")
        print("   This is expected if running locally without API server")
        print("   In production, this would connect to api.diotec360.com\n")
        return
    
    time.sleep(1)
    
    # Step 3: Register node
    print("STEP 3: Register Node with Network")
    print("-" * 70)
    try:
        registration = discovery.register_node()
        print(f"✅ Node registered successfully!")
        print(f"   Node ID: {registration['node_id']}")
        print(f"   Message: {registration['message']}\n")
    except Exception as e:
        print(f"❌ Registration failed: {e}\n")
        return
    
    time.sleep(1)
    
    # Step 4: Discover peers
    print("STEP 4: Discover Peer Nodes")
    print("-" * 70)
    try:
        peers = discovery.discover_peers(max_peers=10)
        print(f"✅ Discovered {len(peers)} peer nodes")
        
        if peers:
            print("\n   Top 5 Peers:")
            for i, peer in enumerate(peers[:5], 1):
                print(f"   {i}. {peer.node_id} - {peer.sovereign_identity}")
                print(f"      Location: {peer.ip_address}")
                print(f"      Contribution: {peer.contribution_score:.2f}")
        else:
            print("   No peers found (network is empty)")
        print()
    except Exception as e:
        print(f"⚠️  Peer discovery failed: {e}\n")
    
    time.sleep(1)
    
    # Step 5: Start mining
    print("STEP 5: Start Mining Logic Proofs")
    print("-" * 70)
    try:
        mining_session = discovery.start_mining()
        print(f"✅ Mining session started!")
        print(f"   Node: {mining_session['node_identity']}")
        print(f"   Status: {mining_session['status']}")
        print(f"   Started: {mining_session['started_at']}")
        print(f"\n   💰 REWARD SPLIT:")
        print(f"      30% → Genesis Authority (Dionísio)")
        print(f"      70% → Network Miners (You!)")
        print(f"\n   ⛏️  Submit logic proofs to earn DIOTEC credits!")
        print(f"   🌍 Your contributions strengthen the global network\n")
    except Exception as e:
        print(f"❌ Mining start failed: {e}\n")
        return
    
    time.sleep(1)
    
    # Success summary
    print("="*70)
    print("   🎉 SUCCESS! YOU ARE NOW PART OF THE DIOTEC 360 NETWORK")
    print("="*70)
    print("\n   What happens next:")
    print("   1. Your node appears on the global map at diotec360.com")
    print("   2. You can submit logic proofs for verification")
    print("   3. You earn DIOTEC credits proportional to your contribution")
    print("   4. You participate in network governance votes")
    print("   5. You help secure the world's first sovereign AI network")
    print("\n   Welcome to the Sovereign Swarm! 🦾⚡🌌\n")


def simulate_local_mode():
    """
    Simulate local mode when API is not available
    
    Shows what the flow would look like with real API
    """
    print_banner()
    
    print("📍 RUNNING IN LOCAL SIMULATION MODE")
    print("   (API server not available - showing expected flow)\n")
    time.sleep(1)
    
    print("EXPECTED FLOW WITH LIVE API:")
    print("-" * 70)
    print("\n1. 🔍 Discover Master Server")
    print("   → GET https://api.diotec360.com/api/lattice/ping")
    print("   ← Status: active, Genesis Root: 782708...df94b84")
    
    print("\n2. 📝 Register Node")
    print("   → POST https://api.diotec360.com/api/lattice/register")
    print("   ← Node ID: abc123..., Status: registered")
    
    print("\n3. 🌐 Discover Peers")
    print("   → POST https://api.diotec360.com/api/lattice/peers")
    print("   ← 50 active peers returned")
    
    print("\n4. ⛏️  Start Mining")
    print("   → POST https://api.diotec360.com/api/lattice/mining/start")
    print("   ← Session ID: xyz789..., Status: mining")
    
    print("\n5. 💓 Send Heartbeats")
    print("   → POST https://api.diotec360.com/api/lattice/heartbeat/{node_id}")
    print("   ← Every 10 seconds to stay alive")
    
    print("\n6. 🗺️  Appear on Global Map")
    print("   → Your node lights up on diotec360.com/studio")
    print("   ← Real-time visualization via GunDB")
    
    print("\n" + "="*70)
    print("   TO ENABLE LIVE MODE:")
    print("="*70)
    print("   1. Deploy API to Hugging Face Spaces")
    print("   2. Configure DNS: api.diotec360.com")
    print("   3. Run this script again")
    print("   4. Watch your node join the global network! 🌍✨\n")


if __name__ == "__main__":
    print("\n🌌 DIOTEC 360 IA - Lattice Discovery Demo v10.2.0\n")
    
    # Try real connection first
    print("Attempting to connect to master server...")
    print("(This will fail if API is not deployed yet)\n")
    
    try:
        simulate_user_journey()
    except Exception as e:
        print(f"\n⚠️  Live connection failed: {e}")
        print("\nSwitching to simulation mode...\n")
        time.sleep(1)
        simulate_local_mode()


# DIOTEC 360 IA - From Zero to Mining in 60 Seconds
# The future of distributed AI is here.
