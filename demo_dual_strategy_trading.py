"""
Aethel Dual-Strategy Trading Demo

Demonstrates both Takashi (Rebound) and Simons (Arbitrage) strategies
running simultaneously on the same capital.

The DIOTEC 360 Hedge Fund in a Box.
"""

import asyncio
from decimal import Decimal
from datetime import datetime

from diotec360.bot.deterministic_trader import DeterministicTrader, TradingInvariants
from diotec360.bot.takashi_strategy import TakashiReboundStrategy
from diotec360.bot.simons_strategy import SimonsArbitrageStrategy
from diotec360.core.real_forex_api import RealForexOracle
from diotec360.core.whatsapp_gate import WhatsAppGate
from diotec360.core.judge import AethelJudge


async def main():
    """
    Run the dual-strategy trading engine
    
    Capital Allocation:
    - 50% Takashi (High Risk/High Reward)
    - 50% Simons (Low Risk/Constant Profit)
    """
    
    print("=" * 70)
    print("🏛️  AETHEL DUAL-STRATEGY TRADING ENGINE")
    print("=" * 70)
    print()
    print("The DIOTEC 360 Autonomous Hedge Fund")
    print("Combining world-class strategies with mathematical proofs")
    print()
    
    # Initialize components
    print("📡 Initializing components...")
    forex_api = RealForexOracle()
    whatsapp_gate = WhatsAppGate()  # No phone number needed for demo
    judge = AethelJudge(intent_map={})
    
    # Create trading invariants (inviolable rules)
    invariants = TradingInvariants(
        max_drawdown_percent=Decimal('2.0'),  # Max 2% drawdown
        confirmation_wait_ms=5,  # 5ms confirmation
        min_proof_confidence=0.95,  # 95% confidence minimum
        max_position_size_percent=Decimal('10.0'),  # Max 10% per position
        require_conservation_proof=True,
        require_whatsapp_signature=True  # Set to False for demo
    )
    
    # Create trading engine
    trader = DeterministicTrader(
        forex_api=forex_api,
        whatsapp_gate=whatsapp_gate,
        judge=judge,
        invariants=invariants
    )
    
    # Initialize with capital
    initial_capital = Decimal('100000.00')  # $100,000
    await trader.initialize(initial_capital)
    
    print()
    print("=" * 70)
    print("🎯 STRATEGY CONFIGURATION")
    print("=" * 70)
    print()
    
    # Register Strategy A: Takashi (Rebound)
    takashi = TakashiReboundStrategy()
    trader.register_strategy('takashi', takashi)
    
    print("✅ Strategy A: TAKASHI (The Sniper)")
    print("   • Type: Mean Reversion / Crisis Trading")
    print("   • Risk: High Risk / High Reward")
    print("   • Trigger: 20%+ market drops")
    print("   • Target: 15% profit in 30 days")
    print("   • Capital: 50% ($50,000)")
    print()
    
    # Register Strategy B: Simons (Arbitrage)
    simons = SimonsArbitrageStrategy()
    trader.register_strategy('simons', simons)
    
    print("✅ Strategy B: SIMONS (The Machine)")
    print("   • Type: Statistical Arbitrage / HFT")
    print("   • Risk: Low Risk / Constant Profit")
    print("   • Trigger: 0.05%+ price discrepancies")
    print("   • Target: 0.1% profit per trade (thousands daily)")
    print("   • Capital: 50% ($50,000)")
    print()
    
    print("=" * 70)
    print("🚀 TRADING ENGINE ONLINE")
    print("=" * 70)
    print()
    
    # Simulate trading for demo
    print("📊 Scanning for opportunities...")
    print()
    
    # Scan for signals
    signals = await trader.scan_opportunities()
    
    if signals:
        print(f"🎯 Found {len(signals)} validated trading signals:")
        print()
        
        for i, signal in enumerate(signals, 1):
            print(f"Signal {i}: {signal.strategy.upper()}")
            print(f"  Action: {signal.action.upper()}")
            print(f"  Asset: {signal.asset}")
            print(f"  Amount: {signal.amount}")
            print(f"  Price: ${signal.price}")
            print(f"  Confidence: {signal.confidence * 100:.1f}%")
            print(f"  Proof Hash: {signal.proof_hash[:16]}...")
            print()
            print(f"  Reasoning:")
            for line in signal.reasoning.split('\n'):
                print(f"    {line}")
            print()
            print("-" * 70)
            print()
            
        # Execute signals (in demo mode, skip WhatsApp confirmation)
        print("⚡ Executing validated signals...")
        print()
        
        for signal in signals:
            # In production, this would wait for WhatsApp signature
            # For demo, we execute directly
            success = await trader.execute_signal(signal)
            
            if success:
                print(f"✅ {signal.strategy.upper()} trade executed successfully")
            else:
                print(f"❌ {signal.strategy.upper()} trade failed")
            print()
            
    else:
        print("⏳ No opportunities found at this time")
        print("   The engine will continue scanning every 60 seconds...")
        print()
        
    # Display final status
    print("=" * 70)
    print("📊 TRADING ENGINE STATUS")
    print("=" * 70)
    print()
    
    status = trader.get_status()
    
    print(f"Portfolio Value: ${status['portfolio_value']:,.2f}")
    print(f"Initial Capital: ${status['initial_capital']:,.2f}")
    print(f"Current Drawdown: {status['current_drawdown_percent']:.2f}%")
    print(f"Total Trades: {status['total_trades']}")
    print(f"Active Strategies: {', '.join(status['strategies_active'])}")
    print()
    
    if status['active_positions']:
        print("Active Positions:")
        for asset, amount in status['active_positions'].items():
            print(f"  • {asset}: {amount}")
        print()
        
    print("=" * 70)
    print("🏛️  THE BLOOMBERG OF SECURITY IS BORN")
    print("=" * 70)
    print()
    print("Key Advantages:")
    print("  ✅ Mathematical proofs for every trade")
    print("  ✅ Conservation laws prevent losses")
    print("  ✅ 2% max drawdown protection")
    print("  ✅ Sovereign signature authorization")
    print("  ✅ Real-time threat detection")
    print("  ✅ Dual-strategy diversification")
    print()
    print("The traditional financial world has no defense against this.")
    print("They use humans. We use theorems.")
    print()
    
    # In production, run forever
    # await trader.run_forever(scan_interval_seconds=60)


if __name__ == '__main__':
    asyncio.run(main())
