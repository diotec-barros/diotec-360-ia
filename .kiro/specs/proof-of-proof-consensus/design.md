# Design Document: Proof-of-Proof Consensus Protocol

## Overview

Aethel v3.0 transforms network security from a wasteful competition into a meaningful validation process. The Proof-of-Proof consensus protocol replaces traditional mining with Z3 proof verification, creating a distributed system where every CPU cycle contributes to validating logical correctness.

The design builds on established Byzantine consensus algorithms (specifically, a variant of PBFT - Practical Byzantine Fault Tolerance) but replaces arbitrary transaction validation with proof verification. This creates a unique property: **network security scales with proof difficulty**, meaning the harder it is to verify correctness, the more secure the network becomes.

### Key Innovation

Traditional blockchains waste energy on meaningless hash computations. Aethel's Proof-of-Proof protocol makes computation meaningful:
- **Bitcoin**: Hash(nonce) < target → Useless work
- **Aethel**: Verify(Z3_proof) = valid → Truth validation

### Design Principles

1. **Meaningful Work**: Every computation validates logical correctness
2. **Byzantine Resilience**: Tolerate 33% malicious nodes
3. **Conservation Preservation**: Distributed consensus must maintain value conservation
4. **Zero Trust**: Cryptographic verification at every layer
5. **Graceful Degradation**: System remains functional under network stress

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Aethel Network Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Node 1     │  │   Node 2     │  │   Node N     │      │
│  │              │  │              │  │              │      │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │      │
│  │ │Consensus │ │  │ │Consensus │ │  │ │Consensus │ │      │
│  │ │ Engine   │ │  │ │ Engine   │ │  │ │ Engine   │ │      │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │      │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │      │
│  │ │  Proof   │ │  │ │  Proof   │ │  │ │  Proof   │ │      │
│  │ │Verifier  │ │  │ │Verifier  │ │  │ │Verifier  │ │      │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │      │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │      │
│  │ │  State   │ │  │ │  State   │ │  │ │  State   │ │      │
│  │ │  Store   │ │  │ │  Store   │ │  │ │  Store   │ │      │
│  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  P2P Network   │                        │
│                    │  (libp2p)      │                        │
│                    └────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

**Consensus Engine**:
- Implements PBFT-variant consensus algorithm
- Coordinates voting rounds among nodes
- Handles view changes and leader election
- Ensures Byzantine fault tolerance

**Proof Verifier**:
- Validates Z3 proofs using AethelJudge
- Calculates proof difficulty metrics
- Submits verification results to consensus
- Detects invalid proof attempts

**State Store**:
- Maintains local copy of global state
- Implements Merkle tree for efficient verification
- Handles state synchronization with peers
- Validates conservation properties

**P2P Network**:
- Manages peer discovery and connections
- Broadcasts proof blocks and consensus messages
- Handles network partitions gracefully
- Implements gossip protocol for state propagation

## Components and Interfaces

### 1. Consensus Engine

The consensus engine implements a modified PBFT algorithm optimized for proof verification.

#### Core Algorithm: Proof-PBFT

Traditional PBFT has three phases: Pre-Prepare, Prepare, Commit. We add a fourth phase: Verify.

**Phase 0: Verify** (New)
```
Input: proof_block
Output: verification_result

For each proof in proof_block:
    result = AethelJudge.verify(proof)
    difficulty = measure_verification_time(result)
    
Return (all_valid, difficulty_sum)
```

**Phase 1: Pre-Prepare**
```
Leader selects proof_block from mempool
Leader broadcasts: <PRE-PREPARE, view, seq, proof_block, signature>
```

**Phase 2: Prepare**
```
Each node verifies proof_block independently
If valid: broadcast <PREPARE, view, seq, digest, verification_result, signature>
Wait for 2f+1 matching PREPARE messages (Byzantine quorum)
```

**Phase 3: Commit**
```
If prepared: broadcast <COMMIT, view, seq, digest, signature>
Wait for 2f+1 matching COMMIT messages
Execute state transition
```

**Phase 4: Finalize**
```
Update local state with new Merkle root
Distribute rewards based on verification_result
Broadcast state update to network
```

#### View Change Protocol

