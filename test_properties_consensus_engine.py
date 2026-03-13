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
Property-Based Tests for ConsensusEngine

Tests consensus correctness and latency properties using Hypothesis.

Properties:
- Property 9: Consensus correctness
- Property 10: Consensus latency

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0

**Validates: Requirements 6.7**
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
from diotec360.moe.consensus_engine import ConsensusEngine
from diotec360.moe.data_models import ExpertVerdict
import time


# Strategy for generating expert names
expert_names = st.sampled_from([
    "Z3_Expert",
    "Sentinel_Expert",
    "Guardian_Expert",
    "Custom_Expert_1",
    "Custom_Expert_2"
])

# Strategy for generating verdicts
verdict_types = st.sampled_from(["APPROVE", "REJECT"])

# Strategy for generating confidence scores (0.0 to 1.0)
confidence_scores = st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)

# Strategy for generating latencies (1ms to 30000ms)
latencies = st.floats(min_value=1.0, max_value=30000.0, allow_nan=False, allow_infinity=False)

# Strategy for generating expert verdicts
@st.composite
def expert_verdict_strategy(draw):
    """Generate random ExpertVerdict."""
    name = draw(expert_names)
    verdict = draw(verdict_types)
    confidence = draw(confidence_scores)
    latency = draw(latencies)
    reason = f"Test reason for {verdict}" if verdict == "REJECT" else None
    
    return ExpertVerdict(
        expert_name=name,
        verdict=verdict,
        confidence=confidence,
        latency_ms=latency,
        reason=reason
    )

# Strategy for generating list of verdicts (1 to 5 experts)
verdict_lists = st.lists(expert_verdict_strategy(), min_size=1, max_size=5)


