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
Property-Based Tests for GuardianExpert

Tests correctness properties using Hypothesis:
- Property 5: Guardian Expert accuracy
- Property 6: Guardian Expert latency

**Validates: Requirements 4.6, 4.7**

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
import time

from diotec360.moe.guardian_expert import GuardianExpert
from diotec360.moe.data_models import ExpertVerdict


# Strategy for generating valid variable names
variable_names = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), min_codepoint=97, max_codepoint=122),
    min_size=1,
    max_size=10
).filter(lambda x: x.isalpha() and x not in ['and', 'or', 'not', 'true', 'false', 'old'])

# Strategy for generating safe integers (avoid overflow)
safe_integers = st.integers(min_value=-1000000, max_value=1000000)

# Strategy for generating positive amounts
positive_amounts = st.integers(min_value=1, max_value=100000)


@st.composite
def balanced_transfer(draw):
    """Generate a balanced transfer (conservation preserved)."""
    sender = draw(variable_names)
    receiver = draw(variable_names)
    assume(sender != receiver)  # Different accounts
    
    amount = draw(positive_amounts)
    
    intent = f"""
    verify {{
        {sender}_balance == old_{sender}_balance - {amount}
        {receiver}_balance == old_{receiver}_balance + {amount}
    }}
    """
    
    return intent, amount


@st.composite
def unbalanced_transfer(draw):
    """Generate an unbalanced transfer (conservation violated)."""
    sender = draw(variable_names)
    receiver = draw(variable_names)
    assume(sender != receiver)
    
    sent_amount = draw(positive_amounts)
    received_amount = draw(positive_amounts)
    assume(sent_amount != received_amount)  # Ensure imbalance
    
    intent = f"""
    verify {{
        {sender}_balance == old_{sender}_balance - {sent_amount}
        {receiver}_balance == old_{receiver}_balance + {received_amount}
    }}
    """
    
    return intent, sent_amount, received_amount


@st.composite
def multi_party_transfer(draw):
    """Generate a multi-party transfer."""
    num_receivers = draw(st.integers(min_value=2, max_value=5))
    
    sender = draw(variable_names)
    receivers = [draw(variable_names) for _ in range(num_receivers)]
    
    # Ensure all names are unique
    all_names = [sender] + receivers
    assume(len(set(all_names)) == len(all_names))
    
    # Generate amounts that sum correctly
    amounts = [draw(st.integers(min_value=1, max_value=1000)) for _ in range(num_receivers)]
    total_sent = sum(amounts)
    
    intent = f"verify {{\n"
    intent += f"    {sender}_balance == old_{sender}_balance - {total_sent}\n"
    for receiver, amount in zip(receivers, amounts):
        intent += f"    {receiver}_balance == old_{receiver}_balance + {amount}\n"
    intent += "}"
    
    return intent, total_sent, amounts


