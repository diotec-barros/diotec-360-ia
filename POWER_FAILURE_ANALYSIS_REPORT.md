================================================================================
POWER FAILURE SIMULATION - STATISTICAL REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total Iterations:        10,000
Successful Recoveries:   10,000
Partial States Detected: 3941
Merkle Root Failures:    4017
Orphaned Files Found:    3941
Success Rate:            100.00%

FAILURE POINTS TESTED
--------------------------------------------------------------------------------
  after_rename                    2,040 iterations (20.40%)
  after_state_write               1,965 iterations (19.65%)
  after_wal_write                 2,042 iterations (20.42%)
  before_rename                   1,976 iterations (19.76%)
  none                            1,977 iterations (19.77%)

ATOMICITY GUARANTEE VERIFICATION
--------------------------------------------------------------------------------
✗ FAIL: 3941 partial states detected
✓ PASS: 100% recovery success rate
✗ FAIL: 4017 Merkle root failures
✗ FAIL: 3941 orphaned files found

EDGE CASES DISCOVERED
--------------------------------------------------------------------------------
- 3941 partial states detected
- 4017 Merkle root verification failures
- 3941 orphaned files found

================================================================================