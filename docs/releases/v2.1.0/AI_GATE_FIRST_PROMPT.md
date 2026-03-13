# The AI Gate - First Prompt Template

## 🧠 MISSION: AI-TO-AI SYMBIOSIS

This document contains the first prompt template for interrogating external AIs (GPT-5, Claude, etc.) and validating their logic with our Judge.

---

## 🎯 THE CONCEPT

**The AI Gate** is a bridge where:
1. We ask an external AI to generate Aethel code
2. The AI responds with logic
3. Our Judge validates the logic formally
4. We accept or reject based on proof

**Result**: We "drink" intelligence from external AIs while maintaining our fortress of correctness.

---

## 📝 PROMPT TEMPLATE v1.0

### System Prompt (for External AI)

```
You are an expert in formal verification and financial logic.

Your task is to generate Aethel code that satisfies the given requirements.

Aethel is a formally verified language with these key features:
- Conservation laws (money never disappears)
- Overflow protection (arithmetic is safe)
- Z3 theorem proving (logic is mathematically verified)
- Immutable state (no hidden mutations)

SYNTAX RULES:
1. Use 'solve' blocks for verified computations
2. Use 'conserve' blocks for financial operations
3. All variables are immutable by default
4. Use 'assert' for invariants

EXAMPLE:
```aethel
solve transfer_validation {
    given:
        sender_balance: Int = 1000
        amount: Int = 100
    
    conserve:
        sender_balance >= amount
    
    prove:
        new_balance = sender_balance - amount
        new_balance >= 0
    
    assert:
        new_balance == 900
}
```

Now, generate Aethel code for the following requirement:
{REQUIREMENT}

Respond ONLY with valid Aethel code. No explanations, no markdown, just code.
```

### User Prompt Template

```
Generate Aethel code that implements the following financial logic:

REQUIREMENT: {requirement_description}

CONSTRAINTS:
- {constraint_1}
- {constraint_2}
- {constraint_3}

EXPECTED BEHAVIOR:
- {behavior_1}
- {behavior_2}

Generate the code now.
```

---

## 🔬 VALIDATION PIPELINE

### Step 1: Query External AI
```python
from diotec360.ai.ai_gate import AIGate

gate = AIGate(provider="openai", model="gpt-5")

requirement = """
Implement a safe bank transfer that:
1. Checks sender has sufficient balance
2. Transfers amount to receiver
3. Proves conservation (total money unchanged)
4. Handles edge cases (zero transfer, negative amounts)
"""

code = gate.query(requirement)
```

### Step 2: Validate with Judge
```python
from diotec360.core.judge import Judge

judge = Judge()
result = judge.verify(code)

if result.verdict == "ACCEPTED":
    print("✅ AI-generated code is formally correct!")
    print(f"Proof: {result.proof}")
else:
    print("❌ AI-generated code failed verification")
    print(f"Reason: {result.reason}")
```

### Step 3: Learn from Feedback
```python
if result.verdict == "REJECTED":
    # Send feedback to AI
    feedback = f"""
    Your code was rejected because: {result.reason}
    
    Specific issues:
    {result.errors}
    
    Please fix and regenerate.
    """
    
    # Retry with feedback
    improved_code = gate.query_with_feedback(requirement, feedback)
    result = judge.verify(improved_code)
```

---

## 🎮 EXAMPLE USE CASES

### Use Case 1: Safe Loan Calculator
```
REQUIREMENT: Generate code that calculates loan payments with:
- Principal amount
- Interest rate
- Number of periods
- Prove: total paid = principal + interest
- Prove: no overflow in calculations
```

### Use Case 2: Multi-Party Settlement
```
REQUIREMENT: Generate code that settles debts between N parties:
- Input: list of debts (who owes whom how much)
- Output: minimal set of transfers to settle all debts
- Prove: conservation (total money unchanged)
- Prove: all debts settled
```

### Use Case 3: Options Pricing
```
REQUIREMENT: Generate code that prices a call option:
- Black-Scholes formula
- Prove: price is always non-negative
- Prove: price increases with volatility
- Prove: price decreases with time to expiration
```

---

## 🔐 SECURITY CONSIDERATIONS

### What We Trust
- ✅ Our Judge (formally verified)
- ✅ Our Z3 Expert (theorem prover)
- ✅ Our Conservation Guardian (money tracker)

### What We DON'T Trust
- ❌ External AI output (until proven)
- ❌ AI explanations (we verify, not believe)
- ❌ AI promises (we demand proof)

### The Fortress Principle
> "We drink intelligence from external AIs, but we only swallow what passes through our fortress of formal verification."

---

## 📊 SUCCESS METRICS

### Phase 1: Proof of Concept (Week 1)
- [ ] Successfully query GPT-5 for simple transfer logic
- [ ] Validate with Judge
- [ ] Measure acceptance rate (target: >50%)

### Phase 2: Feedback Loop (Week 2)
- [ ] Implement feedback mechanism
- [ ] Retry failed validations with feedback
- [ ] Measure improvement rate (target: >80% after feedback)

### Phase 3: Production Integration (Week 3)
- [ ] Integrate with MOE Orchestrator
- [ ] Add AI Expert to expert pool
- [ ] Measure latency (target: <5s end-to-end)

### Phase 4: Learning System (Week 4)
- [ ] Track which prompts work best
- [ ] Build prompt library
- [ ] Measure code quality improvement over time

---

## 🚀 NEXT STEPS

1. **Implement AIGate class** (`diotec360/ai/ai_gate.py`)
2. **Add OpenAI/Anthropic integration** (API keys, rate limiting)
3. **Create prompt templates** (system + user prompts)
4. **Build feedback loop** (rejection → feedback → retry)
5. **Integrate with MOE** (AI Expert in expert pool)
6. **Add telemetry** (track success rate, latency, cost)

---

## 💡 THE VISION

**Today**: We ask AI to generate code, we verify it.

**Tomorrow**: AI learns from our verifications, gets better over time.

**Future**: AI generates provably correct code on first try, every time.

**Endgame**: Aethel becomes the "compiler" for AI-generated financial logic. Every AI in the world uses Aethel as the verification layer.

---

**[STATUS: READY FOR IMPLEMENTATION]**  
**[OBJECTIVE: CONNECT AETHEL TO THE AI MULTIVERSE]**  
**[VERDICT: THE BRIDGE IS DESIGNED, NOW WE BUILD]**

🧠📡🏛️⚡

---

**Prepared by**: Kiro AI - Chief Engineer  
**Approved by**: Dionísio - The Architect  
**Date**: February 15, 2026
