# Design Document: Conservation Checker v1.3

## Overview

The Conservation Checker is a static analysis component that validates the fundamental law of conservation in financial transactions: the sum of all balance changes must equal zero. It operates as a pre-verification pass in the Judge system, analyzing verify blocks to detect violations before expensive Z3 solver calls.

The system works by:
1. Parsing verify blocks to identify balance change expressions
2. Extracting the magnitude and direction of each change
3. Computing the sum of all changes
4. Reporting violations with detailed diagnostics

This design integrates seamlessly with Aethel's existing architecture while adding minimal overhead.

## Architecture

### System Context

```
┌─────────────┐
│   Parser    │ ──> AST
└─────────────┘
       │
       ▼
┌─────────────────────────────┐
│         Judge               │
│  ┌───────────────────────┐  │
│  │ Conservation_Checker  │  │ ──> Violation Report (if failed)
│  └───────────────────────┘  │
│           │                 │
│           ▼ (if passed)     │
│  ┌───────────────────────┐  │
│  │    Z3_Solver          │  │ ──> Proof Result
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### Component Interaction Flow

1. **Parser** converts Aethel source to AST
2. **Judge** receives AST and invokes Conservation_Checker
3. **Conservation_Checker** analyzes verify blocks:
   - Identifies balance variables
   - Extracts change amounts
   - Validates conservation law
4. If conservation fails: Judge returns error immediately
5. If conservation passes: Judge proceeds to Z3 verification

### Integration Points

- **Input**: AST from Parser (specifically verify block nodes)
- **Output**: Either success (continue to Z3) or violation report (fail fast)
- **Location**: New module `aethel/core/conservation.py`
- **Invocation**: Called from `judge.py` before Z3 solver

## Components and Interfaces

### ConservationChecker Class

```python
class ConservationChecker:
    """
    Analyzes verify blocks to detect conservation violations.
    """
    
    def check_intent(self, intent_node: IntentNode) -> ConservationResult:
        """
        Check conservation for an entire intent.
        
        Args:
            intent_node: AST node representing an intent
            
        Returns:
            ConservationResult with status and details
        """
        pass
    
    def analyze_verify_block(self, verify_block: VerifyBlock) -> List[BalanceChange]:
        """
        Extract all balance changes from a verify block.
        
        Args:
            verify_block: AST node representing a verify block
            
        Returns:
            List of BalanceChange objects
        """
        pass
    
    def validate_conservation(self, changes: List[BalanceChange]) -> ConservationResult:
        """
        Validate that sum of changes equals zero.
        
        Args:
            changes: List of balance changes
            
        Returns:
            ConservationResult indicating pass/fail
        """
        pass
```

### BalanceChange Data Structure

```python
@dataclass
class BalanceChange:
    """Represents a single balance change in a transaction."""
    variable_name: str
    amount: Expr  # Symbolic expression (could be numeric or symbolic)
    line_number: int
    is_increase: bool  # True for gains, False for losses
    
    def to_signed_amount(self) -> Expr:
        """Convert to signed amount (positive for increase, negative for decrease)."""
        return self.amount if self.is_increase else -self.amount
```

### ConservationResult Data Structure

```python
@dataclass
class ConservationResult:
    """Result of conservation checking."""
    is_valid: bool
    changes: List[BalanceChange]
    violation_amount: Optional[Expr] = None
    error_message: Optional[str] = None
    
    def format_error(self) -> str:
        """Format a human-readable error message."""
        if self.is_valid:
            return "Conservation check passed"
        
        lines = ["❌ FAILED: Conservation violation detected"]
        for change in self.changes:
            sign = "+" if change.is_increase else "-"
            lines.append(f"   {change.variable_name}: {sign}{change.amount}")
        
        if self.violation_amount > 0:
            lines.append(f"   Total: {self.violation_amount} units created from nothing")
        else:
            lines.append(f"   Total: {abs(self.violation_amount)} units destroyed")
        
        return "\n".join(lines)
```

### Judge Integration

```python
# In aethel/core/judge.py

class Judge:
    def __init__(self):
        self.conservation_checker = ConservationChecker()
        # ... existing initialization
    
    def verify_intent(self, intent_node: IntentNode) -> VerificationResult:
        """Verify an intent with conservation checking."""
        
        # Step 1: Check conservation (fast pre-check)
        conservation_result = self.conservation_checker.check_intent(intent_node)
        
        if not conservation_result.is_valid:
            return VerificationResult(
                success=False,
                error=conservation_result.format_error(),
                proof=None
            )
        
        # Step 2: Proceed to Z3 verification (existing logic)
        return self._verify_with_z3(intent_node)
```

## Data Models

### AST Node Extensions

The existing Parser already produces AST nodes. We'll work with:

```python
# Existing AST structures (no modifications needed)

class VerifyBlock:
    """Represents a verify block in the AST."""
    statements: List[Statement]
    line_number: int

class BinaryOp:
    """Represents binary operations like ==, +, -, etc."""
    left: Expr
    op: str
    right: Expr
    line_number: int