class TestGuardianExpertAccuracyProperty:
    """
    Property 5: Guardian Expert accuracy
    
    **Validates: Requirements 4.6**
    
    The Guardian Expert must maintain high accuracy in detecting
    conservation violations and validating financial constraints.
    """
    
    @given(transfer=balanced_transfer())
    @settings(max_examples=50, deadline=5000)
    def test_property_5_conservation_approval(self, transfer):
        """
        Property: Guardian Expert correctly approves balanced transfers.
        
        If sum(inputs) == sum(outputs), the expert MUST approve with
        high confidence.
        """
        intent, amount = transfer
        
        expert = GuardianExpert()
        verdict = expert.verify(intent, f"tx_prop5_balanced_{amount}")
        
        # Property: Must approve balanced transfers
        assert verdict.verdict == "APPROVE", \
            f"Failed to approve balanced transfer of {amount}"
        
        # Property: Must have high confidence
        assert verdict.confidence >= 0.9, \
            f"Low confidence ({verdict.confidence}) for balanced transfer"
    
    @given(transfer=unbalanced_transfer())
    @settings(max_examples=50, deadline=5000)
    def test_property_5_conservation_rejection(self, transfer):
        """
        Property: Guardian Expert correctly rejects unbalanced transfers.
        
        If sum(inputs) != sum(outputs), the expert MUST reject with
        high confidence.
        """
        intent, sent, received = transfer
        
        expert = GuardianExpert()
        verdict = expert.verify(intent, f"tx_prop5_unbalanced_{sent}_{received}")
        
        # Property: Must reject unbalanced transfers
        assert verdict.verdict == "REJECT", \
            f"Failed to reject unbalanced transfer: sent={sent}, received={received}"
        
        # Property: Must have high confidence in rejection
        assert verdict.confidence >= 0.9, \
            f"Low confidence ({verdict.confidence}) for conservation violation"
        
        # Property: Reason should mention conservation
        assert verdict.reason is not None, \
            "Rejection should have a reason"
        assert "conservation" in verdict.reason.lower(), \
            f"Reason should mention conservation: {verdict.reason}"
    
    @given(transfer=multi_party_transfer())
    @settings(max_examples=30, deadline=5000)
    def test_property_5_multi_party_conservation(self, transfer):
        """
        Property: Guardian Expert correctly validates multi-party transfers.
        
        For transfers with multiple receivers, conservation must still hold:
        sum(all outputs) == sum(all inputs).
        """
        intent, total_sent, amounts = transfer
        total_received = sum(amounts)
        
        expert = GuardianExpert()
        verdict = expert.verify(intent, f"tx_prop5_multi_{total_sent}")
        
        # Property: Must approve if balanced
        assert verdict.verdict == "APPROVE", \
            f"Failed to approve multi-party transfer: sent={total_sent}, received={total_received}"
        
        # Property: Must have high confidence
        assert verdict.confidence >= 0.9, \
            f"Low confidence for multi-party transfer"
    
    @given(
        sender=variable_names,
        receiver=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_5_zero_sum_invariant(self, sender, receiver, amount):
        """
        Property: Guardian Expert enforces zero-sum invariant.
        
        For any transfer, the net change across all accounts must be zero.
        """
        assume(sender != receiver)
        
        expert = GuardianExpert()
        
        # Balanced transfer
        intent = f"""
        verify {{
            {sender}_balance == old_{sender}_balance - {amount}
            {receiver}_balance == old_{receiver}_balance + {amount}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop5_zero_sum_{amount}")
        
        # Property: Zero-sum transfers must be approved
        assert verdict.verdict == "APPROVE", \
            f"Failed to approve zero-sum transfer"
        
        # Property: Perfect conservation = perfect confidence
        assert verdict.confidence == 1.0, \
            f"Perfect conservation should have confidence 1.0, got {verdict.confidence}"
    
    @given(
        var=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_5_money_creation_detection(self, var, amount):
        """
        Property: Guardian Expert detects money creation.
        
        If balance increases without corresponding decrease elsewhere,
        the expert MUST reject (money created from nothing).
        """
        expert = GuardianExpert()
        
        # Money creation: balance increases with no source
        intent = f"""
        verify {{
            {var}_balance == old_{var}_balance + {amount}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop5_creation_{amount}")
        
        # Property: Must reject money creation
        assert verdict.verdict == "REJECT", \
            f"Failed to detect money creation: +{amount}"
        
        # Property: High confidence in rejection
        assert verdict.confidence >= 0.9, \
            f"Low confidence for money creation detection"
    
    @given(
        var=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_5_money_destruction_detection(self, var, amount):
        """
        Property: Guardian Expert detects money destruction.
        
        If balance decreases without corresponding increase elsewhere,
        the expert MUST reject (money destroyed).
        """
        expert = GuardianExpert()
        
        # Money destruction: balance decreases with no destination
        intent = f"""
        verify {{
            {var}_balance == old_{var}_balance - {amount}
        }}
        """
        
        verdict = expert.verify(intent, f"tx_prop5_destruction_{amount}")
        
        # Property: Must reject money destruction
        assert verdict.verdict == "REJECT", \
            f"Failed to detect money destruction: -{amount}"
        
        # Property: High confidence in rejection
        assert verdict.confidence >= 0.9, \
            f"Low confidence for money destruction detection"


class TestGuardianExpertLatencyProperty:
    """
    Property 6: Guardian Expert latency
    
    **Validates: Requirements 4.7**
    
    The Guardian Expert must complete verification within 50ms timeout.
    """
    
    @given(transfer=balanced_transfer())
    @settings(max_examples=50, deadline=5000)
    def test_property_6_latency_under_timeout(self, transfer):
        """
        Property: Guardian Expert completes within 50ms timeout.
        
        For any valid transfer, verification must complete within 50ms.
        """
        intent, amount = transfer
        
        expert = GuardianExpert(timeout_ms=50)
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop6_latency_{amount}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Property: Must complete quickly (allow some overhead)
        assert elapsed_ms < 100, \
            f"Verification took too long: {elapsed_ms:.2f}ms > 100ms"
        
        # Property: Latency metric should match actual time
        assert abs(verdict.latency_ms - elapsed_ms) < 10, \
            f"Latency metric mismatch: {verdict.latency_ms}ms vs {elapsed_ms}ms"
    
    @given(transfer=multi_party_transfer())
    @settings(max_examples=30, deadline=5000)
    def test_property_6_complex_transfer_latency(self, transfer):
        """
        Property: Complex transfers complete within timeout.
        
        Even multi-party transfers should complete within 50ms.
        """
        intent, total_sent, amounts = transfer
        
        expert = GuardianExpert(timeout_ms=50)
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop6_complex_{total_sent}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Property: Must complete within reasonable time
        assert elapsed_ms < 100, \
            f"Complex transfer took too long: {elapsed_ms:.2f}ms"
        
        # Property: Latency should be recorded
        assert verdict.latency_ms > 0, \
            "Latency not recorded"
    
    @given(
        sender=variable_names,
        receiver=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_6_simple_transfer_fast(self, sender, receiver, amount):
        """
        Property: Simple transfers complete very quickly.
        
        Simple two-party transfers should complete in under 20ms.
        """
        assume(sender != receiver)
        
        expert = GuardianExpert()
        
        intent = f"""
        verify {{
            {sender}_balance == old_{sender}_balance - {amount}
            {receiver}_balance == old_{receiver}_balance + {amount}
        }}
        """
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop6_fast_{amount}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Property: Simple transfers should be very fast
        assert elapsed_ms < 50, \
            f"Simple transfer took too long: {elapsed_ms:.2f}ms > 50ms"
    
    @given(num_transfers=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20, deadline=5000)
    def test_property_6_latency_scales_linearly(self, num_transfers):
        """
        Property: Latency scales linearly with number of transfers.
        
        Processing multiple balance changes should not cause exponential
        latency growth.
        """
        expert = GuardianExpert()
        
        # Generate intent with multiple balance changes
        intent = "verify {\n"
        total_sent = 0
        for i in range(num_transfers):
            amount = 100
            total_sent += amount
            intent += f"    sender_balance == old_sender_balance - {total_sent}\n"
            intent += f"    receiver{i}_balance == old_receiver{i}_balance + {amount}\n"
        intent += "}"
        
        start_time = time.time()
        verdict = expert.verify(intent, f"tx_prop6_scale_{num_transfers}")
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Property: Should complete within reasonable time
        # Allow 10ms per transfer as upper bound
        max_allowed_ms = num_transfers * 10
        assert elapsed_ms < max_allowed_ms, \
            f"Latency grew too much: {elapsed_ms:.2f}ms for {num_transfers} transfers"
    
    @given(transfer=balanced_transfer())
    @settings(max_examples=50, deadline=5000)
    def test_property_6_telemetry_recording(self, transfer):
        """
        Property: All verifications are recorded for telemetry.
        
        Every verification must increment the verification counter and
        record latency.
        """
        intent, amount = transfer
        
        expert = GuardianExpert()
        
        initial_count = expert.total_verifications
        initial_latency = expert.total_latency_ms
        
        verdict = expert.verify(intent, f"tx_prop6_telemetry_{amount}")
        
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


class TestGuardianExpertRobustnessProperties:
    """Additional robustness properties for GuardianExpert."""
    
    @given(text=st.text(min_size=0, max_size=100))
    @settings(max_examples=50, deadline=5000)
    def test_property_graceful_error_handling(self, text):
        """
        Property: Expert handles malformed input gracefully.
        
        Any input should return a valid ExpertVerdict without crashing.
        """
        expert = GuardianExpert()
        
        # This should not crash
        verdict = expert.verify(text, "tx_prop_error")
        
        # Property: Must return valid verdict
        assert isinstance(verdict, ExpertVerdict), \
            "Must return ExpertVerdict even for malformed input"
        
        # Property: Must have expert name
        assert verdict.expert_name == "Guardian_Expert", \
            "Verdict must have correct expert name"
        
        # Property: Must have latency
        assert verdict.latency_ms >= 0, \
            "Latency must be non-negative"
        
        # Property: Verdict must be valid
        assert verdict.verdict in ["APPROVE", "REJECT"], \
            f"Invalid verdict: {verdict.verdict}"
    
    @given(
        sender=variable_names,
        receiver=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_double_spending_prevention(self, sender, receiver, amount):
        """
        Property: Expert prevents double-spending.
        
        The same transaction ID cannot be processed twice.
        """
        assume(sender != receiver)
        
        expert = GuardianExpert()
        
        intent = f"""
        verify {{
            {sender}_balance == old_{sender}_balance - {amount}
            {receiver}_balance == old_{receiver}_balance + {amount}
        }}
        """
        
        tx_id = f"tx_prop_double_{amount}"
        
        # First verification should succeed
        verdict1 = expert.verify(intent, tx_id)
        assert verdict1.verdict == "APPROVE", \
            "First verification should succeed"
        
        # Second verification with same tx_id should fail
        verdict2 = expert.verify(intent, tx_id)
        assert verdict2.verdict == "REJECT", \
            "Double-spending should be rejected"
        assert "double-spending" in verdict2.reason.lower(), \
            "Rejection should mention double-spending"
    
    @given(
        var=variable_names,
        amount=positive_amounts
    )
    @settings(max_examples=50, deadline=5000)
    def test_property_merkle_state_consistency(self, var, amount):
        """
        Property: Merkle tree state remains consistent.
        
        State updates should maintain Merkle tree integrity.
        """
        expert = GuardianExpert()
        
        # Update state
        expert.update_state(f"{var}_balance", amount)
        
        # Get root hash
        root1 = expert.get_state_root()
        
        # Property: Root hash should be valid
        assert root1 is not None, \
            "Root hash should not be None"
        assert len(root1) == 64, \
            f"Root hash should be 64 chars (SHA-256), got {len(root1)}"
        
        # Update state again
        expert.update_state(f"{var}_balance", amount + 1)
        
        # Get new root hash
        root2 = expert.get_state_root()
        
        # Property: Root hash should change when state changes
        assert root2 != root1, \
            "Root hash should change when state changes"
    
    @given(
        sender=variable_names,
        receiver=variable_names,
        amount=positive_amounts,
        num_sequential=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=20, deadline=5000)
    def test_property_sequential_transactions(self, sender, receiver, amount, num_sequential):
        """
        Property: Sequential transactions are processed correctly.
        
        Multiple different transactions should all be processed successfully.
        """
        assume(sender != receiver)
        
        expert = GuardianExpert()
        
        for i in range(num_sequential):
            intent = f"""
            verify {{
                {sender}_balance == old_{sender}_balance - {amount}
                {receiver}_balance == old_{receiver}_balance + {amount}
            }}
            """
            
            verdict = expert.verify(intent, f"tx_prop_seq_{i}_{amount}")
            
            # Property: Each transaction should be approved
            assert verdict.verdict == "APPROVE", \
                f"Transaction {i} should be approved"
            
            # Property: Each should have high confidence
            assert verdict.confidence >= 0.9, \
                f"Transaction {i} should have high confidence"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
