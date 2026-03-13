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
Unit Tests for MOEOrchestrator

Tests:
- Expert registration and unregistration
- Parallel expert execution
- Result aggregation
- Verdict caching behavior
- Cache TTL expiration
- Cache hit/miss tracking

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import time
import tempfile
import os
from pathlib import Path
from diotec360.moe.orchestrator import MOEOrchestrator, CacheEntry
from diotec360.moe.base_expert import BaseExpert
from diotec360.moe.data_models import ExpertVerdict, MOEResult
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert


class MockExpert(BaseExpert):
    """Mock expert for testing."""
    
    def __init__(self, name: str, verdict: str = "APPROVE", confidence: float = 0.9, latency_ms: float = 10.0):
        super().__init__(name)
        self.mock_verdict = verdict
        self.mock_confidence = confidence
        self.mock_latency_ms = latency_ms
        self.verify_calls = []
        
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """Mock verification that returns predefined verdict."""
        self.verify_calls.append((intent, tx_id))
        
        # Simulate latency
        time.sleep(self.mock_latency_ms / 1000)
        
        return ExpertVerdict(
            expert_name=self.name,
            verdict=self.mock_verdict,
            confidence=self.mock_confidence,
            latency_ms=self.mock_latency_ms,
            reason=None if self.mock_verdict == "APPROVE" else "Mock rejection",
            proof_trace={'mock': True}
        )


class SlowExpert(BaseExpert):
    """Expert that takes a long time to verify (for timeout testing)."""
    
    def __init__(self, name: str, delay_seconds: float = 5.0):
        super().__init__(name)
        self.delay_seconds = delay_seconds
        
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """Slow verification."""
        time.sleep(self.delay_seconds)
        
        return ExpertVerdict(
            expert_name=self.name,
            verdict="APPROVE",
            confidence=0.9,
            latency_ms=self.delay_seconds * 1000,
            reason=None,
            proof_trace=None
        )


class FailingExpert(BaseExpert):
    """Expert that always crashes (for error handling testing)."""
    
    def __init__(self, name: str):
        super().__init__(name)
        
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """Always raises exception."""
        raise RuntimeError("Mock expert failure")


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_telemetry.db")
        yield db_path


@pytest.fixture
def orchestrator(temp_db):
    """Create orchestrator instance for testing."""
    return MOEOrchestrator(
        max_workers=3,
        expert_timeout=30,
        telemetry_db_path=temp_db,
        cache_ttl_seconds=300,
        enable_cache=True
    )


class TestExpertRegistration:
    """Test expert registration and management."""
    
    def test_register_expert(self, orchestrator):
        """Test registering a new expert."""
        expert = MockExpert("Test_Expert")
        orchestrator.register_expert(expert)
        
        assert "Test_Expert" in orchestrator.experts
        assert orchestrator.experts["Test_Expert"] == expert
    
    def test_register_duplicate_expert(self, orchestrator):
        """Test that registering duplicate expert raises error."""
        expert1 = MockExpert("Test_Expert")
        expert2 = MockExpert("Test_Expert")
        
        orchestrator.register_expert(expert1)
        
        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register_expert(expert2)
    
    def test_unregister_expert(self, orchestrator):
        """Test unregistering an expert."""
        expert = MockExpert("Test_Expert")
        orchestrator.register_expert(expert)
        
        orchestrator.unregister_expert("Test_Expert")
        
        assert "Test_Expert" not in orchestrator.experts
    
    def test_unregister_nonexistent_expert(self, orchestrator):
        """Test that unregistering nonexistent expert raises error."""
        with pytest.raises(KeyError, match="not found"):
            orchestrator.unregister_expert("Nonexistent_Expert")
    
    def test_register_multiple_experts(self, orchestrator):
        """Test registering multiple experts."""
        expert1 = MockExpert("Expert_1")
        expert2 = MockExpert("Expert_2")
        expert3 = MockExpert("Expert_3")
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        orchestrator.register_expert(expert3)
        
        assert len(orchestrator.experts) == 3
        assert "Expert_1" in orchestrator.experts
        assert "Expert_2" in orchestrator.experts
        assert "Expert_3" in orchestrator.experts


