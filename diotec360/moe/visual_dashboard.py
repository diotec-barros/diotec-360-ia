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
Visual Dashboard - Real-time MOE Expert Status Display

Provides console-based visual indicators for MOE expert status:
- LED indicators for each expert (Z3, Sentinel, Guardian)
- Real-time status updates (processing, approved, rejected)
- Confidence scores and latency display
- Animated parallel processing indicators

Author: Kiro AI - Engenheiro-Chefe
Date: February 15, 2026
Version: v2.1.0
"""

import time
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from .data_models import ExpertVerdict, MOEResult


class LEDState(Enum):
    """LED indicator states with color codes."""
    IDLE = "⚪"  # White - Not activated
    PROCESSING = "🟡"  # Yellow - Processing
    APPROVED = "🟢"  # Green - Approved
    REJECTED = "🔴"  # Red - Rejected
    ERROR = "⚫"  # Black - Error/Failure


@dataclass
class ExpertStatus:
    """
    Status information for a single expert.
    
    Attributes:
        name: Expert name
        state: Current LED state
        confidence: Confidence score (0.0-1.0), None if not complete
        latency_ms: Latency in milliseconds, None if not complete
        reason: Rejection reason, None if approved or processing
    """
    name: str
    state: LEDState
    confidence: Optional[float] = None
    latency_ms: Optional[float] = None
    reason: Optional[str] = None


class VisualDashboard:
    """
    Console-based visual dashboard for MOE expert status.
    
    Displays real-time LED indicators showing expert verification progress:
    - Yellow (🟡) = Processing
    - Green (🟢) = Approved
    - Red (🔴) = Rejected
    - White (⚪) = Idle/Not activated
    - Black (⚫) = Error
    
    Also displays confidence scores, latency, and overall consensus.
    """
    
    def __init__(
        self,
        expert_names: List[str] = None,
        enable_animation: bool = True,
        animation_speed: float = 0.1
    ):
        """
        Initialize visual dashboard.
        
        Args:
            expert_names: List of expert names to display (default: Z3, Sentinel, Guardian)
            enable_animation: Enable animated processing indicators (default True)
            animation_speed: Animation frame delay in seconds (default 0.1)
        """
        if expert_names is None:
            expert_names = ["Z3_Expert", "Sentinel_Expert", "Guardian_Expert"]
        
        self.expert_names = expert_names
        self.enable_animation = enable_animation
        self.animation_speed = animation_speed
        
        # Initialize expert statuses
        self.expert_statuses: Dict[str, ExpertStatus] = {
            name: ExpertStatus(name=name, state=LEDState.IDLE)
            for name in expert_names
        }
        
        # Overall status
        self.overall_confidence: Optional[float] = None
        self.total_latency_ms: Optional[float] = None
        self.consensus: Optional[str] = None
        
        # Animation state
        self.animation_frame = 0
        self.animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
    def start_verification(self, activated_experts: List[str]) -> None:
        """
        Mark verification as started for specified experts.
        
        Args:
            activated_experts: List of expert names that will be activated
        """
        # Reset all statuses
        for name in self.expert_names:
            if name in activated_experts:
                self.expert_statuses[name].state = LEDState.PROCESSING
                self.expert_statuses[name].confidence = None
                self.expert_statuses[name].latency_ms = None
                self.expert_statuses[name].reason = None
            else:
                self.expert_statuses[name].state = LEDState.IDLE
        
        # Reset overall status
        self.overall_confidence = None
        self.total_latency_ms = None
        self.consensus = None
        
        # Display initial state
        self.render()
        
    def update_expert(self, verdict: ExpertVerdict) -> None:
        """
        Update expert status with verdict.
        
        Args:
            verdict: ExpertVerdict from completed expert
        """
        if verdict.expert_name not in self.expert_statuses:
            return
        
        status = self.expert_statuses[verdict.expert_name]
        
        # Update state based on verdict
        if verdict.verdict == "APPROVE":
            status.state = LEDState.APPROVED
        elif verdict.verdict == "REJECT":
            status.state = LEDState.REJECTED
        else:
            status.state = LEDState.ERROR
        
        # Update metrics
        status.confidence = verdict.confidence
        status.latency_ms = verdict.latency_ms
        status.reason = verdict.reason
        
        # Re-render dashboard
        self.render()
        
    def complete_verification(self, result: MOEResult) -> None:
        """
        Mark verification as complete with final result.
        
        Args:
            result: Final MOEResult with consensus
        """
        # Update all expert statuses from result
        for verdict in result.expert_verdicts:
            self.update_expert(verdict)
        
        # Update overall status
        self.overall_confidence = result.overall_confidence
        self.total_latency_ms = result.total_latency_ms
        self.consensus = result.consensus
        
        # Final render
        self.render()
        
    def render(self) -> None:
        """
        Render the dashboard to console.
        
        Displays:
        - Header with title
        - LED indicators for each expert
        - Confidence scores and latency
        - Overall consensus and confidence
        """
        # Clear previous output (move cursor up and clear lines)
        if hasattr(self, '_last_line_count'):
            for _ in range(self._last_line_count):
                sys.stdout.write('\033[F')  # Move cursor up
                sys.stdout.write('\033[K')  # Clear line
        
        lines = []
        
        # Header
        lines.append("┌─────────────────────────────────────────────────────────┐")
        lines.append("│  AETHEL MOE VERIFICATION STATUS                         │")
        lines.append("├─────────────────────────────────────────────────────────┤")
        
        # Expert status lines
        for name in self.expert_names:
            status = self.expert_statuses[name]
            line = self._format_expert_line(status)
            lines.append(line)
        
        lines.append("├─────────────────────────────────────────────────────────┤")
        
        # Overall status
        if self.overall_confidence is not None:
            confidence_pct = self.overall_confidence * 100
            lines.append(f"│  Overall Confidence: {confidence_pct:5.1f}%                        │")
        else:
            lines.append("│  Overall Confidence: ---%                               │")
        
        if self.total_latency_ms is not None:
            lines.append(f"│  Total Time: {self.total_latency_ms:6.1f} ms                              │")
        else:
            lines.append("│  Total Time: -- ms                                      │")
        
        # Consensus result
        if self.consensus is not None:
            if self.consensus == "APPROVED":
                lines.append("│                                                         │")
                lines.append("│  ✅ TRANSACTION APPROVED                                │")
            elif self.consensus == "REJECTED":
                lines.append("│                                                         │")
                lines.append("│  ❌ TRANSACTION REJECTED                                │")
            else:  # UNCERTAIN
                lines.append("│                                                         │")
                lines.append("│  ⚠️  UNCERTAIN - HUMAN REVIEW REQUIRED                  │")
        
        lines.append("└─────────────────────────────────────────────────────────┘")
        
        # Print all lines
        output = "\n".join(lines)
        print(output, flush=True)
        
        # Store line count for next render
        self._last_line_count = len(lines)
        
    def _format_expert_line(self, status: ExpertStatus) -> str:
        """
        Format a single expert status line.
        
        Args:
            status: ExpertStatus to format
            
        Returns:
            Formatted line string
        """
        # LED indicator
        led = status.state.value
        
        # Expert name (shortened for display)
        display_name = status.name.replace("_Expert", "")
        
        # Status text
        if status.state == LEDState.PROCESSING:
            if self.enable_animation:
                spinner = self.animation_chars[self.animation_frame % len(self.animation_chars)]
                status_text = f"Processing... {spinner}"
            else:
                status_text = "Processing..."
        elif status.state == LEDState.APPROVED:
            confidence_pct = status.confidence * 100 if status.confidence else 0
            status_text = f"APPROVED ({confidence_pct:.0f}%)"
        elif status.state == LEDState.REJECTED:
            confidence_pct = status.confidence * 100 if status.confidence else 0
            status_text = f"REJECTED ({confidence_pct:.0f}%)"
        elif status.state == LEDState.ERROR:
            status_text = "ERROR"
        else:  # IDLE
            status_text = "Idle"
        
        # Latency
        if status.latency_ms is not None:
            latency_text = f"{status.latency_ms:.0f}ms"
        else:
            latency_text = ""
        
        # Format line with padding
        line = f"│  {led} {display_name:<16} {status_text:<20} {latency_text:>6} │"
        
        # Ensure line is exactly 59 characters (including borders)
        if len(line) < 59:
            line = line[:-2] + " " * (59 - len(line)) + " │"
        elif len(line) > 59:
            line = line[:57] + " │"
        
        return line
        
    def animate_processing(self) -> None:
        """
        Advance animation frame for processing indicators.
        
        Call this periodically while experts are processing to show animation.
        """
        if not self.enable_animation:
            return
        
        self.animation_frame += 1
        
        # Only re-render if any expert is processing
        has_processing = any(
            status.state == LEDState.PROCESSING
            for status in self.expert_statuses.values()
        )
        
        if has_processing:
            self.render()
            time.sleep(self.animation_speed)
            
    def clear(self) -> None:
        """
        Clear the dashboard display.
        """
        if hasattr(self, '_last_line_count'):
            for _ in range(self._last_line_count):
                sys.stdout.write('\033[F')  # Move cursor up
                sys.stdout.write('\033[K')  # Clear line
            self._last_line_count = 0
            
    def get_expert_display_name(self, expert_name: str) -> str:
        """
        Get display-friendly expert name.
        
        Args:
            expert_name: Full expert name
            
        Returns:
            Shortened display name
        """
        return expert_name.replace("_Expert", "")


class DashboardManager:
    """
    Manager for visual dashboard lifecycle.
    
    Provides high-level interface for dashboard operations:
    - Start/stop verification display
    - Update expert statuses
    - Handle animation
    """
    
    def __init__(self, expert_names: List[str] = None):
        """
        Initialize dashboard manager.
        
        Args:
            expert_names: List of expert names to display
        """
        self.dashboard = VisualDashboard(expert_names=expert_names)
        self.is_active = False
        
    def start(self, activated_experts: List[str]) -> None:
        """
        Start verification display.
        
        Args:
            activated_experts: List of experts that will be activated
        """
        self.is_active = True
        self.dashboard.start_verification(activated_experts)
        
    def update(self, verdict: ExpertVerdict) -> None:
        """
        Update expert status.
        
        Args:
            verdict: ExpertVerdict from completed expert
        """
        if self.is_active:
            self.dashboard.update_expert(verdict)
            
    def complete(self, result: MOEResult) -> None:
        """
        Complete verification display.
        
        Args:
            result: Final MOEResult
        """
        if self.is_active:
            self.dashboard.complete_verification(result)
            self.is_active = False
            
    def animate(self) -> None:
        """
        Advance animation frame.
        """
        if self.is_active:
            self.dashboard.animate_processing()
            
    def clear(self) -> None:
        """
        Clear dashboard display.
        """
        self.dashboard.clear()
        self.is_active = False
