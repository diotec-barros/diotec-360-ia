# Aethel Examples

This directory contains links to comprehensive Aethel code examples demonstrating various use cases.

## Example Categories

All examples are located in the root `examples/` directory, organized by use case:

### 🏦 Banking Examples
Location: [`../../examples/`](../../examples/)

Examples demonstrating safe financial operations:
- **safe_banking.ae** - Basic account transfers with conservation proofs
- **payroll.ae** - Batch payroll processing with atomic guarantees
- **multi_currency_transfer.ae** - Cross-currency operations

### 💎 DeFi Examples
Location: [`../../examples/`](../../examples/)

Examples for decentralized finance protocols:
- **defi_liquidation_conservation.ae** - Safe liquidation with conservation proofs
- **flash_loan_shield.ae** - Flash loan attack prevention
- **portfolio_rebalancing.ae** - Multi-asset portfolio management

### 📋 Compliance Examples
Location: [`../../examples/`](../../examples/)

Examples demonstrating regulatory compliance:
- **private_compliance.ae** - Zero-knowledge compliance reporting
- **audit_trail.ae** - Cryptographic audit trails
- **regulatory_reporting.ae** - Automated compliance reports

### ⚡ Parallel Execution Examples
Location: [`../../examples/`](../../examples/)

Examples showcasing high-throughput parallel processing:
- **atomic_batch.ae** - Atomic batch operations
- **liquidation_parallel.ae** - Parallel liquidation processing
- **payroll_parallel.ae** - High-throughput payroll

## Quick Start

### View All Examples

```bash
# List all available examples
ls ../../examples/

# View a specific example
cat ../../examples/safe_banking.ae
```

### Run an Example

```python
from diotec360.core.judge import Judge

# Load and verify an example
judge = Judge()
with open('../../examples/safe_banking.ae', 'r') as f:
    code = f.read()

verdict = judge.verify(code)
print(f"Proof valid: {verdict.is_valid}")
```

### Example Structure

Each example includes:
- **Detailed comments** explaining the code
- **Conservation proofs** demonstrating value preservation
- **Security features** showing attack prevention
- **Real-world context** explaining the use case

## Learning Path

### Beginner
1. Start with `safe_banking.ae` - Basic transfers
2. Try `payroll.ae` - Batch operations
3. Explore `audit_trail.ae` - Proof generation

### Intermediate
1. Study `defi_liquidation_conservation.ae` - Complex proofs
2. Learn `flash_loan_shield.ae` - Attack prevention
3. Practice `atomic_batch.ae` - Parallel execution

### Advanced
1. Master `private_compliance.ae` - Zero-knowledge proofs
2. Optimize `payroll_parallel.ae` - High-throughput systems
3. Build custom examples using the patterns learned

## Documentation

For detailed explanations of Aethel concepts used in these examples:

- **Language Syntax**: [../language-reference/syntax.md](../language-reference/syntax.md)
- **Conservation Laws**: [../language-reference/conservation-laws.md](../language-reference/conservation-laws.md)
- **API Reference**: [../api-reference/](../api-reference/)
- **Getting Started**: [../getting-started/quickstart.md](../getting-started/quickstart.md)

## Contributing Examples

Have a great example to share? We welcome contributions!

1. Create your example in `examples/` directory
2. Add detailed comments explaining the code
3. Include conservation proofs where applicable
4. Submit a pull request

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## Example Template

```python
# Title: Brief description
# Category: banking | defi | compliance | parallel
# Difficulty: beginner | intermediate | advanced
# Description: Detailed explanation of what this example demonstrates

solve example_operation {
    # Your code here with detailed comments
    
    proof conservation {
        # Conservation law proofs
    }
}
```

## Support

- **Questions**: [GitHub Discussions](https://github.com/diotec360/diotec360/discussions)
- **Issues**: [GitHub Issues](https://github.com/diotec360/diotec360/issues)
- **Discord**: [discord.gg/aethel](https://discord.gg/aethel)

---

**Note**: All examples are tested and verified to work with Diotec360 v1.9.0. If you encounter any issues, please report them on GitHub.

