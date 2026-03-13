# Benchmark Results

This document provides published benchmark results for Aethel and instructions for running benchmarks on your own infrastructure.

## Reference System

All published results were obtained on the following reference system:

**Hardware**:
- CPU: Intel Core i7-9700K (8 cores @ 3.6 GHz)
- RAM: 32 GB DDR4-3200
- Storage: Samsung 970 EVO Plus NVMe SSD
- Network: 1 Gbps Ethernet

**Software**:
- OS: Ubuntu 22.04 LTS
- Python: 3.10.12
- Aethel: v1.9.0

## Published Results

### Proof Generation Benchmarks

#### Simple Transfer (100 iterations)

| Metric | Value |
|--------|-------|
| Mean | 2.34 ms |
| Median | 2.21 ms |
| P95 | 3.89 ms |
| P99 | 5.12 ms |
| Min | 1.87 ms |
| Max | 8.45 ms |
| Std Dev | 0.67 ms |

**Interpretation**: Simple transfers complete in under 5ms for 99% of cases, suitable for real-time payment processing.

#### Complex DeFi (100 iterations)

| Metric | Value |
|--------|-------|
| Mean | 12.67 ms |
| Median | 11.89 ms |
| P95 | 18.34 ms |
| P99 | 23.56 ms |
| Min | 9.12 ms |
| Max | 31.78 ms |
| Std Dev | 3.45 ms |

**Interpretation**: Complex DeFi operations complete in under 25ms for 99% of cases, enabling high-frequency trading strategies.

#### Conservation Validation (100 iterations)

| Metric | Value |
|--------|-------|
| Mean | 0.45 ms |
| Median | 0.42 ms |
| P95 | 0.78 ms |
| P99 | 1.12 ms |
| Min | 0.34 ms |
| Max | 2.34 ms |
| Std Dev | 0.23 ms |

**Interpretation**: Conservation validation adds minimal overhead (<1ms), ensuring financial correctness without performance penalty.

### Transaction Throughput Benchmarks

#### Sequential Throughput (10 seconds)

| Metric | Value |
|--------|-------|
| Transactions Processed | 8,234 |
| Duration | 10.02 seconds |
| TPS | 821.76 |
| Avg Latency | 1.22 ms |

**Interpretation**: Sequential processing achieves 800+ TPS, suitable for single-user applications and development.

#### Burst Throughput

| Burst Size | Duration | TPS | Avg Latency |
|------------|----------|-----|-------------|
| 10 | 0.012s | 833.33 | 1.20 ms |
| 50 | 0.058s | 862.07 | 1.16 ms |
| 100 | 0.114s | 877.19 | 1.14 ms |
| 500 | 0.562s | 889.68 | 1.12 ms |
| 1000 | 1.118s | 894.45 | 1.12 ms |

**Interpretation**: Larger bursts achieve higher throughput due to reduced overhead, with diminishing returns above 500 transactions.

#### Sustained Load (10 seconds, 1-second intervals)

| Metric | Value |
|--------|-------|
| Mean TPS | 834.56 |
| Median TPS | 836.12 |
| Min TPS | 798.45 |
| Max TPS | 867.23 |
| Std Dev | 18.67 |

**Interpretation**: Throughput remains stable over time with <3% variation, demonstrating predictable performance.

#### Mixed Workload (10 seconds)

| Metric | Value |
|--------|-------|
| Total Transactions | 5,678 |
| Duration | 10.01 seconds |
| Overall TPS | 567.23 |
| Simple Transfers | 2,839 (50%) |
| DeFi Swaps | 1,703 (30%) |
| Complex Proofs | 1,136 (20%) |

**Interpretation**: Mixed workload achieves 567 TPS, representing realistic production performance with diverse transaction types.

### Parallel Execution Benchmarks

#### Sequential Baseline (1000 transactions)

| Metric | Value |
|--------|-------|
| Duration | 1.234 seconds |
| TPS | 810.37 |
| Workers | 1 |

#### Parallel Scaling (1000 transactions)

| Workers | Duration | TPS | Scaling Factor | Efficiency |
|---------|----------|-----|----------------|------------|
| 2 | 0.645s | 1,550.39 | 1.91x | 95.7% |
| 4 | 0.334s | 2,994.01 | 3.69x | 92.4% |
| 8 | 0.178s | 5,617.98 | 6.93x | 86.6% |

**Interpretation**: Near-linear scaling up to 8 cores with >85% efficiency, demonstrating excellent parallelization.

#### Batch Processing (1000 transactions)

| Batch Size | Num Batches | Duration | TPS | Batches/sec |
|------------|-------------|----------|-----|-------------|
| 10 | 100 | 0.123s | 8,130.08 | 813.01 |
| 50 | 20 | 0.098s | 10,204.08 | 204.08 |
| 100 | 10 | 0.089s | 11,235.96 | 112.36 |
| 500 | 2 | 0.084s | 11,904.76 | 23.81 |

**Interpretation**: Batch processing achieves 10,000+ TPS with optimal batch sizes, ideal for bulk operations.

#### Conflict Detection (1000 transactions)

| Conflict Rate | Duration | TPS | Overhead |
|---------------|----------|-----|----------|
| 0% | 0.178s | 5,617.98 | 0% |
| 10% | 0.192s | 5,208.33 | -7.3% |
| 25% | 0.218s | 4,587.16 | -18.3% |
| 50% | 0.267s | 3,745.32 | -33.3% |

