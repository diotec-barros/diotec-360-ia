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
Aethel Sentinel Monitor - Core Telemetry System
The nervous system that feels every pulse of the machine.

This module implements the Sentinel Heart, tracking resource consumption
per transaction to detect anomalies before they become attacks.

Research Foundation:
- Darktrace's Enterprise Immune System (unsupervised ML for anomaly detection)
- Statistical process control (z-score based deviation detection)
- Biological immune system principles (baseline learning, anomaly flagging)

Author: Kiro AI - Engenheiro-Chefe
Version: v1.9.0 "The Autonomous Sentinel"
Date: February 4, 2026
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import time
import psutil
import statistics
import json
import sqlite3
import threading
from pathlib import Path

from diotec360.core.thread_cpu_accounting import (
    ThreadCPUAccounting,
    ThreadCPUContext,
    ThreadCPUMetrics,
    CPUViolation
)


@dataclass
class TransactionMetrics:
    """
    Metrics captured for a single transaction.
    
    This is the "pulse reading" of each transaction - we measure:
    - Time: When did it start/end?
    - CPU: How much processor time did it consume?
    - Memory: How much RAM delta occurred?
    - Z3: How long did the theorem prover take?
    - Layers: Which defense layers passed/failed?
    - Anomaly: How abnormal is this transaction?
    - Thread CPU: Per-thread CPU consumption (RVC-004)
    
    Attributes:
        tx_id: Unique transaction identifier
        start_time: Unix timestamp when transaction began
        end_time: Unix timestamp when transaction completed (None if in progress)
        cpu_time_ms: CPU time consumed in milliseconds
        memory_delta_mb: Memory delta in megabytes (can be negative)
        z3_duration_ms: Time spent in Z3 solver in milliseconds
        layer_results: Dict mapping layer name to pass/fail boolean
        anomaly_score: Normalized score 0.0-1.0 (0.0=normal, 1.0=extreme anomaly)
        thread_cpu_ms: Per-thread CPU time in milliseconds (RVC-004)
        cpu_violation: Whether thread CPU threshold was exceeded (RVC-004)
    """
    tx_id: str
    start_time: float
    end_time: Optional[float] = None
    cpu_time_ms: float = 0.0
    memory_delta_mb: float = 0.0
    z3_duration_ms: float = 0.0
    layer_results: Dict[str, bool] = field(default_factory=dict)
    anomaly_score: float = 0.0
    thread_cpu_ms: float = 0.0
    cpu_violation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'tx_id': self.tx_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'cpu_time_ms': self.cpu_time_ms,
            'memory_delta_mb': self.memory_delta_mb,
            'z3_duration_ms': self.z3_duration_ms,
            'layer_results': self.layer_results,
            'anomaly_score': self.anomaly_score,
            'thread_cpu_ms': self.thread_cpu_ms,
            'cpu_violation': self.cpu_violation
        }


@dataclass
class SystemBaseline:
    """
    Statistical baseline for normal system behavior.
    
    This is the "immune system memory" - we learn what "healthy" looks like
    by tracking the last 1000 transactions. Any transaction that deviates
    significantly from this baseline is flagged as anomalous.
    
    Uses z-score calculation:
        z = (observed - mean) / std_dev
    
    If z > 3.0 (more than 3 standard deviations), it's anomalous.
    
    Attributes:
        avg_cpu_ms: Average CPU time across baseline window
        avg_memory_mb: Average memory delta across baseline window
        avg_z3_ms: Average Z3 duration across baseline window
        std_dev_cpu: Standard deviation of CPU time
        std_dev_memory: Standard deviation of memory delta
        std_dev_z3: Standard deviation of Z3 duration
        window_size: Number of transactions in rolling window (default: 1000)
    """
    avg_cpu_ms: float = 0.0
    avg_memory_mb: float = 0.0
    avg_z3_ms: float = 0.0
    std_dev_cpu: float = 1.0  # Initialize to 1.0 to avoid division by zero
    std_dev_memory: float = 1.0
    std_dev_z3: float = 1.0
    window_size: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'avg_cpu_ms': self.avg_cpu_ms,
            'avg_memory_mb': self.avg_memory_mb,
            'avg_z3_ms': self.avg_z3_ms,
            'std_dev_cpu': self.std_dev_cpu,
            'std_dev_memory': self.std_dev_memory,
            'std_dev_z3': self.std_dev_z3,
            'window_size': self.window_size
        }