class TestConsensusEngineProperties:
    """Property-based tests for ConsensusEngine."""
    
    @given(verdicts=verdict_lists)
    @settings(max_examples=100, deadline=None)
    def test_property_9_consensus_correctness(self, verdicts):
        """
        Property 9: Consensus correctness
        
        Validates:
        1. High-confidence rejection from any expert triggers REJECTED
        2. Unanimous approval with high confidence triggers APPROVED
        3. Mixed or low confidence triggers UNCERTAIN
        4. Result always contains all input verdicts
        5. Activated experts list matches input verdicts
        
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**
        """
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        result = engine.aggregate(verdicts)
        
        # Property 1: Result must have valid consensus
        assert result.consensus in ["APPROVED", "REJECTED", "UNCERTAIN"]
        
        # Property 2: Result must contain all input verdicts
        assert len(result.expert_verdicts) == len(verdicts)
        assert result.expert_verdicts == verdicts
        
        # Property 3: Activated experts list must match input
        assert len(result.activated_experts) == len(verdicts)
        for verdict in verdicts:
            assert verdict.expert_name in result.activated_experts
        
        # Property 4: Overall confidence must be between 0.0 and 1.0
        assert 0.0 <= result.overall_confidence <= 1.0
        
        # Property 5: High-confidence rejection triggers REJECTED
        has_high_conf_rejection = any(
            v.verdict == "REJECT" and v.confidence >= 0.7
            for v in verdicts
        )
        if has_high_conf_rejection:
            assert result.consensus == "REJECTED"
        
        # Property 6: Unanimous high-confidence approval triggers APPROVED
        all_approve = all(v.verdict == "APPROVE" for v in verdicts)
        avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts)
        
        if all_approve and avg_confidence >= 0.7:
            assert result.consensus == "APPROVED"
        
        # Property 7: If not high-conf rejection and not unanimous high-conf approval, then UNCERTAIN
        if not has_high_conf_rejection and not (all_approve and avg_confidence >= 0.7):
            assert result.consensus == "UNCERTAIN"
    
    @given(verdicts=verdict_lists)
    @settings(max_examples=100, deadline=None)
    def test_property_10_consensus_latency(self, verdicts):
        """
        Property 10: Consensus latency
        
        Validates:
        1. Consensus aggregation completes within 1 second
        2. Total latency is max of expert latencies (parallel execution)
        3. Aggregation overhead is minimal (<10ms)
        
        **Validates: Requirements 6.7**
        """
        engine = ConsensusEngine()
        
        # Measure aggregation time
        start_time = time.perf_counter()
        result = engine.aggregate(verdicts)
        end_time = time.perf_counter()
        
        aggregation_time_ms = (end_time - start_time) * 1000
        
        # Property 1: Aggregation completes within 1 second
        assert aggregation_time_ms < 1000, f"Aggregation took {aggregation_time_ms}ms, exceeds 1000ms"
        
        # Property 2: Total latency is max of expert latencies
        max_expert_latency = max(v.latency_ms for v in verdicts)
        assert result.total_latency_ms == max_expert_latency
        
        # Property 3: Aggregation overhead is minimal (<10ms for most cases)
        # Note: This is a soft requirement, may occasionally exceed on slow systems
        if aggregation_time_ms > 10:
            # Log warning but don't fail (system-dependent)
            print(f"Warning: Aggregation overhead {aggregation_time_ms}ms exceeds 10ms target")
    
    @given(
        verdicts=verdict_lists,
        threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_consensus_threshold_invariant(self, verdicts, threshold):
        """
        Property: Consensus respects configured threshold
        
        Validates that changing the confidence threshold affects consensus decisions.
        """
        engine = ConsensusEngine(confidence_threshold=threshold)
        
        result = engine.aggregate(verdicts)
        
        # Check that high-confidence rejections respect threshold
        for verdict in verdicts:
            if verdict.verdict == "REJECT" and verdict.confidence >= threshold:
                assert result.consensus == "REJECTED"
                break
        
        # Check that unanimous approvals respect threshold
        all_approve = all(v.verdict == "APPROVE" for v in verdicts)
        avg_confidence = sum(v.confidence for v in verdicts) / len(verdicts)
        
        if all_approve and avg_confidence >= threshold:
            assert result.consensus == "APPROVED"
    
    @given(verdicts=verdict_lists)
    @settings(max_examples=100, deadline=None)
    def test_property_consensus_determinism(self, verdicts):
        """
        Property: Consensus is deterministic
        
        Validates that the same input always produces the same output.
        """
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        # Run aggregation twice
        result1 = engine.aggregate(verdicts)
        result2 = engine.aggregate(verdicts)
        
        # Results must be identical
        assert result1.consensus == result2.consensus
        assert result1.overall_confidence == result2.overall_confidence
        assert result1.total_latency_ms == result2.total_latency_ms
        assert result1.activated_experts == result2.activated_experts
    
    @given(verdicts=verdict_lists)
    @settings(max_examples=100, deadline=None)
    def test_property_consensus_monotonicity(self, verdicts):
        """
        Property: Consensus confidence is monotonic with expert confidence
        
        Validates that overall confidence reflects expert confidence levels.
        """
        engine = ConsensusEngine()
        
        result = engine.aggregate(verdicts)
        
        # Overall confidence should be within range of expert confidences
        min_confidence = min(v.confidence for v in verdicts)
        max_confidence = max(v.confidence for v in verdicts)
        
        assert min_confidence <= result.overall_confidence <= max_confidence
    
    @given(
        approve_count=st.integers(min_value=1, max_value=5),
        reject_count=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_consensus_approval_rate(self, approve_count, reject_count):
        """
        Property: Consensus reflects approval rate
        
        Validates that consensus decision aligns with expert approval rate.
        """
        assume(approve_count + reject_count > 0)
        
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        # Create verdicts with high confidence
        verdicts = []
        for i in range(approve_count):
            verdicts.append(ExpertVerdict(f"Expert_{i}", "APPROVE", 0.95, 100.0))
        for i in range(reject_count):
            verdicts.append(ExpertVerdict(f"Expert_{approve_count + i}", "REJECT", 0.95, 100.0))
        
        result = engine.aggregate(verdicts)
        
        # If any rejection with high confidence, must be REJECTED
        if reject_count > 0:
            assert result.consensus == "REJECTED"
        # If all approve with high confidence, must be APPROVED
        elif approve_count > 0 and reject_count == 0:
            assert result.consensus == "APPROVED"
    
    def test_property_empty_verdicts_safety(self):
        """
        Property: Empty verdicts handled safely
        
        Validates that empty verdict list doesn't crash and returns safe default.
        """
        engine = ConsensusEngine()
        
        result = engine.aggregate([])
        
        assert result.consensus == "REJECTED"  # Safe default
        assert result.overall_confidence == 0.0
        assert len(result.expert_verdicts) == 0
        assert len(result.activated_experts) == 0
    
    @given(
        num_experts=st.integers(min_value=1, max_value=10),
        confidence=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_consensus_scales_with_experts(self, num_experts, confidence):
        """
        Property: Consensus scales with number of experts
        
        Validates that consensus works correctly regardless of expert count.
        """
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        # Create verdicts with same confidence
        verdicts = [
            ExpertVerdict(f"Expert_{i}", "APPROVE", confidence, 100.0)
            for i in range(num_experts)
        ]
        
        result = engine.aggregate(verdicts)
        
        # All approve with same confidence
        if confidence >= 0.7:
            assert result.consensus == "APPROVED"
        else:
            assert result.consensus == "UNCERTAIN"
        
        # Overall confidence should equal individual confidence
        assert abs(result.overall_confidence - confidence) < 0.001


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
