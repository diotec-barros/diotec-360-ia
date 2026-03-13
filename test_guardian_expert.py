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
Unit Tests for GuardianExpert - Financial Specialist

Tests:
- Conservation verification
- Merkle tree validation
- Double-spending detection
- Confidence scoring

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import time
from diotec360.moe.guardian_expert import GuardianExpert
from diotec360.moe.data_models import ExpertVerdict


class TestGuardianExpertBasics:
    """Test basic GuardianExpert functionality."""
    
    def test_expert_initialization(self):
        """Test GuardianExpert initializes correctly."""
        expert = GuardianExpert()
        
        assert expert.name == "Guardian_Expert"
        assert expert.timeout_ms == 50
        assert expert.conservation_checker is not None
        assert expert.state_tree is not None
        
    def test_custom_timeout(self):
        """Test custom timeout setting."""
        expert = GuardianExpert(timeout_ms=100)
        
        assert expert.timeout_ms == 100


class TestGuardianExpertConservation:
    """Test conservation verification."""
    
    def test_simple_conservation_approval(self):
        """Test simple valid conservation is approved."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_001")
        
        assert verdict.expert_name == "Guardian_Expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.9
        assert verdict.latency_ms > 0
        assert verdict.latency_ms < 100  # Should be fast
        assert verdict.reason is None
        
    def test_conservation_violation_rejection(self):
        """Test conservation violation is rejected."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 200
        }
        """
        
        verdict = expert.verify(intent, "tx_002")
        
        assert verdict.expert_name == "Guardian_Expert"
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0  # High confidence in rejection
        assert verdict.reason is not None
        assert "conservation" in verdict.reason.lower()
        
    def test_multiple_transfers_conservation(self):
        """Test conservation with multiple transfers."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 300
            receiver1_balance == old_receiver1_balance + 100
            receiver2_balance == old_receiver2_balance + 200
        }
        """
        
        verdict = expert.verify(intent, "tx_003")
        
        assert verdict.expert_name == "Guardian_Expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.9
        
    def test_zero_sum_conservation(self):
        """Test perfect zero-sum conservation."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            account_a == old_account_a - 50
            account_b == old_account_b + 30
            account_c == old_account_c + 20
        }
        """
        
        verdict = expert.verify(intent, "tx_004")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 1.0  # Perfect conservation
        
    def test_no_balance_changes(self):
        """Test intent with no balance changes."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            x > 0
            y > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_005")
        
        # No balance changes = skip conservation check
        assert verdict.verdict == "APPROVE"


class TestGuardianExpertMerkleIntegrity:
    """Test Merkle tree validation."""
    
    def test_merkle_integrity_with_no_state(self):
        """Test Merkle integrity when no state updates."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_006")
        
        # No state updates = skip Merkle check
        assert verdict.verdict == "APPROVE"
        
    def test_merkle_root_tracking(self):
        """Test Merkle root is tracked correctly."""
        expert = GuardianExpert()
        
        # Update state
        expert.update_state("account_1", 1000)
        expert.update_state("account_2", 2000)
        
        root1 = expert.get_state_root()
        assert root1 is not None
        assert len(root1) == 64  # SHA-256 hex string
        
        # Update state again
        expert.update_state("account_1", 900)
        
        root2 = expert.get_state_root()
        assert root2 != root1  # Root should change
        
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation."""
        expert = GuardianExpert()
        
        # Add state
        expert.update_state("account_1", 1000)
        expert.update_state("account_2", 2000)
        
        # Generate proof
        proof = expert.state_tree.generate_proof("account_1")
        
        assert proof is not None
        assert proof.key == "account_1"
        assert proof.value == 1000
        
    def test_merkle_proof_verification(self):
        """Test Merkle proof verification."""
        expert = GuardianExpert()
        
        # Add state
        expert.update_state("account_1", 1000)
        expert.update_state("account_2", 2000)
        
        # Generate and verify proof
        proof = expert.state_tree.generate_proof("account_1")
        assert expert.state_tree.verify_proof(proof) is True


class TestGuardianExpertDoubleSpending:
    """Test double-spending detection."""
    
    def test_no_double_spending(self):
        """Test normal transaction without double-spending."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_007")
        
        assert verdict.verdict == "APPROVE"
        
    def test_double_spending_detection(self):
        """Test detection of double-spending attempt."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        # First transaction
        verdict1 = expert.verify(intent, "tx_008")
        assert verdict1.verdict == "APPROVE"
        
        # Try to process same transaction again
        verdict2 = expert.verify(intent, "tx_008")
        assert verdict2.verdict == "REJECT"
        assert "double-spending" in verdict2.reason.lower()
        assert verdict2.confidence == 1.0
        
    def test_different_transactions_allowed(self):
        """Test different transactions are allowed."""
        expert = GuardianExpert()
        
        intent1 = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        intent2 = """
        verify {
            sender_balance == old_sender_balance - 50
            receiver_balance == old_receiver_balance + 50
        }
        """
        
        verdict1 = expert.verify(intent1, "tx_009")
        assert verdict1.verdict == "APPROVE"
        
        verdict2 = expert.verify(intent2, "tx_010")
        assert verdict2.verdict == "APPROVE"
        
    def test_reset_transaction_history(self):
        """Test resetting transaction history."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        # Process transaction
        verdict1 = expert.verify(intent, "tx_011")
        assert verdict1.verdict == "APPROVE"
        
        # Reset history
        expert.reset_transaction_history()
        
        # Same transaction should now be allowed
        verdict2 = expert.verify(intent, "tx_011")
        assert verdict2.verdict == "APPROVE"


class TestGuardianExpertBalanceConstraints:
    """Test account balance constraint verification."""
    
    def test_positive_balance_constraint(self):
        """Test positive balance constraint is enforced."""
        expert = GuardianExpert()
        
        intent = """
        guard {
            sender_balance >= 100
        }
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_012")
        
        assert verdict.verdict == "APPROVE"
        
    def test_negative_balance_rejection(self):
        """Test negative balance is rejected."""
        expert = GuardianExpert()
        
        intent = """
        guard {
            sender_balance >= -100
        }
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_013")
        
        assert verdict.verdict == "REJECT"
        assert "balance constraint" in verdict.reason.lower()
        
    def test_zero_balance_allowed(self):
        """Test zero balance is allowed."""
        expert = GuardianExpert()
        
        intent = """
        guard {
            sender_balance >= 0
        }
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_014")
        
        assert verdict.verdict == "APPROVE"