When leader fails or timeout occurs:
```
1. Node broadcasts <VIEW-CHANGE, new_view, last_stable_checkpoint, signature>
2. Wait for 2f+1 VIEW-CHANGE messages
3. New leader (node_id = new_view mod N) takes over
4. New leader broadcasts <NEW-VIEW, new_view, view_change_messages, signature>
5. Resume consensus with new leader
```

#### Interface

```python
class ConsensusEngine:
    def __init__(self, node_id: str, validator_stake: int, network: P2PNetwork):
        self.node_id = node_id
        self.validator_stake = validator_stake
        self.network = network
        self.view = 0
        self.sequence = 0
        self.state_store = StateStore()
        self.proof_verifier = ProofVerifier()
        
    def start_consensus_round(self, proof_block: ProofBlock) -> ConsensusResult:
        """Initiate a new consensus round for the given proof block."""
        pass
        
    def handle_pre_prepare(self, message: PrePrepareMessage) -> None:
        """Process PRE-PREPARE message from leader."""
        pass
        
    def handle_prepare(self, message: PrepareMessage) -> None:
        """Process PREPARE message from peer."""
        pass
        
    def handle_commit(self, message: CommitMessage) -> None:
        """Process COMMIT message from peer."""
        pass
        
    def handle_view_change(self, message: ViewChangeMessage) -> None:
        """Handle view change when leader fails."""
        pass
        
    def is_leader(self) -> bool:
        """Check if this node is the current leader."""
        return (self.view % self.network.node_count()) == hash(self.node_id)
        
    def verify_quorum(self, messages: List[Message]) -> bool:
        """Verify that we have Byzantine quorum (2f+1 messages)."""
        return len(messages) >= (2 * self.max_faulty_nodes() + 1)
        
    def max_faulty_nodes(self) -> int:
        """Calculate maximum number of Byzantine nodes we can tolerate."""
        return (self.network.node_count() - 1) // 3
```

### 2. Proof Verifier

Wraps AethelJudge to provide verification with difficulty measurement.

#### Difficulty Calculation

Proof difficulty is measured by:
1. **Verification Time**: Wall-clock time to verify proof
2. **Z3 Solver Complexity**: Number of SMT solver iterations
3. **Proof Size**: Byte size of the proof object

```python
difficulty = (verification_time_ms * 1000) + (solver_iterations * 10) + (proof_size_bytes)
```

This ensures complex proofs provide higher rewards.

#### Interface

```python
class ProofVerifier:
    def __init__(self, judge: AethelJudge):
        self.judge = judge
        
    def verify_proof(self, proof: Z3Proof) -> VerificationResult:
        """Verify a single Z3 proof and measure difficulty."""
        start_time = time.time()
        solver_stats = {}
        
        try:
            is_valid = self.judge.verify(proof, stats=solver_stats)
            verification_time = (time.time() - start_time) * 1000  # ms
            
            difficulty = self._calculate_difficulty(
                verification_time,
                solver_stats['iterations'],
                len(proof.serialize())
            )
            
            return VerificationResult(
                valid=is_valid,
                difficulty=difficulty,
                verification_time=verification_time,
                proof_hash=hash(proof)
            )
        except Exception as e:
            return VerificationResult(
                valid=False,
                difficulty=0,
                error=str(e)
            )
            
    def verify_proof_block(self, block: ProofBlock) -> BlockVerificationResult:
        """Verify all proofs in a block."""
        results = []
        total_difficulty = 0
        
        for proof in block.proofs:
            result = self.verify_proof(proof)
            results.append(result)
            
            if not result.valid:
                return BlockVerificationResult(
                    valid=False,
                    failed_proof=proof,
                    results=results
                )
            
            total_difficulty += result.difficulty
            
        return BlockVerificationResult(
            valid=True,
            total_difficulty=total_difficulty,
            results=results
        )
        
    def _calculate_difficulty(self, time_ms: float, iterations: int, size_bytes: int) -> int:
        """Calculate proof difficulty score."""
        return int((time_ms * 1000) + (iterations * 10) + size_bytes)
```

### 3. State Store

Manages distributed state using Merkle trees for efficient verification.

#### Merkle Tree Structure

