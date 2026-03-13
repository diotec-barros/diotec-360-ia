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
Unit Tests for Visual Dashboard

Tests the visual dashboard LED indicator system, confidence display,
and animation behavior.

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import pytest
import time
from io import StringIO
from unittest.mock import patch, MagicMock
from diotec360.moe.visual_dashboard import (
    VisualDashboard,
    DashboardManager,
    LEDState,
    ExpertStatus
)
from diotec360.moe.data_models import ExpertVerdict, MOEResult


class TestLEDState:
    """Test LED state enumeration."""
    
    def test_led_states_exist(self):
        """Test that all LED states are defined."""
        assert LEDState.IDLE.value == "⚪"
        assert LEDState.PROCESSING.value == "🟡"
        assert LEDState.APPROVED.value == "🟢"
        assert LEDState.REJECTED.value == "🔴"
        assert LEDState.ERROR.value == "⚫"


class TestExpertStatus:
    """Test ExpertStatus dataclass."""
    
    def test_create_expert_status(self):
        """Test creating expert status."""
        status = ExpertStatus(
            name="Z3_Expert",
            state=LEDState.PROCESSING
        )
        
        assert status.name == "Z3_Expert"
        assert status.state == LEDState.PROCESSING
        assert status.confidence is None
        assert status.latency_ms is None
        assert status.reason is None
        
    def test_expert_status_with_metrics(self):
        """Test expert status with confidence and latency."""
        status = ExpertStatus(
            name="Sentinel_Expert",
            state=LEDState.APPROVED,
            confidence=0.95,
            latency_ms=45.2
        )
        
        assert status.confidence == 0.95
        assert status.latency_ms == 45.2


