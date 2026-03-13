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
Core data models for the Proof-of-Proof consensus protocol.

This module defines all data structures used in the consensus protocol:
- ProofBlock: Container for proofs to be verified
- ConsensusMessage: Base class for PBFT protocol messages
- StateTransition: Represents changes to global state
- VerificationResult: Result of proof verification
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum
import hashlib
import json
import time

# Import Ghost Identity types
try:
    from diotec360.core.ghost_identity import GhostProof, RingSignature
except ImportError:
    # Fallback for testing without full Aethel installation
    GhostProof = Any
    RingSignature = Any


class MessageType(Enum):
    """Types of consensus protocol messages."""
    PRE_PREPARE = "PRE_PREPARE"
    PREPARE = "PREPARE"
    COMMIT = "COMMIT"
    VIEW_CHANGE = "VIEW_CHANGE"
    NEW_VIEW = "NEW_VIEW"


class SlashingViolation(Enum):
    """Types of slashing violations."""
    INVALID_VERIFICATION = "INVALID_VERIFICATION"
    DOUBLE_SIGN = "DOUBLE_SIGN"


@dataclass
class SignedProof:
    """
    A proof with sovereign identity signature.
    
    Attributes:
        proof_data: The actual proof content (intent or proof object)
        public_key: Public key of the proof creator (hex string)
        signature: ED25519 signature over proof_data (hex string)
        timestamp: Unix timestamp when proof was signed
    """
    proof_data: Any
    public_key: str = ""
    signature: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "proof_data": self.proof_data,
            "public_key": self.public_key,
            "signature": self.signature,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SignedProof":
        """Create from dictionary."""
        return cls(
            proof_data=data["proof_data"],
            public_key=data.get("public_key", ""),
            signature=data.get("signature", ""),
            timestamp=data.get("timestamp", int(time.time())),
        )


@dataclass
class ProofBlock:
    """
    A block containing proofs to be verified.
    
    Attributes:
        block_id: Unique identifier for this block
        timestamp: Unix timestamp when block was created
        proofs: List of Z3 proofs to verify (can be SignedProof or raw proofs)
        previous_block_hash: Hash of the previous block
        proposer_id: ID of the node that proposed this block
        signature: Cryptographic signature from proposer
        transactions: Optional list of transactions for double-spend detection
    """
    block_id: str
    timestamp: int
    proofs: List[Any]  # Will be SignedProof or Z3Proof objects
    previous_block_hash: str
    proposer_id: str
    signature: bytes = b""
    transactions: List[Dict[str, Any]] = field(default_factory=list)
    
    def hash(self) -> str:
        """Calculate block hash using SHA-256."""
        block_data = {
            "block_id": self.block_id,
            "timestamp": self.timestamp,
            "proofs": [str(p) for p in self.proofs],
            "previous_block_hash": self.previous_block_hash,
            "proposer_id": self.proposer_id,
        }
        serialized = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()
    
    def serialize(self) -> bytes:
        """Serialize block for transmission."""
        block_data = {
            "block_id": self.block_id,
            "timestamp": self.timestamp,
            "proofs": [str(p) for p in self.proofs],
            "previous_block_hash": self.previous_block_hash,
            "proposer_id": self.proposer_id,
            "signature": self.signature.hex(),
        }
        return json.dumps(block_data).encode()
    
    @classmethod
    def deserialize(cls, data: bytes) -> "ProofBlock":
        """Deserialize block from bytes."""
        block_data = json.loads(data.decode())
        return cls(
            block_id=block_data["block_id"],
            timestamp=block_data["timestamp"],
            proofs=block_data["proofs"],  # Will need proper deserialization
            previous_block_hash=block_data["previous_block_hash"],
            proposer_id=block_data["proposer_id"],
            signature=bytes.fromhex(block_data["signature"]),
        )


@dataclass
class ConsensusMessage:
    """
    Base class for consensus protocol messages.
    
    Attributes:
        message_type: Type of consensus message
        view: Current view number
        sequence: Sequence number for this consensus round
        sender_id: ID of the node sending this message
        signature: Cryptographic signature from sender
        ghost_proof: Optional Ghost Identity proof for anonymous participation
        use_ghost_identity: Whether this message uses Ghost Identity
    """
    message_type: MessageType
    view: int
    sequence: int
    sender_id: str
    signature: bytes = b""
    ghost_proof: Optional[Any] = None  # GhostProof type
    use_ghost_identity: bool = False
    
    def serialize(self) -> bytes:
        """Serialize message for transmission."""
        msg_data = {
            "message_type": self.message_type.value,
            "view": self.view,
            "sequence": self.sequence,
            "sender_id": self.sender_id,
            "signature": self.signature.hex(),
            "use_ghost_identity": self.use_ghost_identity,
        }
        
        # Don't serialize ghost_proof to avoid leaking private information
        # Ghost proof is verified separately
        
        return json.dumps(msg_data).encode()


