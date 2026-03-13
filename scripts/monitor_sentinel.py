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
Sentinel Monitoring Dashboard

Real-time monitoring of Autonomous Sentinel metrics:
- Transaction metrics and anomaly detection
- Crisis Mode status
- Quarantine system status
- Self-Healing rules
- Attack statistics

Usage:
    python scripts/monitor_sentinel.py
    python scripts/monitor_sentinel.py --refresh 5
"""

import sqlite3
import time
import argparse
import os
from datetime import datetime, timedelta


def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_telemetry_stats(db_path: str, time_window: int = 3600) -> dict:
    """Get telemetry statistics for time window."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cutoff_time = time.time() - time_window
    
    # Total transactions
    cursor.execute("""
        SELECT COUNT(*) FROM transaction_metrics 
        WHERE timestamp > ?
    """, (cutoff_time,))
    total = cursor.fetchone()[0]
    
    # Anomalous transactions
    cursor.execute("""
        SELECT COUNT(*) FROM transaction_metrics 
        WHERE timestamp > ? AND anomaly_score > 0.7
    """, (cutoff_time,))
    anomalous = cursor.fetchone()[0]
    
    # Average metrics
    cursor.execute("""
        SELECT 
            AVG(cpu_time_ms),
            AVG(memory_delta_mb),
            AVG(z3_duration_ms),
            AVG(anomaly_score)
        FROM transaction_metrics 
        WHERE timestamp > ?
    """, (cutoff_time,))
    avg_cpu, avg_mem, avg_z3, avg_anomaly = cursor.fetchone()
    
    # Crisis Mode status
    cursor.execute("""
        SELECT crisis_mode FROM transaction_metrics 
        ORDER BY timestamp DESC LIMIT 1
    """)
    result = cursor.fetchone()
    crisis_mode = result[0] if result else 0
    
    # Crisis Mode transitions
    cursor.execute("""
        SELECT COUNT(*) FROM crisis_mode_transitions 
        WHERE timestamp > ?
    """, (cutoff_time,))
    crisis_transitions = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total': total,
        'anomalous': anomalous,
        'anomaly_rate': (anomalous / total * 100) if total > 0 else 0,
        'avg_cpu_ms': avg_cpu or 0,
        'avg_memory_mb': avg_mem or 0,
        'avg_z3_ms': avg_z3 or 0,
        'avg_anomaly_score': avg_anomaly or 0,
        'crisis_mode': bool(crisis_mode),
        'crisis_transitions': crisis_transitions
    }


def get_gauntlet_stats(db_path: str, time_window: int = 3600) -> dict:
    """Get attack statistics for time window."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cutoff_time = time.time() - time_window
    
    # Total attacks
    cursor.execute("""
        SELECT COUNT(*) FROM attack_records 
        WHERE timestamp > ?
    """, (cutoff_time,))
    total_attacks = cursor.fetchone()[0]
    
    # Attacks by category
    cursor.execute("""
        SELECT attack_category, COUNT(*) 
        FROM attack_records 
        WHERE timestamp > ?
        GROUP BY attack_category
    """, (cutoff_time,))
    by_category = dict(cursor.fetchall())
    
    # Attacks by detection method
    cursor.execute("""
        SELECT detection_method, COUNT(*) 
        FROM attack_records 
        WHERE timestamp > ?
        GROUP BY detection_method
    """, (cutoff_time,))
    by_detection = dict(cursor.fetchall())
    
    # Self-Healing rules
    cursor.execute("""
        SELECT COUNT(*) FROM self_healing_rules WHERE active=1
    """)
    active_rules = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT AVG(effectiveness) FROM self_healing_rules WHERE active=1
    """)
    avg_effectiveness = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_attacks': total_attacks,
        'by_category': by_category,
        'by_detection': by_detection,
        'active_rules': active_rules,
        'avg_effectiveness': avg_effectiveness
    }


