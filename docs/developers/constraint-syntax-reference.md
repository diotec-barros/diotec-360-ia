# Constraint Syntax Reference - RVC v2 Hardening

## Version: v1.9.2 "The Hardening"
## Audience: Developers

---

## Overview

RVC v2 hardening introduces **hard-reject parsing** for transaction constraints. All constraints must use explicitly supported AST node types. Unsupported syntax will trigger `UnsupportedConstraintError` and reject the transaction.

**Design Principle**: "Unknown = Rejected". The system will never silently ignore constraints.

---

## Supported AST Node Types

### Arithmetic Operations

| Operator | AST Node | Example | Description |
|----------|----------|---------|-------------|
| `+` | `ast.Add` | `balance + 100` | Addition |
| `-` | `ast.Sub` | `balance - 50` | Subtraction |
| `*` | `ast.Mult` | `price * quantity` | Multiplication |
| `/` | `ast.Div` | `total / count` | Division |

### Comparison Operations

| Operator | AST Node | Example | Description |
|----------|----------|---------|-------------|
| `==` | `ast.Eq` | `status == 1` | Equality |
| `!=` | `ast.NotEq` | `balance != 0` | Inequality |
| `<` | `ast.Lt` | `balance < 1000` | Less than |
| `<=` | `ast.LtE` | `balance <= 1000` | Less than or equal |
| `>` | `ast.Gt` | `balance > 0` | Greater than |
| `>=` | `ast.GtE` | `balance >= 0` | Greater than or equal |

### Logical Operations

| Operator | AST Node | Example | Description |
|----------|----------|---------|-------------|
| `and` | `ast.And` | `balance >= 0 and balance <= 1000` | Logical AND |
| `or` | `ast.Or` | `status == 1 or status == 2` | Logical OR |
| `not` | `ast.Not` | `not (balance < 0)` | Logical NOT |

### Values

| Type | AST Node | Example | Description |
|------|----------|---------|-------------|
| Number | `ast.Num`, `ast.Constant` | `100`, `3.14` | Numeric constants |
| Variable | `ast.Name` | `balance`, `price` | Variable references |

---

## Constraint Examples

### Valid Constraints

```python
# Simple comparison
"balance >= 0"

# Range check
"balance >= 0 and balance <= 1000"

# Multiple conditions
"balance >= 0 and status == 1 and price > 0"

# Arithmetic in constraints
"balance + deposit >= minimum"

# Complex expressions
"(balance - withdrawal) >= 0 and (balance - withdrawal) <= limit"

# Logical operations
"status == 1 or status == 2 or status == 3"

# Negation
"not (balance < 0)"
```

### Invalid Constraints (Will Be Rejected)

```python
# ✗ Bitwise operations NOT supported
"balance | flags == 0"  # UnsupportedConstraintError: BitOr

# ✗ Bitwise AND NOT supported
"balance & mask == 0"  # UnsupportedConstraintError: BitAnd

# ✗ Bit shifts NOT supported
"value << 2 == 8"  # UnsupportedConstraintError: LShift

# ✗ Modulo NOT supported (yet)
"balance % 10 == 0"  # UnsupportedConstraintError: Mod

# ✗ Power NOT supported
"value ** 2 == 100"  # UnsupportedConstraintError: Pow

# ✗ Floor division NOT supported
"total // count == 5"  # UnsupportedConstraintError: FloorDiv

# ✗ String operations NOT supported
"name + '_suffix'"  # UnsupportedConstraintError: (strings not supported)

# ✗ List/Dict operations NOT supported
"balance in [100, 200, 300]"  # UnsupportedConstraintError: In

# ✗ Function calls NOT supported
"abs(balance) > 0"  # UnsupportedConstraintError: Call

# ✗ Subscripting NOT supported
"balances[0] > 0"  # UnsupportedConstraintError: Subscript
```

---

## Migration Guide

### Replacing Unsupported Operations

#### Bitwise OR → Logical OR

```python
# Before (INVALID):
"status | flags == 0"

# After (VALID):
"status == 0 or flags == 0"
```

#### Bitwise AND → Logical AND

```python
# Before (INVALID):
"status & flags == 1"

# After (VALID):
"status == 1 and flags == 1"
```

#### Modulo → Multiple Conditions

```python
# Before (INVALID):
"balance % 100 == 0"

# After (VALID - check specific values):
"balance == 0 or balance == 100 or balance == 200 or balance == 300"

# Or use arithmetic:
"(balance / 100) * 100 == balance"  # Check if divisible by 100
```

#### Power → Multiplication

```python
# Before (INVALID):
"value ** 2 == 100"

# After (VALID):
"value * value == 100"
```

#### Absolute Value → Conditional

```python
# Before (INVALID):
"abs(balance) > 0"

# After (VALID):
"balance > 0 or balance < 0"  # Non-zero check
```

---

## Best Practices

### 1. Validate Constraints Before Submission

```python
from diotec360.core.judge import AethelJudge

def validate_constraint(constraint_str: str) -> bool:
    """Validate constraint syntax before submitting transaction"""
    try:
        judge = AethelJudge({})
        judge._parse_constraint(constraint_str)
        return True
    except UnsupportedConstraintError as e:
        print(f"Invalid constraint: {e}")
        return False

# Usage
if validate_constraint("balance >= 0"):
    # Submit transaction
    pass
```

### 2. Use Constraint Templates

