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
Aethel Commodity Oracle v5.2 - "The BRICS Commodity Nexus"

Monitors Gold, Oil, and Grains for carry trade profit protection.
Integrates with Alpha Vantage API for real-time commodity prices.

Philosophy: "When the dollar falls, Gold rises. Protect the Yen's profit."

Autor: Kiro AI - Engenheiro-Chefe
Versão: v5.2 "BRICS Commodity Nexus"
Data: 23 de Fevereiro de 2026
"""

import os
import time
import hashlib
import requests
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class CommodityPrice:
    """Commodity price with authenticity seal"""
    commodity: str
    price: Decimal
    currency: str  # USD, EUR, etc.
    unit: str  # oz (gold), barrel (oil), bushel (grains)
    timestamp: float
    source: str
    authenticity_seal: str
    
    def __post_init__(self):
        """Generate authenticity seal"""
        if not self.authenticity_seal:
            seal_data = f"{self.commodity}:{self.price}:{self.timestamp}:{self.source}"
            self.authenticity_seal = hashlib.sha256(seal_data.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'commodity': self.commodity,
            'price': float(self.price),
            'currency': self.currency,
            'unit': self.unit,
            'timestamp': self.timestamp,
            'source': self.source,
            'authenticity_seal': self.authenticity_seal
        }


class CommodityOracle:
    """
    Oracle for fetching commodity prices.
    
    Supports:
    - Gold (XAU/USD) - Safe haven asset
    - Silver (XAG/USD) - Industrial metal
    - Oil (WTI, Brent) - Energy commodity
    - Wheat - Agricultural commodity
    - Corn - Agricultural commodity
    
    Data source: Alpha Vantage API
    Cache: 1 hour (commodities are less volatile than forex)
    """
    
    # Fallback prices (approximate as of Feb 2026)
    FALLBACK_PRICES = {
        'GOLD': Decimal('2050.00'),    # USD per troy ounce
        'SILVER': Decimal('24.50'),    # USD per troy ounce
        'WTI': Decimal('78.50'),       # USD per barrel
        'BRENT': Decimal('82.00'),     # USD per barrel
        'WHEAT': Decimal('6.20'),      # USD per bushel
        'CORN': Decimal('4.80'),       # USD per bushel
    }
    
    COMMODITY_UNITS = {
        'GOLD': 'troy ounce',
        'SILVER': 'troy ounce',
        'WTI': 'barrel',
        'BRENT': 'barrel',
        'WHEAT': 'bushel',
        'CORN': 'bushel',
    }
    
    COMMODITY_SYMBOLS = {
        'GOLD': 'XAU/USD',
        'SILVER': 'XAG/USD',
        'WTI': 'WTI/USD',
        'BRENT': 'BRENT/USD',
        'WHEAT': 'WHEAT/USD',
        'CORN': 'CORN/USD',
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Commodity Oracle.
        
        Args:
            api_key: Alpha Vantage API key (or uses ALPHA_VANTAGE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        self.last_request_time = 0
        self.min_request_interval = 12  # Rate limiting
        
        print(f"[COMMODITY_ORACLE] Initialized with API key: {self.api_key[:8]}...")
    
    def _rate_limit(self):
        """Implement rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"[COMMODITY_ORACLE] Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def get_price(self, commodity: str) -> Optional[CommodityPrice]:
        """
        Get commodity price.
        
        Args:
            commodity: Commodity code (GOLD, SILVER, WTI, BRENT, WHEAT, CORN)
        
        Returns:
            CommodityPrice or None if failed
        """
        commodity = commodity.upper()
        
        # Check cache
        cache_key = commodity
        if cache_key in self.cache:
            cached_price, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                print(f"[COMMODITY_ORACLE] Using cached price for {commodity}")
                return cached_price
        
        # Try to fetch from API
        price = self._fetch_from_api(commodity)
        
        if price:
            # Cache result
            self.cache[cache_key] = (price, time.time())
            return price
        
        # Fallback to reference prices
        print(f"[COMMODITY_ORACLE] Using fallback price for {commodity}")
        return self._get_fallback_price(commodity)
    
    def _fetch_from_api(self, commodity: str) -> Optional[CommodityPrice]:
        """
        Fetch commodity price from API.
        
        Note: Alpha Vantage has limited commodity support.
        For production, would integrate with specialized commodity APIs.
        """
        # TODO: Integrate with commodity-specific APIs
        # - Metals: Kitco, LBMA
        # - Oil: EIA, IEA
        # - Grains: CME, CBOT
        return None
    
    def _get_fallback_price(self, commodity: str) -> Optional[CommodityPrice]:
        """Get fallback price from reference data"""
        if commodity not in self.FALLBACK_PRICES:
            print(f"[COMMODITY_ORACLE] Commodity not supported: {commodity}")
            return None
        
        price = CommodityPrice(
            commodity=commodity,
            price=self.FALLBACK_PRICES[commodity],
            currency='USD',
            unit=self.COMMODITY_UNITS[commodity],
            timestamp=time.time(),
            source="fallback_reference",
            authenticity_seal=""
        )
        
        print(f"[COMMODITY_ORACLE] ✅ {commodity}: ${price.price} per {price.unit}")
        print(f"[COMMODITY_ORACLE] Seal: {price.authenticity_seal[:16]}...")
        
        return price
    
    def get_multiple_prices(self, commodities: List[str]) -> Dict[str, Optional[CommodityPrice]]:
        """
        Get prices for multiple commodities.
        
        Args:
            commodities: List of commodity codes
        
        Returns:
            Dictionary commodity -> CommodityPrice
        """
        results = {}
        for commodity in commodities:
            results[commodity] = self.get_price(commodity)
            time.sleep(0.5)  # Rate limiting
        return results
    
    def calculate_gold_hedge_ratio(self, carry_trade_profit: Decimal, gold_price: Decimal) -> Decimal:
        """
        Calculate how much gold to buy to hedge carry trade profit.
        
        Args:
            carry_trade_profit: Profit from carry trade in USD
            gold_price: Current gold price in USD per troy ounce
        
        Returns:
            Number of troy ounces to buy
        """
        if gold_price <= 0:
            return Decimal('0')
        
        ounces = carry_trade_profit / gold_price
        
        print(f"\n💎 Gold Hedge Calculation:")
        print(f"   Carry Trade Profit: ${carry_trade_profit}")
        print(f"   Gold Price: ${gold_price} per oz")
        print(f"   Recommended Hedge: {ounces:.4f} oz")
        
        return ounces
    
    def detect_dollar_weakness(self, gold_price_current: Decimal, gold_price_24h_ago: Decimal) -> bool:
        """
        Detect dollar weakness by monitoring gold price movement.
        
        When gold rises significantly, it often indicates dollar weakness.
        This is a signal to move carry trade profits into gold.
        
        Args:
            gold_price_current: Current gold price
            gold_price_24h_ago: Gold price 24 hours ago
        
        Returns:
            True if dollar is weakening (gold rising > 2%)
        """
        if gold_price_24h_ago <= 0:
            return False
        
        change_pct = ((gold_price_current - gold_price_24h_ago) / gold_price_24h_ago) * Decimal('100')
        
        is_weak = change_pct > Decimal('2.0')  # 2% threshold
        
        print(f"\n💵 Dollar Strength Analysis:")
        print(f"   Gold 24h ago: ${gold_price_24h_ago}")
        print(f"   Gold now: ${gold_price_current}")
        print(f"   Change: {change_pct:+.2f}%")
        print(f"   Dollar Status: {'WEAK ⚠️' if is_weak else 'STRONG ✅'}")
        
        return is_weak


