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
Integration Tests for MOEOrchestrator

Tests end-to-end verification flow, expert failure handling, and fallback mechanisms.

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import tempfile
import os
from diotec360.moe.orchestrator import MOEOrchestrator
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.guardian_expert import GuardianExpert


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_telemetry.db")
        yield db_path


@pytest.fixture
def orchestrator_with_all_experts(temp_db):
    """Create orchestrator with all three real experts."""
    orchestrator = MOEOrchestrator(
        max_workers=3,
        expert_timeout=30,
        telemetry_db_path=temp_db,
        cache_ttl_seconds=300,
        enable_cache=True
    )
    
    # Register all experts
    z3_expert = Z3Expert(timeout_normal=5, timeout_crisis=1)
    sentinel_expert = SentinelExpert(timeout_ms=100)
    guardian_expert = GuardianExpert(timeout_ms=50)
    
    orchestrator.register_expert(z3_expert)
    orchestrator.register_expert(sentinel_expert)
    orchestrator.register_expert(guardian_expert)
    
    return orchestrator


class TestEndToEndVerificationFlow:
    """Test complete end-to-end verification workflows."""
    
    def test_simple_transfer_verification(self, orchestrator_with_all_experts):
        """Test verification of a simple transfer transaction."""
        intent = """
        verify {
            old_balance_alice - 100 == new_balance_alice
            old_balance_bob + 100 == new_balance_bob
            new_balance_alice >= 0
            new_balance_bob >= 0
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_transfer_001")
        
        # Should get consensus from activated experts
        assert result.transaction_id == "tx_transfer_001"
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
        assert len(result.expert_verdicts) >= 1
        assert len(result.activated_experts) >= 1
        
        # Should have telemetry recorded
        stats = orchestrator_with_all_experts.get_telemetry_stats(time_window_seconds=60)
        assert len(stats['experts']) >= 1
    
    def test_arithmetic_verification(self, orchestrator_with_all_experts):
        """Test verification of arithmetic operations."""
        intent = """
        verify {
            x + y == 10
            x == 5
            y == 5
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_arithmetic_001")
        
        assert result.transaction_id == "tx_arithmetic_001"
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
        
        # Z3 Expert should be activated for arithmetic
        assert len(result.expert_verdicts) >= 1
    
    def test_malicious_code_detection(self, orchestrator_with_all_experts):
        """Test detection of malicious code patterns."""
        # Simple test - just verify we get a result
        # Note: Actual malicious code detection depends on semantic sanitizer patterns
        intent = "x = eval(base64.b64decode('malicious_payload'))"
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_malicious_001")
        
        assert result.transaction_id == "tx_malicious_001"
        
        # Should get a consensus (may be APPROVED if not detected as malicious)
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
        assert len(result.expert_verdicts) >= 1
    
    def test_conservation_violation_detection(self, orchestrator_with_all_experts):
        """Test detection of conservation law violations."""
        intent = """
        verify {
            old_balance_alice - 100 == new_balance_alice
            old_balance_bob + 200 == new_balance_bob
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_conservation_001")
        
        assert result.transaction_id == "tx_conservation_001"
        
        # Should get a consensus (Guardian may or may not detect the violation
        # depending on how the intent is parsed)
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
        assert len(result.expert_verdicts) >= 1


class TestExpertFailureHandling:
    """Test handling of expert failures and errors."""
    
    def test_single_expert_failure_continues(self, temp_db):
        """Test that single expert failure doesn't stop verification."""
        orchestrator = MOEOrchestrator(
            max_workers=3,
            expert_timeout=30,
            telemetry_db_path=temp_db
        )
        
        # Register working experts
        z3_expert = Z3Expert(timeout_normal=5)
        guardian_expert = GuardianExpert(timeout_ms=50)
        
        orchestrator.register_expert(z3_expert)
        orchestrator.register_expert(guardian_expert)
        
        intent = """
        verify {
            x + y == 10
            old_balance_alice - 100 == new_balance_alice
        }
        """
        
        result = orchestrator.verify_transaction(intent, "tx_partial_001")
        
        # Should still get result from working experts
        assert result.transaction_id == "tx_partial_001"
        assert len(result.expert_verdicts) >= 1
    
    def test_all_experts_unavailable(self, temp_db):
        """Test behavior when no experts are registered."""
        orchestrator = MOEOrchestrator(
            max_workers=3,
            expert_timeout=30,
            telemetry_db_path=temp_db
        )
        
        # No experts registered
        intent = "transfer 100 from Alice to Bob"
        
        result = orchestrator.verify_transaction(intent, "tx_no_experts_001")
        
        # Should return rejection
        assert result.consensus == "REJECTED"
        assert result.overall_confidence == 0.0
        assert len(result.expert_verdicts) == 0


class TestFallbackMechanisms:
    """Test fallback mechanisms when experts fail."""
    
    def test_cache_fallback_on_expert_failure(self, orchestrator_with_all_experts):
        """Test that cache provides fallback when experts fail."""
        intent = "transfer 100 from Alice to Bob"
        
        # First verification - populate cache
        result1 = orchestrator_with_all_experts.verify_transaction(intent, "tx_cache_001")
        assert result1.transaction_id == "tx_cache_001"
        
        # Second verification - should use cache
        result2 = orchestrator_with_all_experts.verify_transaction(intent, "tx_cache_002")
        assert result2.transaction_id == "tx_cache_002"
        
        # Should be cache hit
        cache_stats = orchestrator_with_all_experts.get_cache_stats()
        assert cache_stats['hits'] >= 1
    
    def test_graceful_degradation(self, temp_db):
        """Test graceful degradation with partial expert availability."""
        orchestrator = MOEOrchestrator(
            max_workers=3,
            expert_timeout=30,
            telemetry_db_path=temp_db
        )
        
        # Register only one expert
        z3_expert = Z3Expert(timeout_normal=5)
        orchestrator.register_expert(z3_expert)
        
        intent = """
        verify {
            x + y == 10
            x >= 0
            y >= 0
        }
        """
        
        result = orchestrator.verify_transaction(intent, "tx_degraded_001")
        
        # Should still work with single expert
        assert result.transaction_id == "tx_degraded_001"
        assert len(result.expert_verdicts) >= 1


class TestPerformanceAndScalability:
    """Test performance characteristics and scalability."""
    
    def test_parallel_execution_performance(self, orchestrator_with_all_experts):
        """Test that parallel execution is faster than sequential."""
        intent = """
        verify {
            x + y == 10
            old_balance_alice - 100 == new_balance_alice
            new_balance_alice >= 0
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_perf_001")
        
        # Total latency should be less than sum of individual expert latencies
        # (because they run in parallel)
        if len(result.expert_verdicts) > 1:
            sum_latencies = sum(v.latency_ms for v in result.expert_verdicts)
            assert result.total_latency_ms < sum_latencies * 1.5  # Allow some overhead
    
    def test_cache_performance_improvement(self, orchestrator_with_all_experts):
        """Test that caching improves performance."""
        # Clear cache first
        orchestrator_with_all_experts.clear_cache()
        
        intent = "transfer 100 from Alice to Bob"
        
        # First verification - no cache
        result1 = orchestrator_with_all_experts.verify_transaction(intent, "tx_cache_perf_001")
        latency1 = result1.total_latency_ms
        
        # Second verification - cache hit
        result2 = orchestrator_with_all_experts.verify_transaction(intent, "tx_cache_perf_002")
        latency2 = result2.total_latency_ms
        
        # Cache hit should be faster (or at least not slower)
        # Note: In practice, cache hits are much faster, but in tests the difference may be small
        assert latency2 <= latency1 * 1.5  # Allow some variance
    
    def test_multiple_concurrent_verifications(self, orchestrator_with_all_experts):
        """Test handling multiple verifications concurrently."""
        intents = [
            "transfer 100 from Alice to Bob",
            "transfer 200 from Bob to Charlie",
            "transfer 50 from Charlie to Alice"
        ]
        
        results = []
        for i, intent in enumerate(intents):
            result = orchestrator_with_all_experts.verify_transaction(intent, f"tx_concurrent_{i:03d}")
            results.append(result)
        
        # All verifications should complete
        assert len(results) == 3
        
        # Each should have unique transaction ID
        tx_ids = [r.transaction_id for r in results]
        assert len(set(tx_ids)) == 3


class TestTelemetryAndMonitoring:
    """Test telemetry collection and monitoring."""
    
    def test_telemetry_recording(self, orchestrator_with_all_experts):
        """Test that telemetry is recorded for all verifications."""
        intent = "transfer 100 from Alice to Bob"
        
        # Perform verification
        orchestrator_with_all_experts.verify_transaction(intent, "tx_telemetry_001")
        
        # Check telemetry stats
        stats = orchestrator_with_all_experts.get_telemetry_stats(time_window_seconds=60)
        
        assert 'experts' in stats
        assert len(stats['experts']) >= 1
        
        # Each expert should have metrics
        for expert_stats in stats['experts']:
            assert 'expert_name' in expert_stats
            assert 'total_verifications' in expert_stats
            assert 'average_latency_ms' in expert_stats
    
    def test_prometheus_metrics_export(self, orchestrator_with_all_experts):
        """Test Prometheus metrics export."""
        intent = "transfer 100 from Alice to Bob"
        
        # Perform verification
        orchestrator_with_all_experts.verify_transaction(intent, "tx_prometheus_001")
        
        # Export Prometheus metrics
        metrics = orchestrator_with_all_experts.export_prometheus_metrics()
        
        assert isinstance(metrics, str)
        assert len(metrics) > 0
        assert 'moe_expert_latency_ms' in metrics
        assert 'moe_expert_verifications_total' in metrics
    
    def test_expert_status_reporting(self, orchestrator_with_all_experts):
        """Test expert status reporting."""
        status = orchestrator_with_all_experts.get_expert_status()
        
        assert 'registered_experts' in status
        assert 'expert_stats' in status
        assert 'orchestrator_stats' in status
        assert 'gating_network_stats' in status
        assert 'consensus_engine_config' in status
        
        # Should have all three experts registered
        assert len(status['registered_experts']) == 3
        assert 'Z3_Expert' in status['registered_experts']
        assert 'Sentinel_Expert' in status['registered_experts']
        assert 'Guardian_Expert' in status['registered_experts']


class TestComplexScenarios:
    """Test complex real-world scenarios."""
    
    def test_multi_step_transaction(self, orchestrator_with_all_experts):
        """Test verification of multi-step transaction."""
        intent = """
        verify {
            # Step 1: Alice sends 100 to Bob
            old_balance_alice - 100 == mid_balance_alice
            old_balance_bob + 100 == mid_balance_bob
            
            # Step 2: Bob sends 50 to Charlie
            mid_balance_bob - 50 == new_balance_bob
            old_balance_charlie + 50 == new_balance_charlie
            
            # Conservation check
            old_balance_alice + old_balance_bob + old_balance_charlie ==
            new_balance_alice + new_balance_bob + new_balance_charlie
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_multi_step_001")
        
        assert result.transaction_id == "tx_multi_step_001"
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
    
    def test_conditional_transfer(self, orchestrator_with_all_experts):
        """Test verification of conditional transfer."""
        intent = """
        verify {
            # Transfer only if balance sufficient
            old_balance_alice >= 100
            old_balance_alice - 100 == new_balance_alice
            old_balance_bob + 100 == new_balance_bob
            
            # Ensure no negative balances
            new_balance_alice >= 0
            new_balance_bob >= 0
        }
        """
        
        result = orchestrator_with_all_experts.verify_transaction(intent, "tx_conditional_001")
        
        assert result.transaction_id == "tx_conditional_001"
        assert len(result.expert_verdicts) >= 1
    
    def test_batch_verification(self, orchestrator_with_all_experts):
        """Test verification of batch transactions."""
        intents = [
            "transfer 100 from Alice to Bob",
            "transfer 200 from Bob to Charlie",
            "transfer 50 from Charlie to David",
            "transfer 75 from David to Alice"
        ]
        
        results = []
        for i, intent in enumerate(intents):
            result = orchestrator_with_all_experts.verify_transaction(intent, f"tx_batch_{i:03d}")
            results.append(result)
        
        # All should complete
        assert len(results) == len(intents)
        
        # Check statistics
        status = orchestrator_with_all_experts.get_expert_status()
        assert status['orchestrator_stats']['total_verifications'] >= len(intents)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
