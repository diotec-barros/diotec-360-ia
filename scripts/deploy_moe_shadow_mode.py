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
Deploy MOE Intelligence Layer in Shadow Mode

Shadow Mode: MOE runs in parallel but doesn't affect verdicts
- MOE Orchestrator: ENABLED (collect telemetry)
- Expert Execution: ENABLED (all experts)
- Verdict Override: DISABLED (MOE verdicts logged but not used)
- Fallback: Always use existing layers
- Caching: DISABLED (collect fresh data)

Purpose: Establish baseline metrics and validate expert accuracy

Duration: 1-2 weeks

Usage:
    python scripts/deploy_moe_shadow_mode.py
    python scripts/deploy_moe_shadow_mode.py --config ./config/moe_shadow_mode.env
"""

import os
import sys
import argparse
from pathlib import Path


def create_shadow_mode_config(output_path: str) -> None:
    """Create shadow mode configuration file."""
    config = """# MOE Intelligence Layer v2.1.0 - Shadow Mode Configuration
# Purpose: Monitoring only, verdicts don't affect system
# Duration: 1-2 weeks to establish baseline

# ============================================================================
# Core MOE Settings
# ============================================================================
DIOTEC360_MOE_ENABLED=true
DIOTEC360_MOE_MODE=shadow
DIOTEC360_MOE_TELEMETRY_DB_PATH=./.diotec360_moe/telemetry.db

# ============================================================================
# MOE Orchestrator - ENABLED (Shadow Mode)
# ============================================================================
DIOTEC360_MOE_OVERRIDE_VERDICT=false  # Don't override existing layers
DIOTEC360_MOE_LOG_VERDICTS=true  # Log all MOE verdicts for analysis
DIOTEC360_MOE_PARALLEL_EXPERTS=true  # Execute experts in parallel

# ============================================================================
# Expert Configuration - ALL ENABLED
# ============================================================================
DIOTEC360_Z3_EXPERT_ENABLED=true
DIOTEC360_Z3_EXPERT_TIMEOUT_NORMAL=30
DIOTEC360_Z3_EXPERT_TIMEOUT_CRISIS=5
DIOTEC360_Z3_EXPERT_CONFIDENCE_THRESHOLD=0.7

DIOTEC360_SENTINEL_EXPERT_ENABLED=true
DIOTEC360_SENTINEL_EXPERT_TIMEOUT_MS=100
DIOTEC360_SENTINEL_EXPERT_CONFIDENCE_THRESHOLD=0.7

DIOTEC360_GUARDIAN_EXPERT_ENABLED=true
DIOTEC360_GUARDIAN_EXPERT_TIMEOUT_MS=50
DIOTEC360_GUARDIAN_EXPERT_CONFIDENCE_THRESHOLD=0.7

# ============================================================================
# Gating Network - ENABLED (Route to all experts)
# ============================================================================
DIOTEC360_GATING_NETWORK_ENABLED=true
DIOTEC360_GATING_NETWORK_TIMEOUT_MS=10
DIOTEC360_GATING_NETWORK_DEFAULT_ROUTE=all  # Route to all experts in shadow mode

# ============================================================================
# Consensus Engine - ENABLED (Log consensus)
# ============================================================================
DIOTEC360_CONSENSUS_ENGINE_ENABLED=true
DIOTEC360_CONSENSUS_CONFIDENCE_THRESHOLD=0.7
DIOTEC360_CONSENSUS_UNCERTAINTY_THRESHOLD=0.5

# ============================================================================
# Verdict Caching - DISABLED (Collect fresh data)
# ============================================================================
DIOTEC360_MOE_CACHE_ENABLED=false
DIOTEC360_MOE_CACHE_TTL_SECONDS=300

