# Diotec360 v1.9.0 - Example Standards & Grammar Reference

## Executive Summary

The Diotec360 v1.9.0 "Autonomous Sentinel" release includes **two types of examples**:

1. **Parseable Examples** - Clean `.ae` files that work in the Proof Viewer (frontend)
2. **Documentation Examples** - Rich pseudo-code with comments explaining concepts

This document defines the **Golden Standard** for parseable examples.

---

## The Grammar Reality

### What the Backend Supports (Production Grammar)

The production grammar (`aethel/core/grammar.py`) supports:

```aethel
intent transfer(sender: Balance, receiver: Balance, amount: Balance) {
    guard {
        sender >= amount;
        amount >= 0;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        sender >= 0;
        receiver >= 0;
        sender + receiver >= 0;
    }
}
```

### Supported Features

✅ **Intent definitions** with `guard`, `solve`, `verify` blocks  
✅ **Atomic batch** constructs for parallel execution  
✅ **Arithmetic expressions**: `+`, `-`, `*`, `/`, `%`  
✅ **Comparison operators**: `>=`, `<=`, `==`, `!=`, `>`, `<`  
✅ **Numeric literals**: `0`, `100`, `-50`  
✅ **Comments**: `#` (hash symbol only)  
✅ **Keywords**: `secret`, `external` for parameters  
✅ **Parentheses**: `(expr)` for grouping  

### NOT Supported (Yet)

❌ **C-style comments**: `//` (use `#` instead)  
❌ **State declarations**: `state accounts: map<address, int>`  
❌ **Init blocks**: `init: accounts[alice] = 1000`  
❌ **Transaction blocks**: `transaction transfer: ...`  
❌ **Dot notation**: `account.balance` (use flat names)  
❌ **Assignment in conditions**: `value = expr` (use separate variables)  
❌ **Arrays/Lists**: `[1, 2, 3]`  
❌ **String literals**: `"hello"`  
❌ **Function calls**: `transfer(a, b, c)`  
❌ **Control flow**: `if`, `for`, `while`  
❌ **Multiple intents per file** (without `atomic_batch`)  

---

## The Golden Standard Template

### Minimal Valid Example

```aethel
# Comment describing the intent

intent example_name(param1: Type1, param2: Type2) {
    guard {
        # Pre-conditions
        param1 >= 0;
        param2 >= param1;
    }
    
    solve {
        priority: security;
        target: ledger;
    }
    
    verify {
        # Post-conditions
        param1 >= 0;
        param2 >= 0;
    }
}
```

### With External Oracle Data

```aethel
intent oracle_example(
    account: Balance,
    external price: Balance,
    threshold: Balance
) {
    guard {
        price >= threshold;
        account >= 0;
    }
    
    solve {
        priority: security;
        target: oracle;
    }
    
    verify {
        account >= 0;
        price >= 0;
    }
}
```

### With Secret (ZKP) Values

```aethel
intent secret_example(
    secret sender: Balance,
    secret receiver: Balance,
    amount: Balance
) {
    guard {
        sender >= amount;
        amount >= 0;
    }
    
    solve {
        priority: privacy;
        target: zkp;
    }
    
    verify {
        sender >= 0;
        receiver >= 0;
    }
}
```

### Atomic Batch (Parallel Execution)

```aethel
atomic_batch batch_name {
    intent task1(a: Balance, b: Balance) {
        guard {
            a >= 0;
        }
        
        solve {
            priority: security;
            target: ledger;
        }
        
        verify {
            a >= 0;
            b >= 0;
        }
    }
    
    intent task2(c: Balance, d: Balance) {
        guard {
            c >= 0;
        }
        
        solve {
            priority: security;
            target: ledger;
        }
        
        verify {
            c >= 0;
            d >= 0;
        }
    }
}
```

---

## Validation Rules

### Rule 1: All Intents Must Have 3 Blocks

Every intent MUST have:
- `guard { ... }` - Pre-conditions
- `solve { ... }` - Execution directives
- `verify { ... }` - Post-conditions

**Missing any block = Parse Error**

