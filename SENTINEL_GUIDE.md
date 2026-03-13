# Autonomous Sentinel Operator Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Configuration](#configuration)
4. [Monitoring and Alerting](#monitoring-and-alerting)
5. [Crisis Mode Management](#crisis-mode-management)
6. [Quarantine System](#quarantine-system)
7. [Self-Healing Engine](#self-healing-engine)
8. [Adversarial Vaccine](#adversarial-vaccine)
9. [Troubleshooting](#troubleshooting)
10. [Performance Tuning](#performance-tuning)
11. [Security Best Practices](#security-best-practices)

## Introduction

The Autonomous Sentinel v1.9.0 transforms Aethel from a passive fortress into an autonomous self-protecting entity. This guide provides operators with everything needed to deploy, monitor, and maintain the Sentinel in production environments.

### Key Capabilities
- **Real-time Telemetry**: Monitor CPU, memory, and Z3 solver metrics per transaction
- **Anomaly Detection**: Statistical analysis to identify suspicious behavior
- **Crisis Mode**: Automatic defensive posture during attacks
- **Quarantine Isolation**: Segregate suspicious transactions without halting the system
- **Self-Healing**: Automatic rule generation from attack traces
- **Adversarial Vaccine**: Proactive testing with 1000+ attack scenarios

### Performance Impact
- Normal mode overhead: <5%
- Semantic analysis latency: <100ms
- Throughput preservation: ≥95% of v1.8.0

## Architecture Overview

### Component Stack

```
┌─────────────────────────────────────────────────────────┐
│                   Transaction Input                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Sentinel Monitor (Telemetry)                │
│  • Start transaction tracking                            │
│  • Record baseline metrics                               │
│  • Calculate anomaly scores                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Semantic Sanitizer (Layer -1)                    │
│  • AST parsing and entropy calculation                   │
│  • Trojan pattern detection                              │
│  • High entropy rejection                                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─── PASS ───┐
                     │             │
                     ▼             ▼
              ┌──────────┐   ┌──────────┐
              │ Crisis?  │   │ Normal   │
              │ PoW Gate │   │ Path     │
              └────┬─────┘   └────┬─────┘
                   │              │
                   └──────┬───────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Quarantine System                           │
│  • Batch segmentation (normal vs suspicious)            │
│  • Parallel execution in isolated contexts               │
│  • Merkle amputation for failed transactions             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         Existing Defense Layers (0-4)                    │
│  Layer 0: Input Sanitizer                                │
│  Layer 1: Conservation Checker                           │
│  Layer 2: Overflow Detector                              │
│  Layer 3: Z3 Formal Verifier                             │
│  Layer 4: ZKP Privacy Layer                              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Gauntlet Report (Logging)                   │
│  • Attack forensics                                      │
│  • Compliance reporting                                  │
│  • Statistics aggregation                                │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Transaction Arrival**: Sentinel Monitor starts tracking
2. **Semantic Analysis**: AST parsing, entropy calculation, pattern matching
3. **Crisis Check**: If Crisis Mode active, validate PoW
4. **Quarantine Decision**: Segment batch based on anomaly scores
5. **Parallel Execution**: Normal and quarantine batches execute simultaneously
6. **Layer Processing**: All 5 defense layers execute in sequence
7. **Telemetry Collection**: Metrics recorded from all layers
8. **Logging**: Rejections logged to Gauntlet Report

## Configuration

### Environment Variables

```bash
# Core Sentinel Settings
DIOTEC360_SENTINEL_ENABLED=true
DIOTEC360_SENTINEL_DB_PATH=./data/telemetry.db

# Crisis Mode Thresholds
DIOTEC360_CRISIS_ANOMALY_THRESHOLD=0.10      # 10% anomaly rate
DIOTEC360_CRISIS_REQUEST_THRESHOLD=1000      # 1000 req/s
DIOTEC360_CRISIS_COOLDOWN_SECONDS=120        # 2 minutes

# Semantic Sanitizer
DIOTEC360_PATTERN_DB_PATH=./data/trojan_patterns.json
DIOTEC360_ENTROPY_THRESHOLD=0.8              # 0.0-1.0
DIOTEC360_SEMANTIC_TIMEOUT_MS=100            # 100ms max

# Adaptive Rigor
DIOTEC360_NORMAL_Z3_TIMEOUT=30               # 30 seconds
DIOTEC360_CRISIS_Z3_TIMEOUT=5                # 5 seconds
DIOTEC360_POW_BASE_DIFFICULTY=4              # 4 leading zeros
DIOTEC360_POW_MAX_DIFFICULTY=8               # 8 leading zeros

# Quarantine System
DIOTEC360_QUARANTINE_CAPACITY=100            # Max 100 concurrent
DIOTEC360_QUARANTINE_THRESHOLD=0.7           # Anomaly score threshold

# Self-Healing
DIOTEC360_SELF_HEALING_ENABLED=true
DIOTEC360_RULE_EFFECTIVENESS_THRESHOLD=0.7   # 70% effectiveness
DIOTEC360_HISTORICAL_TX_LIMIT=1000           # For false positive testing

# Adversarial Vaccine
DIOTEC360_VACCINE_ENABLED=false              # Disabled by default
DIOTEC360_VACCINE_SCHEDULE="0 2 * * *"       # Daily at 2 AM
DIOTEC360_VACCINE_SCENARIOS=1000             # 1000 scenarios per session

# Gauntlet Report
DIOTEC360_GAUNTLET_DB_PATH=./data/gauntlet.db
DIOTEC360_RETENTION_DAYS=90                  # 90-day retention
```

### Configuration Files

#### trojan_patterns.json

```json
{
  "patterns": [
    {
      "pattern_id": "trojan_001",
      "name": "Infinite Loop Trojan",
      "ast_signature": "WHILE_LOOP{condition:CONSTANT(True),body:ANY}",
      "severity": 0.9,
      "description": "While loop with constant True condition",
      "active": true,
      "created_at": 1707148800.0
    },
    {
      "pattern_id": "trojan_002",
      "name": "Infinite Recursion",
      "ast_signature": "RECURSIVE_CALL{base_case:NONE}",
      "severity": 0.95,
      "description": "Recursive function without base case",
      "active": true,
      "created_at": 1707148800.0
    }
  ],
  "version": "1.9.0",
  "last_updated": 1707148800.0
}
```

## Monitoring and Alerting

### Key Metrics

#### Sentinel Monitor Metrics
- `sentinel.transactions.total`: Total transactions processed
- `sentinel.transactions.anomalous`: Transactions flagged as anomalous
- `sentinel.anomaly_rate`: Percentage of anomalous transactions
- `sentinel.crisis_mode.active`: Boolean (0 or 1)
- `sentinel.crisis_mode.activations`: Count of Crisis Mode activations
- `sentinel.avg_cpu_time_ms`: Average CPU time per transaction
- `sentinel.avg_memory_delta_mb`: Average memory delta per transaction
- `sentinel.avg_z3_duration_ms`: Average Z3 solver duration

#### Semantic Sanitizer Metrics
- `sanitizer.rejections.total`: Total rejections
- `sanitizer.rejections.high_entropy`: Rejections due to high entropy
- `sanitizer.rejections.trojan_pattern`: Rejections due to pattern match
- `sanitizer.avg_analysis_time_ms`: Average analysis time
- `sanitizer.patterns.active`: Number of active patterns

#### Quarantine System Metrics
- `quarantine.transactions.isolated`: Transactions in quarantine
- `quarantine.capacity.used`: Current capacity usage
- `quarantine.capacity.max`: Maximum capacity
- `quarantine.reintegrations`: Successful reintegrations
- `quarantine.amputations`: Merkle amputations performed

#### Self-Healing Metrics
- `self_healing.rules.generated`: Total rules generated
- `self_healing.rules.active`: Currently active rules
- `self_healing.rules.deactivated`: Rules deactivated due to low effectiveness
- `self_healing.avg_effectiveness`: Average rule effectiveness score

### Alert Thresholds

#### Critical Alerts (Immediate Action Required)
```yaml
- name: Crisis Mode Activated
  condition: sentinel.crisis_mode.active == 1
  severity: CRITICAL
  action: Page on-call engineer
  
- name: Quarantine Capacity Critical
  condition: quarantine.capacity.used / quarantine.capacity.max > 0.9
  severity: CRITICAL
  action: Scale quarantine capacity or reject new transactions
  
- name: Sentinel Overhead High
  condition: sentinel.overhead_pct > 10
  severity: CRITICAL
  action: Investigate performance degradation
```

#### Warning Alerts (Monitor Closely)
```yaml
- name: Anomaly Rate Elevated
  condition: sentinel.anomaly_rate > 0.05
  severity: WARNING
  action: Monitor for potential attack
  
- name: False Positive Rate High
  condition: self_healing.false_positive_rate > 0.01
  severity: WARNING
  action: Review recent rules for over-blocking
  
- name: Semantic Analysis Slow
  condition: sanitizer.avg_analysis_time_ms > 80
  severity: WARNING
  action: Optimize pattern database or increase timeout
```

#### Info Alerts (Informational)
```yaml
- name: Crisis Mode Deactivated
  condition: sentinel.crisis_mode.active == 0 (after being 1)
  severity: INFO
  action: Log event, no action required
  
- name: New Self-Healing Rule
  condition: self_healing.rules.generated increases
  severity: INFO
  action: Review new rule in next maintenance window
```

### Monitoring Dashboard

Recommended dashboard layout (Grafana, Datadog, etc.):

```
┌─────────────────────────────────────────────────────────┐
│                  Sentinel Overview                       │
├─────────────────────────────────────────────────────────┤
│  Crisis Mode: [NORMAL]    Anomaly Rate: [2.3%]          │
│  Throughput: [1,234 tx/s] Overhead: [3.2%]              │
└─────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│  Anomaly Rate (24h)  │  Crisis Mode Activations (7d)    │
│  [Line Graph]        │  [Bar Chart]                     │
└──────────────────────┴──────────────────────────────────┘

┌──────────────────────┬──────────────────────────────────┐
│  Quarantine Status   │  Attack Types (30d)              │
│  Used: 12/100        │  [Pie Chart]                     │
│  [Gauge]             │  - DoS: 45%                      │
│                      │  - Trojan: 30%                   │
│                      │  - Injection: 15%                │
│                      │  - Other: 10%                    │
└──────────────────────┴──────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Recent Attacks (Last 100)                               │
│  [Table: Timestamp, Type, Detection Method, Severity]    │
└─────────────────────────────────────────────────────────┘
```

## Crisis Mode Management

### Activation Triggers

Crisis Mode activates automatically when:
1. **Anomaly Rate**: >10% of transactions in 60-second window
2. **Request Rate**: >1000 requests per second

### Crisis Mode Behavior

When activated:
- Z3 timeout: 30s → 5s (faster rejection of complex attacks)
- Proof depth: deep → shallow (reduce computational cost)
- PoW required: All transactions must include valid Proof of Work
- PoW difficulty: 4-8 leading zeros (scales with attack intensity)
- Notifications: Broadcast to all components within 1 second

### Manual Activation

```python
from aethel.core.sentinel_monitor import SentinelMonitor

sentinel = SentinelMonitor()
sentinel.activate_crisis_mode(reason="Manual activation by operator")
```

### Deactivation

Crisis Mode deactivates automatically when:
- Anomaly rate <2% for 120 consecutive seconds
- Gradual recovery over 60 seconds:
  - Z3 timeout: 5s → 30s (linear increase)
  - PoW required: YES → NO (after 30 seconds)
  - Proof depth: shallow → deep (gradual increase)

### Manual Deactivation

```python
sentinel.deactivate_crisis_mode(reason="Manual deactivation by operator")
```

**⚠️ Warning**: Manual deactivation during an active attack may expose the system to DoS. Only deactivate if you're certain the attack has subsided.

## Quarantine System

### How It Works

1. **Batch Segmentation**: Incoming batch split into normal and suspicious
2. **Parallel Execution**: Both batches execute simultaneously
3. **Isolation**: Suspicious transactions run in separate context
4. **Verification**: All defense layers applied to both batches
5. **Merkle Operations**:
   - Failed transactions: Merkle amputation (remove branch)
   - Successful transactions: Reintegration into main tree

### Capacity Management

Maximum quarantine capacity: 100 concurrent transactions (configurable)

When capacity exceeded:
- New transactions rejected with HTTP 503
- `Retry-After` header indicates wait time
- Clients should implement exponential backoff

### Monitoring Quarantine

```python
from aethel.core.quarantine_system import QuarantineSystem

quarantine = QuarantineSystem()
status = quarantine.get_status()

print(f"Capacity: {status['used']}/{status['max']}")
print(f"Isolated: {status['isolated_count']}")
print(f"Reintegrated: {status['reintegrated_count']}")
print(f"Amputated: {status['amputated_count']}")
```

### Quarantine Log

```python
log = quarantine.get_log(limit=100)
for entry in log:
    print(f"{entry.timestamp}: {entry.tx_id} - {entry.reason}")
```

## Self-Healing Engine

### Rule Generation Process

1. **Attack Detection**: Attack blocked by any layer
2. **Pattern Extraction**: Generalize AST pattern from attack code
3. **False Positive Validation**: Test against 1000 historical transactions
4. **Rule Injection**: If zero false positives, inject into Semantic Sanitizer
5. **Effectiveness Tracking**: Monitor true/false positives over time
6. **Deactivation**: If effectiveness <70%, deactivate rule

### Monitoring Self-Healing

```python
from aethel.core.self_healing import SelfHealingEngine

healing = SelfHealingEngine()
stats = healing.get_statistics()

print(f"Total rules: {stats['total_rules']}")
print(f"Active rules: {stats['active_rules']}")
print(f"Avg effectiveness: {stats['avg_effectiveness']:.2%}")
print(f"Rules generated (24h): {stats['rules_generated_24h']}")
```

### Reviewing Generated Rules

```python
rules = healing.get_recent_rules(limit=10)
for rule in rules:
    print(f"Rule: {rule.pattern.name}")
    print(f"  Severity: {rule.pattern.severity}")
    print(f"  Effectiveness: {rule.effectiveness_score:.2%}")
    print(f"  True positives: {rule.true_positives}")
    print(f"  False positives: {rule.false_positives}")
    print(f"  Active: {rule.active}")
```

### Manual Rule Management

```python
# Deactivate a rule
healing.deactivate_rule("trojan_recursive_lambda")

# Reactivate a rule
healing.activate_rule("trojan_recursive_lambda")

# Delete a rule
healing.delete_rule("trojan_recursive_lambda")
```

## Adversarial Vaccine

### Training Sessions

The Adversarial Vaccine generates 1000 attack scenarios to test defenses:
- 250 mutations of known exploits
- 250 Trojan patterns (legitimate code + hidden malice)
- 250 DoS attacks (resource exhaustion)
- 250 novel attacks (using Architect's creativity)

### Scheduling

```bash
# Cron format: "minute hour day month weekday"
DIOTEC360_VACCINE_SCHEDULE="0 2 * * *"  # Daily at 2 AM
```

### Manual Training

```python
from aethel.core.adversarial_vaccine import AdversarialVaccine

vaccine = AdversarialVaccine()
report = vaccine.run_vaccination(scenarios=1000)

print(f"Total scenarios: {report.total_scenarios}")
print(f"Blocked by Sentinel: {report.blocked_by_sentinel}")
print(f"Blocked by layers: {report.blocked_by_layers}")
print(f"Vulnerabilities found: {report.vulnerabilities_found}")
print(f"Vulnerabilities patched: {report.vulnerabilities_patched}")
```

### Interpreting Results

- **Blocked by Sentinel**: Good! Attacks caught before reaching Judge
- **Blocked by Layers**: Acceptable, but consider generating rules
- **Vulnerabilities Found**: Critical! These attacks reached the Judge
- **Vulnerabilities Patched**: Self-Healing generated rules to fix them

### Best Practices

1. **Run during off-peak hours**: Training uses CPU resources
2. **Monitor production impact**: Ensure <5% throughput degradation
3. **Review vulnerability reports**: Understand what was missed
4. **Adjust scenario count**: Start with 100, increase to 1000 gradually

## Troubleshooting

### High False Positive Rate

**Symptoms**: Legitimate transactions being rejected

**Diagnosis**:
```python
# Check recent rejections
from aethel.core.gauntlet_report import GauntletReport

gauntlet = GauntletReport()
recent = gauntlet.get_recent_attacks(limit=100)

# Look for patterns in rejected transactions
for attack in recent:
    if attack.detection_method == "semantic_sanitizer":
        print(f"Rejected: {attack.code_snippet}")
        print(f"Reason: {attack.reason}")
```

**Solutions**:
1. Review recent Self-Healing rules for over-blocking
2. Deactivate problematic rules
3. Adjust entropy threshold (increase from 0.8 to 0.85)
4. Add legitimate patterns to whitelist

### High Sentinel Overhead

**Symptoms**: Transaction processing >5% slower than v1.8.0

**Diagnosis**:
```python
# Check telemetry overhead
sentinel = SentinelMonitor()
stats = sentinel.get_statistics(time_window=3600)

print(f"Avg CPU time: {stats['avg_cpu_time_ms']}ms")
print(f"Avg memory delta: {stats['avg_memory_delta_mb']}MB")
print(f"Overhead: {stats['overhead_pct']:.2%}")
```

**Solutions**:
1. Optimize pattern database (remove inactive patterns)
2. Increase semantic analysis timeout
3. Disable Adversarial Vaccine during peak hours
4. Scale horizontally (add more nodes)

### Crisis Mode Oscillation

**Symptoms**: Crisis Mode activating/deactivating repeatedly

**Diagnosis**:
```python
# Check Crisis Mode history
transitions = sentinel.get_crisis_mode_transitions(limit=50)
for t in transitions:
    print(f"{t.timestamp}: {t.from_mode} → {t.to_mode} ({t.reason})")
```

**Solutions**:
1. Increase cooldown period (120s → 180s)
2. Adjust anomaly threshold (10% → 15%)
3. Implement rate limiting at load balancer
4. Investigate source of anomalous traffic

### Quarantine Capacity Exceeded

**Symptoms**: HTTP 503 errors with `Retry-After` header

**Diagnosis**:
```python
# Check quarantine capacity
quarantine = QuarantineSystem()
status = quarantine.get_status()

print(f"Capacity: {status['used']}/{status['max']}")
print(f"Avg processing time: {status['avg_processing_time_ms']}ms")
```

**Solutions**:
1. Increase quarantine capacity (100 → 200)
2. Optimize quarantine processing (reduce timeout)
3. Implement client-side retry with exponential backoff
4. Scale quarantine system horizontally

## Performance Tuning

### Optimization Checklist

- [ ] Pattern database optimized (remove inactive patterns)
- [ ] Semantic analysis timeout tuned for workload
- [ ] Quarantine capacity sized for peak load
- [ ] Telemetry collection async (non-blocking)
- [ ] Database indices created for common queries
- [ ] Gauntlet Report cleanup scheduled (90-day retention)
- [ ] Adversarial Vaccine scheduled during off-peak hours

### Benchmarking

```bash
# Run performance benchmarks
python benchmark_sentinel_overhead.py
python benchmark_semantic_sanitizer.py

# Compare with baseline
python -m pytest test_properties_performance.py -v
```

### Scaling Guidelines

| Throughput | Sentinel Nodes | Quarantine Capacity | Pattern DB Size |
|------------|----------------|---------------------|-----------------|
| <100 tx/s  | 1              | 50                  | <100 patterns   |
| 100-500    | 2-3            | 100                 | <200 patterns   |
| 500-1000   | 3-5            | 200                 | <300 patterns   |
| 1000-5000  | 5-10           | 500                 | <500 patterns   |
| >5000      | 10+            | 1000+               | <1000 patterns  |

## Security Best Practices

### Access Control

- Restrict access to Sentinel configuration files
- Use environment variables for sensitive settings
- Implement role-based access control (RBAC) for manual operations
- Audit all manual Crisis Mode activations/deactivations

### Data Protection

- Encrypt telemetry database at rest
- Encrypt Gauntlet Report database at rest
- Sanitize code snippets in logs (remove sensitive data)
- Implement data retention policies (90 days default)

### Incident Response

1. **Detection**: Monitor alerts for Crisis Mode activations
2. **Analysis**: Review Gauntlet Report for attack patterns
3. **Containment**: Verify Crisis Mode active, quarantine working
4. **Eradication**: Self-Healing generates rules automatically
5. **Recovery**: Monitor for Crisis Mode deactivation
6. **Lessons Learned**: Review vaccination reports, adjust thresholds

### Compliance

- Export Gauntlet Reports monthly for auditors
- Maintain 90-day attack logs for regulatory requirements
- Document all manual interventions
- Review Self-Healing rules quarterly

---

## Support

For additional support:
- Documentation: https://aethel.dev/docs/sentinel
- GitHub Issues: https://github.com/diotec360/aethel/issues
- Community Forum: https://forum.aethel.dev
- Email: support@aethel.dev

## Version

This guide is for Autonomous Sentinel v1.9.0
Last updated: February 5, 2026
