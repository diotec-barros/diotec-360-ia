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
End-to-end integration tests for Proof-of-Proof consensus protocol - Task 23.1

This test suite validates the complete consensus flow with multiple nodes.
"""

import pytest
from typing import Dict

from diotec360.consensus.consensus_engine import ConsensusEngine
from diotec360.consensus.proof_verifier import ProofVerifier
from diotec360.consensus.state_store import StateStore
from diotec360.consensus.proof_mempool import ProofMempool
from diotec360.consensus.mock_network import MockP2PNetwork
from diotec360.consensus.data_models import (
    ProofBlock, PrePrepareMessage, PrepareMessage, CommitMessage,
    MessageType, PeerInfo
)
from diotec360.consensus.monitoring import MetricsCollector


def create_test_network(node_count: int, ghost_config=None) -> Dict[str, ConsensusEngine]:
    """Create a test network with the specified number of nodes."""
    nodes = {}
    networks = {}
    
    for i in range(node_count):
        node_id = f'node{i}'
        network = MockP2PNetwork(node_id)
        networks[node_id] = network
        
        node = ConsensusEngine(
            node_id=node_id,
            validator_stake=1000,
            network=network,
            proof_verifier=ProofVerifier(),
            state_store=StateStore(),
            proof_mempool=ProofMempool(),
            ghost_config=ghost_config,
            metrics_collector=MetricsCollector(),
        )
        nodes[node_id] = node
    
    for node_id, network in networks.items():
        for other_id in networks.keys():
            if node_id != other_id:
                peer_info = PeerInfo(
                    peer_id=other_id,
                    address=f'localhost:{5000 + int(other_id[-1])}',
                    stake=1000,
                )
                network.add_peer(peer_info)
    
    for node_id, node in nodes.items():
        node.pre_prepare_handler = node.handle_pre_prepare
        node.prepare_handler = node.handle_prepare
        node.commit_handler = node.handle_commit
        node.view_change_handler = node.handle_view_change
    
    return nodes


def run_consensus_round(nodes: Dict[str, ConsensusEngine], proof_block: ProofBlock, use_ghost: bool = False):
    """Run a complete consensus round."""
    leader_id = 'node0'
    leader = nodes[leader_id]
    leader.start_consensus_round(proof_block)
    
    pre_prepare = PrePrepareMessage(
        message_type=MessageType.PRE_PREPARE,
        view=leader.view,
        sequence=leader.sequence,
        sender_id=leader_id,
        proof_block=proof_block,
        use_ghost_identity=use_ghost,
    )
    
    for node_id, node in nodes.items():
        if node_id != leader_id:
            node.handle_pre_prepare(pre_prepare)
    
    prepare_messages = []
    for node_id, node in nodes.items():
        if node.current_state and node.current_state.verification_result:
            prepare = PrepareMessage(
                message_type=MessageType.PREPARE,
                view=node.view,
                sequence=node.sequence,
                sender_id=node_id,
                block_digest=proof_block.hash(),
                verification_result=node.current_state.verification_result,
                use_ghost_identity=use_ghost,
            )
            prepare_messages.append(prepare)
    
    for node in nodes.values():
        for prepare in prepare_messages:
            node.handle_prepare(prepare)
    
    commit_messages = []
    for node_id, node in nodes.items():
        if node.current_state and node.current_state.prepared:
            commit = CommitMessage(
                message_type=MessageType.COMMIT,
                view=node.view,
                sequence=node.sequence,
                sender_id=node_id,
                block_digest=proof_block.hash(),
                use_ghost_identity=use_ghost,
            )
            commit_messages.append(commit)
    
    result = None
    for node in nodes.values():
        for commit in commit_messages:
            r = node.handle_commit(commit)
            if r and r.consensus_reached:
                result = r
                break
        if result:
            break
    
    return result


def test_four_node_consensus_basic():
    """Test basic consensus with 4 nodes (minimum Byzantine configuration)."""
    nodes = create_test_network(4)
    
    for node in nodes.values():
        node.state_store.set_balance('treasury', 10000)
    
    leader = nodes['node0']
    proofs = [
        {'constraints': ['x > 0'], 'post_conditions': ['x > 0'], 'valid': True},
        {'constraints': ['y > 0'], 'post_conditions': ['y > 0'], 'valid': True},
    ]
    
    for proof in proofs:
        leader.proof_mempool.add_proof(proof)
    
    proof_block = leader.propose_block_from_mempool(block_size=2)
    assert proof_block is not None
    assert len(proof_block.proofs) == 2
    
    result = run_consensus_round(nodes, proof_block)
    
    assert result is not None
    assert result.consensus_reached == True
    assert result.finalized_state is not None
    assert result.total_difficulty > 0
    assert leader.proof_mempool.size() == 0


def test_ten_node_consensus_with_rewards():
    """Test consensus with 10 nodes and verify reward distribution."""
    nodes = create_test_network(10)
    
    for node in nodes.values():
        node.state_store.set_balance('treasury', 100000)
    
    leader = nodes['node0']
    proofs = [
        {'constraints': ['x > 0'] * 3, 'post_conditions': ['x > 0'], 'valid': True},
        {'constraints': ['y > 0'] * 5, 'post_conditions': ['y > 0'], 'valid': True},
    ]
    
    for proof in proofs:
        leader.proof_mempool.add_proof(proof)
    
    proof_block = leader.propose_block_from_mempool(block_size=2)
    result = run_consensus_round(nodes, proof_block)
    
    assert result.consensus_reached == True
    assert result.total_difficulty > 0
    
    from diotec360.consensus.reward_distributor import RewardDistributor
    reward_distributor = RewardDistributor(leader.state_store)
    rewards = reward_distributor.calculate_rewards(result)
    
    assert len(rewards) == len(result.participating_nodes)
    assert sum(rewards.values()) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