```
                    Root Hash
                   /         \
              H(A,B)          H(C,D)
             /     \          /     \
          H(A)    H(B)     H(C)    H(D)
           |       |        |       |
        State_A State_B State_C State_D
```

Each leaf contains:
- Account balances (for token rewards)
- Proof verification history
- Validator stakes
- Conservation checksum

#### Interface

```python
class StateStore:
    def __init__(self, persistence_layer: PersistenceLayer):
        self.merkle_tree = MerkleTree()
        self.persistence = persistence_layer
        self.conservation_validator = ConservationValidator()
        
    def apply_state_transition(self, transition: StateTransition) -> bool:
        """Apply a state transition and update Merkle tree."""
        # Validate conservation property
        if not self.conservation_validator.validate(transition):
            return False
            
        # Apply changes
        for change in transition.changes:
            self.merkle_tree.update(change.key, change.value)
            
        # Persist to disk
        self.persistence.save_state(self.merkle_tree.root_hash, transition)
        
        return True
        
    def get_merkle_proof(self, key: str) -> MerkleProof:
        """Generate Merkle proof for a specific state key."""
        return self.merkle_tree.generate_proof(key)
        
    def verify_merkle_proof(self, proof: MerkleProof, root_hash: str) -> bool:
        """Verify a Merkle proof against a root hash."""
        return self.merkle_tree.verify_proof(proof, root_hash)
        
    def sync_from_peer(self, peer_root_hash: str, peer_address: str) -> bool:
        """Synchronize state from a peer node."""
        # Request Merkle tree snapshot
        snapshot = self.network.request_state_snapshot(peer_address, peer_root_hash)
        
        # Verify snapshot integrity
        if hash(snapshot) != peer_root_hash:
            return False
            
        # Apply snapshot
        self.merkle_tree.load_snapshot(snapshot)
        self.persistence.save_snapshot(snapshot)
        
        return True
        
    def get_conservation_checksum(self) -> int:
        """Calculate total value in system (must be conserved)."""
        return self.conservation_validator.calculate_total_value(self.merkle_tree)
```

### 4. P2P Network Layer

Handles peer-to-peer communication using libp2p.

#### Network Topology

- **Gossip Protocol**: State updates propagate via gossip
- **DHT**: Distributed hash table for peer discovery
- **Pub/Sub**: Topic-based message broadcasting

#### Interface

```python
class P2PNetwork:
    def __init__(self, node_id: str, listen_port: int):
        self.node_id = node_id
        self.listen_port = listen_port
        self.peers = {}
        self.message_handlers = {}
        
    def start(self) -> None:
        """Start P2P network listener."""
        pass
        
    def broadcast(self, topic: str, message: Message) -> None:
        """Broadcast message to all peers on topic."""
        pass
        
    def send_to_peer(self, peer_id: str, message: Message) -> None:
        """Send message to specific peer."""
        pass
        
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe to messages on a topic."""
        self.message_handlers[topic] = handler
        
    def discover_peers(self) -> List[PeerInfo]:
        """Discover peers using DHT."""
        pass
        
    def node_count(self) -> int:
        """Return number of connected peers."""
        return len(self.peers)
```

### 5. Reward Distribution System

Calculates and distributes rewards based on proof verification.

#### Reward Formula

```
base_reward = 10 tokens per proof block
difficulty_multiplier = total_difficulty / 1_000_000
node_reward = (base_reward * difficulty_multiplier) / participating_nodes

If node verified correctly: node_reward
If node verified incorrectly: -slash_amount (from stake)
```

#### Interface

