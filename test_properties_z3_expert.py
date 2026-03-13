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
Property-Based Tests for Z3Expert

Tests correctness properties using Hypothesis:
- Property 1: Z3 Expert accuracy
- Property 2: Z3 Expert latency

**Validates: Requirements 2.6, 2.7**

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
import time

from diotec360.moe.z3_expert import Z3Expert
from diotec360.moe.data_models import ExpertVerdict


# Strategy for generating valid variable names
variable_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=10
).filter(lambda x: x.isalpha() and x not in ['and', 'or', 'not', 'true', 'false'])

# Strategy for generating integers
safe_integers = st.integers(min_value=-1000000, max_value=1000000)

# Strategy for generating comparison operators
comparison_ops = st.sampled_from(['>', '<', '>=', '<=', '==', '!='])

# Strategy for generating arithmetic operators
arithmetic_ops = st.sampled_from(['+', '-', '*'])


@st.composite
def simple_constraint(draw):
    """Generate a simple constraint like 'x > 5'."""
    var = draw(variable_names)
    op = draw(comparison_ops)
    value = draw(safe_integers)
    return f"{var} {op} {value}"


@st.composite
def arithmetic_constraint(draw):
    """Generate an arithmetic constraint like 'x + y > 10'."""
    var1 = draw(variable_names)
    var2 = draw(variable_names)
    assume(var1 != var2)  # Different variables
    
    arith_op = draw(arithmetic_ops)
    comp_op = draw(comparison_ops)
    value = draw(safe_integers)
    
    return f"{var1} {arith_op} {var2} {comp_op} {value}"


@st.composite
def valid_intent(draw):
    """Generate a valid intent with guards and verify blocks."""
    num_guards = draw(st.integers(min_value=0, max_value=5))
    num_verifies = draw(st.integers(min_value=1, max_value=5))
    
    guards = [draw(simple_constraint()) for _ in range(num_guards)]
    verifies = [draw(simple_constraint()) for _ in range(num_verifies)]
    
    intent = ""
    if guards:
        intent += "guard {\n"
        for guard in guards:
            intent += f"    {guard}\n"
        intent += "}\n"
    
    intent += "verify {\n"
    for verify in verifies:
        intent += f"    {verify}\n"
    intent += "}"
    
    return intent


