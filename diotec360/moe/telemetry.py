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
ExpertTelemetry - Performance tracking and monitoring for MOE experts

Tracks expert performance metrics in SQLite database:
- Latency per expert per transaction
- Accuracy (true positives, false positives)
- Confidence distribution
- Verdict distribution

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .data_models import ExpertVerdict, MOEResult


class ExpertTelemetry:
    """
    Tracks expert performance metrics for monitoring and optimization.
    
    Stores metrics in SQLite database for:
    - Real-time monitoring
    - Historical analysis
    - Performance optimization
    - Anomaly detection
    """
    
    def __init__(self, db_path: str = ".aethel_moe/telemetry.db"):
        """
        Initialize telemetry system.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for expert verdicts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expert_verdicts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                transaction_id TEXT NOT NULL,
                expert_name TEXT NOT NULL,
                verdict TEXT NOT NULL,
                confidence REAL NOT NULL,
                latency_ms REAL NOT NULL,
                reason TEXT,
                proof_trace TEXT
            )
        ''')
        
        # Table for consensus results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consensus_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                transaction_id TEXT NOT NULL,
                consensus TEXT NOT NULL,
                overall_confidence REAL NOT NULL,
                total_latency_ms REAL NOT NULL,
                activated_experts TEXT NOT NULL
            )
        ''')
        
        # Table for ground truth (for accuracy tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ground_truth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                transaction_id TEXT NOT NULL,
                expert_name TEXT NOT NULL,
                was_correct INTEGER NOT NULL
            )
        ''')
        
        # Indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_verdicts_expert 
            ON expert_verdicts(expert_name, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_verdicts_tx 
            ON expert_verdicts(transaction_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_consensus_tx 
            ON consensus_results(transaction_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ground_truth_expert 
            ON ground_truth(expert_name, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
    def record(self, tx_id: str, verdicts: List[ExpertVerdict], 
              consensus: MOEResult) -> None:
        """
        Record expert verdicts and consensus for telemetry.
        
        Args:
            tx_id: Transaction identifier
            verdicts: List of expert verdicts
            consensus: Aggregated consensus result
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        timestamp = time.time()
        
        try:
            # Record individual expert verdicts
            for verdict in verdicts:
                cursor.execute('''
                    INSERT INTO expert_verdicts 
                    (timestamp, transaction_id, expert_name, verdict, 
                     confidence, latency_ms, reason, proof_trace)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    tx_id,
                    verdict.expert_name,
                    verdict.verdict,
                    verdict.confidence,
                    verdict.latency_ms,
                    verdict.reason,
                    str(verdict.proof_trace) if verdict.proof_trace else None
                ))
            
            # Record consensus result
            cursor.execute('''
                INSERT INTO consensus_results 
                (timestamp, transaction_id, consensus, overall_confidence,
                 total_latency_ms, activated_experts)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                consensus.transaction_id,
                consensus.consensus,
                consensus.overall_confidence,
                consensus.total_latency_ms,
                ','.join(consensus.activated_experts)
            ))
            
            conn.commit()
        finally:
            conn.close()
            
    def record_ground_truth(self, tx_id: str, expert_name: str, 
                           was_correct: bool) -> None:
        """
        Record ground truth for accuracy tracking.
        
        Args:
            tx_id: Transaction identifier
            expert_name: Name of the expert
            was_correct: True if expert verdict matched ground truth
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO ground_truth 
                (timestamp, transaction_id, expert_name, was_correct)
                VALUES (?, ?, ?, ?)
            ''', (
                time.time(),
                tx_id,
                expert_name,
                1 if was_correct else 0
            ))
            conn.commit()
        finally:
            conn.close()
            
    def get_expert_stats(self, expert_name: str, 
                        time_window_seconds: int = 3600) -> Dict[str, Any]:
        """
        Get performance statistics for a specific expert.
        
        Args:
            expert_name: Name of the expert
            time_window_seconds: Time window for statistics (default: 1 hour)
            
        Returns:
            Dictionary with performance metrics:
            - average_latency_ms: Average latency
            - accuracy: Accuracy if ground truth available
            - confidence_avg: Average confidence
            - confidence_std: Standard deviation of confidence
            - verdict_distribution: Count of approvals vs rejections
            - total_verifications: Total number of verifications
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - time_window_seconds
        
        try:
            # Get latency and confidence stats
            cursor.execute('''
                SELECT 
                    AVG(latency_ms) as avg_latency,
                    AVG(confidence) as avg_confidence,
                    COUNT(*) as total_verifications,
                    SUM(CASE WHEN verdict = 'APPROVE' THEN 1 ELSE 0 END) as approvals,
                    SUM(CASE WHEN verdict = 'REJECT' THEN 1 ELSE 0 END) as rejections
                FROM expert_verdicts
                WHERE expert_name = ? AND timestamp >= ?
            ''', (expert_name, cutoff_time))
            
            row = cursor.fetchone()
            
            if row and row[2] > 0:  # If we have data
                avg_latency, avg_confidence, total, approvals, rejections = row
                
                # Get accuracy from ground truth
                cursor.execute('''
                    SELECT AVG(was_correct) as accuracy
                    FROM ground_truth
                    WHERE expert_name = ? AND timestamp >= ?
                ''', (expert_name, cutoff_time))
                
                accuracy_row = cursor.fetchone()
                accuracy = accuracy_row[0] if accuracy_row and accuracy_row[0] is not None else None
                
                # Calculate confidence standard deviation
                cursor.execute('''
                    SELECT confidence
                    FROM expert_verdicts
                    WHERE expert_name = ? AND timestamp >= ?
                ''', (expert_name, cutoff_time))
                
                confidences = [row[0] for row in cursor.fetchall()]
                confidence_std = 0.0
                if len(confidences) > 1:
                    mean = sum(confidences) / len(confidences)
                    variance = sum((x - mean) ** 2 for x in confidences) / len(confidences)
                    confidence_std = variance ** 0.5
                
                return {
                    'expert_name': expert_name,
                    'time_window_seconds': time_window_seconds,
                    'average_latency_ms': avg_latency,
                    'accuracy': accuracy,
                    'confidence_avg': avg_confidence,
                    'confidence_std': confidence_std,
                    'verdict_distribution': {
                        'approvals': approvals,
                        'rejections': rejections
                    },
                    'total_verifications': total
                }
            else:
                # No data available
                return {
                    'expert_name': expert_name,
                    'time_window_seconds': time_window_seconds,
                    'average_latency_ms': 0.0,
                    'accuracy': None,
                    'confidence_avg': 0.0,
                    'confidence_std': 0.0,
                    'verdict_distribution': {
                        'approvals': 0,
                        'rejections': 0
                    },
                    'total_verifications': 0
                }
        finally:
            conn.close()
            
    def get_all_experts_stats(self, time_window_seconds: int = 3600) -> List[Dict[str, Any]]:
        """
        Get statistics for all experts.
        
        Args:
            time_window_seconds: Time window for statistics (default: 1 hour)
            
        Returns:
            List of statistics dictionaries, one per expert
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - time_window_seconds
        
        try:
            # Get list of all experts
            cursor.execute('''
                SELECT DISTINCT expert_name
                FROM expert_verdicts
                WHERE timestamp >= ?
            ''', (cutoff_time,))
            
            expert_names = [row[0] for row in cursor.fetchall()]
            
            # Get stats for each expert
            return [self.get_expert_stats(name, time_window_seconds) 
                   for name in expert_names]
        finally:
            conn.close()
            
    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        stats = self.get_all_experts_stats(time_window_seconds=3600)
        
        lines = []
        lines.append("# HELP moe_expert_latency_ms Average expert latency in milliseconds")
        lines.append("# TYPE moe_expert_latency_ms gauge")
        
        for stat in stats:
            lines.append(f'moe_expert_latency_ms{{expert="{stat["expert_name"]}"}} {stat["average_latency_ms"]}')
        
        lines.append("")
        lines.append("# HELP moe_expert_accuracy Expert accuracy (0.0 to 1.0)")
        lines.append("# TYPE moe_expert_accuracy gauge")
        
        for stat in stats:
            if stat["accuracy"] is not None:
                lines.append(f'moe_expert_accuracy{{expert="{stat["expert_name"]}"}} {stat["accuracy"]}')
        
        lines.append("")
        lines.append("# HELP moe_expert_confidence_avg Average expert confidence")
        lines.append("# TYPE moe_expert_confidence_avg gauge")
        
        for stat in stats:
            lines.append(f'moe_expert_confidence_avg{{expert="{stat["expert_name"]}"}} {stat["confidence_avg"]}')
        
        lines.append("")
        lines.append("# HELP moe_expert_verifications_total Total verifications per expert")
        lines.append("# TYPE moe_expert_verifications_total counter")
        
        for stat in stats:
            lines.append(f'moe_expert_verifications_total{{expert="{stat["expert_name"]}"}} {stat["total_verifications"]}')
        
        return "\n".join(lines)
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """
        Remove telemetry data older than specified days.
        
        Args:
            days_to_keep: Number of days of data to retain
            
        Returns:
            Number of records deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        try:
            # Delete old verdicts
            cursor.execute('''
                DELETE FROM expert_verdicts WHERE timestamp < ?
            ''', (cutoff_time,))
            verdicts_deleted = cursor.rowcount
            
            # Delete old consensus results
            cursor.execute('''
                DELETE FROM consensus_results WHERE timestamp < ?
            ''', (cutoff_time,))
            consensus_deleted = cursor.rowcount
            
            # Delete old ground truth
            cursor.execute('''
                DELETE FROM ground_truth WHERE timestamp < ?
            ''', (cutoff_time,))
            ground_truth_deleted = cursor.rowcount
            
            conn.commit()
            
            total_deleted = verdicts_deleted + consensus_deleted + ground_truth_deleted
            return total_deleted
        finally:
            conn.close()


# Singleton instance
_telemetry_instance: Optional[ExpertTelemetry] = None


def get_expert_telemetry(db_path: str = ".aethel_moe/telemetry.db") -> ExpertTelemetry:
    """
    Get singleton instance of ExpertTelemetry.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        ExpertTelemetry instance
    """
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = ExpertTelemetry(db_path)
    return _telemetry_instance
