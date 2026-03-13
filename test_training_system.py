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
Unit Tests for Expert Training and Adaptation System

Tests:
- Ground truth collection
- Accuracy calculation
- Confidence threshold adjustment
- A/B testing framework
- Model version management
- Automatic model promotion

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import pytest
import time
import tempfile
import os
from pathlib import Path
from diotec360.moe.training import (
    ExpertTrainingSystem,
    ABTestingFramework,
    GroundTruthRecord,
    AccuracyMetrics,
    ExpertModelVersion
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def training_system(temp_db):
    """Create ExpertTrainingSystem instance for testing."""
    return ExpertTrainingSystem(temp_db)


@pytest.fixture
def ab_testing(training_system):
    """Create ABTestingFramework instance for testing."""
    return ABTestingFramework(training_system)


class TestGroundTruthCollection:
    """Test ground truth collection functionality."""
    
    def test_record_single_ground_truth(self, training_system):
        """Test recording a single ground truth record."""
        record = training_system.record_ground_truth(
            transaction_id="tx_001",
            expert_name="Z3_Expert",
            expert_verdict="APPROVE",
            expert_confidence=0.95,
            actual_outcome="APPROVE"
        )
        
        assert record.transaction_id == "tx_001"
        assert record.expert_name == "Z3_Expert"
        assert record.expert_verdict == "APPROVE"
        assert record.expert_confidence == 0.95
        assert record.actual_outcome == "APPROVE"
        assert record.was_correct is True
        assert record.timestamp > 0
    
    def test_record_incorrect_verdict(self, training_system):
        """Test recording incorrect expert verdict."""
        record = training_system.record_ground_truth(
            transaction_id="tx_002",
            expert_name="Sentinel_Expert",
            expert_verdict="APPROVE",
            expert_confidence=0.80,
            actual_outcome="REJECT"
        )
        
        assert record.was_correct is False
    
    def test_record_batch_ground_truth(self, training_system):
        """Test batch recording of ground truth."""
        records_data = [
            ("tx_001", "Z3_Expert", "APPROVE", 0.95, "APPROVE"),
            ("tx_002", "Z3_Expert", "REJECT", 0.90, "REJECT"),
            ("tx_003", "Z3_Expert", "APPROVE", 0.85, "REJECT"),
        ]
        
        records = training_system.record_batch_ground_truth(records_data)
        
        assert len(records) == 3
        assert records[0].was_correct is True
        assert records[1].was_correct is True
        assert records[2].was_correct is False
    
    def test_get_ground_truth_records(self, training_system):
        """Test retrieving ground truth records."""
        # Record some data
        training_system.record_ground_truth(
            "tx_001", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
        )
        training_system.record_ground_truth(
            "tx_002", "Sentinel_Expert", "REJECT", 0.90, "REJECT"
        )
        
        # Get all records
        all_records = training_system.get_ground_truth_records()
        assert len(all_records) == 2
        
        # Get records for specific expert
        z3_records = training_system.get_ground_truth_records(expert_name="Z3_Expert")
        assert len(z3_records) == 1
        assert z3_records[0].expert_name == "Z3_Expert"
    
    def test_get_ground_truth_count(self, training_system):
        """Test counting ground truth records."""
        # Record some data
        for i in range(5):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        for i in range(3):
            training_system.record_ground_truth(
                f"tx_{i+5:03d}", "Sentinel_Expert", "REJECT", 0.90, "REJECT"
            )
        
        # Count all records
        total_count = training_system.get_ground_truth_count()
        assert total_count == 8
        
        # Count for specific expert
        z3_count = training_system.get_ground_truth_count(expert_name="Z3_Expert")
        assert z3_count == 5
    
    def test_cleanup_old_ground_truth(self, training_system):
        """Test cleanup of old ground truth data."""
        # Record some data
        for i in range(10):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Cleanup with 0 days (should delete all)
        deleted = training_system.cleanup_old_ground_truth(days_to_keep=0)
        assert deleted == 10
        
        # Verify all deleted
        count = training_system.get_ground_truth_count()
        assert count == 0


class TestAccuracyCalculation:
    """Test accuracy calculation functionality."""
    
    def test_calculate_accuracy_perfect(self, training_system):
        """Test accuracy calculation with perfect accuracy."""
        # Record 100 correct verdicts
        for i in range(100):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        metrics = training_system.calculate_accuracy("Z3_Expert", window_size=100)
        
        assert metrics.expert_name == "Z3_Expert"
        assert metrics.window_size == 100
        assert metrics.accuracy == 1.0
        assert metrics.true_positives == 100
        assert metrics.false_positives == 0
        assert metrics.false_negatives == 0
    
    def test_calculate_accuracy_with_errors(self, training_system):
        """Test accuracy calculation with some errors."""
        # Record 90 correct, 10 incorrect
        for i in range(90):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        for i in range(10):
            training_system.record_ground_truth(
                f"tx_{i+90:03d}", "Z3_Expert", "APPROVE", 0.80, "REJECT"
            )
        
        metrics = training_system.calculate_accuracy("Z3_Expert", window_size=100)
        
        assert metrics.accuracy == 0.90
        assert metrics.true_positives == 90
        assert metrics.false_positives == 10
    
    def test_calculate_accuracy_confusion_matrix(self, training_system):
        """Test confusion matrix calculation."""
        # True positives: 40
        for i in range(40):
            training_system.record_ground_truth(
                f"tx_tp_{i:03d}", "Guardian_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # True negatives: 30
        for i in range(30):
            training_system.record_ground_truth(
                f"tx_tn_{i:03d}", "Guardian_Expert", "REJECT", 0.90, "REJECT"
            )
        
        # False positives: 20
        for i in range(20):
            training_system.record_ground_truth(
                f"tx_fp_{i:03d}", "Guardian_Expert", "APPROVE", 0.70, "REJECT"
            )
        
        # False negatives: 10
        for i in range(10):
            training_system.record_ground_truth(
                f"tx_fn_{i:03d}", "Guardian_Expert", "REJECT", 0.85, "APPROVE"
            )
        
        metrics = training_system.calculate_accuracy("Guardian_Expert", window_size=100)
        
        assert metrics.true_positives == 40
        assert metrics.true_negatives == 30
        assert metrics.false_positives == 20
        assert metrics.false_negatives == 10
        assert metrics.accuracy == 0.70  # (40 + 30) / 100
        
        # Check precision and recall
        expected_precision = 40 / (40 + 20)  # TP / (TP + FP) = 0.667
        expected_recall = 40 / (40 + 10)     # TP / (TP + FN) = 0.80
        
        assert abs(metrics.precision - expected_precision) < 0.01
        assert abs(metrics.recall - expected_recall) < 0.01
    
    def test_calculate_accuracy_no_data(self, training_system):
        """Test accuracy calculation with no data."""
        metrics = training_system.calculate_accuracy("NonExistent_Expert", window_size=100)
        
        assert metrics.window_size == 0
        assert metrics.accuracy == 0.0
        assert metrics.true_positives == 0
    
    def test_calculate_accuracy_confidence_tracking(self, training_system):
        """Test tracking of confidence for correct vs incorrect verdicts."""
        # Correct verdicts with high confidence
        for i in range(50):
            training_system.record_ground_truth(
                f"tx_correct_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Incorrect verdicts with lower confidence
        for i in range(50):
            training_system.record_ground_truth(
                f"tx_incorrect_{i:03d}", "Z3_Expert", "APPROVE", 0.65, "REJECT"
            )
        
        metrics = training_system.calculate_accuracy("Z3_Expert", window_size=100)
        
        assert metrics.avg_confidence_correct == 0.95
        assert metrics.avg_confidence_incorrect == 0.65


class TestConfidenceThresholdAdjustment:
    """Test confidence threshold adjustment functionality."""
    
    def test_adjust_threshold_high_accuracy(self, training_system):
        """Test threshold adjustment when accuracy is high."""
        # Record perfect accuracy
        for i in range(100):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Adjust threshold (accuracy = 1.0, target = 0.999)
        new_threshold = training_system.adjust_confidence_threshold(
            "Z3_Expert",
            current_threshold=0.7,
            target_accuracy=0.999,
            window_size=100
        )
        
        # Should lower threshold since accuracy is above target
        assert new_threshold < 0.7
    
    def test_adjust_threshold_low_accuracy(self, training_system):
        """Test threshold adjustment when accuracy is low."""
        # Record 80% accuracy
        for i in range(80):
            training_system.record_ground_truth(
                f"tx_correct_{i:03d}", "Sentinel_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        for i in range(20):
            training_system.record_ground_truth(
                f"tx_incorrect_{i:03d}", "Sentinel_Expert", "APPROVE", 0.70, "REJECT"
            )
        
        # Adjust threshold (accuracy = 0.80, target = 0.999)
        new_threshold = training_system.adjust_confidence_threshold(
            "Sentinel_Expert",
            current_threshold=0.7,
            target_accuracy=0.999,
            window_size=100
        )
        
        # Should raise threshold since accuracy is below target
        assert new_threshold > 0.7
    
    def test_adjust_threshold_insufficient_data(self, training_system):
        """Test threshold adjustment with insufficient data."""
        # Record only 50 samples (less than minimum 100)
        for i in range(50):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Should keep current threshold
        new_threshold = training_system.adjust_confidence_threshold(
            "Z3_Expert",
            current_threshold=0.7,
            target_accuracy=0.999,
            window_size=100
        )
        
        assert new_threshold == 0.7
    
    def test_adjust_threshold_clamping(self, training_system):
        """Test that threshold is clamped to valid range."""
        # Record perfect accuracy
        for i in range(100):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Try to adjust from very high threshold
        new_threshold = training_system.adjust_confidence_threshold(
            "Z3_Expert",
            current_threshold=0.95,
            target_accuracy=0.999,
            window_size=100
        )
        
        # Should be clamped to maximum 1.0
        assert new_threshold <= 1.0
        assert new_threshold >= 0.5
    
    def test_get_threshold_history(self, training_system):
        """Test retrieving threshold adjustment history."""
        # Record some data
        for i in range(100):
            training_system.record_ground_truth(
                f"tx_{i:03d}", "Z3_Expert", "APPROVE", 0.95, "APPROVE"
            )
        
        # Adjust threshold multiple times
        training_system.adjust_confidence_threshold("Z3_Expert", 0.7, 0.999, 100)
        training_system.adjust_confidence_threshold("Z3_Expert", 0.65, 0.999, 100)
        
        # Get history
        history = training_system.get_threshold_history("Z3_Expert", limit=10)
        
        assert len(history) == 2
        assert 'timestamp' in history[0]
        assert 'old_threshold' in history[0]
        assert 'new_threshold' in history[0]
        assert 'reason' in history[0]


class TestABTestingFramework:
    """Test A/B testing framework functionality."""
    
    def test_register_model_version(self, ab_testing):
        """Test registering a new model version."""
        model_config = {
            'timeout': 30,
            'confidence_threshold': 0.7
        }
        
        version = ab_testing.register_model_version(
            expert_name="Z3_Expert",
            model_version="v2.0",
            model_config=model_config,
            ab_test_group="B"
        )
        
        assert version.expert_name == "Z3_Expert"
        assert version.model_version == "v2.0"
        assert version.model_config == model_config
        assert version.ab_test_group == "B"
        assert version.is_active is False
    
    def test_activate_model_version(self, ab_testing):
        """Test activating a model version."""
        # Register two versions
        ab_testing.register_model_version(
            "Z3_Expert", "v1.0", {'timeout': 30}, "A"
        )
        ab_testing.register_model_version(
            "Z3_Expert", "v2.0", {'timeout': 25}, "B"
        )
        
        # Activate v2.0
        ab_testing.activate_model_version("Z3_Expert", "v2.0")
        
        # Check active version
        active = ab_testing.get_active_model_version("Z3_Expert")
        assert active is not None
        assert active.model_version == "v2.0"
        assert active.is_active is True
    
    def test_get_active_model_version_none(self, ab_testing):
        """Test getting active version when none exists."""
        active = ab_testing.get_active_model_version("NonExistent_Expert")
        assert active is None
    
    def test_get_all_model_versions(self, ab_testing):
        """Test retrieving all model versions."""
        # Register multiple versions
        ab_testing.register_model_version("Z3_Expert", "v1.0", {}, "A")
        ab_testing.register_model_version("Z3_Expert", "v2.0", {}, "B")
        ab_testing.register_model_version("Z3_Expert", "v3.0", {}, "C")
        
        versions = ab_testing.get_all_model_versions("Z3_Expert")
        
        assert len(versions) == 3
        assert all(v.expert_name == "Z3_Expert" for v in versions)
    
    def test_compare_model_versions(self, ab_testing, training_system):
        """Test comparing two model versions."""
        # Register versions
        ab_testing.register_model_version("Z3_Expert", "v1.0", {}, "A")
        ab_testing.register_model_version("Z3_Expert", "v2.0", {}, "B")
        
        # Record ground truth for v1.0 (90% accuracy)
        for i in range(90):
            training_system.record_ground_truth(
                f"tx_v1_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(10):
            training_system.record_ground_truth(
                f"tx_v1_err_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.80, "REJECT"
            )
        
        # Record ground truth for v2.0 (95% accuracy)
        for i in range(95):
            training_system.record_ground_truth(
                f"tx_v2_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(5):
            training_system.record_ground_truth(
                f"tx_v2_err_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.80, "REJECT"
            )
        
        # Compare versions
        comparison = ab_testing.compare_model_versions(
            "Z3_Expert", "v1.0", "v2.0", window_size=100
        )
        
        assert comparison['expert_name'] == "Z3_Expert"
        assert comparison['winner'] == "v2.0"
        assert abs(comparison['accuracy_improvement'] - 0.05) < 0.001
    
    def test_auto_promote_better_model(self, ab_testing, training_system):
        """Test automatic promotion of better model."""
        # Register versions
        ab_testing.register_model_version("Z3_Expert", "v1.0", {}, "A")
        ab_testing.register_model_version("Z3_Expert", "v2.0", {}, "B")
        
        # Activate v1.0
        ab_testing.activate_model_version("Z3_Expert", "v1.0")
        
        # Record ground truth showing v2.0 is better
        for i in range(90):
            training_system.record_ground_truth(
                f"tx_v1_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(10):
            training_system.record_ground_truth(
                f"tx_v1_err_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.80, "REJECT"
            )
        
        for i in range(95):
            training_system.record_ground_truth(
                f"tx_v2_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(5):
            training_system.record_ground_truth(
                f"tx_v2_err_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.80, "REJECT"
            )
        
        # Auto-promote (min_improvement = 0.001, actual = 0.05)
        promoted = ab_testing.auto_promote_better_model(
            "Z3_Expert", "v1.0", "v2.0", window_size=100, min_improvement=0.001
        )
        
        assert promoted == "v2.0"
        
        # Verify v2.0 is now active
        active = ab_testing.get_active_model_version("Z3_Expert")
        assert active.model_version == "v2.0"
    
    def test_auto_promote_insufficient_improvement(self, ab_testing, training_system):
        """Test that promotion doesn't happen with insufficient improvement."""
        # Register versions
        ab_testing.register_model_version("Z3_Expert", "v1.0", {}, "A")
        ab_testing.register_model_version("Z3_Expert", "v2.0", {}, "B")
        
        # Activate v1.0
        ab_testing.activate_model_version("Z3_Expert", "v1.0")
        
        # Record ground truth showing minimal difference
        for i in range(95):
            training_system.record_ground_truth(
                f"tx_v1_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(5):
            training_system.record_ground_truth(
                f"tx_v1_err_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.80, "REJECT"
            )
        
        for i in range(96):
            training_system.record_ground_truth(
                f"tx_v2_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.95, "APPROVE"
            )
        for i in range(4):
            training_system.record_ground_truth(
                f"tx_v2_err_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.80, "REJECT"
            )
        
        # Auto-promote with high min_improvement threshold
        promoted = ab_testing.auto_promote_better_model(
            "Z3_Expert", "v1.0", "v2.0", window_size=100, min_improvement=0.05
        )
        
        # Should not promote (improvement is only 0.01)
        assert promoted is None
        
        # Verify v1.0 is still active
        active = ab_testing.get_active_model_version("Z3_Expert")
        assert active.model_version == "v1.0"


class TestIntegration:
    """Integration tests for training system."""
    
    def test_complete_training_workflow(self, training_system, ab_testing):
        """Test complete training and adaptation workflow."""
        # Step 1: Register model versions
        ab_testing.register_model_version("Z3_Expert", "v1.0", {'timeout': 30}, "A")
        ab_testing.register_model_version("Z3_Expert", "v2.0", {'timeout': 25}, "B")
        ab_testing.activate_model_version("Z3_Expert", "v1.0")
        
        # Step 2: Collect ground truth for both versions
        for i in range(100):
            outcome = "APPROVE" if i < 90 else "REJECT"
            training_system.record_ground_truth(
                f"tx_v1_{i:03d}", "Z3_Expert_v1.0", "APPROVE", 0.95, outcome
            )
        
        for i in range(100):
            outcome = "APPROVE" if i < 96 else "REJECT"
            training_system.record_ground_truth(
                f"tx_v2_{i:03d}", "Z3_Expert_v2.0", "APPROVE", 0.95, outcome
            )
        
        # Step 3: Calculate accuracy
        metrics_v1 = training_system.calculate_accuracy("Z3_Expert_v1.0", 100)
        metrics_v2 = training_system.calculate_accuracy("Z3_Expert_v2.0", 100)
        
        assert metrics_v1.accuracy == 0.90
        assert metrics_v2.accuracy == 0.96
        
        # Step 4: Adjust confidence thresholds
        new_threshold_v1 = training_system.adjust_confidence_threshold(
            "Z3_Expert_v1.0", 0.7, 0.999, 100
        )
        new_threshold_v2 = training_system.adjust_confidence_threshold(
            "Z3_Expert_v2.0", 0.7, 0.999, 100
        )
        
        # v1 should have higher threshold (lower accuracy)
        # v2 should have lower threshold (higher accuracy)
        assert new_threshold_v1 > new_threshold_v2
        
        # Step 5: Auto-promote better model
        promoted = ab_testing.auto_promote_better_model(
            "Z3_Expert", "v1.0", "v2.0", 100, 0.01
        )
        
        assert promoted == "v2.0"
        
        # Step 6: Verify promotion
        active = ab_testing.get_active_model_version("Z3_Expert")
        assert active.model_version == "v2.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
