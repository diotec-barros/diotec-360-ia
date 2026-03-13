# Cross-Platform Testing Guide: RVC-003 & RVC-004

## Overview

This guide provides instructions for running the complete RVC-003 & RVC-004 test suite across all supported platforms: Linux, Windows, and macOS.

## Platform Status

- ✅ **Windows**: Complete (Task 12.2)
- ⏳ **Linux**: Pending execution (Task 12.1)
- ⏳ **macOS**: Pending execution (Task 12.3)

## Prerequisites

### All Platforms
- Python 3.8+
- pytest
- hypothesis (for property-based tests)

### Platform-Specific Requirements

**Linux:**
- GCC compiler (for pthread support)
- `libpthread` development headers

**Windows:**
- Windows 10+ (for GetThreadTimes API)
- Visual C++ Runtime

**macOS:**
- macOS 10.14+ (for thread_info API)
- Xcode Command Line Tools

## Installation

```bash
# Install Python dependencies
pip install pytest hypothesis psutil

# Linux-specific (if needed)
sudo apt-get install build-essential libpthread-stubs0-dev

# macOS-specific (if needed)
xcode-select --install
```

## Test Execution

### Quick Test (All Platforms)

Run the minimal test suite to verify basic functionality:

```bash
python run_cross_platform_tests.py --quick
```

### Full Test Suite (All Platforms)

Run the complete test suite including all unit tests, integration tests, and stress tests:

```bash
python run_cross_platform_tests.py --full
```

### Platform-Specific Tests

Run only the platform-specific thread CPU accounting tests:

```bash
# Linux
python -m pytest test_thread_cpu_linux.py -v

# Windows
python -m pytest test_thread_cpu_windows.py -v

# macOS
python -m pytest test_thread_cpu_macos.py -v
```

### Benchmark Tests

Run performance benchmarks to measure overhead:

```bash
# Atomic commit overhead
python benchmark_atomic_commit.py

# Thread CPU accounting overhead
python benchmark_thread_cpu_overhead.py
```

## Test Categories

### 1. Atomic Commit Tests (RVC-003)

**Core Tests:**
- `test_rvc_003_atomic_commit.py` - Basic atomic commit functionality
- `test_crash_recovery.py` - Crash recovery protocol
- `test_power_failure_simulation.py` - Power failure simulation (1000 iterations)
- `test_power_failure_fast.py` - Fast power failure test (100 iterations)

**Integration Tests:**
- `test_task_9_state_store_integration.py` - StateStore integration

**Expected Results:**
- All atomic commit operations should be atomic (no partial states)
- Crash recovery should restore consistent state
- Merkle Root integrity should be maintained
- 100% success rate on power failure simulations

### 2. Thread CPU Accounting Tests (RVC-004)

**Platform-Specific Tests:**
- `test_thread_cpu_linux.py` - Linux pthread APIs
- `test_thread_cpu_windows.py` - Windows GetThreadTimes API
- `test_thread_cpu_macos.py` - macOS thread_info API
- `test_thread_cpu_platform.py` - Platform detection and abstraction

**Core Tests:**
- `test_rvc_004_thread_cpu_accounting.py` - Basic thread CPU tracking
- `test_attack_generation_harness.py` - Sub-millisecond attack generation
- `test_concurrent_thread_attacks.py` - Concurrent thread attack detection

**Integration Tests:**
- `test_sentinel_thread_cpu_integration.py` - Sentinel integration
- `test_checkpoint_8_submillisecond.py` - Sub-millisecond detection validation

**Expected Results:**
- Thread CPU time measurement should work on all platforms
- Sub-millisecond attacks should be detected (100% detection rate)
- Zero measurable overhead in normal operation
- Concurrent thread tracking should work independently

### 3. Integration Tests

**Complete System Tests:**
- `test_task_9_state_store_integration.py` - Full StateStore integration
- `test_sentinel_thread_cpu_integration.py` - Sentinel integration
- `test_thread_cpu_integration.py` - Thread CPU accounting integration

