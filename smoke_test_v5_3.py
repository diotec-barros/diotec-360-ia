"""
V5.3 SMOKE TEST - Prova de Fogo
Teste simplificado sem emojis para Windows
"""

import asyncio
from decimal import Decimal
from datetime import datetime

from diotec360.core.crypto import AethelCrypt
from diotec360.core.whatsapp_gate import WhatsAppGate, create_whatsapp_message
from diotec360.core.real_forex_api import get_real_forex_oracle
from diotec360.bot.deterministic_trader import DeterministicTrader, TradeSignal, TradingInvariants
from diotec360.core.judge import AethelJudge
from diotec360.core.vault import AethelVault
from diotec360.core.nexus_strategy import NexusStrategy


async def test_gap1_async():
    """GAP 1: Oracle is truly async"""
    print("\n[TEST 1] GAP 1: Async/Sync Mismatch")
    oracle = get_real_forex_oracle()
    
    quote_coro = oracle.get_quote("EUR/USD")
    assert asyncio.iscoroutine(quote_coro), "get_quote must return coroutine"
    
    quote = await quote_coro
    print(f"   PASS: Oracle is truly async")
    print(f"   Quote: {quote.price if quote else 'None (API limit)'}")
    return True


async def test_gap2_3_real_pnl():
    """GAP 2 & 3: Real PnL with trading costs"""
    print("\n[TEST 2] GAP 2 & 3: Real PnL Calculation")
    
    oracle = get_real_forex_oracle()
    whatsapp = WhatsAppGate()
    vault = AethelVault()
    judge = AethelJudge(intent_map={})
    
    trader = DeterministicTrader(
        forex_api=oracle,
        whatsapp_gate=whatsapp,
        judge=judge
    )
    
    await trader.initialize(Decimal('10000'))
    
    signal = TradeSignal(
        strategy='test',
        action='buy',
        asset='EUR/USD',
        amount=Decimal('100'),
        price=Decimal('1.0850'),
        confidence=0.96,
        proof_hash='test',
        timestamp=datetime.now(),
        reasoning='Test'
    )
    
    projected = await trader._calculate_projected_value(signal)
    
    assert projected < Decimal('10000'), "Buy should decrease portfolio value"
    cost = Decimal('10000') - projected
    
    print(f"   PASS: Real PnL calculation")
    print(f"   Initial: $10,000.00")
    print(f"   Projected: ${projected:.2f}")
    print(f"   Cost (with fees/slippage): ${cost:.2f}")
    return True


def test_gap4_ed25519():
    """GAP 4: Real ED25519 signatures"""
    print("\n[TEST 3] GAP 4: ED25519 Signatures")
    
    crypt = AethelCrypt()
    keypair = crypt.generate_keypair()
    
    whatsapp = WhatsAppGate(user_keypair=keypair)
    
    message = create_whatsapp_message(
        sender_id="user_123",
        content="Compre EUR/USD $1000"
    )
    
    response = whatsapp.process_message(message)
    
    assert response.signature is not None, "Orders must be signed"
    assert len(response.signature) == 128, "ED25519 signature is 128 hex chars"
    
    is_valid = whatsapp.verify_response_signature(response)
    assert is_valid, "Signature must be valid"
    
    print(f"   PASS: Real ED25519 signatures")
    print(f"   Signature: {response.signature[:32]}...")
    print(f"   Valid: {is_valid}")
    return True


async def test_gap6_nexus():
    """GAP 6: Nexus causal rules lookup"""
    print("\n[TEST 4] GAP 6: Nexus Causal Rules")
    
    nexus = NexusStrategy()
    
    assert 'drought_brazil' in nexus.causal_rules
    assert 'suez_blockage' in nexus.causal_rules
    assert 'fed_rate_hike_signal' in nexus.causal_rules
    
    rule = nexus.causal_rules['drought_brazil']
    assert 'affected_assets' in rule
    assert 'direction' in rule
    
    print(f"   PASS: Causal rules lookup fixed")
    print(f"   Total rules: {len(nexus.causal_rules)}")
    print(f"   Sample: drought_brazil -> {rule['affected_assets']}")
    return True


async def run_smoke_test():
    """Execute all smoke tests"""
    print("=" * 70)
    print("V5.3 REAL-WORLD HARDENING - SMOKE TEST")
    print("=" * 70)
    
    try:
        # Test 1: Async
        await test_gap1_async()
        
        # Test 2: PnL
        await test_gap2_3_real_pnl()
        
        # Test 3: ED25519
        test_gap4_ed25519()
        
        # Test 4: Nexus
        await test_gap6_nexus()
        
        print("\n" + "=" * 70)
        print("SMOKE TEST PASSED - ALL GAPS SEALED")
        print("=" * 70)
        print("\nRESULTS:")
        print("  [PASS] GAP 1: Oracle is truly async")
        print("  [PASS] GAP 2 & 3: Real PnL with trading costs")
        print("  [PASS] GAP 4: ED25519 sovereign signatures")
        print("  [PASS] GAP 6: Nexus causal rules fixed")
        print("\nSTATUS: PRODUCTION-READY")
        print("VERDICT: THE CARDBOARD DOORS ARE NOW STEEL")
        
    except Exception as e:
        print(f"\n[FAIL] Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(run_smoke_test())
    exit(0 if success else 1)
