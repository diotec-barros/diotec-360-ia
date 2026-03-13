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
Start a validator node for Proof-of-Proof consensus network.

This script starts a validator node that participates in consensus:
- Loads node configuration
- Initializes consensus engine
- Connects to P2P network
- Starts consensus rounds
- Monitors node health

Usage:
    python scripts/start_validator.py --node-id node_1 --config config/node_1.json
"""

import argparse
import json
import time
import signal
import sys
from pathlib import Path
from typing import Optional

from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.monitoring import MetricsCollector
from diotec360.consensus.ghost_consensus import GhostConsensusConfig


class ValidatorNode:
    """
    Validator node for Proof-of-Proof consensus.
    
    This class manages a validator node that participates in consensus:
    - Maintains connection to P2P network
    - Verifies proofs and participates in voting
    - Proposes blocks when elected as leader
    - Monitors node health and performance
    """
    
    def __init__(
        self,
        node_id: str,
        stake: int,
        network_config: dict,
        genesis_config: dict,
    ):
        """
        Initialize validator node.
        
        Args:
            node_id: Unique identifier for this node
            stake: Amount of stake locked by this node
            network_config: Network configuration (peers, ports, etc.)
            genesis_config: Genesis state configuration
        """
        self.node_id = node_id
        self.stake = stake
        self.network_config = network_config
        self.genesis_config = genesis_config
        self.running = False
        
        # Initialize components
        print(f"\nInitializing validator node: {node_id}")
        print(f"  Stake: {stake}")
        
        # Create P2P network
        self.network = MockP2PNetwork(node_id)
        
        # Create proof verifier
        self.proof_verifier = ProofVerifier()
        
        # Create state store
        self.state_store = StateStore()
        
        # Load genesis state
        self._load_genesis_state()
        
        # Create proof mempool
        self.proof_mempool = ProofMempool()
        
        # Create metrics collector
        self.metrics = MetricsCollector()
        
        # Create consensus engine
        self.consensus_engine = ConsensusEngine(
            node_id=node_id,
            validator_stake=stake,
            network=self.network,
            proof_verifier=self.proof_verifier,
            state_store=self.state_store,
            proof_mempool=self.proof_mempool,
            metrics_collector=self.metrics,
        )
        
        print("  Validator node initialized successfully")
    
    def _load_genesis_state(self) -> None:
        """Load genesis state into state store."""
        validators = self.genesis_config.get("validators", [])
        
        for validator in validators:
            node_id = validator["node_id"]
            stake = validator["stake"]
            self.state_store.set_validator_stake(node_id, stake)
            
            if "initial_balance" in validator:
                balance = validator["initial_balance"]
                self.state_store.merkle_tree.update(f"balance:{node_id}", balance)
    
    def connect_to_network(self) -> None:
        """Connect to P2P network and discover peers."""
        print("\nConnecting to P2P network...")
        
        # Get bootstrap peers from config
        bootstrap_peers = self.network_config.get("bootstrap_peers", [])
        
        # Connect to bootstrap peers
        for peer in bootstrap_peers:
            peer_id = peer["node_id"]
            if peer_id != self.node_id:
                self.network.add_peer(peer_id)
                print(f"  Connected to peer: {peer_id}")
        
        print(f"  Connected to {self.network.node_count()} peers")
    
    def start(self) -> None:
        """Start the validator node."""
        self.running = True
        
        print("\n" + "=" * 60)
        print(f"Validator node {self.node_id} is now running")
        print("=" * 60)
        print("\nNode status:")
        print(f"  Node ID: {self.node_id}")
        print(f"  Stake: {self.stake}")
        print(f"  Connected peers: {self.network.node_count()}")
        print(f"  Is leader: {self.consensus_engine.is_leader()}")
        print(f"  Current view: {self.consensus_engine.view}")
        print(f"  Current sequence: {self.consensus_engine.sequence}")
        print("\nPress Ctrl+C to stop the node")
        
        # Main consensus loop
        try:
            while self.running:
                self._consensus_loop()
                time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            print("\n\nShutting down validator node...")
            self.stop()
    
    def _consensus_loop(self) -> None:
        """Main consensus loop - propose blocks if leader, participate in voting."""
        # Check if we're the leader
        if self.consensus_engine.is_leader():
            # Try to propose a block from mempool
            proof_block = self.consensus_engine.propose_block_from_mempool(block_size=10)
            
            if proof_block is not None:
                print(f"\n[{time.strftime('%H:%M:%S')}] Proposing block with {len(proof_block.proofs)} proofs")
                result = self.consensus_engine.start_consensus_round(proof_block)
                
                if result.consensus_reached:
                    print(f"  ✓ Consensus reached! Block finalized: {result.finalized_state[:16]}...")
                    self._print_consensus_metrics(result)
        
        # Check for consensus timeout
        time_since_last_consensus = time.time() - self.consensus_engine.last_consensus_time
        if time_since_last_consensus > self.consensus_engine.consensus_timeout:
            if not self.consensus_engine.in_view_change:
                print(f"\n[{time.strftime('%H:%M:%S')}] Consensus timeout, initiating view change...")
                self.consensus_engine.initiate_view_change()
    
    def _print_consensus_metrics(self, result) -> None:
        """Print consensus round metrics."""
        print(f"  Participating nodes: {len(result.participating_nodes)}")
        print(f"  Total difficulty: {result.total_difficulty}")
        print(f"  Mempool size: {self.proof_mempool.size()}")
    
    def stop(self) -> None:
        """Stop the validator node."""
        self.running = False
        
        # Print final metrics
        print("\nFinal node metrics:")
        print(f"  Total consensus rounds: {len(self.metrics.consensus_rounds)}")
        print(f"  Average round duration: {self._calculate_avg_duration():.2f}s")
        print(f"  Verification accuracy: {self._calculate_accuracy():.1f}%")
        
        print("\nValidator node stopped")
    
    def _calculate_avg_duration(self) -> float:
        """Calculate average consensus round duration."""
        if not self.metrics.consensus_rounds:
            return 0.0
        
        total_duration = sum(
            round_data["duration"]
            for round_data in self.metrics.consensus_rounds.values()
        )
        return total_duration / len(self.metrics.consensus_rounds)
    
    def _calculate_accuracy(self) -> float:
        """Calculate verification accuracy percentage."""
        if self.node_id not in self.metrics.verification_accuracy:
            return 0.0
        
        accuracy_data = self.metrics.verification_accuracy[self.node_id]
        if not accuracy_data:
            return 0.0
        
        correct = sum(1 for result in accuracy_data if result)
        return (correct / len(accuracy_data)) * 100


def load_config(config_path: Path) -> dict:
    """Load node configuration from file."""
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)


def load_genesis_config(genesis_path: Path) -> dict:
    """Load genesis configuration from file."""
    if not genesis_path.exists():
        print(f"Warning: Genesis file not found: {genesis_path}")
        print("Using default genesis configuration")
        return {
            "validators": [
                {"node_id": "node_1", "stake": 10000, "initial_balance": 0},
                {"node_id": "node_2", "stake": 10000, "initial_balance": 0},
                {"node_id": "node_3", "stake": 10000, "initial_balance": 0},
                {"node_id": "node_4", "stake": 10000, "initial_balance": 0},
            ]
        }
    
    with open(genesis_path, 'r') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Start a validator node for Proof-of-Proof consensus"
    )
    parser.add_argument(
        "--node-id",
        type=str,
        required=True,
        help="Unique identifier for this node"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to node configuration file"
    )
    parser.add_argument(
        "--genesis",
        type=str,
        default="data/genesis_state.json",
        help="Path to genesis state file"
    )
    parser.add_argument(
        "--stake",
        type=int,
        default=10000,
        help="Amount of stake to lock (default: 10000)"
    )
    
    args = parser.parse_args()
    
    # Load configurations
    if args.config:
        config = load_config(Path(args.config))
        node_id = config.get("node_id", args.node_id)
        stake = config.get("stake", args.stake)
        network_config = config.get("network", {})
    else:
        node_id = args.node_id
        stake = args.stake
        network_config = {
            "bootstrap_peers": [
                {"node_id": "node_1"},
                {"node_id": "node_2"},
                {"node_id": "node_3"},
                {"node_id": "node_4"},
            ]
        }
    
    genesis_config = load_genesis_config(Path(args.genesis))
    
    # Create and start validator node
    node = ValidatorNode(
        node_id=node_id,
        stake=stake,
        network_config=network_config,
        genesis_config=genesis_config,
    )
    
    # Connect to network
    node.connect_to_network()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print("\n\nReceived shutdown signal...")
        node.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the node
    node.start()


if __name__ == "__main__":
    main()