def display_dashboard(telemetry_path: str, gauntlet_path: str, time_window: int):
    """Display monitoring dashboard."""
    clear_screen()
    
    # Header
    print("=" * 80)
    print("🤖 AUTONOMOUS SENTINEL MONITORING DASHBOARD".center(80))
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Window: Last {time_window // 60} minutes")
    print("=" * 80)
    
    # Get statistics
    try:
        telemetry = get_telemetry_stats(telemetry_path, time_window)
        gauntlet = get_gauntlet_stats(gauntlet_path, time_window)
    except Exception as e:
        print(f"\n❌ Error reading databases: {e}")
        print("\nMake sure databases are initialized:")
        print("  python scripts/init_databases.py")
        return
    
    # System Status
    print("\n📊 SYSTEM STATUS")
    print("-" * 80)
    
    crisis_status = "🚨 CRISIS MODE" if telemetry['crisis_mode'] else "✅ NORMAL"
    print(f"Mode: {crisis_status}")
    print(f"Transactions: {telemetry['total']}")
    print(f"Anomaly Rate: {telemetry['anomaly_rate']:.2f}% ", end="")
    
    if telemetry['anomaly_rate'] > 10:
        print("⚠️  HIGH")
    elif telemetry['anomaly_rate'] > 5:
        print("⚠️  ELEVATED")
    else:
        print("✅ NORMAL")
    
    print(f"Crisis Transitions: {telemetry['crisis_transitions']}")
    
    # Performance Metrics
    print("\n⚡ PERFORMANCE METRICS")
    print("-" * 80)
    print(f"Avg CPU Time: {telemetry['avg_cpu_ms']:.2f} ms")
    print(f"Avg Memory Delta: {telemetry['avg_memory_mb']:.2f} MB")
    print(f"Avg Z3 Duration: {telemetry['avg_z3_ms']:.2f} ms")
    print(f"Avg Anomaly Score: {telemetry['avg_anomaly_score']:.3f}")
    
    # Attack Statistics
    print("\n🛡️  ATTACK STATISTICS")
    print("-" * 80)
    print(f"Total Attacks Blocked: {gauntlet['total_attacks']}")
    
    if gauntlet['by_category']:
        print("\nBy Category:")
        for category, count in sorted(gauntlet['by_category'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / gauntlet['total_attacks'] * 100) if gauntlet['total_attacks'] > 0 else 0
            print(f"  {category:15s}: {count:4d} ({percentage:5.1f}%)")
    
    if gauntlet['by_detection']:
        print("\nBy Detection Method:")
        for method, count in sorted(gauntlet['by_detection'].items(), 
                                   key=lambda x: x[1], reverse=True):
            percentage = (count / gauntlet['total_attacks'] * 100) if gauntlet['total_attacks'] > 0 else 0
            print(f"  {method:20s}: {count:4d} ({percentage:5.1f}%)")
    
    # Self-Healing
    print("\n🔧 SELF-HEALING ENGINE")
    print("-" * 80)
    print(f"Active Rules: {gauntlet['active_rules']}")
    print(f"Avg Effectiveness: {gauntlet['avg_effectiveness']:.1%}")
    
    # Alerts
    print("\n🔔 ALERTS")
    print("-" * 80)
    
    alerts = []
    
    if telemetry['crisis_mode']:
        alerts.append("🚨 CRITICAL: Crisis Mode Active")
    
    if telemetry['anomaly_rate'] > 10:
        alerts.append(f"⚠️  WARNING: High Anomaly Rate ({telemetry['anomaly_rate']:.1f}%)")
    
    if gauntlet['avg_effectiveness'] < 0.7 and gauntlet['active_rules'] > 0:
        alerts.append(f"⚠️  WARNING: Low Rule Effectiveness ({gauntlet['avg_effectiveness']:.1%})")
    
    if not alerts:
        print("✅ No alerts")
    else:
        for alert in alerts:
            print(alert)
    
    # Footer
    print("\n" + "=" * 80)
    print("Press Ctrl+C to exit")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor Autonomous Sentinel in real-time"
    )
    parser.add_argument(
        '--telemetry-path',
        default='./data/telemetry.db',
        help='Path to telemetry database'
    )
    parser.add_argument(
        '--gauntlet-path',
        default='./data/gauntlet.db',
        help='Path to gauntlet database'
    )
    parser.add_argument(
        '--refresh',
        type=int,
        default=5,
        help='Refresh interval in seconds (default: 5)'
    )
    parser.add_argument(
        '--window',
        type=int,
        default=3600,
        help='Time window in seconds (default: 3600 = 1 hour)'
    )
    
    args = parser.parse_args()
    
    print("Starting Sentinel Monitor...")
    print(f"Refresh interval: {args.refresh} seconds")
    print(f"Time window: {args.window // 60} minutes")
    print("\nPress Ctrl+C to exit\n")
    
    time.sleep(2)
    
    try:
        while True:
            display_dashboard(args.telemetry_path, args.gauntlet_path, args.window)
            time.sleep(args.refresh)
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")


if __name__ == '__main__':
    main()
