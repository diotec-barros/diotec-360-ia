"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

RVC3 - Armored Lattice Test Suite
Tests for v3.0.4 "The Armored Lattice" hardening

Tests:
- RVC3-001: Authenticated State (Signed Merkle Root)
- RVC3-002: Exponential Backoff (DoS Prevention)
- RVC3-003: Active Peer Sensing (Zombie Detection)
"""

import pytest
import asyncio
import time
import os
from unittest.mock import Mock, patch, AsyncMock
from api.main import (
    _get_p2p_peer_count,
    _force_state_reconciliation,
    _handle_reconciliation_failure,
    _reconciliation_backoff,
    _reconciliation_failures,
    lattice_state
)


class TestRVC3_001_AuthenticatedState:
    """
    RVC3-001: The Attack of the "False Reconciliation"
    
    Vulnerability: Malicious node sends fake state with valid Merkle Root
    Fix: Require ED25519 signature from trusted keys
    """
    
    @pytest.mark.asyncio
    async def test_state_endpoint_signs_merkle_root(self):
        """State endpoint should sign Merkle Root with node's private key"""
        # Setup: Mock persistence and environment
        with patch('api.main.persistence') as mock_persistence:
            mock_persistence.merkle_db.get_root.return_value = "test_root_123"
            mock_persistence.merkle_db.state = {"account1": 1000}
            
            # Set private key
            os.environ["DIOTEC360_NODE_PRIVKEY_HEX"] = "a" * 64
            
            # Call endpoint
            result = await lattice_state()
            
            # Verify signature is present
            assert result["success"] is True
            assert result["merkle_root"] == "test_root_123"
            assert "signature" in result
            assert result["signed"] is True
            assert "timestamp" in result
            
            print("[RVC3-001] ✓ State endpoint signs Merkle Root")
    
    @pytest.mark.asyncio
    async def test_reconciliation_rejects_untrusted_peer(self):
        """Reconciliation should reject state from untrusted peers"""
        import httpx
        from diotec360.core.crypto import DIOTEC360Crypt
        
        # Setup: Mock HTTP client and response
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "merkle_root": "malicious_root",
            "state": {"hacker": 999999},
            "state_size": 1,
            "signed": True,
            "signature": "fake_signature",
            "timestamp": int(time.time())
        }
        mock_client.get.return_value = mock_response
        
        # Set trusted keys (empty = reject all)
        os.environ["DIOTEC360_TRUSTED_STATE_PUBKEYS"] = "trusted_key_1,trusted_key_2"
        
        # Mock crypto verification to fail
        with patch.object(DIOTEC360Crypt, 'verify_signature', return_value=False):
            # Call reconciliation
            await _force_state_reconciliation(mock_client, "http://malicious-node", "malicious_root")
            
            # Verify rejection
            assert "http://malicious-node" in _reconciliation_failures
            print("[RVC3-001] ✓ Untrusted peer rejected")
    
    @pytest.mark.asyncio
    async def test_reconciliation_accepts_trusted_peer(self):
        """Reconciliation should accept state from trusted peers"""
        import httpx
        from diotec360.core.crypto import DIOTEC360Crypt
        
        # Clear previous failures
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # Setup: Mock HTTP client and response
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "merkle_root": "trusted_root",
            "state": {"account1": 1000},
            "state_size": 1,
            "signed": True,
            "signature": "valid_signature",
            "timestamp": int(time.time())
        }
        mock_client.get.return_value = mock_response
        
        # Set trusted keys
        os.environ["DIOTEC360_TRUSTED_STATE_PUBKEYS"] = "trusted_key_1"
        
        # Mock persistence
        with patch('api.main.persistence') as mock_persistence:
            mock_persistence.merkle_db.state = {}
            mock_persistence.merkle_db.get_root.return_value = "new_root_after_reconciliation"
            
            # Mock crypto verification to succeed
            with patch.object(DIOTEC360Crypt, 'verify_signature', return_value=True):
                # Call reconciliation
                await _force_state_reconciliation(mock_client, "http://trusted-node", "trusted_root")
                
                # Verify acceptance (no failures recorded)
                assert "http://trusted-node" not in _reconciliation_failures
                print("[RVC3-001] ✓ Trusted peer accepted")


