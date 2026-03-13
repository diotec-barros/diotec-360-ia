# Implementation Plan: RVC-003 & RVC-004 Security Fixes

## Overview

This implementation plan addresses the final two critical vulnerabilities from the security audit: RVC-003 (Atomic Commit) and RVC-004 (Thread CPU Accounting). The implementation is divided into two major phases with clear checkpoints to ensure incremental validation.

The approach prioritizes security and correctness over performance, with comprehensive testing at each step. All code will be implemented in Python to integrate with the existing Aethel codebase.

## Tasks

- [x] 1. Implement Write-Ahead Log (WAL) Foundation
  - [x] 1.1 Create WAL data structures and file format
    - Implement `WALEntry` dataclass with transaction ID, changes, timestamp, and commit status
    - Design JSON-based WAL file format for human readability
    - Implement WAL file rotation and garbage collection
    - _Requirements: 2.1, 2.5_
  
  - [ ]* 1.2 Write property test for WAL durability
    - **Property 2: Write-Ahead Logging Protocol**
    - **Validates: Requirements 2.1, 2.2, 2.5**
  
  - [x] 1.3 Implement WAL append and fsync operations
    - Implement `append_entry()` with JSON serialization
    - Add fsync() call after each WAL write
    - Implement `mark_committed()` for commit tracking
    - Add error handling for disk full scenarios
    - _Requirements: 2.1, 2.2, 2.5_
  
  - [ ]* 1.4 Write unit tests for WAL operations
    - Test WAL append with various entry sizes
    - Test fsync error handling
    - Test WAL file rotation
    - _Requirements: 2.1, 2.5_

- [x] 2. Implement Atomic Commit Layer
  - [x] 2.1 Create atomic commit protocol implementation
    - Implement `AtomicCommitLayer` class with transaction management
    - Implement `begin_transaction()` for transaction initialization
    - Implement temporary file creation with unique naming
    - Add atomic rename using `os.rename()` (POSIX atomic operation)
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.2 Implement commit transaction protocol
    - Implement `commit_transaction()` with full protocol:
      1. Write changes to WAL
      2. Fsync WAL
      3. Apply changes to Merkle Tree
      4. Write state to temp file
      5. Fsync temp file
      6. Atomic rename temp → canonical
      7. Mark WAL committed
    - Add error handling for each step
    - _Requirements: 1.1, 1.2, 2.1, 2.2_
  
  - [ ]* 2.3 Write property test for atomic state persistence
    - **Property 1: Atomic State Persistence**
    - **Validates: Requirements 1.1, 1.2, 1.3, 8.2**
  
  - [x] 2.4 Implement rollback transaction
    - Implement `rollback_transaction()` to discard changes
    - Clean up temporary files on rollback
    - Ensure Merkle Tree state is unchanged
    - _Requirements: 3.2_

- [x] 3. Implement Crash Recovery Protocol
  - [x] 3.1 Create crash recovery detection
    - Implement `recover_from_crash()` entry point
    - Scan WAL for uncommitted transactions
    - Detect orphaned temporary files
    - _Requirements: 3.1_
  
  - [x] 3.2 Implement recovery actions
    - Roll back uncommitted transactions
    - Delete orphaned temporary files
    - Replay committed but unapplied WAL entries
    - _Requirements: 3.1, 3.2, 2.3_
  
  - [x] 3.3 Implement Merkle Root verification
    - Verify Merkle Root matches restored state
    - Restore from last checkpoint if verification fails
    - Generate recovery report with statistics
    - _Requirements: 1.4, 1.5, 3.3_
  
  - [ ]* 3.4 Write property test for crash recovery correctness
    - **Property 3: Crash Recovery Correctness**
    - **Validates: Requirements 3.1, 3.2, 3.3, 2.3, 2.4**
  
  - [ ]* 3.5 Write property test for Merkle Root integrity
    - **Property 4: Merkle Root Integrity**
    - **Validates: Requirements 1.4, 1.5, 3.3**
  
  - [x] 3.6 Implement recovery audit logging
    - Log all recovery operations to audit trail
    - Include rollback details, temp file deletions, verification results
    - _Requirements: 3.5_
  
  - [ ]* 3.7 Write property test for temporary file cleanup
    - **Property 5: Temporary File Cleanup**
    - **Validates: Requirements 1.3, 3.1**

- [x] 4. Checkpoint - Atomic Commit Complete
  - Ensure all atomic commit tests pass
  - Verify crash recovery works correctly
  - Benchmark write latency overhead
  - Ask the user if questions arise

