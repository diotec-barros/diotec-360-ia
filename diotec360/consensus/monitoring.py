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
Monitoring and Observability for Proof-of-Proof consensus protocol.

This module implements comprehensive monitoring and metrics collection for the
consensus protocol. It provides:
- Consensus metrics (duration, participants, proof count)
- Mempool metrics (size, processing rate)
- Verification accuracy tracking
- Reward tracking
- Byzantine behavior logging

All metrics are Prometheus-compatible and can be exposed via HTTP endpoint.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime


@dataclass
class ConsensusMetrics:
    """Metrics for a single consensus round."""
    round_id: str
    duration: float  # seconds
    participants: List[str]
    proof_count: int
    total_difficulty: int
    timestamp: float
    view: int
    sequence: int
    success: bool


@dataclass
class MempoolMetrics:
    """Real-time mempool metrics."""
    size: int
    max_size: int
    utilization: float
    total_added: int
    total_removed: int
    total_rejected: int
    processing_rate: float  # proofs per second
    timestamp: float


@dataclass
class VerificationAccuracy:
    """Verification accuracy for a node over a sliding window."""
    node_id: str
    total_verifications: int
    correct_verifications: int
    accuracy: float  # percentage
    window_size: int
    timestamp: float


@dataclass
class RewardRecord:
    """Record of rewards earned by a node."""
    node_id: str
    round_id: str
    reward_amount: int
    difficulty: int
    timestamp: float


@dataclass
class ByzantineIncident:
    """Record of detected Byzantine behavior."""
    incident_id: str
    node_id: str
    violation_type: str
    evidence: Dict[str, Any]
    timestamp: float
    slashing_amount: int


