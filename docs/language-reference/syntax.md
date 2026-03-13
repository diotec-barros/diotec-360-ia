# Aethel Language Reference

## Overview

This document provides a complete reference for the Diotec360 programming language syntax and semantics.

## Program Structure

### Solve Blocks

The fundamental unit of Aethel programs is the `solve` block:

```aethel
solve block_name {
    # Statements
}
```

**Syntax:**
```
solve <identifier> {
    <statement>*
}
```

**Semantics:**
- Executes all statements in order
- Verifies all constraints
- Generates mathematical proofs
- Checks conservation laws

### Comments

```aethel
# Single-line comment

solve example {
    # This is a comment
    x = 100  # Inline comment
}
```

## Data Types

### Numbers

**Integers:**
```aethel
solve integers {
    count = 42
    negative = -10
    large = 1000000
}
```

**Decimals:**
```aethel
solve decimals {
    price = 99.99
    rate = 0.05
    pi = 3.14159
}
```

### Booleans

```aethel
solve booleans {
    is_active = true
    is_expired = false
}
```

### Strings

```aethel
solve strings {
    account_id = "ACC-12345"
    name = "Alice"
    message = "Transfer complete"
}
```

### Lists

```aethel
solve lists {
    balances = [1000, 2000, 3000]
    names = ["Alice", "Bob", "Charlie"]
    mixed = [100, "text", true]
}
```

## Variables

### Declaration and Assignment

```aethel
solve variables {
    # Declaration with assignment
    balance = 1000
    
    # Reassignment
    balance = balance - 100
    
    # Multiple assignments
    x = y = z = 0
}
```

### Variable Names

**Valid identifiers:**
- Must start with a letter or underscore
- Can contain letters, digits, and underscores
- Case-sensitive

```aethel
solve naming {
    account_balance = 1000      # Valid
    _private_var = 50           # Valid
    balance2 = 200              # Valid
    
    # Invalid:
    # 2balance = 100            # Cannot start with digit
    # account-balance = 100     # Cannot contain hyphen
}
```

## Operators

### Arithmetic Operators

```aethel
solve arithmetic {
    a = 100
    b = 50
    
    sum = a + b              # Addition: 150
    difference = a - b       # Subtraction: 50
    product = a * b          # Multiplication: 5000
    quotient = a / b         # Division: 2.0
    integer_div = a // b     # Integer division: 2
    remainder = a % b        # Modulo: 0
    power = a ** 2           # Exponentiation: 10000
    negation = -a            # Unary minus: -100
}
```

### Comparison Operators

```aethel
solve comparisons {
    x = 100
    y = 50
    
    assert x > y             # Greater than
    assert x >= 100          # Greater than or equal
    assert y < x             # Less than
    assert y <= 50           # Less than or equal
    assert x == 100          # Equal
    assert x != y            # Not equal
}
```

### Logical Operators

```aethel
solve logic {
    a = true
    b = false
    
    result1 = a and b        # Logical AND: false
    result2 = a or b         # Logical OR: true
    result3 = not a          # Logical NOT: false
    
    # Short-circuit evaluation
    assert (x > 0) and (y / x > 1)  # y/x only evaluated if x > 0
}
```

### Operator Precedence

From highest to lowest:

1. `**` (exponentiation)
2. `-` (unary minus), `not`
3. `*`, `/`, `//`, `%`
4. `+`, `-`
5. `<`, `<=`, `>`, `>=`, `==`, `!=`
6. `and`
7. `or`

Use parentheses to override precedence:

```aethel
solve precedence {
    result1 = 2 + 3 * 4      # 14 (multiplication first)
    result2 = (2 + 3) * 4    # 20 (parentheses first)
}
```

## Constraints

### Assert Statements

```aethel
solve assertions {
    balance = 1000
    withdrawal = 150
    
    # Simple assertion
    assert withdrawal > 0
    
    # Complex assertion
    assert (withdrawal > 0) and (withdrawal <= balance)
    
    # Assertion with message (future feature)
    # assert balance >= 0, "Balance cannot be negative"
}
```