class Variable:
    """Represents a variable reference."""
    name: str
    line_number: int
```

### Balance Change Detection Algorithm

The core algorithm for detecting balance changes:

```python
def extract_balance_change(self, statement: BinaryOp) -> Optional[BalanceChange]:
    """
    Extract balance change from a statement like:
    - sender_balance == old_sender_balance - 100
    - receiver_balance == old_receiver_balance + 200
    
    Returns None if statement doesn't represent a balance change.
    """
    
    # Must be an equality comparison
    if statement.op != "==":
        return None
    
    left = statement.left  # new value (e.g., sender_balance)
    right = statement.right  # expression (e.g., old_sender_balance - 100)
    
    # Check if right side is: old_variable ± amount
    if not isinstance(right, BinaryOp):
        return None
    
    if right.op not in ["+", "-"]:
        return None
    
    # Extract old variable and amount
    old_var = right.left
    amount = right.right
    
    # Verify naming convention: old_{variable}
    if not (isinstance(old_var, Variable) and old_var.name.startswith("old_")):
        return None
    
    # Extract variable name
    var_name = old_var.name[4:]  # Remove "old_" prefix
    
    # Determine if increase or decrease
    is_increase = (right.op == "+")
    
    return BalanceChange(
        variable_name=var_name,
        amount=amount,
        line_number=statement.line_number,
        is_increase=is_increase
    )
```

### Conservation Validation Algorithm

```python
def validate_conservation(self, changes: List[BalanceChange]) -> ConservationResult:
    """
    Validate conservation law: sum of all changes must equal zero.
    """
    
    if not changes:
        # No balance changes detected - skip conservation check
        return ConservationResult(is_valid=True, changes=[])
    
    # Compute sum of all signed changes
    total = sum(change.to_signed_amount() for change in changes)
    
    # Check if sum equals zero
    # For symbolic expressions, we use Z3 to check if total == 0 is always true
    if self._is_zero(total):
        return ConservationResult(is_valid=True, changes=changes)
    else:
        return ConservationResult(
            is_valid=False,
            changes=changes,
            violation_amount=total,
            error_message="Conservation violated: sum of changes != 0"
        )

def _is_zero(self, expr: Expr) -> bool:
    """Check if expression equals zero."""
    if isinstance(expr, (int, float)):
        return expr == 0
    
    # For symbolic expressions, use Z3 to check
    solver = z3.Solver()
    solver.add(expr != 0)
    return solver.check() == z3.unsat  # unsat means expr must be 0
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Complete Balance Change Detection

*For any* verify block containing balance comparisons, the Conservation_Checker should identify all balance variables and correctly calculate each balance change as (new_value - old_value), tracking all changes independently.

**Validates: Requirements 1.1, 1.2, 1.3**

### Property 2: Conservation Law Validation

*For any* set of balance changes, the Conservation_Checker should mark the transaction as valid if and only if the sum of all changes equals zero, and should report a violation otherwise.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 3: Complete Violation Reporting

*For any* conservation violation, the error report should include the exact amount created or destroyed, list all balance changes with their amounts and line numbers, and correctly indicate whether money was created (positive sum) or destroyed (negative sum).

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

### Property 4: No Balance Changes Skip

*For any* verify block containing no balance changes, the Conservation_Checker should skip conservation checking and return success.

**Validates: Requirements 1.4**

### Property 5: Z3 Short-Circuit on Violation

*For any* intent with a conservation violation, the Judge should fail verification immediately without calling Z3, and the conservation error should appear in the verification output.

**Validates: Requirements 4.2, 4.4**

### Property 6: Z3 Continuation on Success

*For any* intent with valid conservation, the Judge should proceed to Z3 verification normally.

**Validates: Requirements 4.3**

### Property 7: Caching Consistency

*For any* intent analyzed multiple times, the Conservation_Checker should return identical results on subsequent analyses (caching should not affect correctness).

**Validates: Requirements 5.4**

### Property 8: Arithmetic Expression Handling

*For any* balance change expression using arithmetic operations (+, -, *, /, or nested combinations), the Conservation_Checker should correctly extract and evaluate the net balance change amount.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 9: Multi-Party Conservation

*For any* transaction involving N parties (where N ≥ 2), the Conservation_Checker should validate that the sum of all balance changes equals zero, regardless of the transaction pattern (two-party transfer, split, consolidation, or complex multi-party).

**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

### Property 10: Graceful Error Handling

*For any* malformed balance expression or ambiguous variable type, the Conservation_Checker should report a clear, actionable error message without crashing.

**Validates: Requirements 8.1, 8.2**

## Error Handling

### Error Categories

1. **Conservation Violations** (Expected Errors)
   - Sum of changes ≠ 0
   - Single-account transactions
   - Unbalanced multi-party transactions
   - Action: Report violation with detailed breakdown

2. **Parse Errors** (User Errors)
   - Malformed balance expressions
   - Invalid arithmetic operations
   - Missing old_ prefix
   - Action: Report syntax error with line number

3. **Type Errors** (User Errors)
   - Ambiguous variable types
   - Non-numeric balance changes
   - Action: Request type annotations