class TestRVC3_002_ExponentialBackoff:
    """
    RVC3-002: Exhaustion by Healing Cycle (DoS)
    
    Vulnerability: Attacker sends divergent roots at high speed
    Fix: Exponential backoff after failed reconciliation
    """
    
    def test_backoff_increases_exponentially(self):
        """Backoff time should double with each failure"""
        peer_url = "http://attacker-node"
        
        # Clear state
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # First failure: 2^1 = 2 seconds
        _handle_reconciliation_failure(peer_url)
        assert _reconciliation_failures[peer_url] == 1
        backoff_1 = _reconciliation_backoff[peer_url] - time.time()
        assert 1.9 < backoff_1 < 2.1
        
        # Second failure: 2^2 = 4 seconds
        _handle_reconciliation_failure(peer_url)
        assert _reconciliation_failures[peer_url] == 2
        backoff_2 = _reconciliation_backoff[peer_url] - time.time()
        assert 3.9 < backoff_2 < 4.1
        
        # Third failure: 2^3 = 8 seconds
        _handle_reconciliation_failure(peer_url)
        assert _reconciliation_failures[peer_url] == 3
        backoff_3 = _reconciliation_backoff[peer_url] - time.time()
        assert 7.9 < backoff_3 < 8.1
        
        print("[RVC3-002] ✓ Exponential backoff working")
    
    def test_backoff_caps_at_5_minutes(self):
        """Backoff should cap at 300 seconds (5 minutes)"""
        peer_url = "http://persistent-attacker"
        
        # Clear state
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # Simulate 20 failures (2^20 = 1,048,576 seconds without cap)
        for i in range(20):
            _handle_reconciliation_failure(peer_url)
        
        # Verify cap
        backoff = _reconciliation_backoff[peer_url] - time.time()
        assert backoff <= 300
        print(f"[RVC3-002] ✓ Backoff capped at {backoff:.1f}s (max 300s)")
    
    @pytest.mark.asyncio
    async def test_reconciliation_blocked_during_backoff(self):
        """Reconciliation should be blocked during backoff period"""
        import httpx
        
        peer_url = "http://backoff-test-node"
        
        # Clear state
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # Set backoff (block for 10 seconds)
        _reconciliation_backoff[peer_url] = time.time() + 10
        
        # Setup mock client
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        # Try to reconcile (should be blocked)
        await _force_state_reconciliation(mock_client, peer_url, "test_root")
        
        # Verify no HTTP call was made
        mock_client.get.assert_not_called()
        print("[RVC3-002] ✓ Reconciliation blocked during backoff")


class TestRVC3_003_ActivePeerSensing:
    """
    RVC3-003: The Blind Spot of "Peer Count"
    
    Vulnerability: Attacker creates 1000 zombie nodes (connected but silent)
    Fix: Count only peers with recent signed heartbeats
    """
    
    def test_zombie_peers_not_counted(self):
        """Zombie peers (no recent heartbeat) should not be counted"""
        # Mock lattice_streams
        with patch('api.main.lattice_streams') as mock_streams:
            mock_streams.started = True
            
            # Mock get_peers to return 5 peers
            async def mock_get_peers():
                return ["peer1", "peer2", "peer3", "peer4", "peer5"]
            
            mock_streams.get_peers = mock_get_peers
            
            # Set heartbeats: only 2 peers are active (recent heartbeat)
            current_time = time.time()
            mock_streams._peer_heartbeats = {
                "peer1": current_time - 10,  # Active (10s ago)
                "peer2": current_time - 20,  # Active (20s ago)
                "peer3": current_time - 60,  # Zombie (60s ago)
                "peer4": current_time - 120, # Zombie (120s ago)
                "peer5": 0                   # Zombie (never)
            }
            
            # Count peers
            count = _get_p2p_peer_count()
            
            # Should only count 2 active peers
            assert count == 2
            print("[RVC3-003] ✓ Zombie peers filtered out (2 active / 5 total)")
    
    def test_all_active_peers_counted(self):
        """All peers with recent heartbeats should be counted"""
        with patch('api.main.lattice_streams') as mock_streams:
            mock_streams.started = True
            
            # Mock get_peers to return a simple list (not async)
            mock_streams.get_peers = AsyncMock(return_value=["peer1", "peer2", "peer3"])
            
            # All peers are active
            current_time = time.time()
            mock_streams._peer_heartbeats = {
                "peer1": current_time - 5,
                "peer2": current_time - 15,
                "peer3": current_time - 25
            }
            
            # Mock asyncio.get_event_loop to return a mock loop
            mock_loop = Mock()
            mock_loop.is_running.return_value = False
            
            with patch('api.main.asyncio.get_event_loop', return_value=mock_loop):
                # Mock asyncio.run to return the peer list directly
                with patch('api.main.asyncio.run', return_value=["peer1", "peer2", "peer3"]):
                    # Count peers
                    count = _get_p2p_peer_count()
                    
                    # Should count all 3
                    assert count == 3
                    print("[RVC3-003] ✓ All active peers counted")
    
    def test_no_peers_returns_zero(self):
        """No peers should return 0"""
        with patch('api.main.lattice_streams') as mock_streams:
            mock_streams.started = True
            
            # Mock get_peers to return empty list
            async def mock_get_peers():
                return []
            
            mock_streams.get_peers = mock_get_peers
            mock_streams._peer_heartbeats = {}
            
            # Count peers
            count = _get_p2p_peer_count()
            
            assert count == 0
            print("[RVC3-003] ✓ No peers returns 0")