```python
# Define reusable constraint templates
CONSTRAINT_TEMPLATES = {
    "non_negative": "balance >= 0",
    "range_check": "balance >= {min} and balance <= {max}",
    "status_active": "status == 1",
    "sufficient_funds": "balance >= amount",
}

# Use templates
constraint = CONSTRAINT_TEMPLATES["range_check"].format(min=0, max=1000)
```

### 3. Test Constraints

```python
import pytest
from diotec360.core.integrity_panic import UnsupportedConstraintError

def test_valid_constraints():
    """Test that valid constraints are accepted"""
    valid = [
        "balance >= 0",
        "balance >= 0 and balance <= 1000",
        "status == 1 or status == 2",
    ]
    
    for constraint in valid:
        assert validate_constraint(constraint)

def test_invalid_constraints():
    """Test that invalid constraints are rejected"""
    invalid = [
        "balance | flags == 0",  # Bitwise OR
        "balance & mask == 0",   # Bitwise AND
        "balance % 10 == 0",     # Modulo
    ]
    
    for constraint in invalid:
        with pytest.raises(UnsupportedConstraintError):
            judge._parse_constraint(constraint)
```

### 4. Document Constraints

```python
class Transaction:
    """
    Transaction with conservation constraints
    
    Supported constraint syntax:
    - Arithmetic: +, -, *, /
    - Comparison: ==, !=, <, <=, >, >=
    - Logical: and, or, not
    - Values: numbers, variables
    
    Example constraints:
    - "balance >= 0"
    - "balance >= 0 and balance <= 1000"
    - "status == 1 or status == 2"
    """
    
    def __init__(self, constraints: list[str]):
        self.constraints = constraints
```

---

## Error Handling

### Catching UnsupportedConstraintError

```python
from diotec360.core.integrity_panic import UnsupportedConstraintError

try:
    tx = atomic_layer.begin_transaction(tx_id)
    tx.constraints = ["balance | flags == 0"]  # Invalid
    atomic_layer.commit_transaction(tx)
except UnsupportedConstraintError as e:
    print(f"Constraint error: {e.violation_type}")
    print(f"Details: {e.details}")
    print(f"Recovery hint: {e.recovery_hint}")
    
    # Extract node type that caused the error
    node_type = e.details["node_type"]
    supported = e.details["supported_types"]
    
    print(f"Unsupported node: {node_type}")
    print(f"Supported nodes: {supported}")
    
    # Provide user-friendly error message
    print("Please rewrite your constraint using supported syntax.")
```

### User-Friendly Error Messages

```python
def format_constraint_error(e: UnsupportedConstraintError) -> str:
    """Format error for end users"""
    node_type = e.details["node_type"]
    
    suggestions = {
        "BitOr": "Use 'or' instead of '|'",
        "BitAnd": "Use 'and' instead of '&'",
        "Mod": "Use division and multiplication to check divisibility",
        "Pow": "Use repeated multiplication instead of '**'",
    }
    
    suggestion = suggestions.get(node_type, "See documentation for supported syntax")
    
    return f"Unsupported operation '{node_type}' in constraint. {suggestion}"
```

---

## Performance Considerations

### Constraint Complexity

- **Simple constraints** (< 5 operations): ~0.1ms parsing time
- **Medium constraints** (5-20 operations): ~0.5ms parsing time
- **Complex constraints** (> 20 operations): ~2ms parsing time

### Optimization Tips

1. **Simplify constraints**:
   ```python
   # Slow (many operations):
   "balance >= 0 and balance <= 1000 and status == 1 and price > 0 and quantity > 0"
   
   # Faster (split into multiple constraints):
   ["balance >= 0 and balance <= 1000", "status == 1", "price > 0", "quantity > 0"]
   ```

2. **Avoid redundant checks**:
   ```python
   # Redundant:
   "balance >= 0 and balance > -1"
   
   # Simplified:
   "balance >= 0"
   ```

3. **Use constants**:
   ```python
   # Slower (repeated calculation):
   "balance >= minimum + buffer"
   
   # Faster (pre-calculate):
   min_balance = minimum + buffer
   f"balance >= {min_balance}"
   ```

---

## Future Extensions

The following operations may be supported in future versions:

- **Modulo** (`%`): For divisibility checks
- **Floor Division** (`//`): For integer division
- **Power** (`**`): For exponential constraints
- **Absolute Value** (`abs()`): For magnitude checks
- **Min/Max** (`min()`, `max()`): For range operations

Check the release notes for updates to supported syntax.

---

## Complete AST Node Whitelist

```python
# From aethel/core/judge.py
SUPPORTED_AST_NODES = {
    # Binary operations
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    
    # Unary operations
    ast.UnaryOp,
    ast.USub,  # Unary minus
    ast.UAdd,  # Unary plus
    
    # Comparison operations
    ast.Compare,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    
    # Boolean operations
    ast.BoolOp,
    ast.And,
    ast.Or,
    ast.Not,
    
    # Values
    ast.Num,      # Python 3.7 and earlier
    ast.Constant, # Python 3.8+
    ast.Name,     # Variables
}
```

---

## Support

For questions about constraint syntax:

1. Check this reference guide
2. Review examples in `docs/examples/`
3. Test constraints with validation function
4. Consult API documentation
5. Contact development team

---

*"Hard-reject parsing: Unknown = Rejected. The system will never silently ignore your constraints."*  
— RVC v2 Hardening Design Principle
