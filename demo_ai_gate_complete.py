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
Complete AI Gate Demonstration

This demo shows the AI Gate in action:
1. Querying external AIs (GPT-5, Claude)
2. Validating responses with Judge
3. Feedback loop for rejected responses
4. Caching successful responses
5. Fallback to alternative providers

Author: Kiro AI - Chief Engineer
Date: February 15, 2026
"""

from diotec360.ai.ai_gate import AIGate, AIProvider


def demo_simple_transfer():
    """Demo 1: Simple bank transfer"""
    print("\n" + "=" * 80)
    print("DEMO 1: SIMPLE BANK TRANSFER")
    print("=" * 80)
    
    gate = AIGate(
        default_provider=AIProvider.OPENAI,
        default_model="gpt-4",
        enable_fallback=True,
        enable_caching=True
    )
    
    requirement = """
    Implement a safe bank transfer that:
    1. Checks sender has sufficient balance
    2. Transfers amount to receiver
    3. Proves conservation (total money unchanged)
    4. Handles edge cases (zero transfer, negative amounts)
    """
    
    constraints = [
        "sender_balance >= amount",
        "amount > 0",
        "new_sender_balance >= 0"
    ]
    
    expected_behavior = [
        "Total money before = Total money after",
        "Sender balance decreases by amount",
        "Receiver balance increases by amount"
    ]
    
    result = gate.query(
        requirement=requirement,
        constraints=constraints,
        expected_behavior=expected_behavior
    )
    
    print(f"\n[RESULT] Verdict: {result.verdict}")
    if result.verdict == "ACCEPTED":
        print(f"[RESULT] ✅ Code is formally verified!")
        print(f"[RESULT] Generated Code:")
        print(result.code)
        if result.proof:
            print(f"\n[RESULT] Proof: {result.proof}")
    else:
        print(f"[RESULT] ❌ Code was rejected")
        print(f"[RESULT] Reason: {result.reason}")
        for error in result.errors:
            print(f"[RESULT]   - {error}")


def demo_loan_calculator():
    """Demo 2: Loan payment calculator"""
    print("\n" + "=" * 80)
    print("DEMO 2: LOAN PAYMENT CALCULATOR")
    print("=" * 80)
    
    gate = AIGate()
    
    requirement = """
    Generate code that calculates loan payments with:
    - Principal amount
    - Interest rate (annual percentage)
    - Number of periods (months)
    - Prove: total paid = principal + interest
    - Prove: no overflow in calculations
    - Prove: monthly payment is positive
    """
    
    constraints = [
        "principal > 0",
        "interest_rate >= 0",
        "num_periods > 0",
        "monthly_payment > 0"
    ]
    
    result = gate.query(
        requirement=requirement,
        constraints=constraints
    )
    
    print(f"\n[RESULT] Verdict: {result.verdict}")
    if result.verdict == "ACCEPTED":
        print(f"[RESULT] ✅ Loan calculator is formally verified!")
        print(f"[RESULT] Generation Time: {result.ai_response.generation_time_ms:.0f}ms")
        print(f"[RESULT] Validation Time: {result.validation_time_ms:.0f}ms")
        print(f"[RESULT] Cost: ${result.ai_response.cost_usd:.4f}")
    else:
        print(f"[RESULT] ❌ Code was rejected")
        print(f"[RESULT] Reason: {result.reason}")


def demo_multi_party_settlement():
    """Demo 3: Multi-party debt settlement"""
    print("\n" + "=" * 80)
    print("DEMO 3: MULTI-PARTY DEBT SETTLEMENT")
    print("=" * 80)
    
    gate = AIGate()
    
    requirement = """
    Generate code that settles debts between N parties:
    - Input: list of debts (who owes whom how much)
    - Output: minimal set of transfers to settle all debts
    - Prove: conservation (total money unchanged)
    - Prove: all debts settled after transfers
    - Prove: number of transfers is minimized
    """
    
    constraints = [
        "sum(debts_before) == sum(debts_after)",
        "all debts_after == 0",
        "num_transfers <= num_parties - 1"
    ]
    
    expected_behavior = [
        "All parties end with zero debt",
        "Total money in system unchanged",
        "Minimal number of transfers used"
    ]
    
    result = gate.query(
        requirement=requirement,
        constraints=constraints,
        expected_behavior=expected_behavior
    )
    
    print(f"\n[RESULT] Verdict: {result.verdict}")
    if result.verdict == "ACCEPTED":
        print(f"[RESULT] ✅ Settlement algorithm is formally verified!")
    else:
        print(f"[RESULT] ❌ Code was rejected")
        print(f"[RESULT] This is a complex problem, AI might need multiple attempts")


def demo_cache_hit():
    """Demo 4: Cache hit demonstration"""
    print("\n" + "=" * 80)
    print("DEMO 4: CACHE HIT DEMONSTRATION")
    print("=" * 80)
    
    gate = AIGate(enable_caching=True)
    
    requirement = "Implement a simple addition function that adds two numbers"
    
    # First query (cache miss)
    print("\n[DEMO] First query (cache miss)...")
    result1 = gate.query(requirement=requirement)
    
    # Second query (cache hit)
    print("\n[DEMO] Second query (cache hit)...")
    result2 = gate.query(requirement=requirement)
    
    print(f"\n[RESULT] First query time: {result1.validation_time_ms:.0f}ms")
    print(f"[RESULT] Second query time: {result2.validation_time_ms:.0f}ms")
    print(f"[RESULT] Cache speedup: {result1.validation_time_ms / max(result2.validation_time_ms, 1):.1f}x")


def demo_fallback_provider():
    """Demo 5: Fallback provider demonstration"""
    print("\n" + "=" * 80)
    print("DEMO 5: FALLBACK PROVIDER DEMONSTRATION")
    print("=" * 80)
    
    gate = AIGate(
        default_provider=AIProvider.OPENAI,
        enable_fallback=True
    )
    
    requirement = "Implement a factorial function with overflow protection"
    
    # This will try OpenAI first, then fallback to Anthropic if it fails
    result = gate.query(requirement=requirement)
    
    print(f"\n[RESULT] Verdict: {result.verdict}")
    if result.ai_response:
        print(f"[RESULT] Provider used: {result.ai_response.provider.value}")
        print(f"[RESULT] Model used: {result.ai_response.model}")


def demo_statistics():
    """Demo 6: Statistics and analytics"""
    print("\n" + "=" * 80)
    print("DEMO 6: STATISTICS AND ANALYTICS")
    print("=" * 80)
    
    gate = AIGate()
    
    # Run multiple queries
    requirements = [
        "Add two numbers",
        "Subtract two numbers",
        "Multiply two numbers with overflow check",
        "Divide two numbers with zero check"
    ]
    
    for req in requirements:
        gate.query(requirement=req)
    
    # Get statistics
    stats = gate.get_statistics()
    
    print("\n[STATISTICS]")
    print(f"  Total Queries: {stats['total_queries']}")
    print(f"  Successful: {stats['successful_validations']}")
    print(f"  Failed: {stats['failed_validations']}")
    print(f"  Success Rate: {stats['success_rate_percent']:.1f}%")
    print(f"  Cache Hits: {stats['cache_hits']}")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate_percent']:.1f}%")
    print(f"  Total Cost: ${stats['total_cost_usd']:.4f}")
    print(f"  Avg Generation Time: {stats['avg_generation_time_ms']:.0f}ms")
    print(f"  Avg Validation Time: {stats['avg_validation_time_ms']:.0f}ms")
    
    # Export feedback history
    gate.export_feedback_history("ai_gate_feedback_history.json")
    print("\n[EXPORT] Feedback history exported to ai_gate_feedback_history.json")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("AETHEL AI GATE - COMPLETE DEMONSTRATION")
    print("The Bridge to the AI Multiverse")
    print("=" * 80)
    print("\nThis demo shows how the AI Gate interrogates external AIs")
    print("and validates their logic with our Judge.")
    print("\nThe AI Gate implements the 'Divinity Filter' principle:")
    print("  - We don't trust external AIs to make decisions")
    print("  - We use them to generate hypotheses")
    print("  - We validate everything through formal verification")
    print("  - We only accept what the Judge proves to be perfect")
    
    try:
        # Run demos
        demo_simple_transfer()
        demo_loan_calculator()
        demo_multi_party_settlement()
        demo_cache_hit()
        demo_fallback_provider()
        demo_statistics()
        
        print("\n" + "=" * 80)
        print("DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\n✅ The AI Gate is operational!")
        print("✅ External AIs can now be interrogated and validated!")
        print("✅ The Bridge to the AI Multiverse is OPEN!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("\nNote: This demo requires:")
        print("  1. OpenAI API key (OPENAI_API_KEY environment variable)")
        print("  2. Anthropic API key (ANTHROPIC_API_KEY environment variable)")
        print("  3. Active internet connection")
        print("\nTo run in simulation mode, set AETHEL_AI_GATE_SIMULATION=true")


if __name__ == "__main__":
    main()