```python
class RewardDistributor:
    def __init__(self, state_store: StateStore):
        self.state_store = state_store
        self.base_reward = 10  # tokens
        
    def calculate_rewards(self, consensus_result: ConsensusResult) -> Dict[str, int]:
        """Calculate rewards for all participating nodes."""
        rewards = {}
        
        difficulty_multiplier = consensus_result.total_difficulty / 1_000_000
        total_reward = self.base_reward * difficulty_multiplier
        
        # Count nodes that verified correctly
        correct_nodes = [
            node_id for node_id, result in consensus_result.verifications.items()
            if result.valid
        ]
        
        node_reward = total_reward / len(correct_nodes)
        
        for node_id in correct_nodes:
            rewards[node_id] = node_reward
            
        return rewards
        
    def apply_slashing(self, node_id: str, violation: SlashingViolation) -> int:
        """Apply slashing penalty to a node's stake."""
        stake = self.state_store.get_validator_stake(node_id)
        
        if violation == SlashingViolation.INVALID_VERIFICATION:
            slash_amount = stake * 0.05  # 5% slash
        elif violation == SlashingViolation.DOUBLE_SIGN:
            slash_amount = stake * 0.20  # 20% slash
        else:
            slash_amount = 0
            
        self.state_store.reduce_stake(node_id, slash_amount)
        return slash_amount
        
    def distribute_rewards(self, rewards: Dict[str, int]) -> StateTransition:
        """Create state transition to distribute rewards."""
        changes = []
        
        for node_id, reward in rewards.items():
            changes.append(StateChange(
                key=f"balance:{node_id}",
                value=self.state_store.get_balance(node_id) + reward
            ))
            
        return StateTransition(changes=changes)
```

## Data Models

### ProofBlock

```python
@dataclass
class ProofBlock:
    """A block containing proofs to be verified."""
    block_id: str
    timestamp: int
    proofs: List[Z3Proof]
    previous_block_hash: str
    proposer_id: str
    signature: bytes
    
    def hash(self) -> str:
        """Calculate block hash."""
        return sha256(self.serialize()).hexdigest()
        
    def serialize(self) -> bytes:
        """Serialize block for transmission."""
        pass
```

### ConsensusMessage

```python
@dataclass
class ConsensusMessage:
    """Base class for consensus protocol messages."""
    message_type: MessageType  # PRE_PREPARE, PREPARE, COMMIT, VIEW_CHANGE
    view: int
    sequence: int
    sender_id: str
    signature: bytes
    
@dataclass
class PrePrepareMessage(ConsensusMessage):
    proof_block: ProofBlock
    
@dataclass
class PrepareMessage(ConsensusMessage):
    block_digest: str
    verification_result: BlockVerificationResult
    
@dataclass
class CommitMessage(ConsensusMessage):
    block_digest: str
    
@dataclass
class ViewChangeMessage(ConsensusMessage):
    new_view: int
    last_stable_checkpoint: str
```

### StateTransition

```python
@dataclass
class StateTransition:
    """Represents a change to global state."""
    changes: List[StateChange]
    merkle_root_before: str
    merkle_root_after: str
    conservation_checksum_before: int
    conservation_checksum_after: int
    timestamp: int
    
    def validate_conservation(self) -> bool:
        """Verify that value is conserved across transition."""
        return self.conservation_checksum_before == self.conservation_checksum_after
        
@dataclass
class StateChange:
    key: str
    value: Any
    proof: MerkleProof
```

### VerificationResult

