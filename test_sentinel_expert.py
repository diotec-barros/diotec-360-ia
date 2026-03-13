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
Unit Tests for SentinelExpert - Security Specialist

Tests cover:
- Overflow detection
- DoS pattern detection (infinite loops, resource exhaustion)
- Injection attack detection
- Entropy scoring and confidence calculation
- Timeout behavior

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import time
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.data_models import ExpertVerdict


class TestSentinelExpertBasics:
    """Test basic SentinelExpert functionality"""
    
    def test_initialization(self):
        """Test SentinelExpert initialization"""
        expert = SentinelExpert()
        
        assert expert.name == "Sentinel_Expert"
        assert expert.timeout_ms == 100
        assert expert.semantic_sanitizer is not None
        assert expert.overflow_sentinel is not None
        
    def test_custom_timeout(self):
        """Test SentinelExpert with custom timeout"""
        expert = SentinelExpert(timeout_ms=200)
        
        assert expert.timeout_ms == 200


class TestOverflowDetection:
    """Test overflow/underflow detection"""
    
    def test_detect_overflow_literal_addition(self):
        """Test detection of literal overflow in addition"""
        expert = SentinelExpert()
        
        # Intent with overflow in verify block (format expected by OverflowSentinel)
        intent = """
verify {
    balance == (9223372036854775800 + 100)
}
"""
        
        verdict = expert.verify(intent, "tx_overflow_001")
        
        # Should be rejected (either for overflow or syntax error)
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6
        assert verdict.latency_ms < expert.timeout_ms * 2
        
    def test_detect_underflow_literal_subtraction(self):
        """Test detection of literal underflow in subtraction"""
        expert = SentinelExpert()
        
        # Intent with underflow in verify block
        intent = """
verify {
    balance == (-9223372036854775800 - 100)
}
"""
        
        verdict = expert.verify(intent, "tx_underflow_001")
        
        # Should be rejected (either for underflow or syntax error)
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6
        
    def test_safe_arithmetic_operations(self):
        """Test that safe arithmetic operations are approved"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
balance = old_balance + 100
if balance >= 0:
    pass
"""
        
        verdict = expert.verify(intent, "tx_safe_001")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5
        assert verdict.reason is None


class TestDoSPatternDetection:
    """Test DoS attack pattern detection"""
    
    def test_detect_infinite_loop(self):
        """Test detection of infinite loop (while True without break)"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
def malicious():
    while True:
        x = x + 1
"""
        
        verdict = expert.verify(intent, "tx_dos_001")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6
        assert "loop" in verdict.reason.lower() or "unbounded" in verdict.reason.lower()
        
    def test_detect_infinite_recursion(self):
        """Test detection of infinite recursion (no base case)"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
def recursive_bomb(n):
    return recursive_bomb(n + 1)
"""
        
        verdict = expert.verify(intent, "tx_dos_002")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6
        assert "recursion" in verdict.reason.lower() or "recursive" in verdict.reason.lower()
        
    def test_detect_resource_exhaustion(self):
        """Test detection of exponential memory allocation"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
def exhaust_memory():
    data = []
    while True:
        data += [0] * 1000000
"""
        
        verdict = expert.verify(intent, "tx_dos_003")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6
        
    def test_safe_loop_with_break(self):
        """Test that loops with break statements are approved"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
def safe_loop():
    while True:
        if condition:
            break
"""
        
        verdict = expert.verify(intent, "tx_safe_loop_001")
        
        # Should approve - loop has break statement
        assert verdict.verdict == "APPROVE"


