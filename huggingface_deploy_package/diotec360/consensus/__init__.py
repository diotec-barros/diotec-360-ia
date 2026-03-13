"""
Aethel Consensus Protocol - Proof-of-Proof Consensus

This module implements a Byzantine fault-tolerant consensus protocol where
network security emerges from Z3 proof verification. Instead of mining useless
hashes, nodes compete to verify logical correctness.

Key Components:
- ConsensusEngine: PBFT-variant consensus algorithm
- ProofVerifier: Z3 proof verification with difficulty calculation
- StateStore: Merkle tree-based distributed state management
- P2PNetwork: Peer-to-peer networking layer
- ProofMempool: Priority queue for pending proofs
- RewardDistributor: Economic incentive system (future)
"""

from diotec360.consensus.data_models import (
    ProofBlock,
    ConsensusMessage,
    PrePrepareMessage,
    PrepareMessage,
    CommitMessage,
    ViewChangeMessage,
    StateTransition,
    StateChange,
    VerificationResult,
    BlockVerificationResult,
    ConsensusResult,
    MessageType,
    SlashingViolation,
)

from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.p2p_network import P2PNetwork, P2PNetworkSync, GossipMessage, RetryConfig
from diotec360.consensus.consensus_engine import ConsensusEngine, ConsensusState
from diotec360.consensus.proof_mempool import ProofMempool

__all__ = [
    "ProofBlock",
    "ConsensusMessage",
    "PrePrepareMessage",
    "PrepareMessage",
    "CommitMessage",
    "ViewChangeMessage",
    "StateTransition",
    "StateChange",
    "VerificationResult",
    "BlockVerificationResult",
    "ConsensusResult",
    "MessageType",
    "SlashingViolation",
    "ProofVerifier",
    "P2PNetwork",
    "P2PNetworkSync",
    "GossipMessage",
    "RetryConfig",
    "ConsensusEngine",
    "ConsensusState",
    "ProofMempool",
]