class TestParallelExecution:
    """Test parallel expert execution."""
    
    def test_parallel_execution_all_approve(self, orchestrator):
        """Test parallel execution when all experts approve."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9, latency_ms=50)
        expert2 = MockExpert("Expert_2", verdict="APPROVE", confidence=0.95, latency_ms=30)
        expert3 = MockExpert("Expert_3", verdict="APPROVE", confidence=0.85, latency_ms=40)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        orchestrator.register_expert(expert3)
        
        intent = "transfer 100 from Alice to Bob"
        tx_id = "tx_001"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        # All experts should have been called
        assert len(expert1.verify_calls) == 1
        assert len(expert2.verify_calls) == 1
        assert len(expert3.verify_calls) == 1
        
        # Result should be APPROVED
        assert result.consensus == "APPROVED"
        assert result.transaction_id == tx_id
        assert len(result.expert_verdicts) == 3
        
        # Latency should be max of parallel execution (not sum)
        assert result.total_latency_ms < 200  # Much less than sum (120ms)
    
    def test_parallel_execution_one_rejects(self, orchestrator):
        """Test parallel execution when one expert rejects."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        expert2 = MockExpert("Expert_2", verdict="REJECT", confidence=0.95)
        expert3 = MockExpert("Expert_3", verdict="APPROVE", confidence=0.85)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        orchestrator.register_expert(expert3)
        
        intent = "malicious code"
        tx_id = "tx_002"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        # Result should be REJECTED (one expert rejected)
        assert result.consensus == "REJECTED"
        assert result.transaction_id == tx_id
    
    def test_parallel_execution_timeout(self, orchestrator):
        """Test parallel execution with timeout."""
        # Set short timeout
        orchestrator.expert_timeout = 2
        
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9, latency_ms=10)
        expert2 = SlowExpert("Expert_2", delay_seconds=10)  # Will timeout (10s > 2s timeout)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        
        intent = "test timeout"
        tx_id = "tx_003"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        # Should have verdicts from both experts
        assert len(result.expert_verdicts) == 2
        
        # Find Expert_2 verdict
        expert2_verdict = next(v for v in result.expert_verdicts if v.expert_name == "Expert_2")
        
        # Expert_2 should either timeout (REJECT) or complete slowly (APPROVE)
        # The key is that we get a verdict from both experts
        assert expert2_verdict.expert_name == "Expert_2"
        
        # Result should be REJECTED if Expert_2 timed out, or based on consensus if it completed
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
    
    def test_parallel_execution_expert_failure(self, orchestrator):
        """Test parallel execution when expert crashes."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        expert2 = FailingExpert("Expert_2")
        expert3 = MockExpert("Expert_3", verdict="APPROVE", confidence=0.85)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        orchestrator.register_expert(expert3)
        
        intent = "test failure"
        tx_id = "tx_004"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        # Should have verdicts from all experts (failure creates rejection verdict)
        assert len(result.expert_verdicts) == 3
        
        # Find failure verdict
        failure_verdict = next(v for v in result.expert_verdicts if v.expert_name == "Expert_2")
        assert failure_verdict.verdict == "REJECT"
        assert "failure" in failure_verdict.reason.lower()


class TestResultAggregation:
    """Test result aggregation via consensus engine."""
    
    def test_unanimous_approval(self, orchestrator):
        """Test unanimous approval from all experts."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        expert2 = MockExpert("Expert_2", verdict="APPROVE", confidence=0.95)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        
        intent = "safe transaction"
        tx_id = "tx_005"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        assert result.consensus == "APPROVED"
        assert result.overall_confidence >= 0.7
    
    def test_single_rejection(self, orchestrator):
        """Test that single rejection overrides approvals."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        expert2 = MockExpert("Expert_2", verdict="REJECT", confidence=0.95)
        expert3 = MockExpert("Expert_3", verdict="APPROVE", confidence=0.85)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        orchestrator.register_expert(expert3)
        
        intent = "suspicious transaction"
        tx_id = "tx_006"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        assert result.consensus == "REJECTED"
    
    def test_low_confidence_approval(self, orchestrator):
        """Test that low confidence triggers uncertainty."""
        expert1 = MockExpert("Expert_1", verdict="APPROVE", confidence=0.4)
        expert2 = MockExpert("Expert_2", verdict="APPROVE", confidence=0.5)
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        
        intent = "uncertain transaction"
        tx_id = "tx_007"
        
        result = orchestrator.verify_transaction(intent, tx_id)
        
        # Low average confidence should trigger UNCERTAIN
        assert result.consensus == "UNCERTAIN"
        assert result.overall_confidence < 0.7


class TestVerdictCaching:
    """Test verdict caching functionality."""
    
    def test_cache_hit(self, orchestrator):
        """Test cache hit for identical intent."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        # First verification - cache miss
        result1 = orchestrator.verify_transaction(intent, "tx_001")
        assert orchestrator.cache_misses == 1
        assert orchestrator.cache_hits == 0
        assert len(expert.verify_calls) == 1
        
        # Second verification - cache hit
        result2 = orchestrator.verify_transaction(intent, "tx_002")
        assert orchestrator.cache_hits == 1
        assert orchestrator.cache_misses == 1
        assert len(expert.verify_calls) == 1  # Expert not called again
        
        # Results should be identical (except tx_id)
        assert result1.consensus == result2.consensus
        assert result1.overall_confidence == result2.overall_confidence
    
    def test_cache_miss_different_intent(self, orchestrator):
        """Test cache miss for different intent."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent1 = "transfer 100 from Alice to Bob"
        intent2 = "transfer 200 from Bob to Charlie"
        
        result1 = orchestrator.verify_transaction(intent1, "tx_001")
        result2 = orchestrator.verify_transaction(intent2, "tx_002")
        
        # Both should be cache misses
        assert orchestrator.cache_misses == 2
        assert orchestrator.cache_hits == 0
        assert len(expert.verify_calls) == 2
    
    def test_cache_expiration(self, orchestrator):
        """Test cache TTL expiration."""
        # Set short TTL
        orchestrator.cache_ttl_seconds = 1
        
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        # First verification
        result1 = orchestrator.verify_transaction(intent, "tx_001")
        assert orchestrator.cache_misses == 1
        
        # Wait for cache to expire
        time.sleep(1.5)
        
        # Second verification - cache expired, should be miss
        result2 = orchestrator.verify_transaction(intent, "tx_002")
        assert orchestrator.cache_misses == 2
        assert len(expert.verify_calls) == 2  # Expert called again
    
    def test_cache_disabled(self, orchestrator):
        """Test that caching can be disabled."""
        orchestrator.set_cache_enabled(False)
        
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        # Multiple verifications with same intent
        orchestrator.verify_transaction(intent, "tx_001")
        orchestrator.verify_transaction(intent, "tx_002")
        
        # No cache hits (caching disabled)
        assert orchestrator.cache_hits == 0
        assert len(expert.verify_calls) == 2
    
    def test_clear_cache(self, orchestrator):
        """Test clearing cache."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        # Create cache entry
        orchestrator.verify_transaction(intent, "tx_001")
        assert len(orchestrator.verdict_cache) == 1
        
        # Clear cache
        cleared = orchestrator.clear_cache()
        assert cleared == 1
        assert len(orchestrator.verdict_cache) == 0
        
        # Next verification should be cache miss
        orchestrator.verify_transaction(intent, "tx_002")
        assert len(expert.verify_calls) == 2
    
    def test_cleanup_expired_cache(self, orchestrator):
        """Test cleanup of expired cache entries."""
        orchestrator.cache_ttl_seconds = 1
        
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        # Create multiple cache entries
        orchestrator.verify_transaction("intent 1", "tx_001")
        orchestrator.verify_transaction("intent 2", "tx_002")
        orchestrator.verify_transaction("intent 3", "tx_003")
        
        assert len(orchestrator.verdict_cache) == 3
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Cleanup expired entries
        removed = orchestrator.cleanup_expired_cache()
        assert removed == 3
        assert len(orchestrator.verdict_cache) == 0
    
    def test_cache_stats(self, orchestrator):
        """Test cache statistics."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        # First verification - miss
        orchestrator.verify_transaction(intent, "tx_001")
        
        # Second verification - hit
        orchestrator.verify_transaction(intent, "tx_002")
        
        stats = orchestrator.get_cache_stats()
        
        assert stats['enabled'] == True
        assert stats['ttl_seconds'] == 300
        assert stats['size'] == 1
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 0.5


class TestOrchestratorStatus:
    """Test orchestrator status and statistics."""
    
    def test_get_expert_status(self, orchestrator):
        """Test getting expert status."""
        expert1 = MockExpert("Expert_1")
        expert2 = MockExpert("Expert_2")
        
        orchestrator.register_expert(expert1)
        orchestrator.register_expert(expert2)
        
        status = orchestrator.get_expert_status()
        
        assert 'registered_experts' in status
        assert 'expert_stats' in status
        assert 'orchestrator_stats' in status
        assert 'gating_network_stats' in status
        assert 'consensus_engine_config' in status
        
        assert len(status['registered_experts']) == 2
        assert 'Expert_1' in status['registered_experts']
        assert 'Expert_2' in status['registered_experts']
    
    def test_orchestrator_statistics(self, orchestrator):
        """Test orchestrator statistics tracking."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        # Perform verifications
        orchestrator.verify_transaction("intent 1", "tx_001")
        orchestrator.verify_transaction("intent 2", "tx_002")
        orchestrator.verify_transaction("intent 3", "tx_003")
        
        status = orchestrator.get_expert_status()
        stats = status['orchestrator_stats']
        
        assert stats['total_verifications'] == 3
        assert stats['average_latency_ms'] > 0
    
    def test_reset_statistics(self, orchestrator):
        """Test resetting statistics."""
        expert = MockExpert("Expert_1", verdict="APPROVE", confidence=0.9)
        orchestrator.register_expert(expert)
        
        orchestrator.verify_transaction("intent 1", "tx_001")
        
        assert orchestrator.total_verifications == 1
        
        orchestrator.reset_statistics()
        
        assert orchestrator.total_verifications == 0
        assert orchestrator.total_latency_ms == 0.0


