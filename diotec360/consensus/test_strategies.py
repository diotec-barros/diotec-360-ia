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
Hypothesis strategies for property-based testing of consensus protocol.

This module provides reusable strategies for generating test data for
property-based tests using the Hypothesis library.
"""

from hypothesis import strategies as st
from diotec360.consensus.data_models import (
    ProofBlock,
    StateChange,
    StateTransition,
    VerificationResult,
    PeerInfo,
)
import time


# Basic strategies
node_ids = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
    min_size=5,
    max_size=20
).map(lambda s: f"node_{s}")

block_ids = st.text(
    alphabet="0123456789abcdef",
    min_size=32,
    max_size=64
)

hashes = st.text(
    alphabet="0123456789abcdef",
    min_size=64,
    max_size=64
)

timestamps = st.integers(
    min_value=int(time.time()) - 86400,  # Last 24 hours
    max_value=int(time.time()) + 86400   # Next 24 hours
)

stakes = st.integers(min_value=1000, max_value=1000000)

difficulties = st.integers(min_value=1, max_value=10000000)

verification_times = st.floats(min_value=0.1, max_value=10000.0)


# Network configuration strategies
@st.composite
def network_configs(draw):
    """Generate network configuration for testing."""
    node_count = draw(st.integers(min_value=4, max_value=100))
    byzantine_ratio = draw(st.floats(min_value=0.0, max_value=0.33))
    byzantine_count = int(node_count * byzantine_ratio)
    
    return {
        "node_count": node_count,
        "byzantine_count": byzantine_count,
        "honest_count": node_count - byzantine_count,
    }


# Proof block strategies
@st.composite
def proof_blocks(draw, min_proofs=1, max_proofs=10):
    """
    Generate random proof blocks for testing.
    
    Args:
        draw: Hypothesis draw function
        min_proofs: Minimum number of proofs in block
        max_proofs: Maximum number of proofs in block
        
    Returns:
        ProofBlock instance
    """
    block_id = draw(block_ids)
    timestamp = draw(timestamps)
    num_proofs = draw(st.integers(min_value=min_proofs, max_value=max_proofs))
    
    # Generate mock proofs (strings for now, will be Z3Proof objects later)
    proofs = [f"proof_{i}_{block_id}" for i in range(num_proofs)]
    
    previous_hash = draw(hashes)
    proposer_id = draw(node_ids)
    
    return ProofBlock(
        block_id=block_id,
        timestamp=timestamp,
        proofs=proofs,
        previous_block_hash=previous_hash,
        proposer_id=proposer_id,
    )


# State change strategies
@st.composite
def state_changes(draw):
    """Generate random state changes for testing."""
    key = draw(st.text(min_size=1, max_size=50))
    value = draw(st.integers(min_value=0, max_value=1000000))
    
    return StateChange(key=key, value=value)


@st.composite
def state_transitions(draw, conserve_value=True):
    """
    Generate random state transitions for testing.
    
    Args:
        draw: Hypothesis draw function
        conserve_value: If True, ensure conservation checksum is preserved
        
    Returns:
        StateTransition instance
    """
    num_changes = draw(st.integers(min_value=1, max_value=10))
    changes = [draw(state_changes()) for _ in range(num_changes)]
    
    merkle_before = draw(hashes)
    merkle_after = draw(hashes)
    
    checksum_before = draw(st.integers(min_value=0, max_value=1000000))
    
    if conserve_value:
        checksum_after = checksum_before
    else:
        checksum_after = draw(st.integers(min_value=0, max_value=1000000))
    
    timestamp = draw(timestamps)
    
    return StateTransition(
        changes=changes,
        merkle_root_before=merkle_before,
        merkle_root_after=merkle_after,
        conservation_checksum_before=checksum_before,
        conservation_checksum_after=checksum_after,
        timestamp=timestamp,
    )


# Verification result strategies
@st.composite
def verification_results(draw, force_valid=None):
    """
    Generate random verification results for testing.
    
    Args:
        draw: Hypothesis draw function
        force_valid: If True/False, force valid to that value; if None, random
        
    Returns:
        VerificationResult instance
    """
    if force_valid is None:
        valid = draw(st.booleans())
    else:
        valid = force_valid
    
    difficulty = draw(difficulties)
    verification_time = draw(verification_times)
    proof_hash = draw(hashes)
    
    error = None
    if not valid:
        error = draw(st.text(min_size=10, max_size=100))
    
    return VerificationResult(
        valid=valid,
        difficulty=difficulty,
        verification_time=verification_time,
        proof_hash=proof_hash,
        error=error,
    )


# Peer info strategies
@st.composite
def peer_infos(draw):
    """Generate random peer information for testing."""
    peer_id = draw(node_ids)
    address = f"mock://{peer_id}"
    stake = draw(stakes)
    last_seen = draw(timestamps)
    
    return PeerInfo(
        peer_id=peer_id,
        address=address,
        stake=stake,
        last_seen=last_seen,
    )


# Lists of entities
proof_block_lists = st.lists(proof_blocks(), min_size=1, max_size=10)
state_change_lists = st.lists(state_changes(), min_size=1, max_size=20)
peer_info_lists = st.lists(peer_infos(), min_size=1, max_size=100)
