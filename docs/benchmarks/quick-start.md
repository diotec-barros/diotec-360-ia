# Benchmark Quick Start Guide

Get started with Diotec360 Performance benchmarking in 5 minutes.

## Quick Start

### 1. Install Aethel

```bash
pip install aethel
```

### 2. Clone Repository

```bash
git clone https://github.com/diotec360/aethel.git
cd aethel
```

### 3. Run Benchmarks

```bash
python benchmarks/run_all.py
```

That's it! Results will be saved to `benchmarks/results/`.

## What Gets Measured

### Proof Generation
- Simple transfer proofs: ~2-5ms
- Complex DeFi proofs: ~10-20ms
- Conservation validation: <1ms

### Transaction Throughput
- Sequential: 500-1000 TPS
- Parallel (8 cores): 4000-8000 TPS
- Mixed workload: 300-600 TPS

### Parallel Execution
- Scaling efficiency: 70-95%
- Conflict detection overhead: <10%
- Batch processing gains: 2-10x

## Individual Benchmarks

### Proof Generation Only

```bash
python benchmarks/proof_generation.py
```

**Duration**: ~30 seconds

### Throughput Only

```bash
python benchmarks/transaction_throughput.py
```

**Duration**: ~60 seconds

### Parallel Execution Only

```bash
python benchmarks/parallel_execution.py
```

**Duration**: ~90 seconds

## Understanding Results

### Good Performance Indicators

✅ **Proof Generation**:
- Mean <5ms for simple transfers
- P99 <10ms for simple transfers
- Mean <20ms for complex DeFi

✅ **Throughput**:
- Sequential >500 TPS
- Parallel (8 cores) >4000 TPS
- Stable over time (<5% variance)

✅ **Parallel Scaling**:
- 4 cores: >3x speedup
- 8 cores: >6x speedup
- Efficiency >70%

### Performance Issues

⚠️ **Low Throughput** (<500 TPS):
- Check CPU utilization
- Close background applications
- Verify SSD storage

⚠️ **High Latency** (P99 >50ms):
- Reduce transaction complexity
- Check memory availability
- Profile execution

⚠️ **Poor Scaling** (<60% efficiency):
- Check for conflicts
- Verify CPU core count
- Review batch sizes

## Result Files

Results are saved in JSON format:

```
benchmarks/results/
├── proof_generation_20240101_120000.json
├── transaction_throughput_20240101_120100.json
├── parallel_execution_20240101_120200.json
└── comprehensive_20240101_120300.json
```

### Example Result

```json
{
  "benchmark": "proof_generation",
  "timestamp": "2024-01-01T12:00:00",
  "iterations": 100,
  "tests": [
    {
      "test": "simple_transfer",
      "mean_ms": 2.34,
      "median_ms": 2.21,
      "p95_ms": 3.89,
      "p99_ms": 5.12
    }
  ]
}
```

## Comparing Results

### Against Reference System

Reference system (Intel i7-9700K, 8 cores):
- Sequential: 821 TPS
- Parallel: 5,618 TPS
- Simple proof: 2.34ms mean

Calculate your relative performance:

```python
your_tps = 650
reference_tps = 821
print(f"Performance: {(your_tps/reference_tps)*100:.1f}%")
# Output: Performance: 79.2%
```

### Between Runs

Compare two result files:

```python
import json

with open('results/run1.json') as f:
    run1 = json.load(f)
with open('results/run2.json') as f:
    run2 = json.load(f)

tps1 = run1['tests'][0]['tps']
tps2 = run2['tests'][0]['tps']
change = ((tps2 - tps1) / tps1) * 100

print(f"Change: {change:+.1f}%")
```

## System Requirements

### Minimum

- CPU: 4 cores, 2.0 GHz
- RAM: 4 GB
- Storage: Any SSD
- Python: 3.8+

### Recommended

- CPU: 8+ cores, 3.0+ GHz
- RAM: 16 GB
- Storage: NVMe SSD
- Python: 3.10+

## Tips for Accurate Results

1. **Close Background Apps**: Ensure system is at idle
2. **Run Multiple Times**: Average 3-5 runs for accuracy
3. **Check Temperature**: Avoid thermal throttling
4. **Use Power Mode**: Set to high performance
5. **Disable Power Saving**: Prevent CPU frequency scaling

## Next Steps

- [Detailed Methodology](methodology.md)
- [Performance Characteristics](performance-characteristics.md)
- [Published Results](results.md)
- [Optimization Guide](../advanced/performance-optimization.md)

## Getting Help

- [GitHub Issues](https://github.com/diotec360/diotec360/issues)
- [Community Forum](https://forum.aethel.io)
- [Documentation](https://docs.aethel.io)
- Email: support@diotec360.com