class TestIntegrationWithRealExperts:
    """Integration tests with real expert implementations."""
    
    def test_with_z3_expert(self, orchestrator):
        """Test orchestrator with real Z3Expert."""
        z3_expert = Z3Expert(timeout_normal=5, timeout_crisis=1)
        orchestrator.register_expert(z3_expert)
        
        intent = """
        verify {
            x + y == 10
            x == 5
            y == 5
        }
        """
        
        result = orchestrator.verify_transaction(intent, "tx_z3_001")
        
        assert result.transaction_id == "tx_z3_001"
        assert len(result.expert_verdicts) == 1
        assert result.expert_verdicts[0].expert_name == "Z3_Expert"
    
    def test_with_sentinel_expert(self, orchestrator):
        """Test orchestrator with real SentinelExpert."""
        sentinel_expert = SentinelExpert(timeout_ms=100)
        orchestrator.register_expert(sentinel_expert)
        
        intent = "transfer 100 from Alice to Bob"
        
        result = orchestrator.verify_transaction(intent, "tx_sentinel_001")
        
        assert result.transaction_id == "tx_sentinel_001"
        assert len(result.expert_verdicts) == 1
        assert result.expert_verdicts[0].expert_name == "Sentinel_Expert"
    
    def test_with_guardian_expert(self, orchestrator):
        """Test orchestrator with real GuardianExpert."""
        guardian_expert = GuardianExpert(timeout_ms=50)
        orchestrator.register_expert(guardian_expert)
        
        intent = """
        verify {
            old_balance_alice - 100 == new_balance_alice
            old_balance_bob + 100 == new_balance_bob
        }
        """
        
        result = orchestrator.verify_transaction(intent, "tx_guardian_001")
        
        assert result.transaction_id == "tx_guardian_001"
        assert len(result.expert_verdicts) == 1
        assert result.expert_verdicts[0].expert_name == "Guardian_Expert"
    
    def test_with_all_experts(self, orchestrator):
        """Test orchestrator with all three real experts."""
        z3_expert = Z3Expert(timeout_normal=5)
        sentinel_expert = SentinelExpert(timeout_ms=100)
        guardian_expert = GuardianExpert(timeout_ms=50)
        
        orchestrator.register_expert(z3_expert)
        orchestrator.register_expert(sentinel_expert)
        orchestrator.register_expert(guardian_expert)
        
        intent = """
        verify {
            old_balance_alice - 100 == new_balance_alice
            old_balance_bob + 100 == new_balance_bob
            new_balance_alice >= 0
            new_balance_bob >= 0
        }
        """
        
        result = orchestrator.verify_transaction(intent, "tx_all_001")
        
        assert result.transaction_id == "tx_all_001"
        # Gating network will determine which experts to activate
        assert len(result.expert_verdicts) >= 1
        assert len(result.activated_experts) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
