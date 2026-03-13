# Formal Verification in Aethel

## Overview

Aethel uses formal verification to mathematically prove program correctness. This document explains the theory, techniques, and practical applications of formal verification in Aethel.

## What is Formal Verification?

Formal verification is the process of proving or disproving the correctness of a system with respect to a formal specification using mathematical methods.

### Traditional Testing vs. Formal Verification

**Traditional Testing**:
- Tests specific inputs
- Cannot cover all cases
- May miss edge cases
- Provides confidence, not certainty

**Formal Verification**:
- Proves correctness for all inputs
- Covers all possible cases
- Finds all edge cases
- Provides mathematical certainty

### Example

```aethel
solve transfer {
    balance = 1000
    amount = 100
    
    assert amount <= balance
    
    balance = balance - amount
    
    # Formal verification proves:
    # ∀ amount, balance: (amount <= balance) → (balance - amount >= 0)
}
```

Traditional testing would check specific values. Formal verification proves the property holds for ALL values.

## Verification Techniques

### 1. Symbolic Execution

Aethel uses symbolic execution to explore all possible program paths.

**How it works**:
1. Replace concrete values with symbolic variables
2. Execute program symbolically
3. Generate path conditions
4. Verify conditions hold for all paths

**Example**:

```aethel
solve symbolic_example {
    # Concrete execution: x = 100
    # Symbolic execution: x = α (symbolic variable)
    
    x = 100  # x = α
    y = x + 50  # y = α + 50
    
    assert y > x  # Prove: (α + 50) > α for all α
}
```

Aethel proves: `∀α: (α + 50) > α` ✓

### 2. Constraint Solving

Aethel uses SMT (Satisfiability Modulo Theories) solvers to verify constraints.

**How it works**:
1. Convert assertions to logical formulas
2. Use SMT solver to check satisfiability
3. If unsatisfiable, constraint always holds
4. If satisfiable, find counterexample

**Example**:

```aethel
solve constraint_example {
    balance = 1000
    withdrawal = 150
    
    # Convert to formula: withdrawal <= balance
    # SMT solver checks: ∃ withdrawal, balance: ¬(withdrawal <= balance)
    # If no such values exist, constraint holds
    
    assert withdrawal <= balance
}
```

### 3. Inductive Reasoning

For loops and recursive structures, Aethel uses induction.

**How it works**:
1. Prove base case
2. Prove inductive step
3. Conclude property holds for all iterations

**Example** (future feature):

```aethel
solve inductive_example {
    balances = [1000, 2000, 3000]
    total = 0
    
    # Invariant: total = sum of processed elements
    for balance in balances {
        total = total + balance
        # Prove invariant holds after each iteration
    }
    
    assert total == 6000
}
```

### 4. Conservation Proofs

Aethel generates specialized proofs for conservation laws.

**How it works**:
1. Track all variable modifications
2. Verify total remains constant
3. Generate arithmetic proof
4. Check for overflow/underflow

**Example**:

```aethel
solve conservation_proof {
    alice = 1000
    bob = 500
    
    # Initial: Σ = 1500
    
    alice = alice - 100  # Σ = 1500 - 100 + 100 = 1500
    bob = bob + 100
    
    # Final: Σ = 1500
    
    conserve alice + bob == 1500
    
    # Proof:
    # Let alice₀ = 1000, bob₀ = 500
    # alice₁ = alice₀ - 100 = 900
    # bob₁ = bob₀ + 100 = 600
    # alice₁ + bob₁ = 900 + 600 = 1500 = alice₀ + bob₀ ✓
}
```

## Proof Types

### 1. Constraint Satisfaction Proofs

Proves that all assertions hold.

```aethel
solve constraint_proof {
    x = 100
    y = 50
    
    assert x > 0
    assert y > 0
    assert x > y
    
    # Proof:
    # Given: x = 100, y = 50
    # 1. x > 0: 100 > 0 ✓
    # 2. y > 0: 50 > 0 ✓
    # 3. x > y: 100 > 50 ✓
}
```

### 2. Conservation Proofs

Proves that totals are preserved.

```aethel
solve conservation_proof {
    total_before = alice + bob
    
    # ... operations ...
    
    conserve alice + bob == total_before
    
    # Proof: Arithmetic verification
}
```

### 3. Safety Proofs

Proves absence of errors (overflow, underflow, division by zero).

```aethel
solve safety_proof {
    balance = 1000
    withdrawal = 100
    
    # Prove: balance - withdrawal >= 0
    assert withdrawal <= balance
    
    balance = balance - withdrawal
    
    # Safety proof: No underflow
}
```

### 4. Liveness Proofs

Proves that desired outcomes are eventually reached (future feature).

```aethel
solve liveness_proof {
    # Prove: transaction eventually completes
    # Prove: balance eventually reaches target
}
```

## Proof Certificates

Aethel generates verifiable proof certificates.

### Certificate Structure

```json
{
  "program": "safe_transfer.ae",
  "version": "1.9.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "theorem": "Conservation holds for all executions",
  "proof_type": "conservation",
  "steps": [
    {
      "step": 1,
      "description": "Initial state: alice=1000, bob=500",
      "formula": "alice₀ + bob₀ = 1500"
    },
    {
      "step": 2,
      "description": "Transfer 100 from alice to bob",
      "formula": "alice₁ = alice₀ - 100, bob₁ = bob₀ + 100"
    },
    {
      "step": 3,
      "description": "Final state verification",
      "formula": "alice₁ + bob₁ = 900 + 600 = 1500"
    }
  ],
  "conclusion": "Conservation verified: alice + bob = 1500",
  "is_valid": true,
  "signature": "..."
}
```

### Verifying Certificates

