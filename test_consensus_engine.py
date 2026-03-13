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
Unit Tests for ConsensusEngine

Tests consensus aggregation logic:
- Unanimous approval
- Single expert rejection
- Mixed confidence scenarios
- Uncertainty detection

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
from diotec360.moe.consensus_engine import ConsensusEngine
from diotec360.moe.data_models import ExpertVerdict, MOEResult


class TestConsensusEngine:
    """Test suite for ConsensusEngine."""
    
    def test_unanimous_approval_high_confidence(self):
        """Test unanimous approval with high confidence."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 100.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.90, 50.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.98, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "APPROVED"
        assert result.overall_confidence >= 0.7
        assert len(result.expert_verdicts) == 3
        assert result.total_latency_ms == 100.0  # Max of parallel execution
        assert set(result.activated_experts) == {"Z3_Expert", "Sentinel_Expert", "Guardian_Expert"}
    
    def test_single_expert_rejection_high_confidence(self):
        """Test single expert rejection with high confidence triggers REJECTED."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 100.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.99, 50.0, reason="Overflow detected"),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.98, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "REJECTED"
        assert result.overall_confidence == 0.99  # Uses rejecting expert's confidence
        assert len(result.expert_verdicts) == 3
    
    def test_all_reject_high_confidence(self):
        """Test all experts reject with high confidence."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "REJECT", 0.95, 100.0, reason="Logic error"),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.90, 50.0, reason="Security threat"),
            ExpertVerdict("Guardian_Expert", "REJECT", 0.98, 30.0, reason="Conservation violated")
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "REJECTED"
        assert result.overall_confidence >= 0.7
    
    def test_mixed_verdicts_uncertain(self):
        """Test mixed verdicts with moderate confidence results in UNCERTAIN."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.60, 100.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.55, 50.0, reason="Suspicious pattern"),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.65, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "UNCERTAIN"
        assert result.overall_confidence < 0.7
    
    def test_low_confidence_approval_uncertain(self):
        """Test all approve but with low confidence results in UNCERTAIN."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.50, 100.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.55, 50.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.60, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "UNCERTAIN"
        assert result.overall_confidence < 0.7
    
    def test_empty_verdicts(self):
        """Test handling of empty verdict list."""
        engine = ConsensusEngine()
        
        result = engine.aggregate([])
        
        assert result.consensus == "REJECTED"
        assert result.overall_confidence == 0.0
        assert len(result.expert_verdicts) == 0
        assert result.total_latency_ms == 0.0
    
    def test_single_expert_approve(self):
        """Test single expert approval with high confidence."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 100.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "APPROVED"
        assert result.overall_confidence == 0.95
    
    def test_single_expert_reject(self):
        """Test single expert rejection with high confidence."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "REJECT", 0.95, 100.0, reason="Invalid logic")
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.consensus == "REJECTED"
        assert result.overall_confidence == 0.95
    
    def test_latency_calculation(self):
        """Test that total latency is max of parallel execution."""
        engine = ConsensusEngine()
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 500.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.90, 100.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.98, 50.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert result.total_latency_ms == 500.0  # Max latency
    
    def test_custom_confidence_threshold(self):
        """Test custom confidence threshold."""
        engine = ConsensusEngine(confidence_threshold=0.9)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.85, 100.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.80, 50.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.82, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        # Average confidence is ~0.823, below 0.9 threshold
        assert result.consensus == "UNCERTAIN"
    
    def test_set_confidence_threshold(self):
        """Test updating confidence threshold."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        engine.set_confidence_threshold(0.8)
        
        assert engine.confidence_threshold == 0.8
    
    def test_set_confidence_threshold_invalid(self):
        """Test invalid confidence threshold raises error."""
        engine = ConsensusEngine()
        
        with pytest.raises(ValueError):
            engine.set_confidence_threshold(1.5)
        
        with pytest.raises(ValueError):
            engine.set_confidence_threshold(-0.1)
    
    def test_set_uncertainty_threshold(self):
        """Test updating uncertainty threshold."""
        engine = ConsensusEngine(uncertainty_threshold=0.5)
        
        engine.set_uncertainty_threshold(0.6)
        
        assert engine.uncertainty_threshold == 0.6
    
    def test_set_uncertainty_threshold_invalid(self):
        """Test invalid uncertainty threshold raises error."""
        engine = ConsensusEngine()
        
        with pytest.raises(ValueError):
            engine.set_uncertainty_threshold(1.5)
        
        with pytest.raises(ValueError):
            engine.set_uncertainty_threshold(-0.1)
    
    def test_get_config(self):
        """Test getting current configuration."""
        engine = ConsensusEngine(confidence_threshold=0.75, uncertainty_threshold=0.55)
        
        config = engine.get_config()
        
        assert config['confidence_threshold'] == 0.75
        assert config['uncertainty_threshold'] == 0.55
    
    def test_rejection_with_low_confidence_not_rejected(self):
        """Test rejection with low confidence doesn't trigger immediate REJECTED."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 100.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.40, 50.0, reason="Uncertain threat"),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.98, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        # Low confidence rejection doesn't trigger immediate REJECTED
        assert result.consensus == "UNCERTAIN"
    
    def test_activated_experts_list(self):
        """Test activated experts list is correctly populated."""
        engine = ConsensusEngine()
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.95, 100.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.98, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        assert len(result.activated_experts) == 2
        assert "Z3_Expert" in result.activated_experts
        assert "Guardian_Expert" in result.activated_experts
        assert "Sentinel_Expert" not in result.activated_experts
    
    def test_edge_case_exact_threshold(self):
        """Test edge case where confidence exactly equals threshold."""
        engine = ConsensusEngine(confidence_threshold=0.7)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.75, 100.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.70, 50.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 0.65, 30.0)
        ]
        
        result = engine.aggregate(verdicts)
        
        # Average is exactly 0.7, at threshold should be APPROVED
        assert result.consensus == "APPROVED"
        assert abs(result.overall_confidence - 0.7) < 0.001  # Allow for floating point precision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
