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
Unit Tests for Z3Expert - Mathematical Logic Specialist

Tests:
- Arithmetic verification
- Logical contradiction detection
- Confidence scoring
- Timeout behavior

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import time
from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.data_models import ExpertVerdict


class TestZ3ExpertBasics:
    """Test basic Z3Expert functionality."""
    
    def test_expert_initialization(self):
        """Test Z3Expert initializes correctly."""
        expert = Z3Expert()
        
        assert expert.name == "Z3_Expert"
        assert expert.timeout_normal == 30
        assert expert.timeout_crisis == 5
        assert expert.current_timeout == 30
        assert expert.crisis_mode is False
        
    def test_crisis_mode_toggle(self):
        """Test crisis mode changes timeout."""
        expert = Z3Expert()
        
        # Enable crisis mode
        expert.set_crisis_mode(True)
        assert expert.crisis_mode is True
        assert expert.current_timeout == 5
        
        # Disable crisis mode
        expert.set_crisis_mode(False)
        assert expert.crisis_mode is False
        assert expert.current_timeout == 30


class TestZ3ExpertArithmetic:
    """Test arithmetic verification."""
    
    def test_simple_arithmetic_approval(self):
        """Test simple valid arithmetic is approved."""
        expert = Z3Expert()
        
        intent = """
        guard {
            x > 0
            y > 0
        }
        verify {
            x + y > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_001")
        
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5
        assert verdict.latency_ms > 0
        assert verdict.reason is None
        
    def test_arithmetic_contradiction_rejection(self):
        """Test arithmetic contradiction is rejected."""
        expert = Z3Expert()
        
        intent = """
        guard {
            x == 5
        }
        verify {
            x == 10
        }
        """
        
        verdict = expert.verify(intent, "tx_002")
        
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0  # High confidence in rejection
        assert verdict.reason is not None
        assert "contradiction" in verdict.reason.lower()
        
    def test_complex_arithmetic(self):
        """Test complex arithmetic expressions."""
        expert = Z3Expert()
        
        intent = """
        guard {
            a > 0
            b > 0
        }
        verify {
            a + b > a
            a * b > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_003")
        
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5
        
    def test_overflow_detection(self):
        """Test detection of potential overflow."""
        expert = Z3Expert()
        
        # This should be approved by Z3 (mathematically valid)
        # but overflow detection would be handled by Sentinel Expert
        intent = """
        guard {
            x > 1000000000
            y > 1000000000
        }
        verify {
            x + y > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_004")
        
        # Z3 should approve this (mathematically valid)
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.verdict == "APPROVE"


class TestZ3ExpertLogicalContradictions:
    """Test logical contradiction detection."""
    
    def test_simple_contradiction(self):
        """Test simple logical contradiction."""
        expert = Z3Expert()
        
        intent = """
        verify {
            x > 10
            x < 5
        }
        """
        
        verdict = expert.verify(intent, "tx_005")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0
        assert "contradiction" in verdict.reason.lower()
        
    def test_complex_contradiction(self):
        """Test complex logical contradiction."""
        expert = Z3Expert()
        
        intent = """
        guard {
            a > 0
            b > 0
        }
        verify {
            a + b == 10
            a + b == 20
        }
        """
        
        verdict = expert.verify(intent, "tx_006")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0
        
    def test_no_contradiction(self):
        """Test valid logic without contradiction."""
        expert = Z3Expert()
        
        intent = """
        guard {
            x > 0
            y > 0
        }
        verify {
            x + y > 0
            x * y > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_007")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5


class TestZ3ExpertConfidenceScoring:
    """Test confidence score calculation."""
    
    def test_confidence_simple_proof(self):
        """Test confidence for simple proof."""
        expert = Z3Expert()
        
        # Simple proof with 1 constraint
        intent = """
        verify {
            x > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_008")
        
        assert verdict.verdict == "APPROVE"
        # Simple proofs should have high confidence
        assert verdict.confidence > 0.9
        
    def test_confidence_complex_proof(self):
        """Test confidence for complex proof."""
        expert = Z3Expert()
        
        # Complex proof with many constraints
        intent = """
        verify {
            a > 0
            b > 0
            c > 0
            a + b > c
            b + c > a
            c + a > b
            a + b + c > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_009")
        
        assert verdict.verdict == "APPROVE"
        # Complex proofs should have lower confidence
        assert verdict.confidence < 1.0
        
    def test_confidence_rejection(self):
        """Test confidence for rejection."""
        expert = Z3Expert()
        
        intent = """
        verify {
            x == 5
            x == 10
        }
        """
        
        verdict = expert.verify(intent, "tx_010")
        
        assert verdict.verdict == "REJECT"
        # Rejections should have high confidence
        assert verdict.confidence == 1.0
        
    def test_confidence_no_constraints(self):
        """Test confidence when no constraints found."""
        expert = Z3Expert()
        
        intent = "some random text without constraints"
        
        verdict = expert.verify(intent, "tx_011")
        
        assert verdict.verdict == "APPROVE"
        # No constraints = low confidence
        assert verdict.confidence == 0.5


class TestZ3ExpertTimeoutBehavior:
    """Test timeout handling."""
    
    def test_normal_timeout_setting(self):
        """Test normal timeout is set correctly."""
        expert = Z3Expert(timeout_normal=10, timeout_crisis=2)
        
        assert expert.timeout_normal == 10
        assert expert.timeout_crisis == 2
        assert expert.current_timeout == 10
        
    def test_crisis_timeout_setting(self):
        """Test crisis timeout is set correctly."""
        expert = Z3Expert(timeout_normal=10, timeout_crisis=2)
        expert.set_crisis_mode(True)
        
        assert expert.current_timeout == 2
        
    def test_timeout_with_simple_problem(self):
        """Test that simple problems complete within timeout."""
        expert = Z3Expert(timeout_normal=1, timeout_crisis=1)
        
        intent = """
        verify {
            x > 0
        }
        """
        
        start_time = time.time()
        verdict = expert.verify(intent, "tx_012")
        elapsed = time.time() - start_time
        
        # Should complete quickly
        assert elapsed < 1.0
        assert verdict.verdict == "APPROVE"
        assert verdict.latency_ms < 1000


class TestZ3ExpertComplexityLimits:
    """Test DoS protection via complexity limits."""
    
    def test_too_many_variables(self):
        """Test rejection when too many variables."""
        expert = Z3Expert()
        expert.MAX_VARIABLES = 5  # Set low limit for testing
        
        # Create intent with many variables
        intent = "verify {\n"
        for i in range(10):
            intent += f"    var{i} > 0\n"
        intent += "}"
        
        verdict = expert.verify(intent, "tx_013")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0
        assert "too many variables" in verdict.reason.lower()
        
    def test_too_many_constraints(self):
        """Test rejection when too many constraints."""
        expert = Z3Expert()
        expert.MAX_CONSTRAINTS = 5  # Set low limit for testing
        
        # Create intent with many constraints
        intent = "verify {\n"
        for i in range(10):
            intent += f"    x > {i}\n"
        intent += "}"
        
        verdict = expert.verify(intent, "tx_014")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence == 1.0
        assert "too many constraints" in verdict.reason.lower()
        
    def test_within_complexity_limits(self):
        """Test approval when within complexity limits."""
        expert = Z3Expert()
        
        intent = """
        verify {
            x > 0
            y > 0
            z > 0
        }
        """
        
        verdict = expert.verify(intent, "tx_015")
        
        assert verdict.verdict == "APPROVE"


class TestZ3ExpertErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_intent(self):
        """Test handling of empty intent."""
        expert = Z3Expert()
        
        verdict = expert.verify("", "tx_016")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 0.5  # Low confidence
        
    def test_malformed_intent(self):
        """Test handling of malformed intent."""
        expert = Z3Expert()
        
        intent = "verify { this is not valid syntax }"
        
        verdict = expert.verify(intent, "tx_017")
        
        # Should handle gracefully
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.latency_ms > 0
        
    def test_telemetry_recording(self):
        """Test that verifications are recorded for telemetry."""
        expert = Z3Expert()
        
        initial_count = expert.total_verifications
        
        intent = "verify { x > 0 }"
        expert.verify(intent, "tx_018")
        
        assert expert.total_verifications == initial_count + 1
        assert expert.total_latency_ms > 0
        
    def test_get_stats(self):
        """Test get_stats returns correct information."""
        expert = Z3Expert()
        
        # Perform some verifications
        for i in range(3):
            expert.verify("verify { x > 0 }", f"tx_{i}")
        
        stats = expert.get_stats()
        
        assert stats['name'] == "Z3_Expert"
        assert stats['total_verifications'] == 3
        assert stats['average_latency_ms'] > 0


class TestZ3ExpertIntegration:
    """Integration tests for Z3Expert."""
    
    def test_conservation_verification(self):
        """Test verification of conservation law."""
        expert = Z3Expert()
        
        intent = """
        guard {
            balance_before == 1000
            transfer_amount == 100
        }
        verify {
            balance_after == balance_before - transfer_amount
            balance_after == 900
        }
        """
        
        verdict = expert.verify(intent, "tx_019")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5
        
    def test_financial_invariant(self):
        """Test verification of financial invariant."""
        expert = Z3Expert()
        
        intent = """
        guard {
            total_supply == 1000000
            burned == 100
        }
        verify {
            new_supply == total_supply - burned
            new_supply < total_supply
        }
        """
        
        verdict = expert.verify(intent, "tx_020")
        
        assert verdict.verdict == "APPROVE"
        
    def test_multiple_verifications(self):
        """Test multiple sequential verifications."""
        expert = Z3Expert()
        
        intents = [
            "verify { x > 0 }",
            "verify { y < 100 }",
            "verify { z == 50 }"
        ]
        
        for i, intent in enumerate(intents):
            verdict = expert.verify(intent, f"tx_{i}")
            assert verdict.expert_name == "Z3_Expert"
            assert verdict.latency_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
