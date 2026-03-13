# RVC v2 Hardening - Design Specification

## Version: 1.9.2 "The Hardening"
## Architecture: Fail-Closed Integrity Enforcement

---

## Design Philosophy

**Core Principle**: "Integrity > Availability"

The system is designed to fail safely rather than operate with corrupted or unverified data. This design implements the Architect's mandate: "Better to stop than to lie."

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    INTEGRITY LAYER                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ IntegrityPanic│  │ Fail-Closed  │  │ Hard-Reject  │     │
│  │   Framework   │  │   Recovery   │  │   Parsing    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
           ▲                  ▲                  ▲
           │                  │                  │
┌──────────┴──────────────────┴──────────────────┴───────────┐
│                    PERSISTENCE LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Append-Only  │  │ Merkle Root  │  │  State Store │     │
│  │     WAL      │  │  Validation  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
           ▲                  ▲                  ▲
           │                  │                  │
┌──────────┴──────────────────┴──────────────────┴───────────┐
│                    NETWORK LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Sovereign   │  │  ED25519     │  │   Gossip     │     │
│  │   Gossip     │  │  Signatures  │  │  Protocol    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. IntegrityPanic Framework

**Purpose**: Centralized exception handling for integrity violations

**Class Structure**:
```python
class IntegrityPanic(Exception):
    """Base exception for all integrity violations"""
    def __init__(self, violation_type: str, details: dict, recovery_hint: str):
        self.violation_type = violation_type
        self.details = details
        self.recovery_hint = recovery_hint
        self.timestamp = time.time()
        
class StateCorruptionPanic(IntegrityPanic):
    """State file corrupted or unreadable"""
    
class MerkleRootMismatchPanic(IntegrityPanic):
    """Merkle root doesn't match computed value"""
    
class UnsupportedConstraintError(IntegrityPanic):
    """Constraint cannot be verified by Z3"""
```

**Behavior**:
- All integrity violations logged to audit trail
- System enters safe mode (read-only or shutdown)
- Clear recovery instructions provided
- No automatic "healing" that loses data

---

### 2. Fail-Closed Recovery

**Module**: `aethel/consensus/atomic_commit.py`

**Current Implementation** (VULNERABLE):
```python
def recover_from_crash(self):
    try:
        with open(self.state_file, 'r') as f:
            state = json.load(f)
    except:
        state = {}  # ❌ SILENT DATA LOSS
    return state
```

**New Implementation** (HARDENED):
```python
def recover_from_crash(self):
    """
    Fail-closed recovery: NEVER create empty state
    
    Raises:
        StateCorruptionPanic: If state file corrupted
        MerkleRootMismatchPanic: If integrity check fails
    """
    # Step 1: Attempt to read state file
    try:
        with open(self.state_file, 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        raise StateCorruptionPanic(
            violation_type="STATE_FILE_MISSING",
            details={"path": self.state_file},
            recovery_hint="Restore from Genesis Vault backup or initialize new genesis state"
        )
    except json.JSONDecodeError as e:
        raise StateCorruptionPanic(
            violation_type="STATE_FILE_CORRUPTED",
            details={"path": self.state_file, "error": str(e)},
            recovery_hint="Restore from latest backup in Genesis Vault"
        )
    
    # Step 2: Verify Merkle Root integrity
    computed_root = self._compute_merkle_root(state)
    stored_root = state.get("_merkle_root")
    
    if computed_root != stored_root:
        raise MerkleRootMismatchPanic(
            violation_type="MERKLE_ROOT_MISMATCH",
            details={
                "computed": computed_root,
                "stored": stored_root,
                "state_size": len(state)
            },
            recovery_hint="State has been tampered with. Restore from verified backup."
        )
    
    # Step 3: Verify WAL consistency
    self._verify_wal_consistency(state)
    
    return state
```

**Recovery Procedure**:
1. System detects corruption on boot
2. IntegrityPanic raised with diagnostic info
3. Administrator notified via monitoring
4. Manual restoration from Genesis Vault
5. System verifies restored state before resuming

---

### 3. Append-Only WAL

**Module**: `aethel/consensus/atomic_commit.py`

**Current Implementation** (O(n²)):
```python
def mark_committed(self, tx_id: str):
    # Read entire WAL
    entries = self._read_wal()
    # Modify entry
    for entry in entries:
        if entry['tx_id'] == tx_id:
            entry['status'] = 'COMMIT'
    # Rewrite entire file ❌ O(n²)
    self._write_wal(entries)
```