class TestRVC3_IntegrationScenarios:
    """
    Integration tests for complete attack scenarios
    """
    
    @pytest.mark.asyncio
    async def test_byzantine_node_attack_blocked(self):
        """
        Scenario: Byzantine node tries to poison network with fake state
        Expected: Attack blocked by signature verification
        """
        import httpx
        from diotec360.core.crypto import DIOTEC360Crypt
        
        # Clear state
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # Setup: Byzantine node sends fake state
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "merkle_root": "byzantine_root",
            "state": {"attacker": 1000000},
            "state_size": 1,
            "signed": True,
            "signature": "forged_signature",
            "timestamp": int(time.time())
        }
        mock_client.get.return_value = mock_response
        
        # Set trusted keys
        os.environ["DIOTEC360_TRUSTED_STATE_PUBKEYS"] = "legitimate_key"
        
        # Mock crypto to reject signature
        with patch.object(DIOTEC360Crypt, 'verify_signature', return_value=False):
            # Attempt reconciliation
            await _force_state_reconciliation(mock_client, "http://byzantine-node", "byzantine_root")
            
            # Verify attack blocked
            assert "http://byzantine-node" in _reconciliation_failures
            print("[INTEGRATION] ✓ Byzantine attack blocked")
    
    @pytest.mark.asyncio
    async def test_dos_via_reconciliation_loop_prevented(self):
        """
        Scenario: Attacker floods with divergent roots to exhaust CPU
        Expected: Exponential backoff prevents infinite loop
        """
        import httpx
        
        peer_url = "http://dos-attacker"
        
        # Clear state
        _reconciliation_failures.clear()
        _reconciliation_backoff.clear()
        
        # Setup mock client (always fails)
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.get.return_value = mock_response
        
        # First attempt - should fail and set backoff
        await _force_state_reconciliation(mock_client, peer_url, "attack_root_0")
        
        # Verify first failure recorded
        assert peer_url in _reconciliation_backoff
        assert _reconciliation_failures[peer_url] == 1
        
        # Verify backoff time is set (2^1 = 2 seconds)
        backoff = _reconciliation_backoff[peer_url] - time.time()
        assert 1.9 < backoff < 2.1
        
        # Subsequent attempts should be blocked by backoff
        for i in range(1, 5):
            await _force_state_reconciliation(mock_client, peer_url, f"attack_root_{i}")
        
        # Verify failure count didn't increase (blocked by backoff)
        assert _reconciliation_failures[peer_url] == 1
        
        print(f"[INTEGRATION] ✓ DoS prevented - only 1 failure recorded, 4 attempts blocked")
    
    def test_eclipse_attack_via_zombies_detected(self):
        """
        Scenario: Attacker creates 1000 zombie nodes to isolate victim
        Expected: Zombie detection prevents false "has peers" signal
        """
        with patch('api.main.lattice_streams') as mock_streams:
            mock_streams.started = True
            
            # Mock 1000 zombie peers
            zombie_peers = [f"zombie_{i}" for i in range(1000)]
            
            async def mock_get_peers():
                return zombie_peers
            
            mock_streams.get_peers = mock_get_peers
            
            # All zombies (no recent heartbeats)
            mock_streams._peer_heartbeats = {peer: 0 for peer in zombie_peers}
            
            # Count peers
            count = _get_p2p_peer_count()
            
            # Should detect 0 active peers despite 1000 connections
            assert count == 0
            print("[INTEGRATION] ✓ Eclipse attack detected (0 active / 1000 zombies)")


def run_rvc3_test_suite():
    """Run complete RVC3 test suite"""
    print("\n" + "="*70)
    print("RVC3 - THE ARMORED LATTICE - Test Suite")
    print("="*70 + "\n")
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "="*70)
    print("RVC3 TEST SUITE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_rvc3_test_suite()
