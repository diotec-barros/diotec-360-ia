"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Aethel Persistence Layer - The Sovereign Memory
v2.1.0 - Authenticated State Storage

Three-Tier Architecture:
1. Reality DB (Merkle State) - RocksDB-style key-value store
2. Truth DB (Vault) - Content-addressable code storage (IPFS-style)
3. Vigilance DB (Sentinel Logs) - SQLite audit trail

Philosophy: "A database that can be altered outside the system is not a database. It's a vulnerability."

Each entry is cryptographically linked to proofs. If a single bit changes on disk
without passing through the Judge, the Merkle Root breaks and the system enters Panic Mode.
"""

import sqlite3
import hashlib
import json
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ExecutionRecord:
    """Record of a single execution with cryptographic proof"""
    tx_id: str
    bundle_hash: str
    intent_name: str
    status: str  # 'PROVED', 'FAILED', 'REJECTED', 'TIMEOUT'
    result: Dict[str, Any]
    merkle_root_before: Optional[str]
    merkle_root_after: Optional[str]
    timestamp: float
    elapsed_ms: float
    layer_results: Dict[str, bool]  # Which layers passed/failed
    telemetry: Optional[Dict[str, Any]] = None


@dataclass
class AttackRecord:
    """Record of a blocked attack"""
    attack_id: str
    timestamp: float
    attack_type: str
    category: str
    blocked_by_layer: str
    severity: float
    code_snippet: str
    detection_method: str
    metadata: Dict[str, Any]


class AethelAuditor:
    """
    The Vigilance DB - SQLite-based audit trail.
    
    Stores:
    - Execution logs (every proof attempt)
    - Attack logs (every blocked malicious intent)
    - Telemetry data (performance metrics)
    
    This is the ONLY place where a traditional SQL database is acceptable,
    because it's append-only and doesn't affect state correctness.
    """
    
    def __init__(self, db_path: str = ".aethel_sentinel/telemetry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        
        self._create_tables()
        
        print(f"[AUDITOR] Initialized at: {self.db_path.absolute()}")
    
    def _create_tables(self):
        """Create audit tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Execution logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                bundle_hash TEXT,
                intent_name TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                merkle_root_before TEXT,
                merkle_root_after TEXT,
                timestamp REAL NOT NULL,
                elapsed_ms REAL,
                layer_results TEXT,
                telemetry TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Attack logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attack_id TEXT NOT NULL UNIQUE,
                timestamp REAL NOT NULL,
                attack_type TEXT NOT NULL,
                category TEXT NOT NULL,
                blocked_by_layer TEXT NOT NULL,
                severity REAL NOT NULL,
                code_snippet TEXT,
                detection_method TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Telemetry metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                timestamp REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_tx_id ON execution_logs(tx_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_status ON execution_logs(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_execution_timestamp ON execution_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attack_timestamp ON attack_logs(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attack_type ON attack_logs(attack_type)")
        
        self.conn.commit()
    
    def log_execution(self, record: ExecutionRecord) -> int:
        """
        Log an execution attempt.
        
        Returns:
            Record ID
        """
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO execution_logs (
                tx_id, bundle_hash, intent_name, status, result,
                merkle_root_before, merkle_root_after, timestamp, elapsed_ms,
                layer_results, telemetry
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.tx_id,
            record.bundle_hash,
            record.intent_name,
            record.status,
            json.dumps(record.result),
            record.merkle_root_before,
            record.merkle_root_after,
            record.timestamp,
            record.elapsed_ms,
            json.dumps(record.layer_results),
            json.dumps(record.telemetry) if record.telemetry else None
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def log_attack(self, record: AttackRecord) -> int:
        """
        Log a blocked attack.
        
        Returns:
            Record ID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO attack_logs (
                    attack_id, timestamp, attack_type, category,
                    blocked_by_layer, severity, code_snippet,
                    detection_method, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.attack_id,
                record.timestamp,
                record.attack_type,
                record.category,
                record.blocked_by_layer,
                record.severity,
                record.code_snippet,
                record.detection_method,
                json.dumps(record.metadata)
            ))
            
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Attack already logged (duplicate attack_id)
            return -1
    
    def log_metric(self, tx_id: str, metric_name: str, metric_value: float, timestamp: float):
        """Log a telemetry metric"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO telemetry_metrics (tx_id, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?)
        """, (tx_id, metric_name, metric_value, timestamp))
        
        self.conn.commit()
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        cursor = self.conn.cursor()
        
        # Total executions
        cursor.execute("SELECT COUNT(*) as total FROM execution_logs")
        total = cursor.fetchone()['total']
        
        # Status breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM execution_logs
            GROUP BY status
        """)
        status_breakdown = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Average execution time
        cursor.execute("SELECT AVG(elapsed_ms) as avg_time FROM execution_logs WHERE elapsed_ms IS NOT NULL")
        avg_time = cursor.fetchone()['avg_time'] or 0
        
        return {
            'total_executions': total,
            'status_breakdown': status_breakdown,
            'avg_execution_time_ms': avg_time
        }
    
    def get_attack_stats(self) -> Dict[str, Any]:
        """Get attack statistics"""
        cursor = self.conn.cursor()
        
        # Total attacks
        cursor.execute("SELECT COUNT(*) as total FROM attack_logs")
        total = cursor.fetchone()['total']
        
        # Attack type breakdown
        cursor.execute("""
            SELECT attack_type, COUNT(*) as count
            FROM attack_logs
            GROUP BY attack_type
        """)
        type_breakdown = {row['attack_type']: row['count'] for row in cursor.fetchall()}
        
        # Layer breakdown
        cursor.execute("""
            SELECT blocked_by_layer, COUNT(*) as count
            FROM attack_logs
            GROUP BY blocked_by_layer
        """)
        layer_breakdown = {row['blocked_by_layer']: row['count'] for row in cursor.fetchall()}
        
        return {
            'total_attacks_blocked': total,
            'attack_type_breakdown': type_breakdown,
            'layer_breakdown': layer_breakdown
        }
    
    def get_recent_executions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution logs"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM execution_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_recent_attacks(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent attack logs"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT * FROM attack_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class MerkleStateDB:
    """
    The Reality DB - Authenticated State Storage.
    
    Simulates RocksDB-style key-value store with Merkle Tree authentication.
    In production, this would use actual RocksDB or LevelDB.
    
    Every entry is linked to a Merkle Root. If the database is modified
    outside the system, the root hash breaks and the system detects tampering.
    """
    
    def __init__(self, db_path: str = ".aethel_state"):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        self.snapshot_path = self.db_path / "snapshot.json"
        self.wal_path = self.db_path / "wal.log"  # Write-ahead log
        
        # In-memory state (would be RocksDB in production)
        self.state = {}
        self.merkle_root = None
        
        # Load from disk if exists
        self._load_snapshot()
        
        print(f"[MERKLE DB] Initialized at: {self.db_path.absolute()}")
        if self.merkle_root:
            print(f"   Root: {self.merkle_root[:32]}...")
    
    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root from current state"""
        if not self.state:
            return hashlib.sha256(b"empty").hexdigest()
        
        # Sort keys for deterministic ordering
        sorted_items = sorted(self.state.items())
        
        # Combine all key-value hashes
        combined = ""
        for key, value in sorted_items:
            entry_hash = hashlib.sha256(f"{key}:{json.dumps(value)}".encode()).hexdigest()
            combined += entry_hash
        
        # Generate root hash
        root = hashlib.sha256(combined.encode()).hexdigest()
        return root
    
    def put(self, key: str, value: Any):
        """Store key-value pair and update Merkle root"""
        self.state[key] = value
        self.merkle_root = self._calculate_merkle_root()
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key"""
        return self.state.get(key)
    
    def delete(self, key: str):
        """Delete key and update Merkle root"""
        if key in self.state:
            del self.state[key]
            self.merkle_root = self._calculate_merkle_root()
    
    def get_root(self) -> str:
        """Get current Merkle root"""
        return self.merkle_root
    
    def verify_integrity(self) -> bool:
        """Verify database integrity by recalculating Merkle root"""
        calculated_root = self._calculate_merkle_root()
        return calculated_root == self.merkle_root
    
    def save_snapshot(self):
        """Save state snapshot to disk"""
        snapshot = {
            'state': self.state,
            'merkle_root': self.merkle_root,
            'timestamp': time.time()
        }
        
        with open(self.snapshot_path, 'w') as f:
            json.dump(snapshot, f, indent=2)
        
        print(f"[MERKLE DB] Snapshot saved: {self.snapshot_path}")
    
    def _load_snapshot(self):
        """Load state snapshot from disk"""
        if not self.snapshot_path.exists():
            return
        
        try:
            with open(self.snapshot_path, 'r') as f:
                snapshot = json.load(f)
            
            # Check if snapshot has new format
            if 'state' not in snapshot:
                print(f"[MERKLE DB] Old snapshot format detected, skipping load")
                return
            
            self.state = snapshot['state']
            self.merkle_root = snapshot['merkle_root']
            
            # Verify integrity
            if not self.verify_integrity():
                raise ValueError("DATABASE CORRUPTION DETECTED! Merkle root mismatch.")
            
            print(f"[MERKLE DB] Snapshot loaded: {self.snapshot_path}")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[MERKLE DB] Failed to load snapshot: {e}, starting fresh")


class ContentAddressableVault:
    """
    The Truth DB - Content-Addressable Code Storage.
    
    Simulates IPFS-style storage where code is addressed by its hash.
    You don't fetch by id=10, you fetch by SHA-256 hash of the code.
    
    This guarantees that the code you're running today is EXACTLY
    the same code that was proved last year.
    """
    
    def __init__(self, vault_path: str = ".aethel_vault"):
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        self.bundles_path = self.vault_path / "bundles"
        self.bundles_path.mkdir(exist_ok=True)
        
        self.index_path = self.vault_path / "index.json"
        
        # Load index
        self.index = self._load_index()
        
        print(f"[VAULT DB] Initialized at: {self.vault_path.absolute()}")
        print(f"   Bundles: {len(self.index)}")
    
    def store_bundle(self, code: str, metadata: Dict[str, Any]) -> str:
        """
        Store code bundle and return its content hash.
        
        Args:
            code: The verified code
            metadata: Additional metadata (intent_name, verification_result, etc.)
        
        Returns:
            Content hash (SHA-256)
        """
        # Calculate content hash
        content_hash = hashlib.sha256(code.encode()).hexdigest()
        
        # Check if already exists
        if content_hash in self.index:
            print(f"[VAULT DB] Bundle already exists: {content_hash[:16]}...")
            return content_hash
        
        # Store bundle
        bundle_path = self.bundles_path / f"{content_hash[:16]}.ae_bundle"
        
        bundle = {
            'code': code,
            'metadata': metadata,
            'content_hash': content_hash,
            'timestamp': time.time()
        }
        
        with open(bundle_path, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        # Update index
        self.index[content_hash] = {
            'intent_name': metadata.get('intent_name', 'unknown'),
            'bundle_path': str(bundle_path),
            'timestamp': bundle['timestamp']
        }
        self._save_index()
        
        print(f"[VAULT DB] Bundle stored: {content_hash[:16]}...")
        
        return content_hash
    
    def fetch_bundle(self, content_hash: str) -> Optional[Dict[str, Any]]:
        """Fetch bundle by content hash"""
        if content_hash not in self.index:
            return None
        
        bundle_path = Path(self.index[content_hash]['bundle_path'])
        
        if not bundle_path.exists():
            return None
        
        with open(bundle_path, 'r') as f:
            return json.load(f)
    
    def verify_bundle(self, content_hash: str) -> bool:
        """Verify bundle integrity by recalculating hash"""
        bundle = self.fetch_bundle(content_hash)
        
        if not bundle:
            return False
        
        # Recalculate hash
        calculated_hash = hashlib.sha256(bundle['code'].encode()).hexdigest()
        
        return calculated_hash == content_hash
    
    def list_bundles(self) -> List[Dict[str, Any]]:
        """List all bundles"""
        return [
            {
                'content_hash': hash_val,
                **info
            }
            for hash_val, info in self.index.items()
        ]
    
    def _save_index(self):
        """Save index to disk"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def _load_index(self) -> Dict[str, Any]:
        """Load index from disk"""
        if not self.index_path.exists():
            return {}
        
        with open(self.index_path, 'r') as f:
            return json.load(f)


class AethelPersistenceLayer:
    """
    Complete Persistence Layer - The Sovereign Memory.
    
    Integrates three databases:
    1. Reality DB (Merkle State) - Authenticated state storage
    2. Truth DB (Vault) - Content-addressable code storage
    3. Vigilance DB (Audit Logs) - Execution and attack logs
    
    Philosophy: "A system that forgets is a system that can be deceived."
    """
    
    def __init__(
        self,
        state_path: str = ".aethel_state",
        vault_path: str = ".aethel_vault",
        audit_path: str = ".aethel_sentinel/telemetry.db"
    ):
        print("\n" + "="*70)
        print("AETHEL PERSISTENCE LAYER v2.1.0 - INITIALIZING")
        print("="*70 + "\n")
        
        self.merkle_db = MerkleStateDB(state_path)
        self.vault_db = ContentAddressableVault(vault_path)
        self.auditor = AethelAuditor(audit_path)
        
        print("\n" + "="*70)
        print("PERSISTENCE LAYER READY")
        print("="*70 + "\n")
    
    def save_execution(
        self,
        tx_id: str,
        bundle_hash: str,
        intent_name: str,
        status: str,
        result: Dict[str, Any],
        merkle_root_before: Optional[str],
        merkle_root_after: Optional[str],
        elapsed_ms: float,
        layer_results: Dict[str, bool],
        telemetry: Optional[Dict[str, Any]] = None
    ) -> int:
        """Save execution record to audit log"""
        record = ExecutionRecord(
            tx_id=tx_id,
            bundle_hash=bundle_hash,
            intent_name=intent_name,
            status=status,
            result=result,
            merkle_root_before=merkle_root_before,
            merkle_root_after=merkle_root_after,
            timestamp=time.time(),
            elapsed_ms=elapsed_ms,
            layer_results=layer_results,
            telemetry=telemetry
        )
        
        return self.auditor.log_execution(record)
    
    def save_attack(
        self,
        attack_type: str,
        category: str,
        blocked_by_layer: str,
        severity: float,
        code_snippet: str,
        detection_method: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Save attack record to audit log"""
        attack_id = hashlib.sha256(
            f"{attack_type}_{time.time()}_{code_snippet[:100]}".encode()
        ).hexdigest()[:16]
        
        record = AttackRecord(
            attack_id=attack_id,
            timestamp=time.time(),
            attack_type=attack_type,
            category=category,
            blocked_by_layer=blocked_by_layer,
            severity=severity,
            code_snippet=code_snippet,
            detection_method=detection_method,
            metadata=metadata
        )
        
        return self.auditor.log_attack(record)
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        exec_stats = self.auditor.get_execution_stats()
        attack_stats = self.auditor.get_attack_stats()
        
        return {
            'executions': exec_stats,
            'attacks': attack_stats,
            'merkle_root': self.merkle_db.get_root(),
            'total_bundles': len(self.vault_db.index)
        }
    
    def close(self):
        """Close all database connections"""
        self.auditor.close()
        print("\n[PERSISTENCE] All databases closed")


# Global instance (singleton pattern)
_persistence_layer = None


def get_persistence_layer() -> AethelPersistenceLayer:
    """Get global persistence layer instance"""
    global _persistence_layer
    
    if _persistence_layer is None:
        state_path = os.getenv("AETHEL_STATE_PATH", ".aethel_state")
        vault_path = os.getenv("AETHEL_VAULT_PATH", ".aethel_vault")
        audit_path = os.getenv("AETHEL_AUDIT_PATH", ".aethel_sentinel/telemetry.db")
        _persistence_layer = AethelPersistenceLayer(
            state_path=state_path,
            vault_path=vault_path,
            audit_path=audit_path,
        )
    
    return _persistence_layer