**New Implementation** (O(1)):
```python
def mark_committed(self, tx_id: str):
    """
    Append-only commit marking: O(1) complexity
    
    WAL Format:
    - Each line is independent JSON object
    - PREPARE: {"op": "PREPARE", "tx_id": "...", "data": {...}}
    - COMMIT: {"op": "COMMIT", "tx_id": "...", "timestamp": ...}
    - ABORT: {"op": "ABORT", "tx_id": "...", "reason": "..."}
    """
    commit_entry = {
        "op": "COMMIT",
        "tx_id": tx_id,
        "timestamp": time.time()
    }
    
    # Append single line (O(1) operation)
    with open(self.wal_file, 'a') as f:
        f.write(json.dumps(commit_entry) + '\n')
        f.flush()
        os.fsync(f.fileno())  # Ensure durability

def compact_wal(self):
    """
    Maintenance operation: Remove redundant entries
    
    Called periodically (e.g., every 1000 transactions)
    Not on critical path
    """
    entries = self._read_wal()
    
    # Keep only latest status for each tx_id
    latest_status = {}
    for entry in entries:
        tx_id = entry['tx_id']
        latest_status[tx_id] = entry
    
    # Write compacted WAL
    with open(self.wal_file + '.tmp', 'w') as f:
        for entry in latest_status.values():
            f.write(json.dumps(entry) + '\n')
    
    # Atomic rename
    os.replace(self.wal_file + '.tmp', self.wal_file)
```

**Performance Impact**:
- Before: O(n²) - 1000 txs = 1,000,000 operations
- After: O(n) - 1000 txs = 1,000 operations
- Improvement: 1000x faster under load

---

### 4. Hard-Reject Parsing

**Module**: `aethel/core/judge.py`

**Current Implementation** (VULNERABLE):
```python
def _ast_to_z3(self, node):
    if isinstance(node, ast.BinOp):
        # ... handle binary operations
    elif isinstance(node, ast.Compare):
        # ... handle comparisons
    else:
        # ❌ SILENTLY IGNORE UNSUPPORTED NODES
        return None
```

**New Implementation** (HARDENED):
```python
# Explicit whitelist of supported constraint types
SUPPORTED_AST_NODES = {
    ast.BinOp, ast.UnaryOp, ast.Compare,
    ast.Num, ast.Name, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div,
    ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE
}

def _ast_to_z3(self, node):
    """
    Convert AST to Z3 constraint with hard-reject policy
    
    Raises:
        UnsupportedConstraintError: If node type not in whitelist
    """
    node_type = type(node)
    
    # Hard-reject: unknown node types
    if node_type not in SUPPORTED_AST_NODES:
        raise UnsupportedConstraintError(
            violation_type="UNSUPPORTED_AST_NODE",
            details={
                "node_type": node_type.__name__,
                "node_repr": ast.dump(node),
                "supported_types": [t.__name__ for t in SUPPORTED_AST_NODES]
            },
            recovery_hint="Rewrite constraint using supported syntax. See documentation."
        )
    
    # Process supported nodes
    if isinstance(node, ast.BinOp):
        return self._handle_binop(node)
    elif isinstance(node, ast.Compare):
        return self._handle_compare(node)
    # ... other supported types
```

**Validation Flow**:
```
Transaction Submitted
        ↓
Parse Constraints (AST)
        ↓
    Supported? ──NO──> UnsupportedConstraintError
        ↓                      ↓
       YES              Transaction REJECTED
        ↓
Convert to Z3
        ↓
Verify Proof
```

---

### 5. Sovereign Gossip

**Module**: `aethel/lattice/gossip.py`

**Message Format**:
```python
class SignedGossipMessage:
    """
    Cryptographically signed gossip message
    
    Structure:
    {
        "payload": {
            "type": "STATE_UPDATE",
            "data": {...},
            "timestamp": 1234567890,
            "sender_id": "node_abc123"
        },
        "signature": "ed25519_signature_hex",
        "public_key": "ed25519_pubkey_hex"
    }
    """
```

**Implementation**:
```python
from aethel.core.crypto import ED25519Signer, ED25519Verifier

class SovereignGossip:
    def __init__(self, node_id: str, private_key: bytes):
        self.node_id = node_id
        self.signer = ED25519Signer(private_key)
        self.known_nodes = {}  # node_id -> public_key
    
    def send_message(self, message_type: str, data: dict) -> dict:
        """Sign and send gossip message"""
        payload = {
            "type": message_type,
            "data": data,
            "timestamp": time.time(),
            "sender_id": self.node_id
        }
        
        # Sign payload
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        signature = self.signer.sign(payload_bytes)
        
        return {
            "payload": payload,
            "signature": signature.hex(),
            "public_key": self.signer.public_key.hex()
        }
    
    def receive_message(self, signed_message: dict) -> dict:
        """Verify and process gossip message"""
        payload = signed_message["payload"]
        signature = bytes.fromhex(signed_message["signature"])
        public_key = bytes.fromhex(signed_message["public_key"])
        
        # Verify signature
        payload_bytes = json.dumps(payload, sort_keys=True).encode()
        verifier = ED25519Verifier(public_key)
        
        if not verifier.verify(payload_bytes, signature):
            raise IntegrityPanic(
                violation_type="INVALID_GOSSIP_SIGNATURE",
                details={
                    "sender_id": payload.get("sender_id"),
                    "message_type": payload.get("type")
                },
                recovery_hint="Reject message from untrusted source"
            )
        
        # Verify sender identity
        sender_id = payload["sender_id"]
        if sender_id in self.known_nodes:
            if self.known_nodes[sender_id] != public_key:
                raise IntegrityPanic(
                    violation_type="NODE_IDENTITY_MISMATCH",
                    details={"sender_id": sender_id},
                    recovery_hint="Possible impersonation attack"
                )
        else:
            # Register new node
            self.known_nodes[sender_id] = public_key
        
        return payload
```

