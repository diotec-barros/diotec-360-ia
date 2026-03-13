# Conservation Validator API Reference

## Overview

The Conservation Validator verifies that conservation laws hold in Aethel programs. It provides specialized checking for financial invariants and generates conservation proofs.

## Installation

```python
from diotec360.core.conservation import ConservationValidator
```

## Class: ConservationValidator

### Constructor

```python
ConservationValidator(config: Optional[ValidatorConfig] = None)
```

Creates a new ConservationValidator instance.

**Parameters:**
- `config` (ValidatorConfig, optional): Configuration options

**Example:**
```python
from diotec360.core.conservation import ConservationValidator, ValidatorConfig

config = ValidatorConfig(
    tolerance=1e-10,
    strict_mode=True
)
validator = ConservationValidator(config)
```

### Methods

#### validator.validate()

```python
validate(
    program: str,
    variables: Optional[List[str]] = None
) -> ValidationResult
```

Validates conservation laws in a program.

**Parameters:**
- `program` (str): Aethel source code
- `variables` (List[str], optional): Specific variables to check

**Returns:**
- `ValidationResult`: Validation result with conservation status

**Example:**
```python
program = """
solve transfer {
    alice = 1000
    bob = 500
    
    alice = alice - 100
    bob = bob + 100
    
    conserve alice + bob == 1500
}
"""

result = validator.validate(program)
print(f"Conservation holds: {result.is_conserved}")
```

#### validator.check_invariant()

```python
check_invariant(
    initial_state: Dict[str, float],
    final_state: Dict[str, float],
    invariant: str
) -> bool
```

Checks if an invariant holds between two states.

**Parameters:**
- `initial_state` (Dict[str, float]): Initial variable values
- `final_state` (Dict[str, float]): Final variable values
- `invariant` (str): Invariant expression

**Returns:**
- `bool`: Whether invariant holds

**Example:**
```python
initial = {"alice": 1000, "bob": 500}
final = {"alice": 900, "bob": 600}

holds = validator.check_invariant(
    initial,
    final,
    "alice + bob == 1500"
)
print(f"Invariant holds: {holds}")
```

#### validator.generate_proof()

```python
generate_proof(
    program: str,
    conservation_law: str
) -> ConservationProof
```

Generates a detailed conservation proof.

**Parameters:**
- `program` (str): Aethel source code
- `conservation_law` (str): Conservation law to prove

**Returns:**
- `ConservationProof`: Detailed proof

**Example:**
```python
proof = validator.generate_proof(
    program,
    "alice + bob == 1500"
)

print(f"Proof steps: {len(proof.steps)}")
for step in proof.steps:
    print(f"  {step.description}")
```

#### validator.find_violations()

```python
find_violations(program: str) -> List[ConservationViolation]
```

Finds all conservation violations in a program.

**Parameters:**
- `program` (str): Aethel source code

**Returns:**
- `List[ConservationViolation]`: List of violations

**Example:**
```python
violations = validator.find_violations(program)

if violations:
    print("Conservation violations found:")
    for v in violations:
        print(f"  Line {v.line}: {v.message}")
        print(f"    Expected: {v.expected}")
        print(f"    Actual: {v.actual}")
else:
    print("No violations found")
```

## Data Classes

### ValidatorConfig

Configuration for the ConservationValidator.

```python
@dataclass
class ValidatorConfig:
    tolerance: float = 1e-10
    strict_mode: bool = True
    enable_proofs: bool = True
    check_overflow: bool = True
    check_underflow: bool = True
```

**Fields:**
- `tolerance`: Numerical tolerance for comparisons (default: 1e-10)
- `strict_mode`: Enable strict validation (default: True)
- `enable_proofs`: Generate conservation proofs (default: True)
- `check_overflow`: Check for arithmetic overflow (default: True)
- `check_underflow`: Check for arithmetic underflow (default: True)

### ValidationResult

Result of conservation validation.

```python
@dataclass
class ValidationResult:
    is_conserved: bool
    total_before: float
    total_after: float
    difference: float
    variables: List[str]
    proof: Optional[ConservationProof]
    violations: List[ConservationViolation]
    warnings: List[str]
```

**Fields:**
- `is_conserved`: Whether conservation holds
- `total_before`: Total value before execution
- `total_after`: Total value after execution
- `difference`: Difference (should be ~0)
- `variables`: Variables checked
- `proof`: Conservation proof (if enabled)
- `violations`: List of violations
- `warnings`: List of warnings

### ConservationProof

Proof that conservation holds.

```python
@dataclass
class ConservationProof:
    theorem: str
    steps: List[ProofStep]
    initial_state: Dict[str, float]
    final_state: Dict[str, float]
    total_before: float
    total_after: float
    is_valid: bool
```

**Fields:**
- `theorem`: Conservation theorem being proven
- `steps`: List of proof steps
- `initial_state`: Initial variable values
- `final_state`: Final variable values
- `total_before`: Total before execution
- `total_after`: Total after execution
- `is_valid`: Whether proof is valid

### ConservationViolation

A conservation law violation.

```python
@dataclass
class ConservationViolation:
    line: int
    message: str
    expected: float
    actual: float
    difference: float
    variables: List[str]
```

**Fields:**
- `line`: Line number of violation
- `message`: Violation description
- `expected`: Expected total value
- `actual`: Actual total value
- `difference`: Difference between expected and actual
- `variables`: Variables involved

## Complete Example

