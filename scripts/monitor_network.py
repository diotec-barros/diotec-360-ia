#!/usr/bin/env python3
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
Real-time monitoring dashboard for Proof-of-Proof consensus network.

This script provides a live dashboard showing:
- Network health visualization
- Consensus latency graphs
- Proof throughput metrics
- Validator performance leaderboard

Usage:
    python scripts/monitor_network.py --nodes node_1,node_2,node_3,node_4
"""

import argparse
import time
import sys
from typing import List, Dict
from collections import deque
from datetime import datetime

from diotec360.consensus.monitoring import MetricsCollector


class NetworkMonitor:
    """
    Real-time network monitoring dashboard.
    
    Displays:
    - Network health (active nodes, consensus status)
    - Consensus latency (average, min, max)
    - Proof throughput (proofs/second)
    - Validator performance leaderboard
    """
    
    def __init__(self, node_ids: List[str]):
        """
        Initialize network monitor.
        
        Args:
            node_ids: List of node IDs to monitor
        """
        self.node_ids = node_ids
        self.metrics_collectors: Dict[str, MetricsCollector] = {}
        
        # Initialize metrics collectors for each node
        for node_id in node_ids:
            self.metrics_collectors[node_id] = MetricsCollector()
        
        # Historical data for graphs (last 60 data points)
        self.latency_history = deque(maxlen=60)
        self.throughput_history = deque(maxlen=60)
        
        # Performance tracking
        self.last_update_time = time.time()
        self.total_proofs_processed = 0
    
    def clear_screen(self):
        """Clear terminal screen."""
        print("\033[2J\033[H", end="")
    
    def render_header(self):
        """Render dashboard header."""
        print("=" * 80)
        print(" " * 20 + "PROOF-OF-PROOF CONSENSUS NETWORK MONITOR")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Monitoring {len(self.node_ids)} nodes")
        print("=" * 80)
        print()
    
    def render_network_health(self):
        """Render network health section."""
        print("📊 NETWORK HEALTH")
        print("-" * 80)
        
        # Count active nodes (nodes with recent consensus activity)
        active_nodes = 0
        total_consensus_rounds = 0
        
        for node_id, metrics in self.metrics_collectors.items():
            if metrics.consensus_rounds:
                active_nodes += 1
                total_consensus_rounds += len(metrics.consensus_rounds)
        
        # Calculate network status
        if active_nodes == len(self.node_ids):
            status = "🟢 HEALTHY"
        elif active_nodes >= len(self.node_ids) * 0.67:
            status = "🟡 DEGRADED"
        else:
            status = "🔴 CRITICAL"
        
        print(f"  Status: {status}")
        print(f"  Active Nodes: {active_nodes}/{len(self.node_ids)}")
        print(f"  Total Consensus Rounds: {total_consensus_rounds}")
        print(f"  Byzantine Fault Tolerance: {self._calculate_bft_threshold()}")
        print()
    
    def _calculate_bft_threshold(self) -> str:
        """Calculate Byzantine fault tolerance threshold."""
        n = len(self.node_ids)
        f = (n - 1) // 3
        return f"Can tolerate {f} faulty nodes (33% of {n})"
    
    def render_consensus_latency(self):
        """Render consensus latency metrics."""
        print("⏱️  CONSENSUS LATENCY")
        print("-" * 80)
        
        # Collect latency data from all nodes
        all_durations = []
        for metrics in self.metrics_collectors.values():
            for round_data in metrics.consensus_rounds.values():
                all_durations.append(round_data["duration"])
        
        if all_durations:
            avg_latency = sum(all_durations) / len(all_durations)
            min_latency = min(all_durations)
            max_latency = max(all_durations)
            
            print(f"  Average: {avg_latency:.3f}s")
            print(f"  Minimum: {min_latency:.3f}s")
            print(f"  Maximum: {max_latency:.3f}s")
            
            # Add to history for graph
            self.latency_history.append(avg_latency)
            
            # Render simple ASCII graph
            self._render_latency_graph()
        else:
            print("  No consensus data available")
        
        print()
    
    def _render_latency_graph(self):
        """Render ASCII graph of latency over time."""
        if len(self.latency_history) < 2:
            return
        
        print("\n  Latency Graph (last 60 measurements):")
        
        # Normalize data to fit in 10 rows
        max_val = max(self.latency_history)
        min_val = min(self.latency_history)
        range_val = max_val - min_val if max_val > min_val else 1
        
        # Render 10 rows
        for row in range(10, 0, -1):
            threshold = min_val + (range_val * row / 10)
            line = f"  {threshold:6.2f}s |"
            
            for val in self.latency_history:
                if val >= threshold:
                    line += "█"
                else:
                    line += " "
            
            print(line)
        
        print("         +" + "-" * len(self.latency_history))
        print(f"          {len(self.latency_history)} measurements")
    
    def render_proof_throughput(self):
        """Render proof throughput metrics."""
        print("📈 PROOF THROUGHPUT")
        print("-" * 80)
        
        # Calculate throughput
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        
        # Count total proofs processed
        total_proofs = 0
        for metrics in self.metrics_collectors.values():
            for round_data in metrics.consensus_rounds.values():
                total_proofs += round_data["proof_count"]
        
        # Calculate proofs per second
        new_proofs = total_proofs - self.total_proofs_processed
        if time_elapsed > 0:
            throughput = new_proofs / time_elapsed
        else:
            throughput = 0
        
        self.total_proofs_processed = total_proofs
        self.last_update_time = current_time
        
        print(f"  Total Proofs Processed: {total_proofs}")
        print(f"  Current Throughput: {throughput:.2f} proofs/second")
        
        # Add to history
        self.throughput_history.append(throughput)
        
        # Calculate average throughput
        if self.throughput_history:
            avg_throughput = sum(self.throughput_history) / len(self.throughput_history)
            print(f"  Average Throughput: {avg_throughput:.2f} proofs/second")
        
        print()
    
    def render_validator_leaderboard(self):
        """Render validator performance leaderboard."""
        print("🏆 VALIDATOR PERFORMANCE LEADERBOARD")
        print("-" * 80)
        
        # Collect performance data for each validator
        validator_stats = []
        
        for node_id, metrics in self.metrics_collectors.items():
            # Count consensus rounds participated in
            rounds_participated = len(metrics.consensus_rounds)
            
            # Calculate verification accuracy
            if node_id in metrics.verification_accuracy:
                accuracy_data = metrics.verification_accuracy[node_id]
                if accuracy_data:
                    correct = sum(1 for result in accuracy_data if result)
                    accuracy = (correct / len(accuracy_data)) * 100
                else:
                    accuracy = 0.0
            else:
                accuracy = 0.0
            
            # Calculate total rewards (if tracked)
            total_rewards = metrics.node_rewards.get(node_id, 0)
            
            validator_stats.append({
                "node_id": node_id,
                "rounds": rounds_participated,
                "accuracy": accuracy,
                "rewards": total_rewards,
            })
        
        # Sort by rounds participated (descending)
        validator_stats.sort(key=lambda x: x["rounds"], reverse=True)
        
        # Render table
        print(f"  {'Rank':<6} {'Node ID':<15} {'Rounds':<10} {'Accuracy':<12} {'Rewards':<10}")
        print("  " + "-" * 76)
        
        for rank, stats in enumerate(validator_stats, 1):
            # Add medal emoji for top 3
            if rank == 1:
                rank_str = "🥇 1"
            elif rank == 2:
                rank_str = "🥈 2"
            elif rank == 3:
                rank_str = "🥉 3"
            else:
                rank_str = f"   {rank}"
            
            print(f"  {rank_str:<6} {stats['node_id']:<15} {stats['rounds']:<10} "
                  f"{stats['accuracy']:>6.1f}%     {stats['rewards']:<10.2f}")
        
        print()
    
    def render_mempool_status(self):
        """Render mempool status."""
        print("💾 MEMPOOL STATUS")
        print("-" * 80)
        
        # In a real implementation, this would query actual mempool
        # For now, we show placeholder data
        print("  Pending Proofs: N/A (requires live connection)")
        print("  Processing Rate: N/A (requires live connection)")
        print()
    
    def render_footer(self):
        """Render dashboard footer."""
        print("=" * 80)
        print("Press Ctrl+C to exit")
        print("=" * 80)
    
    def update(self):
        """Update dashboard with latest metrics."""
        self.clear_screen()
        self.render_header()
        self.render_network_health()
        self.render_consensus_latency()
        self.render_proof_throughput()
        self.render_validator_leaderboard()
        self.render_mempool_status()
        self.render_footer()
    
    def run(self, update_interval: float = 2.0):
        """
        Run the monitoring dashboard.
        
        Args:
            update_interval: Seconds between dashboard updates
        """
        print("Starting network monitor...")
        print(f"Monitoring nodes: {', '.join(self.node_ids)}")
        print(f"Update interval: {update_interval}s")
        print("\nPress Ctrl+C to exit\n")
        
        time.sleep(2)  # Give user time to read startup message
        
        try:
            while True:
                self.update()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            print("\n\nStopping network monitor...")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Real-time monitoring dashboard for Proof-of-Proof consensus"
    )
    parser.add_argument(
        "--nodes",
        type=str,
        required=True,
        help="Comma-separated list of node IDs to monitor"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Update interval in seconds (default: 2.0)"
    )
    
    args = parser.parse_args()
    
    # Parse node IDs
    node_ids = [node.strip() for node in args.nodes.split(',')]
    
    # Create and run monitor
    monitor = NetworkMonitor(node_ids)
    monitor.run(update_interval=args.interval)


if __name__ == "__main__":
    main()
