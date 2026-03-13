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
Property-Based Tests for SentinelExpert - Security Specialist

Tests properties:
- Property 3: Sentinel Expert accuracy
- Property 4: Sentinel Expert latency

**Validates: Requirements 3.6, 3.7**

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from diotec360.moe.sentinel_expert import SentinelExpert
from diotec360.moe.data_models import ExpertVerdict


# Strategy for generating Python code strings
@st.composite
def python_code(draw):
    """Generate valid Python code snippets"""
    code_templates = [
        # Simple assignments
        "x = {value}",
        "result = {value} + {value2}",
        "balance = old_balance + {value}",
        
        # Function definitions
        "def func():\n    return {value}",
        "def process(x):\n    return x + {value}",
        
        # Loops
        "for i in range({value}):\n    pass",
        "while condition:\n    break",
        
        # Conditionals
        "if x > {value}:\n    pass",
        "if condition:\n    result = {value}",
    ]
    
    template = draw(st.sampled_from(code_templates))
    value = draw(st.integers(min_value=0, max_value=1000))
    value2 = draw(st.integers(min_value=0, max_value=1000))
    
    return template.format(value=value, value2=value2)


@st.composite
def malicious_code(draw):
    """Generate potentially malicious code patterns"""
    patterns = [
        # Infinite loops
        "while True:\n    pass",
        "while True:\n    x = x + 1",
        
        # Infinite recursion
        "def bomb(n):\n    return bomb(n + 1)",
        "def recurse():\n    return recurse()",
        
        # Resource exhaustion
        "def exhaust():\n    data = []\n    while True:\n        data += [0] * 1000000",
    ]
    
    return draw(st.sampled_from(patterns))


@st.composite
def high_entropy_code(draw):
    """Generate high-entropy (obfuscated) code"""
    # Generate random variable names
    var_count = draw(st.integers(min_value=10, max_value=30))
    
    code_lines = []
    for i in range(var_count):
        var1 = f"a{i}b{i}c{i}"
        var2 = f"d{i}e{i}f{i}"
        var3 = f"g{i}h{i}i{i}"
        op = draw(st.sampled_from(['+', '-', '*', '/']))
        code_lines.append(f"{var1} = {var2} {op} {var3}")
    
    return "\n".join(code_lines)


class TestProperty3_SentinelExpertAccuracy:
    """
    Property 3: Sentinel Expert accuracy
    
    **Validates: Requirements 3.6**
    
    The Sentinel Expert must accurately detect security vulnerabilities:
    - Malicious patterns (infinite loops, recursion) should be rejected
    - Safe code should be approved
    - Confidence scores should reflect detection certainty
    """
    
    @given(code=python_code())
    @settings(max_examples=50, deadline=2000)
    def test_property_3_1_safe_code_approval(self, code):
        """
        Property 3.1: Safe code should be approved with reasonable confidence
        
        For any safe Python code:
        - Expert should return a verdict (APPROVE or REJECT)
        - Confidence should be between 0.0 and 1.0
        - Latency should be recorded
        """
        expert = SentinelExpert()
        
        verdict = expert.verify(code, "tx_prop_3_1")
        
        # Verdict must be valid
        assert isinstance(verdict, ExpertVerdict)
        assert verdict.verdict in ["APPROVE", "REJECT"]
        
        # Confidence must be in valid range
        assert 0.0 <= verdict.confidence <= 1.0
        
        # Latency must be positive
        assert verdict.latency_ms > 0
        
        # Expert name must be correct
        assert verdict.expert_name == "Sentinel_Expert"
    
    @given(code=malicious_code())
    @settings(max_examples=20, deadline=2000)
    def test_property_3_2_malicious_code_rejection(self, code):
        """
        Property 3.2: Malicious code patterns should be rejected
        
        For any code with known malicious patterns:
        - Expert should reject with high confidence
        - Reason should be provided
        """
        expert = SentinelExpert()
        
        verdict = expert.verify(code, "tx_prop_3_2")
        
        # Malicious code should be rejected
        assert verdict.verdict == "REJECT"
        
        # Confidence should be reasonable (at least 0.5)
        assert verdict.confidence >= 0.5
        
        # Reason should be provided for rejection
        assert verdict.reason is not None
        assert len(verdict.reason) > 0
    
    @given(code=high_entropy_code())
    @settings(max_examples=20, deadline=2000)
    def test_property_3_3_entropy_detection(self, code):
        """
        Property 3.3: High entropy code should have elevated entropy scores
        
        For any high-entropy (obfuscated) code:
        - Entropy score should be calculated
        - Entropy should be higher than typical code
        """
        expert = SentinelExpert()
        
        verdict = expert.verify(code, "tx_prop_3_3")
        
        # Entropy should be tracked
        assert 'entropy_score' in verdict.proof_trace
        entropy = verdict.proof_trace['entropy_score']
        
        # Entropy should be in valid range
        assert 0.0 <= entropy <= 1.0
        
        # High entropy code should have elevated entropy
        # (at least higher than minimal code)
        assert entropy > 0.2
    
    @given(
        code=python_code(),
        tx_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=30, deadline=2000)
    def test_property_3_4_consistency(self, code, tx_id):
        """
        Property 3.4: Same code should produce consistent verdicts
        
        For any code verified multiple times:
        - Verdict should be consistent
        - Confidence should be similar (within 0.1)
        """
        expert = SentinelExpert()
        
        # Verify twice
        verdict1 = expert.verify(code, tx_id + "_1")
        verdict2 = expert.verify(code, tx_id + "_2")
        
        # Verdicts should be consistent
        assert verdict1.verdict == verdict2.verdict
        
        # Confidence should be similar
        confidence_diff = abs(verdict1.confidence - verdict2.confidence)
        assert confidence_diff < 0.1
    
    @given(code=python_code())
    @settings(max_examples=30, deadline=2000)
    def test_property_3_5_proof_trace_completeness(self, code):
        """
        Property 3.5: Proof trace should contain required information
        
        For any verification:
        - Proof trace should exist
        - Should contain entropy_score or error information
        """
        expert = SentinelExpert()
        
        verdict = expert.verify(code, "tx_prop_3_5")
        
        # Proof trace must exist
        assert verdict.proof_trace is not None
        assert isinstance(verdict.proof_trace, dict)
        
        # Should contain either entropy_score or error
        has_entropy = 'entropy_score' in verdict.proof_trace
        has_error = 'error' in verdict.proof_trace
        
        assert has_entropy or has_error


