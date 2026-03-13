# Runtime API Reference

## Overview

The Runtime executes verified Aethel programs and manages program state. It provides a safe execution environment with built-in security features.

## Installation

```python
from diotec360.core.runtime import Runtime
```

## Class: Runtime

### Constructor

```python
Runtime(config: Optional[RuntimeConfig] = None)
```

Creates a new Runtime instance.

**Parameters:**
- `config` (RuntimeConfig, optional): Configuration options for the Runtime

**Example:**
```python
from diotec360.core.runtime import Runtime, RuntimeConfig

config = RuntimeConfig(
    enable_sandboxing=True,
    max_memory_mb=512,
    max_execution_time=10
)
runtime = Runtime(config)
```

### Methods

#### runtime.execute()

```python
execute(program: str) -> ExecutionResult
```

Executes a verified Aethel program.

**Parameters:**
- `program` (str): Aethel source code

**Returns:**
- `ExecutionResult`: Execution result with final state

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

result = runtime.execute(program)
print(f"Final state: {result.final_state}")
print(f"alice: {result.final_state['alice']}")
print(f"bob: {result.final_state['bob']}")
```

#### runtime.execute_file()

```python
execute_file(filepath: str) -> ExecutionResult
```

Executes an Aethel program from a file.

**Parameters:**
- `filepath` (str): Path to .ae file

**Returns:**
- `ExecutionResult`: Execution result

**Example:**
```python
result = runtime.execute_file("safe_transfer.ae")
```

#### runtime.execute_with_state()

```python
execute_with_state(
    program: str,
    initial_state: Dict[str, Any]
) -> ExecutionResult
```

Executes a program with a provided initial state.

**Parameters:**
- `program` (str): Aethel source code
- `initial_state` (Dict[str, Any]): Initial variable values

**Returns:**
- `ExecutionResult`: Execution result

**Example:**
```python
initial_state = {
    "alice": 1000,
    "bob": 500
}

result = runtime.execute_with_state(program, initial_state)
```

#### runtime.get_state()

```python
get_state() -> Dict[str, Any]
```

Gets the current runtime state.

**Returns:**
- `Dict[str, Any]`: Current variable values

**Example:**
```python
state = runtime.get_state()
print(f"Current state: {state}")
```

#### runtime.reset()

```python
reset() -> None
```

Resets the runtime state.

**Example:**
```python
runtime.reset()
```

## Data Classes

### RuntimeConfig

Configuration for the Runtime.

```python
@dataclass
class RuntimeConfig:
    enable_sandboxing: bool = True
    max_memory_mb: int = 512
    max_execution_time: int = 10
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_profiling: bool = False
```

**Fields:**
- `enable_sandboxing`: Enable execution sandboxing (default: True)
- `max_memory_mb`: Maximum memory usage in MB (default: 512)
- `max_execution_time`: Maximum execution time in seconds (default: 10)
- `enable_logging`: Enable execution logging (default: True)
- `log_level`: Logging level (default: "INFO")
- `enable_profiling`: Enable performance profiling (default: False)

### ExecutionResult

Result of program execution.

```python
@dataclass
class ExecutionResult:
    success: bool
    final_state: Dict[str, Any]
    execution_time: float
    memory_used: int
    operations_count: int
    logs: List[str]
    errors: List[ExecutionError]
    profile: Optional[ExecutionProfile]
```

**Fields:**
- `success`: Whether execution succeeded
- `final_state`: Final variable values
- `execution_time`: Execution time in seconds
- `memory_used`: Memory used in bytes
- `operations_count`: Number of operations executed
- `logs`: Execution logs
- `errors`: List of execution errors
- `profile`: Performance profile (if enabled)

**Example:**
```python
result = runtime.execute(program)

if result.success:
    print(f"✓ Executed in {result.execution_time:.3f}s")
    print(f"Memory used: {result.memory_used / 1024:.2f} KB")
    print(f"Operations: {result.operations_count}")
    print(f"\nFinal state:")
    for var, value in result.final_state.items():
        print(f"  {var} = {value}")
else:
    print("✗ Execution failed:")
    for error in result.errors:
        print(f"  {error.message}")
```

### ExecutionError

Error encountered during execution.

```python
@dataclass
class ExecutionError:
    error_type: str
    message: str
    line: int
    stack_trace: List[str]
```

**Fields:**
- `error_type`: Type of error (e.g., "runtime_error", "overflow")
- `message`: Error message
- `line`: Line number where error occurred
- `stack_trace`: Execution stack trace

### ExecutionProfile

Performance profile of execution.

```python
@dataclass
class ExecutionProfile:
    total_time: float
    parse_time: float
    verify_time: float
    execute_time: float
    operation_times: Dict[str, float]
    memory_profile: MemoryProfile
```

**Fields:**
- `total_time`: Total execution time
- `parse_time`: Time spent parsing
- `verify_time`: Time spent verifying
- `execute_time`: Time spent executing
- `operation_times`: Time per operation type
- `memory_profile`: Memory usage profile

## Complete Example

```python
from diotec360.core.runtime import Runtime, RuntimeConfig
from diotec360.core.judge import Judge

