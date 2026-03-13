# Conservation Laws in Aethel

## Overview

Conservation laws are mathematical invariants that must hold throughout program execution. Aethel automatically verifies these laws and generates proofs of their correctness.

## What is a Conservation Law?

A conservation law states that a certain quantity remains constant despite transformations. In financial systems, the most important conservation law is:

**Money Conservation**: The total amount of money in a closed system remains constant.

## Syntax

```aethel
conserve <expression>
```

The expression must evaluate to `true` after program execution.

## Basic Examples

### Simple Transfer

```aethel
solve simple_transfer {
    alice = 1000
    bob = 500
    total_before = alice + bob
    
    # Transfer 100 from alice to bob
    alice = alice - 100
    bob = bob + 100
    
    # Verify conservation
    conserve alice + bob == total_before
}
```

### Multi-Party Transfer

```aethel
solve multi_party {
    alice = 1000
    bob = 500
    charlie = 300
    total = alice + bob + charlie
    
    # Multiple transfers
    alice = alice - 200
    bob = bob + 100
    charlie = charlie + 100
    
    # Conservation holds
    conserve alice + bob + charlie == total
}
```

## Advanced Conservation

### Weighted Conservation

```aethel
solve weighted {
    # Different asset types with exchange rates
    usd = 1000
    eur = 500
    eur_to_usd_rate = 1.1
    
    # Total value in USD
    total_usd = usd + (eur * eur_to_usd_rate)
    
    # Exchange 100 EUR to USD
    eur = eur - 100
    usd = usd + (100 * eur_to_usd_rate)
    
    # Conservation in USD terms
    conserve usd + (eur * eur_to_usd_rate) == total_usd
}
```

### Conditional Conservation

```aethel
solve conditional {
    balance = 1000
    fee = 10
    withdrawal = 100
    
    # Total before (including fee)
    total_before = balance
    
    # Withdrawal with fee
    balance = balance - withdrawal - fee
    collected_fees = fee
    
    # Conservation: money either stays in balance or goes to fees
    conserve balance + withdrawal + collected_fees == total_before
}
```

## Conservation in Parallel Execution

### Independent Transfers

```aethel
solve parallel_conservation {
    atomic batch {
        # Transfer 1
        alice = 1000
        bob = 500
        alice = alice - 100
        bob = bob + 100
        
        # Transfer 2 (independent)
        charlie = 800
        dave = 200
        charlie = charlie - 50
        dave = dave + 50
    }
    
    # Each subsystem conserves independently
    conserve alice + bob == 1500
    conserve charlie + dave == 1000
}
```

### Global Conservation

```aethel
solve global_conservation {
    # Multiple accounts
    accounts = [1000, 500, 300, 200]
    total_before = sum(accounts)
    
    # Complex transfers
    accounts[0] = accounts[0] - 100
    accounts[1] = accounts[1] + 50
    accounts[2] = accounts[2] + 30
    accounts[3] = accounts[3] + 20
    
    # Global conservation
    conserve sum(accounts) == total_before
}
```

## Mathematical Proofs

### How Aethel Proves Conservation

Aethel generates formal proofs using:

1. **Symbolic Execution** - Track all variable transformations
2. **Arithmetic Verification** - Verify all operations preserve totals
3. **Path Analysis** - Ensure conservation holds on all execution paths
4. **Theorem Proving** - Generate mathematical proof certificates

### Proof Example

For this program:

```aethel
solve proof_example {
    alice = 1000
    bob = 500
    
    alice = alice - 100
    bob = bob + 100
    
    conserve alice + bob == 1500
}
```

Aethel generates:

```
Proof of Conservation:
  Initial state: alice₀ = 1000, bob₀ = 500
  Total₀ = alice₀ + bob₀ = 1500
  
  Transformation:
    alice₁ = alice₀ - 100 = 900
    bob₁ = bob₀ + 100 = 600
  
  Final state: alice₁ = 900, bob₁ = 600
  Total₁ = alice₁ + bob₁ = 1500
  
  Proof: Total₀ = Total₁ ✓
  
  Mathematical verification:
    ∀ transfer t: (alice₀ + bob₀) = (alice₀ - t) + (bob₀ + t)
    Proven by: Arithmetic identity (a + b = (a - t) + (b + t))
```

## Common Patterns

### Pattern 1: Simple Transfer

```aethel
solve pattern_transfer {
    sender = S
    receiver = R
    amount = A
    
    assert amount > 0
    assert amount <= sender
    
    sender = sender - amount
    receiver = receiver + amount
    
    conserve sender + receiver == S + R
}
```

### Pattern 2: Transfer with Fee

```aethel
solve pattern_fee {
    sender = S
    receiver = R
    fee_account = F
    amount = A
    fee = FEE
    
    assert amount + fee <= sender
    
    sender = sender - amount - fee
    receiver = receiver + amount
    fee_account = fee_account + fee
    
    conserve sender + receiver + fee_account == S + R + F
}
```

### Pattern 3: Multi-Hop Transfer

```aethel
solve pattern_multihop {
    alice = A
    bob = B
    charlie = C
    
    # Alice -> Bob -> Charlie
    amount1 = 100
    amount2 = 50
    
    alice = alice - amount1
    bob = bob + amount1 - amount2
    charlie = charlie + amount2
    
    conserve alice + bob + charlie == A + B + C
}
```

### Pattern 4: Batch Processing

```aethel
solve pattern_batch {
    accounts = [A1, A2, A3, A4]
    total_before = sum(accounts)
    
    # Process multiple transactions
    atomic batch {
        accounts[0] = accounts[0] - 100
        accounts[1] = accounts[1] + 100
        
        accounts[2] = accounts[2] - 50
        accounts[3] = accounts[3] + 50
    }
    
    conserve sum(accounts) == total_before
}
```

## Conservation Violations

### Example 1: Money Creation

```aethel
solve violation_creation {
    alice = 1000
    bob = 500
    
    alice = alice - 100
    bob = bob + 200  # Oops! Created 100 units
    
    conserve alice + bob == 1500  # FAILS!
}
```

Error:
```
✗ Conservation law violated
  Expected: 1500
  Actual: 1600
  Difference: +100 (money created)
```

### Example 2: Money Destruction

```aethel
solve violation_destruction {
    alice = 1000
    bob = 500
    
    alice = alice - 100
    bob = bob + 50  # Oops! Lost 50 units
    
    conserve alice + bob == 1500  # FAILS!
}
```

Error:
```
✗ Conservation law violated
  Expected: 1500
  Actual: 1450
  Difference: -50 (money destroyed)
```

### Example 3: Arithmetic Error

```aethel
solve violation_arithmetic {
    balance = 1000
    
    # Integer division loses precision
    half = balance // 2
    other_half = balance // 2
    
    conserve half + other_half == balance  # FAILS if balance is odd!
}
```

## Best Practices

### 1. Always Specify Conservation

```aethel
# Good: Explicit conservation
solve good {
    total_before = alice + bob
    # ... transfers ...
    conserve alice + bob == total_before
}

# Bad: No conservation check
solve bad {
    # ... transfers ...
    # How do we know money is conserved?
}
```

### 2. Use Meaningful Total Variables

```aethel
# Good: Clear intent
solve clear {
    total_system_value = sum(all_accounts)
    # ... operations ...
    conserve sum(all_accounts) == total_system_value
}

# Bad: Magic numbers
solve unclear {
    # ... operations ...
    conserve sum(all_accounts) == 5000  # Where did 5000 come from?
}
```

### 3. Document Complex Conservation