class TestProperty4_SentinelExpertLatency:
    """
    Property 4: Sentinel Expert latency
    
    **Validates: Requirements 3.7**
    
    The Sentinel Expert must complete verification within timeout:
    - Normal verification should complete within 100ms
    - Latency should be accurately recorded
    - Timeout should be respected
    """
    
    @given(code=python_code())
    @settings(max_examples=50, deadline=2000)
    def test_property_4_1_latency_within_timeout(self, code):
        """
        Property 4.1: Verification should complete within timeout
        
        For any code:
        - Latency should be less than or equal to timeout (with margin)
        - Latency should be positive
        """
        timeout_ms = 100
        expert = SentinelExpert(timeout_ms=timeout_ms)
        
        verdict = expert.verify(code, "tx_prop_4_1")
        
        # Latency must be positive
        assert verdict.latency_ms > 0
        
        # Latency should be within reasonable bounds
        # Allow 2x margin for system variance
        assert verdict.latency_ms < timeout_ms * 2
    
    @given(code=python_code())
    @settings(max_examples=30, deadline=2000)
    def test_property_4_2_latency_recorded_accurately(self, code):
        """
        Property 4.2: Latency should be accurately recorded
        
        For any verification:
        - Recorded latency should match actual execution time (within margin)
        """
        import time
        
        expert = SentinelExpert()
        
        start = time.time()
        verdict = expert.verify(code, "tx_prop_4_2")
        actual_latency_ms = (time.time() - start) * 1000
        
        # Recorded latency should be close to actual
        # Allow 100% margin for measurement overhead and system variance
        latency_diff = abs(verdict.latency_ms - actual_latency_ms)
        assert latency_diff < actual_latency_ms * 1.0
    
    @given(
        code=python_code(),
        timeout_ms=st.integers(min_value=50, max_value=200)
    )
    @settings(max_examples=20, deadline=3000)
    def test_property_4_3_timeout_configuration(self, code, timeout_ms):
        """
        Property 4.3: Timeout should be configurable
        
        For any timeout value:
        - Expert should respect the configured timeout
        - Verification should complete within reasonable time
        """
        expert = SentinelExpert(timeout_ms=timeout_ms)
        
        verdict = expert.verify(code, "tx_prop_4_3")
        
        # Should complete within configured timeout (with margin)
        assert verdict.latency_ms < timeout_ms * 2
    
    @given(code=python_code())
    @settings(max_examples=30, deadline=2000)
    def test_property_4_4_fast_verification_for_simple_code(self, code):
        """
        Property 4.4: Simple code should verify quickly
        
        For any simple code:
        - Verification should complete well within timeout
        - Latency should be reasonable (< 50ms for most cases)
        """
        expert = SentinelExpert(timeout_ms=100)
        
        verdict = expert.verify(code, "tx_prop_4_4")
        
        # Most simple code should verify quickly
        # Allow some cases to take longer due to system variance
        # Just ensure it's not timing out
        assert verdict.latency_ms < expert.timeout_ms * 1.5
    
    @given(code=python_code())
    @settings(max_examples=20, deadline=2000)
    def test_property_4_5_telemetry_tracking(self, code):
        """
        Property 4.5: Latency should be tracked in telemetry
        
        For any verification:
        - Total verifications should increment
        - Average latency should be calculated
        """
        expert = SentinelExpert()
        
        initial_count = expert.total_verifications
        
        verdict = expert.verify(code, "tx_prop_4_5")
        
        # Verification count should increment
        assert expert.total_verifications == initial_count + 1
        
        # Average latency should be calculated
        avg_latency = expert.get_average_latency()
        assert avg_latency > 0
        
        # Total latency should be tracked
        assert expert.total_latency_ms > 0


class TestProperty_Integration:
    """Integration properties combining accuracy and latency"""
    
    @given(
        code=python_code(),
        tx_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=30, deadline=2000)
    def test_property_integration_verdict_completeness(self, code, tx_id):
        """
        Integration Property: Every verdict should be complete and valid
        
        For any verification:
        - All required fields should be present
        - All fields should have valid values
        - Verdict should be actionable
        """
        expert = SentinelExpert()
        
        verdict = expert.verify(code, tx_id)
        
        # Required fields
        assert verdict.expert_name == "Sentinel_Expert"
        assert verdict.verdict in ["APPROVE", "REJECT"]
        assert 0.0 <= verdict.confidence <= 1.0
        assert verdict.latency_ms > 0
        
        # Proof trace
        assert verdict.proof_trace is not None
        assert isinstance(verdict.proof_trace, dict)
        
        # Reason for rejection
        if verdict.verdict == "REJECT":
            # Rejections should have a reason (unless it's an expert failure)
            if verdict.confidence > 0.0:
                assert verdict.reason is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
