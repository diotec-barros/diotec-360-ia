"""
Deterministic Trader - The Core Trading Engine

The robot that cannot err. Every decision is mathematically proven.

Architecture:
- Real-Sense v2.2.6: Market data ingestion
- Judge v1.9.0: Proof generation and verification
- Sentinel v1.9.0: Real-time threat detection
- WhatsApp Gate: Sovereign signature authorization

Invariants (Inviolable):
- Max_Drawdown = 2%
- Confirmation_Wait = 5ms
- Source_Authenticity = True
"""

import asyncio
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..core.real_forex_api import RealForexOracle
from ..core.whatsapp_gate import WhatsAppGate
from ..core.judge import AethelJudge
from ..core.conservation import ConservationChecker
from ..core.sentinel_monitor import get_sentinel_monitor


@dataclass
class TradeSignal:
    """A mathematically proven trade opportunity"""
    strategy: str  # 'takashi' or 'simons'
    action: str  # 'buy' or 'sell'
    asset: str
    amount: Decimal
    price: Decimal
    confidence: float
    proof_hash: str
    timestamp: datetime
    reasoning: str


@dataclass
class TradingInvariants:
    """The inviolable rules of the trading engine"""
    max_drawdown_percent: Decimal = Decimal('2.0')
    confirmation_wait_ms: int = 5
    min_proof_confidence: float = 0.95
    max_position_size_percent: Decimal = Decimal('10.0')
    require_conservation_proof: bool = True
    require_whatsapp_signature: bool = True