```aethel
solve documented {
    # Total value across all currencies in USD terms
    total_usd = usd + (eur * eur_rate) + (gbp * gbp_rate)
    
    # ... currency exchanges ...
    
    # Conservation: total USD value unchanged
    conserve usd + (eur * eur_rate) + (gbp * gbp_rate) == total_usd
}
```

### 4. Test Edge Cases

```aethel
solve edge_cases {
    balance = 1000
    
    # Edge case: zero transfer
    transfer = 0
    balance = balance - transfer
    conserve balance == 1000
    
    # Edge case: full balance transfer
    transfer2 = balance
    balance = balance - transfer2
    conserve balance == 0
}
```

## Performance Considerations

Conservation checking has minimal overhead:

- **Compile-time**: Symbolic analysis adds ~10ms
- **Runtime**: Arithmetic verification adds ~1μs per conserve statement
- **Proof generation**: Typically <100ms for complex programs

For high-performance scenarios, conservation checks can be optimized:

```aethel
solve optimized {
    # Batch conservation checks
    atomic batch {
        # ... many operations ...
    }
    
    # Single conservation check at end
    conserve total_after == total_before
}
```

## Supported Constraint Syntax

### Overview

Diotec360 v1.9.2 implements **hard-reject parsing** (RVC2-004) to prevent security bypasses through unsupported syntax. Any constraint using unsupported operations will be **immediately rejected** with a clear error message.

### Supported Operations

#### Arithmetic Operators

| Operator | Symbol | Example | Description |
|----------|--------|---------|-------------|
| Addition | `+` | `a + b` | Add two values |
| Subtraction | `-` | `a - b` | Subtract values |
| Multiplication | `*` | `a * b` | Multiply values |
| Division | `/` | `a / b` | Divide values |
| Modulo | `%` | `a % b` | Remainder after division |

#### Comparison Operators

| Operator | Symbol | Example | Description |
|----------|--------|---------|-------------|
| Equal | `==` | `a == b` | Values are equal |
| Not Equal | `!=` | `a != b` | Values are not equal |
| Less Than | `<` | `a < b` | a is less than b |
| Less or Equal | `<=` | `a <= b` | a is less than or equal to b |
| Greater Than | `>` | `a > b` | a is greater than b |
| Greater or Equal | `>=` | `a >= b` | a is greater than or equal to b |

#### Unary Operators

| Operator | Symbol | Example | Description |
|----------|--------|---------|-------------|
| Unary Minus | `-` | `-a` | Negate value |
| Unary Plus | `+` | `+a` | Positive value (identity) |

#### Literals and Variables

| Type | Example | Description |
|------|---------|-------------|
| Integer | `42`, `1000` | Whole numbers |
| Float | `3.14`, `0.5` | Decimal numbers |
| Variable | `alice`, `balance` | Named variables |

### Supported Constraint Examples

#### Simple Arithmetic

```aethel
solve arithmetic {
    a = 10
    b = 20
    
    # Supported: Basic arithmetic
    conserve a + b == 30
    conserve a * 2 == 20
    conserve b - a == 10
    conserve b / a == 2
    conserve b % 3 == 2
}
```

#### Comparisons

```aethel
solve comparisons {
    balance = 1000
    threshold = 500
    
    # Supported: All comparison operators
    assert balance > threshold
    assert balance >= 1000
    assert balance != 0
    assert threshold < balance
    assert threshold <= 500
    assert balance == 1000
}
```

#### Complex Expressions

```aethel
solve complex {
    alice = 1000
    bob = 500
    fee = 10
    
    # Supported: Nested arithmetic
    conserve (alice - 100) + (bob + 100) == alice + bob
    
    # Supported: Multiple operations
    conserve alice + bob - fee == 1490
    
    # Supported: Parentheses for precedence
    conserve (alice + bob) * 2 == 3000
}
```

#### Unary Operations

```aethel
solve unary {
    value = 100
    
    # Supported: Unary minus
    conserve -value == -100
    
    # Supported: Unary plus
    conserve +value == 100
    
    # Supported: Negation in expressions
    conserve value + (-50) == 50
}
```

