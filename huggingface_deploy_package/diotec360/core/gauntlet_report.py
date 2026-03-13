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
Gauntlet Report - Attack Forensics and Logging

This module implements the Gauntlet Report system, which logs all blocked
attacks with complete forensics data, categorization, statistics, and
multi-format export capabilities.

Key Features:
- Complete attack record logging
- Attack categorization (injection, DoS, Trojan, overflow, etc.)
- Time-based statistics aggregation
- Multi-format export (JSON, PDF)
- 90-day retention policy
- SQLite persistence

Research Foundation:
Based on Security Information and Event Management (SIEM) systems that
provide centralized logging, correlation, and forensics for security events.
"""

import sqlite3
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path
from enum import Enum


class AttackCategory(Enum):
    """Attack categories for classification"""
    INJECTION = "injection"
    DOS = "dos"
    TROJAN = "trojan"
    OVERFLOW = "overflow"
    CONSERVATION = "conservation"
    UNKNOWN = "unknown"


@dataclass
class AttackRecord:
    """Complete record of a blocked attack"""
    timestamp: float
    attack_type: str
    category: str
    code_snippet: str
    detection_method: str
    severity: float
    blocked_by_layer: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttackRecord':
        """Create from dictionary"""
        return cls(**data)


class GauntletReport:
    """
    Gauntlet Report - Attack Forensics and Logging
    
    Provides complete attack logging and forensics:
    - Logs all blocked attacks with full context
    - Categorizes attacks by type
    - Aggregates statistics by time window
    - Exports to JSON and PDF formats
    - Enforces 90-day retention policy
    
    Properties Validated:
    - Property 39: Complete attack record
    - Property 40: Attack categorization
    - Property 41: Time-based aggregation
    - Property 42: Multi-format export
    - Property 43: Retention policy compliance
    """
    
    def __init__(self, db_path: str = "data/gauntlet.db"):
        """
        Initialize Gauntlet Report
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attack_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                attack_type TEXT NOT NULL,
                category TEXT NOT NULL,
                code_snippet TEXT NOT NULL,
                detection_method TEXT NOT NULL,
                severity REAL NOT NULL,
                blocked_by_layer TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)
        
        # Create index for time-based queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON attack_records(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def log_attack(self, record: AttackRecord) -> None:
        """
        Log a blocked attack
        
        Args:
            record: Attack record to log
        
        Validates: Requirements 7.1, 7.2, 7.3, 7.4
        Property 39: Complete attack record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO attack_records 
            (timestamp, attack_type, category, code_snippet, detection_method, 
             severity, blocked_by_layer, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.timestamp,
            record.attack_type,
            record.category,
            record.code_snippet,
            record.detection_method,
            record.severity,
            record.blocked_by_layer,
            json.dumps(record.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def categorize_attack(self, attack_type: str) -> AttackCategory:
        """
        Categorize attack by type
        
        Args:
            attack_type: Type of attack
        
        Returns:
            Attack category
        
        Validates: Requirements 7.5
        Property 40: Attack categorization
        """
        attack_type_lower = attack_type.lower()
        
        if "injection" in attack_type_lower or "sql" in attack_type_lower:
            return AttackCategory.INJECTION
        elif "dos" in attack_type_lower or "denial" in attack_type_lower:
            return AttackCategory.DOS
        elif "trojan" in attack_type_lower or "malware" in attack_type_lower:
            return AttackCategory.TROJAN
        elif "overflow" in attack_type_lower or "buffer" in attack_type_lower:
            return AttackCategory.OVERFLOW
        elif "conservation" in attack_type_lower or "balance" in attack_type_lower:
            return AttackCategory.CONSERVATION
        else:
            return AttackCategory.UNKNOWN
    
    def get_statistics(self, time_window: Optional[float] = None) -> Dict[str, Any]:
        """
        Get attack statistics
        
        Args:
            time_window: Time window in seconds (None = all time)
        
        Returns:
            Statistics dictionary
        
        Validates: Requirements 7.6
        Property 41: Time-based aggregation
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with optional time filter
        if time_window:
            cutoff_time = time.time() - time_window
            cursor.execute("""
                SELECT category, detection_method, COUNT(*), AVG(severity)
                FROM attack_records
                WHERE timestamp >= ?
                GROUP BY category, detection_method
            """, (cutoff_time,))
        else:
            cursor.execute("""
                SELECT category, detection_method, COUNT(*), AVG(severity)
                FROM attack_records
                GROUP BY category, detection_method
            """)
        
        results = cursor.fetchall()
        
        # Aggregate statistics
        stats = {
            "total_attacks": 0,
            "by_category": {},
            "by_detection_method": {},
            "average_severity": 0.0
        }
        
        total_severity = 0.0
        for category, method, count, avg_severity in results:
            stats["total_attacks"] += count
            total_severity += avg_severity * count
            
            if category not in stats["by_category"]:
                stats["by_category"][category] = 0
            stats["by_category"][category] += count
            
            if method not in stats["by_detection_method"]:
                stats["by_detection_method"][method] = 0
            stats["by_detection_method"][method] += count
        
        if stats["total_attacks"] > 0:
            stats["average_severity"] = total_severity / stats["total_attacks"]
        
        conn.close()
        return stats
    
    def export_json(self, output_path: str, time_window: Optional[float] = None) -> None:
        """
        Export attack records to JSON
        
        Args:
            output_path: Output file path
            time_window: Time window in seconds (None = all time)
        
        Validates: Requirements 7.7
        Property 42: Multi-format export
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if time_window:
            cutoff_time = time.time() - time_window
            cursor.execute("""
                SELECT timestamp, attack_type, category, code_snippet, 
                       detection_method, severity, blocked_by_layer, metadata
                FROM attack_records
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (cutoff_time,))
        else:
            cursor.execute("""
                SELECT timestamp, attack_type, category, code_snippet, 
                       detection_method, severity, blocked_by_layer, metadata
                FROM attack_records
                ORDER BY timestamp DESC
            """)
        
        records = []
        for row in cursor.fetchall():
            records.append({
                "timestamp": row[0],
                "attack_type": row[1],
                "category": row[2],
                "code_snippet": row[3],
                "detection_method": row[4],
                "severity": row[5],
                "blocked_by_layer": row[6],
                "metadata": json.loads(row[7])
            })
        
        # Write to file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump({
                "export_time": time.time(),
                "total_records": len(records),
                "records": records
            }, f, indent=2)
        
        conn.close()
    
    def export_pdf(self, output_path: str, time_window: Optional[float] = None) -> None:
        """
        Export attack statistics to PDF
        
        Args:
            output_path: Output file path
            time_window: Time window in seconds (None = all time)
        
        Validates: Requirements 7.7
        Property 42: Multi-format export
        
        Note: Simplified PDF export (text-based). Full PDF with reportlab
        would require additional dependencies.
        """
        stats = self.get_statistics(time_window)
        
        # Create simple text report
        report = []
        report.append("=" * 60)
        report.append("GAUNTLET REPORT - ATTACK FORENSICS")
        report.append("=" * 60)
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        report.append(f"Total Attacks: {stats['total_attacks']}")
        report.append(f"Average Severity: {stats['average_severity']:.2f}")
        report.append("")
        report.append("Attacks by Category:")
        for category, count in stats['by_category'].items():
            report.append(f"  {category}: {count}")
        report.append("")
        report.append("Attacks by Detection Method:")
        for method, count in stats['by_detection_method'].items():
            report.append(f"  {method}: {count}")
        report.append("=" * 60)
        
        # Write to file
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
    
    def cleanup_old_records(self, retention_days: int = 90) -> int:
        """
        Clean up old attack records
        
        Args:
            retention_days: Number of days to retain (default 90)
        
        Returns:
            Number of records deleted
        
        Validates: Requirements 7.8
        Property 43: Retention policy compliance
        """
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count records to delete
        cursor.execute("""
            SELECT COUNT(*) FROM attack_records WHERE timestamp < ?
        """, (cutoff_time,))
        count = cursor.fetchone()[0]
        
        # Delete old records
        cursor.execute("""
            DELETE FROM attack_records WHERE timestamp < ?
        """, (cutoff_time,))
        
        conn.commit()
        conn.close()
        
        return count
    
    def get_recent_attacks(self, limit: int = 100) -> List[AttackRecord]:
        """
        Get recent attack records
        
        Args:
            limit: Maximum number of records to return
        
        Returns:
            List of attack records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, attack_type, category, code_snippet, 
                   detection_method, severity, blocked_by_layer, metadata
            FROM attack_records
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        records = []
        for row in cursor.fetchall():
            records.append(AttackRecord(
                timestamp=row[0],
                attack_type=row[1],
                category=row[2],
                code_snippet=row[3],
                detection_method=row[4],
                severity=row[5],
                blocked_by_layer=row[6],
                metadata=json.loads(row[7])
            ))
        
        conn.close()
        return records
