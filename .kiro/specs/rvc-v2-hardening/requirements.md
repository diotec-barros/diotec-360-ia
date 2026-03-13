# RVC v2 Hardening - Requirements Specification

## Version: 1.9.2 "The Hardening"
## Status: CRITICAL SECURITY FIXES
## Priority: MAXIMUM

---

## Executive Summary

The Inquisitor's second audit (RVC v2) has identified critical vulnerabilities in Aethel v1.9.1 that compromise system integrity. These vulnerabilities allow silent data corruption, performance degradation attacks, and security bypasses. Version 1.9.2 implements zero-tolerance integrity policies.

**Architect's Verdict**: "Aethel NEVER overwrites corrupted state with empty state. The system must FREEZE rather than lie."

---

## Critical Vulnerabilities Identified

### RVC2-001: Fail-Closed Recovery (CRITICAL)
**Severity**: 🔴 CRITICAL  
**Impact**: Silent data loss, "Truth Blackout"

**Current Behavior**:
- `recover_from_crash()` creates empty state `{}` when corruption detected
- System continues with amnesia instead of failing safely
- Merkle Root validation bypassed silently

**Required Behavior**:
- If `state.json` corrupted OR Merkle Root mismatch → `IntegrityPanic`
- System MUST abort boot and require manual intervention
- Administrator must restore from Genesis Vault backup
- NEVER create empty state automatically

**Acceptance Criteria**:
- [ ] Corrupted state.json triggers IntegrityPanic exception
- [ ] Merkle Root mismatch triggers IntegrityPanic exception
- [ ] System refuses to boot with corrupted state
- [ ] Clear error message guides administrator to backup restoration
- [ ] Zero tolerance for data amnesia

---

### RVC2-002: Optimized WAL (O(n²) DoS Attack)
**Severity**: 🟠 HIGH  
**Impact**: Performance degradation, DoS via I/O exhaustion

**Current Behavior**:
- `mark_committed()` rewrites entire WAL file on every commit
- O(n²) complexity allows DoS attack with many pending transactions
- Disk I/O becomes bottleneck under load

**Required Behavior**:
- Append-only WAL operations
- `mark_committed()` appends single line: `{"status": "COMMIT", "tx_id": "..."}`
- O(1) complexity per commit operation
- Periodic WAL compaction (separate maintenance operation)

**Acceptance Criteria**:
- [ ] mark_committed() uses append-only writes
- [ ] Single line per commit status update
- [ ] O(1) time complexity per commit
- [ ] WAL compaction utility for maintenance
- [ ] Performance benchmarks show linear scaling

---

### RVC2-004: Hard-Reject Parsing (Silent Security Bypass)
**Severity**: 🔴 CRITICAL  
**Impact**: Security constraints silently ignored

**Current Behavior**:
- `_ast_to_z3()` silently ignores unsupported AST nodes
- Security constraints can be bypassed by using unsupported syntax
- No validation failure when constraints dropped

**Required Behavior**:
- Unsupported AST node → raise `UnsupportedConstraintError`
- Transaction MUST be rejected if any constraint cannot be verified
- Explicit whitelist of supported constraint types
- Fail-closed: unknown = rejected

**Acceptance Criteria**:
- [ ] UnsupportedConstraintError exception defined
- [ ] All unsupported nodes trigger exception
- [ ] Transaction rejected when constraint parsing fails
- [ ] Comprehensive test coverage for all AST node types
- [ ] Documentation of supported constraint syntax

---

### RVC2-006: Sovereign Gossip (P2P Authentication)
**Severity**: 🟠 HIGH  
**Impact**: Network spoofing, Byzantine attacks

**Current Behavior**:
- P2P gossip messages accepted without cryptographic verification
- No sender authentication in network layer
- Vulnerable to message injection and spoofing

**Required Behavior**:
- All gossip messages MUST be signed with ED25519 (v2.2 Sovereign Identity)
- Signature verification before message processing
- Public key infrastructure for node identity
- Reject unsigned or invalid signatures

**Acceptance Criteria**:
- [ ] ED25519 signature on all gossip messages
- [ ] Signature verification in message handler
- [ ] Node identity management with public keys
- [ ] Unsigned messages rejected immediately
- [ ] Integration with existing Sovereign Identity system

---

## Non-Functional Requirements

### NFR-1: Zero-Tolerance Integrity
- System prefers unavailability over incorrect data
- "Better to stop than to lie" principle
- All integrity violations trigger panic mode

### NFR-2: Performance Preservation
- Fixes must not degrade normal operation performance
- Append-only WAL should improve performance
- Signature verification overhead < 1ms per message

### NFR-3: Backward Compatibility
- Existing valid transactions continue to work
- State migration path from v1.9.1 to v1.9.2
- Clear upgrade documentation

### NFR-4: Operational Excellence
- Clear error messages for administrators
- Recovery procedures documented
- Monitoring and alerting for integrity violations

---

## Success Metrics

1. **Security**: 100% of identified vulnerabilities sealed
2. **Integrity**: Zero false-positive integrity panics in testing
3. **Performance**: WAL operations scale linearly (O(n) not O(n²))
4. **Reliability**: System fails safely under all corruption scenarios
5. **Auditability**: All integrity violations logged with full context

---

## Commercial Value

**Architect's Statement**: "When we fix these issues, you can tell banks: 'Our system prefers to stop than to lie.' This is what generates the Gold Seal of Trust."

- Enterprise-grade fail-safe behavior
- Regulatory compliance (financial systems)
- Audit trail for all integrity events
- Production-ready for mission-critical applications

---

## Dependencies

- Existing: Atomic Commit (RVC-003), Thread CPU Accounting (RVC-004)
- Existing: Sovereign Identity v2.2 (ED25519 signatures)
- Existing: Merkle Tree state verification
- New: IntegrityPanic exception framework
- New: WAL compaction utilities

---

## Out of Scope

- Performance optimization beyond O(n²) fix
- New cryptographic primitives (use existing ED25519)
- UI/UX changes
- New features unrelated to security hardening

---

## Risk Assessment

**High Risk Items**:
1. IntegrityPanic may cause operational disruptions if triggered incorrectly
2. WAL format changes require careful migration
3. Signature verification adds latency to network operations

**Mitigation**:
1. Comprehensive testing of panic conditions
2. Automated migration scripts with rollback capability
3. Performance benchmarking before deployment

---

## Timeline Estimate

- **Critical Path**: RVC2-001 (Fail-Closed) + RVC2-004 (Hard-Reject)
- **High Priority**: RVC2-002 (WAL Optimization)
- **Important**: RVC2-006 (Sovereign Gossip)

**Target**: All fixes implemented and tested within single development cycle

---

## Approval

**Status**: ✅ APPROVED BY ARCHITECT  
**Authority**: Sovereign Policy Decision  
**Mandate**: Zero-tolerance integrity enforcement

---

*"The Truth is Binary: Either the Merkle Root proves reality, or reality does not exist."*  
— The Architect's Verdict on Integrity
