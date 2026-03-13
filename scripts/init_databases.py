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
Initialize Sentinel Databases

This script creates the SQLite database schemas for:
1. telemetry.db - Transaction metrics and anomaly detection
2. gauntlet.db - Attack forensics and logging

Usage:
    python scripts/init_databases.py
    python scripts/init_databases.py --telemetry-path ./data/telemetry.db
    python scripts/init_databases.py --gauntlet-path ./data/gauntlet.db
"""

import sqlite3
import argparse
import os
from pathlib import Path


def create_telemetry_schema(db_path: str) -> None:
    """Create telemetry database schema."""
    print(f"Creating telemetry database: {db_path}")
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Transaction metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transaction_metrics (
            tx_id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            cpu_time_ms REAL NOT NULL,
            memory_delta_mb REAL NOT NULL,
            z3_duration_ms REAL NOT NULL,
            anomaly_score REAL NOT NULL,
            layer_results TEXT NOT NULL,
            outcome TEXT NOT NULL,
            crisis_mode BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    # Indices for common queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON transaction_metrics(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_anomaly_score 
        ON transaction_metrics(anomaly_score)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_outcome 
        ON transaction_metrics(outcome)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_crisis_mode 
        ON transaction_metrics(crisis_mode)
    """)
    
    # Crisis Mode transitions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crisis_mode_transitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            from_mode TEXT NOT NULL,
            to_mode TEXT NOT NULL,
            reason TEXT NOT NULL,
            anomaly_rate REAL,
            request_rate REAL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_transition_timestamp 
        ON crisis_mode_transitions(timestamp)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Telemetry database created successfully")
    print(f"   Tables: transaction_metrics, crisis_mode_transitions")
    print(f"   Indices: 5 indices created for query optimization")


def create_gauntlet_schema(db_path: str) -> None:
    """Create gauntlet report database schema."""
    print(f"\nCreating gauntlet database: {db_path}")
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Attack records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attack_records (
            record_id TEXT PRIMARY KEY,
            timestamp REAL NOT NULL,
            source_ip TEXT,
            attack_type TEXT NOT NULL,
            attack_category TEXT NOT NULL,
            code_snippet TEXT NOT NULL,
            detection_method TEXT NOT NULL,
            severity REAL NOT NULL,
            metrics_json TEXT NOT NULL,
            blocked BOOLEAN NOT NULL DEFAULT 1
        )
    """)
    
    # Indices for common queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attack_timestamp 
        ON attack_records(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attack_type 
        ON attack_records(attack_type)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attack_category 
        ON attack_records(attack_category)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_detection_method 
        ON attack_records(detection_method)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_severity 
        ON attack_records(severity)
    """)
    
    # Self-Healing rules table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS self_healing_rules (
            rule_id TEXT PRIMARY KEY,
            pattern_id TEXT NOT NULL,
            pattern_name TEXT NOT NULL,
            ast_signature TEXT NOT NULL,
            severity REAL NOT NULL,
            created_at REAL NOT NULL,
            active BOOLEAN NOT NULL DEFAULT 1,
            true_positives INTEGER NOT NULL DEFAULT 0,
            false_positives INTEGER NOT NULL DEFAULT 0,
            effectiveness REAL NOT NULL DEFAULT 1.0
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rule_active 
        ON self_healing_rules(active)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_rule_effectiveness 
        ON self_healing_rules(effectiveness)
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Gauntlet database created successfully")
    print(f"   Tables: attack_records, self_healing_rules")
    print(f"   Indices: 7 indices created for query optimization")


def verify_databases(telemetry_path: str, gauntlet_path: str) -> None:
    """Verify database schemas are correct."""
    print(f"\n🔍 Verifying databases...")
    
    # Verify telemetry database
    conn = sqlite3.connect(telemetry_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'transaction_metrics' in tables, "Missing transaction_metrics table"
    assert 'crisis_mode_transitions' in tables, "Missing crisis_mode_transitions table"
    
    conn.close()
    print(f"   ✅ Telemetry database verified")
    
    # Verify gauntlet database
    conn = sqlite3.connect(gauntlet_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'attack_records' in tables, "Missing attack_records table"
    assert 'self_healing_rules' in tables, "Missing self_healing_rules table"
    
    conn.close()
    print(f"   ✅ Gauntlet database verified")
    
    print(f"\n✅ All databases initialized and verified successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Sentinel databases"
    )
    parser.add_argument(
        '--telemetry-path',
        default='./data/telemetry.db',
        help='Path to telemetry database (default: ./data/telemetry.db)'
    )
    parser.add_argument(
        '--gauntlet-path',
        default='./data/gauntlet.db',
        help='Path to gauntlet database (default: ./data/gauntlet.db)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of databases (deletes existing)'
    )
    
    args = parser.parse_args()
    
    # Check if databases exist
    if os.path.exists(args.telemetry_path) and not args.force:
        print(f"⚠️  Telemetry database already exists: {args.telemetry_path}")
        print(f"   Use --force to recreate")
        return
    
    if os.path.exists(args.gauntlet_path) and not args.force:
        print(f"⚠️  Gauntlet database already exists: {args.gauntlet_path}")
        print(f"   Use --force to recreate")
        return
    
    # Delete existing databases if force flag is set
    if args.force:
        if os.path.exists(args.telemetry_path):
            os.remove(args.telemetry_path)
            print(f"🗑️  Deleted existing telemetry database")
        
        if os.path.exists(args.gauntlet_path):
            os.remove(args.gauntlet_path)
            print(f"🗑️  Deleted existing gauntlet database")
    
    # Create databases
    create_telemetry_schema(args.telemetry_path)
    create_gauntlet_schema(args.gauntlet_path)
    
    # Verify
    verify_databases(args.telemetry_path, args.gauntlet_path)
    
    print(f"\n📝 Next steps:")
    print(f"   1. Set environment variables:")
    print(f"      DIOTEC360_TELEMETRY_DB_PATH={args.telemetry_path}")
    print(f"      DIOTEC360_GAUNTLET_DB_PATH={args.gauntlet_path}")
    print(f"   2. Run deployment script: python scripts/deploy_shadow_mode.py")
    print(f"   3. Monitor telemetry: python scripts/monitor_sentinel.py")


if __name__ == '__main__':
    main()
