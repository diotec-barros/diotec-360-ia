# Benchmark Methodology

This document describes the methodology used for Diotec360 Performance benchmarking, ensuring reproducible and objective measurements.

## Overview

Aethel benchmarks measure three key performance areas:
1. **Proof Generation**: Time to generate mathematical proofs
2. **Transaction Throughput**: Transactions processed per second
3. **Parallel Execution**: Performance scaling across multiple cores

## Benchmark Environment

### Hardware Requirements

**Minimum Specifications:**
- CPU: 4 cores, 2.0 GHz
- RAM: 4 GB
- Storage: SSD recommended

**Recommended Specifications:**
- CPU: 8+ cores, 3.0+ GHz
- RAM: 16 GB
- Storage: NVMe SSD

### Software Requirements

- Python 3.8 or higher
- Diotec360 core installed
- No other CPU-intensive processes running
- System at idle before benchmarking

## Benchmark Categories

### 1. Proof Generation Benchmarks

**Purpose**: Measure the time required to generate mathematical proofs for various transaction types.

**Methodology**:
- Run 100 iterations per test
- Measure time from proof request to proof completion
- Calculate mean, median, P95, P99 latencies
- Test multiple complexity levels

**Test Cases**:

#### Simple Transfer
- Basic account-to-account transfer
- Single balance check
- Two balance updates
- Expected: <5ms per proof

#### Complex DeFi
- Multi-step DeFi operation
- Conservation law validation
- Price impact calculation
- Slippage protection
- Expected: <20ms per proof

#### Conservation Validation
- Validate conservation laws across multiple accounts
- Check total balance preservation
- Expected: <1ms per validation

**Metrics Collected**:
- Mean latency (ms)
- Median latency (ms)
- P95 latency (ms)
- P99 latency (ms)
- Standard deviation
- Min/max latencies

### 2. Transaction Throughput Benchmarks

**Purpose**: Measure the number of transactions that can be processed per second under various load conditions.

**Methodology**:
- Run for 10 seconds per test
- Count total transactions processed
- Calculate transactions per second (TPS)
- Test multiple load patterns

**Test Cases**:

#### Sequential Throughput
- Process transactions one at a time
- Baseline for comparison
- Expected: 500-1000 TPS

#### Burst Throughput
- Process transactions in bursts
- Test burst sizes: 10, 50, 100, 500, 1000
- Measure TPS for each burst size
- Expected: Higher TPS for larger bursts

#### Sustained Load
- Continuous transaction processing
- Measure TPS per second over 10 seconds
- Calculate mean, min, max TPS
- Expected: Consistent TPS over time

#### Mixed Workload
- 50% simple transfers
- 30% DeFi swaps
- 20% complex proofs
- Realistic production workload
- Expected: 300-600 TPS

**Metrics Collected**:
- Transactions per second (TPS)
- Average latency (ms)
- Throughput stability (standard deviation)
- Transactions by type

### 3. Parallel Execution Benchmarks

**Purpose**: Measure performance gains from parallel transaction execution and scaling behavior.

**Methodology**:
- Process 1000 transactions per test
- Vary number of worker threads
- Measure scaling efficiency
- Test conflict detection overhead

**Test Cases**:

#### Sequential Baseline
- Single-threaded execution
- Baseline for scaling comparison
- Expected: 500-1000 TPS

#### Parallel Scaling
- Test with 2, 4, 8, 16, max_cores workers
- Calculate scaling factor vs baseline
- Calculate efficiency percentage
- Expected: Near-linear scaling for independent transactions

#### Batch Processing
- Process transactions in batches
- Test batch sizes: 10, 50, 100, 500
- Measure batches per second
- Expected: Higher throughput with larger batches

#### Conflict Detection
- Test with 0%, 10%, 25%, 50% conflict rates
- Measure overhead of conflict detection
- Expected: Graceful degradation with conflicts

#### Scaling Efficiency
- Test with 100, 500, 1000, 5000, 10000 transactions
- Measure TPS and latency at each scale
- Expected: Consistent performance across scales

**Metrics Collected**:
- Transactions per second (TPS)
- Scaling factor (vs sequential)
- Efficiency percentage
- Average latency (ms)
- Conflict detection overhead

## Measurement Techniques

### Timing

All timing measurements use `time.perf_counter()` for high-resolution timing:

```python
start = time.perf_counter()
# ... operation ...
duration = time.perf_counter() - start
```

### Statistical Analysis

For each benchmark:
- **Mean**: Average performance across all iterations
- **Median**: Middle value, less affected by outliers
- **P95**: 95th percentile (95% of operations complete within this time)
- **P99**: 99th percentile (99% of operations complete within this time)
- **Standard Deviation**: Measure of variability

### Warm-up Period

Each benchmark includes a warm-up phase:
- Run 10 iterations before measurement
- Allows JIT compilation and cache warming
- Ensures stable measurements

## Result Interpretation

### Latency Targets

| Operation | Target | Good | Excellent |
|-----------|--------|------|-----------|
| Simple Transfer Proof | <10ms | <5ms | <2ms |
| Complex DeFi Proof | <50ms | <20ms | <10ms |
| Conservation Validation | <5ms | <1ms | <0.5ms |

### Throughput Targets

| Workload | Target | Good | Excellent |
|----------|--------|------|-----------|
| Sequential | >500 TPS | >1000 TPS | >2000 TPS |
| Parallel (8 cores) | >2000 TPS | >4000 TPS | >8000 TPS |
| Mixed Workload | >300 TPS | >600 TPS | >1000 TPS |

### Scaling Efficiency

| Workers | Target Efficiency | Good | Excellent |
|---------|------------------|------|-----------|
| 2 cores | >80% | >90% | >95% |
| 4 cores | >70% | >80% | >90% |
| 8 cores | >60% | >70% | >80% |

Efficiency = (Actual Speedup / Ideal Speedup) × 100%

## Reproducibility

### Running Benchmarks

```bash
# Run all benchmarks
python benchmarks/run_all.py

# Run individual benchmarks
python benchmarks/proof_generation.py
python benchmarks/transaction_throughput.py
python benchmarks/parallel_execution.py
```

### Result Files

Results are saved in JSON format:
- `benchmarks/results/proof_generation_YYYYMMDD_HHMMSS.json`
- `benchmarks/results/transaction_throughput_YYYYMMDD_HHMMSS.json`
- `benchmarks/results/parallel_execution_YYYYMMDD_HHMMSS.json`
- `benchmarks/results/comprehensive_YYYYMMDD_HHMMSS.json`

### Comparing Results

To compare results across runs:
1. Run benchmarks on same hardware
2. Ensure system is at idle
3. Run multiple times and average results
4. Compare JSON result files

## Limitations

### Known Limitations

1. **Mock Implementations**: Some benchmarks use mock implementations when Aethel components are not available
2. **Network Overhead**: Benchmarks do not include network latency
3. **Disk I/O**: Benchmarks assume in-memory operations
4. **Consensus**: Benchmarks do not include consensus protocol overhead

### Real-World Considerations

Production performance may differ due to:
- Network latency
- Disk I/O
- Consensus protocol overhead
- Database operations
- Concurrent user load
- System resource contention

## Continuous Benchmarking

### CI/CD Integration

Benchmarks run automatically on:
- Every commit to main branch
- Pull requests
- Release candidates

### Performance Regression Detection

Automated alerts trigger when:
- Throughput decreases >10%
- Latency increases >20%
- Scaling efficiency decreases >15%

## References

- [Performance Characteristics](performance-characteristics.md)
- [Benchmark Results](results.md)
- [Optimization Guide](../advanced/performance-optimization.md)
