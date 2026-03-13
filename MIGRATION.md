# Aethel Migration Guide

## Overview

This guide helps you migrate between Diotec360 versions and understand compatibility considerations.

## Version Compatibility Matrix

| From Version | To Version | Compatibility | Migration Required | Notes |
|--------------|------------|---------------|-------------------|-------|
| 1.0.x | 1.1.x | Full | No | Drop-in replacement |
| 1.1.x | 1.2.x | Full | No | Drop-in replacement |
| 1.2.x | 1.3.x | Full | No | Conservation API added |
| 1.3.x | 1.4.x | Full | No | Overflow protection added |
| 1.4.x | 1.5.x | Full | No | Sanitizer added |
| 1.5.x | 1.6.x | Full | No | ZKP support added |
| 1.6.x | 1.7.x | Full | No | Oracle system added |
| 1.7.x | 1.8.x | Full | No | Synchrony protocol added |
| 1.8.x | 1.9.x | Full | No | Autonomous Sentinel added |
| 1.9.x | 2.0.x | Breaking | Yes | Proof-of-Proof consensus |

## Semantic Versioning

Aethel follows [Semantic Versioning 2.0.0](https://semver.org/):

- **Major version** (X.0.0): Breaking changes, migration required
- **Minor version** (1.X.0): New features, backward compatible
- **Patch version** (1.0.X): Bug fixes, backward compatible

## Migration Procedures

### Upgrading Within Major Version (e.g., 1.8.x → 1.9.x)

**Step 1: Backup**
```bash
# Backup your Aethel state
cp -r .DIOTEC360_state .DIOTEC360_state.backup
cp -r .DIOTEC360_vault .DIOTEC360_vault.backup
```

**Step 2: Update Aethel**
```bash
pip install --upgrade aethel
```

**Step 3: Verify**
```bash
aethel --version
aethel test  # Run your test suite
```

**Step 4: Deploy**
```bash
# No code changes required for minor/patch upgrades
aethel run your_program.ae
```

### Upgrading Across Major Versions (e.g., 1.9.x → 2.0.x)

**Step 1: Review Breaking Changes**

Read the [CHANGELOG.md](CHANGELOG.md) for your target version to understand breaking changes.

**Step 2: Run Migration Tool**
```bash
# Automated migration assistant
aethel migrate --from 1.9.0 --to 2.0.0 --check

# Review migration report
cat migration_report.txt
```

**Step 3: Update Code**

The migration tool will identify required changes. Common patterns:

```aethel
# v1.9.x syntax
solve old_style {
    conserve total == 1000
}

# v2.0.x syntax (example - actual syntax TBD)
solve new_style {
    prove total == 1000  # New keyword
}
```

**Step 4: Test Thoroughly**
```bash
# Run comprehensive test suite
aethel test --all

# Run property-based tests
aethel test --property-tests

# Validate proofs
Diotec360 verify --all
```

**Step 5: Staged Rollout**

For production systems:

1. **Shadow mode**: Run v2.0 alongside v1.9, compare results
2. **Canary deployment**: Route 5% of traffic to v2.0
3. **Gradual rollout**: Increase to 25%, 50%, 100%
4. **Monitor**: Watch for anomalies, be ready to rollback

## Common Migration Scenarios

### Scenario 1: Upgrading from v1.3.x to v1.9.x

**Changes:**
- v1.4.x added overflow protection (automatic)
- v1.5.x added sanitizer (automatic)
- v1.6.x added ZKP support (opt-in)
- v1.7.x added oracle system (opt-in)
- v1.8.x added synchrony protocol (opt-in)
- v1.9.x added autonomous sentinel (automatic)

**Migration:**
```bash
# Simple upgrade, no code changes
pip install aethel==1.9.0
aethel test
```

**Considerations:**
- Sentinel monitoring is now active by default
- Performance overhead: ~2-5% (see benchmarks)
- New telemetry data collected (see privacy policy)

### Scenario 2: Adopting New Features

**Adding ZKP Support (v1.6.x+):**

```aethel
# Before (v1.5.x)
solve compliance_check {
    amount = 5000
    assert amount < 10000
}

# After (v1.6.x+)
import zkp

solve private_compliance {
    # Amount remains private
    zkp_proof = zkp.prove_range(amount, 0, 10000)
    assert zkp_proof.valid
}
```

**Adding Parallel Execution (v1.8.x+):**

```aethel
# Before (v1.7.x) - Sequential
solve sequential {
    transfer_1()
    transfer_2()
}

# After (v1.8.x+) - Parallel
solve parallel {
    atomic batch {
        transfer_1()
        transfer_2()
    }
}
```

### Scenario 3: Migrating from Other Systems

**From Solidity:**

```solidity
// Solidity
function transfer(address to, uint amount) public {
    require(balances[msg.sender] >= amount);
    balances[msg.sender] -= amount;
    balances[to] += amount;
}
```

```aethel
# Aethel equivalent
solve transfer {
    sender_balance = 1000
    recipient_balance = 500
    amount = 100
    
    assert amount > 0
    assert sender_balance >= amount
    
    sender_balance = sender_balance - amount
    recipient_balance = recipient_balance + amount
    
    conserve sender_balance + recipient_balance == 1500
}
```

**Key Differences:**
- Aethel uses mathematical proofs instead of runtime checks
- Conservation laws are explicit and verified
- No gas fees for proof generation
- Deterministic execution guaranteed

## Database Migration

### State Store Migration

**v1.x → v2.x:**

```bash
# Export state from v1.x
aethel export-state --format json > state_v1.json

# Upgrade Aethel
pip install aethel==2.0.0

# Import state to v2.x
aethel import-state --format json < state_v1.json

# Verify integrity
Diotec360 verify-state
```

### Vault Migration

```bash
# Vault format is backward compatible
# No migration needed for v1.x → v2.x
# Vault automatically upgrades on first access
```

## API Migration

### Python API Changes

**v1.9.x:**
```python
from aethel.core import Judge

judge = Judge()
result = judge.execute("program.ae")
```

**v2.0.x (example):**
```python
from aethel.consensus import ConsensusJudge

# New consensus-aware API
judge = ConsensusJudge()
result = await judge.execute_with_consensus("program.ae")
```

### REST API Changes

**v1.9.x:**
```bash
POST /api/v1/execute
{
  "program": "solve { ... }"
}
```

**v2.0.x (example):**
```bash
POST /api/v2/execute
{
  "program": "solve { ... }",
  "consensus": {
    "required_validators": 3,
    "timeout_ms": 5000
  }
}
```

## Rollback Procedures

### Rolling Back a Minor Version

```bash
# Restore backup
rm -rf .DIOTEC360_state
cp -r .DIOTEC360_state.backup .DIOTEC360_state

# Downgrade Aethel
pip install aethel==1.8.0

# Verify
aethel --version
aethel test
```

### Rolling Back a Major Version

```bash
# Major version rollback requires careful planning
# 1. Stop all Aethel processes
# 2. Restore database backup
# 3. Downgrade Aethel
# 4. Restore code to previous version
# 5. Test thoroughly before resuming operations

# See ROLLBACK_PLAN.md for detailed procedures
```

## Testing Migration

### Pre-Migration Checklist

- [ ] Read CHANGELOG for target version
- [ ] Backup all data (.DIOTEC360_state, .DIOTEC360_vault)
- [ ] Run migration tool in check mode
- [ ] Review migration report
- [ ] Test in staging environment
- [ ] Prepare rollback plan
- [ ] Schedule maintenance window
- [ ] Notify stakeholders

### Post-Migration Validation

```bash
# Run full test suite
aethel test --all

# Verify proofs
Diotec360 verify --all

# Check performance
aethel benchmark

# Validate state integrity
Diotec360 verify-state

# Monitor for 24 hours
aethel monitor --duration 24h
```

## Commercial Relationships

### How Migration Affects Commercial Services

**Managed Hosting:**
- DIOTEC 360 handles all migrations automatically
- Zero downtime upgrades
- Automatic rollback on issues
- 24/7 support during migration windows

**Enterprise Support:**
- Dedicated migration assistance
- Custom migration scripts
- Pre-migration testing in your environment
- Post-migration monitoring and optimization

**Certification:**
- Certifications remain valid across minor versions
- Major version upgrades may require recertification
- Free recertification for active certificate holders

### Support During Migration

**Community Support:**
- GitHub Issues: Best-effort support
- Discord: Community help
- Forum: Migration discussions

**Professional Support:**
- Email support: 24-hour response time
- Migration planning assistance
- Post-migration health checks

**Enterprise Support:**
- Dedicated migration engineer
- 24/7 phone support
- Custom migration tooling
- Guaranteed success or money back

## Frequently Asked Questions

**Q: Can I skip versions (e.g., 1.5.x → 1.9.x)?**  
A: Yes, within the same major version. The migration tool handles intermediate changes automatically.

**Q: How long does migration take?**  
A: Minor versions: Minutes. Major versions: Hours to days depending on codebase size.

**Q: Will my proofs remain valid after migration?**  
A: Yes, proofs are cryptographically sealed and remain valid across versions.

**Q: Can I run multiple versions simultaneously?**  
A: Yes, for testing. Not recommended for production due to state synchronization complexity.

**Q: What if migration fails?**  
A: Follow rollback procedures. Contact support if issues persist.

**Q: Are there any breaking changes in v1.x?**  
A: No, all v1.x versions are backward compatible.

**Q: When should I upgrade?**  
A: Security patches: Immediately. Minor versions: Within 30 days. Major versions: Plan carefully.

## Getting Help

**Community:**
- [GitHub Issues](https://github.com/diotec360/diotec360/issues)
- [Discord](https://discord.gg/aethel)
- [Forum](https://community.aethel.dev)

**Commercial:**
- Professional Support: support@diotec360.com
- Enterprise Support: enterprise@diotec360.com
- Migration Consulting: consulting@diotec360.com

## See Also

- [CHANGELOG.md](CHANGELOG.md) - Version history
- [ROADMAP.md](ROADMAP.md) - Future versions
- [ROLLBACK_PLAN.md](ROLLBACK_PLAN.md) - Detailed rollback procedures
- [Managed Hosting](docs/commercial/managed-hosting.md) - Zero-hassle upgrades
