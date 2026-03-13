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
Test Suite for Sovereign Gossip Integration - RVC2-006
Validates integration between Gossip Protocol and Sovereign Identity System

Test Coverage:
1. Identity generation and persistence
2. Key pair storage and retrieval
3. Gossip protocol initialization with identity
4. Public key registry synchronization
5. Node identity verification
6. Cross-node identity validation
7. Integration with Sovereign Persistence
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from diotec360.lattice.sovereign_gossip_integration import (
    SovereignGossipIntegration,
    init_sovereign_gossip_integration
)
from diotec360.lattice.gossip import GossipConfig
from diotec360.core.sovereign_persistence import SovereignPersistence


class TestSovereignGossipIntegration:
    """Test suite for Sovereign Gossip Integration"""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        temp_dir = tempfile.mkdtemp()
        identity_path = Path(temp_dir) / "identity"
        state_path = Path(temp_dir) / "state"
        vault_path = Path(temp_dir) / "vault"
        audit_path = Path(temp_dir) / "audit"
        
        yield {
            'temp_dir': temp_dir,
            'identity_path': str(identity_path),
            'state_path': str(state_path),
            'vault_path': str(vault_path),
            'audit_path': str(audit_path)
        }
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_peers(self):
        """Mock peer list function"""
        return lambda: []
    
    def test_identity_generation(self, temp_dirs, mock_peers):
        """Test 1: Identity generation for new node"""
        integration = SovereignGossipIntegration(
            node_id="node_alpha",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Verify identity was generated
        assert integration.keypair is not None
        assert integration.private_key is not None
        assert len(integration.keypair.public_key_hex) == 64  # 32 bytes = 64 hex chars
        
        # Verify identity file was created
        identity_file = Path(temp_dirs['identity_path']) / "node_alpha_identity.json"
        assert identity_file.exists()
        
        print(f"✅ Test 1 PASSED: Identity generated for node_alpha")
        print(f"   Public Key: {integration.keypair.public_key_hex[:32]}...")
    
    def test_identity_persistence(self, temp_dirs, mock_peers):
        """Test 2: Identity persists across restarts"""
        # Create first instance
        integration1 = SovereignGossipIntegration(
            node_id="node_beta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        public_key1 = integration1.keypair.public_key_hex
        
        # Create second instance (simulates restart)
        integration2 = SovereignGossipIntegration(
            node_id="node_beta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        public_key2 = integration2.keypair.public_key_hex
        
        # Verify same identity was loaded
        assert public_key1 == public_key2
        
        print(f"✅ Test 2 PASSED: Identity persisted across restarts")
        print(f"   Public Key: {public_key1[:32]}...")
    
    def test_public_key_storage_in_persistence(self, temp_dirs, mock_peers):
        """Test 3: Public key stored in Sovereign Persistence"""
        integration = SovereignGossipIntegration(
            node_id="node_gamma",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Verify public key was stored in persistence
        stored_identity = integration.persistence.get_state("node_identity:node_gamma")
        
        assert stored_identity is not None
        assert stored_identity['node_id'] == "node_gamma"
        assert stored_identity['public_key'] == integration.keypair.public_key_hex
        assert stored_identity['algorithm'] == 'ED25519'
        
        print(f"✅ Test 3 PASSED: Public key stored in persistence")
        print(f"   Node ID: {stored_identity['node_id']}")
        print(f"   Public Key: {stored_identity['public_key'][:32]}...")
    
    def test_gossip_protocol_initialization(self, temp_dirs, mock_peers):
        """Test 4: Gossip protocol initialized with identity"""
        integration = SovereignGossipIntegration(
            node_id="node_delta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Initialize gossip protocol
        gossip = integration.initialize_gossip_protocol()
        
        # Verify gossip protocol has identity
        assert gossip is not None
        assert gossip.node_id == "node_delta"
        assert gossip.private_key is not None
        assert gossip.public_key_hex == integration.keypair.public_key_hex
        
        print(f"✅ Test 4 PASSED: Gossip protocol initialized with identity")
        print(f"   Node ID: {gossip.node_id}")
        print(f"   Public Key: {gossip.public_key_hex[:32]}...")
    
    def test_node_identity_registration(self, temp_dirs, mock_peers):
        """Test 5: Register external node identity"""
        integration = SovereignGossipIntegration(
            node_id="node_epsilon",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Initialize gossip
        gossip = integration.initialize_gossip_protocol()
        
        # Register external node
        external_node_id = "node_external"
        external_public_key = "a" * 64  # Mock public key
        
        integration.register_node_identity(external_node_id, external_public_key)
        
        # Verify registration in persistence
        stored_identity = integration.persistence.get_state(f"node_identity:{external_node_id}")
        assert stored_identity is not None
        assert stored_identity['public_key'] == external_public_key
        
        # Verify registration in gossip protocol
        assert external_node_id in gossip.known_nodes
        assert gossip.known_nodes[external_node_id] == external_public_key
        
        print(f"✅ Test 5 PASSED: External node identity registered")
        print(f"   Node ID: {external_node_id}")
        print(f"   Public Key: {external_public_key[:32]}...")
    
    def test_node_identity_verification(self, temp_dirs, mock_peers):
        """Test 6: Verify node identity matches stored key"""
        integration = SovereignGossipIntegration(
            node_id="node_zeta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Register a node
        node_id = "node_trusted"
        public_key = "b" * 64
        integration.register_node_identity(node_id, public_key)
        
        # Verify correct public key
        assert integration.verify_node_identity(node_id, public_key) is True
        
        # Verify incorrect public key
        wrong_key = "c" * 64
        assert integration.verify_node_identity(node_id, wrong_key) is False
        
        # Verify unknown node
        assert integration.verify_node_identity("node_unknown", public_key) is False
        
        print(f"✅ Test 6 PASSED: Node identity verification working")
    
    def test_network_identity_registry(self, temp_dirs, mock_peers):
        """Test 7: Get complete network identity registry"""
        integration = SovereignGossipIntegration(
            node_id="node_eta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Register multiple nodes
        nodes = {
            "node_1": "1" * 64,
            "node_2": "2" * 64,
            "node_3": "3" * 64
        }
        
        for node_id, public_key in nodes.items():
            integration.register_node_identity(node_id, public_key)
        
        # Get registry
        registry = integration.get_network_identity_registry()
        
        # Verify all nodes are in registry
        for node_id, public_key in nodes.items():
            assert node_id in registry
            assert registry[node_id] == public_key
        
        # Verify our own node is in registry
        assert "node_eta" in registry
        assert registry["node_eta"] == integration.keypair.public_key_hex
        
        print(f"✅ Test 7 PASSED: Network identity registry complete")
        print(f"   Total Nodes: {len(registry)}")
    
    def test_cross_node_identity_sharing(self, temp_dirs, mock_peers):
        """Test 8: Identity sharing between nodes via persistence"""
        # Create two nodes sharing same persistence
        integration1 = SovereignGossipIntegration(
            node_id="node_theta",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        integration2 = SovereignGossipIntegration(
            node_id="node_iota",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Node 1 should see Node 2's public key
        node2_key = integration2.get_node_public_key("node_iota")
        assert node2_key == integration2.keypair.public_key_hex
        
        # Node 2 should see Node 1's public key
        node1_key = integration1.get_node_public_key("node_theta")
        assert node1_key == integration1.keypair.public_key_hex
        
        print(f"✅ Test 8 PASSED: Cross-node identity sharing working")
        print(f"   Node 1: {integration1.node_id}")
        print(f"   Node 2: {integration2.node_id}")
    
    @pytest.mark.asyncio
    async def test_signed_message_broadcast(self, temp_dirs, mock_peers):
        """Test 9: Broadcast signed message with identity"""
        integration = SovereignGossipIntegration(
            node_id="node_kappa",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Initialize gossip
        gossip = integration.initialize_gossip_protocol()
        
        # Broadcast message
        message_id = integration.broadcast(
            message_type="test_message",
            payload={"data": "test"}
        )
        
        # Verify message was signed
        message = gossip.get_message(message_id)
        assert message is not None
        assert message.signature is not None
        assert message.public_key == integration.keypair.public_key_hex
        
        print(f"✅ Test 9 PASSED: Signed message broadcast")
        print(f"   Message ID: {message_id[:16]}...")
        print(f"   Signature: {message.signature[:32]}...")
    
    def test_identity_info(self, temp_dirs, mock_peers):
        """Test 10: Get identity information"""
        integration = SovereignGossipIntegration(
            node_id="node_lambda",
            identity_path=temp_dirs['identity_path'],
            get_peers_func=mock_peers
        )
        
        # Initialize gossip
        integration.initialize_gossip_protocol()
        
        # Get identity info
        info = integration.get_identity_info()
        
        assert info['node_id'] == "node_lambda"
        assert info['public_key'] == integration.keypair.public_key_hex
        assert info['algorithm'] == 'ED25519'
        assert 'address' in info
        assert 'identity_path' in info
        assert info['known_nodes'] >= 0
        
        print(f"✅ Test 10 PASSED: Identity info retrieved")
        print(f"   Node ID: {info['node_id']}")
        print(f"   Address: {info['address']}")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*70)
    print("SOVEREIGN GOSSIP INTEGRATION - TEST SUITE")
    print("RVC2-006: Integration with Sovereign Identity System")
    print("="*70 + "\n")
    
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_all_tests()