- [x] 5. Implement Thread CPU Accounting Foundation
  - [x] 5.1 Create platform detection and API abstraction
    - Detect platform (Linux, Windows, macOS)
    - Define abstract interface for thread CPU time
    - Implement platform-specific API wrappers
    - _Requirements: 10.4_
  
  - [x] 5.2 Implement Linux thread CPU accounting
    - Use `pthread_getcpuclockid()` + `clock_gettime()` for thread CPU time
    - Implement `get_thread_cpu_time()` for Linux
    - Add error handling for API failures
    - _Requirements: 4.1, 4.2_
  
  - [x] 5.3 Implement Windows thread CPU accounting
    - Use `GetThreadTimes()` for thread CPU time
    - Implement `get_thread_cpu_time()` for Windows
    - Convert Windows time format to milliseconds
    - _Requirements: 4.1, 4.2_
  
  - [x] 5.4 Implement macOS thread CPU accounting
    - Use `thread_info()` with `THREAD_BASIC_INFO` for thread CPU time
    - Implement `get_thread_cpu_time()` for macOS
    - Add error handling for API failures
    - _Requirements: 4.1, 4.2_
  
  - [ ]* 5.5 Write unit tests for platform-specific APIs
    - Test Linux API on Linux systems
    - Test Windows API on Windows systems
    - Test macOS API on macOS systems
    - Test error handling for unsupported platforms
    - _Requirements: 4.1, 4.2, 10.4_

- [x] 6. Implement Thread CPU Tracking
  - [x] 6.1 Create ThreadCPUAccounting class
    - Implement `ThreadCPUAccounting` with threshold configuration
    - Implement `start_tracking()` to capture initial CPU time
    - Implement `stop_tracking()` to calculate CPU consumption
    - Implement `check_violation()` to detect threshold violations
    - _Requirements: 4.1, 4.3_
  
  - [x] 6.2 Implement thread context management
    - Create `ThreadCPUContext` dataclass for tracking state
    - Create `ThreadCPUMetrics` dataclass for results
    - Create `CPUViolation` dataclass for violations
    - _Requirements: 4.1_
  
  - [ ]* 6.3 Write property test for per-thread CPU tracking
    - **Property 7: Per-Thread CPU Tracking**
    - **Validates: Requirements 4.1, 4.2, 4.5**
  
  - [ ]* 6.4 Write property test for zero-overhead measurement
    - **Property 9: Zero-Overhead Measurement**
    - **Validates: Requirements 4.4, 7.2, 7.3, 7.5**

- [x] 7. Integrate Thread CPU Accounting with Sentinel
  - [x] 7.1 Modify SentinelMonitor to add thread CPU tracking
    - Add `ThreadCPUAccounting` instance to `SentinelMonitor.__init__()`
    - Add `active_threads` dictionary to track thread contexts
    - Modify `start_transaction()` to begin thread CPU tracking
    - Modify `end_transaction()` to stop tracking and check violations
    - _Requirements: 6.1_
  
  - [x] 7.2 Implement CPU violation handling
    - Create `_handle_cpu_violation()` method
    - Trigger crisis mode on CPU violations
    - Log CPU violations to telemetry database
    - Capture thread CPU consumption profile
    - _Requirements: 5.2, 5.4, 6.2_
  
  - [x] 7.3 Add thread CPU metrics to telemetry
    - Add `thread_cpu_ms` field to `TransactionMetrics`
    - Add `cpu_violation` boolean field to `TransactionMetrics`
    - Report thread CPU metrics through existing telemetry channels
    - _Requirements: 6.3_
  
  - [ ]* 7.4 Write property test for sub-interval attack detection
    - **Property 8: Sub-Interval Attack Detection**
    - **Validates: Requirements 4.3, 5.1, 5.2, 5.4, 5.5**
  
  - [ ]* 7.5 Write property test for Sentinel integration
    - **Property 10: Sentinel Integration**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [x] 8. Checkpoint - Thread CPU Accounting Complete
  - Ensure all thread CPU accounting tests pass
  - Verify sub-millisecond attack detection works
  - Benchmark runtime overhead (should be 0%)
  - Ask the user if questions arise

- [x] 9. Integrate Atomic Commit with State Store
  - [x] 9.1 Modify StateStore to use AtomicCommitLayer
    - Add `AtomicCommitLayer` instance to `StateStore.__init__()`
    - Modify `apply_state_transition()` to use atomic commit
    - Replace direct Merkle Tree updates with transaction-based updates
    - _Requirements: 1.1, 1.2_
  
  - [x] 9.2 Add crash recovery to StateStore initialization
    - Call `recover_from_crash()` in `StateStore.__init__()`
    - Handle recovery failures (enter safe mode)
    - Log recovery report
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [ ]* 9.3 Write integration tests for StateStore with atomic commit
    - Test state transitions with atomic commit
    - Test crash recovery with StateStore
    - Test Merkle Root integrity after recovery
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 3.3_

