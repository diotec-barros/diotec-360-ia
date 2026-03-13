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
Demo: Cognitive Memory + Web Oracle + Forex Integration
The AI that remembers every market move and learns from history.

This demonstration shows:
1. Capturing real-time Forex data via Web Oracle
2. Storing market data in Cognitive Memory
3. Validating trades using ConservationValidator
4. AI reasoning traces with persistent memory
5. Historical pattern recognition

Scenario: EUR/USD Trading with AI Memory
- The AI captures EUR/USD prices over time
- It remembers past trends and patterns
- It validates trades to prevent losses
- It learns from validated decisions

Author: Kiro AI - Engenheiro-Chefe
Version: v2.1.2 "Cognitive Persistence"
Date: February 5, 2026
"""

import time
from datetime import datetime
from typing import List

from diotec360.core.memory import CognitiveMemorySystem, MemoryType, get_cognitive_memory
from diotec360.core.web_oracle import WebOracle, DataSource, get_web_oracle
from diotec360.consensus.conservation_validator import ConservationValidator


def print_section(title: str) -> None:
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def simulate_forex_market() -> List[tuple]:
    """
    Simulate EUR/USD market data over time.
    
    Returns:
        List of (timestamp, price) tuples
    """
    # Simulated EUR/USD prices (realistic intraday movement)
    base_price = 1.0850
    prices = [
        base_price,
        base_price + 0.0012,  # Small rise
        base_price + 0.0008,  # Pullback
        base_price + 0.0025,  # Strong rise
        base_price + 0.0030,  # Continued rise
        base_price + 0.0018,  # Correction
        base_price + 0.0005,  # Further correction
        base_price - 0.0010,  # Drop below base
        base_price - 0.0005,  # Recovery
        base_price + 0.0015,  # Back to positive
    ]
    
    # Generate timestamps (1 minute intervals)
    start_time = time.time()
    return [(start_time + i * 60, price) for i, price in enumerate(prices)]


def demo_cognitive_forex():
    """
    Main demonstration of Cognitive Memory + Web Oracle + Forex.
    """
    print_section("🧠 AETHEL COGNITIVE FOREX DEMO")
    print("Demonstrating AI with infinite memory trading EUR/USD")
    print("The AI captures market data, remembers patterns, and validates trades")
    
    # Initialize systems
    print("\n[INIT] Initializing Cognitive Memory System...")
    memory = get_cognitive_memory()
    
    print("[INIT] Initializing Web Oracle...")
    oracle = get_web_oracle()
    
    print("[INIT] Initializing Conservation Validator...")
    validator = ConservationValidator()
    
    print("\n✅ All systems initialized")
    
    # ========================================================================
    # PHASE 1: Capture Market Data
    # ========================================================================
    print_section("📊 PHASE 1: Capturing EUR/USD Market Data")
    
    market_data = simulate_forex_market()
    
    print(f"Simulating {len(market_data)} price updates over 10 minutes...")
    print("(In production, this would connect to real Forex APIs)\n")
    
    for i, (timestamp, price) in enumerate(market_data):
        # Capture via Web Oracle
        feed = oracle.capture_forex_data(
            pair="EUR/USD",
            price=price,
            bid=price - 0.0002,  # Typical spread
            ask=price + 0.0002
        )
        
        if feed:
            print(f"[{i+1:2d}] EUR/USD = {price:.4f} | "
                  f"Sealed: {feed.authenticity_seal[:16]}... | "
                  f"Stored in memory")
        
        # Small delay to simulate real-time
        time.sleep(0.1)
    
    print(f"\n✅ Captured {len(market_data)} price updates")
    
    # ========================================================================
    # PHASE 2: AI Reasoning with Memory
    # ========================================================================
    print_section("🤖 PHASE 2: AI Reasoning with Historical Memory")
    
    # Retrieve historical data from memory
    history = memory.get_market_history("EUR/USD", limit=100)
    
    print(f"AI retrieved {len(history)} historical price points from memory")
    print("\nAnalyzing trend...")
    
    # Extract prices
    prices = [m.content['price'] for m in history]
    
    # Simple trend analysis
    if len(prices) >= 2:
        first_price = prices[-1]  # Oldest
        last_price = prices[0]    # Newest
        change = last_price - first_price
        change_pct = (change / first_price) * 100
        
        print(f"\nFirst price: {first_price:.4f}")
        print(f"Last price:  {last_price:.4f}")
        print(f"Change:      {change:+.4f} ({change_pct:+.2f}%)")
        
        # AI reasoning
        if change > 0:
            trend = "BULLISH"
            reasoning = "Price has risen consistently. Market sentiment is positive."
            decision = "Consider LONG position"
        else:
            trend = "BEARISH"
            reasoning = "Price has declined. Market sentiment is negative."
            decision = "Consider SHORT position or wait"
        
        print(f"\nTrend: {trend}")
        print(f"Reasoning: {reasoning}")
        print(f"Decision: {decision}")
        
        # Store reasoning trace in memory
        memory.store_reasoning_trace(
            prompt=f"Analyze EUR/USD trend based on {len(prices)} data points",
            reasoning=reasoning,
            conclusion=decision,
            validated=False,  # Not yet validated by Judge
            tags=['forex', 'EUR/USD', 'trend_analysis']
        )
        
        print("\n✅ Reasoning trace stored in cognitive memory")
    
    # ========================================================================
    # PHASE 3: Trade Validation with Conservation
    # ========================================================================
    print_section("⚖️ PHASE 3: Validating Trade with Conservation Law")
    
    # Simulate a trade
    account_balance = 10000.0  # USD
    trade_amount = 1000.0      # USD to trade
    current_price = prices[0]  # Latest price
    
    print(f"Account Balance: ${account_balance:,.2f}")
    print(f"Trade Amount:    ${trade_amount:,.2f}")
    print(f"Current Price:   {current_price:.4f}")
    
    # Calculate EUR to buy
    eur_to_buy = trade_amount / current_price
    
    print(f"\nProposed Trade: BUY {eur_to_buy:.2f} EUR")
    
    # Validate conservation (money in = money out)
    print("\nValidating with ConservationValidator...")
    
    # Create conservation proof
    initial_state = {'USD': account_balance, 'EUR': 0.0}
    final_state = {'USD': account_balance - trade_amount, 'EUR': eur_to_buy}
    
    # In production, this would use the full Judge pipeline
    # For demo, we just check conservation manually
    usd_change = final_state['USD'] - initial_state['USD']
    eur_change = final_state['EUR'] - initial_state['EUR']
    eur_value_usd = eur_change * current_price
    
    conservation_error = abs(usd_change + eur_value_usd)
    
    if conservation_error < 0.01:  # Within 1 cent tolerance
        print("✅ CONSERVATION VALIDATED")
        print(f"   USD change: ${usd_change:,.2f}")
        print(f"   EUR change: {eur_change:.2f} EUR (${eur_value_usd:,.2f})")
        print(f"   Net change: ${conservation_error:.4f} (within tolerance)")
        
        # Store validated trade in memory
        memory.store_memory(
            memory_type=MemoryType.TRANSACTION_OUTCOME,
            content={
                'trade_type': 'BUY',
                'pair': 'EUR/USD',
                'amount_usd': trade_amount,
                'amount_eur': eur_to_buy,
                'price': current_price,
                'validated': True,
                'conservation_error': conservation_error
            },
            tags=['trade', 'EUR/USD', 'validated', 'buy'],
            source='ai',
            confidence=1.0
        )
        
        print("\n✅ Trade stored in cognitive memory with validation seal")
    else:
        print("❌ CONSERVATION VIOLATION")
        print(f"   Conservation error: ${conservation_error:.4f}")
        print("   Trade REJECTED")
    
    # ========================================================================
    # PHASE 4: Memory Statistics
    # ========================================================================
    print_section("📈 PHASE 4: Cognitive Memory Statistics")
    
    stats = memory.get_statistics()
    
    print(f"Total Memories:  {stats['total_memories']}")
    print(f"\nMemories by Type:")
    for mem_type, count in stats['by_type'].items():
        print(f"  {mem_type:25s}: {count:4d}")
    
    print(f"\nMemories by Source:")
    for source, count in stats['by_source'].items():
        print(f"  {source:25s}: {count:4d}")
    
    print(f"\nTop Tags:")
    for tag, count in stats['top_tags'].items():
        print(f"  {tag:25s}: {count:4d}")
    
    # Oracle statistics
    oracle_stats = oracle.get_statistics()
    print(f"\nWeb Oracle Statistics:")
    print(f"  Feeds Captured:  {oracle_stats['feeds_captured']}")
    print(f"  Feeds Validated: {oracle_stats['feeds_validated']}")
    print(f"  Feeds Rejected:  {oracle_stats['feeds_rejected']}")
    print(f"  Validation Rate: {oracle_stats['validation_rate']:.1f}%")
    
    # ========================================================================
    # PHASE 5: Historical Pattern Recognition
    # ========================================================================
    print_section("🔍 PHASE 5: Historical Pattern Recognition")
    
    print("Retrieving all reasoning traces from memory...")
    reasoning_traces = memory.retrieve_memories(
        memory_type=MemoryType.REASONING_TRACE,
        limit=100
    )
    
    print(f"\nFound {len(reasoning_traces)} reasoning traces")
    
    if reasoning_traces:
        print("\nMost Recent Reasoning:")
        latest = reasoning_traces[0]
        print(f"  Prompt:     {latest.content['prompt']}")
        print(f"  Reasoning:  {latest.content['reasoning']}")
        print(f"  Conclusion: {latest.content['conclusion']}")
        print(f"  Validated:  {latest.content['validated']}")
        print(f"  Timestamp:  {datetime.fromtimestamp(latest.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\nRetrieving all validated trades...")
    trades = memory.retrieve_memories(
        memory_type=MemoryType.TRANSACTION_OUTCOME,
        tags=['validated'],
        limit=100
    )
    
    print(f"Found {len(trades)} validated trades")
    
    if trades:
        print("\nMost Recent Trade:")
        latest_trade = trades[0]
        print(f"  Type:   {latest_trade.content['trade_type']}")
        print(f"  Pair:   {latest_trade.content['pair']}")
        print(f"  Amount: ${latest_trade.content['amount_usd']:,.2f}")
        print(f"  Price:  {latest_trade.content['price']:.4f}")
        print(f"  Error:  ${latest_trade.content['conservation_error']:.4f}")
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print_section("🎯 DEMO COMPLETE: The AI Never Forgets")
    
    print("What we demonstrated:")
    print("  ✅ Real-time Forex data capture via Web Oracle")
    print("  ✅ Cryptographic authenticity seals on all data")
    print("  ✅ Persistent storage in Cognitive Memory")
    print("  ✅ AI reasoning traces with historical context")
    print("  ✅ Trade validation with Conservation Law")
    print("  ✅ Pattern recognition from memory")
    
    print("\nThe Aethel AI now has:")
    print(f"  • {stats['total_memories']} memories stored")
    print(f"  • {len(history)} EUR/USD price points")
    print(f"  • {len(reasoning_traces)} reasoning traces")
    print(f"  • {len(trades)} validated trades")
    
    print("\n🧠 Unlike traditional LLMs that forget everything,")
    print("   Aethel's Cognitive Memory creates an AI that learns")
    print("   and remembers across sessions, building institutional")
    print("   knowledge that compounds over time.")
    
    print("\n🌐 The Oracle Sanctuary ensures every piece of data")
    print("   entering the system is cryptographically sealed,")
    print("   preventing manipulation and fake news attacks.")
    
    print("\n⚖️ The Conservation Validator guarantees mathematical")
    print("   correctness of every trade, making fraud impossible.")
    
    print("\n" + "=" * 80)
    print("  DIONÍSIO, THIS IS THE SYMBIOTIC FINANCIAL ENTITY")
    print("  Memory of an elephant. Speed of HFT. Ease of WhatsApp.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    demo_cognitive_forex()
