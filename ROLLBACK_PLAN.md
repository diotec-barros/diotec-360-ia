# Autonomous Sentinel Rollback Plan

## Overview

This document provides procedures for rolling back the Autonomous Sentinel v1.9.0 to v1.8.0 behavior in case of critical issues. The rollback is designed to be fast (<5 minutes) and safe (no data loss).

## When to Rollback

Execute rollback if any of the following occur:

### Critical Conditions (Immediate Rollback)
- False positive rate >5% for more than 10 minutes
- System overhead >20% for more than 5 minutes
- Quarantine capacity exceeded causing widespread rejections
- Crisis Mode stuck in active state
- Database corruption or data loss
- Security vulnerability discovered in Sentinel components

### Warning Conditions (Consider Rollback)
- False positive rate >2% for more than 30 minutes
- System overhead >10% for more than 15 minutes
- Self-Healing generating ineffective rules (effectiveness <50%)
- Repeated Crisis Mode oscillation (>10 activations per hour)

## Rollback Procedure

### Phase 1: Immediate Disable (< 1 minute)

**Step 1: Disable Sentinel via Environment Variable**

```bash
# Set environment variable to disable Sentinel
export DIOTEC360_SENTINEL_ENABLED=false

# Or update configuration file
echo "DIOTEC360_SENTINEL_ENABLED=false" >> .env

# Restart application
systemctl restart diotec360-judge
# OR
docker-compose restart
# OR
kill -HUP $(cat aethel.pid)
```

**Expected Behavior:**
- Sentinel Monitor: DISABLED (no telemetry collection)
- Semantic Sanitizer: DISABLED (Layer -1 bypassed)
- Crisis Mode: DISABLED
- Quarantine: DISABLED
- Self-Healing: DISABLED
- Adversarial Vaccine: DISABLED
- **Fallback**: System operates with v1.8.0 Layers 0-4 only

**Verification:**
```bash
# Check logs for rollback confirmation
tail -f logs/aethel.log | grep "Sentinel disabled"

# Verify v1.8.0 behavior
curl -X POST http://localhost:7860/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "transfer(alice, bob, 100)"}'

# Should see: "Sentinel: DISABLED" in response headers
```

### Phase 2: Validate Rollback (< 2 minutes)

**Step 2: Run Rollback Tests**

```bash
# Execute rollback test suite
python scripts/test_rollback.py

# Expected output:
# ✅ Sentinel disabled
# ✅ Layer 0-4 operational
# ✅ Throughput restored
# ✅ No Sentinel overhead
```

**Step 3: Monitor System Health**

```bash
# Monitor for 2 minutes
python scripts/monitor_system.py --duration 120

# Check metrics:
# - Throughput should return to v1.8.0 levels
# - Overhead should drop to 0%
# - False positive rate should be 0% (no Sentinel blocking)
```

### Phase 3: Preserve Data (< 2 minutes)

**Step 4: Backup Sentinel Databases**

```bash
# Backup telemetry database
cp ./data/telemetry.db ./backups/telemetry_$(date +%Y%m%d_%H%M%S).db

# Backup gauntlet database
cp ./data/gauntlet.db ./backups/gauntlet_$(date +%Y%m%d_%H%M%S).db

# Backup pattern database
cp ./data/trojan_patterns.json ./backups/trojan_patterns_$(date +%Y%m%d_%H%M%S).json
```

**Step 5: Export Reports for Analysis**

```bash
# Export Gauntlet Report for post-mortem
python scripts/export_gauntlet_report.py \
  --format pdf \
  --output ./reports/rollback_analysis_$(date +%Y%m%d).pdf

# Export telemetry statistics
python scripts/export_telemetry.py \
  --format json \
  --output ./reports/telemetry_$(date +%Y%m%d).json
```

## Fallback Behavior

When Sentinel is disabled, the system operates with v1.8.0 behavior:

### Active Components
- ✅ Layer 0: Input Sanitizer
- ✅ Layer 1: Conservation Checker
- ✅ Layer 2: Overflow Detector
- ✅ Layer 3: Z3 Formal Verifier
- ✅ Layer 4: ZKP Privacy Layer
- ✅ Synchrony Protocol (parallel execution)

### Disabled Components
- ❌ Sentinel Monitor (no telemetry)
- ❌ Semantic Sanitizer (Layer -1)
- ❌ Crisis Mode
- ❌ Quarantine System
- ❌ Self-Healing Engine
- ❌ Adversarial Vaccine
- ❌ Gauntlet Report (no new logs)

### Performance Impact
- Throughput: Returns to v1.8.0 baseline (10-20x improvement)
- Overhead: 0% (Sentinel overhead removed)
- Latency: Returns to v1.8.0 baseline

### Security Impact
- Still protected by 5-layer defense (Layers 0-4)
- No proactive attack detection (Semantic Sanitizer disabled)
- No automatic Crisis Mode response
- No Self-Healing (manual rule updates required)