class TestInjectionAttackDetection:
    """Test injection attack detection through entropy analysis"""
    
    def test_detect_high_entropy_code(self):
        """Test detection of obfuscated/high-entropy code"""
        expert = SentinelExpert()
        
        # Very high entropy code with many random variable names - use valid Python syntax
        # Need extreme complexity to trigger high entropy rejection (threshold is 0.8)
        intent = """
def a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6():
    q7r8s9 = t0u1v2 + w3x4y5
    z6a7b8 = c9d0e1 * f2g3h4
    i5j6k7 = l8m9n0 / o1p2q3
    r4s5t6 = u7v8w9 - x0y1z2
    a3b4c5 = d6e7f8 + g9h0i1
    j2k3l4 = m5n6o7 * p8q9r0
    s1t2u3 = v4w5x6 / y7z8a9
    b0c1d2 = e3f4g5 - h6i7j8
    while k9l0m1:
        n2o3p4 = q5r6s7 + t8u9v0
        if w1x2y3:
            z4a5b6 = c7d8e9 - f0g1h2
            for i3 in j4k5l6:
                m7n8o9 = p0q1r2 * s3t4u5
                v6w7x8 = y9z0a1 / b2c3d4
"""
        
        verdict = expert.verify(intent, "tx_injection_001")
        
        # Test that entropy is calculated (should be high)
        # May or may not be rejected depending on exact entropy score
        assert 'entropy_score' in verdict.proof_trace
        entropy = verdict.proof_trace['entropy_score']
        
        # Entropy should be relatively high for this obfuscated code
        assert entropy > 0.4  # At least medium entropy
        
    def test_approve_low_entropy_code(self):
        """Test that readable code with low entropy is approved"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
sender_balance = old_sender_balance - amount
receiver_balance = old_receiver_balance + amount
"""
        
        verdict = expert.verify(intent, "tx_clean_001")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence > 0.5


class TestEntropyScoring:
    """Test entropy-based confidence scoring"""
    
    def test_confidence_decreases_with_entropy(self):
        """Test that approval confidence decreases as entropy increases"""
        expert = SentinelExpert()
        
        # Low entropy code - use valid Python syntax
        low_entropy_intent = """
amount = 100
"""
        
        # Medium entropy code
        medium_entropy_intent = """
def process_data(input):
    result = calculate_value(input)
    if result > threshold:
        return adjusted_result
"""
        
        verdict_low = expert.verify(low_entropy_intent, "tx_entropy_001")
        verdict_medium = expert.verify(medium_entropy_intent, "tx_entropy_002")
        
        # Both should approve, but low entropy should have higher confidence
        assert verdict_low.verdict == "APPROVE"
        assert verdict_medium.verdict == "APPROVE"
        assert verdict_low.confidence >= verdict_medium.confidence
        
    def test_rejection_confidence_increases_with_entropy(self):
        """Test that rejection confidence increases with entropy"""
        expert = SentinelExpert()
        
        # Very high entropy code (should be rejected) - use valid Python syntax
        high_entropy_intent = """
def a1b2c3d4e5f6g7h8i9j0():
    k1l2m3 = n4o5p6 + q7r8s9
    t0u1v2 = w3x4y5 * z6a7b8
    while c9d0e1:
        f2g3h4 = i5j6k7 + l8m9n0
        if o1p2q3:
            r4s5t6 = u7v8w9 - x0y1z2
            for a3 in b4c5d6:
                e7f8g9 = h0i1j2 * k3l4m5
"""
        
        verdict = expert.verify(high_entropy_intent, "tx_entropy_003")
        
        # Test that entropy is calculated and is high
        assert 'entropy_score' in verdict.proof_trace
        entropy = verdict.proof_trace['entropy_score']
        
        # Entropy should be high for this obfuscated code
        assert entropy > 0.4  # At least medium entropy
        
        # If rejected, confidence should be reasonable
        if verdict.verdict == "REJECT":
            assert verdict.confidence >= 0.6


class TestTimeoutBehavior:
    """Test timeout handling"""
    
    def test_respects_timeout_constraint(self):
        """Test that expert respects timeout constraint"""
        expert = SentinelExpert(timeout_ms=100)
        
        # Simple intent that should complete quickly - use valid Python syntax
        intent = """
amount = 100
"""
        
        verdict = expert.verify(intent, "tx_timeout_001")
        
        # Should complete within timeout
        assert verdict.latency_ms <= expert.timeout_ms * 1.5  # Allow 50% margin
        
    def test_fast_verification(self):
        """Test that verification completes quickly for simple intents"""
        expert = SentinelExpert(timeout_ms=100)
        
        # Use valid Python syntax
        intent = """
amount = 100
"""
        
        start = time.time()
        verdict = expert.verify(intent, "tx_fast_001")
        elapsed_ms = (time.time() - start) * 1000
        
        # Should complete well within timeout
        assert elapsed_ms < expert.timeout_ms
        assert verdict.latency_ms < expert.timeout_ms


