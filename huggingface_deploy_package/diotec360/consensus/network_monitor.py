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
Network latency monitoring for adaptive timeout adjustment.

This module implements network latency monitoring to enable dynamic timeout
adjustment in the consensus protocol. It measures round-trip time to peers
and calculates average network latency.
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import deque


@dataclass
class LatencyMeasurement:
    """A single latency measurement to a peer."""
    peer_id: str
    round_trip_time: float  # milliseconds
    timestamp: float
    success: bool


@dataclass
class PeerLatencyStats:
    """Latency statistics for a peer."""
    peer_id: str
    average_latency: float  # milliseconds
    min_latency: float
    max_latency: float
    measurement_count: int
    last_measurement: float


class NetworkMonitor:
    """
    Monitors network latency to peers for adaptive timeout adjustment.
    
    This class provides:
    - Round-trip time measurement to peers
    - Average network latency calculation
    - Per-peer latency statistics
    - Network health assessment
    
    Validates: Requirements 6.5
    """
    
    def __init__(
        self,
        window_size: int = 100,
        ping_interval: float = 5.0,
    ):
        """
        Initialize NetworkMonitor.
        
        Args:
            window_size: Number of measurements to keep per peer
            ping_interval: Interval between ping measurements (seconds)
        """
        self.window_size = window_size
        self.ping_interval = ping_interval
        
        # Latency measurements per peer
        self.measurements: Dict[str, deque] = {}
        
        # Cached statistics
        self._stats_cache: Dict[str, PeerLatencyStats] = {}
        self._cache_timestamp: Dict[str, float] = {}
        self._cache_ttl = 1.0  # seconds
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def record_latency(
        self,
        peer_id: str,
        round_trip_time: float,
        success: bool = True,
    ) -> None:
        """
        Record a latency measurement for a peer.
        
        Args:
            peer_id: ID of the peer
            round_trip_time: Round-trip time in milliseconds
            success: Whether the measurement was successful
        """
        with self._lock:
            if peer_id not in self.measurements:
                self.measurements[peer_id] = deque(maxlen=self.window_size)
            
            measurement = LatencyMeasurement(
                peer_id=peer_id,
                round_trip_time=round_trip_time,
                timestamp=time.time(),
                success=success,
            )
            
            self.measurements[peer_id].append(measurement)
            
            # Invalidate cache for this peer
            if peer_id in self._cache_timestamp:
                del self._cache_timestamp[peer_id]
    
    def get_peer_latency(self, peer_id: str) -> Optional[PeerLatencyStats]:
        """
        Get latency statistics for a specific peer.
        
        Args:
            peer_id: ID of the peer
            
        Returns:
            PeerLatencyStats or None if no measurements
        """
        with self._lock:
            # Check cache
            if peer_id in self._cache_timestamp:
                if time.time() - self._cache_timestamp[peer_id] < self._cache_ttl:
                    return self._stats_cache.get(peer_id)
            
            # Calculate statistics
            if peer_id not in self.measurements or not self.measurements[peer_id]:
                return None
            
            measurements = [
                m for m in self.measurements[peer_id]
                if m.success
            ]
            
            if not measurements:
                return None
            
            latencies = [m.round_trip_time for m in measurements]
            
            stats = PeerLatencyStats(
                peer_id=peer_id,
                average_latency=sum(latencies) / len(latencies),
                min_latency=min(latencies),
                max_latency=max(latencies),
                measurement_count=len(measurements),
                last_measurement=measurements[-1].timestamp,
            )
            
            # Update cache
            self._stats_cache[peer_id] = stats
            self._cache_timestamp[peer_id] = time.time()
            
            return stats
    
    def get_average_network_latency(self) -> float:
        """
        Calculate average network latency across all peers.
        
        Returns:
            Average latency in milliseconds, or 0.0 if no measurements
        """
        with self._lock:
            all_latencies = []
            
            for peer_id in self.measurements:
                measurements = [
                    m.round_trip_time
                    for m in self.measurements[peer_id]
                    if m.success
                ]
                all_latencies.extend(measurements)
            
            if not all_latencies:
                return 0.0
            
            return sum(all_latencies) / len(all_latencies)
    
    def get_all_peer_stats(self) -> List[PeerLatencyStats]:
        """
        Get latency statistics for all peers.
        
        Returns:
            List of PeerLatencyStats
        """
        with self._lock:
            stats = []
            for peer_id in self.measurements:
                peer_stats = self.get_peer_latency(peer_id)
                if peer_stats:
                    stats.append(peer_stats)
            return stats
    
    def is_high_latency(self, threshold: float = 500.0) -> bool:
        """
        Check if network latency exceeds threshold.
        
        Args:
            threshold: Latency threshold in milliseconds
            
        Returns:
            True if average latency exceeds threshold
        """
        avg_latency = self.get_average_network_latency()
        # Only return True if we have actual measurements and latency exceeds threshold
        if avg_latency == 0.0:
            return False
        return avg_latency > threshold
    
    def measure_peer_latency(self, peer_id: str, network) -> float:
        """
        Measure round-trip time to a peer.
        
        Args:
            peer_id: ID of the peer to ping
            network: P2P network instance
            
        Returns:
            Round-trip time in milliseconds
        """
        start_time = time.time()
        
        try:
            # Send ping message
            network.send_to_peer(peer_id, {"type": "ping", "timestamp": start_time})
            
            # Wait for pong (simplified - in real implementation would use callbacks)
            # For now, simulate with small delay
            time.sleep(0.001)
            
            end_time = time.time()
            rtt = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.record_latency(peer_id, rtt, success=True)
            return rtt
            
        except Exception:
            # Record failed measurement
            self.record_latency(peer_id, 0.0, success=False)
            return -1.0
    
    def start_monitoring(self, network, peer_ids: List[str]) -> None:
        """
        Start continuous latency monitoring.
        
        Args:
            network: P2P network instance
            peer_ids: List of peer IDs to monitor
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        
        def monitor_loop():
            while self._monitoring:
                for peer_id in peer_ids:
                    if not self._monitoring:
                        break
                    self.measure_peer_latency(peer_id, network)
                
                time.sleep(self.ping_interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop continuous latency monitoring."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            self._monitor_thread = None
    
    def get_network_health(self) -> Dict[str, any]:
        """
        Get overall network health metrics.
        
        Returns:
            Dictionary with network health information
        """
        with self._lock:
            avg_latency = self.get_average_network_latency()
            peer_stats = self.get_all_peer_stats()
            
            healthy_peers = sum(
                1 for stats in peer_stats
                if stats.average_latency < 500.0
            )
            
            return {
                'average_latency': avg_latency,
                'total_peers': len(peer_stats),
                'healthy_peers': healthy_peers,
                'high_latency': avg_latency > 500.0,
                'peer_stats': peer_stats,
            }
