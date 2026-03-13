# Aethel MOE v2.1.0 - Deployment Guide

**Version**: v2.1.0  
**Last Updated**: February 15, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Strategy](#deployment-strategy)
4. [Phase 1: Shadow Mode](#phase-1-shadow-mode)
5. [Phase 2: Soft Launch](#phase-2-soft-launch)
6. [Phase 3: Full Activation](#phase-3-full-activation)
7. [Monitoring and Alerts](#monitoring-and-alerts)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The MOE Intelligence Layer deployment follows a **phased rollout strategy** to minimize risk and ensure system stability. The deployment progresses through three phases:

1. **Shadow Mode**: MOE runs alongside existing system without affecting verdicts
2. **Soft Launch**: MOE handles 10-50% of traffic with gradual increase
3. **Full Activation**: MOE becomes primary verification path for 100% of traffic

---

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Disk**: 10GB free space for telemetry and training data
- **OS**: Linux, macOS, or Windows

### Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

**Key dependencies**:
- `z3-solver>=4.12.0` - Z3 theorem prover
- `hypothesis>=6.0.0` - Property-based testing
- `pytest>=7.0.0` - Testing framework
- `prometheus-client>=0.16.0` - Metrics export

### Database Setup

Initialize MOE databases:

```bash
python scripts/init_databases.py
```

This creates:
- `.DIOTEC360_moe/telemetry.db` - Expert performance metrics
- `.DIOTEC360_moe/training.db` - Ground truth and training data
- `.DIOTEC360_moe/cache.db` - Verdict cache

### Configuration

Set environment variables in `.env`:

```bash
# MOE Configuration
DIOTEC360_MOE_ENABLED=false  # Start disabled
DIOTEC360_MOE_SHADOW_MODE=false
DIOTEC360_MOE_TRAFFIC_PERCENTAGE=0

# Expert Timeouts
DIOTEC360_Z3_TIMEOUT_NORMAL=30000
DIOTEC360_Z3_TIMEOUT_CRISIS=5000
DIOTEC360_SENTINEL_TIMEOUT=100
DIOTEC360_GUARDIAN_TIMEOUT=50

# Consensus Thresholds
DIOTEC360_CONSENSUS_CONFIDENCE_THRESHOLD=0.7
DIOTEC360_CONSENSUS_UNCERTAINTY_THRESHOLD=0.5

# Verdict Caching
DIOTEC360_VERDICT_CACHE_ENABLED=true
DIOTEC360_VERDICT_CACHE_TTL=300

# Telemetry
DIOTEC360_TELEMETRY_DB_PATH=.DIOTEC360_moe/telemetry.db
DIOTEC360_TRAINING_DB_PATH=.DIOTEC360_moe/training.db
```

---

## Deployment Strategy

### Timeline

- **Week 1-2**: Shadow Mode
- **Week 3-4**: Soft Launch (10% → 50%)
- **Week 5-6**: Full Activation (100%)

### Success Criteria

Before progressing to next phase:

1. **Expert Accuracy**: >99.9% for all experts
2. **False Positive Rate**: <0.1%
3. **Latency**: P95 < 500ms
4. **Availability**: >99.9% uptime
5. **No Critical Incidents**: Zero P0/P1 incidents

---

## Phase 1: Shadow Mode

**Duration**: Week 1-2  
**Goal**: Validate MOE accuracy without affecting production

### What Happens

- MOE runs in parallel with existing system
- MOE verdicts are logged but NOT used for decisions
- Existing system continues to make all decisions
- Telemetry collected for comparison

### Deployment Steps

#### 1. Enable Shadow Mode

```bash
python scripts/deploy_moe_shadow_mode.py
```

This script:
- Sets `DIOTEC360_MOE_SHADOW_MODE=true`
- Initializes MOE components
- Starts telemetry collection
- Configures monitoring alerts

#### 2. Verify Shadow Mode Active

```bash
python scripts/verify_shadow_mode.py
```

Expected output:
```
✅ Shadow mode active
✅ MOE components initialized
✅ Telemetry recording
✅ Existing system unaffected
```

#### 3. Monitor Telemetry

```bash
python scripts/monitor_moe.py --mode shadow
```

Key metrics to watch:
- **Agreement Rate**: MOE vs existing system (target: >99%)
- **Expert Latency**: All experts within timeout
- **Expert Availability**: >99.9% uptime
- **False Positives**: <0.1%
- **False Negatives**: <0.01%

#### 4. Generate Shadow Mode Report

After 1 week:

```bash
python scripts/generate_shadow_report.py --days 7
```

Review report for:
- Accuracy comparison with existing system
- Latency distribution
- Expert failure rates
- Consensus patterns

### Decision Point

**Proceed to Soft Launch if**:
- Agreement rate >99%
- No critical bugs discovered
- Latency acceptable (P95 <500ms)
- Expert availability >99.9%

**Stay in Shadow Mode if**:
- Agreement rate <99%
- Critical bugs found
- Latency issues
- Expert instability

---

## Phase 2: Soft Launch

**Duration**: Week 3-4  
**Goal**: Gradually increase MOE traffic from 10% to 50%

### What Happens

- MOE handles percentage of production traffic
- Existing system handles remaining traffic
- Gradual traffic increase based on metrics
- Continuous monitoring and adjustment

### Deployment Steps

#### 1. Start at 10% Traffic

```bash
python scripts/deploy_moe_soft_launch.py --traffic-percentage 10
```

This script:
- Sets `DIOTEC360_MOE_ENABLED=true`
- Sets `DIOTEC360_MOE_TRAFFIC_PERCENTAGE=10`
- Configures traffic routing
- Enables production monitoring

#### 2. Monitor 10% Traffic

Monitor for 24-48 hours:

```bash
python scripts/monitor_moe.py --mode soft-launch --traffic 10
```

Key metrics:
- **Error Rate**: Should match existing system
- **Latency**: P95 <500ms
- **Expert Failures**: <0.1%
- **User Impact**: Zero complaints

#### 3. Increase to 25% Traffic

If 10% successful:

```bash
python scripts/deploy_moe_soft_launch.py --traffic-percentage 25
```

Monitor for 24-48 hours.

#### 4. Increase to 50% Traffic

If 25% successful:

```bash
python scripts/deploy_moe_soft_launch.py --traffic-percentage 50
```

Monitor for 48-72 hours.

#### 5. Generate Soft Launch Report

After reaching 50%:

```bash
python scripts/generate_soft_launch_report.py --days 7
```

Review report for:
- Production accuracy vs shadow mode
- Latency impact on user experience
- Expert failure patterns
- Cache hit rate and effectiveness

### Traffic Increase Guidelines

**Increase traffic if**:
- Current traffic level stable for 24-48 hours
- Error rate matches existing system
- Latency acceptable
- No user complaints

**Decrease traffic if**:
- Error rate increases
- Latency degrades
- Expert failures increase
- User complaints received

**Rollback if**:
- Critical bug discovered
- Error rate >2x existing system
- P0/P1 incident occurs

### Decision Point

**Proceed to Full Activation if**:
- 50% traffic stable for 72 hours
- Error rate matches existing system
- Latency acceptable
- Expert availability >99.9%
- Zero P0/P1 incidents

**Stay in Soft Launch if**:
- Metrics not meeting targets
- Intermittent issues
- Need more data

---

## Phase 3: Full Activation

**Duration**: Week 5-6  
**Goal**: MOE handles 100% of production traffic

### What Happens

- MOE becomes primary verification path
- Existing layers become fallback only
- Full visual dashboard deployment
- Production monitoring at scale

### Deployment Steps

#### 1. Deploy Full Activation

```bash
python scripts/deploy_moe_full_activation.py
```

This script:
- Sets `DIOTEC360_MOE_TRAFFIC_PERCENTAGE=100`
- Enables all MOE features
- Deploys visual dashboard
- Configures production alerts

#### 2. Verify Full Activation

```bash
python scripts/verify_full_activation.py
```

Expected output:
```
✅ MOE handling 100% traffic
✅ All experts operational
✅ Visual dashboard active
✅ Monitoring configured
✅ Alerts configured
```

#### 3. Monitor Production

```bash
python scripts/monitor_moe.py --mode production
```

Key metrics:
- **Throughput**: >1000 tx/s (with caching)
- **Latency**: P95 <500ms
- **Expert Availability**: >99.9%
- **Cache Hit Rate**: >90%
- **Error Rate**: <0.1%

#### 4. Generate Production Report

Daily for first week:

```bash
python scripts/generate_production_report.py --days 1
```

Weekly thereafter:

```bash
python scripts/generate_production_report.py --days 7
```

### Post-Activation Tasks

#### Week 1: Intensive Monitoring

- Monitor metrics every 4 hours
- Review all alerts immediately
- Generate daily reports
- On-call engineer 24/7

#### Week 2-4: Normal Monitoring

- Monitor metrics daily
- Review alerts within 1 hour
- Generate weekly reports
- Standard on-call rotation

#### Month 2+: Steady State

- Monitor metrics weekly
- Review alerts within 4 hours
- Generate monthly reports
- Standard on-call rotation

---

## Monitoring and Alerts

### Monitoring Dashboard

Access monitoring dashboard:

```bash
python scripts/start_monitoring_dashboard.py
```

Dashboard shows:
- Real-time expert status
- Throughput and latency
- Error rates
- Cache hit rate
- Expert availability

### Alert Configuration

Alerts configured in `config/moe_monitoring_alerts.yaml`:

```yaml
alerts:
  - name: expert_failure_rate_high
    condition: expert_failure_rate > 0.1%
    severity: P1
    action: page_oncall
    
  - name: latency_high
    condition: p95_latency > 500ms
    severity: P2
    action: notify_team
    
  - name: expert_unavailable
    condition: expert_availability < 99.9%
    severity: P1
    action: page_oncall
    
  - name: cache_hit_rate_low
    condition: cache_hit_rate < 80%
    severity: P3
    action: notify_team
```

### Prometheus Metrics

Export metrics to Prometheus:

```python
from aethel.moe.telemetry import ExpertTelemetry

telemetry = ExpertTelemetry()
metrics = telemetry.export_prometheus()
```

Key metrics:
- `moe_expert_latency_ms` - Expert latency histogram
- `moe_expert_verdicts_total` - Expert verdict counter
- `moe_consensus_total` - Consensus result counter
- `moe_cache_hit_rate` - Cache hit rate gauge
- `moe_expert_availability` - Expert availability gauge

---

## Rollback Procedures

### Emergency Rollback

If critical issue discovered:

```bash
python scripts/rollback_moe.py --emergency
```

This immediately:
- Sets `DIOTEC360_MOE_ENABLED=false`
- Routes all traffic to existing system
- Preserves telemetry for analysis
- Notifies team

### Gradual Rollback

If non-critical issue:

```bash
python scripts/rollback_moe.py --gradual --target-percentage 25
```

This gradually:
- Reduces MOE traffic to target percentage
- Monitors for stability
- Allows investigation without full rollback

### Rollback Testing

Test rollback procedures monthly:

```bash
python scripts/test_moe_rollback.py
```

Verifies:
- Rollback completes in <60 seconds
- Existing system handles 100% traffic
- No data loss
- Telemetry preserved

---

## Troubleshooting

### Issue: High Expert Failure Rate

**Symptoms**:
- Expert failure rate >0.1%
- Alerts firing frequently

**Diagnosis**:
```bash
python scripts/diagnose_expert_failures.py --expert Z3_Expert
```

**Common Causes**:
- Timeout too aggressive
- Resource exhaustion
- Invalid input patterns

**Solutions**:
1. Increase expert timeout
2. Add resource limits
3. Improve input validation

### Issue: High Latency

**Symptoms**:
- P95 latency >500ms
- User complaints

**Diagnosis**:
```bash
python scripts/diagnose_latency.py
```

**Common Causes**:
- Cache disabled or low hit rate
- Expert timeout too high
- Too many experts activated

**Solutions**:
1. Enable verdict caching
2. Optimize expert timeouts
3. Tune gating network routing

### Issue: Low Cache Hit Rate

**Symptoms**:
- Cache hit rate <80%
- High latency

**Diagnosis**:
```bash
python scripts/diagnose_cache.py
```

**Common Causes**:
- TTL too short
- Cache size too small
- High transaction diversity

**Solutions**:
1. Increase cache TTL
2. Increase cache size
3. Implement cache warming

### Issue: Expert Disagreement

**Symptoms**:
- MOE verdict differs from existing system
- User confusion

**Diagnosis**:
```bash
python scripts/diagnose_disagreement.py --tx-id <transaction_id>
```

**Common Causes**:
- Expert bug
- Edge case not covered
- Threshold misconfiguration

**Solutions**:
1. Review expert logic
2. Add test case
3. Adjust confidence thresholds

---

## Best Practices

### 1. Monitor Continuously

- Set up automated monitoring
- Review metrics daily during rollout
- Investigate all anomalies

### 2. Test Thoroughly

- Run full test suite before deployment
- Test rollback procedures
- Validate in staging environment

### 3. Communicate Clearly

- Notify team before each phase
- Document all changes
- Share metrics and reports

### 4. Iterate Carefully

- Don't rush phase transitions
- Collect sufficient data
- Learn from each phase

### 5. Maintain Fallback

- Keep existing system operational
- Test fallback regularly
- Document rollback procedures

---

## Support

### Documentation

- **MOE Guide**: `MOE_GUIDE.md`
- **API Reference**: `API_REFERENCE_MOE_V2_1_0.md`
- **Migration Guide**: `MIGRATION_GUIDE_V2_1.md`

### Scripts

- **Deployment**: `scripts/deploy_moe_*.py`
- **Monitoring**: `scripts/monitor_moe.py`
- **Rollback**: `scripts/rollback_moe.py`
- **Diagnostics**: `scripts/diagnose_*.py`

### Contact

- **Issues**: https://github.com/diotec360/aethel/issues
- **Discussions**: https://github.com/diotec360/aethel/discussions
- **Email**: support@aethel.ai

---

**Author**: Kiro AI - Engenheiro-Chefe  
**Date**: February 15, 2026  
**Version**: v2.1.0 "The MOE Intelligence Layer"  
**Status**: 🏛️ READY FOR DEPLOYMENT