```python
from diotec360.core.proof import verify_certificate

# Load certificate
with open("proof.json") as f:
    certificate = json.load(f)

# Verify independently
is_valid = verify_certificate(certificate)
print(f"Certificate valid: {is_valid}")
```

## Soundness and Completeness

### Soundness

**Definition**: If Diotec360 verifies a program, the program is correct.

**Guarantee**: Aethel is sound. Verified programs are mathematically correct.

**Why it matters**: No false positives. If verification passes, the program is safe.

### Completeness

**Definition**: If a program is correct, Aethel can verify it.

**Reality**: Aethel is incomplete (by design). Some correct programs may not verify.

**Why it matters**: False negatives are acceptable. Better to reject some correct programs than accept incorrect ones.

### Example

```aethel
# This program is correct but may not verify
solve complex_logic {
    # Very complex mathematical proof
    # May exceed solver timeout
    # Aethel rejects (incomplete)
}
```

## Decidability

### Decidable Properties

Aethel can always decide these properties:

1. **Arithmetic constraints** - Always decidable
2. **Conservation laws** - Always decidable
3. **Type safety** - Always decidable
4. **Overflow/underflow** - Always decidable

### Undecidable Properties

Some properties are undecidable in general:

1. **Halting problem** - Cannot always determine if program terminates
2. **Equivalence** - Cannot always determine if two programs are equivalent

**Aethel's approach**: Use timeouts and approximations for undecidable properties.

## Verification Complexity

### Time Complexity

| Property | Complexity | Notes |
|----------|-----------|-------|
| Constraint checking | O(n) | Linear in constraints |
| Conservation checking | O(n) | Linear in variables |
| Symbolic execution | O(2^n) | Exponential in branches |
| SMT solving | NP-complete | Worst case |

### Space Complexity

| Component | Complexity | Notes |
|-----------|-----------|-------|
| AST storage | O(n) | Linear in program size |
| Symbolic state | O(n) | Linear in variables |
| Proof certificate | O(n) | Linear in proof steps |

### Practical Performance

Most Aethel programs verify in **10-100ms**:

- Simple programs: <10ms
- Medium programs: 10-50ms
- Complex programs: 50-100ms
- Very complex: 100ms-1s

## Advanced Techniques

### 1. Abstraction

Simplify complex programs for verification:

```aethel
solve abstraction_example {
    # Abstract away implementation details
    # Focus on high-level properties
    
    balance = abstract_balance()
    withdrawal = abstract_withdrawal()
    
    assert withdrawal <= balance
    
    # Verify abstract model
}
```

### 2. Compositional Verification

Verify components independently:

```aethel
solve component_1 {
    # Verify component 1
    conserve property_1
}

solve component_2 {
    # Verify component 2
    conserve property_2
}

# Compose verified components
solve system {
    component_1()
    component_2()
    
    # System properties follow from component properties
}
```

### 3. Assume-Guarantee Reasoning

Make assumptions about environment:

```aethel
solve assume_guarantee {
    # Assume: input is valid
    assume input > 0
    
    # Guarantee: output is valid
    output = process(input)
    
    guarantee output > 0
}
```

## Limitations

### 1. Timeout Limits

Complex proofs may timeout:

```python
config = JudgeConfig(timeout=30)  # 30 second limit
```

### 2. Solver Limitations

SMT solvers have limitations:

- Non-linear arithmetic is hard
- Floating-point is approximate
- Some theories are undecidable

### 3. Specification Burden

Verification requires specifications:

```aethel
# Need to specify what "correct" means
solve example {
    # Without assertions, nothing to verify
    x = x + 1
    
    # With assertions, can verify
    assert x > 0
}
```

## Best Practices

### 1. Write Clear Specifications

```aethel
# Good: Clear specification
solve clear_spec {
    balance = 1000
    withdrawal = 100
    
    # Explicit constraints
    assert withdrawal > 0
    assert withdrawal <= balance
    
    balance = balance - withdrawal
    
    # Explicit conservation
    conserve balance >= 0
}

# Bad: Unclear specification
solve unclear_spec {
    balance = 1000
    withdrawal = 100
    
    balance = balance - withdrawal
    # What properties should hold?
}
```

### 2. Use Incremental Verification

```aethel
solve incremental {
    # Verify step by step
    
    # Step 1
    x = 100
    assert x > 0
    
    # Step 2
    y = x + 50
    assert y > x
    
    # Step 3
    z = y * 2
    assert z > y
}
```

### 3. Leverage Proof Certificates

```python
# Generate certificate
result = judge.verify(program)
certificate = result.proof.to_certificate()

# Save for audit
with open("proof.json", "w") as f:
    json.dump(certificate, f)

# Verify independently later
is_valid = verify_certificate(certificate)
```

## Research Directions

### Current Research

1. **Faster SMT solving** - Improve verification speed
2. **Better abstractions** - Handle more complex programs
3. **Machine learning** - Learn verification strategies
4. **Parallel verification** - Verify components in parallel

### Future Features

1. **Loop invariants** - Automatic inference
2. **Recursive proofs** - Handle recursion
3. **Probabilistic verification** - Handle uncertainty
4. **Interactive proving** - User-guided proofs

## See Also

- [Language Reference](../language-reference/syntax.md)
- [Conservation Laws](../language-reference/conservation-laws.md)
- [Architecture](../architecture/system-overview.md)
- [API Reference](../api-reference/judge.md)

## References

1. **SMT Solving**: Barrett, C., et al. "Satisfiability Modulo Theories"
2. **Symbolic Execution**: King, J. "Symbolic Execution and Program Testing"
3. **Formal Methods**: Clarke, E., et al. "Model Checking"
4. **Conservation Laws**: Noether, E. "Invariant Variation Problems"