# Configure runtime
config = RuntimeConfig(
    enable_sandboxing=True,
    max_memory_mb=256,
    max_execution_time=5,
    enable_profiling=True
)

# Create runtime and judge
runtime = Runtime(config)
judge = Judge()

# Aethel program
program = """
solve payroll {
    # Company account
    company_balance = 100000
    
    # Employee salaries
    employee_1 = 0
    employee_2 = 0
    employee_3 = 0
    
    # Salary amounts
    salary_1 = 5000
    salary_2 = 6000
    salary_3 = 5500
    
    total_payroll = salary_1 + salary_2 + salary_3
    
    # Constraints
    assert total_payroll <= company_balance
    assert salary_1 > 0
    assert salary_2 > 0
    assert salary_3 > 0
    
    # Execute payroll
    company_balance = company_balance - total_payroll
    employee_1 = employee_1 + salary_1
    employee_2 = employee_2 + salary_2
    employee_3 = employee_3 + salary_3
    
    # Conservation
    conserve company_balance + employee_1 + employee_2 + employee_3 == 100000
}
"""

# Verify program
verification = judge.verify(program)

if verification.is_valid:
    print("✓ Program verified")
    
    # Execute program
    result = runtime.execute(program)
    
    if result.success:
        print(f"✓ Executed successfully")
        print(f"Execution time: {result.execution_time:.3f}s")
        print(f"Memory used: {result.memory_used / 1024:.2f} KB")
        
        print(f"\nFinal balances:")
        print(f"  Company: ${result.final_state['company_balance']:,.2f}")
        print(f"  Employee 1: ${result.final_state['employee_1']:,.2f}")
        print(f"  Employee 2: ${result.final_state['employee_2']:,.2f}")
        print(f"  Employee 3: ${result.final_state['employee_3']:,.2f}")
        
        # Show profile if enabled
        if result.profile:
            print(f"\nPerformance profile:")
            print(f"  Parse: {result.profile.parse_time:.3f}s")
            print(f"  Verify: {result.profile.verify_time:.3f}s")
            print(f"  Execute: {result.profile.execute_time:.3f}s")
    else:
        print("✗ Execution failed")
        for error in result.errors:
            print(f"  {error.message}")
else:
    print("✗ Verification failed")
```

## Sandboxing

The Runtime provides sandboxing for secure execution:

```python
config = RuntimeConfig(
    enable_sandboxing=True,
    max_memory_mb=256,
    max_execution_time=5
)

runtime = Runtime(config)

# Execution is sandboxed:
# - Memory limited to 256 MB
# - Execution time limited to 5 seconds
# - No file system access
# - No network access
# - No system calls
```

## State Management

### Persistent State

```python
# Execute multiple programs with shared state
runtime = Runtime()

# Program 1: Initialize accounts
program1 = """
solve init {
    alice = 1000
    bob = 500
}
"""
runtime.execute(program1)

# Get state
state = runtime.get_state()
print(f"State after program 1: {state}")

# Program 2: Transfer (uses state from program 1)
program2 = """
solve transfer {
    alice = alice - 100
    bob = bob + 100
    conserve alice + bob == 1500
}
"""
runtime.execute(program2)

# Final state
final_state = runtime.get_state()
print(f"Final state: {final_state}")
```

### State Reset

```python
# Reset state between executions
runtime.execute(program1)
runtime.reset()  # Clear state
runtime.execute(program2)  # Fresh execution
```

## Error Handling

```python
from diotec360.core.runtime import Runtime, RuntimeError

runtime = Runtime()

try:
    result = runtime.execute(program)
    if not result.success:
        for error in result.errors:
            print(f"Execution error: {error.message}")
except RuntimeError as e:
    print(f"Runtime error: {e}")
except MemoryError:
    print("Out of memory")
except TimeoutError:
    print("Execution timed out")
```

## Performance Tips

### 1. Reuse Runtime Instances

```python
# Good: Reuse runtime
runtime = Runtime()
for program in programs:
    result = runtime.execute(program)
    runtime.reset()

# Bad: Create new runtime each time
for program in programs:
    runtime = Runtime()  # Expensive!
    result = runtime.execute(program)
```

### 2. Disable Profiling in Production

```python
# Development
config = RuntimeConfig(enable_profiling=True)

# Production
config = RuntimeConfig(enable_profiling=False)
```

### 3. Adjust Resource Limits

```python
# For simple programs
config = RuntimeConfig(
    max_memory_mb=128,
    max_execution_time=1
)

# For complex programs
config = RuntimeConfig(
    max_memory_mb=1024,
    max_execution_time=30
)
```

## Integration with Judge

Always verify before executing:

```python
from diotec360.core.judge import Judge
from diotec360.core.runtime import Runtime

judge = Judge()
runtime = Runtime()

# Verify first
verification = judge.verify(program)

if verification.is_valid:
    # Then execute
    result = runtime.execute(program)
else:
    print("Cannot execute: verification failed")
```

## See Also

- [Judge API](judge.md)
- [Conservation Validator API](conservation-validator.md)
- [Language Reference](../language-reference/syntax.md)
- [Examples](../examples/banking.md)