## Rollback Testing Checklist

Before declaring rollback complete, verify:

- [ ] Sentinel disabled (check logs)
- [ ] Layer 0-4 operational (run test suite)
- [ ] Throughput restored to v1.8.0 levels
- [ ] Overhead reduced to 0%
- [ ] No false positives (Sentinel not blocking)
- [ ] Databases backed up
- [ ] Reports exported for analysis
- [ ] Monitoring confirms stable operation
- [ ] Stakeholders notified

## Post-Rollback Analysis

After rollback, conduct root cause analysis:

### 1. Review Telemetry Data

```bash
# Analyze telemetry for anomalies
python scripts/analyze_telemetry.py \
  --start "2026-02-05 00:00:00" \
  --end "2026-02-05 23:59:59"

# Look for:
# - Anomaly rate spikes
# - Performance degradation patterns
# - Crisis Mode triggers
```

### 2. Review Gauntlet Report

```bash
# Analyze attack patterns
python scripts/analyze_gauntlet.py \
  --start "2026-02-05 00:00:00" \
  --end "2026-02-05 23:59:59"

# Look for:
# - False positive patterns
# - Legitimate transactions blocked
# - Attack types causing issues
```

### 3. Review Self-Healing Rules

```bash
# List all generated rules
python scripts/list_rules.py --all

# Identify problematic rules
python scripts/analyze_rules.py --effectiveness-threshold 0.5

# Look for:
# - Rules with high false positive rates
# - Rules with low effectiveness
# - Rules blocking legitimate patterns
```

### 4. Identify Root Cause

Common root causes:
- **High False Positives**: Entropy threshold too low, pattern too broad
- **High Overhead**: Telemetry collection too frequent, pattern database too large
- **Crisis Mode Oscillation**: Thresholds too sensitive, baseline not established
- **Quarantine Capacity**: Capacity too small for traffic volume
- **Self-Healing Issues**: Historical transaction sample not representative

## Re-Deployment After Rollback

Once root cause is identified and fixed:

### 1. Fix Configuration

```bash
# Example: Increase entropy threshold
export DIOTEC360_ENTROPY_THRESHOLD=0.85  # Was 0.8

# Example: Increase Crisis Mode threshold
export DIOTEC360_CRISIS_ANOMALY_THRESHOLD=0.15  # Was 0.10

# Example: Increase quarantine capacity
export DIOTEC360_QUARANTINE_CAPACITY=200  # Was 100
```

### 2. Test in Staging

```bash
# Deploy to staging environment
python scripts/deploy_shadow_mode.py --env staging

# Run for 24 hours
# Monitor metrics closely
# Verify fix resolves issue
```

### 3. Gradual Re-Deployment

```bash
# Phase 1: Shadow Mode (1 week)
python scripts/deploy_shadow_mode.py

# Phase 2: Soft Launch (2 weeks)
python scripts/deploy_soft_launch.py

# Phase 3: Full Activation
python scripts/deploy_full_activation.py
```

## Emergency Contacts

In case of critical issues:

- **On-Call Engineer**: [phone/pager]
- **Security Team**: [email/slack]
- **DevOps Team**: [email/slack]
- **Management**: [email/phone]

## Rollback Script

For automated rollback, use:

```bash
#!/bin/bash
# scripts/rollback_sentinel.sh

echo "🔄 Rolling back Autonomous Sentinel..."

# Disable Sentinel
export DIOTEC360_SENTINEL_ENABLED=false
echo "DIOTEC360_SENTINEL_ENABLED=false" >> .env

# Restart application
systemctl restart diotec360-judge

# Wait for restart
sleep 5

# Verify rollback
python scripts/test_rollback.py

# Backup databases
mkdir -p ./backups
cp ./data/telemetry.db ./backups/telemetry_$(date +%Y%m%d_%H%M%S).db
cp ./data/gauntlet.db ./backups/gauntlet_$(date +%Y%m%d_%H%M%S).db

# Export reports
python scripts/export_gauntlet_report.py \
  --format pdf \
  --output ./reports/rollback_analysis_$(date +%Y%m%d).pdf

echo "✅ Rollback complete"
echo "📊 Monitor system for 10 minutes: python scripts/monitor_system.py"
```

## Rollback Metrics

Track rollback metrics for continuous improvement:

- **Time to Rollback**: Target <5 minutes
- **Data Loss**: Target 0 (all data preserved)
- **Downtime**: Target <1 minute
- **False Rollbacks**: Target <1 per quarter
- **Root Cause Identification**: Target <24 hours

## Version History

| Version | Date       | Changes |
|---------|------------|---------|
| 1.0     | 2026-02-05 | Initial rollback plan for v1.9.0 |

## Approval

This rollback plan has been reviewed and approved by:

- [ ] Engineering Lead
- [ ] Security Lead
- [ ] DevOps Lead
- [ ] Product Manager

---

**Last Updated**: February 5, 2026
**Next Review**: March 5, 2026