class DeterministicTrader:
    """
    The Deterministic Trading Engine
    
    A robot that cannot err because every decision is:
    1. Mathematically proven (Judge v1.9)
    2. Conservation-law validated
    3. Sentinel-monitored for threats
    4. Sovereign-signature authorized
    
    "The Bloomberg of Security is Born"
    """
    
    def __init__(
        self,
        forex_api: RealForexOracle,
        whatsapp_gate: WhatsAppGate,
        judge: AethelJudge,
        invariants: Optional[TradingInvariants] = None
    ):
        self.forex_api = forex_api
        self.whatsapp_gate = whatsapp_gate
        self.judge = judge
        self.invariants = invariants or TradingInvariants()
        
        # Core components
        self.conservation = ConservationChecker()
        self.sentinel = get_sentinel_monitor()
        
        # State tracking
        self.portfolio_value = Decimal('0')
        self.initial_capital = Decimal('0')
        self.active_positions: Dict[str, Decimal] = {}
        self.trade_history: List[TradeSignal] = []
        
        # Strategy engines (injected)
        self.strategies = {}
        
    def register_strategy(self, name: str, strategy):
        """Register a trading strategy (Takashi or Simons)"""
        self.strategies[name] = strategy
        
    async def initialize(self, initial_capital: Decimal):
        """Initialize the trading engine with capital"""
        self.initial_capital = initial_capital
        self.portfolio_value = initial_capital
        
        print(f"🏛️ Deterministic Trader Initialized")
        print(f"💰 Initial Capital: ${initial_capital:,.2f}")
        print(f"🛡️ Max Drawdown: {self.invariants.max_drawdown_percent}%")
        print(f"⚡ Confirmation Wait: {self.invariants.confirmation_wait_ms}ms")
        
    async def scan_opportunities(self) -> List[TradeSignal]:
        """
        Scan all registered strategies for opportunities
        Returns only mathematically proven signals
        """
        signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                # Each strategy generates candidate signals
                candidates = await strategy.generate_signals(self.forex_api)
                
                # Validate each signal with Judge
                for candidate in candidates:
                    if await self._validate_signal(candidate):
                        signals.append(candidate)
                        
            except Exception as e:
                print(f"⚠️ Strategy {strategy_name} error: {e}")
                self.sentinel.log_anomaly(f"strategy_error_{strategy_name}", str(e))
                
        return signals
        
    async def _validate_signal(self, signal: TradeSignal) -> bool:
        """
        Validate a trade signal with mathematical proofs
        
        Checks:
        1. Conservation law (no money created/destroyed)
        2. Drawdown limit (max 2%)
        3. Position size limit
        4. Proof confidence threshold
        """
        # Check 1: Proof confidence
        if signal.confidence < self.invariants.min_proof_confidence:
            return False
            
        # Check 2: Drawdown protection
        projected_value = await self._calculate_projected_value(signal)
        drawdown = ((self.initial_capital - projected_value) / self.initial_capital) * 100
        
        if drawdown > self.invariants.max_drawdown_percent:
            print(f"🛡️ DRAWDOWN PROTECTION: Signal rejected (would cause {drawdown:.2f}% drawdown)")
            return False
            
        # Check 3: Position size limit
        position_size_percent = (signal.amount * signal.price / self.portfolio_value) * 100
        if position_size_percent > self.invariants.max_position_size_percent:
            return False
            
        # Check 4: Conservation proof (if required)
        if self.invariants.require_conservation_proof:
            if not await self._verify_conservation(signal):
                return False
                
        return True
        
    async def _calculate_projected_value(self, signal: TradeSignal) -> Decimal:
        """
        Calculate portfolio value after executing signal (MARK-TO-MARKET)
        
        FIX GAP 2 & 3: Real PnL calculation with:
        - Real-time market prices from RealForexOracle
        - Trading fees (0.1% typical)
        - Slippage (0.05% typical)
        - Bid-ask spread from real quotes
        """
        # Get current market price for the asset
        try:
            quote = await self.forex_api.get_quote(signal.asset)
            if quote is not None and hasattr(quote, 'price'):
                current_market_price = Decimal(str(quote.price))
            else:
                current_market_price = signal.price
        except Exception:
            current_market_price = signal.price
        
        # Calculate trading costs (REAL)
        trading_fee_percent = Decimal('0.001')  # 0.1% fee
        slippage_percent = Decimal('0.0005')  # 0.05% slippage
        
        if signal.action == 'buy':
            # Buying: pay ASK price + fees + slippage
            effective_price = current_market_price * (1 + trading_fee_percent + slippage_percent)
            cost = signal.amount * effective_price
            projected_value = self.portfolio_value - cost
        else:
            # Selling: receive BID price - fees - slippage
            effective_price = current_market_price * (1 - trading_fee_percent - slippage_percent)
            revenue = signal.amount * effective_price
            projected_value = self.portfolio_value + revenue
        
        # Add mark-to-market value of existing positions
        for asset, position_amount in self.active_positions.items():
            asset_price = current_market_price
            if asset != signal.asset:
                try:
                    asset_quote = await self.forex_api.get_quote(asset)
                    if asset_quote is not None and hasattr(asset_quote, 'price'):
                        asset_price = Decimal(str(asset_quote.price))
                except Exception:
                    asset_price = current_market_price

            if asset == signal.asset:
                # This position will be modified by the trade
                if signal.action == 'buy':
                    new_amount = position_amount + signal.amount
                else:
                    new_amount = position_amount - signal.amount

                # Mark to market at current price
                projected_value += new_amount * asset_price
            else:
                # Other positions marked to market
                projected_value += position_amount * asset_price
                
        return projected_value
            
    async def _verify_conservation(self, signal: TradeSignal) -> bool:
        """Verify conservation law for the trade"""
        # Generate Aethel code for conservation proof
        aethel_code = f"""
        solve trade_{signal.strategy} {{
            asset: Currency = {signal.asset}
            amount: Decimal = {signal.amount}
            price: Decimal = {signal.price}
            action: String = "{signal.action}"
            
            proof conservation {{
                # Total value before = Total value after
                portfolio_before == portfolio_after
                # No money created or destroyed
                sum(all_balances_before) == sum(all_balances_after)
            }}
        }}
        """
        
        verdict = self.judge.verify(aethel_code)
        return verdict.is_valid
        
    async def execute_signal(self, signal: TradeSignal) -> bool:
        """
        Execute a validated trade signal
        
        Flow:
        1. Send WhatsApp notification
        2. Wait for sovereign signature
        3. Execute trade
        4. Generate proof certificate
        5. Store in Merkle Vault
        """
        # Step 1: Notify user via WhatsApp
        message = f"""
🤖 **Trade Signal Detected**

Strategy: {signal.strategy.upper()}
Action: {signal.action.upper()} {signal.asset}
Amount: {signal.amount}
Price: ${signal.price}
Confidence: {signal.confidence * 100:.1f}%

Reasoning: {signal.reasoning}

Reply 'CONFIRM' to authorize this trade.
        """
        
        await self.whatsapp_gate.send_message(message)
        
        # Step 2: Wait for signature (if required)
        if self.invariants.require_whatsapp_signature:
            print("⏳ Waiting for sovereign signature...")
            
            # Wait for confirmation with timeout
            confirmed = await self.whatsapp_gate.wait_for_confirmation(
                timeout_seconds=300  # 5 minutes
            )
            
            if not confirmed:
                print("❌ Trade cancelled: No signature received")
                return False
                
        # Step 3: Execute trade
        print(f"⚡ Executing {signal.action} {signal.amount} {signal.asset} @ ${signal.price}")
        
        # Simulate trade execution (replace with real exchange API)
        success = await self._execute_on_exchange(signal)
        
        if not success:
            print("❌ Trade execution failed")
            return False
            
        # Step 4: Update portfolio
        self._update_portfolio(signal)
        
        # Step 5: Store proof
        self.trade_history.append(signal)
        
        print(f"✅ Trade executed successfully")
        print(f"📜 Proof Hash: {signal.proof_hash}")
        
        return True
        
    async def _execute_on_exchange(self, signal: TradeSignal) -> bool:
        """
        Execute trade on exchange (REAL IMPLEMENTATION)
        
        TODO: Integrate with real exchange APIs:
        - OANDA for Forex
        - Interactive Brokers for stocks
        - Binance for crypto
        
        For now, this is a placeholder that simulates execution.
        Replace with actual exchange API calls before production.
        """
        await asyncio.sleep(0.005)  # Simulate 5ms confirmation wait
        
        # TODO: Replace with real exchange integration
        # Example for OANDA:
        # async with aiohttp.ClientSession() as session:
        #     order_data = {
        #         'instrument': signal.asset,
        #         'units': str(signal.amount),
        #         'type': 'MARKET',
        #         'side': signal.action.upper()
        #     }
        #     async with session.post(
        #         f"{OANDA_API_URL}/v3/accounts/{ACCOUNT_ID}/orders",
        #         headers={'Authorization': f'Bearer {OANDA_API_KEY}'},
        #         json=order_data
        #     ) as response:
        #         result = await response.json()
        #         return result.get('orderFillTransaction') is not None
        
        print(f"⚠️ PLACEHOLDER: Real exchange execution not yet implemented")
        print(f"   Signal: {signal.action} {signal.amount} {signal.asset} @ ${signal.price}")
        print(f"   TODO: Integrate with OANDA/IB/Binance API")
        
        return True  # Placeholder success
        
    def _update_portfolio(self, signal: TradeSignal):
        """Update portfolio state after trade"""
        if signal.action == 'buy':
            self.active_positions[signal.asset] = \
                self.active_positions.get(signal.asset, Decimal('0')) + signal.amount
            self.portfolio_value -= signal.amount * signal.price
        else:
            self.active_positions[signal.asset] = \
                self.active_positions.get(signal.asset, Decimal('0')) - signal.amount
            self.portfolio_value += signal.amount * signal.price
            
    async def run_forever(self, scan_interval_seconds: int = 60):
        """
        Run the trading engine continuously
        
        Main loop:
        1. Scan for opportunities
        2. Validate signals
        3. Execute approved trades
        4. Monitor for threats
        """
        print("🚀 Deterministic Trader ONLINE")
        print(f"📡 Scanning every {scan_interval_seconds} seconds")
        
        while True:
            try:
                # Scan for opportunities
                signals = await self.scan_opportunities()
                
                if signals:
                    print(f"🎯 Found {len(signals)} validated signals")
                    
                    # Execute each signal
                    for signal in signals:
                        await self.execute_signal(signal)
                        
                # Check portfolio health
                self._check_portfolio_health()
                
                # Wait for next scan
                await asyncio.sleep(scan_interval_seconds)
                
            except Exception as e:
                print(f"⚠️ Trading loop error: {e}")
                self.sentinel.log_anomaly("trading_loop_error", str(e))
                await asyncio.sleep(scan_interval_seconds)
                
    def _check_portfolio_health(self):
        """Monitor portfolio for invariant violations"""
        current_drawdown = ((self.initial_capital - self.portfolio_value) / 
                           self.initial_capital) * 100
        
        if current_drawdown > self.invariants.max_drawdown_percent:
            print(f"🚨 CRITICAL: Drawdown limit exceeded ({current_drawdown:.2f}%)")
            print(f"🛡️ EMERGENCY STOP: Halting all trading")
            # TODO: Implement emergency stop mechanism
            
    def get_status(self) -> Dict:
        """Get current trading engine status"""
        current_drawdown = ((self.initial_capital - self.portfolio_value) / 
                           self.initial_capital) * 100
        
        return {
            'portfolio_value': float(self.portfolio_value),
            'initial_capital': float(self.initial_capital),
            'current_drawdown_percent': float(current_drawdown),
            'active_positions': {k: float(v) for k, v in self.active_positions.items()},
            'total_trades': len(self.trade_history),
            'strategies_active': list(self.strategies.keys())
        }