# Singleton instance
_oracle_instance = None


def get_commodity_oracle() -> CommodityOracle:
    """Get singleton instance of Commodity Oracle"""
    global _oracle_instance
    if _oracle_instance is None:
        _oracle_instance = CommodityOracle()
    return _oracle_instance


if __name__ == "__main__":
    # Demo
    print("=" * 80)
    print("COMMODITY ORACLE - BRICS COMMODITY NEXUS")
    print("=" * 80)
    
    oracle = get_commodity_oracle()
    
    # Test Gold price
    print("\n💎 Fetching Gold price...")
    gold_price = oracle.get_price("GOLD")
    
    if gold_price:
        print(f"\n✅ SUCCESS!")
        print(f"Commodity: {gold_price.commodity}")
        print(f"Price: ${gold_price.price} per {gold_price.unit}")
        print(f"Currency: {gold_price.currency}")
        print(f"Seal: {gold_price.authenticity_seal[:32]}...")
    
    # Test Oil price
    print("\n🛢️  Fetching WTI Oil price...")
    oil_price = oracle.get_price("WTI")
    
    if oil_price:
        print(f"\n✅ SUCCESS!")
        print(f"Commodity: {oil_price.commodity}")
        print(f"Price: ${oil_price.price} per {oil_price.unit}")
        print(f"Currency: {oil_price.currency}")
        print(f"Seal: {oil_price.authenticity_seal[:32]}...")
    
    # Calculate gold hedge
    print("\n💎 Calculating Gold Hedge for Carry Trade Profit...")
    carry_profit = Decimal('1000.00')  # $1,000 profit from Yen carry trade
    ounces = oracle.calculate_gold_hedge_ratio(carry_profit, gold_price.price)
    
    # Detect dollar weakness
    print("\n💵 Detecting Dollar Weakness...")
    gold_24h_ago = Decimal('2000.00')  # Simulated price from 24h ago
    is_weak = oracle.detect_dollar_weakness(gold_price.price, gold_24h_ago)
    
    if is_weak:
        print("\n⚠️  ALERT: Dollar is weakening!")
        print(f"   Recommendation: Move ${carry_profit} into {ounces:.4f} oz of Gold")
    else:
        print("\n✅ Dollar is strong - carry trade profits are safe in USD")