class SentinelMonitor:
    """
    The Sentinel Heart - Central telemetry system.
    
    This is the nervous system of the Autonomous Sentinel. It:
    1. Records the start of each transaction (baseline snapshot)
    2. Measures resource consumption during execution
    3. Calculates anomaly scores using statistical deviation
    4. Maintains a rolling baseline of "normal" behavior
    5. Triggers Crisis Mode when anomaly rate exceeds threshold
    
    The monitor uses a circular buffer (deque) to maintain the last 1000
    transactions for baseline calculation. This ensures we adapt to changing
    workload patterns while detecting sudden anomalies.
    
    Research Foundation:
    - Darktrace's unsupervised learning approach
    - Statistical process control (SPC) for manufacturing quality
    - Biological immune systems (self/non-self discrimination)
    """
    
    def __init__(self, db_path: str = ".diotec360_sentinel/telemetry.db"):
        """
        Initialize the Sentinel Monitor.
        
        Args:
            db_path: Path to SQLite database for persistent telemetry storage
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Rolling window of metrics for baseline calculation
        # Using deque with maxlen ensures O(1) append and automatic eviction
        self.metrics_window: deque[TransactionMetrics] = deque(maxlen=1000)
        
        # Current baseline (updated after each transaction)
        self.baseline = SystemBaseline()
        
        # Active transactions (tx_id -> start state)
        self.active_transactions: Dict[str, Dict[str, Any]] = {}
        
        # Thread CPU accounting (RVC-004)
        self.thread_cpu_accounting = ThreadCPUAccounting(cpu_threshold_ms=100.0)
        
        # Active threads (thread_id -> ThreadCPUContext)
        self.active_threads: Dict[int, ThreadCPUContext] = {}
        
        # Crisis Mode state
        self.crisis_mode_active = False
        self.crisis_mode_listeners: List[callable] = []
        self.crisis_mode_activated_at: Optional[float] = None  # Track when Crisis Mode was activated
        self.crisis_mode_deactivation_candidate_at: Optional[float] = None  # Track when conditions first met for deactivation
        
        # Request rate tracking (for DoS detection)
        self.request_timestamps: deque[float] = deque(maxlen=1000)
        
        # Thread pool for async database operations
        self._db_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="sentinel_db")
        
        # OPTIMIZATION: Cache psutil Process object to avoid repeated lookups
        self._process = psutil.Process()
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_metrics (
                tx_id TEXT PRIMARY KEY,
                timestamp REAL,
                cpu_time_ms REAL,
                memory_delta_mb REAL,
                z3_duration_ms REAL,
                anomaly_score REAL,
                layer_results TEXT,
                outcome TEXT,
                thread_cpu_ms REAL,
                cpu_violation INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON transaction_metrics(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_anomaly_score 
            ON transaction_metrics(anomaly_score)
        """)
        
        # Create crisis mode transitions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crisis_mode_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                transition_type TEXT,
                anomaly_rate REAL,
                request_rate INTEGER,
                triggering_condition TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crisis_timestamp 
            ON crisis_mode_transitions(timestamp)
        """)
        
        # Create CPU violations table (RVC-004)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cpu_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tx_id TEXT,
                timestamp REAL,
                thread_id INTEGER,
                cpu_time_ms REAL,
                threshold_ms REAL,
                excess_ms REAL
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cpu_violations_timestamp 
            ON cpu_violations(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def start_transaction(self, tx_id: str) -> None:
        """
        Record transaction start and capture initial resource state.
        
        This is the "before" snapshot - we capture:
        - Current timestamp
        - Current process CPU time
        - Current process memory usage
        - Thread CPU time (RVC-004)
        
        Args:
            tx_id: Unique transaction identifier
        """
        # OPTIMIZATION: Use cached process object
        cpu_times = self._process.cpu_times()
        memory_info = self._process.memory_info()
        
        # Capture initial state
        initial_state = {
            'start_time': time.time(),
            'cpu_time_start': cpu_times.user + cpu_times.system,
            'memory_start_mb': memory_info.rss / (1024 * 1024),
            'z3_start_time': None  # Will be set when Z3 starts
        }
        
        self.active_transactions[tx_id] = initial_state
        
        # Start thread CPU tracking (RVC-004)
        thread_id = threading.get_ident()
        cpu_context = self.thread_cpu_accounting.start_tracking(thread_id)
        self.active_threads[thread_id] = cpu_context
        
        # Track request rate for DoS detection
        self.request_timestamps.append(time.time())
    
    def end_transaction(self, tx_id: str, layer_results: Dict[str, bool]) -> TransactionMetrics:
        """
        Calculate metrics and update baseline.
        
        This is the "after" snapshot - we calculate:
        - CPU time delta
        - Memory delta
        - Z3 duration (if Z3 was used)
        - Anomaly score based on baseline
        - Thread CPU consumption (RVC-004)
        
        Args:
            tx_id: Unique transaction identifier
            layer_results: Dict mapping layer name to pass/fail boolean
        
        Returns:
            TransactionMetrics object with all calculated metrics
        """
        if tx_id not in self.active_transactions:
            raise ValueError(f"Transaction {tx_id} was not started")
        
        initial_state = self.active_transactions[tx_id]
        
        # OPTIMIZATION: Use cached process object
        cpu_times = self._process.cpu_times()
        memory_info = self._process.memory_info()
        
        # Calculate deltas
        end_time = time.time()
        cpu_time_end = cpu_times.user + cpu_times.system
        memory_end_mb = memory_info.rss / (1024 * 1024)
        
        cpu_time_ms = (cpu_time_end - initial_state['cpu_time_start']) * 1000
        memory_delta_mb = memory_end_mb - initial_state['memory_start_mb']
        
        # Z3 duration (if Z3 was used)
        z3_duration_ms = 0.0
        if initial_state.get('z3_start_time'):
            z3_duration_ms = (initial_state.get('z3_end_time', end_time) - 
                            initial_state['z3_start_time']) * 1000
        
        # Create metrics object
        metrics = TransactionMetrics(
            tx_id=tx_id,
            start_time=initial_state['start_time'],
            end_time=end_time,
            cpu_time_ms=cpu_time_ms,
            memory_delta_mb=memory_delta_mb,
            z3_duration_ms=z3_duration_ms,
            layer_results=layer_results
        )
        
        # Stop thread CPU tracking and check for violations (RVC-004)
        thread_id = threading.get_ident()
        if thread_id in self.active_threads:
            cpu_context = self.active_threads[thread_id]
            cpu_metrics = self.thread_cpu_accounting.stop_tracking(cpu_context)
            
            # Check for CPU violation
            violation = self.thread_cpu_accounting.check_violation(cpu_metrics)
            if violation:
                self._handle_cpu_violation(tx_id, violation)
            
            # Add CPU metrics to transaction metrics
            metrics.thread_cpu_ms = cpu_metrics.cpu_time_ms
            metrics.cpu_violation = violation is not None
            
            del self.active_threads[thread_id]
        
        # Calculate anomaly score
        metrics.anomaly_score = self.calculate_anomaly_score(metrics)
        
        # Add to rolling window
        self.metrics_window.append(metrics)
        
        # Update baseline (optimized to run every 10 transactions)
        self._update_baseline()
        
        # Persist to database (async)
        # OPTIMIZATION: Skip database writes in high-throughput scenarios
        # Database writes add significant overhead and should be batched
        if len(self.metrics_window) % 100 == 0:  # Only persist every 100th transaction
            self._persist_metrics(metrics)
        
        # OPTIMIZATION: Only check crisis conditions every 10 transactions
        if len(self.metrics_window) % 10 == 0:
            if self.check_crisis_conditions():
                if not self.crisis_mode_active:
                    self._activate_crisis_mode()
            else:
                if self.crisis_mode_active:
                    self._deactivate_crisis_mode()
        
        # Clean up
        del self.active_transactions[tx_id]
        
        return metrics

    def calculate_anomaly_score(self, metrics: TransactionMetrics) -> float:
        """
        Calculate anomaly score based on deviation from baseline.
        
        Uses z-score calculation for each metric:
            z = (observed - mean) / std_dev
        
        The anomaly score is the maximum z-score across all metrics,
        normalized to 0.0-1.0 range:
            anomaly_score = max(z_cpu, z_memory, z_z3) / 3.0
        
        If z > 3.0 (more than 3 standard deviations), anomaly_score > 1.0,
        which we clamp to 1.0.
        
        Args:
            metrics: TransactionMetrics object to score
        
        Returns:
            Anomaly score between 0.0 (normal) and 1.0 (extreme anomaly)
        """
        if len(self.metrics_window) < 10:
            # Not enough data for baseline, assume normal
            return 0.0
        
        # Calculate z-scores for each metric
        z_cpu = abs(metrics.cpu_time_ms - self.baseline.avg_cpu_ms) / self.baseline.std_dev_cpu
        z_memory = abs(metrics.memory_delta_mb - self.baseline.avg_memory_mb) / self.baseline.std_dev_memory
        z_z3 = abs(metrics.z3_duration_ms - self.baseline.avg_z3_ms) / self.baseline.std_dev_z3
        
        # Maximum z-score indicates most anomalous dimension
        max_z = max(z_cpu, z_memory, z_z3)
        
        # Normalize to 0.0-1.0 (z > 3.0 is considered anomalous)
        anomaly_score = min(max_z / 3.0, 1.0)
        
        return anomaly_score
    
    def _update_baseline(self) -> None:
        """
        Update baseline statistics from rolling window.
        
        Recalculates mean and standard deviation for:
        - CPU time
        - Memory delta
        - Z3 duration
        
        Uses Python's statistics module for numerical stability.
        
        OPTIMIZATION: Only recalculate every 10 transactions to reduce overhead.
        """
        # Only update baseline every 10 transactions to reduce overhead
        if len(self.metrics_window) < 2 or len(self.metrics_window) % 10 != 0:
            return
        
        # Extract metrics from window
        cpu_times = [m.cpu_time_ms for m in self.metrics_window]
        memory_deltas = [m.memory_delta_mb for m in self.metrics_window]
        z3_durations = [m.z3_duration_ms for m in self.metrics_window]
        
        # Calculate means
        self.baseline.avg_cpu_ms = statistics.mean(cpu_times)
        self.baseline.avg_memory_mb = statistics.mean(memory_deltas)
        self.baseline.avg_z3_ms = statistics.mean(z3_durations)
        
        # Calculate standard deviations (with minimum of 1.0 to avoid division by zero)
        self.baseline.std_dev_cpu = max(statistics.stdev(cpu_times), 1.0)
        self.baseline.std_dev_memory = max(statistics.stdev(memory_deltas), 1.0)
        self.baseline.std_dev_z3 = max(statistics.stdev(z3_durations), 1.0)
    
    def check_crisis_conditions(self) -> bool:
        """
        Detect if Crisis Mode should activate.
        
        Crisis Mode triggers when:
        1. Anomaly rate > 10% in last 60 seconds, OR
        2. Request rate > 1000 requests/second
        
        Returns:
            True if Crisis Mode should be active, False otherwise
        """
        current_time = time.time()
        
        # Check anomaly rate in last 60 seconds
        recent_metrics = [m for m in self.metrics_window 
                         if current_time - m.start_time <= 60]
        
        if len(recent_metrics) > 0:
            anomalous_count = sum(1 for m in recent_metrics if m.anomaly_score > 0.7)
            anomaly_rate = anomalous_count / len(recent_metrics)
            
            if anomaly_rate > 0.10:  # 10% threshold
                return True
        
        # Check request rate (requests per second)
        # If we have >= 1000 requests in the last second, that's >= 1000 req/s
        recent_requests = [ts for ts in self.request_timestamps 
                          if current_time - ts <= 1.0]
        
        if len(recent_requests) >= 1000:
            return True
        
        return False
    
    def _log_crisis_transition(self, transition_type: str, anomaly_rate: float, 
                              request_rate: int, condition: str) -> None:
        """
        Log Crisis Mode transition to database.
        
        Args:
            transition_type: "activation" or "deactivation"
            anomaly_rate: Current anomaly rate (0.0-1.0)
            request_rate: Current request rate (requests/second)
            condition: Description of triggering condition
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO crisis_mode_transitions 
                (timestamp, transition_type, anomaly_rate, request_rate, triggering_condition)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                transition_type,
                anomaly_rate,
                request_rate,
                condition
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SENTINEL] Error logging crisis transition: {e}")
    
    def _activate_crisis_mode(self) -> None:
        """
        Activate Crisis Mode and broadcast to listeners.
        
        Logs the transition and notifies all registered components
        (Adaptive Rigor, Quarantine System, etc.)
        """
        self.crisis_mode_active = True
        self.crisis_mode_activated_at = time.time()
        self.crisis_mode_deactivation_candidate_at = None  # Reset deactivation tracking
        
        # Log transition with triggering conditions
        current_time = time.time()
        recent_metrics = [m for m in self.metrics_window 
                         if current_time - m.start_time <= 60]
        
        anomaly_rate = 0.0
        if len(recent_metrics) > 0:
            anomalous_count = sum(1 for m in recent_metrics if m.anomaly_score > 0.7)
            anomaly_rate = anomalous_count / len(recent_metrics)
        
        recent_requests = [ts for ts in self.request_timestamps 
                          if current_time - ts <= 1.0]
        request_rate = len(recent_requests)
        
        print(f"[SENTINEL] 🚨 CRISIS MODE ACTIVATED")
        print(f"[SENTINEL]    Anomaly rate: {anomaly_rate:.1%} (threshold: 10%)")
        print(f"[SENTINEL]    Request rate: {request_rate}/s (threshold: 1000/s)")
        print(f"[SENTINEL]    Timestamp: {current_time}")
        
        # Log transition to database
        if anomaly_rate > 0.10:
            condition = f"Anomaly rate {anomaly_rate:.1%} exceeded 10% threshold"
        else:
            condition = f"Request rate {request_rate}/s exceeded 1000/s threshold"
        
        self._log_crisis_transition("activation", anomaly_rate, request_rate, condition)
        
        # Broadcast to listeners
        for listener in self.crisis_mode_listeners:
            try:
                listener(active=True)
            except Exception as e:
                print(f"[SENTINEL] Error notifying listener: {e}")
    
    def _deactivate_crisis_mode(self) -> None:
        """
        Deactivate Crisis Mode and broadcast to listeners.
        
        Only deactivates if anomaly rate has been < 2% for 120 consecutive seconds.
        This implements the cooldown period to prevent oscillation.
        """
        current_time = time.time()
        
        # Check if conditions for deactivation are met
        recent_metrics = [m for m in self.metrics_window 
                         if current_time - m.start_time <= 120]
        
        if len(recent_metrics) == 0:
            # No recent metrics, can't determine if safe to deactivate
            return
        
        anomalous_count = sum(1 for m in recent_metrics if m.anomaly_score > 0.7)
        anomaly_rate = anomalous_count / len(recent_metrics)
        
        if anomaly_rate >= 0.02:  # Still above 2% threshold
            # Conditions not met, reset deactivation tracking
            self.crisis_mode_deactivation_candidate_at = None
            return
        
        # Conditions are met (anomaly rate < 2%)
        # Track when conditions were first met
        if self.crisis_mode_deactivation_candidate_at is None:
            self.crisis_mode_deactivation_candidate_at = current_time
            print(f"[SENTINEL] 📊 Crisis Mode deactivation conditions met, starting 120s cooldown")
            return
        
        # Check if 120 seconds have elapsed since conditions were first met
        elapsed = current_time - self.crisis_mode_deactivation_candidate_at
        if elapsed < 120.0:
            # Still in cooldown period
            remaining = 120.0 - elapsed
            if int(remaining) % 30 == 0:  # Log every 30 seconds
                print(f"[SENTINEL] ⏳ Crisis Mode cooldown: {remaining:.0f}s remaining")
            return
        
        # Cooldown complete, deactivate Crisis Mode
        self.crisis_mode_active = False
        duration = current_time - self.crisis_mode_activated_at if self.crisis_mode_activated_at else 0
        
        # Calculate current request rate
        recent_requests = [ts for ts in self.request_timestamps 
                          if current_time - ts <= 1.0]
        request_rate = len(recent_requests)
        
        # Log transition
        print(f"[SENTINEL] ✅ CRISIS MODE DEACTIVATED")
        print(f"[SENTINEL]    Duration: {duration:.1f}s")
        print(f"[SENTINEL]    Final anomaly rate: {anomaly_rate:.1%}")
        print(f"[SENTINEL]    System stabilized")
        
        # Log transition to database
        condition = f"Anomaly rate {anomaly_rate:.1%} below 2% for 120 consecutive seconds"
        self._log_crisis_transition("deactivation", anomaly_rate, request_rate, condition)
        
        # Reset tracking
        self.crisis_mode_activated_at = None
        self.crisis_mode_deactivation_candidate_at = None
        
        # Broadcast to listeners
        for listener in self.crisis_mode_listeners:
            try:
                listener(active=False)
            except Exception as e:
                print(f"[SENTINEL] Error notifying listener: {e}")
    
    def _handle_cpu_violation(self, tx_id: str, violation: CPUViolation) -> None:
        """
        Handle CPU threshold violation (RVC-004).
        
        This method is called when a thread exceeds the CPU threshold,
        indicating a potential sub-millisecond attack. It:
        1. Logs the violation details
        2. Triggers Crisis Mode if not already active
        3. Persists violation to database for audit
        
        Args:
            tx_id: Transaction ID
            violation: CPUViolation details
        """
        print(f"[SENTINEL] 🚨 CPU VIOLATION DETECTED")
        print(f"[SENTINEL]    TX: {tx_id}")
        print(f"[SENTINEL]    Thread: {violation.thread_id}")
        print(f"[SENTINEL]    CPU Time: {violation.cpu_time_ms:.2f}ms")
        print(f"[SENTINEL]    Threshold: {violation.threshold_ms:.2f}ms")
        print(f"[SENTINEL]    Excess: {violation.excess_ms:.2f}ms")
        
        # Trigger immediate response
        if not self.crisis_mode_active:
            self._activate_crisis_mode()
        
        # Log violation to database
        self._log_cpu_violation(tx_id, violation)
    
    def _log_cpu_violation(self, tx_id: str, violation: CPUViolation) -> None:
        """
        Log CPU violation to database (RVC-004).
        
        Args:
            tx_id: Transaction ID
            violation: CPUViolation details
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO cpu_violations 
                (tx_id, timestamp, thread_id, cpu_time_ms, threshold_ms, excess_ms)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tx_id,
                violation.timestamp,
                violation.thread_id,
                violation.cpu_time_ms,
                violation.threshold_ms,
                violation.excess_ms
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SENTINEL] Error logging CPU violation: {e}")
    
    def register_crisis_listener(self, callback: callable) -> None:
        """
        Register a callback for Crisis Mode state changes.
        
        Args:
            callback: Function that accepts (active: bool) parameter
        """
        self.crisis_mode_listeners.append(callback)
    
    def get_statistics(self, time_window_seconds: int = 3600) -> Dict[str, Any]:
        """
        Return aggregated statistics for monitoring.
        
        Args:
            time_window_seconds: Time window for statistics (default: 1 hour)
        
        Returns:
            Dictionary with telemetry statistics in JSON-serializable format
        """
        current_time = time.time()
        cutoff_time = current_time - time_window_seconds
        
        # Filter metrics to time window
        recent_metrics = [m for m in self.metrics_window if m.start_time >= cutoff_time]
        
        if not recent_metrics:
            return {
                'time_window_seconds': time_window_seconds,
                'transaction_count': 0,
                'baseline': self.baseline.to_dict(),
                'crisis_mode_active': self.crisis_mode_active
            }
        
        # Calculate statistics
        anomalous_count = sum(1 for m in recent_metrics if m.anomaly_score > 0.7)
        failed_count = sum(1 for m in recent_metrics 
                          if not all(m.layer_results.values()))
        
        return {
            'time_window_seconds': time_window_seconds,
            'transaction_count': len(recent_metrics),
            'anomaly_rate': anomalous_count / len(recent_metrics),
            'failure_rate': failed_count / len(recent_metrics),
            'avg_cpu_ms': statistics.mean(m.cpu_time_ms for m in recent_metrics),
            'avg_memory_mb': statistics.mean(m.memory_delta_mb for m in recent_metrics),
            'avg_z3_ms': statistics.mean(m.z3_duration_ms for m in recent_metrics),
            'baseline': self.baseline.to_dict(),
            'crisis_mode_active': self.crisis_mode_active,
            'request_rate_per_second': len([ts for ts in self.request_timestamps 
                                           if current_time - ts <= 1.0])
        }
    
    def _persist_metrics(self, metrics: TransactionMetrics) -> None:
        """
        Persist metrics to SQLite database asynchronously.
        
        Uses ThreadPoolExecutor to avoid blocking the main thread.
        Database writes happen in background threads.
        
        Args:
            metrics: TransactionMetrics to persist
        """
        # Submit to thread pool for async execution
        self._db_executor.submit(self._persist_metrics_sync, metrics)
    
    def _persist_metrics_sync(self, metrics: TransactionMetrics) -> None:
        """
        Synchronous database write (called by thread pool).
        
        Args:
            metrics: TransactionMetrics to persist
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Determine outcome
            outcome = "accepted" if all(metrics.layer_results.values()) else "rejected"
            
            cursor.execute("""
                INSERT OR REPLACE INTO transaction_metrics 
                (tx_id, timestamp, cpu_time_ms, memory_delta_mb, z3_duration_ms, 
                 anomaly_score, layer_results, outcome, thread_cpu_ms, cpu_violation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.tx_id,
                metrics.start_time,
                metrics.cpu_time_ms,
                metrics.memory_delta_mb,
                metrics.z3_duration_ms,
                metrics.anomaly_score,
                json.dumps(metrics.layer_results),
                outcome,
                metrics.thread_cpu_ms,
                1 if metrics.cpu_violation else 0
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[SENTINEL] Error persisting metrics: {e}")
    
    def shutdown(self) -> None:
        """
        Shutdown the Sentinel Monitor gracefully.
        
        Waits for all pending database writes to complete.
        """
        self._db_executor.shutdown(wait=True)


# Singleton instance
_sentinel_monitor: Optional[SentinelMonitor] = None


def get_sentinel_monitor() -> SentinelMonitor:
    """
    Get the singleton Sentinel Monitor instance.
    
    Returns:
        SentinelMonitor singleton
    """
    global _sentinel_monitor
    if _sentinel_monitor is None:
        _sentinel_monitor = SentinelMonitor()
    return _sentinel_monitor
