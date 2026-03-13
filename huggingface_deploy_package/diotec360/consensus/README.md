# Aethel Consensus Protocol

## Overview

The Proof-of-Proof consensus protocol is a Byzantine fault-tolerant consensus mechanism where network security emerges from Z3 proof verification. Instead of mining useless hashes (Proof-of-Work) or locking capital (Proof-of-Stake), nodes compete to verify logical correctness.

## Architecture

```
aethel/consensus/
├── __init__.py              # Module exports
├── data_models.py           # Core data structures
├── mock_network.py          # Mock P2P network for testing
├── test_strategies.py       # Hypothesis strategies for property-based testing
└── README.md               # This file
```

## Core Components

### Data Models (`data_models.py`)

**ProofBlock**: Container for proofs to be verified
- Contains batch of Z3 proofs
- Includes proposer signature and previous block hash
- Supports serialization for network transmission

**ConsensusMessage**: Base class for PBFT protocol messages
- PrePrepareMessage: Leader proposes proof block
- PrepareMessage: Nodes verify and vote
- CommitMessage: Nodes commit to finalized state
- ViewChangeMessage: Handle leader failures

**StateTransition**: Represents changes to global state
- Includes Merkle root hashes before/after
- Validates conservation property
- Supports atomic state updates

**VerificationResult**: Result of proof verification
- Includes validity, difficulty, and timing
- Tracks verification errors
- Used for reward calculation

### Mock Network (`mock_network.py`)

**MockP2PNetwork**: Simulated P2P network for testing
- Message broadcasting and direct messaging
- Peer discovery simulation
- Network condition simulation (latency, packet loss, partitions)
- Byzantine behavior simulation

**NetworkConfig**: Configuration for network simulation
- Latency settings
- Packet loss rate
- Byzantine node identification
- Partition group definitions

### Test Strategies (`test_strategies.py`)

Hypothesis strategies for property-based testing:
- `proof_blocks()`: Generate random proof blocks
- `state_transitions()`: Generate state transitions (with/without conservation)
- `verification_results()`: Generate verification results
- `peer_infos()`: Generate peer information
- `network_configs()`: Generate network configurations

## Usage

### Creating a Proof Block

```python
from aethel.consensus import ProofBlock

block = ProofBlock(
    block_id="block_1",
    timestamp=1234567890,
    proofs=[proof1, proof2, proof3],
    previous_block_hash="0" * 64,
    proposer_id="node_1",
)

# Calculate block hash
block_hash = block.hash()

# Serialize for transmission
serialized = block.serialize()
```

### Setting Up Mock Network

```python
from aethel.consensus.mock_network import create_test_network

# Create network with 10 nodes, 3 Byzantine
networks = create_test_network(node_count=10, byzantine_count=3)

# Access individual node networks
node1_network = networks["node_0"]
node1_network.start()

# Broadcast message
from aethel.consensus import PrepareMessage, MessageType

message = PrepareMessage(
    message_type=MessageType.PREPARE,
    view=0,
    sequence=1,
    sender_id="node_0",
    block_digest="abc123",
)

node1_network.broadcast("consensus", message)
```

### Property-Based Testing

```python
from hypothesis import given, settings
from aethel.consensus.test_strategies import proof_blocks, network_configs

@given(proof_blocks(), network_configs())
@settings(max_examples=100)
def test_consensus_property(block, config):
    """Test that consensus works across various configurations."""
    # Create network
    networks = create_test_network(
        node_count=config["node_count"],
        byzantine_count=config["byzantine_count"]
    )
    
    # Run consensus (to be implemented)
    # result = run_consensus(networks, block)
    
    # Verify properties
    # assert result.consensus_reached
    pass
```

## Testing

Run infrastructure tests:

```bash
python -m pytest test_consensus_infrastructure.py -v
```

## Next Steps

The infrastructure is now in place. The following components need to be implemented:

1. **ProofVerifier** - Wraps AethelJudge for proof verification with difficulty calculation
2. **StateStore** - Merkle tree-based state management
3. **ConsensusEngine** - PBFT consensus algorithm implementation
4. **P2PNetwork** - Real P2P networking using libp2p
5. **RewardDistributor** - Economic incentive system

See `.kiro/specs/proof-of-proof-consensus/tasks.md` for the complete implementation plan.

## Design Documents

- Requirements: `.kiro/specs/proof-of-proof-consensus/requirements.md`
- Design: `.kiro/specs/proof-of-proof-consensus/design.md`
- Tasks: `.kiro/specs/proof-of-proof-consensus/tasks.md`
