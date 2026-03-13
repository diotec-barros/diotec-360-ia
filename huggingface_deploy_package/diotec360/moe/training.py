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
Expert Training and Adaptation System

Implements ground truth collection, accuracy calculation, and A/B testing
for continuous improvement of MOE expert models.

Key Features:
- Ground truth collection from actual outcomes
- Per-expert accuracy calculation over rolling windows
- Confidence threshold adjustment based on historical accuracy
- A/B testing framework for expert model comparison
- Automatic promotion of better-performing models

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import sqlite3
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import deque
from .telemetry import ExpertTelemetry


@dataclass
class GroundTruthRecord:
    """
    Ground truth record for expert training.
    
    Attributes:
        transaction_id: Unique transaction identifier
        expert_name: Name of the expert
        expert_verdict: Expert's verdict (APPROVE/REJECT)
        expert_confidence: Expert's confidence score
        actual_outcome: Actual outcome (APPROVE/REJECT)
        was_correct: True if expert verdict matched actual outcome
        timestamp: Unix timestamp when recorded
    """
    transaction_id: str
    expert_name: str
    expert_verdict: str
    expert_confidence: float
    actual_outcome: str
    was_correct: bool
    timestamp: float


@dataclass
class AccuracyMetrics:
    """
    Accuracy metrics for an expert over a time window.
    
    Attributes:
        expert_name: Name of the expert
        window_size: Number of transactions in rolling window
        accuracy: Overall accuracy (0.0-1.0)
        true_positives: Count of correct approvals
        true_negatives: Count of correct rejections
        false_positives: Count of incorrect approvals
        false_negatives: Count of incorrect rejections
        precision: Precision score (TP / (TP + FP))
        recall: Recall score (TP / (TP + FN))
        f1_score: F1 score (harmonic mean of precision and recall)
        avg_confidence_correct: Average confidence when correct
        avg_confidence_incorrect: Average confidence when incorrect
    """
    expert_name: str
    window_size: int
    accuracy: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float
    avg_confidence_correct: float
    avg_confidence_incorrect: float


