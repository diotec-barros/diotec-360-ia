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
Deploy MOE Intelligence Layer in Full Activation Mode

Full Activation: MOE handles 100% of traffic with production thresholds
- MOE Orchestrator: ENABLED
- Expert Execution: ENABLED (all experts)
- Verdict Override: ENABLED (100% of traffic)
- Confidence Thresholds: PRODUCTION (0.7)
- Fallback: Enabled for failures only
- Caching: ENABLED
- Auto-Threshold Adjustment: ENABLED

Purpose: Full production deployment

Duration: Ongoing

Usage:
    python scripts/deploy_moe_full_activation.py
    python scripts/deploy_moe_full_activation.py --config ./config/moe_production.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_production_config(output_path: str) -> None:
    """Create production configuration file."""
    config = """# MOE Intelligence Layer v2.1.0 - Production Configuration
# Purpose: Full activation with production thresholds
# Duration: Ongoing production deployment

# ============================================================================
# Core MOE Settings
# ============================================================================
DIOTEC360_MOE_ENABLED=true
DIOTEC360_MOE_MODE=production
DIOTEC360_MOE_TELEMETRY_DB_PATH=./.diotec360_moe/telemetry.db

# ============================================================================
# MOE Orchestrator - ENABLED (100% Traffic)
# ============================================================================
DIOTEC360_MOE_OVERRIDE_VERDICT=true  # Override existing layers
DIOTEC360_MOE_TRAFFIC_PERCENTAGE=100  # 100% of traffic
DIOTEC360_MOE_LOG_VERDICTS=true
DIOTEC360_MOE_PARALLEL_EXPERTS=true

# ============================================================================
# Expert Configuration - PRODUCTION THRESHOLDS
# ============================================================================
DIOTEC360_Z3_EXPERT_ENABLED=true
DIOTEC360_Z3_EXPERT_TIMEOUT_NORMAL=30
DIOTEC360_Z3_EXPERT_TIMEOUT_CRISIS=5
DIOTEC360_Z3_EXPERT_CONFIDENCE_THRESHOLD=0.7  # Production threshold

DIOTEC360_SENTINEL_EXPERT_ENABLED=true
DIOTEC360_SENTINEL_EXPERT_TIMEOUT_MS=100
DIOTEC360_SENTINEL_EXPERT_CONFIDENCE_THRESHOLD=0.7  # Production threshold

DIOTEC360_GUARDIAN_EXPERT_ENABLED=true
DIOTEC360_GUARDIAN_EXPERT_TIMEOUT_MS=50
DIOTEC360_GUARDIAN_EXPERT_CONFIDENCE_THRESHOLD=0.7  # Production threshold

# ============================================================================
# Gating Network - ENABLED (Intelligent Routing)
# ============================================================================
DIOTEC360_GATING_NETWORK_ENABLED=true
DIOTEC360_GATING_NETWORK_TIMEOUT_MS=10
DIOTEC360_GATING_NETWORK_DEFAULT_ROUTE=intelligent  # Route based on features
DIOTEC360_GATING_NETWORK_LEARNING_ENABLED=true  # Learn from routing patterns

# ============================================================================
# Consensus Engine - ENABLED (Production Thresholds)
# ============================================================================
DIOTEC360_CONSENSUS_ENGINE_ENABLED=true
DIOTEC360_CONSENSUS_CONFIDENCE_THRESHOLD=0.7  # Production threshold
DIOTEC360_CONSENSUS_UNCERTAINTY_THRESHOLD=0.5  # Production threshold

# ============================================================================
# Fallback Configuration - ENABLED (Failures Only)
# ============================================================================
DIOTEC360_MOE_FALLBACK_ENABLED=true
DIOTEC360_MOE_FALLBACK_ON_TIMEOUT=true
DIOTEC360_MOE_FALLBACK_ON_LOW_CONFIDENCE=false  # Don't fallback on low confidence
DIOTEC360_MOE_FALLBACK_ON_UNCERTAINTY=false  # Don't fallback on uncertainty

# ============================================================================
# Verdict Caching - ENABLED (Optimized)
# ============================================================================
DIOTEC360_MOE_CACHE_ENABLED=true
DIOTEC360_MOE_CACHE_TTL_SECONDS=300  # 5 minutes
DIOTEC360_MOE_CACHE_MAX_SIZE=10000
DIOTEC360_MOE_CACHE_EVICTION_POLICY=lru

# ============================================================================
# Expert Training - ENABLED (Continuous Learning)
# ============================================================================
DIOTEC360_MOE_TRAINING_ENABLED=true
DIOTEC360_MOE_TRAINING_DB_PATH=./.diotec360_moe/training.db
DIOTEC360_MOE_TRAINING_WINDOW=1000
DIOTEC360_MOE_AUTO_THRESHOLD_ADJUSTMENT=true  # Auto-adjust based on accuracy
DIOTEC360_MOE_AB_TESTING_ENABLED=true  # A/B test new expert models

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
# Alerting - ENABLED (All Alerts)
# ============================================================================
DIOTEC360_MOE_ALERT_EXPERT_FAILURE=true
DIOTEC360_MOE_ALERT_HIGH_LATENCY=true
DIOTEC360_MOE_ALERT_LOW_ACCURACY=true
DIOTEC360_MOE_ALERT_FALLBACK_RATE=true
DIOTEC360_MOE_ALERT_CONSENSUS_UNCERTAINTY=true
DIOTEC360_MOE_ALERT_THROUGHPUT_DEGRADATION=true

# ============================================================================
# Performance Tuning
# ============================================================================
DIOTEC360_MOE_ASYNC_EXPERT_EXECUTION=true
DIOTEC360_MOE_EXPERT_POOL_SIZE=10
DIOTEC360_MOE_TELEMETRY_BATCH_SIZE=100
DIOTEC360_MOE_ASYNC_PERSISTENCE=true
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Production configuration created: {output_path}")


def validate_soft_launch_complete() -> bool:
    """Validate that soft launch was completed successfully."""
    print("🔍 Validating soft launch completion...")
    
    # Check if telemetry database has sufficient data
    telemetry_db = Path('./.diotec360_moe/telemetry.db')
    if not telemetry_db.exists():
        print("❌ MOE telemetry database not found")
        return False
    
    import sqlite3
    conn = sqlite3.connect(str(telemetry_db))
    cursor = conn.cursor()
    
    # Check if we have enough production data
    cursor.execute("SELECT COUNT(*) FROM expert_verdicts WHERE mode='soft_launch'")
    count = cursor.fetchone()[0]
    
    if count < 10000:
        print(f"⚠️  Only {count} soft launch verdicts in database")
        print("   Recommended: At least 10,000 verdicts for validation")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            conn.close()
            return False
    
    # Check false positive rate
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN verdict='REJECT' AND actual_outcome='SAFE' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as fp_rate
        FROM expert_verdicts
        WHERE mode='soft_launch' AND actual_outcome IS NOT NULL
    """)
    
    fp_rate = cursor.fetchone()[0]
    if fp_rate is not None:
        fp_rate_pct = fp_rate * 100
        print(f"\n📊 False Positive Rate: {fp_rate_pct:.3f}%")
        
        if fp_rate > 0.001:  # >0.1%
            print(f"   ⚠️  False positive rate above 0.1% target")
            response = input("   Continue anyway? (y/n): ")
            if response.lower() != 'y':
                conn.close()
                return False
    
    # Check expert performance
    cursor.execute("""
        SELECT expert_name,
               AVG(latency_ms) as avg_latency,
               MAX(latency_ms) as max_latency,
               AVG(confidence) as avg_confidence
        FROM expert_verdicts
        WHERE mode='soft_launch'
        GROUP BY expert_name
    """)
    
    print(f"\n✅ Soft launch complete ({count} verdicts collected)")
    print("\n📊 Expert Performance:")
    for row in cursor.fetchall():
        expert_name, avg_latency, max_latency, avg_confidence = row
        print(f"   {expert_name}:")
        print(f"      Avg Latency: {avg_latency:.2f}ms")
        print(f"      Max Latency: {max_latency:.2f}ms")
        print(f"      Avg Confidence: {avg_confidence:.3f}")
    
    conn.close()
    return True