**Interpretation**: Conflict detection adds minimal overhead for typical conflict rates (<10%), with graceful degradation at higher rates.

#### Scaling Efficiency (8 workers)

| Transactions | Duration | TPS | Avg Latency |
|--------------|----------|-----|-------------|
| 100 | 0.019s | 5,263.16 | 0.19 ms |
| 500 | 0.091s | 5,494.51 | 0.18 ms |
| 1,000 | 0.178s | 5,617.98 | 0.18 ms |
| 5,000 | 0.887s | 5,636.42 | 0.18 ms |
| 10,000 | 1.769s | 5,653.11 | 0.18 ms |

**Interpretation**: Performance scales linearly with transaction count, maintaining consistent throughput and latency.

## Running Benchmarks on Your Infrastructure

### Prerequisites

1. **Install Aethel**:
```bash
pip install aethel
```

2. **Clone Repository**:
```bash
git clone https://github.com/diotec360/aethel.git
cd aethel
```

3. **Verify Installation**:
```bash
python -c "import aethel; print(aethel.__version__)"
```

### Running All Benchmarks

```bash
python benchmarks/run_all.py
```

This will:
- Run all three benchmark suites
- Save results to `benchmarks/results/`
- Display summary statistics
- Generate comprehensive report

**Expected Duration**: 5-10 minutes

### Running Individual Benchmarks

#### Proof Generation

```bash
python benchmarks/proof_generation.py
```

**Options**:
- `--iterations N`: Number of iterations (default: 100)

**Output**: `benchmarks/results/proof_generation_YYYYMMDD_HHMMSS.json`

#### Transaction Throughput

```bash
python benchmarks/transaction_throughput.py
```

**Options**:
- `--duration N`: Duration in seconds (default: 10)

**Output**: `benchmarks/results/transaction_throughput_YYYYMMDD_HHMMSS.json`

#### Parallel Execution

```bash
python benchmarks/parallel_execution.py
```

**Options**:
- `--transactions N`: Number of transactions (default: 1000)

**Output**: `benchmarks/results/parallel_execution_YYYYMMDD_HHMMSS.json`

### Interpreting Your Results

#### Compare with Reference System

Calculate relative performance:

```python
your_tps = 650  # Your measured TPS
reference_tps = 821  # Reference system TPS
relative_performance = (your_tps / reference_tps) * 100
print(f"Your system: {relative_performance:.1f}% of reference")
```

#### Identify Bottlenecks

**Low TPS (<500)**:
- Check CPU utilization
- Verify no background processes
- Ensure SSD storage
- Check Python version

**High Latency (P99 >50ms)**:
- Reduce transaction complexity
- Increase batch size
- Check memory availability
- Profile code execution

**Poor Scaling (<70% efficiency)**:
- Check for conflicts
- Verify CPU core count
- Monitor thread contention
- Review batch sizes

### Best Practices

1. **System Preparation**:
   - Close unnecessary applications
   - Disable background services
   - Ensure system is at idle
   - Run benchmarks multiple times

2. **Result Validation**:
   - Run benchmarks 3-5 times
   - Calculate average results
   - Check for outliers
   - Compare with reference system

3. **Documentation**:
   - Record hardware specifications
   - Note software versions
   - Document system configuration
   - Save result files

### Troubleshooting

#### Benchmarks Fail to Run

**Error**: `ModuleNotFoundError: No module named 'aethel'`
- **Solution**: Install Aethel: `pip install aethel`

**Error**: `Permission denied`
- **Solution**: Run with appropriate permissions or use virtual environment

#### Results Seem Incorrect

**TPS Much Lower Than Expected**:
- Check CPU utilization during benchmark
- Verify no background processes running
- Ensure adequate RAM available
- Check for thermal throttling

**High Variance in Results**:
- Run benchmarks multiple times
- Ensure system is at idle
- Close unnecessary applications
- Check for system updates running

#### Performance Issues

**Low Throughput**:
- Increase number of workers
- Use batch processing
- Optimize transaction complexity
- Check hardware specifications

**High Latency**:
- Reduce batch size
- Use sequential processing
- Simplify proof constraints
- Check memory usage

## Continuous Benchmarking

### CI/CD Integration

Benchmarks run automatically on:
- Every commit to main branch
- Pull requests
- Release candidates
- Nightly builds

### Performance Tracking

View historical performance data:
- [Performance Dashboard](https://benchmarks.aethel.io)
- [GitHub Actions Results](https://github.com/diotec360/diotec360/actions)
- [Release Performance Reports](https://github.com/diotec360/diotec360/releases)

### Regression Detection

Automated alerts trigger when:
- Throughput decreases >10%
- Latency increases >20%
- Scaling efficiency decreases >15%
- Memory usage increases >25%

## Contributing Benchmark Results

We welcome community benchmark results! To contribute:

1. **Run Benchmarks**: Follow instructions above
2. **Document System**: Record hardware/software specifications
3. **Submit Results**: Create GitHub issue with results
4. **Include Context**: Explain any unusual configurations

**Template**:
```markdown
## System Specifications
- CPU: [model, cores, frequency]
- RAM: [size, type, speed]
- Storage: [type, model]
- OS: [name, version]
- Python: [version]
- Aethel: [version]

## Results
[Attach JSON result files]

## Notes
[Any relevant observations or configurations]
```

## References

- [Benchmark Methodology](methodology.md)
- [Performance Characteristics](performance-characteristics.md)
- [Optimization Guide](../advanced/performance-optimization.md)
- [System Architecture](../architecture/system-overview.md)