class ExpertTrainingSystem:
    """
    Training and adaptation system for MOE experts.
    
    Manages:
    - Ground truth collection from actual transaction outcomes
    - Accuracy calculation over rolling windows
    - Confidence threshold adjustment
    - Expert model versioning and A/B testing
    - Automatic model promotion
    """
    
    def __init__(self, db_path: str = ".diotec360_moe/training.db"):
        """
        Initialize training system.
        
        Args:
            db_path: Path to SQLite database for training data
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize SQLite database schema for training data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for ground truth records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ground_truth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                transaction_id TEXT NOT NULL,
                expert_name TEXT NOT NULL,
                expert_verdict TEXT NOT NULL,
                expert_confidence REAL NOT NULL,
                actual_outcome TEXT NOT NULL,
                was_correct INTEGER NOT NULL
            )
        ''')
        
        # Table for expert model versions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expert_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expert_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                model_config TEXT,
                deployed_at REAL NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 0,
                ab_test_group TEXT,
                UNIQUE(expert_name, model_version)
            )
        ''')
        
        # Table for model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                expert_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                window_size INTEGER NOT NULL,
                accuracy REAL NOT NULL,
                true_positives INTEGER NOT NULL,
                true_negatives INTEGER NOT NULL,
                false_positives INTEGER NOT NULL,
                false_negatives INTEGER NOT NULL,
                precision REAL NOT NULL,
                recall REAL NOT NULL,
                f1_score REAL NOT NULL,
                avg_confidence_correct REAL NOT NULL,
                avg_confidence_incorrect REAL NOT NULL
            )
        ''')
        
        # Table for confidence threshold adjustments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confidence_thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                expert_name TEXT NOT NULL,
                old_threshold REAL NOT NULL,
                new_threshold REAL NOT NULL,
                reason TEXT NOT NULL
            )
        ''')
        
        # Indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ground_truth_expert_time 
            ON ground_truth(expert_name, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ground_truth_tx 
            ON ground_truth(transaction_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_performance_expert 
            ON model_performance(expert_name, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_expert_models_active 
            ON expert_models(expert_name, is_active)
        ''')
        
        conn.commit()
        conn.close()
        
    def record_ground_truth(
        self,
        transaction_id: str,
        expert_name: str,
        expert_verdict: str,
        expert_confidence: float,
        actual_outcome: str
    ) -> GroundTruthRecord:
        """
        Record ground truth for a transaction.
        
        Args:
            transaction_id: Unique transaction identifier
            expert_name: Name of the expert
            expert_verdict: Expert's verdict (APPROVE/REJECT)
            expert_confidence: Expert's confidence score (0.0-1.0)
            actual_outcome: Actual outcome (APPROVE/REJECT)
            
        Returns:
            GroundTruthRecord with recorded data
        """
        was_correct = (expert_verdict == actual_outcome)
        timestamp = time.time()
        
        record = GroundTruthRecord(
            transaction_id=transaction_id,
            expert_name=expert_name,
            expert_verdict=expert_verdict,
            expert_confidence=expert_confidence,
            actual_outcome=actual_outcome,
            was_correct=was_correct,
            timestamp=timestamp
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO ground_truth 
                (timestamp, transaction_id, expert_name, expert_verdict,
                 expert_confidence, actual_outcome, was_correct)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                transaction_id,
                expert_name,
                expert_verdict,
                expert_confidence,
                actual_outcome,
                1 if was_correct else 0
            ))
            
            conn.commit()
        finally:
            conn.close()
            
        return record
    
    def record_batch_ground_truth(
        self,
        records: List[Tuple[str, str, str, float, str]]
    ) -> List[GroundTruthRecord]:
        """
        Record multiple ground truth records in batch.
        
        Args:
            records: List of tuples (tx_id, expert_name, expert_verdict, 
                    expert_confidence, actual_outcome)
                    
        Returns:
            List of GroundTruthRecord objects
        """
        ground_truth_records = []
        timestamp = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for tx_id, expert_name, expert_verdict, expert_confidence, actual_outcome in records:
                was_correct = (expert_verdict == actual_outcome)
                
                cursor.execute('''
                    INSERT INTO ground_truth 
                    (timestamp, transaction_id, expert_name, expert_verdict,
                     expert_confidence, actual_outcome, was_correct)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    tx_id,
                    expert_name,
                    expert_verdict,
                    expert_confidence,
                    actual_outcome,
                    1 if was_correct else 0
                ))
                
                ground_truth_records.append(GroundTruthRecord(
                    transaction_id=tx_id,
                    expert_name=expert_name,
                    expert_verdict=expert_verdict,
                    expert_confidence=expert_confidence,
                    actual_outcome=actual_outcome,
                    was_correct=was_correct,
                    timestamp=timestamp
                ))
            
            conn.commit()
        finally:
            conn.close()
            
        return ground_truth_records
    
    def get_ground_truth_records(
        self,
        expert_name: Optional[str] = None,
        limit: int = 1000,
        time_window_seconds: Optional[int] = None
    ) -> List[GroundTruthRecord]:
        """
        Retrieve ground truth records.
        
        Args:
            expert_name: Filter by expert name (None for all experts)
            limit: Maximum number of records to return
            time_window_seconds: Only return records within this time window
            
        Returns:
            List of GroundTruthRecord objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = '''
                SELECT transaction_id, expert_name, expert_verdict,
                       expert_confidence, actual_outcome, was_correct, timestamp
                FROM ground_truth
            '''
            
            conditions = []
            params = []
            
            if expert_name is not None:
                conditions.append('expert_name = ?')
                params.append(expert_name)
            
            if time_window_seconds is not None:
                cutoff_time = time.time() - time_window_seconds
                conditions.append('timestamp >= ?')
                params.append(cutoff_time)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            records = []
            for row in cursor.fetchall():
                records.append(GroundTruthRecord(
                    transaction_id=row[0],
                    expert_name=row[1],
                    expert_verdict=row[2],
                    expert_confidence=row[3],
                    actual_outcome=row[4],
                    was_correct=bool(row[5]),
                    timestamp=row[6]
                ))
            
            return records
        finally:
            conn.close()
    
    def get_ground_truth_count(
        self,
        expert_name: Optional[str] = None,
        time_window_seconds: Optional[int] = None
    ) -> int:
        """
        Get count of ground truth records.
        
        Args:
            expert_name: Filter by expert name (None for all experts)
            time_window_seconds: Only count records within this time window
            
        Returns:
            Count of records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            query = 'SELECT COUNT(*) FROM ground_truth'
            
            conditions = []
            params = []
            
            if expert_name is not None:
                conditions.append('expert_name = ?')
                params.append(expert_name)
            
            if time_window_seconds is not None:
                cutoff_time = time.time() - time_window_seconds
                conditions.append('timestamp >= ?')
                params.append(cutoff_time)
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def cleanup_old_ground_truth(self, days_to_keep: int = 90) -> int:
        """
        Remove ground truth data older than specified days.
        
        Args:
            days_to_keep: Number of days of data to retain (default 90)
            
        Returns:
            Number of records deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        
        try:
            cursor.execute('''
                DELETE FROM ground_truth WHERE timestamp < ?
            ''', (cutoff_time,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
        finally:
            conn.close()



    def calculate_accuracy(
        self,
        expert_name: str,
        window_size: int = 1000
    ) -> AccuracyMetrics:
        """
        Calculate accuracy metrics for an expert over rolling window.
        
        Args:
            expert_name: Name of the expert
            window_size: Number of most recent transactions to analyze
            
        Returns:
            AccuracyMetrics with detailed performance metrics
        """
        records = self.get_ground_truth_records(
            expert_name=expert_name,
            limit=window_size
        )
        
        if not records:
            # No data available - return default metrics
            return AccuracyMetrics(
                expert_name=expert_name,
                window_size=0,
                accuracy=0.0,
                true_positives=0,
                true_negatives=0,
                false_positives=0,
                false_negatives=0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                avg_confidence_correct=0.0,
                avg_confidence_incorrect=0.0
            )
        
        # Calculate confusion matrix
        true_positives = 0
        true_negatives = 0
        false_positives = 0
        false_negatives = 0
        
        confidence_correct = []
        confidence_incorrect = []
        
        for record in records:
            if record.expert_verdict == "APPROVE" and record.actual_outcome == "APPROVE":
                true_positives += 1
                confidence_correct.append(record.expert_confidence)
            elif record.expert_verdict == "REJECT" and record.actual_outcome == "REJECT":
                true_negatives += 1
                confidence_correct.append(record.expert_confidence)
            elif record.expert_verdict == "APPROVE" and record.actual_outcome == "REJECT":
                false_positives += 1
                confidence_incorrect.append(record.expert_confidence)
            elif record.expert_verdict == "REJECT" and record.actual_outcome == "APPROVE":
                false_negatives += 1
                confidence_incorrect.append(record.expert_confidence)
        
        # Calculate metrics
        total = len(records)
        accuracy = (true_positives + true_negatives) / total if total > 0 else 0.0
        
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0 else 0.0
        )
        
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0 else 0.0
        )
        
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )
        
        avg_confidence_correct = (
            sum(confidence_correct) / len(confidence_correct)
            if confidence_correct else 0.0
        )
        
        avg_confidence_incorrect = (
            sum(confidence_incorrect) / len(confidence_incorrect)
            if confidence_incorrect else 0.0
        )
        
        metrics = AccuracyMetrics(
            expert_name=expert_name,
            window_size=len(records),
            accuracy=accuracy,
            true_positives=true_positives,
            true_negatives=true_negatives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            avg_confidence_correct=avg_confidence_correct,
            avg_confidence_incorrect=avg_confidence_incorrect
        )
        
        # Store metrics in database
        self._store_accuracy_metrics(metrics)
        
        return metrics
    
    def _store_accuracy_metrics(self, metrics: AccuracyMetrics) -> None:
        """
        Store accuracy metrics in database.
        
        Args:
            metrics: AccuracyMetrics to store
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO model_performance 
                (timestamp, expert_name, model_version, window_size, accuracy,
                 true_positives, true_negatives, false_positives, false_negatives,
                 precision, recall, f1_score, avg_confidence_correct, avg_confidence_incorrect)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                time.time(),
                metrics.expert_name,
                'current',  # Default model version
                metrics.window_size,
                metrics.accuracy,
                metrics.true_positives,
                metrics.true_negatives,
                metrics.false_positives,
                metrics.false_negatives,
                metrics.precision,
                metrics.recall,
                metrics.f1_score,
                metrics.avg_confidence_correct,
                metrics.avg_confidence_incorrect
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def adjust_confidence_threshold(
        self,
        expert_name: str,
        current_threshold: float,
        target_accuracy: float = 0.999,
        window_size: int = 1000
    ) -> float:
        """
        Adjust expert confidence threshold based on historical accuracy.
        
        Strategy:
        - If accuracy > target: Lower threshold (be more lenient)
        - If accuracy < target: Raise threshold (be more strict)
        
        Args:
            expert_name: Name of the expert
            current_threshold: Current confidence threshold
            target_accuracy: Target accuracy (default 0.999 = 99.9%)
            window_size: Number of transactions to analyze
            
        Returns:
            New confidence threshold
        """
        metrics = self.calculate_accuracy(expert_name, window_size)
        
        if metrics.window_size < 100:
            # Not enough data - keep current threshold
            return current_threshold
        
        # Calculate adjustment based on accuracy gap
        accuracy_gap = target_accuracy - metrics.accuracy
        
        # Adjustment factor: 0.1 * accuracy_gap
        # If accuracy is too low, increase threshold
        # If accuracy is too high, decrease threshold
        adjustment = 0.1 * accuracy_gap
        
        # Clamp adjustment to reasonable range
        adjustment = max(-0.1, min(0.1, adjustment))
        
        new_threshold = current_threshold + adjustment
        
        # Clamp threshold to valid range [0.5, 1.0]
        new_threshold = max(0.5, min(1.0, new_threshold))
        
        # Record threshold adjustment
        self._record_threshold_adjustment(
            expert_name,
            current_threshold,
            new_threshold,
            f"Accuracy: {metrics.accuracy:.4f}, Target: {target_accuracy:.4f}, Gap: {accuracy_gap:.4f}"
        )
        
        return new_threshold
    
    def _record_threshold_adjustment(
        self,
        expert_name: str,
        old_threshold: float,
        new_threshold: float,
        reason: str
    ) -> None:
        """
        Record confidence threshold adjustment.
        
        Args:
            expert_name: Name of the expert
            old_threshold: Previous threshold
            new_threshold: New threshold
            reason: Reason for adjustment
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO confidence_thresholds 
                (timestamp, expert_name, old_threshold, new_threshold, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                time.time(),
                expert_name,
                old_threshold,
                new_threshold,
                reason
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_threshold_history(
        self,
        expert_name: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get threshold adjustment history for an expert.
        
        Args:
            expert_name: Name of the expert
            limit: Maximum number of records to return
            
        Returns:
            List of threshold adjustment records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT timestamp, old_threshold, new_threshold, reason
                FROM confidence_thresholds
                WHERE expert_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (expert_name, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row[0],
                    'old_threshold': row[1],
                    'new_threshold': row[2],
                    'reason': row[3]
                })
            
            return history
        finally:
            conn.close()


@dataclass
class ExpertModelVersion:
    """
    Expert model version for A/B testing.
    
    Attributes:
        expert_name: Name of the expert
        model_version: Version identifier (e.g., "v1.0", "v2.0")
        model_config: JSON configuration for the model
        deployed_at: Unix timestamp when deployed
        is_active: Whether this version is currently active
        ab_test_group: A/B test group identifier (e.g., "A", "B")
    """
    expert_name: str
    model_version: str
    model_config: Dict[str, Any]
    deployed_at: float
    is_active: bool
    ab_test_group: Optional[str] = None


class ABTestingFramework:
    """
    A/B testing framework for expert model comparison.
    
    Supports:
    - Multiple model versions per expert
    - Traffic splitting between versions
    - Performance comparison
    - Automatic promotion of better models
    """
    
    def __init__(self, training_system: ExpertTrainingSystem):
        """
        Initialize A/B testing framework.
        
        Args:
            training_system: ExpertTrainingSystem instance
        """
        self.training_system = training_system
        self.db_path = training_system.db_path
    
    def register_model_version(
        self,
        expert_name: str,
        model_version: str,
        model_config: Dict[str, Any],
        ab_test_group: Optional[str] = None
    ) -> ExpertModelVersion:
        """
        Register a new expert model version.
        
        Args:
            expert_name: Name of the expert
            model_version: Version identifier
            model_config: Model configuration dictionary
            ab_test_group: A/B test group identifier
            
        Returns:
            ExpertModelVersion object
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        deployed_at = time.time()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO expert_models 
                (expert_name, model_version, model_config, deployed_at, is_active, ab_test_group)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                expert_name,
                model_version,
                json.dumps(model_config),
                deployed_at,
                0,  # Not active by default
                ab_test_group
            ))
            
            conn.commit()
        finally:
            conn.close()
        
        return ExpertModelVersion(
            expert_name=expert_name,
            model_version=model_version,
            model_config=model_config,
            deployed_at=deployed_at,
            is_active=False,
            ab_test_group=ab_test_group
        )
    
    def activate_model_version(
        self,
        expert_name: str,
        model_version: str
    ) -> None:
        """
        Activate a specific model version (deactivates others).
        
        Args:
            expert_name: Name of the expert
            model_version: Version to activate
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Deactivate all versions for this expert
            cursor.execute('''
                UPDATE expert_models 
                SET is_active = 0
                WHERE expert_name = ?
            ''', (expert_name,))
            
            # Activate specified version
            cursor.execute('''
                UPDATE expert_models 
                SET is_active = 1
                WHERE expert_name = ? AND model_version = ?
            ''', (expert_name, model_version))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_active_model_version(
        self,
        expert_name: str
    ) -> Optional[ExpertModelVersion]:
        """
        Get currently active model version for an expert.
        
        Args:
            expert_name: Name of the expert
            
        Returns:
            ExpertModelVersion if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT model_version, model_config, deployed_at, ab_test_group
                FROM expert_models
                WHERE expert_name = ? AND is_active = 1
            ''', (expert_name,))
            
            row = cursor.fetchone()
            if row:
                return ExpertModelVersion(
                    expert_name=expert_name,
                    model_version=row[0],
                    model_config=json.loads(row[1]) if row[1] else {},
                    deployed_at=row[2],
                    is_active=True,
                    ab_test_group=row[3]
                )
            
            return None
        finally:
            conn.close()
    
    def compare_model_versions(
        self,
        expert_name: str,
        version_a: str,
        version_b: str,
        window_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Compare performance of two model versions.
        
        Args:
            expert_name: Name of the expert
            version_a: First version to compare
            version_b: Second version to compare
            window_size: Number of transactions to analyze
            
        Returns:
            Dictionary with comparison results
        """
        # Calculate accuracy for both versions
        metrics_a = self.training_system.calculate_accuracy(
            f"{expert_name}_{version_a}",
            window_size
        )
        
        metrics_b = self.training_system.calculate_accuracy(
            f"{expert_name}_{version_b}",
            window_size
        )
        
        # Determine winner
        winner = None
        if metrics_a.accuracy > metrics_b.accuracy:
            winner = version_a
        elif metrics_b.accuracy > metrics_a.accuracy:
            winner = version_b
        
        return {
            'expert_name': expert_name,
            'version_a': {
                'version': version_a,
                'metrics': asdict(metrics_a)
            },
            'version_b': {
                'version': version_b,
                'metrics': asdict(metrics_b)
            },
            'winner': winner,
            'accuracy_improvement': metrics_b.accuracy - metrics_a.accuracy if winner == version_b else metrics_a.accuracy - metrics_b.accuracy
        }
    
    def auto_promote_better_model(
        self,
        expert_name: str,
        version_a: str,
        version_b: str,
        window_size: int = 1000,
        min_improvement: float = 0.001
    ) -> Optional[str]:
        """
        Automatically promote better-performing model version.
        
        Args:
            expert_name: Name of the expert
            version_a: Current production version
            version_b: Candidate version
            window_size: Number of transactions to analyze
            min_improvement: Minimum accuracy improvement required for promotion
            
        Returns:
            Promoted version identifier, or None if no promotion
        """
        comparison = self.compare_model_versions(
            expert_name,
            version_a,
            version_b,
            window_size
        )
        
        if comparison['winner'] == version_b:
            improvement = comparison['accuracy_improvement']
            
            if improvement >= min_improvement:
                # Promote version B
                self.activate_model_version(expert_name, version_b)
                return version_b
        
        return None
    
    def get_all_model_versions(
        self,
        expert_name: str
    ) -> List[ExpertModelVersion]:
        """
        Get all registered model versions for an expert.
        
        Args:
            expert_name: Name of the expert
            
        Returns:
            List of ExpertModelVersion objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT model_version, model_config, deployed_at, is_active, ab_test_group
                FROM expert_models
                WHERE expert_name = ?
                ORDER BY deployed_at DESC
            ''', (expert_name,))
            
            versions = []
            for row in cursor.fetchall():
                versions.append(ExpertModelVersion(
                    expert_name=expert_name,
                    model_version=row[0],
                    model_config=json.loads(row[1]) if row[1] else {},
                    deployed_at=row[2],
                    is_active=bool(row[3]),
                    ab_test_group=row[4]
                ))
            
            return versions
        finally:
            conn.close()


# Singleton instances
_training_system_instance: Optional[ExpertTrainingSystem] = None
_ab_testing_instance: Optional[ABTestingFramework] = None


def get_training_system(db_path: str = ".diotec360_moe/training.db") -> ExpertTrainingSystem:
    """
    Get singleton instance of ExpertTrainingSystem.
    
    Args:
        db_path: Path to training database
        
    Returns:
        ExpertTrainingSystem instance
    """
    global _training_system_instance
    if _training_system_instance is None:
        _training_system_instance = ExpertTrainingSystem(db_path)
    return _training_system_instance


def get_ab_testing_framework(
    training_system: Optional[ExpertTrainingSystem] = None
) -> ABTestingFramework:
    """
    Get singleton instance of ABTestingFramework.
    
    Args:
        training_system: ExpertTrainingSystem instance (creates default if None)
        
    Returns:
        ABTestingFramework instance
    """
    global _ab_testing_instance
    if _ab_testing_instance is None:
        if training_system is None:
            training_system = get_training_system()
        _ab_testing_instance = ABTestingFramework(training_system)
    return _ab_testing_instance
