# Diotec360 Performance Benchmarks

This directory contains performance benchmarking tools for Aethel. These benchmarks measure key performance characteristics and provide objective data for evaluating Aethel's capabilities.

## Benchmark Categories

### 1. Proof Generation (`proof_generation.py`)
Measures the time required to generate mathematical proofs for various transaction types and complexities.

### 2. Transaction Throughput (`transaction_throughput.py`)
Measures the number of transactions that can be processed per second under various load conditions.

### 3. Parallel Execution (`parallel_execution.py`)
Measures the performance gains from parallel transaction execution and scaling behavior.

## Running Benchmarks

### Run All Benchmarks
```bash
python benchmarks/run_all.py
```

### Run Individual Benchmarks
```bash
python benchmarks/proof_generation.py
python benchmarks/transaction_throughput.py
python benchmarks/parallel_execution.py
```

### Run on Your Infrastructure
All benchmarks can be run on your own infrastructure to validate performance characteristics in your environment.

## Benchmark Results

Results are saved in JSON format in the `results/` directory with timestamps. See the [Benchmark Documentation](../docs/benchmarks/methodology.md) for detailed methodology and published results.

## Requirements

- Python 3.8+
- Diotec360 core installed
- At least 4GB RAM recommended
- Multi-core CPU recommended for parallel execution benchmarks

## Interpreting Results

Each benchmark produces:
- **Mean**: Average performance across all iterations
- **Median**: Middle value, less affected by outliers
- **P95/P99**: 95th and 99th percentile latencies
- **Throughput**: Operations per second
- **Scaling Factor**: Performance improvement with parallelization

See the [Performance Documentation](../docs/benchmarks/performance-characteristics.md) for detailed interpretation guidance.
