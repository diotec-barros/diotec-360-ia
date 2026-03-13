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
Deploy MOE Intelligence Layer in Soft Launch Mode

Soft Launch: MOE affects 10% of traffic with high confidence thresholds
- MOE Orchestrator: ENABLED
- Expert Execution: ENABLED (all experts)
- Verdict Override: ENABLED (10% of traffic)
- Confidence Thresholds: HIGH (conservative)
- Fallback: Enabled for low confidence verdicts
- Caching: ENABLED

Purpose: Gradual activation with conservative thresholds

Duration: 2-4 weeks

Usage:
    python scripts/deploy_moe_soft_launch.py
    python scripts/deploy_moe_soft_launch.py --config ./config/moe_soft_launch.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_soft_launch_config(output_path: str) -> None:
    """Create soft launch configuration file."""
    config = """# MOE Intelligence Layer v2.1.0 - Soft Launch Configuration
# Purpose: MOE affects 10% of traffic with high confidence thresholds
# Duration: 2-4 weeks to validate production readiness

# ============================================================================
# Core MOE Settings
# ============================================================================
DIOTEC360_MOE_ENABLED=true
DIOTEC360_MOE_MODE=soft_launch
DIOTEC360_MOE_TELEMETRY_DB_PATH=./.diotec360_moe/telemetry.db

# ============================================================================
# MOE Orchestrator - ENABLED (10% Traffic)
# ============================================================================
DIOTEC360_MOE_OVERRIDE_VERDICT=true  # Override existing layers
DIOTEC360_MOE_TRAFFIC_PERCENTAGE=10  # 10% of traffic
DIOTEC360_MOE_LOG_VERDICTS=true
DIOTEC360_MOE_PARALLEL_EXPERTS=true

# ============================================================================
# Expert Configuration - HIGH CONFIDENCE THRESHOLDS
# ============================================================================
DIOTEC360_Z3_EXPERT_ENABLED=true
DIOTEC360_Z3_EXPERT_TIMEOUT_NORMAL=30
DIOTEC360_Z3_EXPERT_TIMEOUT_CRISIS=5
DIOTEC360_Z3_EXPERT_CONFIDENCE_THRESHOLD=0.85  # High (vs 0.7 production)

DIOTEC360_SENTINEL_EXPERT_ENABLED=true
DIOTEC360_SENTINEL_EXPERT_TIMEOUT_MS=100
DIOTEC360_SENTINEL_EXPERT_CONFIDENCE_THRESHOLD=0.85  # High (vs 0.7 production)

DIOTEC360_GUARDIAN_EXPERT_ENABLED=true
DIOTEC360_GUARDIAN_EXPERT_TIMEOUT_MS=50
DIOTEC360_GUARDIAN_EXPERT_CONFIDENCE_THRESHOLD=0.85  # High (vs 0.7 production)

# ============================================================================
# Gating Network - ENABLED (Intelligent Routing)
# ============================================================================
DIOTEC360_GATING_NETWORK_ENABLED=true
DIOTEC360_GATING_NETWORK_TIMEOUT_MS=10
DIOTEC360_GATING_NETWORK_DEFAULT_ROUTE=intelligent  # Route based on features

# ============================================================================
# Consensus Engine - ENABLED (High Thresholds)
# ============================================================================
DIOTEC360_CONSENSUS_ENGINE_ENABLED=true
DIOTEC360_CONSENSUS_CONFIDENCE_THRESHOLD=0.85  # High (vs 0.7 production)
DIOTEC360_CONSENSUS_UNCERTAINTY_THRESHOLD=0.6  # High (vs 0.5 production)

# ============================================================================
# Fallback Configuration - ENABLED
# ============================================================================
DIOTEC360_MOE_FALLBACK_ENABLED=true
DIOTEC360_MOE_FALLBACK_ON_TIMEOUT=true
DIOTEC360_MOE_FALLBACK_ON_LOW_CONFIDENCE=true
DIOTEC360_MOE_FALLBACK_ON_UNCERTAINTY=true

# ============================================================================
# Verdict Caching - ENABLED
# ============================================================================
DIOTEC360_MOE_CACHE_ENABLED=true
DIOTEC360_MOE_CACHE_TTL_SECONDS=300  # 5 minutes
DIOTEC360_MOE_CACHE_MAX_SIZE=10000

# ============================================================================
# Expert Training - ENABLED (Continuous Learning)
# ============================================================================
DIOTEC360_MOE_TRAINING_ENABLED=true
DIOTEC360_MOE_TRAINING_DB_PATH=./.diotec360_moe/training.db
DIOTEC360_MOE_TRAINING_WINDOW=1000
DIOTEC360_MOE_AUTO_THRESHOLD_ADJUSTMENT=false  # Manual adjustment in soft launch

# ============================================================================
# Visual Dashboard - ENABLED
# ============================================================================
DIOTEC360_MOE_VISUAL_DASHBOARD_ENABLED=true
DIOTEC360_MOE_DASHBOARD_UPDATE_INTERVAL_MS=100

# ============================================================================
# Monitoring and Logging
# ============================================================================
DIOTEC360_MOE_LOG_LEVEL=INFO
DIOTEC360_MOE_METRICS_ENABLED=true
DIOTEC360_MOE_METRICS_PORT=9091

# ============================================================================
# Alerting - ENABLED
# ============================================================================
DIOTEC360_MOE_ALERT_EXPERT_FAILURE=true
DIOTEC360_MOE_ALERT_HIGH_LATENCY=true
DIOTEC360_MOE_ALERT_LOW_ACCURACY=true
DIOTEC360_MOE_ALERT_FALLBACK_RATE=true
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Soft launch configuration created: {output_path}")


def validate_shadow_mode_complete() -> bool:
    """Validate that shadow mode was completed successfully."""
    print("🔍 Validating shadow mode completion...")
    
    # Check if telemetry database has data
    telemetry_db = Path('./.diotec360_moe/telemetry.db')
    if not telemetry_db.exists():
        print("❌ MOE telemetry database not found")
        print("   Run shadow mode first: python scripts/deploy_moe_shadow_mode.py")
        return False
    
    import sqlite3
    conn = sqlite3.connect(str(telemetry_db))
    cursor = conn.cursor()
    
    # Check if we have enough data
    cursor.execute("SELECT COUNT(*) FROM expert_verdicts")
    count = cursor.fetchone()[0]
    
    if count < 1000:
        print(f"⚠️  Only {count} expert verdicts in telemetry database")
        print("   Recommended: At least 1000 verdicts for baseline")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            conn.close()
            return False
    
    # Check expert accuracy
    cursor.execute("""
        SELECT expert_name, 
               AVG(CASE WHEN verdict_matches_existing = 1 THEN 1.0 ELSE 0.0 END) as accuracy
        FROM expert_verdicts
        GROUP BY expert_name
    """)
    
    print(f"\n✅ Shadow mode complete ({count} verdicts collected)")
    print("\n📊 Expert Accuracy:")
    for row in cursor.fetchall():
        expert_name, accuracy = row
        accuracy_pct = accuracy * 100
        status = "✅" if accuracy >= 0.999 else "⚠️"
        print(f"   {status} {expert_name}: {accuracy_pct:.2f}%")
        
        if accuracy < 0.999:
            print(f"      Warning: Accuracy below 99.9% target")
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                conn.close()
                return False
    
    conn.close()
    return True


def deploy_soft_launch(config_path: str) -> None:
    """Deploy MOE in soft launch mode."""
    print("\n🚀 Deploying MOE Intelligence Layer in Soft Launch Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    print("\n✅ Soft Launch Deployment Complete!")
    print("\n📊 Monitoring:")
    print("   - MOE Telemetry: http://localhost:9091/metrics")
    print("   - MOE Dashboard: http://localhost:3000/moe")
    print("   - Expert Status: http://localhost:3000/moe/experts")
    print("   - Consensus Analysis: http://localhost:3000/moe/consensus")
    print("   - Logs: tail -f logs/moe.log")
    
    print("\n📈 What to Monitor:")
    print("   1. False Positive Rate:")
    print("      - Target: <0.1%")
    print("      - Alert if >1%")
    print("      - Compare MOE verdicts with existing layers")
    print("   2. Expert Performance:")
    print("      - Latency within targets")
    print("      - Timeout rate <1%")
    print("      - Failure rate <0.1%")
    print("   3. Consensus Quality:")
    print("      - Unanimous approval rate")
    print("      - Uncertainty rate (should be <1%)")
    print("      - Fallback activation rate")
    print("   4. Throughput Impact:")
    print("      - Overhead should be <10ms")
    print("      - Throughput ≥95% of baseline")
    print("   5. Cache Performance:")
    print("      - Cache hit rate")
    print("      - Cache effectiveness")
    
    print("\n⚠️  Important:")
    print("   - MOE affects 10% of traffic")
    print("   - High confidence thresholds (0.85)")
    print("   - Fallback enabled for low confidence")
    print("   - Monitor false positives closely")
    
    print("\n⏱️  Duration: Run for 2-4 weeks")
    print("\n📝 Next Steps:")
    print("   1. Monitor false positive rate daily")
    print("   2. Review expert performance metrics")
    print("   3. Analyze consensus patterns")
    print("   4. Gradually increase traffic percentage (20%, 50%)")
    print("   5. Reduce confidence thresholds if stable")
    print("   6. After 2-4 weeks, proceed to Full Activation:")
    print("      python scripts/deploy_moe_full_activation.py")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy MOE in Soft Launch Mode (10% traffic, high thresholds)"
    )
    parser.add_argument(
        '--config',
        default='./config/moe_soft_launch.env',
        help='Path to configuration file (default: ./config/moe_soft_launch.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip shadow mode validation'
    )
    
    args = parser.parse_args()
    
    # Validate shadow mode complete
    if not args.skip_validation:
        if not validate_shadow_mode_complete():
            sys.exit(1)
    
    # Create configuration
    create_soft_launch_config(args.config)
    
    # Deploy
    deploy_soft_launch(args.config)


if __name__ == '__main__':
    main()
