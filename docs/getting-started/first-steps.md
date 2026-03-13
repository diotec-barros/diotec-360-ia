# First Steps with Aethel

## Introduction

This guide introduces the core concepts of Aethel and helps you build a solid foundation for writing verified financial programs.

## Core Philosophy

Aethel is built on three principles:

1. **Trust Through Transparency** - Mathematical proofs provide verifiable correctness
2. **Conservation by Default** - Financial invariants are enforced automatically
3. **Security First** - Vulnerabilities are detected before execution

## Basic Concepts

### 1. Solve Blocks

Every Aethel program uses `solve` blocks for verification:

```aethel
solve my_program {
    # Your code here
}
```

The `solve` block tells Aethel to:
- Verify all constraints
- Check conservation laws
- Generate mathematical proofs
- Detect security issues

### 2. Variables and Types

Aethel supports standard data types:

```aethel
solve types_demo {
    # Numbers
    integer_value = 100
    decimal_value = 99.99
    
    # Booleans
    is_valid = true
    is_expired = false
    
    # Strings
    account_id = "ACC-12345"
    
    # Lists
    balances = [1000, 2000, 3000]
}
```

### 3. Assertions

Use `assert` to specify constraints:

```aethel
solve constraints {
    balance = 1000
    withdrawal = 150
    
    # Constraint: withdrawal must not exceed balance
    assert withdrawal <= balance
    
    # Constraint: withdrawal must be positive
    assert withdrawal > 0
    
    # Execute withdrawal
    balance = balance - withdrawal
}
```

If any assertion fails, Aethel rejects the program before execution.

### 4. Conservation Laws

Use `conserve` to specify invariants:

```aethel
solve conservation {
    account_a = 1000
    account_b = 500
    total_before = account_a + account_b
    
    # Transfer
    transfer_amount = 200
    account_a = account_a - transfer_amount
    account_b = account_b + transfer_amount
    
    # Conservation: total must remain constant
    conserve account_a + account_b == total_before
}
```

Aethel generates a mathematical proof that conservation holds.

### 5. Arithmetic Operations

Standard arithmetic is supported:

```aethel
solve arithmetic {
    a = 100
    b = 50
    
    sum = a + b          # Addition: 150
    difference = a - b   # Subtraction: 50
    product = a * b      # Multiplication: 5000
    quotient = a / b     # Division: 2
    remainder = a % b    # Modulo: 0
    power = a ** 2       # Exponentiation: 10000
}
```

### 6. Comparison Operators

```aethel
solve comparisons {
    x = 100
    y = 50
    
    assert x > y         # Greater than
    assert x >= y        # Greater than or equal
    assert y < x         # Less than
    assert y <= x        # Less than or equal
    assert x == 100      # Equal
    assert x != y        # Not equal
}
```

### 7. Logical Operators

```aethel
solve logic {
    balance = 1000
    withdrawal = 100
    is_active = true
    
    # AND operator
    assert (withdrawal > 0) and (withdrawal <= balance)
    
    # OR operator
    assert is_active or (balance == 0)
    
    # NOT operator
    assert not (balance < 0)
}
```

## Building Your First Real Program

Let's build a simple banking system:

```aethel
solve banking_system {
    # Account balances
    checking = 5000
    savings = 10000
    
    # Transaction parameters
    transfer_to_savings = 1000
    withdrawal = 500
    
    # Constraints
    assert transfer_to_savings > 0
    assert transfer_to_savings <= checking
    assert withdrawal > 0
    assert withdrawal <= checking - transfer_to_savings
    
    # Execute transactions
    checking = checking - transfer_to_savings
    savings = savings + transfer_to_savings
    checking = checking - withdrawal
    
    # Conservation: total money preserved
    total_initial = 15000
    conserve checking + savings == total_initial - withdrawal
    
    # Final state verification
    assert checking >= 0
    assert savings >= 0
}
```

Run it:

```bash
aethel run banking_system.ae
```

Output:

```
✓ All constraints satisfied
✓ Conservation law verified
✓ Proof generated successfully

Final state:
  checking: 3500
  savings: 11000
  withdrawn: 500
  
Mathematical proof: Conservation verified across 3 operations
```

## Understanding Proofs

When Aethel generates a proof, it verifies:

1. **Constraint Satisfaction** - All `assert` statements hold
2. **Conservation Laws** - All `conserve` statements are proven
3. **Arithmetic Safety** - No overflow, underflow, or division by zero
4. **State Consistency** - Final state is mathematically sound

## Error Handling

Aethel catches errors before execution:

### Example: Constraint Violation

```aethel
solve error_demo {
    balance = 100
    withdrawal = 150
    
    assert withdrawal <= balance  # This will fail!
    
    balance = balance - withdrawal
}
```

Output:

```
✗ Constraint violation detected
  Line 5: assert withdrawal <= balance
  Reason: 150 > 100
  
Program rejected. No execution performed.
```

### Example: Conservation Violation

```aethel
solve conservation_error {
    alice = 1000
    bob = 500
    
    alice = alice - 100
    bob = bob + 50  # Oops! Should be +100
    
    conserve alice + bob == 1500  # This will fail!
}
```

Output:

```
✗ Conservation law violated
  Line 8: conserve alice + bob == 1500
  Expected: 1500
  Actual: 1450
  Difference: -50
  
Program rejected. Conservation violation detected.
```

## Best Practices

### 1. Always Use Assertions

```aethel
# Good: Explicit constraints
solve good_practice {
    balance = 1000
    amount = 100
    
    assert amount > 0
    assert amount <= balance
    
    balance = balance - amount
}

# Bad: No constraints
solve bad_practice {
    balance = 1000
    amount = 100
    
    balance = balance - amount  # What if amount is negative?
}
```

### 2. Specify Conservation Laws

```aethel
# Good: Explicit conservation
solve good_conservation {
    total_before = account_a + account_b
    
    # ... transfers ...
    
    conserve account_a + account_b == total_before
}

# Bad: No conservation check
solve bad_conservation {
    # ... transfers ...
    # How do we know money wasn't created or destroyed?
}
```

### 3. Use Meaningful Names

```aethel
# Good: Clear names
solve clear_names {
    customer_balance = 1000
    withdrawal_amount = 100
    minimum_balance = 50
    
    assert withdrawal_amount <= customer_balance - minimum_balance
}

# Bad: Unclear names
solve unclear_names {
    x = 1000
    y = 100
    z = 50
    
    assert y <= x - z  # What does this mean?
}
```

## Next Steps

You now understand the basics of Aethel! Continue learning:

- [Language Reference](../language-reference/syntax.md) - Complete syntax guide
- [Examples](../examples/banking.md) - Real-world use cases
- [API Reference](../api-reference/judge.md) - Programmatic integration
- [Advanced Topics](../advanced/formal-verification.md) - Deep dive into verification

## Practice Exercises

Try these exercises to reinforce your learning:

### Exercise 1: Payroll System

Create a program that distributes payroll to multiple employees while preserving total funds.

### Exercise 2: Interest Calculator

Build a compound interest calculator with constraints on rates and time periods.

### Exercise 3: Multi-Currency Exchange

Implement a currency exchange system with conservation across different currencies.

Solutions are available in the [examples directory](../examples/).

## Getting Help

- [GitHub Issues](https://github.com/diotec360/diotec360/issues)
- [Community Forum](https://community.aethel.dev)
- [Discord](https://discord.gg/aethel)

For enterprise support: [diotec360.com/aethel](https://diotec360.com/aethel)
