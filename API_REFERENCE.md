# Aethel Consensus Protocol API Reference

## Overview

This document provides a complete API reference for the Aethel Proof-of-Proof consensus protocol. It covers:
- Core consensus APIs
- Proof verification APIs
- State management APIs
- Network communication APIs
- Monitoring and metrics APIs

All APIs are implemented in Python 3.9+ and follow type-safe patterns with dataclasses and type hints.

## Table of Contents

1. [Consensus Engine API](#consensus-engine-api)
2. [Proof Verifier API](#proof-verifier-api)
3. [State Store API](#state-store-api)
4. [P2P Network API](#p2p-network-api)
5. [Reward Distributor API](#reward-distributor-api)
6. [Proof Mempool API](#proof-mempool-api)
7. [Monitoring API](#monitoring-api)
8. [Data Models](#data-models)
9. [Metrics Endpoints](#metrics-endpoints)

---

## Consensus Engine API

### `ConsensusEngine`

The main consensus engine implementing PBFT-variant protocol.

#### Constructor

```python
def __init__(
    self,
    node_id: str,
    validator_stake: int,
    network: MockP2PNetwork,
    proof_verifier: Optional[ProofVerifier] = None,
    state_store: Optional[StateStore] = None,
    proof_mempool: Optional[ProofMempool] = None,
    ghost_config: Optional[GhostConsensusConfig] = None,
    metrics_collector: Optional[MetricsCollector] = None,
)
```

**Parameters**:
- `node_id` (str): Unique identifier for this node
- `validator_stake` (int): Amount of stake this node has locked
- `network` (MockP2PNetwork): P2P network for communication
- `proof_verifier` (Optional[ProofVerifier]): ProofVerifier instance
- `state_store` (Optional[StateStore]): StateStore instance
- `proof_mempool` (Optional[ProofMempool]): ProofMempool instance
- `ghost_config` (Optional[GhostConsensusConfig]): Ghost Identity configuration
- `metrics_collector` (Optional[MetricsCollector]): MetricsCollector instance

**Example**:
```python
from aethel.consensus import ConsensusEngine, MockP2PNetwork

network = MockP2PNetwork()
engine = ConsensusEngine(
    node_id="node_1",
    validator_stake=1000,
    network=network
)
```

#### Methods

##### `start_consensus_round(proof_block: ProofBlock) -> ConsensusResult`

Initiate a new consensus round for the given proof block.

**Parameters**:
- `proof_block` (ProofBlock): The proof block to reach consensus on

**Returns**:
- `ConsensusResult`: Result indicating whether consensus was reached

**Example**:
```python
proof_block = ProofBlock(
    block_id="block_1",
    timestamp=int(time.time()),
    proofs=[proof1, proof2, proof3]
)

result = engine.start_consensus_round(proof_block)
if result.consensus_reached:
    print(f"Consensus reached! Difficulty: {result.total_difficulty}")
```

##### `is_leader() -> bool`

Check if this node is the current leader.

**Returns**:
- `bool`: True if this node is the leader for current view

**Example**:
```python
if engine.is_leader():
    print("This node is the leader")
    proof_block = engine.propose_block_from_mempool()
```

##### `verify_quorum(messages: List[ConsensusMessage]) -> bool`

Verify that we have Byzantine quorum (2f+1 messages).

**Parameters**:
- `messages` (List[ConsensusMessage]): List of consensus messages

**Returns**:
- `bool`: True if we have Byzantine quorum

**Example**:
```python
prepare_messages = list(engine.current_state.prepare_messages.values())
if engine.verify_quorum(prepare_messages):
    print("Byzantine quorum reached!")
```

##### `max_faulty_nodes() -> int`

Calculate maximum number of Byzantine nodes we can tolerate.

**Returns**:
- `int`: Maximum number of faulty nodes (f = ⌊(N-1)/3⌋)

**Example**:
```python
f = engine.max_faulty_nodes()
print(f"Can tolerate up to {f} Byzantine nodes")
```

##### `propose_block_from_mempool(block_size: int = 10) -> Optional[ProofBlock]`

Leader selects proof block from mempool for consensus.

**Parameters**:
- `block_size` (int): Number of proofs to include in block (default: 10)

**Returns**:
- `Optional[ProofBlock]`: ProofBlock ready for consensus, or None if mempool is empty

**Example**:
```python
if engine.is_leader():
    proof_block = engine.propose_block_from_mempool(block_size=20)
    if proof_block:
        engine.start_consensus_round(proof_block)
```

##### `handle_pre_prepare(message: PrePrepareMessage) -> None`

Process PRE-PREPARE message from leader.

**Parameters**:
- `message` (PrePrepareMessage): PRE-PREPARE message from leader

**Example**:
```python
# Typically called automatically by network handler
engine.handle_pre_prepare(pre_prepare_msg)
```

##### `handle_prepare(message: PrepareMessage) -> None`

Process PREPARE message from peer.

**Parameters**:
- `message` (PrepareMessage): PREPARE message from peer

**Example**:
```python
# Typically called automatically by network handler
engine.handle_prepare(prepare_msg)
```

##### `handle_commit(message: CommitMessage) -> Optional[ConsensusResult]`

Process COMMIT message from peer.

**Parameters**:
- `message` (CommitMessage): COMMIT message from peer

**Returns**:
- `Optional[ConsensusResult]`: ConsensusResult if consensus is finalized, None otherwise

**Example**:
```python
result = engine.handle_commit(commit_msg)
if result and result.consensus_reached:
    print("Consensus finalized!")
```

##### `initiate_view_change() -> None`

Initiate a view change due to timeout or leader failure.

**Example**:
```python
# Detect timeout
if time.time() - engine.last_consensus_time > engine.consensus_timeout:
    engine.initiate_view_change()
```

##### `handle_view_change(message: ViewChangeMessage) -> None`

Handle view change when leader fails or timeout occurs.

**Parameters**:
- `message` (ViewChangeMessage): VIEW-CHANGE message from peer

**Example**:
```python
# Typically called automatically by network handler
engine.handle_view_change(view_change_msg)
```

---

## Proof Verifier API

### `ProofVerifier`

Wraps AethelJudge to provide proof verification with difficulty measurement.

#### Constructor

```python
def __init__(
    self,
    judge: Optional[AethelJudge] = None,
    require_signatures: bool = True,
    max_workers: int = 4
)
```

**Parameters**:
- `judge` (Optional[AethelJudge]): AethelJudge instance
- `require_signatures` (bool): Whether to require valid signatures on proofs
- `max_workers` (int): Maximum number of parallel verification workers

**Example**:
```python
from aethel.consensus import ProofVerifier
from aethel.core.judge import AethelJudge

judge = AethelJudge()
verifier = ProofVerifier(judge=judge, max_workers=8)
```

#### Methods

##### `verify_proof(proof: Any) -> VerificationResult`

Verify a single Z3 proof and measure difficulty.

**Parameters**:
- `proof` (Any): Proof object to verify (SignedProof, intent_name string, or dict)

**Returns**:
- `VerificationResult`: Result with validity, difficulty, and timing info

**Example**:
```python
proof = {
    'intent_name': 'transfer_funds',
    'constraints': ['balance >= amount'],
    'post_conditions': ['new_balance = balance - amount']
}

result = verifier.verify_proof(proof)
print(f"Valid: {result.valid}, Difficulty: {result.difficulty}")
```

##### `verify_proof_block(block: ProofBlock, parallel: bool = True) -> BlockVerificationResult`

Verify all proofs in a block.

**Parameters**:
- `block` (ProofBlock): ProofBlock containing proofs to verify
- `parallel` (bool): Whether to use parallel verification (default: True)

**Returns**:
- `BlockVerificationResult`: Result with validity and aggregated difficulty

**Example**:
```python
proof_block = ProofBlock(
    block_id="block_1",
    timestamp=int(time.time()),
    proofs=[proof1, proof2, proof3]
)

result = verifier.verify_proof_block(proof_block, parallel=True)
if result.valid:
    print(f"All proofs valid! Total difficulty: {result.total_difficulty}")
```

##### `verify_signature(signed_proof: SignedProof) -> bool`

Verify the cryptographic signature on a proof.

**Parameters**:
- `signed_proof` (SignedProof): SignedProof with signature to verify

**Returns**:
- `bool`: True if signature is valid, False otherwise

**Example**:
```python
from aethel.consensus.data_models import SignedProof

signed_proof = SignedProof(
    proof_data={'intent_name': 'transfer'},
    public_key="0x1234...",
    signature="0xabcd..."
)

if verifier.verify_signature(signed_proof):
    print("Signature valid!")
```

##### `batch_verify_signatures(signed_proofs: List[SignedProof]) -> Dict[str, bool]`

Verify signatures for multiple proofs in batch.

**Parameters**:
- `signed_proofs` (List[SignedProof]): List of SignedProof objects to verify

**Returns**:
- `Dict[str, bool]`: Dictionary mapping proof hash to verification result

**Example**:
```python
results = verifier.batch_verify_signatures([proof1, proof2, proof3])
for proof_hash, is_valid in results.items():
    print(f"Proof {proof_hash[:8]}: {'✓' if is_valid else '✗'}")
```

##### `get_stats() -> Dict[str, Any]`

Get verification statistics.

**Returns**:
- `Dict[str, Any]`: Dictionary with verification count, total difficulty, and cache stats

**Example**:
```python
stats = verifier.get_stats()
print(f"Verifications: {stats['verification_count']}")
print(f"Average difficulty: {stats['average_difficulty']}")
print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
```

---

## State Store API

### `StateStore`

Distributed state store with Merkle tree authentication.

#### Constructor

```python
def __init__(self, persistence_layer: Optional[AethelPersistenceLayer] = None)
```

**Parameters**:
- `persistence_layer` (Optional[AethelPersistenceLayer]): Optional persistence layer for storage

**Example**:
```python
from aethel.consensus import StateStore
from aethel.core.persistence import AethelPersistenceLayer

persistence = AethelPersistenceLayer()
state_store = StateStore(persistence_layer=persistence)
```

#### Methods

##### `apply_state_transition(transition: StateTransition) -> bool`

Apply a state transition to the store.

**Parameters**:
- `transition` (StateTransition): StateTransition to apply

**Returns**:
- `bool`: True if transition was applied successfully

**Example**:
```python
transition = StateTransition(
    changes=[
        StateChange(key="balance:node1", value=1500),
        StateChange(key="balance:node2", value=500)
    ]
)

if state_store.apply_state_transition(transition):
    print("State transition applied!")
```

##### `get_merkle_proof(key: str) -> Optional[MerkleProof]`

Generate Merkle proof for a state key.

**Parameters**:
- `key` (str): State key to generate proof for

**Returns**:
- `Optional[MerkleProof]`: MerkleProof if key exists, None otherwise

**Example**:
```python
proof = state_store.get_merkle_proof("balance:node1")
if proof:
    print(f"Merkle proof generated for balance:node1")
```

##### `verify_merkle_proof(proof: MerkleProof) -> bool`

Verify a Merkle proof against the current root hash.

**Parameters**:
- `proof` (MerkleProof): MerkleProof to verify

**Returns**:
- `bool`: True if proof is valid

**Example**:
```python
if state_store.verify_merkle_proof(proof):
    print("Merkle proof is valid!")
```

##### `sync_from_peer(peer_root_hash: str, peer_state: Dict[str, Any]) -> bool`

Synchronize state from a peer node.

**Parameters**:
- `peer_root_hash` (str): Root hash from peer
- `peer_state` (Dict[str, Any]): State dictionary from peer

**Returns**:
- `bool`: True if sync was successful

**Example**:
```python
peer_state = {
    "balance:node1": 1000,
    "balance:node2": 500,
    "stake:node1": 1000
}

if state_store.sync_from_peer("0xabcd...", peer_state):
    print("State synced from peer!")
```

##### `get_balance(node_id: str) -> int`

Get balance for a node.

**Parameters**:
- `node_id` (str): Node identifier

**Returns**:
- `int`: Balance as integer (0 if not found)

**Example**:
```python
balance = state_store.get_balance("node1")
print(f"Node1 balance: {balance} AETHEL")
```

##### `set_balance(node_id: str, balance: int) -> None`

Set balance for a node.

**Parameters**:
- `node_id` (str): Node identifier
- `balance` (int): New balance

**Example**:
```python
state_store.set_balance("node1", 1500)
```

##### `get_validator_stake(node_id: str) -> int`

Get validator stake for a node.

**Parameters**:
- `node_id` (str): Node identifier

**Returns**:
- `int`: Stake as integer (0 if not found)

**Example**:
```python
stake = state_store.get_validator_stake("node1")
print(f"Node1 stake: {stake} AETHEL")
```

##### `set_validator_stake(node_id: str, stake: int) -> None`

Set validator stake for a node.

**Parameters**:
- `node_id` (str): Node identifier
- `stake` (int): New stake amount

**Example**:
```python
state_store.set_validator_stake("node1", 1000)
```

##### `reduce_stake(node_id: str, amount: int) -> None`

Reduce validator stake (for slashing).

**Parameters**:
- `node_id` (str): Node identifier
- `amount` (int): Amount to reduce

**Example**:
```python
# Slash 5% for invalid verification
stake = state_store.get_validator_stake("node1")
slash_amount = int(stake * 0.05)
state_store.reduce_stake("node1", slash_amount)
```

##### `validate_minimum_stake(node_id: str) -> bool`

Validate that node meets minimum stake requirement.

**Parameters**:
- `node_id` (str): Node identifier

**Returns**:
- `bool`: True if node has sufficient stake (>= 1000 tokens)

**Example**:
```python
if state_store.validate_minimum_stake("node1"):
    print("Node1 can participate in consensus")
```

##### `get_root_hash() -> str`

Get current Merkle root hash.

**Returns**:
- `str`: Root hash as hex string

**Example**:
```python
root_hash = state_store.get_root_hash()
print(f"Current state root: {root_hash}")
```

##### `get_conservation_checksum() -> int`

Calculate total value in system (conservation checksum).

**Returns**:
- `int`: Total value as integer

**Example**:
```python
checksum = state_store.get_conservation_checksum()
print(f"Total value in system: {checksum} AETHEL")
```

##### `detect_double_spend(transactions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]`

Detect double-spend attempts in a list of transactions.

**Parameters**:
- `transactions` (List[Dict[str, Any]]): List of transaction dictionaries

**Returns**:
- `Optional[Dict[str, Any]]`: Dictionary with conflict details if double-spend detected, None otherwise

**Example**:
```python
transactions = [
    {'id': 'tx1', 'inputs': [{'txid': 'prev_tx', 'output_index': 0}]},
    {'id': 'tx2', 'inputs': [{'txid': 'prev_tx', 'output_index': 0}]}  # Double-spend!
]

conflict = state_store.detect_double_spend(transactions)
if conflict:
    print(f"Double-spend detected: {conflict}")
```

---

## P2P Network API

### `MockP2PNetwork`

P2P network layer for consensus communication (mock implementation for testing).

#### Constructor

```python
def __init__(self, node_id: str = "", latency_ms: int = 0)
```

**Parameters**:
- `node_id` (str): Node identifier
- `latency_ms` (int): Simulated network latency in milliseconds

**Example**:
```python
from aethel.consensus import MockP2PNetwork

network = MockP2PNetwork(node_id="node1", latency_ms=100)
```

#### Methods

##### `broadcast(topic: str, message: Any) -> None`

Broadcast message to all peers on topic.

**Parameters**:
- `topic` (str): Topic name
- `message` (Any): Message to broadcast

**Example**:
```python
prepare_msg = PrepareMessage(
    message_type=MessageType.PREPARE,
    view=0,
    sequence=1,
    sender_id="node1",
    block_digest="0xabcd..."
)

network.broadcast("consensus", prepare_msg)
```

##### `subscribe(topic: str, handler: Callable) -> None`

Subscribe to messages on a topic.

**Parameters**:
- `topic` (str): Topic name
- `handler` (Callable): Message handler function

**Example**:
```python
def handle_consensus_message(message):
    print(f"Received: {message}")

network.subscribe("consensus", handle_consensus_message)
```

##### `add_peer(peer_id: str, peer_network: 'MockP2PNetwork') -> None`

Add a peer to the network.

**Parameters**:
- `peer_id` (str): Peer identifier
- `peer_network` (MockP2PNetwork): Peer's network instance

**Example**:
```python
peer_network = MockP2PNetwork(node_id="node2")
network.add_peer("node2", peer_network)
```

##### `node_count() -> int`

Return number of connected peers.

**Returns**:
- `int`: Number of peers

**Example**:
```python
peer_count = network.node_count()
print(f"Connected to {peer_count} peers")
```

---

## Reward Distributor API

### `RewardDistributor`

Calculates and distributes rewards for proof verification.

#### Constructor

```python
def __init__(
    self,
    state_store: StateStore,
    base_reward: int = 10,
    metrics_collector: Optional[MetricsCollector] = None,
)
```

**Parameters**:
- `state_store` (StateStore): StateStore for managing balances and stakes
- `base_reward` (int): Base reward per proof block (default: 10 tokens)
- `metrics_collector` (Optional[MetricsCollector]): MetricsCollector instance

**Example**:
```python
from aethel.consensus import RewardDistributor, StateStore

state_store = StateStore()
distributor = RewardDistributor(state_store, base_reward=10)
```

#### Methods

##### `calculate_rewards(consensus_result: ConsensusResult) -> Dict[str, int]`

Calculate rewards for all participating nodes.

**Parameters**:
- `consensus_result` (ConsensusResult): Result of consensus round

**Returns**:
- `Dict[str, int]`: Dictionary mapping node_id to reward amount

**Example**:
```python
consensus_result = ConsensusResult(
    consensus_reached=True,
    total_difficulty=5000000,
    participating_nodes=["node1", "node2", "node3"]
)

rewards = distributor.calculate_rewards(consensus_result)
for node_id, reward in rewards.items():
    print(f"{node_id}: {reward} AETHEL")
```

##### `distribute_rewards(rewards: Dict[str, int], round_id: str = "", difficulty: int = 0) -> StateTransition`

Create state transition to distribute rewards.

**Parameters**:
- `rewards` (Dict[str, int]): Dictionary mapping node_id to reward amount
- `round_id` (str): ID of the consensus round (for tracking)
- `difficulty` (int): Total difficulty of the round (for tracking)

**Returns**:
- `StateTransition`: State transition with balance updates

**Example**:
```python
rewards = {"node1": 5, "node2": 5, "node3": 5}
transition = distributor.distribute_rewards(
    rewards,
    round_id="round_42",
    difficulty=5000000
)

state_store.apply_state_transition(transition)
```

##### `apply_slashing(node_id: str, violation: SlashingViolation, evidence: Optional[Dict[str, Any]] = None) -> int`

Apply slashing penalty to a node's stake.

**Parameters**:
- `node_id` (str): ID of the node to slash
- `violation` (SlashingViolation): Type of slashing violation
- `evidence` (Optional[Dict[str, Any]]): Cryptographic evidence of the violation

**Returns**:
- `int`: Amount of stake slashed

**Example**:
```python
from aethel.consensus.data_models import SlashingViolation

# Slash for invalid verification
slashed = distributor.apply_slashing(
    node_id="node_malicious",
    violation=SlashingViolation.INVALID_VERIFICATION,
    evidence={'proof_hash': '0xabcd...', 'expected': True, 'actual': False}
)

print(f"Slashed {slashed} AETHEL from node_malicious")
```

---

## Proof Mempool API

### `ProofMempool`

Queue of pending proofs awaiting verification.

#### Constructor

```python
def __init__(self, max_size: int = 10000)
```

**Parameters**:
- `max_size` (int): Maximum number of proofs in mempool (default: 10000)

**Example**:
```python
from aethel.consensus import ProofMempool

mempool = ProofMempool(max_size=5000)
```

#### Methods

##### `add_proof(proof: Any, difficulty: int = 0) -> bool`

Add a proof to the mempool.

**Parameters**:
- `proof` (Any): Proof object to add
- `difficulty` (int): Proof difficulty (for prioritization)

**Returns**:
- `bool`: True if proof was added successfully

**Example**:
```python
proof = {'intent_name': 'transfer', 'constraints': [...]}
if mempool.add_proof(proof, difficulty=50000):
    print("Proof added to mempool")
```

##### `get_next_block(block_size: int = 10) -> Optional[ProofBlock]`

Get next proof block from mempool (highest difficulty first).

**Parameters**:
- `block_size` (int): Number of proofs to include in block

**Returns**:
- `Optional[ProofBlock]`: ProofBlock with highest difficulty proofs, or None if mempool is empty

**Example**:
```python
proof_block = mempool.get_next_block(block_size=20)
if proof_block:
    print(f"Got block with {len(proof_block.proofs)} proofs")
```

##### `remove_proofs(proof_hashes: List[str]) -> None`

Remove proofs from mempool after consensus.

**Parameters**:
- `proof_hashes` (List[str]): List of proof hashes to remove

**Example**:
```python
finalized_hashes = ["0xabcd...", "0xef01...", "0x2345..."]
mempool.remove_proofs(finalized_hashes)
```

##### `get_size() -> int`

Get current mempool size.

**Returns**:
- `int`: Number of proofs in mempool

**Example**:
```python
size = mempool.get_size()
print(f"Mempool contains {size} proofs")
```

##### `get_stats() -> Dict[str, Any]`

Get mempool statistics.

**Returns**:
- `Dict[str, Any]`: Dictionary with size, average difficulty, and processing rate

**Example**:
```python
stats = mempool.get_stats()
print(f"Mempool size: {stats['size']}")
print(f"Average difficulty: {stats['average_difficulty']}")
print(f"Processing rate: {stats['processing_rate']} proofs/sec")
```

---

## Monitoring API

### `MetricsCollector`

Collects and exposes consensus metrics.

#### Constructor

```python
def __init__(self)
```

**Example**:
```python
from aethel.consensus.monitoring import MetricsCollector

metrics = MetricsCollector()
```

#### Methods

##### `record_consensus_round(...) -> None`

Record metrics for a consensus round.

**Parameters**:
- `round_id` (str): Unique identifier for the round
- `duration` (float): Round duration in seconds
- `participants` (List[str]): List of participating node IDs
- `proof_count` (int): Number of proofs in the block
- `total_difficulty` (int): Total difficulty of all proofs
- `view` (int): View number
- `sequence` (int): Sequence number
- `success` (bool): Whether consensus succeeded

**Example**:
```python
metrics.record_consensus_round(
    round_id="round_42",
    duration=8.5,
    participants=["node1", "node2", "node3"],
    proof_count=10,
    total_difficulty=5000000,
    view=0,
    sequence=42,
    success=True
)
```

##### `record_verification(node_id: str, correct: bool) -> None`

Record a verification result for accuracy tracking.

**Parameters**:
- `node_id` (str): Node identifier
- `correct` (bool): Whether verification was correct

**Example**:
```python
metrics.record_verification("node1", correct=True)
```

##### `record_reward(node_id: str, round_id: str, reward_amount: int, difficulty: int) -> None`

Record a reward distribution.

**Parameters**:
- `node_id` (str): Node identifier
- `round_id` (str): Consensus round ID
- `reward_amount` (int): Amount of reward
- `difficulty` (int): Proof difficulty

**Example**:
```python
metrics.record_reward(
    node_id="node1",
    round_id="round_42",
    reward_amount=5,
    difficulty=5000000
)
```

##### `record_byzantine_incident(node_id: str, violation_type: str, evidence: Dict[str, Any], slashing_amount: int) -> None`

Record a Byzantine behavior incident.

**Parameters**:
- `node_id` (str): Node identifier
- `violation_type` (str): Type of violation
- `evidence` (Dict[str, Any]): Cryptographic evidence
- `slashing_amount` (int): Amount slashed

**Example**:
```python
metrics.record_byzantine_incident(
    node_id="node_malicious",
    violation_type="double_sign",
    evidence={'msg1': '0xabcd...', 'msg2': '0xef01...'},
    slashing_amount=200
)
```

##### `get_consensus_metrics() -> Dict[str, Any]`

Get aggregated consensus metrics.

**Returns**:
- `Dict[str, Any]`: Dictionary with consensus statistics

**Example**:
```python
stats = metrics.get_consensus_metrics()
print(f"Total rounds: {stats['total_rounds']}")
print(f"Average duration: {stats['average_duration_ms']}ms")
print(f"Success rate: {stats['success_rate']*100}%")
```

##### `get_verification_accuracy(node_id: str) -> float`

Get verification accuracy for a node.

**Parameters**:
- `node_id` (str): Node identifier

**Returns**:
- `float`: Accuracy as decimal (0.0 to 1.0)

**Example**:
```python
accuracy = metrics.get_verification_accuracy("node1")
print(f"Node1 accuracy: {accuracy*100:.1f}%")
```

##### `get_node_rewards(node_id: str) -> Dict[str, Any]`

Get reward statistics for a node.

**Parameters**:
- `node_id` (str): Node identifier

**Returns**:
- `Dict[str, Any]`: Dictionary with reward statistics

**Example**:
```python
rewards = metrics.get_node_rewards("node1")
print(f"Total rewards: {rewards['total_rewards']} AETHEL")
print(f"Average per round: {rewards['average_per_round']} AETHEL")
```

---

## Data Models

### `ProofBlock`

A block containing proofs to be verified.

```python
@dataclass
class ProofBlock:
    block_id: str
    timestamp: int
    proofs: List[Any]
    previous_block_hash: str = ""
    proposer_id: str = ""
    signature: bytes = b""
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    
    def hash(self) -> str:
        """Calculate block hash."""
        pass
```

**Example**:
```python
from aethel.consensus.data_models import ProofBlock

block = ProofBlock(
    block_id="block_1",
    timestamp=int(time.time()),
    proofs=[proof1, proof2, proof3],
    proposer_id="node1"
)

block_hash = block.hash()
```

### `ConsensusMessage`

Base class for consensus protocol messages.

```python
@dataclass
class ConsensusMessage:
    message_type: MessageType
    view: int
    sequence: int
    sender_id: str
    signature: bytes = b""
    use_ghost_identity: bool = False
    ghost_proof: Optional[Dict[str, Any]] = None
```

### `VerificationResult`

Result of verifying a single proof.

```python
@dataclass
class VerificationResult:
    valid: bool
    difficulty: int
    verification_time: float
    proof_hash: str
    error: Optional[str] = None
```

**Example**:
```python
result = VerificationResult(
    valid=True,
    difficulty=50000,
    verification_time=150.5,
    proof_hash="0xabcd..."
)
```

### `BlockVerificationResult`

Result of verifying an entire proof block.

```python
@dataclass
class BlockVerificationResult:
    valid: bool
    total_difficulty: int
    results: List[VerificationResult]
    failed_proof: Optional[Any] = None
```

**Example**:
```python
block_result = BlockVerificationResult(
    valid=True,
    total_difficulty=150000,
    results=[result1, result2, result3]
)
```

### `ConsensusResult`

Result of a consensus round.

```python
@dataclass
class ConsensusResult:
    consensus_reached: bool
    finalized_state: Optional[str] = None
    total_difficulty: int = 0
    verifications: Dict[str, VerificationResult] = field(default_factory=dict)
    participating_nodes: List[str] = field(default_factory=list)
```

**Example**:
```python
result = ConsensusResult(
    consensus_reached=True,
    finalized_state="0xabcd...",
    total_difficulty=5000000,
    participating_nodes=["node1", "node2", "node3"]
)
```

### `StateTransition`

Represents a change to global state.

```python
@dataclass
class StateTransition:
    changes: List[StateChange]
    merkle_root_before: str = ""
    merkle_root_after: str = ""
    conservation_checksum_before: int = 0
    conservation_checksum_after: int = 0
    timestamp: int = 0
```

**Example**:
```python
transition = StateTransition(
    changes=[
        StateChange(key="balance:node1", value=1500),
        StateChange(key="balance:node2", value=500)
    ],
    timestamp=int(time.time())
)
```

### `SlashingViolation`

Enum for types of slashing violations.

```python
class SlashingViolation(Enum):
    INVALID_VERIFICATION = "invalid_verification"
    DOUBLE_SIGN = "double_sign"
```

**Example**:
```python
from aethel.consensus.data_models import SlashingViolation

violation = SlashingViolation.INVALID_VERIFICATION
```

---

## Metrics Endpoints

### HTTP Metrics API

The consensus engine exposes metrics via HTTP on port 9090 (configurable).

#### `GET /metrics`

Get Prometheus-compatible metrics.

**Response**:
```
# HELP consensus_rounds_total Total number of consensus rounds
# TYPE consensus_rounds_total counter
consensus_rounds_total 1234

# HELP consensus_duration_seconds Duration of consensus rounds
# TYPE consensus_duration_seconds histogram
consensus_duration_seconds_bucket{le="5"} 100
consensus_duration_seconds_bucket{le="10"} 950
consensus_duration_seconds_bucket{le="15"} 1200
consensus_duration_seconds_sum 10450.5
consensus_duration_seconds_count 1234

# HELP verification_accuracy Verification accuracy per node
# TYPE verification_accuracy gauge
verification_accuracy{node="node1"} 0.98
verification_accuracy{node="node2"} 0.97

# HELP rewards_earned_total Total rewards earned per node
# TYPE rewards_earned_total counter
rewards_earned_total{node="node1"} 1250
rewards_earned_total{node="node2"} 1100
```

#### `GET /metrics/consensus`

Get detailed consensus metrics as JSON.

**Response**:
```json
{
  "total_rounds": 1234,
  "successful_rounds": 1220,
  "failed_rounds": 14,
  "success_rate": 0.988,
  "average_duration_ms": 8500,
  "average_participants": 10,
  "average_proof_count": 10,
  "total_difficulty": 6150000000
}
```

#### `GET /metrics/mempool`

Get mempool metrics as JSON.

**Response**:
```json
{
  "size": 150,
  "max_size": 10000,
  "utilization": 0.015,
  "average_difficulty": 500000,
  "processing_rate": 12.5,
  "oldest_proof_age_seconds": 45
}
```

#### `GET /metrics/node/{node_id}`

Get metrics for a specific node.

**Response**:
```json
{
  "node_id": "node1",
  "stake": 1000,
  "balance": 1250,
  "verification_accuracy": 0.98,
  "total_verifications": 1000,
  "correct_verifications": 980,
  "total_rewards": 1250,
  "average_reward_per_round": 2.5,
  "byzantine_incidents": 0
}
```

#### `GET /metrics/byzantine`

Get Byzantine incident logs.

**Response**:
```json
{
  "total_incidents": 5,
  "incidents": [
    {
      "node_id": "node_malicious",
      "violation_type": "double_sign",
      "timestamp": 1640000000,
      "evidence": {
        "message1": "0xabcd...",
        "message2": "0xef01...",
        "signature1": "0x2345...",
        "signature2": "0x6789..."
      },
      "slashing_amount": 200
    }
  ]
}
```

---

## Code Examples

### Complete Consensus Flow

```python
from aethel.consensus import (
    ConsensusEngine,
    ProofVerifier,
    StateStore,
    MockP2PNetwork,
    ProofMempool,
    RewardDistributor
)
from aethel.consensus.data_models import ProofBlock
import time

# Initialize components
network = MockP2PNetwork(node_id="node1")
state_store = StateStore()
proof_verifier = ProofVerifier()
proof_mempool = ProofMempool()
reward_distributor = RewardDistributor(state_store)

# Create consensus engine
engine = ConsensusEngine(
    node_id="node1",
    validator_stake=1000,
    network=network,
    proof_verifier=proof_verifier,
    state_store=state_store,
    proof_mempool=proof_mempool
)

# Add proofs to mempool
proofs = [
    {'intent_name': 'transfer1', 'constraints': [...]},
    {'intent_name': 'transfer2', 'constraints': [...]},
    {'intent_name': 'transfer3', 'constraints': [...]}
]

for proof in proofs:
    proof_mempool.add_proof(proof, difficulty=50000)

# Leader proposes block
if engine.is_leader():
    proof_block = engine.propose_block_from_mempool(block_size=10)
    if proof_block:
        result = engine.start_consensus_round(proof_block)
        
        if result.consensus_reached:
            # Calculate and distribute rewards
            rewards = reward_distributor.calculate_rewards(result)
            transition = reward_distributor.distribute_rewards(rewards)
            state_store.apply_state_transition(transition)
            
            print(f"Consensus reached! Rewards distributed.")
```

### Monitoring Node Health

```python
from aethel.consensus.monitoring import MetricsCollector

metrics = MetricsCollector()

# Check verification accuracy
accuracy = metrics.get_verification_accuracy("node1")
if accuracy < 0.95:
    print(f"⚠️ Low accuracy: {accuracy*100:.1f}%")
    # Alert operator

# Check rewards
rewards = metrics.get_node_rewards("node1")
print(f"Total rewards: {rewards['total_rewards']} AETHEL")

# Check consensus health
consensus_stats = metrics.get_consensus_metrics()
print(f"Success rate: {consensus_stats['success_rate']*100:.1f}%")
print(f"Average duration: {consensus_stats['average_duration_ms']}ms")
```

### State Synchronization

```python
from aethel.consensus import StateStore

# Node that fell behind
state_store = StateStore()

# Request state from peer
peer_root_hash = "0xabcd..."
peer_state = {
    "balance:node1": 1000,
    "balance:node2": 500,
    "stake:node1": 1000,
    "stake:node2": 1000
}

# Sync from peer
if state_store.sync_from_peer(peer_root_hash, peer_state):
    print("✓ State synced successfully")
    print(f"Current root: {state_store.get_root_hash()}")
else:
    print("✗ State sync failed (hash mismatch)")
```

---

## Error Handling

### Common Errors

#### `InsufficientStakeError`

Raised when a node attempts to participate without sufficient stake.

```python
try:
    engine.start_consensus_round(proof_block)
except InsufficientStakeError as e:
    print(f"Cannot participate: {e}")
    # Stake more tokens
```

#### `InvalidProofError`

Raised when proof verification fails.

```python
try:
    result = verifier.verify_proof(proof)
except InvalidProofError as e:
    print(f"Proof verification failed: {e}")
    # Log error and skip proof
```

#### `ConservationViolationError`

Raised when state transition violates conservation property.

```python
try:
    state_store.apply_state_transition(transition)
except ConservationViolationError as e:
    print(f"Conservation violated: {e}")
    # Reject transition
```

---

## Best Practices

### Performance

1. **Enable parallel verification** for blocks with many proofs
2. **Use message batching** to reduce network overhead
3. **Enable Merkle tree caching** for faster state access
4. **Monitor metrics** to identify bottlenecks

### Security

1. **Always verify signatures** before consensus
2. **Validate minimum stake** before accepting messages
3. **Check for double-spends** in transactions
4. **Monitor Byzantine incidents** and alert on suspicious activity

### Reliability

1. **Implement proper error handling** for all API calls
2. **Use persistence layer** to recover from crashes
3. **Monitor verification accuracy** and alert when < 95%
4. **Keep software up to date** to avoid slashing

---

## Conclusion

This API reference provides complete documentation for the Aethel Proof-of-Proof consensus protocol. For more information:

- **Protocol Design**: See `CONSENSUS_PROTOCOL.md`
- **Operator Guide**: See `NODE_OPERATOR_GUIDE.md`
- **Source Code**: See `aethel/consensus/` directory
- **Tests**: See `test_consensus_*.py` files

For support, visit https://docs.aethel.network or join our Discord community.