class TestZ3ExpertAccuracyProperty:
    """
    Property 1: Z3 Expert accuracy
    
    **Validates: Requirements 2.6**
    
    The Z3 Expert must maintain high accuracy in detecting mathematical
    contradictions and validating consistent constraints.
    """
    
    @given(
        var=variable_names,
        value1=safe_integers,
        value2=safe_integers
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_1_contradiction_detection(self, var, value1, value2):
        """
        Property: Z3 Expert correctly detects contradictions.
        
        If we assert x == value1 and x == value2 where value1 != value2,
        the expert MUST reject with high confidence.
        """
        assume(value1 != value2)  # Ensure contradiction
        
        expert = Z3Expert()
        
        intent = f"""
        verify {{
            {var} == {value1}
            {var} == {value2}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop1_{var}")
        
        # Property: Must reject contradictions
        assert verdict.verdict == "REJECT", \
            f"Failed to detect contradiction: {var} == {value1} and {var} == {value2}"
        
        # Property: Must have high confidence in rejection
        assert verdict.confidence >= 0.7, \
            f"Low confidence ({verdict.confidence}) for clear contradiction"
    
    @given(
        var=variable_names,
        value=safe_integers
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_1_tautology_acceptance(self, var, value):
        """
        Property: Z3 Expert correctly accepts tautologies.
        
        If we assert x == value and x == value (same constraint),
        the expert MUST approve.
        """
        expert = Z3Expert()
        
        intent = f"""
        verify {{
            {var} == {value}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop1_taut_{var}")
        
        # Property: Must approve tautologies
        assert verdict.verdict == "APPROVE", \
            f"Failed to approve tautology: {var} == {value}"
    
    @given(
        var=variable_names,
        lower=safe_integers,
        upper=safe_integers
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_1_range_consistency(self, var, lower, upper):
        """
        Property: Z3 Expert correctly validates range constraints.
        
        If lower <= upper, then x >= lower AND x <= upper is satisfiable.
        If lower > upper, then x >= lower AND x <= upper is unsatisfiable.
        """
        expert = Z3Expert()
        
        intent = f"""
        verify {{
            {var} >= {lower}
            {var} <= {upper}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop1_range_{var}")
        
        if lower <= upper:
            # Property: Valid range should be approved
            assert verdict.verdict == "APPROVE", \
                f"Failed to approve valid range: {lower} <= {var} <= {upper}"
        else:
            # Property: Invalid range should be rejected
            assert verdict.verdict == "REJECT", \
                f"Failed to reject invalid range: {lower} <= {var} <= {upper}"
    
    @given(
        var1=variable_names,
        var2=variable_names,
        value1=safe_integers,
        value2=safe_integers
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_1_arithmetic_consistency(self, var1, var2, value1, value2):
        """
        Property: Z3 Expert correctly validates arithmetic constraints.
        
        If var1 == value1 and var2 == value2, then var1 + var2 == value1 + value2
        must be satisfiable.
        """
        assume(var1 != var2)  # Different variables
        
        expert = Z3Expert()
        
        expected_sum = value1 + value2
        
        intent = f"""
        guard {{
            {var1} == {value1}
            {var2} == {value2}
        }}
        verify {{
            {var1} + {var2} == {expected_sum}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop1_arith_{var1}_{var2}")
        
        # Property: Arithmetic consistency must be approved
        assert verdict.verdict == "APPROVE", \
            f"Failed to approve arithmetic consistency: {var1}={value1}, {var2}={value2}, sum={expected_sum}"


class TestZ3ExpertLatencyProperty:
    """
    Property 2: Z3 Expert latency
    
    **Validates: Requirements 2.7**
    
    The Z3 Expert must complete verification within specified timeout limits:
    - Normal mode: 30 seconds
    - Crisis mode: 5 seconds
    """
    
    @given(intent=valid_intent())
    @settings(max_examples=30, deadline=35000, suppress_health_check=[HealthCheck.too_slow])
    def test_property_2_normal_mode_latency(self, intent):
        """
        Property: Z3 Expert completes within normal timeout (30s).
        
        For any valid intent, verification must complete within 30 seconds
        in normal mode.
        """
        expert = Z3Expert(timeout_normal=30, timeout_crisis=5)
        
        start_time = time.time()
        verdict = expert.verify(intent, "tx_prop2_normal")
        elapsed = time.time() - start_time
        
        # Property: Must complete within timeout
        assert elapsed < 30.0, \
            f"Verification exceeded normal timeout: {elapsed:.2f}s > 30s"
        
        # Property: Latency metric should match actual time
        assert abs(verdict.latency_ms - elapsed * 1000) < 100, \
            f"Latency metric mismatch: {verdict.latency_ms}ms vs {elapsed * 1000}ms"
    
    @given(intent=valid_intent())
    @settings(max_examples=30, deadline=10000, suppress_health_check=[HealthCheck.too_slow])
    def test_property_2_crisis_mode_latency(self, intent):
        """
        Property: Z3 Expert completes within crisis timeout (5s).
        
        For any valid intent, verification must complete within 5 seconds
        in crisis mode.
        """
        expert = Z3Expert(timeout_normal=30, timeout_crisis=5)
        expert.set_crisis_mode(True)
        
        start_time = time.time()
        verdict = expert.verify(intent, "tx_prop2_crisis")
        elapsed = time.time() - start_time
        
        # Property: Must complete within crisis timeout
        assert elapsed < 5.0, \
            f"Verification exceeded crisis timeout: {elapsed:.2f}s > 5s"
    
    @given(
        var=variable_names,
        value=safe_integers
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_2_simple_intent_fast(self, var, value):
        """
        Property: Simple intents complete quickly.
        
        Simple intents (single constraint) should complete in under 1 second.
        """
        expert = Z3Expert()
        
        intent = f"""
        verify {{
            {var} > {value}
        }}
        """
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop2_fast_{var}")
        elapsed = time.time() - start_time
        
        # Property: Simple intents should be fast
        assert elapsed < 1.0, \
            f"Simple intent took too long: {elapsed:.2f}s > 1s"
        
        # Property: Latency should be recorded
        assert verdict.latency_ms > 0, \
            "Latency not recorded"
    
    @given(num_constraints=st.integers(min_value=1, max_value=20))
    @settings(max_examples=20, deadline=10000)
    def test_property_2_latency_scales_with_complexity(self, num_constraints):
        """
        Property: Latency scales reasonably with complexity.
        
        More constraints should not cause exponential latency growth.
        """
        expert = Z3Expert()
        
        # Generate intent with multiple constraints
        intent = "verify {\n"
        for i in range(num_constraints):
            intent += f"    x{i} > 0\n"
        intent += "}"
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop2_scale_{num_constraints}")
        elapsed = time.time() - start_time
        
        # Property: Should complete within reasonable time
        # Allow 0.1s per constraint as upper bound
        max_allowed = num_constraints * 0.1
        assert elapsed < max_allowed, \
            f"Latency grew too much: {elapsed:.2f}s for {num_constraints} constraints"
    
    @given(intent=valid_intent())
    @settings(max_examples=30, deadline=35000, suppress_health_check=[HealthCheck.too_slow])
    def test_property_2_telemetry_recording(self, intent):
        """
        Property: All verifications are recorded for telemetry.
        
        Every verification must increment the verification counter and
        record latency.
        """
        expert = Z3Expert()
        
        initial_count = expert.total_verifications
        initial_latency = expert.total_latency_ms
        
        verdict = expert.verify(intent, "tx_prop2_telemetry")
        
        # Property: Verification count must increase
        assert expert.total_verifications == initial_count + 1, \
            "Verification not counted"
        
        # Property: Latency must be recorded
        assert expert.total_latency_ms > initial_latency, \
            "Latency not recorded"
        
        # Property: Recorded latency should match verdict latency
        latency_delta = expert.total_latency_ms - initial_latency
        assert abs(latency_delta - verdict.latency_ms) < 1.0, \
            f"Latency mismatch: {latency_delta}ms vs {verdict.latency_ms}ms"


class TestZ3ExpertRobustnessProperties:
    """Additional robustness properties for Z3Expert."""
    
    @given(
        var=variable_names,
        num_vars=st.integers(min_value=1, max_value=150)
    )
    @settings(max_examples=20, deadline=10000)
    def test_property_complexity_protection(self, var, num_vars):
        """
        Property: Expert rejects intents exceeding complexity limits.
        
        Intents with too many variables should be rejected to prevent DoS.
        """
        expert = Z3Expert()
        expert.MAX_VARIABLES = 100  # Set limit
        
        # Generate intent with many variables
        intent = "verify {\n"
        for i in range(num_vars):
            intent += f"    {var}{i} > 0\n"
        intent += "}"
        
        verdict = expert.verify(intent, f"tx_prop_complex_{num_vars}")
        
        if num_vars > expert.MAX_VARIABLES:
            # Property: Must reject when over limit
            assert verdict.verdict == "REJECT", \
                f"Failed to reject intent with {num_vars} variables (limit: {expert.MAX_VARIABLES})"
            assert "too many variables" in verdict.reason.lower(), \
                "Rejection reason should mention variable limit"
        else:
            # Property: Should process when within limit
            assert verdict.expert_name == "Z3_Expert", \
                "Expert should process intent within limits"
    
    @given(text=st.text(min_size=0, max_size=100))
    @settings(max_examples=50, deadline=5000)
    def test_property_graceful_error_handling(self, text):
        """
        Property: Expert handles malformed input gracefully.
        
        Any input should return a valid ExpertVerdict without crashing.
        """
        expert = Z3Expert()
        
        # This should not crash
        verdict = expert.verify(text, "tx_prop_error")
        
        # Property: Must return valid verdict
        assert isinstance(verdict, ExpertVerdict), \
            "Must return ExpertVerdict even for malformed input"
        
        # Property: Must have expert name
        assert verdict.expert_name == "Z3_Expert", \
            "Verdict must have correct expert name"
        
        # Property: Must have latency
        assert verdict.latency_ms >= 0, \
            "Latency must be non-negative"
        
        # Property: Verdict must be valid
        assert verdict.verdict in ["APPROVE", "REJECT"], \
            f"Invalid verdict: {verdict.verdict}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
