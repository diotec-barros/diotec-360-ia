# Diotec360 v1.9.0 Examples - Production Ready

This directory contains **working, tested examples** that demonstrate Aethel's capabilities.

---

## 🏦 Banking & Finance

### global_bank.ae
Complete banking system with multi-account transfers and conservation guarantees.

**Features**:
- Account management
- Secure transfers
- Balance conservation
- Overflow protection

**Test**: `python test_global_bank.py`

---

## 🔐 DeFi & Trading

### defi_liquidation_conservation.ae
DeFi liquidation logic with Conservation Oracle integration.

**Features**:
- Automated liquidations
- Solvency proofs
- Conservation validation
- Risk management

**Test**: Integrated in `test_conservation_oracle_integration.py`

### defi_exchange_parallel.ae
Parallel DEX operations with deterministic execution.

**Features**:
- Concurrent order matching
- Conflict-free trading
- Atomic swaps
- Linearizability guaranteed

**Protocol**: Synchrony v1.8.0

### liquidation_parallel.ae
Parallel liquidation processing without race conditions.

**Features**:
- Batch liquidations
- Deterministic ordering
- Conservation preserved
- High throughput

**Protocol**: Synchrony v1.8.0

---

## 💼 Enterprise & Payroll

### payroll_parallel.ae
Parallel payroll processing with atomic commits.

**Features**:
- Batch salary payments
- Atomic transactions
- Conservation guaranteed
- Audit trail

**Protocol**: Synchrony v1.8.0

---

## 🛡️ Security & Defense

### sentinel_demo.ae
Autonomous Sentinel demonstration with 7-layer defense.

**Features**:
- Attack detection
- Adaptive rigor
- Quarantine system
- Self-healing

**Test**: `python showcase/3_immune_system.py`

### adversarial_test.ae
Adversarial attack scenarios for security validation.

**Features**:
- Overflow attacks
- Injection attempts
- DoS simulation
- Vaccine testing

**Test**: `python test_adversarial_vaccine.py`

---

## 🔒 Privacy & Compliance

### private_compliance.ae
Zero-knowledge compliance with privacy-preserving audits.

**Features**:
- ZKP proofs
- Private transactions
- Regulatory compliance
- Ghost Protocol integration

**Protocol**: Ghost v1.6.0

---

## 📚 How to Use

### 1. View Example Code
```bash
cat aethel/examples/global_bank.ae
```

### 2. Run Demonstrations
```bash
# Banking showcase
python showcase/1_safe_banking.py

# Security showcase
python showcase/3_immune_system.py

# AI safety showcase
python showcase/2_ai_supervisor.py
```

### 3. Run Tests
```bash
# Test specific example
pytest test_global_bank.py -v

# Test all conservation examples
pytest test_conservation_oracle_integration.py -v

# Test parallel execution
pytest test_parallel_executor.py -v
```

---

## 🎯 Example Categories

| Category | Examples | Status |
|----------|----------|--------|
| Banking | 1 | ✅ Production |
| DeFi | 3 | ✅ Production |
| Enterprise | 1 | ✅ Production |
| Security | 2 | ✅ Production |
| Privacy | 1 | ✅ Production |
| **TOTAL** | **8** | **✅ All Working** |

---

## 🚀 Quick Start

### For Developers
```bash
# Clone and explore
cd aethel/examples
ls -la

# Read an example
cat global_bank.ae

# Run the showcases
cd ../..
python showcase/1_safe_banking.py
```

### For Auditors
```bash
# Run all tests
pytest test_global_bank.py test_conservation_oracle_integration.py -v

# Check conservation
python demo_conservation.py

# Verify financial calculations
python demo_stdlib.py
```

---

## 📖 Learning Path

1. **Start Here**: `global_bank.ae` - Simple banking operations
2. **Conservation**: `defi_liquidation_conservation.ae` - Learn conservation rules
3. **Parallel**: `payroll_parallel.ae` - Understand Synchrony Protocol
4. **Security**: `sentinel_demo.ae` - Explore autonomous defense
5. **Privacy**: `private_compliance.ae` - Master Ghost Protocol

---

## ⚠️ Removed Examples

The following examples have been removed as they are outdated or non-functional:

- `finance.ae` → Replaced by StdLib v2.0.0 (`demo_stdlib.py`)
- `finance_exploit.ae` → Replaced by conservation demos
- `defi_liquidation.ae` → Replaced by `defi_liquidation_conservation.ae`
- `prediction_market.ae` → Needs parser update (v2.0)
- `vote.ae` → Needs parser update (v2.0)
- `weather_insurance.ae` → Needs parser update (v2.0)
- `private_transfer.ae` → Replaced by `private_compliance.ae`
- `private_voting.ae` → Needs parser update (v2.0)

These will be restored in v2.0 with updated syntax.

---

## 🔧 Technical Details

### Protocols Used

- **Conservation Guardian**: All financial examples
- **Synchrony Protocol v1.8.0**: All `*_parallel.ae` examples
- **Ghost Protocol v1.6.0**: All `private_*.ae` examples
- **Autonomous Sentinel v1.9.0**: All security examples

### Verification

Every example in this directory:
- ✅ Has been tested
- ✅ Passes all assertions
- ✅ Is mathematically proven
- ✅ Is production-ready

---

## 📞 Support

- **Documentation**: See `FUNCTIONAL_TESTS_REPORT.md`
- **Issues**: Check GitHub issues
- **Community**: Join our Discord

---

**"Every example is a proof. Every proof is a guarantee."**

*Diotec360 v1.9.0 "Apex" - The Age of Facts*