```python
@dataclass
class VerificationResult:
    """Result of verifying a single proof."""
    valid: bool
    difficulty: int
    verification_time: float  # milliseconds
    proof_hash: str
    error: Optional[str] = None
    
@dataclass
class BlockVerificationResult:
    """Result of verifying an entire proof block."""
    valid: bool
    total_difficulty: int
    results: List[VerificationResult]
    failed_proof: Optional[Z3Proof] = None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Proof Verification Completeness
*For any* proof block received by a node, all proofs in the block must be verified using AethelJudge before the node participates in consensus.
**Validates: Requirements 1.1**

### Property 2: Reward-Difficulty Proportionality
*For any* two proofs with difficulties D1 and D2 where D1 < D2, the verification reward for the second proof must be greater than or equal to the first (reward scales with difficulty).
**Validates: Requirements 1.2, 4.4**

### Property 3: Multi-Node Reward Distribution
*For any* proof verified by multiple nodes, the sum of all rewards distributed must equal the total reward for that proof, and each node's share must be proportional to their verification speed and correctness.
**Validates: Requirements 1.3**

### Property 4: Difficulty Monotonicity
*For any* two proofs where Z3 solver time T1 < T2, the calculated difficulty D1 must be less than or equal to D2 (difficulty increases with solver complexity).
**Validates: Requirements 1.4**

### Property 5: Invalid Verification Rejection
*For any* invalid proof verification submitted by a node, the system must reject it and record the failure without accepting it into consensus.
**Validates: Requirements 1.5**

### Property 6: Byzantine Fault Tolerance
*For any* network configuration with N nodes where up to ⌊(N-1)/3⌋ nodes are Byzantine (malicious or faulty), the system must still reach consensus on state transitions.
**Validates: Requirements 2.2**

### Property 7: Quorum-Based Conflict Resolution
*For any* set of conflicting proof verifications, the system must resolve the conflict by accepting the verification supported by a Byzantine quorum (2f+1 nodes) and rejecting others.
**Validates: Requirements 2.3**

### Property 8: Consensus Safety
*For any* two honest nodes in the same consensus round, they must never accept conflicting states for the same sequence number (safety property).
**Validates: Requirements 2.4, 7.1**

### Property 9: Consensus Liveness
*For any* consensus round where at least ⌈2N/3⌉ nodes are honest and responsive, consensus must complete within the timeout threshold (liveness property).
**Validates: Requirements 2.5**

### Property 10: View Change on Timeout
*For any* consensus round that exceeds the timeout threshold, the system must initiate a view change and start a new round with an updated leader.
**Validates: Requirements 2.6**

### Property 11: State Propagation Completeness
*For any* finalized state transition, all honest nodes in the network must eventually receive the Merkle tree update.
**Validates: Requirements 3.2**

### Property 12: Proof-Based Conflict Resolution
*For any* detected state conflict between nodes, the system must resolve it by verifying the proof chain and accepting the state with valid proof lineage.
**Validates: Requirements 3.3**

### Property 13: Eventual Consistency
*For any* execution of the consensus protocol, all honest nodes must eventually converge to the same state (eventual consistency property).
**Validates: Requirements 3.4**

### Property 14: Conservation Across State Transitions
*For any* state transition applied to the distributed system, the total value in the system (conservation checksum) must remain constant before and after the transition.
**Validates: Requirements 3.6, 5.2**

### Property 15: Reward Issuance Correctness
*For any* node that successfully verifies a proof and participates in consensus, the system must issue the calculated verification reward to that node's balance.
**Validates: Requirements 4.1**

### Property 16: Slashing on Invalid Verification
*For any* node that submits an invalid proof verification, the system must reduce their validator stake by the slashing amount.
**Validates: Requirements 4.2**

### Property 17: Minimum Stake Enforcement
*For any* node attempting to participate in consensus, the system must reject participation if their validator stake is below the minimum threshold.
**Validates: Requirements 4.3**

### Property 18: Reward Distribution Timeliness
*For any* consensus round that finalizes, rewards must be distributed to all participating nodes within 10 seconds of finalization.
**Validates: Requirements 4.5**

### Property 19: No Offline Penalties
*For any* node that is offline during a consensus round, the system must not apply any slashing penalties to their validator stake.
**Validates: Requirements 4.6**

### Property 20: Token Supply Conservation
*For any* sequence of consensus rounds, the total token supply must never exceed the defined emission schedule (conservation of token supply).
**Validates: Requirements 4.7**

### Property 21: Proof Mempool Integration
*For any* proof generated by AethelJudge, the system must submit it to the proof mempool for network verification.
**Validates: Requirements 5.1**

### Property 22: Zero-Knowledge Privacy Preservation
*For any* proof using Ghost_Identity, the consensus protocol must not reveal any private information about the identity during verification or state propagation.
**Validates: Requirements 5.3**

### Property 23: Signature Verification Before Consensus
*For any* proof involving sovereign identity signatures, the system must verify all signatures before allowing the proof to participate in consensus.
**Validates: Requirements 5.5**

### Property 24: Consensus Time Scalability
*For any* network with N nodes where 1000 ≤ N ≤ 10000, consensus time must not exceed 30 seconds (scalability property).
**Validates: Requirements 6.2**

### Property 25: Mempool Prioritization
*For any* proof mempool containing multiple pending proofs, proofs must be ordered by difficulty (highest difficulty first) when selecting proofs for the next block.
**Validates: Requirements 6.3**

### Property 26: Adaptive Timeout Adjustment
*For any* network condition where latency exceeds 500ms, the system must dynamically increase consensus timeouts to prevent premature view changes.
**Validates: Requirements 6.5**

### Property 27: Sybil Resistance via Stake
*For any* attacker controlling multiple nodes, their influence on consensus must be limited by their total validator stake, not by the number of nodes they control.
**Validates: Requirements 7.2**

### Property 28: 51% Attack Resistance
*For any* network configuration where up to 51% of nodes are malicious, the system must still prevent acceptance of invalid proof verifications (requires 67% for Byzantine consensus).
**Validates: Requirements 7.3**

### Property 29: Long-Range Attack Prevention
*For any* alternative state history presented by an attacker, the system must reject it if it violates the conservation property at any point in the history.
**Validates: Requirements 7.4**

### Property 30: Cryptographic Proof Integrity
*For any* proof submitted to the network, the system must verify its cryptographic signature and reject proofs with invalid or missing signatures.
**Validates: Requirements 7.5**

### Property 31: Partition Safety
*For any* network partition that prevents Byzantine quorum, the system must halt consensus rather than risk accepting inconsistent states.
**Validates: Requirements 7.6**

### Property 32: Consensus Metrics Emission
*For any* completed consensus round, the system must emit metrics including round duration, participant count, proof count, and total difficulty.
**Validates: Requirements 8.1**

### Property 33: Real-Time Mempool Metrics
*For any* query of mempool metrics, the system must return accurate real-time values for mempool size and proof processing rate.
**Validates: Requirements 8.2**

### Property 34: Low Accuracy Alerting
*For any* node whose verification accuracy falls below 95% over a sliding window, the system must trigger an alert to the node operator.
**Validates: Requirements 8.3**

### Property 35: Reward Tracking Accuracy
*For any* node participating in consensus, the system must accurately track and report their cumulative verification rewards.
**Validates: Requirements 8.4**

### Property 36: Byzantine Behavior Logging
*For any* detected Byzantine behavior (invalid verification, double-signing, etc.), the system must log the incident with cryptographic evidence.
**Validates: Requirements 8.5**

## Error Handling

### Consensus Failures

**Leader Failure**:
- Detection: Timeout waiting for PRE-PREPARE message
- Recovery: Initiate view change, elect new leader
- Guarantee: Liveness preserved if 67%+ nodes honest

**Network Partition**:
- Detection: Unable to reach Byzantine quorum
- Recovery: Halt consensus, wait for partition to heal
- Guarantee: Safety preserved (no inconsistent states)

**Invalid Proof Block**:
- Detection: Proof verification fails during VERIFY phase
- Recovery: Reject block, do not broadcast PREPARE message
- Guarantee: Invalid proofs never reach consensus

### State Synchronization Failures

**Merkle Proof Mismatch**:
- Detection: Merkle proof verification fails against root hash
- Recovery: Request full state snapshot from multiple peers
- Guarantee: Eventually sync to correct state

**Conservation Violation**:
- Detection: State transition violates conservation checksum
- Recovery: Reject transition, maintain previous state
- Guarantee: Value conservation always maintained

**Peer Unavailability**:
- Detection: Peer doesn't respond to state sync request
- Recovery: Try alternative peers from peer list
- Guarantee: Eventually sync if any honest peer available

### Economic System Failures

**Insufficient Stake**:
- Detection: Node attempts consensus with stake below minimum
- Recovery: Reject participation, notify node operator
- Guarantee: Only adequately staked nodes participate

**Reward Distribution Failure**:
- Detection: State transition for rewards fails validation
- Recovery: Retry reward distribution in next block
- Guarantee: Rewards eventually distributed (at-least-once semantics)

**Slashing Dispute**:
- Detection: Node disputes slashing event
- Recovery: Provide cryptographic evidence of violation
- Guarantee: Only provably invalid behavior is slashed

## Testing Strategy

### Dual Testing Approach

The Proof-of-Proof consensus protocol requires both unit testing and property-based testing for comprehensive validation:

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Example: Test consensus with exactly 4 nodes (minimum Byzantine configuration)
- Example: Test mempool with exactly 1000 pending proofs
- Example: Test reward distribution with specific difficulty values
- Edge case: Test view change when leader crashes mid-round
- Edge case: Test state sync when new node joins during consensus
- Integration: Test AethelJudge integration with proof verification

**Property Tests**: Verify universal properties across all inputs
- Property tests must run minimum 100 iterations due to randomization
- Each test must reference its design document property
- Tag format: **Feature: proof-of-proof-consensus, Property {N}: {property_text}**

### Property-Based Testing Configuration

**Library Selection**:
- Python: Use Hypothesis for property-based testing
- Rust: Use proptest or quickcheck

**Test Configuration**:
```python
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(
    node_count=st.integers(min_value=4, max_value=100),
    byzantine_ratio=st.floats(min_value=0.0, max_value=0.33)
)
def test_property_6_byzantine_fault_tolerance(node_count, byzantine_ratio):
    """
    Feature: proof-of-proof-consensus
    Property 6: Byzantine Fault Tolerance
    
    For any network configuration with N nodes where up to ⌊(N-1)/3⌋ nodes 
    are Byzantine, the system must still reach consensus.
    """
    byzantine_count = int(node_count * byzantine_ratio)
    network = create_test_network(node_count, byzantine_count)
    
    proof_block = generate_random_proof_block()
    result = network.run_consensus(proof_block)
    
    assert result.consensus_reached
    assert result.finalized_state is not None