### Unsupported Operations

The following operations are **NOT supported** and will cause immediate transaction rejection:

#### Bitwise Operations (Not Supported)

```aethel
solve unsupported_bitwise {
    a = 10
    b = 5
    
    # ❌ REJECTED: Bitwise OR
    conserve a | b == 15
    
    # ❌ REJECTED: Bitwise AND
    conserve a & b == 0
    
    # ❌ REJECTED: Bitwise XOR
    conserve a ^ b == 15
    
    # ❌ REJECTED: Left shift
    conserve a << 1 == 20
    
    # ❌ REJECTED: Right shift
    conserve a >> 1 == 5
}
```

#### Logical Operations (Not Supported)

```aethel
solve unsupported_logical {
    a = true
    b = false
    
    # ❌ REJECTED: Logical AND
    conserve a and b == false
    
    # ❌ REJECTED: Logical OR
    conserve a or b == true
    
    # ❌ REJECTED: Logical NOT
    conserve not a == false
}
```

#### Advanced Operations (Not Supported)

```aethel
solve unsupported_advanced {
    a = 10
    
    # ❌ REJECTED: Power/exponentiation
    conserve a ** 2 == 100
    
    # ❌ REJECTED: Floor division
    conserve a // 3 == 3
    
    # ❌ REJECTED: Function calls
    conserve abs(a) == 10
    
    # ❌ REJECTED: List operations
    conserve a in [1, 2, 3] == false
}
```

### Error Messages

When an unsupported operation is used, Aethel provides clear error messages:

```
🔒 HARD-REJECT - Unsupported constraint: BitOr

Violation Type: UNSUPPORTED_AST_NODE
Node Type: BitOr
Supported Types: BinOp, UnaryOp, Compare, Num, Constant, Name, Add, Sub, Mult, Div, Mod, Eq, NotEq, Lt, LtE, Gt, GtE, USub, UAdd

Recovery Hint: Rewrite constraint using supported syntax. See documentation.
```

### Migration Guide

If you have constraints using unsupported operations, here's how to rewrite them:

#### Example 1: Bitwise OR → Arithmetic

```aethel
# Before (unsupported)
conserve flags | mask == result

# After (supported)
# Use arithmetic operations or separate checks
conserve flags + mask == result  # If appropriate for your use case
```

#### Example 2: Logical AND → Multiple Assertions

```aethel
# Before (unsupported)
conserve balance > 0 and balance < 1000

# After (supported)
assert balance > 0
assert balance < 1000
```

#### Example 3: Power → Multiplication

```aethel
# Before (unsupported)
conserve value ** 2 == 100

# After (supported)
conserve value * value == 100
```

#### Example 4: Floor Division → Regular Division

```aethel
# Before (unsupported)
conserve amount // 2 == 5

# After (supported)
conserve amount / 2 == 5
```

### Why Hard-Reject?

Aethel implements hard-reject parsing for security reasons:

1. **No Silent Failures**: Unsupported operations are explicitly rejected, not silently ignored
2. **Security Guarantee**: Prevents constraint bypass through exotic syntax
3. **Clear Feedback**: Developers get immediate, actionable error messages
4. **Formal Verification**: Only operations with proven semantics are allowed

This approach follows the principle: **"Better to reject than to lie"**

### Extending Support

If you need support for additional operations, please:

1. Open an issue on GitHub describing your use case
2. Provide examples of constraints that would benefit
3. Explain why existing operations cannot express your constraint

The Diotec360 Team carefully evaluates each extension to ensure:
- Formal semantics are well-defined
- Z3 can efficiently verify the operation
- Security properties are preserved

## See Also

- [Language Syntax](syntax.md)
- [Proof Generation](../advanced/formal-verification.md)
- [Examples](../examples/banking.md)
- [API Reference](../api-reference/conservation-validator.md)