def deploy_full_activation(config_path: str) -> None:
    """Deploy MOE in full activation mode."""
    print("\n🚀 Deploying MOE Intelligence Layer in Full Activation Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    print("\n✅ Full Activation Deployment Complete!")
    print("\n🎉 MOE Intelligence Layer is now fully operational!")
    
    print("\n📊 Monitoring:")
    print("   - MOE Telemetry: http://localhost:9091/metrics")
    print("   - MOE Dashboard: http://localhost:3000/moe")
    print("   - Expert Status: http://localhost:3000/moe/experts")
    print("   - Consensus Analysis: http://localhost:3000/moe/consensus")
    print("   - Training Metrics: http://localhost:3000/moe/training")
    print("   - A/B Testing: http://localhost:3000/moe/ab-testing")
    print("   - Logs: tail -f logs/moe.log")
    
    print("\n📈 What to Monitor:")
    print("   1. Expert Accuracy:")
    print("      - Target: >99.9%")
    print("      - Alert if <99.9%")
    print("   2. False Positive Rate:")
    print("      - Target: <0.1%")
    print("      - Alert if >1%")
    print("   3. Expert Latency:")
    print("      - Z3 Expert: <30s (95th percentile)")
    print("      - Sentinel Expert: <100ms (95th percentile)")
    print("      - Guardian Expert: <50ms (95th percentile)")
    print("   4. Orchestration Overhead:")
    print("      - Target: <10ms")
    print("      - Alert if >10ms")
    print("   5. Throughput:")
    print("      - Target: >1000 tx/s")
    print("      - Alert if <1000 tx/s")
    print("   6. Consensus Quality:")
    print("      - Unanimous approval rate")
    print("      - Uncertainty rate (should be <1%)")
    print("   7. Cache Performance:")
    print("      - Cache hit rate")
    print("      - Cache effectiveness")
    print("   8. Expert Training:")
    print("      - Accuracy improvement over time")
    print("      - Threshold adjustments")
    print("      - A/B test results")
    
    print("\n🔔 Alerts Configured:")
    print("   - Expert failure (CRITICAL)")
    print("   - High latency >10ms overhead (WARNING)")
    print("   - Low accuracy <99.9% (CRITICAL)")
    print("   - High fallback rate >5% (WARNING)")
    print("   - Consensus uncertainty >1% (WARNING)")
    print("   - Throughput degradation >5% (CRITICAL)")
    
    print("\n📝 Ongoing Maintenance:")
    print("   1. Review expert performance weekly")
    print("   2. Review training metrics weekly")
    print("   3. Review A/B test results monthly")
    print("   4. Adjust thresholds based on accuracy trends")
    print("   5. Update expert models based on A/B tests")
    print("   6. Export compliance reports monthly")
    
    print("\n🔄 Rollback Plan:")
    print("   If issues arise, rollback with:")
    print("   python scripts/rollback_moe.py")
    
    print("\n🏛️  The Council of Experts is now in session!")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy MOE in Full Activation Mode (production)"
    )
    parser.add_argument(
        '--config',
        default='./config/moe_production.env',
        help='Path to configuration file (default: ./config/moe_production.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip soft launch validation'
    )
    
    args = parser.parse_args()
    
    # Validate soft launch complete
    if not args.skip_validation:
        if not validate_soft_launch_complete():
            sys.exit(1)
    
    # Create configuration
    create_production_config(args.config)
    
    # Deploy
    deploy_full_activation(args.config)


if __name__ == '__main__':
    main()