**Semantics:**
- Evaluated before program execution
- If any assertion fails, program is rejected
- No side effects

### Conservation Laws

```aethel
solve conservation {
    alice = 1000
    bob = 500
    total_before = alice + bob
    
    # Transfer
    alice = alice - 100
    bob = bob + 100
    
    # Conservation check
    conserve alice + bob == total_before
}
```

**Semantics:**
- Verified after program execution
- Generates mathematical proof
- Must hold for all execution paths

## Control Flow

### Conditional Execution (Future Feature)

```aethel
# Planned syntax
solve conditionals {
    balance = 1000
    withdrawal = 150
    
    if withdrawal <= balance {
        balance = balance - withdrawal
        status = "success"
    } else {
        status = "insufficient funds"
    }
}
```

### Loops (Future Feature)

```aethel
# Planned syntax
solve loops {
    balances = [1000, 2000, 3000]
    total = 0
    
    for balance in balances {
        total = total + balance
    }
    
    conserve total == 6000
}
```

## Parallel Execution

### Atomic Batch

```aethel
solve parallel {
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
    
    # Each transfer preserves conservation
    conserve alice + bob == 1500
    conserve charlie + dave == 1000
}
```

**Semantics:**
- All operations in batch execute atomically
- Either all succeed or all fail
- Independent operations can execute in parallel
- Dependencies are automatically detected

## Built-in Functions

### Mathematical Functions

```aethel
solve math_functions {
    # Absolute value
    abs_value = abs(-100)        # 100
    
    # Minimum and maximum
    min_value = min(10, 20, 5)   # 5
    max_value = max(10, 20, 5)   # 20
    
    # Rounding
    rounded = round(3.7)         # 4
    floor_value = floor(3.7)     # 3
    ceil_value = ceil(3.2)       # 4
    
    # Power and root
    square = pow(5, 2)           # 25
    sqrt_value = sqrt(25)        # 5.0
}
```

### List Functions

```aethel
solve list_functions {
    numbers = [1, 2, 3, 4, 5]
    
    # Length
    count = len(numbers)         # 5
    
    # Sum
    total = sum(numbers)         # 15
    
    # Average
    average = avg(numbers)       # 3.0
    
    # Access
    first = numbers[0]           # 1
    last = numbers[-1]           # 5
}
```

## Proof Syntax

### Proof Annotations

```aethel
solve annotated {
    balance = 1000
    
    # Proof annotation (documentation only)
    # @proof: balance >= 0 (invariant)
    
    withdrawal = 100
    assert withdrawal <= balance
    
    balance = balance - withdrawal
    
    # @proof: balance >= 0 (preserved)
}
```

### Proof Generation

Aethel automatically generates proofs for:

1. **Constraint satisfaction** - All assertions hold
2. **Conservation laws** - All conserve statements proven
3. **Arithmetic safety** - No overflow/underflow
4. **State consistency** - Final state is valid

## Standard Library

### Financial Functions

```aethel
import financial

solve interest_calc {
    principal = 10000
    rate = 0.05
    time = 2
    
    # Simple interest
    interest = financial.simple_interest(principal, rate, time)
    
    # Compound interest
    compound = financial.compound_interest(principal, rate, time, 12)
    
    assert interest > 0
    assert compound > interest
}
```

### Risk Functions

```aethel
import risk

solve risk_assessment {
    portfolio_value = 100000
    volatility = 0.15
    confidence = 0.95
    
    # Value at Risk
    var = risk.value_at_risk(portfolio_value, volatility, confidence)
    
    assert var > 0
    assert var < portfolio_value
}
```

## Error Handling

### Compile-Time Errors

```aethel
solve compile_error {
    x = 100
    y = x + z  # Error: 'z' is not defined
}
```

### Runtime Errors

```aethel
solve runtime_error {
    x = 100
    y = 0
    z = x / y  # Error: Division by zero
}
```

### Constraint Violations

```aethel
solve constraint_error {
    balance = 100
    withdrawal = 150
    
    assert withdrawal <= balance  # Error: Constraint violated
}
```