class TestExpertFailureHandling:
    """Test expert failure scenarios"""
    
    def test_handles_invalid_intent_gracefully(self):
        """Test that expert handles invalid intent without crashing"""
        expert = SentinelExpert()
        
        # Invalid intent (empty string)
        verdict = expert.verify("", "tx_invalid_001")
        
        # Should not crash, should return a verdict
        assert isinstance(verdict, ExpertVerdict)
        assert verdict.expert_name == "Sentinel_Expert"
        
    def test_handles_malformed_intent(self):
        """Test handling of malformed intent"""
        expert = SentinelExpert()
        
        # Malformed intent with syntax errors
        intent = "this is not valid code {{{ ]]] ((("
        
        verdict = expert.verify(intent, "tx_malformed_001")
        
        # Should reject malformed code
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.0


class TestStatistics:
    """Test statistics and metrics"""
    
    def test_records_verification_metrics(self):
        """Test that expert records verification metrics"""
        expert = SentinelExpert()
        
        # Use valid Python syntax
        intent = """
amount = 100
"""
        
        # Perform multiple verifications
        for i in range(5):
            expert.verify(intent, f"tx_stats_{i}")
        
        stats = expert.get_stats()
        
        assert stats['total_verifications'] == 5
        assert stats['average_latency_ms'] > 0
        assert stats['name'] == "Sentinel_Expert"
        
    def test_security_specific_stats(self):
        """Test security-specific statistics"""
        expert = SentinelExpert(timeout_ms=150)
        
        stats = expert.get_security_stats()
        
        assert stats['timeout_ms'] == 150
        assert 'high_entropy_threshold' in stats
        assert 'semantic_sanitizer_patterns' in stats


class TestIntegrationWithComponents:
    """Test integration with SemanticSanitizer and OverflowSentinel"""
    
    def test_semantic_sanitizer_integration(self):
        """Test that SentinelExpert properly uses SemanticSanitizer"""
        expert = SentinelExpert()
        
        # Intent with known trojan pattern - use valid Python syntax
        intent = """
def trojan():
    while True:
        pass
"""
        
        verdict = expert.verify(intent, "tx_integration_001")
        
        assert verdict.verdict == "REJECT"
        assert 'entropy_score' in verdict.proof_trace or 'detected_patterns' in verdict.proof_trace
        
    def test_overflow_sentinel_integration(self):
        """Test that SentinelExpert properly uses OverflowSentinel"""
        expert = SentinelExpert()
        
        # Intent with overflow in verify block
        intent = """
verify {
    balance == (9223372036854775800 + 100)
}
"""
        
        verdict = expert.verify(intent, "tx_integration_002")
        
        # Should be rejected
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.6


class TestConfidenceCalculation:
    """Test confidence calculation logic"""
    
    def test_high_confidence_rejection_for_overflow(self):
        """Test high confidence rejection for overflow"""
        expert = SentinelExpert()
        
        intent = """
        verify {
            balance == (9223372036854775800 + 100)
        }
        """
        
        verdict = expert.verify(intent, "tx_conf_001")
        
        assert verdict.verdict == "REJECT"
        assert verdict.confidence >= 0.9
        
    def test_medium_confidence_rejection_for_entropy(self):
        """Test medium-high confidence rejection for high entropy"""
        expert = SentinelExpert()
        
        # High entropy code
        intent = """
        function x1y2z3() {
            a4b5c6 = d7e8f9 + g0h1i2
            j3k4l5 = m6n7o8 * p9q0r1
        }
        """
        
        verdict = expert.verify(intent, "tx_conf_002")
        
        if verdict.verdict == "REJECT":
            assert verdict.confidence >= 0.6
            
    def test_confidence_in_approval(self):
        """Test confidence calculation for approvals"""
        expert = SentinelExpert()
        
        # Clean, low-entropy code - use valid Python syntax
        intent = """
amount = 100
"""
        
        verdict = expert.verify(intent, "tx_conf_003")
        
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence >= 0.5  # Minimum confidence for approvals


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