```

### Test Coverage Requirements

**Consensus Protocol**:
- Unit tests for each message type (PRE-PREPARE, PREPARE, COMMIT, VIEW-CHANGE)
- Property tests for Byzantine fault tolerance (Property 6)
- Property tests for safety and liveness (Properties 8, 9)
- Edge cases for leader failure and view changes

**Proof Verification**:
- Unit tests for specific proof types (arithmetic, conservation, identity)
- Property tests for difficulty calculation (Properties 2, 4)
- Property tests for verification completeness (Property 1)
- Edge cases for malformed proofs

**State Synchronization**:
- Unit tests for Merkle tree operations
- Property tests for eventual consistency (Property 13)
- Property tests for conservation preservation (Property 14)
- Edge cases for network partitions

**Economic System**:
- Unit tests for reward calculation with specific values
- Property tests for reward distribution (Properties 15, 18)
- Property tests for slashing (Property 16)
- Property tests for token supply conservation (Property 20)

**Security**:
- Unit tests for specific attack scenarios
- Property tests for attack resistance (Properties 27, 28, 29)
- Property tests for cryptographic integrity (Property 30)
- Edge cases for network partitions (Property 31)

### Performance Testing

In addition to correctness testing, performance benchmarks are required:

**Consensus Latency**:
- Measure consensus time with 1000 nodes (Requirement 6.1)
- Measure consensus time scaling from 1000 to 10,000 nodes (Property 24)

**Proof Throughput**:
- Measure proof verification rate (Requirement 6.4)
- Measure mempool processing rate (Property 33)

**State Sync Performance**:
- Measure time for new node to sync (Requirement 3.1)
- Measure Merkle tree update propagation time (Property 11)

These performance tests complement correctness tests but are not property-based tests.

## Implementation Notes

### Phase 1: Core Consensus (Weeks 1-3)
- Implement PBFT consensus engine
- Implement proof verifier with difficulty calculation
- Implement basic P2P networking
- Unit tests for consensus messages

### Phase 2: State Management (Weeks 4-5)
- Implement Merkle tree state store
- Implement state synchronization protocol
- Implement conservation validator
- Property tests for state consistency

### Phase 3: Economic System (Week 6)
- Implement reward distribution
- Implement slashing mechanism
- Implement stake management
- Property tests for economic properties

### Phase 4: Integration (Week 7)
- Integrate with AethelJudge
- Integrate with Ghost_Identity
- Integrate with persistence layer
- Integration tests

### Phase 5: Security & Testing (Weeks 8-9)
- Implement attack detection
- Comprehensive property-based testing
- Performance benchmarking
- Security audit

### Phase 6: Deployment (Week 10)
- Deploy testnet with 100 nodes
- Monitor and optimize
- Deploy mainnet with 1000+ nodes
- Documentation and operator guides
