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
Property-Based Tests for GatingNetwork

Tests routing correctness and latency properties using Hypothesis.

Properties:
- Property 7: Routing correctness
- Property 8: Routing latency

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import time
from diotec360.moe.gating_network import GatingNetwork


# Strategy for generating transaction intents
@st.composite
def intent_strategy(draw):
    """Generate random transaction intents with various features."""
    
    # Choose intent type
    intent_type = draw(st.sampled_from([
        'financial',
        'arithmetic',
        'loop',
        'recursion',
        'complex',
        'empty',
        'mixed'
    ]))
    
    if intent_type == 'financial':
        amount = draw(st.integers(min_value=1, max_value=10000))
        from_account = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=10))
        to_account = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=3, max_size=10))
        return f"transfer {amount} from {from_account} to {to_account}"
    
    elif intent_type == 'arithmetic':
        a = draw(st.integers(min_value=1, max_value=100))
        b = draw(st.integers(min_value=1, max_value=100))
        op = draw(st.sampled_from(['+', '-', '*', '/']))
        return f"let result = {a} {op} {b}"
    
    elif intent_type == 'loop':
        iterations = draw(st.integers(min_value=1, max_value=100))
        return f"for i in range({iterations}) {{ process(i) }}"
    
    elif intent_type == 'recursion':
        return "function factorial(n) { return n * factorial(n-1) }"
    
    elif intent_type == 'complex':
        nesting = draw(st.integers(min_value=3, max_value=8))
        indent = "    "
        lines = ["function complex(a, b, c) {"]
        for i in range(nesting):
            lines.append(indent * (i + 1) + f"if a > {i} {{")
        lines.append(indent * (nesting + 1) + "return a + b + c")
        for i in range(nesting):
            lines.append(indent * (nesting - i) + "}")
        lines.append("}")
        return "\n".join(lines)
    
    elif intent_type == 'empty':
        return ""
    
    else:  # mixed
        amount = draw(st.integers(min_value=1, max_value=1000))
        return f"transfer {amount} from alice to bob\nverify {{ alice_balance >= {amount} }}\nlet new_balance = alice_balance - {amount}"