```python
from diotec360.core.conservation import ConservationValidator, ValidatorConfig

# Configure validator
config = ValidatorConfig(
    tolerance=1e-10,
    strict_mode=True,
    enable_proofs=True
)

validator = ConservationValidator(config)

# Program with conservation law
program = """
solve multi_transfer {
    # Initial balances
    alice = 1000
    bob = 500
    charlie = 300
    
    # Total before
    total_before = alice + bob + charlie
    
    # Multiple transfers
    transfer_1 = 100
    transfer_2 = 50
    
    assert transfer_1 <= alice
    assert transfer_2 <= bob
    
    # Execute transfers
    alice = alice - transfer_1
    bob = bob + transfer_1 - transfer_2
    charlie = charlie + transfer_2
    
    # Conservation law
    conserve alice + bob + charlie == total_before
}
"""

# Validate conservation
result = validator.validate(program)

if result.is_conserved:
    print("✓ Conservation verified")
    print(f"Total before: {result.total_before}")
    print(f"Total after: {result.total_after}")
    print(f"Difference: {result.difference}")
    
    # Display proof
    if result.proof:
        print(f"\nConservation Proof:")
        print(f"Theorem: {result.proof.theorem}")
        print(f"\nSteps:")
        for i, step in enumerate(result.proof.steps, 1):
            print(f"  {i}. {step.description}")
        print(f"\nInitial state: {result.proof.initial_state}")
        print(f"Final state: {result.proof.final_state}")
else:
    print("✗ Conservation violated")
    for violation in result.violations:
        print(f"\nViolation at line {violation.line}:")
        print(f"  {violation.message}")
        print(f"  Expected: {violation.expected}")
        print(f"  Actual: {violation.actual}")
        print(f"  Difference: {violation.difference}")

# Check for warnings
if result.warnings:
    print(f"\nWarnings:")
    for warning in result.warnings:
        print(f"  - {warning}")
```

## Advanced Usage

### Custom Invariants

```python
# Check custom invariant
initial = {
    "usd": 1000,
    "eur": 500,
    "eur_rate": 1.1
}

final = {
    "usd": 1055,
    "eur": 450,
    "eur_rate": 1.1
}

# Check USD-equivalent conservation
invariant = "usd + (eur * eur_rate) == 1550"

holds = validator.check_invariant(initial, final, invariant)
print(f"USD-equivalent conserved: {holds}")
```

### Weighted Conservation

```python
program = """
solve weighted_conservation {
    # Different asset types
    gold_oz = 100
    silver_oz = 1000
    
    # Exchange rates (in USD)
    gold_price = 2000
    silver_price = 25
    
    # Total value in USD
    total_usd = (gold_oz * gold_price) + (silver_oz * silver_price)
    
    # Exchange 10 oz gold for silver
    gold_oz = gold_oz - 10
    silver_oz = silver_oz + (10 * gold_price / silver_price)
    
    # Conservation in USD terms
    conserve (gold_oz * gold_price) + (silver_oz * silver_price) == total_usd
}
"""

result = validator.validate(program)
```

### Batch Validation

```python
programs = [program1, program2, program3]

results = []
for program in programs:
    result = validator.validate(program)
    results.append(result)

# Summary
conserved_count = sum(1 for r in results if r.is_conserved)
print(f"Conservation rate: {conserved_count}/{len(results)}")
```

## Error Handling

```python
from diotec360.core.conservation import ConservationValidator, ValidationError

validator = ConservationValidator()

try:
    result = validator.validate(program)
except ValidationError as e:
    print(f"Validation error: {e}")
except ValueError as e:
    print(f"Invalid input: {e}")
```

## Numerical Precision

The validator handles floating-point precision:

```python
# Configure tolerance
config = ValidatorConfig(tolerance=1e-10)
validator = ConservationValidator(config)

# This will pass despite floating-point errors
program = """
solve precision {
    a = 0.1 + 0.2
    b = 0.3
    
    # 0.1 + 0.2 != 0.3 in floating point!
    # But validator uses tolerance
    conserve a == b
}
"""

result = validator.validate(program)
# result.is_conserved == True (within tolerance)
```

## Performance Tips

### 1. Disable Proofs for Performance

```python
config = ValidatorConfig(enable_proofs=False)
validator = ConservationValidator(config)

# Faster validation without proof generation
result = validator.validate(program)
```

### 2. Specify Variables to Check

```python
# Check only specific variables
result = validator.validate(
    program,
    variables=["alice", "bob"]  # Ignore other variables
)
```

### 3. Batch Processing

```python
# Reuse validator instance
validator = ConservationValidator()

for program in programs:
    result = validator.validate(program)
```

## Integration Example

```python
from diotec360.core.judge import Judge
from diotec360.core.runtime import Runtime
from diotec360.core.conservation import ConservationValidator

# Create components
judge = Judge()
runtime = Runtime()
validator = ConservationValidator()

# Full verification and execution pipeline
def execute_with_conservation(program: str):
    # Step 1: Verify program
    verification = judge.verify(program)
    if not verification.is_valid:
        return {"error": "Verification failed"}
    
    # Step 2: Check conservation
    conservation = validator.validate(program)
    if not conservation.is_conserved:
        return {"error": "Conservation violated"}
    
    # Step 3: Execute
    execution = runtime.execute(program)
    if not execution.success:
        return {"error": "Execution failed"}
    
    return {
        "success": True,
        "final_state": execution.final_state,
        "conservation_proof": conservation.proof
    }

# Use pipeline
result = execute_with_conservation(program)
```

## See Also

- [Judge API](judge.md)
- [Runtime API](runtime.md)
- [Conservation Laws](../language-reference/conservation-laws.md)
- [Examples](../examples/banking.md)
