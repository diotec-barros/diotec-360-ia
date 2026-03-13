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
MOE Intelligence Layer Monitoring Script

Real-time monitoring of MOE expert performance, consensus quality,
and system health.

Usage:
    python scripts/monitor_moe.py
    python scripts/monitor_moe.py --interval 5
    python scripts/monitor_moe.py --export-prometheus
"""

import os
import sys
import time
import argparse
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any


class MOEMonitor:
    """Monitor MOE Intelligence Layer performance and health."""
    
    def __init__(self, telemetry_db_path: str = "./.diotec360_moe/telemetry.db"):
        self.telemetry_db_path = Path(telemetry_db_path)
        if not self.telemetry_db_path.exists():
            raise FileNotFoundError(f"Telemetry database not found: {telemetry_db_path}")
    
    def get_expert_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get expert performance statistics."""
        conn = sqlite3.connect(str(self.telemetry_db_path))
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        stats = {}
        
        for expert_name in ['Z3_Expert', 'Sentinel_Expert', 'Guardian_Expert']:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_verdicts,
                    AVG(latency_ms) as avg_latency,
                    MAX(latency_ms) as max_latency,
                    AVG(confidence) as avg_confidence,
                    SUM(CASE WHEN verdict='APPROVE' THEN 1 ELSE 0 END) as approvals,
                    SUM(CASE WHEN verdict='REJECT' THEN 1 ELSE 0 END) as rejections,
                    SUM(CASE WHEN timeout=1 THEN 1 ELSE 0 END) as timeouts,
                    SUM(CASE WHEN failure=1 THEN 1 ELSE 0 END) as failures
                FROM expert_verdicts
                WHERE expert_name = ? AND timestamp > ?
            """, (expert_name, cutoff_time.isoformat()))
            
            row = cursor.fetchone()
            
            stats[expert_name] = {
                'total_verdicts': row[0],
                'avg_latency_ms': round(row[1], 2) if row[1] else 0,
                'max_latency_ms': round(row[2], 2) if row[2] else 0,
                'avg_confidence': round(row[3], 3) if row[3] else 0,
                'approvals': row[4],
                'rejections': row[5],
                'timeouts': row[6],
                'failures': row[7],
                'timeout_rate': round(row[6] / row[0] * 100, 2) if row[0] > 0 else 0,
                'failure_rate': round(row[7] / row[0] * 100, 2) if row[0] > 0 else 0
            }
        
        conn.close()
        return stats
    
    def get_consensus_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get consensus engine statistics."""
        conn = sqlite3.connect(str(self.telemetry_db_path))
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_transactions,
                SUM(CASE WHEN consensus='APPROVED' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN consensus='REJECTED' THEN 1 ELSE 0 END) as rejected,
                SUM(CASE WHEN consensus='UNCERTAIN' THEN 1 ELSE 0 END) as uncertain,
                AVG(overall_confidence) as avg_confidence,
                AVG(total_latency_ms) as avg_latency
            FROM moe_results
            WHERE timestamp > ?
        """, (cutoff_time.isoformat(),))
        
        row = cursor.fetchone()
        
        total = row[0] if row[0] else 0
        
        stats = {
            'total_transactions': total,
            'approved': row[1],
            'rejected': row[2],
            'uncertain': row[3],
            'approval_rate': round(row[1] / total * 100, 2) if total > 0 else 0,
            'rejection_rate': round(row[2] / total * 100, 2) if total > 0 else 0,
            'uncertainty_rate': round(row[3] / total * 100, 2) if total > 0 else 0,
            'avg_confidence': round(row[4], 3) if row[4] else 0,
            'avg_latency_ms': round(row[5], 2) if row[5] else 0
        }
        
        conn.close()
        return stats
    
    def get_orchestration_stats(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get orchestration overhead statistics."""
        conn = sqlite3.connect(str(self.telemetry_db_path))
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        cursor.execute("""
            SELECT 
                AVG(gating_latency_ms) as avg_gating_latency,
                AVG(consensus_latency_ms) as avg_consensus_latency,
                AVG(gating_latency_ms + consensus_latency_ms) as avg_overhead,
                MAX(gating_latency_ms + consensus_latency_ms) as max_overhead
            FROM moe_results
            WHERE timestamp > ?
        """, (cutoff_time.isoformat(),))
        
        row = cursor.fetchone()
        
        stats = {
            'avg_gating_latency_ms': round(row[0], 2) if row[0] else 0,
            'avg_consensus_latency_ms': round(row[1], 2) if row[1] else 0,
            'avg_overhead_ms': round(row[2], 2) if row[2] else 0,
            'max_overhead_ms': round(row[3], 2) if row[3] else 0
        }
        
        conn.close()
        return stats
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get verdict cache statistics."""
        conn = sqlite3.connect(str(self.telemetry_db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(cache_hits) as total_hits,
                SUM(cache_misses) as total_misses,
                cache_size
            FROM cache_stats
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if row and row[0] is not None:
            total_hits = row[0]
            total_misses = row[1]
            total_requests = total_hits + total_misses
            
            stats = {
                'total_hits': total_hits,
                'total_misses': total_misses,
                'hit_rate': round(total_hits / total_requests * 100, 2) if total_requests > 0 else 0,
                'cache_size': row[2]
            }
        else:
            stats = {
                'total_hits': 0,
                'total_misses': 0,
                'hit_rate': 0,
                'cache_size': 0
            }
        
        conn.close()
        return stats
    
    def check_health(self) -> Dict[str, Any]:
        """Check overall MOE health and identify issues."""
        expert_stats = self.get_expert_stats(time_window_minutes=10)
        consensus_stats = self.get_consensus_stats(time_window_minutes=10)
        orchestration_stats = self.get_orchestration_stats(time_window_minutes=10)
        
        issues = []
        warnings = []
        
        # Check expert failure rates
        for expert_name, stats in expert_stats.items():
            if stats['failure_rate'] > 5:
                issues.append(f"{expert_name} failure rate: {stats['failure_rate']}% (>5%)")
            elif stats['failure_rate'] > 1:
                warnings.append(f"{expert_name} failure rate: {stats['failure_rate']}% (>1%)")
            
            if stats['timeout_rate'] > 5:
                issues.append(f"{expert_name} timeout rate: {stats['timeout_rate']}% (>5%)")
            elif stats['timeout_rate'] > 1:
                warnings.append(f"{expert_name} timeout rate: {stats['timeout_rate']}% (>1%)")
        
        # Check orchestration overhead
        if orchestration_stats['avg_overhead_ms'] > 10:
            issues.append(f"Orchestration overhead: {orchestration_stats['avg_overhead_ms']}ms (>10ms)")
        elif orchestration_stats['avg_overhead_ms'] > 5:
            warnings.append(f"Orchestration overhead: {orchestration_stats['avg_overhead_ms']}ms (>5ms)")
        
        # Check uncertainty rate
        if consensus_stats['uncertainty_rate'] > 1:
            warnings.append(f"Uncertainty rate: {consensus_stats['uncertainty_rate']}% (>1%)")
        
        health_status = "HEALTHY" if not issues else "UNHEALTHY"
        if warnings and not issues:
            health_status = "WARNING"
        
        return {
            'status': health_status,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_dashboard(self, time_window_minutes: int = 60):
        """Print real-time monitoring dashboard."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("MOE INTELLIGENCE LAYER - REAL-TIME MONITORING")
        print("=" * 80)
        print(f"Time Window: Last {time_window_minutes} minutes")
        print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Health Check
        health = self.check_health()
        status_color = {
            'HEALTHY': '✅',
            'WARNING': '⚠️',
            'UNHEALTHY': '❌'
        }
        print(f"Overall Status: {status_color[health['status']]} {health['status']}")
        
        if health['issues']:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in health['issues']:
                print(f"   - {issue}")
        
        if health['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in health['warnings']:
                print(f"   - {warning}")
        
        print()
        
        # Expert Performance
        print("-" * 80)
        print("EXPERT PERFORMANCE")
        print("-" * 80)
        
        expert_stats = self.get_expert_stats(time_window_minutes)
        
        for expert_name, stats in expert_stats.items():
            print(f"\n{expert_name}:")
            print(f"  Verdicts: {stats['total_verdicts']} (✅ {stats['approvals']} | ❌ {stats['rejections']})")
            print(f"  Latency: {stats['avg_latency_ms']}ms avg, {stats['max_latency_ms']}ms max")
            print(f"  Confidence: {stats['avg_confidence']}")
            print(f"  Timeouts: {stats['timeouts']} ({stats['timeout_rate']}%)")
            print(f"  Failures: {stats['failures']} ({stats['failure_rate']}%)")
        
        # Consensus Statistics
        print("\n" + "-" * 80)
        print("CONSENSUS ENGINE")
        print("-" * 80)
        
        consensus_stats = self.get_consensus_stats(time_window_minutes)
        
        print(f"\nTotal Transactions: {consensus_stats['total_transactions']}")
        print(f"  ✅ Approved: {consensus_stats['approved']} ({consensus_stats['approval_rate']}%)")
        print(f"  ❌ Rejected: {consensus_stats['rejected']} ({consensus_stats['rejection_rate']}%)")
        print(f"  ❓ Uncertain: {consensus_stats['uncertain']} ({consensus_stats['uncertainty_rate']}%)")
        print(f"Average Confidence: {consensus_stats['avg_confidence']}")
        print(f"Average Latency: {consensus_stats['avg_latency_ms']}ms")
        
        # Orchestration Overhead
        print("\n" + "-" * 80)
        print("ORCHESTRATION OVERHEAD")
        print("-" * 80)
        
        orchestration_stats = self.get_orchestration_stats(time_window_minutes)
        
        print(f"\nGating Network: {orchestration_stats['avg_gating_latency_ms']}ms avg")
        print(f"Consensus Engine: {orchestration_stats['avg_consensus_latency_ms']}ms avg")
        print(f"Total Overhead: {orchestration_stats['avg_overhead_ms']}ms avg, {orchestration_stats['max_overhead_ms']}ms max")
        
        overhead_status = "✅" if orchestration_stats['avg_overhead_ms'] < 10 else "❌"
        print(f"Status: {overhead_status} {'Within target (<10ms)' if orchestration_stats['avg_overhead_ms'] < 10 else 'Above target (>10ms)'}")
        
        # Cache Performance
        print("\n" + "-" * 80)
        print("VERDICT CACHE")
        print("-" * 80)
        
        cache_stats = self.get_cache_stats()
        
        print(f"\nCache Hits: {cache_stats['total_hits']}")
        print(f"Cache Misses: {cache_stats['total_misses']}")
        print(f"Hit Rate: {cache_stats['hit_rate']}%")
        print(f"Cache Size: {cache_stats['cache_size']}")
        
        print("\n" + "=" * 80)
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format."""
        expert_stats = self.get_expert_stats(time_window_minutes=5)
        consensus_stats = self.get_consensus_stats(time_window_minutes=5)
        orchestration_stats = self.get_orchestration_stats(time_window_minutes=5)
        cache_stats = self.get_cache_stats()
        
        metrics = []
        
        # Expert metrics
        for expert_name, stats in expert_stats.items():
            expert_label = expert_name.lower().replace('_', '_')
            metrics.append(f'{expert_label}_verdicts_total {stats["total_verdicts"]}')
            metrics.append(f'{expert_label}_avg_latency_ms {stats["avg_latency_ms"]}')
            metrics.append(f'{expert_label}_avg_confidence {stats["avg_confidence"]}')
            metrics.append(f'{expert_label}_timeouts_total {stats["timeouts"]}')
            metrics.append(f'{expert_label}_failures_total {stats["failures"]}')
        
        # Consensus metrics
        metrics.append(f'moe_transactions_total {consensus_stats["total_transactions"]}')
        metrics.append(f'moe_verdicts_approved {consensus_stats["approved"]}')
        metrics.append(f'moe_verdicts_rejected {consensus_stats["rejected"]}')
        metrics.append(f'moe_verdicts_uncertain {consensus_stats["uncertain"]}')
        metrics.append(f'moe_avg_confidence {consensus_stats["avg_confidence"]}')
        
        # Orchestration metrics
        metrics.append(f'moe_overhead_ms {orchestration_stats["avg_overhead_ms"]}')
        metrics.append(f'gating_network_latency_ms {orchestration_stats["avg_gating_latency_ms"]}')
        metrics.append(f'consensus_engine_latency_ms {orchestration_stats["avg_consensus_latency_ms"]}')
        
        # Cache metrics
        metrics.append(f'verdict_cache_hits_total {cache_stats["total_hits"]}')
        metrics.append(f'verdict_cache_misses_total {cache_stats["total_misses"]}')
        metrics.append(f'verdict_cache_hit_rate {cache_stats["hit_rate"] / 100}')
        metrics.append(f'verdict_cache_size {cache_stats["cache_size"]}')
        
        return '\n'.join(metrics)


def main():
    parser = argparse.ArgumentParser(
        description="Monitor MOE Intelligence Layer performance"
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Update interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--time-window',
        type=int,
        default=60,
        help='Time window in minutes (default: 60)'
    )
    parser.add_argument(
        '--export-prometheus',
        action='store_true',
        help='Export metrics in Prometheus format and exit'
    )
    parser.add_argument(
        '--db-path',
        default='./.diotec360_moe/telemetry.db',
        help='Path to telemetry database'
    )
    
    args = parser.parse_args()
    
    try:
        monitor = MOEMonitor(telemetry_db_path=args.db_path)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    if args.export_prometheus:
        print(monitor.export_prometheus_metrics())
        sys.exit(0)
    
    # Real-time monitoring loop
    try:
        while True:
            monitor.print_dashboard(time_window_minutes=args.time_window)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        sys.exit(0)


if __name__ == '__main__':
    main()
