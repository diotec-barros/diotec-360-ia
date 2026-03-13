# Quick Start Tutorial

## 5-Minute Proof Generation

This tutorial will guide you through creating your first Aethel program and generating a mathematical proof in just 5 minutes.

## Step 1: Create Your First Aethel Program

Create a file named `safe_transfer.ae`:

```aethel
# Safe money transfer with conservation proof

solve transfer {
    # Initial state
    alice_balance = 1000
    bob_balance = 500
    
    # Transfer amount
    amount = 100
    
    # Constraints: amount must be positive and not exceed balance
    assert amount > 0
    assert amount <= alice_balance
    
    # Execute transfer
    alice_balance = alice_balance - amount
    bob_balance = bob_balance + amount
    
    # Conservation law: total money must remain constant
    conserve alice_balance + bob_balance == 1500
}
```

## Step 2: Run the Program

Execute your Aethel program:

```bash
aethel run safe_transfer.ae
```

## Step 3: View the Proof

Aethel automatically generates a mathematical proof that your transfer preserves conservation:

```
✓ Proof Generated Successfully

Conservation Proof:
  Initial: alice(1000) + bob(500) = 1500
  Transfer: -100 from alice, +100 to bob
  Final: alice(900) + bob(600) = 1500
  
✓ Conservation law verified: Total remains 1500
✓ All constraints satisfied
✓ Proof is mathematically sound

Execution time: 0.023s
```

## Step 4: Explore the Proof Details

Generate a detailed proof report:

```bash
aethel prove safe_transfer.ae --verbose
```

This outputs:

```
=== Aethel Proof Report ===

Program: safe_transfer.ae
Status: ✓ VERIFIED

Constraints Verified:
  1. amount > 0 ✓
  2. amount <= alice_balance ✓
  
Conservation Laws:
  1. alice_balance + bob_balance == 1500 ✓
  
Proof Steps:
  1. Initial state: {alice: 1000, bob: 500}
  2. Constraint check: 100 > 0 ✓
  3. Constraint check: 100 <= 1000 ✓
  4. Execute: alice = 1000 - 100 = 900
  5. Execute: bob = 500 + 100 = 600
  6. Conservation check: 900 + 600 = 1500 ✓
  
Mathematical Proof:
  ∀ transfer: (alice₀ + bob₀ = alice₁ + bob₁)
  Proven by: Arithmetic verification
  
Security: No overflow, underflow, or conservation violations detected
```

## What Just Happened?

You've just:

1. **Written a financial program** with explicit constraints
2. **Generated a mathematical proof** that the program is correct
3. **Verified conservation laws** automatically
4. **Detected potential security issues** before execution

## Key Concepts

### Solve Blocks

The `solve` block is where Aethel performs verification:

```aethel
solve block_name {
    # Your code here
}
```

### Assertions

Use `assert` to specify constraints that must hold:

```aethel
assert amount > 0
assert balance >= amount
```

### Conservation Laws

Use `conserve` to specify invariants that must be preserved:

```aethel
conserve total_before == total_after
```

## Try More Examples

### Example 1: Multi-Party Transfer

```aethel
solve multi_transfer {
    alice = 1000
    bob = 500
    charlie = 300
    
    # Transfer from alice to bob and charlie
    transfer_to_bob = 200
    transfer_to_charlie = 150
    
    assert transfer_to_bob + transfer_to_charlie <= alice
    
    alice = alice - transfer_to_bob - transfer_to_charlie
    bob = bob + transfer_to_bob
    charlie = charlie + transfer_to_charlie
    
    conserve alice + bob + charlie == 1800
}
```

### Example 2: Interest Calculation

```aethel
solve interest {
    principal = 10000
    rate = 0.05  # 5% annual rate
    time = 2     # 2 years
    
    interest = principal * rate * time
    final_amount = principal + interest
    
    assert interest > 0
    assert final_amount > principal
    
    conserve final_amount == 11000
}
```

### Example 3: Parallel Transfers

```aethel
solve parallel_transfers {
    # Multiple independent transfers
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

## Next Steps

Now that you've created your first proof, explore:

- [First Steps Guide](first-steps.md) - Learn more Aethel concepts
- [Language Reference](../language-reference/syntax.md) - Complete syntax guide
- [API Reference](../api-reference/judge.md) - Programmatic access

### Explore Real-World Examples

Check out our comprehensive example library organized by use case:

**Banking Examples:**
- [Safe Banking Transfer](../../examples/banking/safe_banking.ae) - Basic secure transfer with conservation proof
- [Payroll Distribution](../../examples/banking/payroll.ae) - Multi-employee payroll with budget constraints
- [Multi-Currency Transfer](../../examples/banking/multi_currency_transfer.ae) - Currency exchange with value conservation

**DeFi Examples:**
- [DeFi Liquidation](../../examples/defi/defi_liquidation.ae) - Collateralized loan liquidation with conservation
- [Flash Loan Shield](../../examples/defi/flash_loan_shield.ae) - Flash loan arbitrage with exploit protection
- [Portfolio Rebalancing](../../examples/defi/portfolio_rebalancing.ae) - Crypto portfolio rebalancing with value proof

**Compliance Examples:**
- [Private Compliance](../../examples/compliance/private_compliance.ae) - Zero-knowledge compliance verification
- [Audit Trail](../../examples/compliance/audit_trail.ae) - Immutable audit trail generation
- [Regulatory Reporting](../../examples/compliance/regulatory_reporting.ae) - Aggregated reporting with proof

**Parallel Execution Examples:**
- [Atomic Batch](../../examples/parallel/atomic_batch.ae) - Batch processing with atomicity guarantees
- [Parallel Transfers](../../examples/parallel/parallel_transfers.ae) - Concurrent transfers with conflict detection
- [Concurrent Settlement](../../examples/parallel/concurrent_settlement.ae) - Multi-party settlement with linearizability

## Common Questions

**Q: Do I need to understand formal verification?**  
A: No! Aethel handles the mathematical proofs automatically. Just write your constraints.

**Q: Can I use Aethel in production?**  
A: Yes! Aethel is production-ready. For mission-critical deployments, consider our [managed hosting](../commercial/managed-services.md).

**Q: How fast is proof generation?**  
A: Most proofs complete in milliseconds. Complex proofs may take seconds.

**Q: Can I integrate Aethel with existing systems?**  
A: Yes! See our [API Reference](../api-reference/runtime.md) for integration guides.

## Getting Help

- [GitHub Issues](https://github.com/diotec360/diotec360/issues)
- [Community Forum](https://community.aethel.dev)
- [Discord](https://discord.gg/aethel)

For enterprise support: [diotec360.com/aethel](https://diotec360.com/aethel)
