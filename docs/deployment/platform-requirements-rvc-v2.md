# RVC v2 Platform Requirements and Performance Considerations

## Version: v1.9.2 "The Hardening"
## Date: February 23, 2026

---

## Overview

The RVC v2 hardening introduces fail-closed recovery and append-only WAL with fsync durability guarantees. These features prioritize **correctness over performance**, which has platform-specific performance implications.

This document provides guidance for deploying Diotec360 v1.9.2 across different platforms.

---

## Platform Performance Comparison

### WAL Commit Latency by Platform

| Platform | Typical fsync Latency | Expected Commit Latency | Throughput | Status |
|----------|----------------------|------------------------|------------|--------|
| **Linux (ext4, SSD)** | 1-5ms | 2-10ms | 100-500 tx/sec | ✅ Recommended |
| **Linux (xfs, NVMe)** | 0.5-2ms | 1-5ms | 200-1000 tx/sec | ✅ Optimal |
| **macOS (APFS, SSD)** | 10-50ms | 20-100ms | 10-50 tx/sec | ⚠ Acceptable |
| **Windows (NTFS, SSD)** | 50-300ms | 100-600ms | 2-10 tx/sec | ⚠ Limited |

### Root Cause: fsync() System Call Overhead

The RVC v2 hardening uses `fsync()` to guarantee durability:
- Every commit writes to WAL and calls `fsync()`
- Every state update writes to state file and calls `fsync()`
- This ensures zero data loss on power failure

**Platform Differences**:
- **Linux**: Optimized fsync implementation, direct I/O support
- **macOS**: APFS has higher fsync overhead than ext4/xfs
- **Windows**: NTFS fsync is 50-100x slower than Linux ext4

This is a **well-documented operating system limitation**, not an Aethel code issue.

---

## Recommended Deployment Configurations

### Production Deployment (Financial Applications)

**Platform**: Linux (Ubuntu 22.04 LTS or RHEL 9)  
**File System**: ext4 or xfs  
**Storage**: Enterprise NVMe SSD with power-loss protection  
**Expected Performance**:
- Commit latency: 2-10ms (99th percentile)
- Throughput: 100-500 transactions/second
- Recovery time: < 100ms

**Configuration**:
```python
from diotec360.consensus.atomic_commit import AtomicCommitLayer, DurabilityLevel

atomic_layer = AtomicCommitLayer(
    state_dir="/var/diotec360/state",
    wal_dir="/var/diotec360/wal",
    durability_level=DurabilityLevel.STRICT  # Default: fsync on every commit
)
```

---

### Development/Testing (Non-Critical Applications)

**Platform**: Any (Linux, macOS, Windows)  
**File System**: Any  
**Storage**: Consumer SSD  
**Expected Performance**:
- Commit latency: 10-600ms (platform-dependent)
- Throughput: 2-100 transactions/second
- Recovery time: < 200ms

**Configuration**:
```python
# Option 1: Use default STRICT durability (slower but safe)
atomic_layer = AtomicCommitLayer(state_dir, wal_dir)

# Option 2: Use RELAXED durability for faster testing (future release)
# atomic_layer = AtomicCommitLayer(
#     state_dir, wal_dir,
#     durability_level=DurabilityLevel.RELAXED  # Skip fsync (faster but risky)
# )
```

**Note**: RELAXED durability mode will be available in v1.9.3. For v1.9.2, all commits use STRICT durability.

---

### Windows Deployment Considerations

**Performance Limitations**:
- WAL commit latency: 100-600ms (99th percentile)
- Throughput: 2-10 transactions/second
- Root cause: Windows NTFS fsync overhead

**Recommended Use Cases**:
- ✓ Development and testing
- ✓ Low-frequency transactions (< 10/sec)
- ✓ Demonstrations and prototypes
- ⚠ Production (with batch commit optimization)
- ✗ High-frequency trading (use Linux)

**Mitigation Strategies**:

1. **Batch Commits** (Recommended for v1.9.3):
   ```python
   # Group multiple transactions into single commit
   with atomic_layer.batch_commit() as batch:
       batch.add_transaction(tx1)
       batch.add_transaction(tx2)
       batch.add_transaction(tx3)
   # Single fsync for all 3 transactions
   # Expected improvement: 10-100x throughput
   ```

2. **Use ReFS Instead of NTFS**:
   - ReFS (Resilient File System) has better fsync performance
   - Available on Windows Server 2012+ and Windows 10 Pro+
   - Expected improvement: 2-5x faster than NTFS