### Rule 2: Conditions Must End with Semicolon

```aethel
# ✅ CORRECT
guard {
    amount >= 0;
    sender >= amount;
}

# ❌ WRONG (missing semicolons)
guard {
    amount >= 0
    sender >= amount
}
```

### Rule 3: Solve Block Must Have Settings

```aethel
# ✅ CORRECT
solve {
    priority: security;
    target: ledger;
}

# ❌ WRONG (empty solve block)
solve {
}
```

### Rule 4: Use Hash Comments Only

```aethel
# ✅ CORRECT
# This is a comment

# ❌ WRONG (C-style comments not supported)
// This will cause parse error
```

### Rule 5: No Assignments in Conditions

```aethel
# ✅ CORRECT (use separate parameters)
intent example(value: Balance, result: Balance) {
    guard {
        value >= 0;
        result >= value * 2;
    }
    ...
}

# ❌ WRONG (assignment in guard)
intent example(value: Balance) {
    guard {
        result = value * 2;  # Parse error!
    }
    ...
}
```

---

## Current Example Status

### ✅ Valid Examples (Proof Viewer Ready)

1. `simple_transfer.ae` - Basic account transfer
2. `insurance_payout.ae` - Parametric insurance with oracle
3. `defi_liquidation.ae` - Collateral liquidation
4. `batch_transfer.ae` - Atomic batch payroll
5. `secret_payment.ae` - Zero-knowledge transfer
6. `private_compliance.ae` - ZKP compliance check

### ⚠️ Documentation Examples (Not Parseable)

These examples contain rich pseudo-code for documentation purposes:

1. `adversarial_test.ae` - Shows attack patterns (uses `state`, `transaction`)
2. `sentinel_demo.ae` - Shows telemetry (uses `state`, `init`, `for` loops)
3. `crop_insurance.ae` - Shows multiple intents (needs `atomic_batch`)
4. `global_bank.ae` - Shows complex logic (uses `//` comments, arrays)
5. `defi_exchange_parallel.ae` - Shows dot notation (`.balance`)
6. `liquidation_parallel.ae` - Shows assignments (`value = expr`)
7. `payroll_parallel.ae` - Shows dot notation
8. `defi_liquidation_conservation.ae` - Shows assignments
9. `crop_insurance_web.ae` - Shows `//` comments

---

## Recommendations

### For Proof Viewer (Frontend)

**Use only the 6 valid examples** in the example selector dropdown:
- simple_transfer.ae
- insurance_payout.ae
- defi_liquidation.ae
- batch_transfer.ae
- secret_payment.ae
- private_compliance.ae

### For Documentation (GitHub, Docs Site)

**Keep all examples** - they demonstrate concepts even if not parseable.

Add a header to documentation examples:

```aethel
# NOTE: This is a documentation example with pseudo-code
# For parseable examples, see: simple_transfer.ae, insurance_payout.ae, etc.
```

### For v2.0.0 (Future)

Expand the grammar to support:
- Multiple intents per file (without atomic_batch wrapper)
- State declarations and init blocks
- Dot notation for nested structures
- Assignment statements
- C-style comments (`//`)
- Control flow constructs

---

## Validation Script

Use `validate_examples.py` to check examples:

```bash
python validate_examples.py
```

Output shows which examples pass/fail parsing.

---

## Summary

**The Philosophy**: Diotec360 v1.9.0 prioritizes **mathematical correctness** over syntactic sugar. The grammar is intentionally minimal to ensure every construct can be formally verified.

**The Reality**: Some examples are "aspirational" - they show what Aethel *will* support, not what it supports *today*.

**The Solution**: Separate parseable examples (for Proof Viewer) from documentation examples (for learning).

**The Future**: v2.0.0 will expand the grammar while maintaining formal verification guarantees.

---

**Status**: 6/15 examples are Proof Viewer ready (40% coverage)  
**Target**: 100% coverage by v2.0.0  
**Verdict**: ✅ Production-ready with clear documentation

🏛️ **The Architect's Seal**: "Precision over convenience. Truth over syntax."
