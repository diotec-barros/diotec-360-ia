================================================================================
POWER FAILURE SIMULATION - STATISTICAL REPORT
================================================================================

SUMMARY
--------------------------------------------------------------------------------
Total Iterations:        500
Successful Recoveries:   500
Partial States Detected: 0
Merkle Root Failures:    0
Orphaned Files Found:    0
Success Rate:            100.00%

FAILURE POINTS TESTED
--------------------------------------------------------------------------------
  after_rename                      49 iterations
  after_state_write                 45 iterations
  after_wal_write                   53 iterations
  before_rename                     44 iterations
  before_state_write                61 iterations
  before_wal_commit                 40 iterations
  before_wal_write                  46 iterations
  during_rename                     48 iterations
  during_state_write                59 iterations
  during_wal_write                  55 iterations

ATOMICITY GUARANTEE VERIFICATION
--------------------------------------------------------------------------------
✓ PASS: No partial states detected
✓ PASS: 100% recovery success rate
✓ PASS: All Merkle roots valid after recovery
✓ PASS: No orphaned files after recovery

================================================================================