3. **Enterprise Storage**:
   - Use NVMe SSD with battery-backed write cache
   - Expected improvement: 2-10x faster than consumer SSD

4. **Deploy on Linux** (Recommended):
   - Use WSL2 (Windows Subsystem for Linux) for development
   - Deploy production on Linux servers
   - Expected improvement: 50-100x faster than Windows NTFS

---

## Hardware Requirements

### Minimum Requirements

**Storage**:
- Type: Consumer SSD
- Interface: SATA III
- Write Speed: 500 MB/s
- Capacity: 50 GB

**Expected Performance**:
- Linux: 10-50ms commit latency
- macOS: 20-100ms commit latency
- Windows: 100-600ms commit latency

---

### Recommended Requirements (Production)

**Storage**:
- Type: Enterprise NVMe SSD
- Interface: PCIe 3.0 x4 or higher
- Write Speed: 2000 MB/s
- Capacity: 200 GB
- Features: Power-loss protection (PLP)

**Expected Performance**:
- Linux: 2-10ms commit latency
- macOS: 10-50ms commit latency
- Windows: 50-300ms commit latency

---

### Optimal Requirements (High-Frequency Trading)

**Storage**:
- Type: Enterprise NVMe SSD with battery-backed cache
- Interface: PCIe 4.0 x4 or higher
- Write Speed: 5000 MB/s
- Capacity: 500 GB
- Features: Power-loss protection, battery-backed write cache

**Expected Performance**:
- Linux: 1-5ms commit latency
- macOS: 5-20ms commit latency
- Windows: 20-100ms commit latency

---

## Performance Tuning

### Linux Optimizations

1. **Use Direct I/O**:
   ```python
   # Future release (v1.9.3)
   atomic_layer = AtomicCommitLayer(
       state_dir, wal_dir,
       use_direct_io=True  # Bypass page cache
   )
   ```

2. **Tune File System**:
   ```bash
   # Mount with noatime to reduce write overhead
   mount -o noatime,nodiratime /dev/nvme0n1 /var/aethel
   
   # For ext4: enable journal checksums
   tune2fs -O journal_checksum /dev/nvme0n1
   
   # For xfs: use allocsize for better performance
   mount -o allocsize=64m /dev/nvme0n1 /var/aethel
   ```

3. **Increase I/O Scheduler Priority**:
   ```bash
   # Use deadline scheduler for SSDs
   echo deadline > /sys/block/nvme0n1/queue/scheduler
   
   # Increase queue depth
   echo 1024 > /sys/block/nvme0n1/queue/nr_requests
   ```

---

### macOS Optimizations

1. **Use APFS with Encryption Disabled**:
   - APFS encryption adds fsync overhead
   - For non-sensitive data, disable encryption

2. **Disable Spotlight Indexing**:
   ```bash
   # Disable Spotlight on Aethel data directory
   mdutil -i off /var/aethel
   ```

3. **Use External NVMe Drive**:
   - External Thunderbolt 3/4 NVMe drives have better performance
   - Expected improvement: 2-5x faster than internal SSD

---

### Windows Optimizations

1. **Use ReFS Instead of NTFS**:
   ```powershell
   # Format drive with ReFS
   Format-Volume -DriveLetter D -FileSystem ReFS -NewFileSystemLabel "Aethel"
   ```

2. **Disable Write-Cache Buffer Flushing**:
   ```powershell
   # WARNING: Only for testing, not production!
   # This disables fsync durability guarantees
   Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Class\{4d36e967-e325-11ce-bfc1-08002be10318}\0000" -Name "CacheIsPowerProtected" -Value 1
   ```

3. **Use Enterprise Storage**:
   - Consumer SSDs have poor fsync performance on Windows
   - Enterprise NVMe with battery-backed cache: 10-50x improvement

4. **Deploy on WSL2** (Development):
   ```bash
   # Install WSL2 with Ubuntu
   wsl --install -d Ubuntu-22.04
   
   # Run Aethel in WSL2 (Linux performance)
   wsl -d Ubuntu-22.04
   cd /mnt/c/aethel
   python demo_atomic_commit.py
   ```

---

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Commit Latency**:
   - Metric: `DIOTEC360_commit_latency_ms`
   - Alert: p99 > 1000ms (Windows), p99 > 100ms (Linux)

2. **WAL File Size**:
   - Metric: `DIOTEC360_wal_size_bytes`
   - Alert: > 1 GB (trigger compaction)

3. **Recovery Time**:
   - Metric: `DIOTEC360_recovery_time_ms`
   - Alert: > 5000ms (indicates large WAL)