class MetricsCollector:
    """
    Collects and stores metrics for the consensus protocol.
    
    This class provides thread-safe metrics collection with:
    - Consensus round metrics
    - Mempool metrics
    - Verification accuracy tracking
    - Reward tracking
    - Byzantine behavior logging
    
    All metrics are stored in memory with configurable retention periods.
    """
    
    def __init__(
        self,
        max_consensus_history: int = 1000,
        max_reward_history: int = 10000,
        max_incident_history: int = 1000,
        accuracy_window_size: int = 100,
    ):
        """
        Initialize MetricsCollector.
        
        Args:
            max_consensus_history: Maximum consensus rounds to store
            max_reward_history: Maximum reward records to store
            max_incident_history: Maximum Byzantine incidents to store
            accuracy_window_size: Window size for accuracy calculation
        """
        self.max_consensus_history = max_consensus_history
        self.max_reward_history = max_reward_history
        self.max_incident_history = max_incident_history
        self.accuracy_window_size = accuracy_window_size
        
        # Consensus metrics
        self.consensus_history: deque = deque(maxlen=max_consensus_history)
        self.consensus_count = 0
        self.consensus_success_count = 0
        self.consensus_failure_count = 0
        
        # Mempool metrics
        self.current_mempool_metrics: Optional[MempoolMetrics] = None
        self.mempool_history: deque = deque(maxlen=100)
        
        # Verification accuracy tracking
        self.verification_records: Dict[str, deque] = {}  # node_id -> deque of (correct: bool)
        self.accuracy_alerts: List[Dict[str, Any]] = []
        
        # Reward tracking
        self.reward_history: deque = deque(maxlen=max_reward_history)
        self.cumulative_rewards: Dict[str, int] = {}  # node_id -> total rewards
        
        # Byzantine behavior logging
        self.incident_history: deque = deque(maxlen=max_incident_history)
        self.incident_count = 0
        
        # Thread safety
        self._lock = threading.Lock()
    
    def record_consensus_round(
        self,
        round_id: str,
        duration: float,
        participants: List[str],
        proof_count: int,
        total_difficulty: int,
        view: int,
        sequence: int,
        success: bool = True,
    ) -> None:
        """
        Record metrics for a completed consensus round.
        
        This method implements Property 32: Consensus Metrics Emission.
        
        Args:
            round_id: Unique identifier for this round
            duration: Time taken to reach consensus (seconds)
            participants: List of participating node IDs
            proof_count: Number of proofs in the block
            total_difficulty: Total difficulty of all proofs
            view: View number
            sequence: Sequence number
            success: Whether consensus was successful
        """
        with self._lock:
            metrics = ConsensusMetrics(
                round_id=round_id,
                duration=duration,
                participants=participants,
                proof_count=proof_count,
                total_difficulty=total_difficulty,
                timestamp=time.time(),
                view=view,
                sequence=sequence,
                success=success,
            )
            
            self.consensus_history.append(metrics)
            self.consensus_count += 1
            
            if success:
                self.consensus_success_count += 1
            else:
                self.consensus_failure_count += 1
    
    def update_mempool_metrics(
        self,
        size: int,
        max_size: int,
        total_added: int,
        total_removed: int,
        total_rejected: int,
    ) -> None:
        """
        Update real-time mempool metrics.
        
        This method implements Property 33: Real-Time Mempool Metrics.
        
        Args:
            size: Current number of proofs in mempool
            max_size: Maximum mempool capacity
            total_added: Total proofs added since start
            total_removed: Total proofs removed since start
            total_rejected: Total proofs rejected since start
        """
        with self._lock:
            # Calculate processing rate
            processing_rate = 0.0
            if self.current_mempool_metrics:
                time_delta = time.time() - self.current_mempool_metrics.timestamp
                if time_delta > 0:
                    removed_delta = total_removed - self.current_mempool_metrics.total_removed
                    processing_rate = removed_delta / time_delta
            
            metrics = MempoolMetrics(
                size=size,
                max_size=max_size,
                utilization=size / max_size if max_size > 0 else 0.0,
                total_added=total_added,
                total_removed=total_removed,
                total_rejected=total_rejected,
                processing_rate=processing_rate,
                timestamp=time.time(),
            )
            
            self.current_mempool_metrics = metrics
            self.mempool_history.append(metrics)
    
    def record_verification(self, node_id: str, correct: bool) -> None:
        """
        Record a verification attempt by a node.
        
        This method tracks verification accuracy over a sliding window
        and implements Property 34: Low Accuracy Alerting.
        
        Args:
            node_id: ID of the node that performed verification
            correct: Whether the verification was correct
        """
        with self._lock:
            # Initialize deque for this node if needed
            if node_id not in self.verification_records:
                self.verification_records[node_id] = deque(maxlen=self.accuracy_window_size)
            
            # Record verification
            self.verification_records[node_id].append(correct)
            
            # Check accuracy and trigger alert if below threshold
            accuracy = self.get_verification_accuracy(node_id)
            if accuracy and accuracy.accuracy < 95.0:
                self._trigger_accuracy_alert(node_id, accuracy)
    
    def get_verification_accuracy(self, node_id: str) -> Optional[VerificationAccuracy]:
        """
        Get verification accuracy for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            VerificationAccuracy or None if no data
        """
        with self._lock:
            if node_id not in self.verification_records:
                return None
            
            records = self.verification_records[node_id]
            if not records:
                return None
            
            total = len(records)
            correct = sum(1 for r in records if r)
            accuracy = (correct / total * 100) if total > 0 else 0.0
            
            return VerificationAccuracy(
                node_id=node_id,
                total_verifications=total,
                correct_verifications=correct,
                accuracy=accuracy,
                window_size=self.accuracy_window_size,
                timestamp=time.time(),
            )
    
    def _trigger_accuracy_alert(self, node_id: str, accuracy: VerificationAccuracy) -> None:
        """
        Trigger an alert when node accuracy drops below 95%.
        
        This implements Property 34: Low Accuracy Alerting.
        
        Args:
            node_id: ID of the node with low accuracy
            accuracy: Current accuracy metrics
        """
        alert = {
            'type': 'low_accuracy',
            'node_id': node_id,
            'accuracy': accuracy.accuracy,
            'threshold': 95.0,
            'total_verifications': accuracy.total_verifications,
            'correct_verifications': accuracy.correct_verifications,
            'timestamp': time.time(),
            'message': f"Node {node_id} accuracy dropped to {accuracy.accuracy:.2f}% (threshold: 95%)"
        }
        
        self.accuracy_alerts.append(alert)
    
    def record_reward(
        self,
        node_id: str,
        round_id: str,
        reward_amount: int,
        difficulty: int,
    ) -> None:
        """
        Record reward earned by a node.
        
        This method implements Property 35: Reward Tracking Accuracy.
        
        Args:
            node_id: ID of the node that earned reward
            round_id: ID of the consensus round
            reward_amount: Amount of reward earned
            difficulty: Difficulty of the proofs verified
        """
        with self._lock:
            record = RewardRecord(
                node_id=node_id,
                round_id=round_id,
                reward_amount=reward_amount,
                difficulty=difficulty,
                timestamp=time.time(),
            )
            
            self.reward_history.append(record)
            
            # Update cumulative rewards
            if node_id not in self.cumulative_rewards:
                self.cumulative_rewards[node_id] = 0
            self.cumulative_rewards[node_id] += reward_amount
    
    def get_cumulative_rewards(self, node_id: str) -> int:
        """
        Get cumulative rewards for a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Total rewards earned
        """
        with self._lock:
            return self.cumulative_rewards.get(node_id, 0)
    
    def record_byzantine_incident(
        self,
        node_id: str,
        violation_type: str,
        evidence: Dict[str, Any],
        slashing_amount: int = 0,
    ) -> str:
        """
        Record detected Byzantine behavior.
        
        This method implements Property 36: Byzantine Behavior Logging.
        
        Args:
            node_id: ID of the Byzantine node
            violation_type: Type of violation (e.g., "invalid_verification", "double_sign")
            evidence: Cryptographic evidence of the violation
            slashing_amount: Amount of stake slashed
            
        Returns:
            Incident ID
        """
        with self._lock:
            incident_id = f"incident_{self.incident_count}_{int(time.time())}"
            
            incident = ByzantineIncident(
                incident_id=incident_id,
                node_id=node_id,
                violation_type=violation_type,
                evidence=evidence,
                timestamp=time.time(),
                slashing_amount=slashing_amount,
            )
            
            self.incident_history.append(incident)
            self.incident_count += 1
            
            return incident_id
    
    def get_consensus_metrics(self, limit: int = 100) -> List[ConsensusMetrics]:
        """
        Get recent consensus metrics.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of ConsensusMetrics
        """
        with self._lock:
            return list(self.consensus_history)[-limit:]
    
    def get_mempool_metrics(self) -> Optional[MempoolMetrics]:
        """
        Get current mempool metrics.
        
        Returns:
            Current MempoolMetrics or None
        """
        with self._lock:
            return self.current_mempool_metrics
    
    def get_reward_history(self, node_id: Optional[str] = None, limit: int = 100) -> List[RewardRecord]:
        """
        Get reward history.
        
        Args:
            node_id: Filter by node ID (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of RewardRecord
        """
        with self._lock:
            if node_id:
                records = [r for r in self.reward_history if r.node_id == node_id]
            else:
                records = list(self.reward_history)
            
            return records[-limit:]
    
    def get_byzantine_incidents(self, node_id: Optional[str] = None, limit: int = 100) -> List[ByzantineIncident]:
        """
        Get Byzantine incident history.
        
        Args:
            node_id: Filter by node ID (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of ByzantineIncident
        """
        with self._lock:
            if node_id:
                incidents = [i for i in self.incident_history if i.node_id == node_id]
            else:
                incidents = list(self.incident_history)
            
            return incidents[-limit:]
    
    def get_accuracy_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get accuracy alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        with self._lock:
            return self.accuracy_alerts[-limit:]
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for all metrics.
        
        Returns:
            Dictionary with summary statistics
        """
        with self._lock:
            # Calculate average consensus duration
            avg_duration = 0.0
            if self.consensus_history:
                avg_duration = sum(m.duration for m in self.consensus_history) / len(self.consensus_history)
            
            # Calculate success rate
            success_rate = 0.0
            if self.consensus_count > 0:
                success_rate = (self.consensus_success_count / self.consensus_count) * 100
            
            return {
                'consensus': {
                    'total_rounds': self.consensus_count,
                    'successful_rounds': self.consensus_success_count,
                    'failed_rounds': self.consensus_failure_count,
                    'success_rate': success_rate,
                    'average_duration': avg_duration,
                },
                'mempool': {
                    'current_size': self.current_mempool_metrics.size if self.current_mempool_metrics else 0,
                    'utilization': self.current_mempool_metrics.utilization if self.current_mempool_metrics else 0.0,
                    'processing_rate': self.current_mempool_metrics.processing_rate if self.current_mempool_metrics else 0.0,
                },
                'rewards': {
                    'total_records': len(self.reward_history),
                    'total_nodes': len(self.cumulative_rewards),
                    'total_rewards_distributed': sum(self.cumulative_rewards.values()),
                },
                'byzantine': {
                    'total_incidents': self.incident_count,
                    'recent_incidents': len(self.incident_history),
                },
                'accuracy': {
                    'nodes_tracked': len(self.verification_records),
                    'alerts_triggered': len(self.accuracy_alerts),
                },
            }
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus format.
        
        Returns:
            Prometheus-formatted metrics string
        """
        with self._lock:
            lines = []
            
            # Consensus metrics
            lines.append("# HELP consensus_rounds_total Total number of consensus rounds")
            lines.append("# TYPE consensus_rounds_total counter")
            lines.append(f"consensus_rounds_total {self.consensus_count}")
            
            lines.append("# HELP consensus_success_total Total number of successful consensus rounds")
            lines.append("# TYPE consensus_success_total counter")
            lines.append(f"consensus_success_total {self.consensus_success_count}")
            
            lines.append("# HELP consensus_failure_total Total number of failed consensus rounds")
            lines.append("# TYPE consensus_failure_total counter")
            lines.append(f"consensus_failure_total {self.consensus_failure_count}")
            
            # Average duration
            if self.consensus_history:
                avg_duration = sum(m.duration for m in self.consensus_history) / len(self.consensus_history)
                lines.append("# HELP consensus_duration_seconds Average consensus duration")
                lines.append("# TYPE consensus_duration_seconds gauge")
                lines.append(f"consensus_duration_seconds {avg_duration:.6f}")
            
            # Mempool metrics
            if self.current_mempool_metrics:
                lines.append("# HELP mempool_size Current number of proofs in mempool")
                lines.append("# TYPE mempool_size gauge")
                lines.append(f"mempool_size {self.current_mempool_metrics.size}")
                
                lines.append("# HELP mempool_utilization Mempool utilization (0-1)")
                lines.append("# TYPE mempool_utilization gauge")
                lines.append(f"mempool_utilization {self.current_mempool_metrics.utilization:.6f}")
                
                lines.append("# HELP mempool_processing_rate Proof processing rate (proofs/second)")
                lines.append("# TYPE mempool_processing_rate gauge")
                lines.append(f"mempool_processing_rate {self.current_mempool_metrics.processing_rate:.6f}")
            
            # Reward metrics
            lines.append("# HELP rewards_distributed_total Total rewards distributed")
            lines.append("# TYPE rewards_distributed_total counter")
            lines.append(f"rewards_distributed_total {sum(self.cumulative_rewards.values())}")
            
            # Byzantine incidents
            lines.append("# HELP byzantine_incidents_total Total Byzantine incidents detected")
            lines.append("# TYPE byzantine_incidents_total counter")
            lines.append(f"byzantine_incidents_total {self.incident_count}")
            
            # Accuracy alerts
            lines.append("# HELP accuracy_alerts_total Total accuracy alerts triggered")
            lines.append("# TYPE accuracy_alerts_total counter")
            lines.append(f"accuracy_alerts_total {len(self.accuracy_alerts)}")
            
            return "\n".join(lines)