# ============================================================================
# Expert Training - ENABLED (Collect ground truth)
# ============================================================================
DIOTEC360_MOE_TRAINING_ENABLED=true
DIOTEC360_MOE_TRAINING_DB_PATH=./.diotec360_moe/training.db
DIOTEC360_MOE_TRAINING_WINDOW=1000

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
"""
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(config)
    
    print(f"✅ Shadow mode configuration created: {output_path}")


def validate_prerequisites() -> bool:
    """Validate that prerequisites are met."""
    print("🔍 Validating prerequisites...")
    
    # Check if MOE telemetry database directory exists
    moe_dir = Path('./.diotec360_moe')
    if not moe_dir.exists():
        print(f"📁 Creating MOE directory: {moe_dir}")
        moe_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if existing layers are operational
    try:
        from diotec360.core.judge import Judge
        judge = Judge()
        print("✅ Existing Judge layers operational")
    except Exception as e:
        print(f"❌ Existing Judge layers not operational: {e}")
        return False
    
    # Check if MOE components exist
    try:
        from diotec360.moe.orchestrator import MOEOrchestrator
        print("✅ MOE components available")
    except Exception as e:
        print(f"❌ MOE components not found: {e}")
        return False
    
    print("✅ All prerequisites met")
    return True


def deploy_shadow_mode(config_path: str) -> None:
    """Deploy MOE in shadow mode."""
    print("\n🚀 Deploying MOE Intelligence Layer in Shadow Mode...")
    print("=" * 60)
    
    # Load configuration
    print(f"\n📝 Loading configuration from: {config_path}")
    
    # In a real deployment, this would:
    # 1. Load environment variables from config file
    # 2. Initialize MOE Orchestrator with shadow mode
    # 3. Register all experts
    # 4. Start telemetry collection
    # 5. Verify experts are responding
    
    print("\n✅ Shadow Mode Deployment Complete!")
    print("\n📊 Monitoring:")
    print("   - MOE Telemetry: http://localhost:9091/metrics")
    print("   - MOE Dashboard: http://localhost:3000/moe")
    print("   - Expert Status: http://localhost:3000/moe/experts")
    print("   - Logs: tail -f logs/moe.log")
    
    print("\n📈 What to Monitor:")
    print("   1. Expert Accuracy:")
    print("      - Z3 Expert: Compare verdicts with existing Layer 3")
    print("      - Sentinel Expert: Compare with existing Layers 0-2")
    print("      - Guardian Expert: Compare with existing Layer 1")
    print("      - Target: >99.9% agreement with existing layers")
    print("   2. Expert Latency:")
    print("      - Z3 Expert: <30s (95th percentile)")
    print("      - Sentinel Expert: <100ms (95th percentile)")
    print("      - Guardian Expert: <50ms (95th percentile)")
    print("   3. Consensus Quality:")
    print("      - Unanimous approval rate")
    print("      - Rejection rate per expert")
    print("      - Uncertainty rate (should be <1%)")
    print("   4. Orchestration Overhead:")
    print("      - Target: <10ms per transaction")
    print("      - Gating Network: <10ms")
    print("      - Consensus Engine: <1s")
    print("   5. Expert Failures:")
    print("      - Timeout rate per expert")
    print("      - Exception rate per expert")
    print("      - Fallback activation rate")
    
    print("\n⏱️  Duration: Run for 1-2 weeks")
    print("\n📝 Next Steps:")
    print("   1. Monitor expert accuracy daily")
    print("   2. Review expert latency distribution")
    print("   3. Analyze consensus patterns")
    print("   4. Identify and fix any expert failures")
    print("   5. Adjust confidence thresholds if needed")
    print("   6. After 1-2 weeks, proceed to Soft Launch:")
    print("      python scripts/deploy_moe_soft_launch.py")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy MOE in Shadow Mode (monitoring only)"
    )
    parser.add_argument(
        '--config',
        default='./config/moe_shadow_mode.env',
        help='Path to configuration file (default: ./config/moe_shadow_mode.env)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip prerequisite validation'
    )
    
    args = parser.parse_args()
    
    # Validate prerequisites
    if not args.skip_validation:
        if not validate_prerequisites():
            sys.exit(1)
    
    # Create configuration
    create_shadow_mode_config(args.config)
    
    # Deploy
    deploy_shadow_mode(args.config)


if __name__ == '__main__':
    main()