## Best Practices

### 1. Use Descriptive Names

```aethel
# Good
solve clear_naming {
    customer_balance = 1000
    withdrawal_amount = 100
}

# Bad
solve unclear_naming {
    x = 1000
    y = 100
}
```

### 2. Always Specify Constraints

```aethel
# Good
solve with_constraints {
    balance = 1000
    amount = 100
    
    assert amount > 0
    assert amount <= balance
    
    balance = balance - amount
}

# Bad
solve without_constraints {
    balance = 1000
    amount = 100
    
    balance = balance - amount  # What if amount is invalid?
}
```

### 3. Use Conservation Laws

```aethel
# Good
solve with_conservation {
    total_before = account_a + account_b
    
    # ... transfers ...
    
    conserve account_a + account_b == total_before
}

# Bad
solve without_conservation {
    # ... transfers ...
    # No verification that money is conserved
}
```

### 4. Document Complex Logic

```aethel
solve documented {
    # Calculate compound interest with monthly compounding
    principal = 10000
    annual_rate = 0.05
    years = 2
    compounds_per_year = 12
    
    # Formula: A = P(1 + r/n)^(nt)
    rate_per_period = annual_rate / compounds_per_year
    total_periods = years * compounds_per_year
    final_amount = principal * (1 + rate_per_period) ** total_periods
    
    assert final_amount > principal
}
```

## Language Grammar

### EBNF Notation

```ebnf
program ::= solve_block+

solve_block ::= "solve" identifier "{" statement* "}"

statement ::= assignment
            | assertion
            | conservation
            | atomic_batch

assignment ::= identifier "=" expression

assertion ::= "assert" expression

conservation ::= "conserve" expression

atomic_batch ::= "atomic" "batch" "{" statement* "}"

expression ::= term (("+"|"-") term)*

term ::= factor (("*"|"/"|"//"|"%") factor)*

factor ::= ("+" | "-") factor
         | primary ("**" factor)?

primary ::= number
          | string
          | boolean
          | identifier
          | "(" expression ")"
          | function_call
          | list

function_call ::= identifier "(" (expression ("," expression)*)? ")"

list ::= "[" (expression ("," expression)*)? "]"

identifier ::= letter (letter | digit | "_")*

number ::= digit+ ("." digit+)?

string ::= '"' character* '"'

boolean ::= "true" | "false"
```

## Example Library

Explore our comprehensive collection of real-world examples:

### Banking Examples
- [Safe Banking Transfer](../../examples/banking/safe_banking.ae) - Secure transfer with conservation proof
- [Payroll Distribution](../../examples/banking/payroll.ae) - Multi-employee payroll processing
- [Multi-Currency Transfer](../../examples/banking/multi_currency_transfer.ae) - Currency exchange with value conservation

### DeFi Examples
- [DeFi Liquidation](../../examples/defi/defi_liquidation.ae) - Collateralized loan liquidation
- [Flash Loan Shield](../../examples/defi/flash_loan_shield.ae) - Flash loan with exploit protection
- [Portfolio Rebalancing](../../examples/defi/portfolio_rebalancing.ae) - Crypto portfolio rebalancing

### Compliance Examples
- [Private Compliance](../../examples/compliance/private_compliance.ae) - Zero-knowledge compliance checks
- [Audit Trail](../../examples/compliance/audit_trail.ae) - Immutable audit trail generation
- [Regulatory Reporting](../../examples/compliance/regulatory_reporting.ae) - Aggregated reporting with proofs

### Parallel Execution Examples
- [Atomic Batch](../../examples/parallel/atomic_batch.ae) - Batch processing with atomicity
- [Parallel Transfers](../../examples/parallel/parallel_transfers.ae) - Concurrent transfers with conflict detection
- [Concurrent Settlement](../../examples/parallel/concurrent_settlement.ae) - Multi-party settlement

## See Also

- [Getting Started](../getting-started/quickstart.md)
- [API Reference](../api-reference/judge.md)
- [Advanced Topics](../advanced/formal-verification.md)
