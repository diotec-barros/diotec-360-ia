# 🎭 Aethel Zero-Knowledge Proofs Guide

**Version**: 1.6.0 "Ghost Protocol"  
**Date**: February 4, 2026  
**Status**: Simulation (Real ZKP in v1.7.0)

---

## 🎯 What are Zero-Knowledge Proofs?

Zero-Knowledge Proofs (ZKP) allow you to **prove something is true without revealing why it's true**.

### Real-World Analogy

**Without ZKP**:
- "I have $10,000 in my account" → Shows bank statement

**With ZKP**:
- "I have enough money to buy this $5,000 car" → Proves it without showing balance

---

## 🚀 Quick Start

### 1. Mark Variables as Secret

Use the `secret` keyword to hide values:

```aethel
intent private_transfer(sender: Account, receiver: Account, amount: int) {
    guard {
        secret sender_balance >= amount;  # Balance hidden!
        amount > 0;                        # Amount visible
    }
    
    verify {
        secret sender_balance == old_sender_balance - amount;
    }
}
```

### 2. Run Verification

```bash
# Using CLI
python -m aethel.cli.main verify private_transfer.ae

# Using API
curl -X POST https://diotec-diotec360-judge.hf.space/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "..."}'
```

### 3. Check ZKP Status

```json
{
  "status": "PROVED",
  "zkp_status": "SIMULATED",
  "secret_variables": ["sender_balance"],
  "message": "✅ ZKP-Ready: Balance proven without revelation"
}
```

---

## 📚 The `secret` Keyword

### Syntax

```aethel
secret variable_name operator value
```

### Valid Operators

- `==` - Equality
- `>=` - Greater than or equal
- `<=` - Less than or equal
- `>` - Greater than
- `<` - Less than
- `!=` - Not equal

### Where to Use

✅ **In `guard` blocks**:
```aethel
guard {
    secret balance >= amount;
    secret age >= 18;
}
```

✅ **In `verify` blocks**:
```aethel
verify {
    secret balance == old_balance - amount;
    secret total == sum_of_parts;
}
```

❌ **NOT in `solve` blocks**:
```aethel
solve {
    secret priority: security;  # ERROR!
}
```

---

## 🎨 Common Patterns

### Pattern 1: Private Balance Transfer

**Use Case**: Transfer money without revealing balances

```aethel
intent private_transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        secret sender_balance >= amount;
        amount > 0;
    }
    
    verify {
        secret sender_balance == old_sender_balance - amount;
        secret receiver_balance == old_receiver_balance + amount;
        total_supply == old_total_supply;  # Conservation still public
    }
}
```

**What's Hidden**: Sender and receiver balances  
**What's Public**: Transfer amount, conservation proof

### Pattern 2: Private Voting

**Use Case**: Vote without revealing choice

```aethel
intent private_vote(voter: Account, candidate: Candidate) {
    guard {
        secret voter_has_voted == false;
        voter_is_eligible == true;
    }
    
    verify {
        secret voter_has_voted == true;
        candidate_votes == old_candidate_votes + 1;
    }
}
```

**What's Hidden**: Who voted, vote status  
**What's Public**: Vote was counted, eligibility

### Pattern 3: Private Compliance

**Use Case**: Prove compliance without revealing data

```aethel
intent prove_compliance(entity: Account, threshold: int) {
    guard {
        secret entity_value >= threshold;
        threshold > 0;
    }
    
    verify {
        secret compliance_score >= 0.95;
        entity_is_compliant == true;
    }
}
```

**What's Hidden**: Actual value, compliance score  
**What's Public**: Compliance status, threshold

### Pattern 4: Private Age Verification

**Use Case**: Prove age without revealing birthdate

```aethel
intent verify_age(user: Account, min_age: int) {
    guard {
        secret user_age >= min_age;
        min_age >= 0;
    }
    
    verify {
        secret age_verified == true;
        user_can_access == true;
    }
}
```

**What's Hidden**: Exact age  
**What's Public**: Age requirement met

---

## 🔧 Advanced Usage

### Mixing Public and Private

You can mix public and private constraints:

```aethel
intent hybrid_transfer(sender: Account, receiver: Account, amount: Balance) {
    guard {
        # Private
        secret sender_balance >= amount;
        secret sender_credit_score >= 700;
        
        # Public
        amount > 0;
        amount <= 10000;
        sender != receiver;
    }
    
    verify {
        # Private
        secret sender_balance == old_sender_balance - amount;
        secret receiver_balance == old_receiver_balance + amount;
        
        # Public
        total_supply == old_total_supply;
        transaction_count == old_transaction_count + 1;
    }
}
```

### Multiple Secret Variables

```aethel
intent multi_secret(account: Account) {
    guard {
        secret balance >= 1000;
        secret credit_score >= 700;
        secret debt_ratio <= 0.3;
        secret income >= 50000;
    }
    
    verify {
        secret financial_health_score >= 0.8;
        account_approved == true;
    }
}
```

### Conservation with Secrets

Conservation laws work with secret variables:

```aethel
intent private_multi_transfer(
    sender: Account,
    receiver1: Account,
    receiver2: Account,
    amount1: Balance,
    amount2: Balance
) {
    guard {
        secret sender_balance >= (amount1 + amount2);
    }
    
    verify {
        secret sender_balance == old_sender_balance - amount1 - amount2;
        secret receiver1_balance == old_receiver1_balance + amount1;
        secret receiver2_balance == old_receiver2_balance + amount2;
        
        # Conservation still proven!
        total_supply == old_total_supply;
    }
}
```

---

## ⚠️ Important Limitations (v1.6.0)

### This is a SIMULATION

**v1.6.0 does NOT provide cryptographic privacy!**

What it does:
- ✅ Validates ZKP syntax
- ✅ Tests user experience
- ✅ Prepares architecture
- ✅ Enables "ZKP-Ready" development

What it does NOT do:
- ❌ Hide actual values
- ❌ Provide cryptographic security
- ❌ Protect against adversaries
- ❌ Use real ZKP cryptography

### When to Use v1.6.0

**Good for**:
- Testing ZKP syntax
- Prototyping private applications
- Validating UX
- Preparing for v1.7.0

**NOT good for**:
- Production systems
- Real privacy requirements
- Sensitive data
- Security-critical applications

### v1.7.0 - Real ZKP (Coming Soon)

Will implement:
- Pedersen Commitments
- Range Proofs (Bulletproofs)
- Cryptographic security
- Real privacy guarantees

---

## 📊 Performance

### v1.6.0 (Simulation)

- Syntax validation: <1ms
- Commitment generation: <1ms
- Total overhead: <5ms per intent
- Memory: +50KB per intent

### v1.7.0 (Real ZKP - Future)

- Commitment generation: ~10ms
- Range proof: ~50ms
- Verification: ~20ms
- Total overhead: ~100ms per intent

---

## 🎯 Use Cases

### Financial Services

**Private Banking**:
```aethel
secret balance >= withdrawal_amount;
```
- Banks verify transactions without seeing balances
- Customers maintain financial privacy
- Regulators can audit without accessing data

**Credit Scoring**:
```aethel
secret credit_score >= 700;
```
- Prove creditworthiness without revealing score
- Lenders verify eligibility without seeing details

### Governance

**Private Voting**:
```aethel
secret voter_has_voted == false;
```
- Elections with verifiable results
- Secret ballots maintained
- No voter coercion possible

**DAO Governance**:
```aethel
secret token_balance >= proposal_threshold;
```
- Prove voting power without revealing holdings
- Anonymous governance participation

### Compliance

**Tax Compliance**:
```aethel
secret taxes_paid >= required_tax;
```
- Prove tax payment without revealing income
- Governments verify compliance without accessing records

**Regulatory Compliance**:
```aethel
secret compliance_score >= 0.95;
```
- Prove regulatory compliance without exposing data
- Auditors verify without seeing sensitive information

### Identity

**Age Verification**:
```aethel
secret age >= 18;
```
- Prove age without revealing birthdate
- Access control without identity exposure

**Credential Verification**:
```aethel
secret has_credential == true;
```
- Prove qualifications without revealing details
- Privacy-preserving authentication

---

## 🐛 Troubleshooting

### Error: "No secret variables found"

**Problem**: No variables marked with `secret`

**Solution**:
```aethel
# ❌ Wrong
guard {
    balance >= amount;
}

# ✅ Correct
guard {
    secret balance >= amount;
}
```

### Error: "Secret variable used inconsistently"

**Problem**: Variable marked secret in one place, public in another

**Solution**:
```aethel
# ❌ Wrong
guard {
    secret balance >= amount;
}
verify {
    balance == old_balance - amount;  # Missing 'secret'!
}

# ✅ Correct
guard {
    secret balance >= amount;
}
verify {
    secret balance == old_balance - amount;
}
```

### Error: "Cannot use secret in solve block"

**Problem**: `secret` keyword in `solve` block

**Solution**:
```aethel
# ❌ Wrong
solve {
    secret priority: security;
}

# ✅ Correct
solve {
    priority: security;  # solve is always public
}
```

---

## 📚 Examples

See the `aethel/examples/` directory:

- `private_transfer.ae` - Private financial transfer
- `private_voting.ae` - Private voting system
- `private_compliance.ae` - Private tax compliance

---

## 🚀 Next Steps

1. **Try the examples**: Load examples in Aethel Studio
2. **Write your own**: Create private intents for your use case
3. **Test syntax**: Validate ZKP syntax with the simulator
4. **Prepare for v1.7.0**: Design with real ZKP in mind

---

## 📞 Resources

- **Spec**: `V1_6_0_GHOST_PROTOCOL_SPEC.md`
- **Implementation**: `aethel/core/zkp_simulator.py`
- **Tests**: `test_zkp_simulator.py`
- **Examples**: `aethel/examples/private_*.ae`
- **API**: https://diotec-diotec360-judge.hf.space/docs

---

## 💡 Tips

1. **Start simple**: Begin with one secret variable
2. **Mix public/private**: Not everything needs to be secret
3. **Test thoroughly**: Use the simulator to validate syntax
4. **Think ahead**: Design for real ZKP (v1.7.0)
5. **Document clearly**: Explain what's hidden and what's public

---

**"Prove without revealing. Verify without seeing."**

🎭 Ghost Protocol - Where secrets are proven, but never revealed.

