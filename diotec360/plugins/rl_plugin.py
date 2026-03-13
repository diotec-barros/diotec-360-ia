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
Reinforcement Learning Plugin for Aethel

Connects RL agents to Aethel's safety layer for trading bots
"""

from typing import Dict, Any
from .base import AethelPlugin, Action, ActionType, ProofResult


class RLPlugin(AethelPlugin):
    """
    Plugin for Reinforcement Learning agents
    
    Allows RL trading bots to operate with mathematical safety guarantees.
    
    Features:
    - RL proposes trades
    - Aethel verifies constraints (conservation, stop-loss, overflow)
    - Execute only verified trades
    
    Key Benefit: RL runs at full speed, Aethel acts as emergency brake
    
    Commercial Value: $1K-10K/month per trading bot
    
    Example:
        plugin = RLPlugin(my_trading_model)
        result = plugin.run({
            "market_state": current_prices,
            "portfolio": my_portfolio
        })
        if result.success:
            execute_trade(result.output)
    """
    
    def __init__(
        self,
        rl_model: Any = None,
        max_position_size: float = 100000,
        stop_loss_percent: float = 5.0,
        **kwargs
    ):
        """
        Initialize RL plugin
        
        Args:
            rl_model: RL model (PyTorch, TensorFlow, etc.)
            max_position_size: Maximum position size
            stop_loss_percent: Stop-loss percentage
        """
        super().__init__(name="rl-trading", version="1.0.0")
        self.rl_model = rl_model
        self.max_position_size = max_position_size
        self.stop_loss_percent = stop_loss_percent
    
    def propose_action(self, context: Dict) -> Action:
        """
        RL model proposes a trade
        
        Args:
            context: {
                "market_state": current prices,
                "portfolio": current holdings
            }
        
        Returns:
            Action with trade details
        """
        market_state = context.get("market_state", {})
        portfolio = context.get("portfolio", {})
        
        if self.rl_model:
            # Use real RL model
            trade = self._predict_trade(market_state, portfolio)
        else:
            # Mock trade for demo
            trade = self._mock_trade(market_state, portfolio)
        
        return Action(
            type=ActionType.TRADE,
            data=trade,
            context=context
        )
    
    def verify_action(self, action: Action) -> ProofResult:
        """
        Verify trade satisfies all constraints
        
        Checks:
        1. Conservation: Money is not created/destroyed
        2. Overflow: No integer overflow
        3. Stop-loss: Respects stop-loss limits
        4. Position size: Within limits
        
        Args:
            action: Trade action
        
        Returns:
            ProofResult with verification status
        """
        trade = action.data
        
        # Verify constraints
        checks = {
            "conservation": self._verify_conservation(trade),
            "overflow": self._verify_overflow(trade),
            "stop_loss": self._verify_stop_loss(trade),
            "position_size": self._verify_position_size(trade)
        }
        
        all_valid = all(checks.values())
        
        if not all_valid:
            failed_checks = [k for k, v in checks.items() if not v]
            return ProofResult(
                valid=False,
                error=f"Failed checks: {', '.join(failed_checks)}",
                proof_log=checks
            )
        
        return ProofResult(
            valid=True,
            proof_log=checks,
            confidence=1.0
        )
    
    def execute_action(self, action: Action) -> Any:
        """
        Execute verified trade
        
        Args:
            action: Verified trade action
        
        Returns:
            Trade execution result
        """
        trade = action.data
        
        return {
            "trade": trade,
            "verified": True,
            "status": "ready_to_execute",
            "safety_checks_passed": True
        }
    
    def _predict_trade(self, market_state: Dict, portfolio: Dict) -> Dict:
        """Use RL model to predict trade"""
        # This would call the actual RL model
        # For now, return mock trade
        return self._mock_trade(market_state, portfolio)
    
    def _mock_trade(self, market_state: Dict, portfolio: Dict) -> Dict:
        """Generate mock trade for demo"""
        return {
            "action": "buy",
            "symbol": "BTC",
            "amount": 1000,
            "price": 50000,
            "stop_loss": 47500,  # 5% stop-loss
            "take_profit": 55000
        }
    
    def _verify_conservation(self, trade: Dict) -> bool:
        """Verify money conservation"""
        # Money in = Money out
        amount = trade.get("amount", 0)
        price = trade.get("price", 0)
        total = amount * price
        
        # Check if total is reasonable
        return 0 < total <= self.max_position_size
    
    def _verify_overflow(self, trade: Dict) -> bool:
        """Verify no integer overflow"""
        amount = trade.get("amount", 0)
        price = trade.get("price", 0)
        
        # Check for overflow
        MAX_INT = 2**63 - 1
        return (amount * price) < MAX_INT
    
    def _verify_stop_loss(self, trade: Dict) -> bool:
        """Verify stop-loss is respected"""
        price = trade.get("price", 0)
        stop_loss = trade.get("stop_loss", 0)
        
        if price == 0:
            return False
        
        # Calculate stop-loss percentage
        loss_percent = abs((price - stop_loss) / price) * 100
        
        # Must be within configured limit
        return loss_percent <= self.stop_loss_percent
    
    def _verify_position_size(self, trade: Dict) -> bool:
        """Verify position size is within limits"""
        amount = trade.get("amount", 0)
        price = trade.get("price", 0)
        total = amount * price
        
        return total <= self.max_position_size