class TestGatingNetworkProperties:
    """Property-based tests for GatingNetwork."""
    
    @given(intent=intent_strategy())
    @settings(max_examples=100, deadline=1000)
    def test_property_7_routing_correctness(self, intent):
        """
        Property 7: Routing correctness
        
        **Validates: Requirements 5.7**
        
        Property: For any transaction intent, the gating network must:
        1. Return a non-empty list of experts
        2. Only return valid expert names
        3. Not return duplicate experts
        4. Activate Guardian for financial transactions
        5. Activate Z3 for arithmetic operations
        6. Activate Sentinel for loops
        """
        gating = GatingNetwork()
        
        # Route the intent
        experts = gating.route(intent)
        
        # Property 1: Must return non-empty list
        assert len(experts) > 0, "Routing must activate at least one expert"
        
        # Property 2: Only valid expert names
        valid_experts = {'Z3_Expert', 'Sentinel_Expert', 'Guardian_Expert'}
        for expert in experts:
            assert expert in valid_experts, f"Invalid expert name: {expert}"
        
        # Property 3: No duplicates
        assert len(experts) == len(set(experts)), "Routing must not return duplicate experts"
        
        # Property 4: Guardian for financial transactions
        if any(keyword in intent.lower() for keyword in ['transfer', 'send', 'pay', 'balance']):
            assert 'Guardian_Expert' in experts, "Guardian must be activated for financial transactions"
        
        # Property 5: Z3 for arithmetic operations
        if any(op in intent for op in ['+', '-', '*', '/', 'calculate', 'compute']):
            assert 'Z3_Expert' in experts, "Z3 must be activated for arithmetic operations"
        
        # Property 6: Sentinel for loops
        if any(keyword in intent.lower() for keyword in ['for', 'while', 'loop']):
            assert 'Sentinel_Expert' in experts, "Sentinel must be activated for loops"
    
    @given(intent=intent_strategy())
    @settings(max_examples=100, deadline=1000)
    def test_property_8_routing_latency(self, intent):
        """
        Property 8: Routing latency
        
        **Validates: Requirements 5.7**
        
        Property: For any transaction intent, routing must complete within 10ms.
        This is a critical performance requirement for the gating network.
        """
        gating = GatingNetwork()
        
        # Measure routing latency
        start_time = time.time()
        experts = gating.route(intent)
        latency_ms = (time.time() - start_time) * 1000
        
        # Property: Routing must complete within 10ms (Requirement 5.7)
        assert latency_ms < 10.0, f"Routing latency {latency_ms:.2f}ms exceeds 10ms limit"
        
        # Verify latency was recorded correctly
        if len(gating.routing_history) > 0:
            recorded_latency = gating.routing_history[-1].latency_ms
            # Recorded latency should be close to measured latency (within 1ms tolerance)
            assert abs(recorded_latency - latency_ms) < 1.0, "Recorded latency should match measured latency"
    
    @given(
        intents=st.lists(intent_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=50, deadline=2000)
    def test_property_routing_consistency(self, intents):
        """
        Property: Routing consistency
        
        Property: Routing the same intent multiple times should produce the same result.
        The gating network should be deterministic.
        """
        gating = GatingNetwork()
        
        for intent in intents:
            # Route the same intent twice
            experts1 = gating.route(intent)
            experts2 = gating.route(intent)
            
            # Should produce the same result (order may differ, so compare sets)
            assert set(experts1) == set(experts2), "Routing should be deterministic"
    
    @given(intent=intent_strategy())
    @settings(max_examples=100, deadline=1000)
    def test_property_feature_extraction_completeness(self, intent):
        """
        Property: Feature extraction completeness
        
        Property: Feature extraction must always return all required features.
        """
        gating = GatingNetwork()
        
        features = gating.extract_features(intent)
        
        # Required features
        required_features = [
            'has_transfers',
            'has_arithmetic',
            'has_loops',
            'has_recursion',
            'complexity_score',
            'intent_length',
            'num_variables',
            'num_functions'
        ]
        
        for feature in required_features:
            assert feature in features, f"Missing required feature: {feature}"
        
        # Feature types
        assert isinstance(features['has_transfers'], bool)
        assert isinstance(features['has_arithmetic'], bool)
        assert isinstance(features['has_loops'], bool)
        assert isinstance(features['has_recursion'], bool)
        assert isinstance(features['complexity_score'], float)
        assert isinstance(features['intent_length'], int)
        assert isinstance(features['num_variables'], int)
        assert isinstance(features['num_functions'], int)
        
        # Feature ranges
        assert 0.0 <= features['complexity_score'] <= 1.0, "Complexity score must be in [0, 1]"
        assert features['intent_length'] >= 0, "Intent length must be non-negative"
        assert features['num_variables'] >= 0, "Number of variables must be non-negative"
        assert features['num_functions'] >= 0, "Number of functions must be non-negative"
    
    @given(
        intents=st.lists(intent_strategy(), min_size=10, max_size=50)
    )
    @settings(max_examples=20, deadline=5000)
    def test_property_statistics_accuracy(self, intents):
        """
        Property: Statistics accuracy
        
        Property: Routing statistics must accurately reflect routing history.
        """
        gating = GatingNetwork()
        
        # Route all intents
        for intent in intents:
            gating.route(intent)
        
        stats = gating.get_routing_stats()
        
        # Total routings should match
        assert stats['total_routings'] == len(intents), "Total routings should match number of intents"
        
        # Average latency should be positive
        assert stats['average_latency_ms'] > 0, "Average latency should be positive"
        
        # Activation rates should be in [0, 1]
        for expert, rate in stats['expert_activation_rates'].items():
            assert 0.0 <= rate <= 1.0, f"Activation rate for {expert} must be in [0, 1]"
        
        # Average experts per routing should be >= 1
        assert stats['average_experts_per_routing'] >= 1.0, "Average experts per routing should be at least 1"
    
    @given(intent=st.text(min_size=0, max_size=10000))
    @settings(max_examples=100, deadline=1000)
    def test_property_robustness_arbitrary_input(self, intent):
        """
        Property: Robustness to arbitrary input
        
        Property: The gating network should handle any string input without crashing.
        """
        gating = GatingNetwork()
        
        try:
            # Should not crash on any input
            experts = gating.route(intent)
            
            # Should always return a list
            assert isinstance(experts, list), "Route should always return a list"
            
            # Should always return at least one expert
            assert len(experts) > 0, "Route should always activate at least one expert"
            
        except Exception as e:
            pytest.fail(f"Gating network crashed on input: {e}")
    
    @given(
        intent=intent_strategy(),
        history_size=st.integers(min_value=1, max_value=100)
    )
    @settings(max_examples=50, deadline=2000)
    def test_property_history_size_limit(self, intent, history_size):
        """
        Property: History size limit
        
        Property: Routing history should respect the configured size limit.
        """
        gating = GatingNetwork(history_size=history_size)
        
        # Route more intents than history size
        num_routings = history_size + 10
        for _ in range(num_routings):
            gating.route(intent)
        
        # History should not exceed size limit
        assert len(gating.routing_history) <= history_size, "History should not exceed size limit"
    
    @given(intent=intent_strategy())
    @settings(max_examples=100, deadline=1000)
    def test_property_routing_decision_structure(self, intent):
        """
        Property: Routing decision structure
        
        Property: Each routing decision should have the correct structure.
        """
        gating = GatingNetwork()
        
        experts = gating.route(intent)
        
        # Get the last routing decision
        decision = gating.routing_history[-1]
        
        # Check structure
        assert hasattr(decision, 'features'), "Decision should have features"
        assert hasattr(decision, 'activated_experts'), "Decision should have activated_experts"
        assert hasattr(decision, 'timestamp'), "Decision should have timestamp"
        assert hasattr(decision, 'latency_ms'), "Decision should have latency_ms"
        
        # Check values
        assert decision.activated_experts == experts, "Decision should record activated experts"
        assert decision.timestamp > 0, "Timestamp should be positive"
        assert decision.latency_ms >= 0, "Latency should be non-negative"
        
        # Features should match extracted features
        extracted_features = gating.extract_features(intent)
        assert decision.features == extracted_features, "Decision features should match extracted features"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