**Expected Results:**
- All components should work together seamlessly
- No regressions in existing functionality
- Performance targets should be met

## Performance Targets

### Atomic Commit (RVC-003)
- **Write Latency Overhead**: < 10%
- **Crash Recovery Time**: < 1 second for typical workloads
- **WAL Overhead**: < 5% disk space

### Thread CPU Accounting (RVC-004)
- **Runtime Overhead**: 0% (zero measurable impact)
- **Detection Latency**: < 1ms
- **Memory Overhead**: < 1MB per 1000 threads

## Platform-Specific Notes

### Linux

**Thread CPU Time API:**
- Uses `pthread_getcpuclockid()` + `clock_gettime(CLOCK_THREAD_CPUTIME_ID)`
- Requires `libpthread`
- Sub-nanosecond precision available

**Known Issues:**
- Some older kernels may not support CLOCK_THREAD_CPUTIME_ID
- Container environments may have limited access to thread CPU time

**Verification:**
```bash
# Check if thread CPU time is supported
python -c "import time; print(time.CLOCK_THREAD_CPUTIME_ID)"
```

### Windows

**Thread CPU Time API:**
- Uses `GetThreadTimes()` from kernel32.dll
- Returns user time and kernel time separately
- 100-nanosecond precision

**Known Issues:**
- Requires Windows 10+ for reliable thread CPU time
- Some virtualized environments may have reduced precision

**Verification:**
```powershell
# Check Windows version
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
```

### macOS

**Thread CPU Time API:**
- Uses `thread_info()` with `THREAD_BASIC_INFO`
- Returns user time and system time
- Microsecond precision

**Known Issues:**
- Requires macOS 10.14+ (Mojave)
- Some sandboxed applications may have restricted access

**Verification:**
```bash
# Check macOS version
sw_vers
```

## Troubleshooting

### Test Failures

**Atomic Commit Tests Failing:**
1. Check disk space (WAL requires space)
2. Verify filesystem supports atomic rename (most modern filesystems do)
3. Check file permissions on test directories

**Thread CPU Accounting Tests Failing:**
1. Verify platform detection is correct
2. Check that platform-specific APIs are available
3. Ensure sufficient CPU resources (tests may fail on heavily loaded systems)

**Performance Tests Failing:**
1. Close other applications to reduce system load
2. Run tests multiple times to account for variance
3. Check if system is throttling CPU (thermal issues)

### Platform Detection Issues

If platform detection fails:

```python
import platform
print(f"System: {platform.system()}")
print(f"Release: {platform.release()}")
print(f"Machine: {platform.machine()}")
```

Expected outputs:
- Linux: `System: Linux`
- Windows: `System: Windows`
- macOS: `System: Darwin`

## Reporting Results

After running tests on each platform, document results in the following format:

### Platform: [Linux/Windows/macOS]

**System Information:**
- OS Version: [version]
- Python Version: [version]
- CPU: [model]
- RAM: [amount]

**Test Results:**
- Total Tests: [count]
- Passed: [count]
- Failed: [count]
- Skipped: [count]

**Performance Benchmarks:**
- Atomic Commit Overhead: [percentage]
- Thread CPU Overhead: [percentage]
- Detection Latency: [milliseconds]

**Issues Encountered:**
- [List any issues or anomalies]

**Conclusion:**
- [Pass/Fail with explanation]

## Next Steps

After completing cross-platform testing:

1. ✅ Verify all tests pass on all platforms
2. ✅ Document any platform-specific issues
3. ✅ Update implementation if needed
4. ✅ Proceed to Task 13 (Performance Benchmarking)

## References

- Requirements: `.kiro/specs/rvc-003-004-fixes/requirements.md`
- Design: `.kiro/specs/rvc-003-004-fixes/design.md`
- Tasks: `.kiro/specs/rvc-003-004-fixes/tasks.md`
- Windows Test Report: `WINDOWS_PLATFORM_TEST_REPORT.md`