- [x] 10. Power Failure Simulation Testing
  - [x] 10.1 Create power failure simulation harness
    - Implement test harness that simulates power failure at random points
    - Use `os.kill(SIGKILL)` to simulate abrupt termination
    - Run thousands of iterations with random failure points
    - _Requirements: 8.1, 8.2, 8.3_
  
  - [ ]* 10.2 Write property test for power failure atomicity
    - **Property 1: Atomic State Persistence** (stress test)
    - Test with 10,000+ iterations
    - Verify no partial states after any failure
    - **Validates: Requirements 1.1, 1.2, 1.3, 8.2, 8.3**
  
  - [x] 10.3 Analyze power failure test results
    - Generate statistical report on atomicity guarantees
    - Verify 100% success rate (no partial states)
    - Document any edge cases discovered
    - _Requirements: 8.5_

- [x] 11. Sub-Millisecond Attack Testing
  - [x] 11.1 Create attack generation harness
    - Implement test harness that generates attacks with precise durations
    - Use tight CPU loops with known consumption
    - Generate attacks from 0.1ms to 10ms duration
    - _Requirements: 9.1, 9.2, 9.3_
  
  - [ ]* 11.2 Write property test for sub-millisecond detection
    - **Property 8: Sub-Interval Attack Detection** (stress test)
    - Test with attacks from 0.1ms to 10ms
    - Verify 100% detection rate
    - **Validates: Requirements 5.1, 5.2, 5.3, 9.2**
  
  - [x] 11.3 Test concurrent thread attack detection
    - Run multiple attack threads simultaneously
    - Verify independent detection for each thread
    - Test with various thread counts (2, 4, 8, 16)
    - _Requirements: 4.5, 9.5_

- [x] 12. Cross-Platform Testing
  - [x] 12.1 Run all tests on Linux
    - Execute full test suite on Linux
    - Verify all properties hold
    - Benchmark performance
    - _Requirements: 10.1, 10.4_
  
  - [x] 12.2 Run all tests on Windows
    - Execute full test suite on Windows
    - Verify all properties hold
    - Benchmark performance
    - _Requirements: 10.2, 10.4_
  
  - [x] 12.3 Run all tests on macOS
    - Execute full test suite on macOS
    - Verify all properties hold
    - Benchmark performance
    - _Requirements: 10.3, 10.4_
  
  - [ ]* 12.4 Write property test for cross-platform consistency
    - **Property 11: Cross-Platform Consistency**
    - **Validates: Requirements 10.4**

- [x] 13. Performance Benchmarking
  - [x] 13.1 Benchmark atomic commit overhead
    - Measure write latency before and after atomic commit
    - Target: <10% overhead
    - Generate performance report
    - _Requirements: 11.1, 11.3_
  
  - [x] 13.2 Benchmark thread CPU accounting overhead
    - Measure runtime overhead with and without CPU accounting
    - Target: 0% overhead (zero measurable impact)
    - Generate performance report
    - _Requirements: 11.2, 11.3_
  
  - [x] 13.3 Optimize performance if needed
    - If overhead exceeds targets, implement optimizations:
      - Batch WAL writes
      - Async fsync
      - Cached process objects
      - Lazy CPU time reading
    - Re-benchmark after optimizations
    - _Requirements: 11.4_

- [-] 14. Documentation and Audit Trail
  - [x] 14.1 Document atomic commit protocol
    - Write technical specification for WAL format
    - Document fsync discipline and ordering
    - Document atomic rename protocol
    - Document crash recovery algorithm
    - _Requirements: 12.1_
  
  - [x] 14.2 Document thread CPU accounting mechanism
    - Write technical specification for platform-specific APIs
    - Document CPU time measurement methodology
    - Document violation detection algorithm
    - Document Sentinel integration
    - _Requirements: 12.2_
  
  - [x] 14.3 Generate test reports
    - Compile test results from all property tests
    - Generate coverage reports (target: >95%)
    - Document test methodology and results
    - _Requirements: 12.3_
  
  - [x] 14.4 Document performance impact
    - Compile performance benchmarks
    - Document overhead measurements
    - Document optimization strategies
    - _Requirements: 12.4_
  
  - [x] 14.5 Create security audit report
    - Document RVC-003 mitigation details
    - Document RVC-004 mitigation details
    - Provide evidence of comprehensive testing
    - Include test coverage and performance data
    - _Requirements: 12.5_

- [x] 15. Final Checkpoint - RVC-003 & RVC-004 Complete
  - Ensure all tests pass on all platforms
  - Verify performance targets met
  - Review security audit report
  - Confirm RVC-003 and RVC-004 are fully resolved
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based tests that can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at reasonable breaks
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Cross-platform testing ensures consistent security guarantees
- Performance benchmarking ensures overhead is acceptable
- Documentation provides evidence for security audit