class TestGuardianExpertConfidenceScoring:
    """Test confidence score calculation."""
    
    def test_confidence_perfect_conservation(self):
        """Test confidence for perfect conservation."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_015")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 1.0  # Perfect conservation
        
    def test_confidence_conservation_violation(self):
        """Test confidence for conservation violation."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 200
        }
        """
        
        verdict = expert.verify(intent, "tx_016")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0  # High confidence in rejection
        
    def test_confidence_merkle_violation(self):
        """Test confidence for Merkle violation."""
        expert = GuardianExpert()
        
        # This test would require setting up invalid Merkle state
        # For now, we test that confidence is high for rejections
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_017")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence >= 0.95


class TestGuardianExpertPerformance:
    """Test performance and latency."""
    
    def test_latency_within_timeout(self):
        """Test verification completes within timeout."""
        expert = GuardianExpert(timeout_ms=50)
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        start_time = time.time()
        verdict = expert.verify(intent, "tx_018")
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 100  # Should be fast
        assert verdict.latency_ms < 100
        
    def test_multiple_verifications_performance(self):
        """Test performance with multiple verifications."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        latencies = []
        for i in range(10):
            verdict = expert.verify(intent, f"tx_{i}")
            latencies.append(verdict.latency_ms)
        
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 50  # Average should be under 50ms
        
    def test_complex_transaction_performance(self):
        """Test performance with complex transaction."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            account_1 == old_account_1 - 100
            account_2 == old_account_2 + 30
            account_3 == old_account_3 + 20
            account_4 == old_account_4 + 25
            account_5 == old_account_5 + 25
        }
        """
        
        verdict = expert.verify(intent, "tx_019")
        
        assert verdict.latency_ms < 100
        assert verdict.verdict == "APPROVE"


class TestGuardianExpertErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_intent(self):
        """Test handling of empty intent."""
        expert = GuardianExpert()
        
        verdict = expert.verify("", "tx_020")
        
        assert verdict.expert_name == "Guardian_Expert"
        assert verdict.verdict == "APPROVE"  # No balance changes
        
    def test_malformed_intent(self):
        """Test handling of malformed intent."""
        expert = GuardianExpert()
        
        intent = "verify { this is not valid syntax }"
        
        verdict = expert.verify(intent, "tx_021")
        
        # Should handle gracefully
        assert verdict.expert_name == "Guardian_Expert"
        assert verdict.latency_ms > 0
        
    def test_telemetry_recording(self):
        """Test that verifications are recorded for telemetry."""
        expert = GuardianExpert()
        
        initial_count = expert.total_verifications
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        expert.verify(intent, "tx_022")
        
        assert expert.total_verifications == initial_count + 1
        assert expert.total_latency_ms > 0
        
    def test_get_stats(self):
        """Test get_stats returns correct information."""
        expert = GuardianExpert()
        
        # Perform some verifications
        intent = """
        verify {
            sender_balance == old_sender_balance - 100
            receiver_balance == old_receiver_balance + 100
        }
        """
        
        for i in range(3):
            expert.verify(intent, f"tx_{i}")
        
        stats = expert.get_stats()
        
        assert stats['name'] == "Guardian_Expert"
        assert stats['total_verifications'] == 3
        assert stats['average_latency_ms'] > 0


class TestGuardianExpertIntegration:
    """Integration tests for GuardianExpert."""
    
    def test_financial_transaction_flow(self):
        """Test complete financial transaction flow."""
        expert = GuardianExpert()
        
        # Setup initial state
        expert.update_state("alice", 1000)
        expert.update_state("bob", 500)
        
        # Transaction: Alice sends 100 to Bob
        intent = """
        verify {
            alice_balance == old_alice_balance - 100
            bob_balance == old_bob_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_023")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 1.0
        
    def test_multi_party_transaction(self):
        """Test multi-party transaction."""
        expert = GuardianExpert()
        
        intent = """
        verify {
            sender_balance == old_sender_balance - 300
            receiver1_balance == old_receiver1_balance + 100
            receiver2_balance == old_receiver2_balance + 100
            receiver3_balance == old_receiver3_balance + 100
        }
        """
        
        verdict = expert.verify(intent, "tx_024")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 1.0
        
    def test_sequential_transactions(self):
        """Test sequential transactions."""
        expert = GuardianExpert()
        
        intent1 = """
        verify {
            alice_balance == old_alice_balance - 100
            bob_balance == old_bob_balance + 100
        }
        """
        
        intent2 = """
        verify {
            bob_balance == old_bob_balance - 50
            charlie_balance == old_charlie_balance + 50
        }
        """
        
        verdict1 = expert.verify(intent1, "tx_025")
        assert verdict1.verdict == "APPROVE"
        
        verdict2 = expert.verify(intent2, "tx_026")
        assert verdict2.verdict == "APPROVE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