@dataclass
class PrePrepareMessage(ConsensusMessage):
    """
    PRE-PREPARE message sent by leader to propose a proof block.
    
    Attributes:
        proof_block: The block being proposed for consensus
    """
    proof_block: ProofBlock = None
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.PRE_PREPARE


@dataclass
class PrepareMessage(ConsensusMessage):
    """
    PREPARE message sent by nodes after verifying a proof block.
    
    Attributes:
        block_digest: Hash of the proof block being verified
        verification_result: Result of proof verification
    """
    block_digest: str = ""
    verification_result: Optional["BlockVerificationResult"] = None
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.PREPARE


@dataclass
class CommitMessage(ConsensusMessage):
    """
    COMMIT message sent by nodes after reaching prepare quorum.
    
    Attributes:
        block_digest: Hash of the proof block being committed
    """
    block_digest: str = ""
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.COMMIT


@dataclass
class ViewChangeMessage(ConsensusMessage):
    """
    VIEW-CHANGE message sent when leader fails or timeout occurs.
    
    Attributes:
        new_view: The new view number being proposed
        last_stable_checkpoint: Hash of last finalized state
    """
    new_view: int = 0
    last_stable_checkpoint: str = ""
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.VIEW_CHANGE


@dataclass
class NewViewMessage(ConsensusMessage):
    """
    NEW-VIEW message sent by new leader after view change.
    
    Attributes:
        new_view: The new view number
        view_change_messages: List of VIEW-CHANGE messages that triggered this
        checkpoint: Hash of the checkpoint to resume from
    """
    new_view: int = 0
    view_change_messages: List[ViewChangeMessage] = field(default_factory=list)
    checkpoint: str = ""
    
    def __post_init__(self):
        """Ensure message type is set correctly."""
        self.message_type = MessageType.NEW_VIEW


@dataclass
class StateChange:
    """
    Represents a single change to the global state.
    
    Attributes:
        key: State key being modified
        value: New value for the key
        proof: Merkle proof for this change (optional)
    """
    key: str
    value: Any
    proof: Optional[Any] = None  # Will be MerkleProof


@dataclass
class StateTransition:
    """
    Represents a change to global state with conservation validation.
    
    Attributes:
        changes: List of state changes to apply
        merkle_root_before: Merkle root hash before transition
        merkle_root_after: Merkle root hash after transition
        conservation_checksum_before: Total value before transition
        conservation_checksum_after: Total value after transition
        timestamp: Unix timestamp of transition
    """
    changes: List[StateChange]
    merkle_root_before: str = ""
    merkle_root_after: str = ""
    conservation_checksum_before: int = 0
    conservation_checksum_after: int = 0
    timestamp: int = field(default_factory=lambda: int(time.time()))
    
    def validate_conservation(self) -> bool:
        """
        Verify that value is conserved across transition.
        
        Returns:
            True if conservation checksum is unchanged
        """
        return self.conservation_checksum_before == self.conservation_checksum_after


@dataclass
class VerificationResult:
    """
    Result of verifying a single proof.
    
    Attributes:
        valid: Whether the proof is valid
        difficulty: Calculated difficulty score
        verification_time: Time taken to verify (milliseconds)
        proof_hash: Hash of the verified proof
        error: Error message if verification failed
    """
    valid: bool
    difficulty: int
    verification_time: float
    proof_hash: str
    error: Optional[str] = None


@dataclass
class BlockVerificationResult:
    """
    Result of verifying an entire proof block.
    
    Attributes:
        valid: Whether all proofs in the block are valid
        total_difficulty: Sum of all proof difficulties
        results: Individual verification results for each proof
        failed_proof: The proof that failed (if any)
    """
    valid: bool
    total_difficulty: int
    results: List[VerificationResult]
    failed_proof: Optional[Any] = None  # Will be Z3Proof


@dataclass
class ConsensusResult:
    """
    Result of a consensus round.
    
    Attributes:
        consensus_reached: Whether consensus was achieved
        finalized_state: The finalized state after consensus
        total_difficulty: Total difficulty of verified proofs
        verifications: Map of node_id to verification result
        participating_nodes: List of nodes that participated
    """
    consensus_reached: bool
    finalized_state: Optional[str] = None
    total_difficulty: int = 0
    verifications: Dict[str, VerificationResult] = field(default_factory=dict)
    participating_nodes: List[str] = field(default_factory=list)


@dataclass
class PeerInfo:
    """
    Information about a peer node in the network.
    
    Attributes:
        peer_id: Unique identifier for the peer
        address: Network address (IP:port)
        stake: Validator stake amount
        last_seen: Unix timestamp of last communication
    """
    peer_id: str
    address: str
    stake: int = 0
    last_seen: int = field(default_factory=lambda: int(time.time()))


@dataclass
class MerkleProof:
    """
    Merkle proof for verifying state inclusion.
    
    Attributes:
        leaf_hash: Hash of the leaf node
        path: List of sibling hashes from leaf to root
        root_hash: Expected root hash
    """
    leaf_hash: str
    path: List[str]
    root_hash: str