4. **Internal Errors** (System Errors)
   - Z3 solver failures
   - AST traversal errors
   - Action: Provide debugging information and stack trace

### Error Message Format

```
❌ FAILED: Conservation violation detected
   sender_balance: -100 (line 15)
   receiver_balance: +200 (line 16)
   ────────────────────────────────
   Total: 100 units created from nothing
   
   Hint: In a valid transaction, the sum of all balance 
   changes must equal zero. Check your arithmetic.
```

### Error Recovery Strategy

- **Fail Fast**: Stop verification immediately on conservation violations
- **No Partial Results**: Either all checks pass or verification fails
- **Clear Attribution**: Always include line numbers and variable names
- **Actionable Hints**: Suggest fixes when possible

## Testing Strategy

### Dual Testing Approach

The Conservation Checker will be validated using both unit tests and property-based tests:

- **Unit Tests**: Verify specific examples, edge cases, and error conditions
- **Property Tests**: Verify universal properties across all inputs
- Both approaches are complementary and necessary for comprehensive coverage

### Unit Testing Focus

Unit tests will cover:
- Specific example transactions (simple transfer, split, consolidation)
- Edge cases (zero amounts, single account, empty verify blocks)
- Error conditions (malformed expressions, type errors, parser failures)
- Integration points (Judge invocation, Z3 interaction)

Unit tests should be minimal - property-based tests handle covering lots of inputs. Focus unit tests on concrete examples that demonstrate correct behavior and integration between components.

### Property-Based Testing Configuration

- **Library**: Hypothesis (Python property-based testing library)
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each test references its design document property
- **Tag Format**: `# Feature: conservation-checker, Property N: [property text]`

### Property Test Coverage

Each correctness property will be implemented as a single property-based test:

1. **Property 1 Test**: Generate random verify blocks with balance changes, verify all are detected
2. **Property 2 Test**: Generate random balanced and unbalanced transactions, verify conservation validation
3. **Property 3 Test**: Generate random violations, verify error reports are complete
4. **Property 4 Test**: Generate random non-balance verify blocks, verify skipping behavior
5. **Property 5 Test**: Generate random violations, verify Z3 is not called
6. **Property 6 Test**: Generate random valid transactions, verify Z3 is called
7. **Property 7 Test**: Generate random intents, analyze multiple times, verify results are identical
8. **Property 8 Test**: Generate random arithmetic expressions, verify correct extraction
9. **Property 9 Test**: Generate random N-party transactions, verify conservation validation
10. **Property 10 Test**: Generate random malformed inputs, verify error messages are clear

### Test Data Generation Strategy

For property-based tests, we'll generate:
- **Random balance amounts**: Integers from -1000 to 1000
- **Random variable names**: Valid identifiers (e.g., "account_1", "balance_x")
- **Random arithmetic operations**: +, -, *, / with valid operands
- **Random transaction patterns**: 2-party, 3-party, N-party (N up to 10)
- **Random violations**: Unbalanced amounts with known sums

### Integration Testing

Integration tests will verify:
- End-to-end flow: Parser → Judge → Conservation_Checker → Z3
- Error propagation: Conservation errors appear in final output
- Performance: Conservation checking adds < 10% overhead (benchmark test)

### Test Organization

```
tests/
├── unit/
│   ├── test_conservation_checker.py      # Unit tests for ConservationChecker
│   ├── test_balance_change.py            # Unit tests for BalanceChange
│   └── test_judge_integration.py         # Unit tests for Judge integration
├── property/
│   ├── test_conservation_properties.py   # Property-based tests (Properties 1-10)
│   └── generators.py                     # Hypothesis generators for test data
└── integration/
    └── test_end_to_end.py                # Full pipeline integration tests
```

## Performance Considerations

### Algorithmic Complexity

- **Balance Detection**: O(n) where n = number of statements in verify block
- **Conservation Validation**: O(m) where m = number of balance changes
- **Overall**: O(n) per intent verification

### Optimization Strategies

1. **Early Exit**: Skip conservation checking if no balance changes detected
2. **Caching**: Cache analysis results for identical verify blocks
3. **Lazy Evaluation**: Only compute violation details if conservation fails
4. **Symbolic Simplification**: Simplify expressions before Z3 evaluation

### Performance Targets

- **Overhead**: < 10% increase in total verification time
- **Memory**: O(m) where m = number of balance changes (minimal)
- **Scalability**: Linear scaling with program size

## Implementation Notes

### Phase 1: Core Implementation
- Implement ConservationChecker class
- Implement balance change detection algorithm
- Implement conservation validation algorithm
- Add basic error reporting

### Phase 2: Judge Integration
- Integrate with Judge.verify_intent()
- Add short-circuit logic for violations
- Propagate errors to verification output

### Phase 3: Advanced Features
- Add caching for repeated analyses
- Enhance error messages with hints
- Optimize symbolic expression handling

### Phase 4: Testing & Validation
- Write unit tests for core functionality
- Write property-based tests for all properties
- Run integration tests with existing Aethel programs
- Benchmark performance impact
