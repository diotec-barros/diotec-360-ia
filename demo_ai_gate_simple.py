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
AI Gate Simple Demo - The First Conversation with the Gods

This demo shows the AI Gate in action:
1. We ask an external AI to generate Aethel code
2. The AI responds with logic
3. Our Judge validates the logic
4. We accept or reject based on proof

This is the first time Aethel "talks" to external AIs!

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
"""

from diotec360.ai.ai_gate import AIGate, AIProvider
import json


def demo_simple_transfer():
    """
    Demo 1: Simple bank transfer
    
    Ask AI to generate code for a safe bank transfer.
    """
    print("\n" + "=" * 80)
    print("DEMO 1: SIMPLE BANK TRANSFER")
    print("=" * 80)
    
    gate = AIGate()
    
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
        "total_before == total_after"
    ]
    
    expected_behavior = [
        "Sender balance decreases by amount",
        "Receiver balance increases by amount",
        "Total money in system unchanged"
    ]
    
    print(f"\n[DEMO] 🤖 Querying AI with requirement...")
    print(f"[DEMO] Requirement: {requirement.strip()}")
    
    result = gate.query(
        requirement=requirement,
        constraints=constraints,
        expected_behavior=expected_behavior,
        provider=AIProvider.OPENAI,
        model="gpt-4"
    )
    
    print(f"\n[DEMO] 📊 Result:")
    print(f"  Success: {result.success}")
    print(f"  Total Time: {result.total_time_ms:.2f}ms")
    print(f"  Generation Time: {result.response.generation_time_ms:.2f}ms")
    print(f"  Validation Time: {result.validation.validation_time_ms:.2f}ms")
    print(f"  Tokens Used: {result.response.tokens_used}")
    print(f"  Attempt: {result.response.attempt}")
    
    if result.success:
        print(f"\n[DEMO] ✅ AI-GENERATED CODE PASSED VERIFICATION!")
        print(f"\n[DEMO] Generated Code:")
        print("-" * 80)
        print(result.response.code)
        print("-" * 80)
    else:
        print(f"\n[DEMO] ❌ AI-GENERATED CODE FAILED VERIFICATION")
        print(f"[DEMO] Reason: {result.validation.verification_result.reason}")
        if result.validation.feedback:
            print(f"[DEMO] Feedback: {result.validation.feedback}")
    
    return result


def demo_loan_calculator():
    """
    Demo 2: Loan payment calculator
    
    Ask AI to generate code for calculating loan payments.
    """
    print("\n" + "=" * 80)
    print("DEMO 2: LOAN PAYMENT CALCULATOR")
    print("=" * 80)
    
    gate = AIGate()
    
    requirement = """
    Generate code that calculates loan payments with:
    - Principal amount
    - Interest rate
    - Number of periods
    - Prove: total paid = principal + interest
    - Prove: no overflow in calculations
    """
    
    constraints = [
        "principal > 0",
        "interest_rate >= 0",
        "periods > 0",
        "total_paid == principal + total_interest"
    ]
    
    expected_behavior = [
        "Calculate monthly payment",
        "Calculate total interest",
        "Prove conservation of money"
    ]
    
    print(f"\n[DEMO] 🤖 Querying AI with requirement...")
    print(f"[DEMO] Requirement: {requirement.strip()}")
    
    result = gate.query(
        requirement=requirement,
        constraints=constraints,
        expected_behavior=expected_behavior,
        provider=AIProvider.OPENAI,
        model="gpt-4"
    )
    
    print(f"\n[DEMO] 📊 Result:")
    print(f"  Success: {result.success}")
    print(f"  Total Time: {result.total_time_ms:.2f}ms")
    
    if result.success:
        print(f"\n[DEMO] ✅ AI-GENERATED CODE PASSED VERIFICATION!")
        print(f"\n[DEMO] Generated Code:")
        print("-" * 80)
        print(result.response.code)
        print("-" * 80)
    else:
        print(f"\n[DEMO] ❌ AI-GENERATED CODE FAILED VERIFICATION")
        print(f"[DEMO] Reason: {result.validation.verification_result.reason}")
    
    return result


def demo_statistics():
    """
    Demo 3: Show AI Gate statistics
    """
    print("\n" + "=" * 80)
    print("DEMO 3: AI GATE STATISTICS")
    print("=" * 80)
    
    gate = AIGate()
    stats = gate.get_statistics()
    
    print(f"\n[DEMO] 📊 AI Gate Statistics:")
    print(f"  Total Queries: {stats['total_queries']}")
    print(f"  Successful: {stats['successful_queries']}")
    print(f"  Failed: {stats['failed_queries']}")
    print(f"  Success Rate: {stats['success_rate_percent']:.1f}%")
    print(f"  Total Retries: {stats['total_retries']}")
    print(f"  Avg Retries per Success: {stats['avg_retries_per_success']:.2f}")
    print(f"  Cache Size: {stats['cache_size']}")
    
    return stats


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🏛️ AETHEL AI GATE - THE FIRST CONVERSATION WITH THE GODS 🧠")
    print("=" * 80)
    print("\nThis demo shows the AI Gate connecting Aethel to external AIs.")
    print("We ask GPT-4 to generate code, then validate it with our Judge.")
    print("\nThe AI Gate implements the 'Filter of Divinity' principle:")
    print("  1. We don't trust external AIs blindly")
    print("  2. We use them to generate hypotheses")
    print("  3. We validate everything through formal verification")
    print("  4. We only accept what the Judge proves to be perfect")
    
    # Run demos
    try:
        result1 = demo_simple_transfer()
        result2 = demo_loan_calculator()
        stats = demo_statistics()
        
        print("\n" + "=" * 80)
        print("🎉 AI GATE DEMO COMPLETE!")
        print("=" * 80)
        print("\nThe bridge to the AI multiverse is operational!")
        print("Aethel can now 'drink' intelligence from external AIs")
        print("while maintaining the fortress of formal verification.")
        
        print("\n[STATUS: THE SYMBIOSIS HAS BEGUN] 🌌✨🧠🔐")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\nNote: This demo requires API keys for external AIs.")
        print("Set environment variables:")
        print("  - OPENAI_API_KEY for OpenAI")
        print("  - ANTHROPIC_API_KEY for Claude")
        print("\nOr use local models with AIProvider.LOCAL_LLAMA")
