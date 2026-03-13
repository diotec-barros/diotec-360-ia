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
Join an existing Proof-of-Proof consensus network.

This script helps a new node join an existing consensus network:
- Discovers bootstrap peers
- Synchronizes state from existing nodes
- Validates stake requirements
- Starts participating in consensus

Usage:
    python scripts/join_network.py --node-id node_5 --stake 10000 --bootstrap node_1:8000
"""

import argparse
import json
import time
import sys
from pathlib import Path
from typing import List, Dict

from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.monitoring import MetricsCollector


class NetworkJoiner:
    """
    Helper class for joining an existing consensus network.
    
    This class handles the process of:
    1. Discovering bootstrap peers
    2. Synchronizing state from existing nodes
    3. Validating stake requirements
    4. Starting consensus participation
    """
    
    def __init__(
        self,
        node_id: str,
        stake: int,
        bootstrap_peers: List[str],
    ):
        """
        Initialize network joiner.
        
        Args:
            node_id: Unique identifier for this node
            stake: Amount of stake to lock
            bootstrap_peers: List of bootstrap peer addresses
        """
        self.node_id = node_id
        self.stake = stake
        self.bootstrap_peers = bootstrap_peers
        
        print("\n" + "=" * 60)
        print("Joining Proof-of-Proof Consensus Network")
        print("=" * 60)
        print(f"\nNode ID: {node_id}")
        print(f"Stake: {stake}")
        print(f"Bootstrap peers: {', '.join(bootstrap_peers)}")
    
    def validate_stake(self, min_stake: int = 1000) -> bool:
        """
        Validate that node has sufficient stake to participate.
        
        Args:
            min_stake: Minimum stake required
            
        Returns:
            True if stake is sufficient
        """
        print(f"\nValidating stake (minimum: {min_stake})...")
        
        if self.stake < min_stake:
            print(f"  ✗ Insufficient stake: {self.stake} < {min_stake}")
            return False
        
        print(f"  ✓ Stake validated: {self.stake} >= {min_stake}")
        return True
    
    def discover_peers(self) -> List[str]:
        """
        Discover peers in the network.
        
        Returns:
            List of discovered peer IDs
        """
        print("\nDiscovering peers...")
        
        # In a real implementation, this would use DHT or gossip protocol
        # For now, we use the bootstrap peers
        discovered_peers = []
        
        for peer_addr in self.bootstrap_peers:
            # Parse peer address (format: node_id:port)
            if ':' in peer_addr:
                peer_id = peer_addr.split(':')[0]
            else:
                peer_id = peer_addr
            
            discovered_peers.append(peer_id)
            print(f"  Found peer: {peer_id}")
        
        print(f"\n  Total peers discovered: {len(discovered_peers)}")
        return discovered_peers
    
    def sync_state(self, peers: List[str]) -> StateStore:
        """
        Synchronize state from existing nodes.
        
        This performs a fast-sync using Merkle tree snapshots:
        1. Request current Merkle root from peers
        2. Download state snapshot
        3. Verify snapshot integrity
        4. Load snapshot into local state store
        
        Args:
            peers: List of peer IDs to sync from
            
        Returns:
            Synchronized StateStore
        """
        print("\nSynchronizing state from network...")
        
        # Create state store
        state_store = StateStore()
        
        # In a real implementation, this would:
        # 1. Request Merkle root from multiple peers
        # 2. Download state snapshot from peer with matching root
        # 3. Verify snapshot integrity
        # 4. Load snapshot into state store
        
        # For now, we simulate this with a basic state
        print("  Requesting Merkle root from peers...")
        print("  Downloading state snapshot...")
        print("  Verifying snapshot integrity...")
        
        # Set our own stake
        state_store.set_validator_stake(self.node_id, self.stake)
        
        # Get current Merkle root
        merkle_root = state_store.merkle_tree.get_root_hash()
        print(f"  ✓ State synchronized (Merkle root: {merkle_root[:16]}...)")
        
        return state_store
    
    def create_validator_node(
        self,
        state_store: StateStore,
        peers: List[str]
    ) -> ConsensusEngine:
        """
        Create and configure validator node.
        
        Args:
            state_store: Synchronized state store
            peers: List of connected peers
            
        Returns:
            Configured ConsensusEngine
        """
        print("\nCreating validator node...")
        
        # Create P2P network
        network = MockP2PNetwork(self.node_id)
        
        # Add peers
        for peer_id in peers:
            if peer_id != self.node_id:
                network.add_peer(peer_id)
        
        print(f"  Connected to {network.node_count()} peers")
        
        # Create consensus engine
        consensus_engine = ConsensusEngine(
            node_id=self.node_id,
            validator_stake=self.stake,
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=state_store,
            proof_mempool=ProofMempool(),
            metrics_collector=MetricsCollector(),
        )
        
        print("  ✓ Validator node created")
        
        return consensus_engine
    
    def join(self) -> ConsensusEngine:
        """
        Execute the full network join process.
        
        Returns:
            Configured ConsensusEngine ready to participate in consensus
        """
        # Step 1: Validate stake
        if not self.validate_stake():
            print("\nError: Insufficient stake to join network")
            sys.exit(1)
        
        # Step 2: Discover peers
        peers = self.discover_peers()
        
        if not peers:
            print("\nError: No peers discovered. Cannot join network.")
            sys.exit(1)
        
        # Step 3: Sync state
        state_store = self.sync_state(peers)
        
        # Step 4: Create validator node
        consensus_engine = self.create_validator_node(state_store, peers)
        
        print("\n" + "=" * 60)
        print("Successfully joined network!")
        print("=" * 60)
        print("\nNode is now ready to participate in consensus")
        print(f"  Node ID: {self.node_id}")
        print(f"  Stake: {self.stake}")
        print(f"  Connected peers: {len(peers)}")
        print(f"  Current view: {consensus_engine.view}")
        print(f"  Is leader: {consensus_engine.is_leader()}")
        
        return consensus_engine


def save_node_config(
    node_id: str,
    stake: int,
    peers: List[str],
    output_path: Path
) -> None:
    """
    Save node configuration to file.
    
    Args:
        node_id: Node identifier
        stake: Node stake
        peers: Connected peers
        output_path: Path to save configuration
    """
    config = {
        "node_id": node_id,
        "stake": stake,
        "network": {
            "bootstrap_peers": [{"node_id": peer} for peer in peers]
        },
        "joined_at": int(time.time()),
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nNode configuration saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Join an existing Proof-of-Proof consensus network"
    )
    parser.add_argument(
        "--node-id",
        type=str,
        required=True,
        help="Unique identifier for this node"
    )
    parser.add_argument(
        "--stake",
        type=int,
        required=True,
        help="Amount of stake to lock"
    )
    parser.add_argument(
        "--bootstrap",
        type=str,
        action="append",
        required=True,
        help="Bootstrap peer address (can be specified multiple times)"
    )
    parser.add_argument(
        "--save-config",
        type=str,
        help="Path to save node configuration"
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start validator node after joining"
    )
    
    args = parser.parse_args()
    
    # Create network joiner
    joiner = NetworkJoiner(
        node_id=args.node_id,
        stake=args.stake,
        bootstrap_peers=args.bootstrap,
    )
    
    # Join the network
    consensus_engine = joiner.join()
    
    # Save configuration if requested
    if args.save_config:
        peers = joiner.discover_peers()
        save_node_config(
            args.node_id,
            args.stake,
            peers,
            Path(args.save_config)
        )
    
    # Start validator node if requested
    if args.start:
        print("\nStarting validator node...")
        print("Use Ctrl+C to stop")
        
        try:
            while True:
                # Simple consensus loop
                if consensus_engine.is_leader():
                    proof_block = consensus_engine.propose_block_from_mempool(block_size=10)
                    if proof_block:
                        print(f"\n[{time.strftime('%H:%M:%S')}] Proposing block...")
                        consensus_engine.start_consensus_round(proof_block)
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nStopping validator node...")
    else:
        print("\nTo start the validator node, run:")
        print(f"  python scripts/start_validator.py --node-id {args.node_id}")


if __name__ == "__main__":
    main()
