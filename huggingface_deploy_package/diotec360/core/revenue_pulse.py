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
Aethel Revenue Pulse - The Heartbeat of the Empire
===================================================

Real-time revenue monitoring system that tracks every credit deduction
and displays the financial pulse of DIOTEC 360.

This is the "magic moment" - watching money flow into the vault in real-time
as the Aethel network processes verifications around the world.

Features:
- Real-time credit deduction tracking
- Revenue accumulation counter
- Transaction rate monitoring
- Visual pulse animation
- Revenue projections
- Milestone notifications

Author: Kiro AI - Chief Engineer
Version: v2.2.10 "Revenue Pulse"
Date: February 11, 2026
"""

import time
import threading
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from collections import deque

from diotec360.core.billing import BillingKernel, get_billing_kernel, OperationType


@dataclass
class PulseEvent:
    """Single revenue pulse event"""
    timestamp: datetime
    account_id: str
    operation_type: OperationType
    credits_charged: int
    revenue_usd: Decimal
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'account_id': self.account_id,
            'operation': self.operation_type.value,
            'credits': self.credits_charged,
            'revenue_usd': float(self.revenue_usd)
        }


@dataclass
class RevenueMetrics:
    """Real-time revenue metrics"""
    total_revenue_usd: Decimal = Decimal("0")
    total_transactions: int = 0
    transactions_per_second: float = 0.0
    revenue_per_second: Decimal = Decimal("0")
    
    # Time-based metrics
    last_minute_revenue: Decimal = Decimal("0")
    last_hour_revenue: Decimal = Decimal("0")
    last_day_revenue: Decimal = Decimal("0")
    
    # Projections
    projected_daily_revenue: Decimal = Decimal("0")
    projected_monthly_revenue: Decimal = Decimal("0")
    projected_annual_revenue: Decimal = Decimal("0")
    
    def to_dict(self) -> Dict:
        return {
            'total_revenue_usd': float(self.total_revenue_usd),
            'total_transactions': self.total_transactions,
            'transactions_per_second': self.transactions_per_second,
            'revenue_per_second': float(self.revenue_per_second),
            'last_minute_revenue': float(self.last_minute_revenue),
            'last_hour_revenue': float(self.last_hour_revenue),
            'last_day_revenue': float(self.last_day_revenue),
            'projections': {
                'daily': float(self.projected_daily_revenue),
                'monthly': float(self.projected_monthly_revenue),
                'annual': float(self.projected_annual_revenue)
            }
        }


class RevenuePulse:
    """
    Revenue Pulse Monitor
    
    Tracks every credit deduction in real-time and provides:
    - Live revenue counter
    - Transaction rate monitoring
    - Revenue projections
    - Milestone notifications
    - Visual pulse events
    
    This is the "heartbeat" of DIOTEC 360 - every pulse is money flowing in.
    """
    
    def __init__(self, credit_value_usd: Decimal = Decimal("0.10")):
        """
        Initialize Revenue Pulse
        
        Args:
            credit_value_usd: USD value per credit (default: $0.10)
        """
        self.billing = get_billing_kernel()
        self.credit_value_usd = credit_value_usd
        
        # Event tracking
        self.recent_events: deque = deque(maxlen=1000)  # Last 1000 events
        self.event_callbacks: List[Callable] = []
        
        # Metrics
        self.metrics = RevenueMetrics()
        
        # Time windows for rate calculation
        self.minute_window: deque = deque(maxlen=60)  # Last 60 seconds
        self.hour_window: deque = deque(maxlen=3600)  # Last hour
        self.day_window: deque = deque(maxlen=86400)  # Last 24 hours
        
        # Milestones
        self.milestones = [
            Decimal("100"),      # First $100
            Decimal("1000"),     # First $1k
            Decimal("10000"),    # First $10k
            Decimal("100000"),   # First $100k
            Decimal("1000000"),  # First $1M 🦄
        ]
        self.reached_milestones = set()
        
        # Monitoring thread
        self.monitoring = False
        self.monitor_thread = None
        
        print("[REVENUE_PULSE] Initialized")
        print(f"   • Credit value: ${self.credit_value_usd} USD")
        print("   • Real-time tracking: ENABLED")
        print("   • Milestone notifications: ENABLED")
    
    def record_transaction(
        self,
        account_id: str,
        operation_type: OperationType,
        credits_charged: int
    ) -> PulseEvent:
        """
        Record a revenue-generating transaction
        
        This is called automatically by the billing system whenever
        credits are deducted from an account.
        
        Args:
            account_id: Customer account ID
            operation_type: Type of operation
            credits_charged: Number of credits charged
        
        Returns:
            PulseEvent with transaction details
        """
        # Calculate revenue
        revenue_usd = Decimal(credits_charged) * self.credit_value_usd
        
        # Create pulse event
        event = PulseEvent(
            timestamp=datetime.now(),
            account_id=account_id,
            operation_type=operation_type,
            credits_charged=credits_charged,
            revenue_usd=revenue_usd
        )
        
        # Record event
        self.recent_events.append(event)
        self.minute_window.append(event)
        self.hour_window.append(event)
        self.day_window.append(event)
        
        # Update metrics
        self._update_metrics(event)
        
        # Check milestones
        self._check_milestones()
        
        # Trigger callbacks
        self._trigger_callbacks(event)
        
        return event
    
    def _update_metrics(self, event: PulseEvent):
        """Update real-time metrics"""
        # Total revenue
        self.metrics.total_revenue_usd += event.revenue_usd
        self.metrics.total_transactions += 1
        
        # Calculate rates
        now = datetime.now()
        
        # Last minute
        minute_ago = now - timedelta(minutes=1)
        minute_events = [e for e in self.minute_window if e.timestamp >= minute_ago]
        self.metrics.last_minute_revenue = sum(e.revenue_usd for e in minute_events)
        
        # Last hour
        hour_ago = now - timedelta(hours=1)
        hour_events = [e for e in self.hour_window if e.timestamp >= hour_ago]
        self.metrics.last_hour_revenue = sum(e.revenue_usd for e in hour_events)
        
        # Last day
        day_ago = now - timedelta(days=1)
        day_events = [e for e in self.day_window if e.timestamp >= day_ago]
        self.metrics.last_day_revenue = sum(e.revenue_usd for e in day_events)
        
        # Transactions per second
        if len(minute_events) > 0:
            self.metrics.transactions_per_second = len(minute_events) / 60.0
        
        # Revenue per second
        if len(minute_events) > 0:
            self.metrics.revenue_per_second = self.metrics.last_minute_revenue / Decimal("60")
        
        # Projections (based on last hour)
        if len(hour_events) > 0:
            hourly_rate = self.metrics.last_hour_revenue
            self.metrics.projected_daily_revenue = hourly_rate * Decimal("24")
            self.metrics.projected_monthly_revenue = hourly_rate * Decimal("24") * Decimal("30")
            self.metrics.projected_annual_revenue = hourly_rate * Decimal("24") * Decimal("365")
    
    def _check_milestones(self):
        """Check if any revenue milestones have been reached"""
        for milestone in self.milestones:
            if milestone not in self.reached_milestones:
                if self.metrics.total_revenue_usd >= milestone:
                    self.reached_milestones.add(milestone)
                    self._announce_milestone(milestone)
    
    def _announce_milestone(self, milestone: Decimal):
        """Announce milestone achievement"""
        print("\n" + "🎉" * 40)
        print(f"💰 MILESTONE REACHED: ${milestone:,.0f} USD!")
        print("🎉" * 40)
        
        # Special messages
        if milestone == Decimal("100"):
            print("🚀 First $100! The journey begins!")
        elif milestone == Decimal("1000"):
            print("💎 First $1,000! Validation achieved!")
        elif milestone == Decimal("10000"):
            print("🏆 First $10,000! Serious business!")
        elif milestone == Decimal("100000"):
            print("🦅 First $100,000! Enterprise scale!")
        elif milestone == Decimal("1000000"):
            print("🦄 FIRST $1 MILLION! UNICORN STATUS! 🦄")
            print("DIOTEC 360 IS NOW A MILLION-DOLLAR COMPANY!")
    
    def _trigger_callbacks(self, event: PulseEvent):
        """Trigger registered callbacks"""
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"[REVENUE_PULSE] Callback error: {e}")
    
    def register_callback(self, callback: Callable):
        """
        Register callback for pulse events
        
        Callback signature: callback(event: PulseEvent) -> None
        """
        self.event_callbacks.append(callback)
    
    def get_metrics(self) -> RevenueMetrics:
        """Get current revenue metrics"""
        return self.metrics
    
    def get_recent_events(self, limit: int = 10) -> List[PulseEvent]:
        """Get recent pulse events"""
        events = list(self.recent_events)
        return events[-limit:]
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("[REVENUE_PULSE] Monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        print("[REVENUE_PULSE] Monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            # Update metrics periodically
            if len(self.recent_events) > 0:
                last_event = self.recent_events[-1]
                self._update_metrics(last_event)
            
            time.sleep(1.0)
    
    def print_dashboard(self):
        """Print revenue dashboard to console"""
        metrics = self.get_metrics()
        
        print("\n" + "═" * 80)
        print("💰 DIOTEC 360 REVENUE PULSE - LIVE DASHBOARD")
        print("═" * 80)
        
        print(f"\n📊 TOTAL REVENUE: ${metrics.total_revenue_usd:,.2f} USD")
        print(f"📈 Total Transactions: {metrics.total_transactions:,}")
        
        print(f"\n⚡ REAL-TIME RATES:")
        print(f"   • Transactions/sec: {metrics.transactions_per_second:.2f}")
        print(f"   • Revenue/sec: ${metrics.revenue_per_second:.4f} USD")
        
        print(f"\n⏱️  TIME WINDOWS:")
        print(f"   • Last Minute: ${metrics.last_minute_revenue:.2f} USD")
        print(f"   • Last Hour: ${metrics.last_hour_revenue:.2f} USD")
        print(f"   • Last 24h: ${metrics.last_day_revenue:.2f} USD")
        
        print(f"\n🔮 PROJECTIONS (based on current rate):")
        print(f"   • Daily: ${metrics.projected_daily_revenue:,.2f} USD")
        print(f"   • Monthly: ${metrics.projected_monthly_revenue:,.2f} USD")
        print(f"   • Annual: ${metrics.projected_annual_revenue:,.2f} USD (ARR)")
        
        print(f"\n🏆 MILESTONES:")
        for milestone in self.milestones:
            status = "✅" if milestone in self.reached_milestones else "⏳"
            progress = min(100, (float(metrics.total_revenue_usd) / float(milestone)) * 100)
            print(f"   {status} ${milestone:,.0f}: {progress:.1f}%")
        
        print("\n" + "═" * 80)
        print("💰 Every pulse is money flowing into DIOTEC 360! 🚀")
        print("═" * 80 + "\n")


# Global instance
_pulse_instance = None

def get_revenue_pulse() -> RevenuePulse:
    """Get singleton instance of Revenue Pulse"""
    global _pulse_instance
    if _pulse_instance is None:
        _pulse_instance = RevenuePulse()
    return _pulse_instance


def initialize_revenue_pulse(credit_value_usd: Decimal = Decimal("0.10")) -> RevenuePulse:
    """Initialize Revenue Pulse with custom credit value"""
    global _pulse_instance
    _pulse_instance = RevenuePulse(credit_value_usd)
    return _pulse_instance


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("REVENUE PULSE - THE HEARTBEAT OF THE EMPIRE")
    print("=" * 80)
    
    pulse = get_revenue_pulse()
    
    # Register callback for visual pulse
    def pulse_callback(event: PulseEvent):
        print(f"💰 PULSE! +${event.revenue_usd:.2f} USD from {event.account_id[:12]}... "
              f"({event.operation_type.value})")
    
    pulse.register_callback(pulse_callback)
    
    # Simulate transactions
    print("\n🎬 Simulating revenue stream...")
    print("─" * 80)
    
    for i in range(20):
        # Simulate different operations
        operations = [
            (OperationType.PROOF_VERIFICATION, 1),
            (OperationType.CONSERVATION_ORACLE, 5),
            (OperationType.GHOST_IDENTITY, 20),
        ]
        
        op_type, credits = operations[i % len(operations)]
        
        pulse.record_transaction(
            account_id=f"ACC_{i:04d}",
            operation_type=op_type,
            credits_charged=credits
        )
        
        time.sleep(0.1)  # Simulate time between transactions
    
    # Show dashboard
    pulse.print_dashboard()
    
    # Show recent events
    print("\n📋 RECENT TRANSACTIONS:")
    print("─" * 80)
    for event in pulse.get_recent_events(5):
        print(f"   {event.timestamp.strftime('%H:%M:%S')} | "
              f"{event.account_id[:12]}... | "
              f"{event.operation_type.value:20s} | "
              f"+${event.revenue_usd:.2f} USD")
    
    print("\n" + "=" * 80)
    print("THE EMPIRE'S HEARTBEAT IS STRONG! 💰🏛️⚡")
    print("=" * 80)