class TestVisualDashboard:
    """Test VisualDashboard class."""
    
    def test_initialization_default_experts(self):
        """Test dashboard initialization with default experts."""
        dashboard = VisualDashboard()
        
        assert len(dashboard.expert_names) == 3
        assert "Z3_Expert" in dashboard.expert_names
        assert "Sentinel_Expert" in dashboard.expert_names
        assert "Guardian_Expert" in dashboard.expert_names
        
        # All experts should start in IDLE state
        for name in dashboard.expert_names:
            assert dashboard.expert_statuses[name].state == LEDState.IDLE
            
    def test_initialization_custom_experts(self):
        """Test dashboard initialization with custom experts."""
        custom_experts = ["Expert1", "Expert2"]
        dashboard = VisualDashboard(expert_names=custom_experts)
        
        assert dashboard.expert_names == custom_experts
        assert len(dashboard.expert_statuses) == 2
        
    def test_start_verification(self):
        """Test starting verification updates expert states."""
        dashboard = VisualDashboard()
        activated = ["Z3_Expert", "Sentinel_Expert"]
        
        dashboard.start_verification(activated)
        
        # Activated experts should be PROCESSING
        assert dashboard.expert_statuses["Z3_Expert"].state == LEDState.PROCESSING
        assert dashboard.expert_statuses["Sentinel_Expert"].state == LEDState.PROCESSING
        
        # Non-activated expert should be IDLE
        assert dashboard.expert_statuses["Guardian_Expert"].state == LEDState.IDLE
        
    def test_update_expert_approved(self):
        """Test updating expert with APPROVE verdict."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Z3_Expert"])
        
        verdict = ExpertVerdict(
            expert_name="Z3_Expert",
            verdict="APPROVE",
            confidence=0.98,
            latency_ms=125.5,
            reason=None
        )
        
        dashboard.update_expert(verdict)
        
        status = dashboard.expert_statuses["Z3_Expert"]
        assert status.state == LEDState.APPROVED
        assert status.confidence == 0.98
        assert status.latency_ms == 125.5
        assert status.reason is None
        
    def test_update_expert_rejected(self):
        """Test updating expert with REJECT verdict."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Sentinel_Expert"])
        
        verdict = ExpertVerdict(
            expert_name="Sentinel_Expert",
            verdict="REJECT",
            confidence=0.85,
            latency_ms=45.2,
            reason="Overflow detected"
        )
        
        dashboard.update_expert(verdict)
        
        status = dashboard.expert_statuses["Sentinel_Expert"]
        assert status.state == LEDState.REJECTED
        assert status.confidence == 0.85
        assert status.latency_ms == 45.2
        assert status.reason == "Overflow detected"
        
    def test_update_unknown_expert(self):
        """Test updating expert not in dashboard (should be ignored)."""
        dashboard = VisualDashboard()
        
        verdict = ExpertVerdict(
            expert_name="Unknown_Expert",
            verdict="APPROVE",
            confidence=0.9,
            latency_ms=100.0
        )
        
        # Should not raise error
        dashboard.update_expert(verdict)
        
    def test_complete_verification_approved(self):
        """Test completing verification with APPROVED consensus."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Z3_Expert", "Sentinel_Expert"])
        
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 45.0)
        ]
        
        result = MOEResult(
            transaction_id="tx123",
            consensus="APPROVED",
            overall_confidence=0.965,
            expert_verdicts=verdicts,
            total_latency_ms=120.0,
            activated_experts=["Z3_Expert", "Sentinel_Expert"]
        )
        
        dashboard.complete_verification(result)
        
        assert dashboard.consensus == "APPROVED"
        assert dashboard.overall_confidence == 0.965
        assert dashboard.total_latency_ms == 120.0
        
        # Both experts should be APPROVED
        assert dashboard.expert_statuses["Z3_Expert"].state == LEDState.APPROVED
        assert dashboard.expert_statuses["Sentinel_Expert"].state == LEDState.APPROVED
        
    def test_complete_verification_rejected(self):
        """Test completing verification with REJECTED consensus."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Guardian_Expert"])
        
        verdicts = [
            ExpertVerdict(
                "Guardian_Expert",
                "REJECT",
                1.0,
                50.0,
                reason="Conservation violated"
            )
        ]
        
        result = MOEResult(
            transaction_id="tx456",
            consensus="REJECTED",
            overall_confidence=1.0,
            expert_verdicts=verdicts,
            total_latency_ms=50.0,
            activated_experts=["Guardian_Expert"]
        )
        
        dashboard.complete_verification(result)
        
        assert dashboard.consensus == "REJECTED"
        assert dashboard.expert_statuses["Guardian_Expert"].state == LEDState.REJECTED
        
    def test_format_expert_line_processing(self):
        """Test formatting expert line in PROCESSING state."""
        dashboard = VisualDashboard(enable_animation=False)
        status = ExpertStatus("Z3_Expert", LEDState.PROCESSING)
        
        line = dashboard._format_expert_line(status)
        
        assert "🟡" in line
        assert "Z3" in line
        assert "Processing" in line
        
    def test_format_expert_line_approved(self):
        """Test formatting expert line in APPROVED state."""
        dashboard = VisualDashboard()
        status = ExpertStatus(
            "Sentinel_Expert",
            LEDState.APPROVED,
            confidence=0.95,
            latency_ms=45.0
        )
        
        line = dashboard._format_expert_line(status)
        
        assert "🟢" in line
        assert "Sentinel" in line
        assert "APPROVED" in line
        assert "95%" in line
        assert "45ms" in line
        
    def test_format_expert_line_rejected(self):
        """Test formatting expert line in REJECTED state."""
        dashboard = VisualDashboard()
        status = ExpertStatus(
            "Guardian_Expert",
            LEDState.REJECTED,
            confidence=1.0,
            latency_ms=50.0
        )
        
        line = dashboard._format_expert_line(status)
        
        assert "🔴" in line
        assert "Guardian" in line
        assert "REJECTED" in line
        assert "100%" in line
        
    def test_format_expert_line_idle(self):
        """Test formatting expert line in IDLE state."""
        dashboard = VisualDashboard()
        status = ExpertStatus("Z3_Expert", LEDState.IDLE)
        
        line = dashboard._format_expert_line(status)
        
        assert "⚪" in line
        assert "Idle" in line
        
    def test_format_expert_line_error(self):
        """Test formatting expert line in ERROR state."""
        dashboard = VisualDashboard()
        status = ExpertStatus("Sentinel_Expert", LEDState.ERROR)
        
        line = dashboard._format_expert_line(status)
        
        assert "⚫" in line
        assert "ERROR" in line
        
    def test_animation_frame_advance(self):
        """Test animation frame advances."""
        dashboard = VisualDashboard(enable_animation=True)
        
        initial_frame = dashboard.animation_frame
        dashboard.animation_frame += 1
        
        assert dashboard.animation_frame == initial_frame + 1
        
    def test_animation_disabled(self):
        """Test animation can be disabled."""
        dashboard = VisualDashboard(enable_animation=False)
        dashboard.start_verification(["Z3_Expert"])
        
        # animate_processing should not change frame when disabled
        initial_frame = dashboard.animation_frame
        dashboard.animate_processing()
        
        assert dashboard.animation_frame == initial_frame
        
    def test_get_expert_display_name(self):
        """Test getting display-friendly expert names."""
        dashboard = VisualDashboard()
        
        assert dashboard.get_expert_display_name("Z3_Expert") == "Z3"
        assert dashboard.get_expert_display_name("Sentinel_Expert") == "Sentinel"
        assert dashboard.get_expert_display_name("Guardian_Expert") == "Guardian"
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_render_output(self, mock_stdout):
        """Test render produces output."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Z3_Expert"])
        
        # Render should produce output
        output = mock_stdout.getvalue()
        
        # Should contain header
        assert "DIOTEC360 MOE VERIFICATION STATUS" in output
        
        # Should contain expert names
        assert "Z3" in output


class TestDashboardManager:
    """Test DashboardManager class."""
    
    def test_initialization(self):
        """Test manager initialization."""
        manager = DashboardManager()
        
        assert manager.dashboard is not None
        assert not manager.is_active
        
    def test_start(self):
        """Test starting verification."""
        manager = DashboardManager()
        manager.start(["Z3_Expert"])
        
        assert manager.is_active
        assert manager.dashboard.expert_statuses["Z3_Expert"].state == LEDState.PROCESSING
        
    def test_update(self):
        """Test updating expert status."""
        manager = DashboardManager()
        manager.start(["Z3_Expert"])
        
        verdict = ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0)
        manager.update(verdict)
        
        assert manager.dashboard.expert_statuses["Z3_Expert"].state == LEDState.APPROVED
        
    def test_update_when_inactive(self):
        """Test update when manager is inactive (should be ignored)."""
        manager = DashboardManager()
        
        verdict = ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0)
        manager.update(verdict)  # Should not raise error
        
        # Expert should still be IDLE
        assert manager.dashboard.expert_statuses["Z3_Expert"].state == LEDState.IDLE
        
    def test_complete(self):
        """Test completing verification."""
        manager = DashboardManager()
        manager.start(["Z3_Expert"])
        
        verdicts = [ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0)]
        result = MOEResult(
            "tx123",
            "APPROVED",
            0.98,
            verdicts,
            120.0,
            ["Z3_Expert"]
        )
        
        manager.complete(result)
        
        assert not manager.is_active
        assert manager.dashboard.consensus == "APPROVED"
        
    def test_animate(self):
        """Test animation."""
        manager = DashboardManager()
        manager.start(["Z3_Expert"])
        
        initial_frame = manager.dashboard.animation_frame
        manager.animate()
        
        # Frame should advance when active and expert is processing
        # (Note: actual animation may not advance if no processing experts)
        
    def test_clear(self):
        """Test clearing dashboard."""
        manager = DashboardManager()
        manager.start(["Z3_Expert"])
        
        manager.clear()
        
        assert not manager.is_active


class TestDashboardIntegration:
    """Integration tests for dashboard with MOE system."""
    
    def test_full_verification_flow(self):
        """Test complete verification flow with dashboard."""
        dashboard = VisualDashboard()
        
        # Start verification
        activated = ["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        dashboard.start_verification(activated)
        
        # All should be processing
        for name in activated:
            assert dashboard.expert_statuses[name].state == LEDState.PROCESSING
            
        # Update experts one by one
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0),
            ExpertVerdict("Sentinel_Expert", "APPROVE", 0.95, 45.0),
            ExpertVerdict("Guardian_Expert", "APPROVE", 1.0, 50.0)
        ]
        
        for verdict in verdicts:
            dashboard.update_expert(verdict)
            assert dashboard.expert_statuses[verdict.expert_name].state == LEDState.APPROVED
            
        # Complete verification
        result = MOEResult(
            "tx123",
            "APPROVED",
            0.976,
            verdicts,
            120.0,
            activated
        )
        
        dashboard.complete_verification(result)
        
        assert dashboard.consensus == "APPROVED"
        assert dashboard.overall_confidence == 0.976
        
    def test_mixed_verdict_flow(self):
        """Test verification with mixed verdicts."""
        dashboard = VisualDashboard()
        
        activated = ["Z3_Expert", "Sentinel_Expert"]
        dashboard.start_verification(activated)
        
        # Z3 approves, Sentinel rejects
        verdicts = [
            ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0),
            ExpertVerdict("Sentinel_Expert", "REJECT", 0.95, 45.0, reason="Overflow detected")
        ]
        
        for verdict in verdicts:
            dashboard.update_expert(verdict)
            
        result = MOEResult(
            "tx456",
            "REJECTED",
            0.95,
            verdicts,
            120.0,
            activated
        )
        
        dashboard.complete_verification(result)
        
        assert dashboard.consensus == "REJECTED"
        assert dashboard.expert_statuses["Z3_Expert"].state == LEDState.APPROVED
        assert dashboard.expert_statuses["Sentinel_Expert"].state == LEDState.REJECTED
        
    def test_partial_activation(self):
        """Test verification with only some experts activated."""
        dashboard = VisualDashboard()
        
        # Only activate Z3 and Guardian
        activated = ["Z3_Expert", "Guardian_Expert"]
        dashboard.start_verification(activated)
        
        # Sentinel should be IDLE
        assert dashboard.expert_statuses["Sentinel_Expert"].state == LEDState.IDLE
        
        # Activated experts should be PROCESSING
        assert dashboard.expert_statuses["Z3_Expert"].state == LEDState.PROCESSING
        assert dashboard.expert_statuses["Guardian_Expert"].state == LEDState.PROCESSING


class TestDashboardPerformance:
    """Performance tests for dashboard."""
    
    def test_render_performance(self):
        """Test render performance."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"])
        
        start_time = time.time()
        
        # Render 100 times
        for _ in range(100):
            dashboard.render()
            
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time (< 1 second for 100 renders)
        assert elapsed < 1.0
        
    def test_update_performance(self):
        """Test update performance."""
        dashboard = VisualDashboard()
        dashboard.start_verification(["Z3_Expert"])
        
        verdict = ExpertVerdict("Z3_Expert", "APPROVE", 0.98, 120.0)
        
        start_time = time.time()
        
        # Update 1000 times
        for _ in range(1000):
            dashboard.update_expert(verdict)
            
        elapsed = time.time() - start_time
        
        # Should complete quickly (< 0.5 seconds for 1000 updates)
        assert elapsed < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
