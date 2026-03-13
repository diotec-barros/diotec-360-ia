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
Initialize genesis state for Proof-of-Proof consensus network.

This script creates the initial state for a new consensus network:
- Initializes genesis block
- Sets up initial validator stakes
- Creates empty mempool
- Initializes state store with genesis values
- Saves genesis configuration

Usage:
    python scripts/init_genesis_state.py --config config/genesis.json
"""

import argparse
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List

from diotec360.consensus.data_models import ProofBlock, StateTransition, StateChange
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool


def create_genesis_block() -> ProofBlock:
    """
    Create the genesis block (first block in the chain).
    
    Returns:
        Genesis ProofBlock with no proofs
    """
    genesis_block = ProofBlock(
        block_id="genesis",
        timestamp=int(time.time()),
        proofs=[],  # Genesis block has no proofs
        previous_block_hash="0" * 64,  # No previous block
        proposer_id="genesis",
        signature=b"",
        transactions=[],
    )
    
    return genesis_block


def initialize_validator_stakes(
    state_store: StateStore,
    validators: List[Dict[str, any]]
) -> None:
    """
    Initialize validator stakes in the state store.
    
    Args:
        state_store: StateStore instance
        validators: List of validator configurations with node_id and stake
    """
    print(f"\nInitializing {len(validators)} validators...")
    
    for validator in validators:
        node_id = validator["node_id"]
        stake = validator["stake"]
        
        # Set validator stake
        state_store.set_validator_stake(node_id, stake)
        
        # Initialize balance (optional, for reward distribution)
        if "initial_balance" in validator:
            balance = validator["initial_balance"]
            state_store.merkle_tree.update(f"balance:{node_id}", balance)
        
        print(f"  - {node_id}: {stake} stake")


def save_genesis_config(
    genesis_block: ProofBlock,
    validators: List[Dict[str, any]],
    output_path: Path
) -> None:
    """
    Save genesis configuration to file.
    
    Args:
        genesis_block: Genesis block
        validators: List of validator configurations
        output_path: Path to save configuration
    """
    config = {
        "genesis_block": {
            "block_id": genesis_block.block_id,
            "timestamp": genesis_block.timestamp,
            "hash": genesis_block.hash(),
        },
        "validators": validators,
        "network": {
            "consensus_timeout": 10.0,
            "view_change_timeout": 5.0,
            "min_stake": 1000,
        },
        "created_at": int(time.time()),
    }
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nGenesis configuration saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize genesis state for Proof-of-Proof consensus"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/genesis.json",
        help="Path to genesis configuration file"
    )
    parser.add_argument(
        "--validators",
        type=str,
        default="config/validators.json",
        help="Path to validators configuration file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/genesis_state.json",
        help="Path to save genesis state"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Proof-of-Proof Consensus - Genesis State Initialization")
    print("=" * 60)
    
    # Load validator configuration
    validators_path = Path(args.validators)
    if validators_path.exists():
        with open(validators_path, 'r') as f:
            validators_config = json.load(f)
            validators = validators_config.get("validators", [])
    else:
        # Default validators for testing
        print(f"\nWarning: {validators_path} not found, using default validators")
        validators = [
            {"node_id": "node_1", "stake": 10000, "initial_balance": 0},
            {"node_id": "node_2", "stake": 10000, "initial_balance": 0},
            {"node_id": "node_3", "stake": 10000, "initial_balance": 0},
            {"node_id": "node_4", "stake": 10000, "initial_balance": 0},
        ]
    
    # Create genesis block
    print("\nCreating genesis block...")
    genesis_block = create_genesis_block()
    print(f"  Genesis block hash: {genesis_block.hash()}")
    
    # Initialize state store
    print("\nInitializing state store...")
    state_store = StateStore()
    
    # Initialize validator stakes
    initialize_validator_stakes(state_store, validators)
    
    # Get initial Merkle root
    initial_root = state_store.merkle_tree.get_root_hash()
    print(f"\nInitial Merkle root: {initial_root}")
    
    # Save genesis configuration
    output_path = Path(args.output)
    save_genesis_config(genesis_block, validators, output_path)
    
    print("\n" + "=" * 60)
    print("Genesis state initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Review genesis configuration")
    print("  2. Start validator nodes with: python scripts/start_validator.py")
    print("  3. Monitor network with: python scripts/monitor_network.py")


if __name__ == "__main__":
    main()