4. **Fsync Failures**:
   - Metric: `DIOTEC360_fsync_errors_total`
   - Alert: > 0 (critical: disk failure)

### Example Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'aethel'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'

# Alert rules
groups:
  - name: DIOTEC360_performance
    rules:
      - alert: HighCommitLatency
        expr: histogram_quantile(0.99, DIOTEC360_commit_latency_ms) > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High commit latency detected"
          description: "p99 commit latency is {{ $value }}ms"
      
      - alert: LargeWALFile
        expr: DIOTEC360_wal_size_bytes > 1073741824  # 1 GB
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "WAL file is large"
          description: "WAL file size is {{ $value }} bytes. Consider compaction."
```

---

## Troubleshooting

### High Commit Latency

**Symptoms**:
- Commit latency > 1 second
- Low transaction throughput

**Diagnosis**:
```python
# Run benchmark to measure fsync performance
python benchmark_rvc_v2_hardening.py

# Check disk I/O stats
# Linux:
iostat -x 1 10

# Windows:
Get-Counter '\PhysicalDisk(*)\Avg. Disk sec/Write' -SampleInterval 1 -MaxSamples 10
```

**Solutions**:
1. **Check Platform**: Verify running on Linux (not Windows)
2. **Check Storage**: Verify using SSD (not HDD)
3. **Check File System**: Verify using ext4/xfs (not NTFS)
4. **Implement Batch Commits**: Group transactions (v1.9.3)
5. **Upgrade Hardware**: Use enterprise NVMe with PLP

---

### WAL File Growing Too Large

**Symptoms**:
- WAL file > 1 GB
- Slow recovery time

**Diagnosis**:
```python
# Check WAL file size
import os
wal_size = os.path.getsize('.diotec360_state/wal/wal.log')
print(f"WAL size: {wal_size / 1024 / 1024:.2f} MB")
```

**Solutions**:
1. **Run WAL Compaction**:
   ```python
   from diotec360.consensus.atomic_commit import AtomicCommitLayer
   
   atomic_layer = AtomicCommitLayer(state_dir, wal_dir)
   atomic_layer.compact_wal()  # Remove redundant entries
   ```

2. **Schedule Periodic Compaction**:
   ```python
   # Compact every 1000 transactions
   if transaction_count % 1000 == 0:
       atomic_layer.compact_wal()
   ```

---

## Frequently Asked Questions

### Q: Why is commit latency so high on Windows?

**A**: Windows NTFS fsync() is 50-100x slower than Linux ext4/xfs. This is a well-documented operating system limitation. The RVC v2 hardening prioritizes correctness (zero data loss) over performance, which requires fsync on every commit.

**Solutions**:
- Deploy on Linux for production (recommended)
- Use batch commits to amortize fsync cost (v1.9.3)
- Use ReFS instead of NTFS (2-5x improvement)
- Use enterprise NVMe with battery-backed cache (10-50x improvement)

---

### Q: Can I disable fsync for better performance?

**A**: Not in v1.9.2. The RVC v2 hardening enforces STRICT durability (fsync on every commit) to guarantee zero data loss. Future releases (v1.9.3) will add a RELAXED durability mode that skips fsync for non-critical applications.

**Trade-offs**:
- **STRICT** (default): Slow but safe (zero data loss)
- **RELAXED** (future): Fast but risky (data loss on power failure)

---

### Q: What is the recommended platform for production?

**A**: Linux (Ubuntu 22.04 LTS or RHEL 9) with enterprise NVMe SSD. This configuration provides:
- Commit latency: 2-10ms (99th percentile)
- Throughput: 100-500 transactions/second
- Zero data loss on power failure

---

### Q: Can I use Aethel on Windows for production?

**A**: Yes, but with limitations:
- ✓ Low-frequency transactions (< 10/sec): Acceptable
- ⚠ Medium-frequency transactions (10-100/sec): Use batch commits (v1.9.3)
- ✗ High-frequency transactions (> 100/sec): Not recommended

For high-frequency trading or financial applications, deploy on Linux.

---

## Conclusion

The RVC v2 hardening prioritizes **correctness over performance**. The fsync durability guarantees ensure zero data loss, but have platform-specific performance implications.

**Recommendations**:
- **Production**: Deploy on Linux with enterprise NVMe
- **Development**: Any platform (document performance expectations)
- **Windows**: Use for testing or low-frequency applications

For questions or support, see the [Aethel documentation](https://github.com/diotec360-lang/aethel) or contact the development team.

---

*"The system prefers to stop than to lie. Performance is important, but correctness is non-negotiable."*  
— Design Principle, v1.9.2 "The Hardening"