---

## Data Flow Diagrams

### Fail-Closed Boot Sequence

```
System Boot
     ↓
Read state.json
     ↓
  Valid? ──NO──> StateCorruptionPanic ──> HALT
     ↓                                      ↓
    YES                            Administrator
     ↓                              Restores Backup
Verify Merkle Root                         ↓
     ↓                                  Retry Boot
  Match? ──NO──> MerkleRootMismatchPanic
     ↓
    YES
     ↓
Verify WAL
     ↓
  Valid? ──NO──> IntegrityPanic
     ↓
    YES
     ↓
System Ready
```

### Append-Only WAL Flow

```
Transaction Commit
        ↓
Append COMMIT entry (O(1))
        ↓
    fsync()
        ↓
    Success
        ↓
[Background: WAL Compaction every N txs]
```

### Hard-Reject Parsing Flow

```
Transaction with Constraints
        ↓
Parse AST
        ↓
For each node:
    ↓
Supported? ──NO──> UnsupportedConstraintError
    ↓                      ↓
   YES              Reject Transaction
    ↓
Convert to Z3
    ↓
Verify Proof
```

---

## Performance Considerations

### Latency Budget

| Operation | Before | After | Target |
|-----------|--------|-------|--------|
| WAL Commit | O(n²) | O(1) | < 5ms |
| State Recovery | ~100ms | ~150ms | < 200ms |
| Signature Verify | N/A | ~0.5ms | < 1ms |
| Constraint Parse | ~10ms | ~12ms | < 15ms |

### Throughput Impact

- **WAL Optimization**: +1000x throughput under load
- **Signature Verification**: -2% throughput (acceptable for security)
- **Hard-Reject Parsing**: No measurable impact (fail-fast)

---

## Security Properties

### Formal Guarantees

1. **Integrity**: `∀ state: corrupted(state) → panic(system)`
2. **Authenticity**: `∀ msg: ¬verified(msg) → rejected(msg)`
3. **Completeness**: `∀ constraint: ¬supported(constraint) → rejected(tx)`
4. **Durability**: `∀ commit: fsync(commit) → persistent(commit)`

### Threat Model

**Mitigated Threats**:
- ✅ Silent data corruption
- ✅ Performance DoS via WAL
- ✅ Constraint bypass attacks
- ✅ Network message spoofing

**Remaining Threats** (out of scope):
- ⚠️ Physical hardware tampering
- ⚠️ Compromised administrator credentials
- ⚠️ Side-channel attacks on cryptography

---

## Migration Strategy

### v1.9.1 → v1.9.2 Upgrade Path

1. **Backup**: Create Genesis Vault snapshot
2. **WAL Migration**: Convert to append-only format
3. **State Verification**: Compute and store Merkle roots
4. **Key Distribution**: Deploy ED25519 keys to all nodes
5. **Gradual Rollout**: Shadow mode → Soft launch → Full activation

### Rollback Plan

- Keep v1.9.1 binaries available
- Genesis Vault contains pre-upgrade snapshots
- Rollback window: 7 days after deployment

---

## Testing Strategy

### Unit Tests
- IntegrityPanic exception handling
- Append-only WAL operations
- Hard-reject parsing for all AST node types
- Signature verification edge cases

### Integration Tests
- Full boot sequence with corrupted state
- WAL recovery under various failure scenarios
- End-to-end gossip with signature verification
- Performance benchmarks (O(n²) → O(n) validation)

### Property-Based Tests
- Merkle root always matches computed value
- WAL append operations are idempotent
- All unsupported AST nodes trigger errors
- Signature verification is deterministic

---

## Monitoring & Observability

### Metrics
- `integrity_panic_total` (counter by violation_type)
- `wal_append_latency_ms` (histogram)
- `signature_verification_latency_ms` (histogram)
- `constraint_rejection_total` (counter by reason)

### Alerts
- **CRITICAL**: IntegrityPanic triggered
- **HIGH**: WAL append latency > 10ms
- **MEDIUM**: Signature verification failures > 1%

---

## Documentation Requirements

1. **Administrator Guide**: Recovery procedures for IntegrityPanic
2. **Developer Guide**: Supported constraint syntax reference
3. **Operations Guide**: WAL compaction scheduling
4. **Security Guide**: Key management for Sovereign Gossip

---

*"The system prefers to stop than to lie. This is the foundation of trust."*  
— Design Principle, v1.9.2 "The Hardening"
