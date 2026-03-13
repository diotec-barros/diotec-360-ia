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
Unit tests for MOE Infrastructure - Base Classes and Interfaces

Author: Kiro AI - Engenheiro-Chefe
Date: February 13, 2026
Version: v2.1.0
"""

import pytest
import time
import tempfile
import os
from pathlib import Path

from diotec360.moe.base_expert import BaseExpert
from diotec360.moe.data_models import ExpertVerdict, MOEResult
from diotec360.moe.telemetry import ExpertTelemetry


class MockExpert(BaseExpert):
    """Mock expert for testing BaseExpert interface."""
    
    def verify(self, intent: str, tx_id: str) -> ExpertVerdict:
        """Mock verification that always approves."""
        start_time = time.time()
        time.sleep(0.01)
        latency_ms = (time.time() - start_time) * 1000
        
        self.record_verification(latency_ms)
        
        return ExpertVerdict(
            expert_name=self.name,
            verdict="APPROVE",
            confidence=0.95,
            latency_ms=latency_ms,
            reason=None,
            proof_trace=None
        )


class TestBaseExpert:
    """Unit tests for BaseExpert abstract class."""
    
    def test_initialization(self):
        """Test BaseExpert initialization."""
        expert = MockExpert("test_expert")
        
        assert expert.name == "test_expert"
        assert expert.total_verifications == 0
        assert expert.total_latency_ms == 0.0
        assert len(expert.accuracy_history) == 0
        assert expert.get_average_latency() == 0.0
        assert expert.get_accuracy() == 1.0
    
    def test_verify(self):
        """Test BaseExpert verify method."""
        expert = MockExpert("test_expert")
        verdict = expert.verify("transfer(100)", "tx_001")
        
        assert verdict.expert_name == "test_expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 0.95
        assert verdict.latency_ms > 0
        assert expert.total_verifications == 1
    
    def test_latency_tracking(self):
        """Test latency tracking across multiple verifications."""
        expert = MockExpert("test_expert")
        
        for i in range(5):
            expert.verify(f"transfer({i})", f"tx_{i:03d}")
        
        assert expert.total_verifications == 5
        assert expert.total_latency_ms > 0
        assert expert.get_average_latency() > 0
    
    def test_accuracy_tracking(self):
        """Test accuracy tracking with ground truth."""
        expert = MockExpert("test_expert")
        
        expert.update_accuracy(True)
        expert.update_accuracy(True)
        expert.update_accuracy(False)
        expert.update_accuracy(True)
        
        assert len(expert.accuracy_history) == 4
        assert expert.get_accuracy() == 0.75
    
    def test_accuracy_rolling_window(self):
        """Test accuracy rolling window (max 1000 entries)."""
        expert = MockExpert("test_expert")
        
        for i in range(1500):
            expert.update_accuracy(i % 2 == 0)
        
        assert len(expert.accuracy_history) == 1000
        assert 0.4 < expert.get_accuracy() < 0.6
    
    def test_get_stats(self):
        """Test get_stats method."""
        expert = MockExpert("test_expert")
        
        expert.verify("transfer(100)", "tx_001")
        expert.verify("transfer(200)", "tx_002")
        expert.update_accuracy(True)
        expert.update_accuracy(True)
        
        stats = expert.get_stats()
        
        assert stats['name'] == "test_expert"
        assert stats['total_verifications'] == 2
        assert stats['average_latency_ms'] > 0
        assert stats['accuracy'] == 1.0
        assert stats['accuracy_sample_size'] == 2


class TestExpertVerdict:
    """Unit tests for ExpertVerdict data structure."""
    
    def test_creation(self):
        """Test ExpertVerdict creation."""
        verdict = ExpertVerdict(
            expert_name="Z3_Expert",
            verdict="APPROVE",
            confidence=0.98,
            latency_ms=25.5,
            reason=None,
            proof_trace={"steps": 10}
        )
        
        assert verdict.expert_name == "Z3_Expert"
        assert verdict.verdict == "APPROVE"
        assert verdict.confidence == 0.98
        assert verdict.latency_ms == 25.5
    
    def test_to_dict(self):
        """Test ExpertVerdict to_dict conversion."""
        verdict = ExpertVerdict(
            expert_name="Sentinel_Expert",
            verdict="REJECT",
            confidence=0.95,
            latency_ms=15.2,
            reason="Overflow detected",
            proof_trace=None
        )
        
        verdict_dict = verdict.to_dict()
        
        assert verdict_dict['expert_name'] == "Sentinel_Expert"
        assert verdict_dict['verdict'] == "REJECT"
        assert verdict_dict['confidence'] == 0.95
    
    def test_json_serialization(self):
        """Test ExpertVerdict JSON serialization."""
        verdict = ExpertVerdict(
            expert_name="Guardian_Expert",
            verdict="APPROVE",
            confidence=1.0,
            latency_ms=10.0,
            reason=None,
            proof_trace={"conservation": "verified"}
        )
        
        json_str = verdict.to_json()
        assert isinstance(json_str, str)
        
        verdict_restored = ExpertVerdict.from_json(json_str)
        
        assert verdict_restored.expert_name == verdict.expert_name
        assert verdict_restored.verdict == verdict.verdict
        assert verdict_restored.confidence == verdict.confidence


class TestMOEResult:
    """Unit tests for MOEResult data structure."""
    
    def test_creation(self):
        """Test MOEResult creation."""
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 15.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 10.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_001",
            consensus="APPROVED",
            overall_confidence=0.976,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        )
        
        assert result.transaction_id == "tx_001"
        assert result.consensus == "APPROVED"
        assert len(result.expert_verdicts) == 3
    
    def test_get_expert_verdict(self):
        """Test getting specific expert verdict from MOEResult."""
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 15.0, reason="Attack detected"),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 10.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_002",
            consensus="REJECTED",
            overall_confidence=0.95,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        )
        
        sentinel_verdict = result.get_expert_verdict("Sentinel_Expert")
        assert sentinel_verdict is not None
        assert sentinel_verdict.verdict == "REJECT"
        
        missing_verdict = result.get_expert_verdict("NonExistent_Expert")
        assert missing_verdict is None
    
    def test_get_approval_rate(self):
        """Test approval rate calculation."""
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 15.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 10.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_003",
            consensus="REJECTED",
            overall_confidence=0.95,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        )
        
        approval_rate = result.get_approval_rate()
        assert approval_rate == 2.0 / 3.0
    
    def test_get_rejection_reasons(self):
        """Test getting rejection reasons."""
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 15.0, reason="Overflow detected"),
            ExpertVerdict("Guardian_Expert", "REJECT", 1.0, 10.0, reason="Conservation violated")
        ]
        
        result = MOEResult(
            transaction_id="tx_004",
            consensus="REJECTED",
            overall_confidence=0.95,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        )
        
        reasons = result.get_rejection_reasons()
        assert len(reasons) == 2
        assert "Sentinel_Expert: Overflow detected" in reasons


class TestExpertTelemetry:
    """Unit tests for ExpertTelemetry system."""
    
    @pytest.fixture
    def temp_telemetry_db(self):
        """Create temporary telemetry database for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_telemetry.db")
            yield db_path
    
    def test_initialization(self, temp_telemetry_db):
        """Test ExpertTelemetry initialization."""
        telemetry = ExpertTelemetry(temp_telemetry_db)
        
        assert telemetry.db_path == Path(temp_telemetry_db)
        assert telemetry.db_path.parent.exists()
    
    def test_record_verdict(self, temp_telemetry_db):
        """Test recording expert verdicts."""
        telemetry = ExpertTelemetry(temp_telemetry_db)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 15.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_001",
            consensus="APPROVED",
            overall_confidence=0.965,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert"]
        )
        
        telemetry.record("tx_001", verdicts, result)
    
    def test_get_expert_stats(self, temp_telemetry_db):
        """Test getting expert statistics."""
        telemetry = ExpertTelemetry(temp_telemetry_db)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 15.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_001",
            consensus="APPROVED",
            overall_confidence=0.965,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert"]
        )
        
        telemetry.record("tx_001", verdicts, result)
        
        stats = telemetry.get_expert_stats("Z3_Expert", time_window_seconds=3600)
        
        assert stats['expert_name'] == "Z3_Expert"
        assert stats['total_verifications'] == 1
        assert stats['average_latency_ms'] == 25.0
    
    def test_record_ground_truth(self, temp_telemetry_db):
        """Test recording ground truth for accuracy tracking."""
        telemetry = ExpertTelemetry(temp_telemetry_db)
        
        telemetry.record_ground_truth("tx_001", "Z3_Expert", True)
        telemetry.record_ground_truth("tx_002", "Z3_Expert", True)
        telemetry.record_ground_truth("tx_003", "Z3_Expert", False)
        
        for i in range(3):
            verdicts = [ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0)]
            result = MOEResult(
                transaction_id=f"tx_{i:03d}",
                consensus="APPROVED",
                overall_confidence=0.98,
                expert_verdicts=verdicts,
                total_latency_ms=25.0,
                activated_experts=["Z3_Expert"]
            )
            telemetry.record(f"tx_{i:03d}", verdicts, result)
        
        stats = telemetry.get_expert_stats("Z3_Expert", time_window_seconds=3600)
        
        assert stats['accuracy'] is not None
        assert stats['accuracy'] == 2.0 / 3.0
    
    def test_export_prometheus(self, temp_telemetry_db):
        """Test Prometheus metrics export."""
        telemetry = ExpertTelemetry(temp_telemetry_db)
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 25.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 15.0)
        ]
        
        result = MOEResult(
            transaction_id="tx_001",
            consensus="APPROVED",
            overall_confidence=0.965,
            expert_verdicts=verdicts,
            total_latency_ms=25.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert"]
        )
        
        telemetry.record("tx_001", verdicts, result)
        
        prometheus_output = telemetry.export_prometheus()
        
        assert isinstance(prometheus_output, str)
        assert "moe_expert_latency_ms" in prometheus_output
        assert "Z3_Expert" in prometheus_output
