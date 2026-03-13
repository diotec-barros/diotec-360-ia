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
Demo: Lattice Discovery System
Demonstrates automatic peer discovery for the Aethel Lattice.

This demo shows how nodes automatically find each other using:
1. Bootstrap nodes
2. Peer exchange
3. Local network discovery

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 3.0 "The Lattice"
Date: February 5, 2026
"""

import asyncio
import logging
from diotec360.lattice.discovery import DiscoveryService, DiscoveryConfig, PeerInfo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_discovery():
    """Demonstrate automatic peer discovery"""
    
    print("\n" + "=" * 80)
    print("AETHEL LATTICE - AUTOMATIC PEER DISCOVERY DEMO")
    print("=" * 80)
    print("\nThis demo shows how Aethel nodes automatically discover each other")
    print("using multiple discovery mechanisms (DNS, bootstrap, peer exchange).")
    print("\n" + "=" * 80 + "\n")
    
    # Create discovery configuration
    config = DiscoveryConfig(
        dns_seeds=[],  # Disable DNS for demo
        bootstrap_nodes=[
            "https://aethel-node1.hf.space",
            "https://api.diotec360.com"
        ],
        enable_local_discovery=True,
        enable_peer_exchange=True,
        discovery_interval=10,  # Faster for demo
        max_peers_to_discover=10
    )
    
    # Create discovery service
    node_id = "demo-node-001"
    node_address = "http://localhost:8000"
    
    discovery = DiscoveryService(config, node_id, node_address)
    
    print(f"[DEMO] Starting discovery service for node: {node_id}")
    print(f"[DEMO] Node address: {node_address}")
    print(f"[DEMO] Bootstrap nodes: {len(config.bootstrap_nodes)}")
    print("\n" + "-" * 80 + "\n")
    
    # Start discovery
    await discovery.start()
    
    # Let discovery run for a while
    print("[DEMO] 🔍 Discovery service running...")
    print("[DEMO] Searching for peers...\n")
    
    for i in range(6):  # Run for 60 seconds (6 x 10s intervals)
        await asyncio.sleep(10)
        
        # Get current peers
        peers = discovery.get_peers()
        stats = discovery.get_discovery_stats()
        
        print(f"\n[DEMO] Discovery Round {i+1}/6")
        print(f"  Total peers discovered: {stats['total_peers']}")
        print(f"  Discovery methods: {stats['discovery_methods']}")
        print(f"  Average reputation: {stats['avg_reputation']:.2f}")
        
        if peers:
            print(f"\n  Discovered Peers:")
            for peer in peers[:5]:  # Show first 5
                print(f"    • {peer.peer_id}")
                print(f"      Address: {peer.address}")
                print(f"      Method: {peer.discovery_method}")
                print(f"      Reputation: {peer.reputation:.2f}")
                print()
        else:
            print("  No peers discovered yet...")
    
    # Stop discovery
    print("\n" + "-" * 80 + "\n")
    print("[DEMO] Stopping discovery service...")
    await discovery.stop()
    
    # Final summary
    print("\n" + "=" * 80)
    print("DISCOVERY DEMO COMPLETE")
    print("=" * 80)
    
    final_stats = discovery.get_discovery_stats()
    print(f"\nFinal Statistics:")
    print(f"  Total peers discovered: {final_stats['total_peers']}")
    print(f"  Discovery methods used: {list(final_stats['discovery_methods'].keys())}")
    print(f"  Average peer reputation: {final_stats['avg_reputation']:.2f}")
    
    if discovery.peers:
        print(f"\n  Peer List:")
        for peer_id, peer in discovery.peers.items():
            print(f"    • {peer_id} @ {peer.address}")
    
    print("\n" + "=" * 80)
    print("\n✅ Discovery system is ready for production deployment!")
    print("   Nodes will automatically find each other when started.")
    print("\n" + "=" * 80 + "\n")


async def demo_peer_exchange():
    """Demonstrate peer exchange mechanism"""
    
    print("\n" + "=" * 80)
    print("PEER EXCHANGE DEMO")
    print("=" * 80)
    print("\nThis shows how nodes share peer information with each other.")
    print("\n" + "=" * 80 + "\n")
    
    # Create two discovery services (simulating two nodes)
    config = DiscoveryConfig(
        dns_seeds=[],
        bootstrap_nodes=[],
        enable_local_discovery=False,
        enable_peer_exchange=True,
        discovery_interval=5
    )
    
    node1 = DiscoveryService(config, "node-1", "http://localhost:8001")
    node2 = DiscoveryService(config, "node-2", "http://localhost:8002")
    
    # Manually add some peers to node1
    node1._add_peer(PeerInfo(
        peer_id="peer-A",
        address="http://peer-a.example.com",
        discovery_method="manual"
    ))
    node1._add_peer(PeerInfo(
        peer_id="peer-B",
        address="http://peer-b.example.com",
        discovery_method="manual"
    ))
    
    print("[DEMO] Node 1 has 2 peers")
    print("[DEMO] Node 2 has 0 peers")
    print("\n[DEMO] If Node 2 connects to Node 1, it will learn about peers A and B")
    print("[DEMO] This is how the network grows organically!\n")
    
    print("=" * 80 + "\n")


if __name__ == "__main__":
    print("\n🌌 AETHEL LATTICE DISCOVERY SYSTEM")
    print("   Epoch 3.0 - The Lattice\n")
    
    # Run discovery demo
    asyncio.run(demo_discovery())
    
    # Run peer exchange demo
    asyncio.run(demo_peer_exchange())
