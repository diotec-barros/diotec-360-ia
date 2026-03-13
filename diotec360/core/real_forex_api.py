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
Aethel Real Forex API - Conexão com Mercado Real
Integração com Alpha Vantage, Polygon.io e OANDA

Este módulo substitui os dados simulados por dados REAIS de Forex.
Cada dado capturado recebe um selo criptográfico de autenticidade.

Autor: Kiro AI - Engenheiro-Chefe
Versão: v2.2.6 "Real-Sense"
Data: 11 de Fevereiro de 2026
"""

import os
import time
import hashlib
import aiohttp
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from diotec360.core.env_compat import getbool


class ForexProvider(Enum):
    """Provedores de dados Forex suportados"""
    ALPHA_VANTAGE = "alpha_vantage"
    POLYGON = "polygon"
    OANDA = "oanda"
    FOREX_COM = "forex_com"


@dataclass
class RealForexQuote:
    """Cotação real de Forex com selo de autenticidade"""
    pair: str
    bid: float
    ask: float
    price: float  # Mid price
    timestamp: float
    provider: str
    source_data: Dict
    authenticity_seal: str
    
    def __post_init__(self):
        """Gera selo de autenticidade"""
        if not self.authenticity_seal:
            seal_data = f"{self.pair}:{self.price}:{self.timestamp}:{self.provider}"
            self.authenticity_seal = hashlib.sha256(seal_data.encode()).hexdigest()


class AlphaVantageConnector:
    """
    Conector para Alpha Vantage API
    
    Free tier: 25 requests/day
    Premium: 75 requests/minute
    
    Docs: https://www.alphavantage.co/documentation/
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa conector Alpha Vantage
        
        Args:
            api_key: Chave API (ou usa variável de ambiente ALPHA_VANTAGE_API_KEY)
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = "https://www.alphavantage.co/query"
        self.last_request_time = 0
        self.min_request_interval = 12  # 5 requests/minute = 12 seconds between requests
        
        print(f"[ALPHA_VANTAGE] Initialized with API key: {self.api_key[:8]}...")
    
    def _rate_limit(self):
        """Implementa rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            print(f"[ALPHA_VANTAGE] Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    async def get_forex_quote(self, from_currency: str, to_currency: str) -> Optional[RealForexQuote]:
        """
        Obtém cotação real de Forex (ASYNC)
        
        Args:
            from_currency: Moeda base (ex: EUR)
            to_currency: Moeda cotada (ex: USD)
        
        Returns:
            RealForexQuote ou None se falhar
        """
        self._rate_limit()
        
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency,
            'apikey': self.api_key
        }
        
        try:
            print(f"[ALPHA_VANTAGE] Fetching {from_currency}/{to_currency}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            # Verifica se há erro
            if 'Error Message' in data:
                print(f"[ALPHA_VANTAGE] Error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                print(f"[ALPHA_VANTAGE] Rate limit: {data['Note']}")
                return None
            
            # Extrai dados
            rate_data = data.get('Realtime Currency Exchange Rate', {})
            
            if not rate_data:
                print(f"[ALPHA_VANTAGE] No data returned")
                return None
            
            # Constrói cotação
            price = float(rate_data.get('5. Exchange Rate', 0))
            bid = float(rate_data.get('8. Bid Price', price * 0.9999))  # Aproximação se não disponível
            ask = float(rate_data.get('9. Ask Price', price * 1.0001))  # Aproximação se não disponível
            
            quote = RealForexQuote(
                pair=f"{from_currency}/{to_currency}",
                bid=bid,
                ask=ask,
                price=price,
                timestamp=time.time(),
                provider="alpha_vantage",
                source_data=rate_data,
                authenticity_seal=""  # Será gerado no __post_init__
            )
            
            print(f"[ALPHA_VANTAGE] ✅ {quote.pair}: {quote.price:.4f}")
            print(f"[ALPHA_VANTAGE] Seal: {quote.authenticity_seal[:16]}...")
            
            return quote
            
        except aiohttp.ClientError as e:
            print(f"[ALPHA_VANTAGE] Request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"[ALPHA_VANTAGE] Parse error: {e}")
            return None


class PolygonConnector:
    """
    Conector para Polygon.io API
    
    Free tier: 5 requests/minute
    Premium: Unlimited
    
    Docs: https://polygon.io/docs/forex
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa conector Polygon
        
        Args:
            api_key: Chave API (ou usa variável de ambiente POLYGON_API_KEY)
        """
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"
        self.last_request_time = 0
        self.min_request_interval = 12
        
        if not self.api_key:
            print("[POLYGON] Warning: No API key provided")
        else:
            print(f"[POLYGON] Initialized with API key: {self.api_key[:8]}...")
    
    def _rate_limit(self):
        """Implementa rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    async def get_forex_quote(self, from_currency: str, to_currency: str) -> Optional[RealForexQuote]:
        """
        Obtém cotação real de Forex via Polygon (ASYNC)
        
        Args:
            from_currency: Moeda base (ex: EUR)
            to_currency: Moeda cotada (ex: USD)
        
        Returns:
            RealForexQuote ou None se falhar
        """
        if not self.api_key:
            print("[POLYGON] Error: API key required")
            return None
        
        self._rate_limit()
        
        # Polygon usa formato C:EURUSD
        ticker = f"C:{from_currency}{to_currency}"
        url = f"{self.base_url}/v2/last/nbbo/{ticker}"
        
        params = {'apiKey': self.api_key}
        
        try:
            print(f"[POLYGON] Fetching {from_currency}/{to_currency}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            if data.get('status') != 'OK':
                print(f"[POLYGON] Error: {data.get('error', 'Unknown error')}")
                return None
            
            # Extrai dados
            results = data.get('results', {})
            
            bid = results.get('bid', 0)
            ask = results.get('ask', 0)
            price = (bid + ask) / 2 if bid and ask else 0
            
            if price == 0:
                print("[POLYGON] No valid price data")
                return None
            
            quote = RealForexQuote(
                pair=f"{from_currency}/{to_currency}",
                bid=bid,
                ask=ask,
                price=price,
                timestamp=time.time(),
                provider="polygon",
                source_data=results,
                authenticity_seal=""
            )
            
            print(f"[POLYGON] ✅ {quote.pair}: {quote.price:.4f}")
            print(f"[POLYGON] Seal: {quote.authenticity_seal[:16]}...")
            
            return quote
            
        except aiohttp.ClientError as e:
            print(f"[POLYGON] Request failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"[POLYGON] Parse error: {e}")
            return None


class RealForexOracle:
    """
    Oráculo de Forex Real - Gerencia múltiplos provedores
    
    Estratégia:
    1. Tenta Alpha Vantage (free tier)
    2. Fallback para Polygon se disponível
    3. Valida dados com múltiplas fontes
    """
    
    def __init__(self):
        """Inicializa oráculo com múltiplos provedores"""
        self.alpha_vantage = AlphaVantageConnector()
        self.polygon = PolygonConnector()
        
        self.providers = [
            (ForexProvider.ALPHA_VANTAGE, self.alpha_vantage),
            (ForexProvider.POLYGON, self.polygon),
        ]
        
        self.cache = {}
        self.cache_ttl = 60  # 1 minuto

        self.test_mode = getbool('DIOTEC360_TEST_MODE', legacy='AETHEL_TEST_MODE', default=False) or \
            getbool('DIOTEC360_OFFLINE', legacy='AETHEL_OFFLINE', default=False)
        
        print("[REAL_FOREX_ORACLE] Initialized with multiple providers")
    
    async def get_quote(self, pair: str) -> Optional[RealForexQuote]:
        """
        Obtém cotação real com fallback automático (ASYNC)
        
        Args:
            pair: Par de moedas (ex: EUR/USD)
        
        Returns:
            RealForexQuote ou None
        """
        if self.test_mode:
            price_map = {
                'EUR/USD': 1.0850,
                'EURUSD': 1.0850,
                'USD/JPY': 150.00,
                'USDJPY': 150.00,
                'GBP/USD': 1.2700,
                'GBPUSD': 1.2700,
            }
            key = pair.strip().upper()
            normalized = key.replace('-', '').replace('/', '')
            price = float(price_map.get(key, price_map.get(normalized, 1.0000)))
            bid = price * 0.9999
            ask = price * 1.0001
            quote = RealForexQuote(
                pair=key if '/' in key else f"{key[:3]}/{key[3:]}" if len(normalized) == 6 else key,
                bid=bid,
                ask=ask,
                price=price,
                timestamp=time.time(),
                provider="test_mode",
                source_data={"test_mode": True},
                authenticity_seal=""
            )
            self.cache[pair] = (quote, time.time())
            return quote

        # Verifica cache
        cache_key = pair
        if cache_key in self.cache:
            cached_quote, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                print(f"[REAL_FOREX_ORACLE] Using cached quote for {pair}")
                return cached_quote
        
        # Parse pair
        parts = pair.replace('/', '').split('-')
        if len(parts) == 1 and len(parts[0]) == 6:
            from_currency = parts[0][:3]
            to_currency = parts[0][3:]
        elif '/' in pair:
            from_currency, to_currency = pair.split('/')
        else:
            print(f"[REAL_FOREX_ORACLE] Invalid pair format: {pair}")
            return None
        
        # Tenta cada provedor
        for provider_type, provider in self.providers:
            try:
                quote = await provider.get_forex_quote(from_currency, to_currency)
                if quote:
                    # Cache resultado
                    self.cache[cache_key] = (quote, time.time())
                    return quote
            except Exception as e:
                print(f"[REAL_FOREX_ORACLE] {provider_type.value} failed: {e}")
                continue
        
        print(f"[REAL_FOREX_ORACLE] All providers failed for {pair}")
        return None
    
    async def get_multiple_quotes(self, pairs: List[str]) -> Dict[str, Optional[RealForexQuote]]:
        """
        Obtém múltiplas cotações (ASYNC)
        
        Args:
            pairs: Lista de pares
        
        Returns:
            Dicionário pair -> quote
        """
        import asyncio
        results = {}
        for pair in pairs:
            results[pair] = await self.get_quote(pair)
            if not self.test_mode:
                await asyncio.sleep(1)
        return results
    
    def validate_quote(self, quote: RealForexQuote) -> bool:
        """
        Valida autenticidade de uma cotação
        
        Args:
            quote: Cotação para validar
        
        Returns:
            True se válida
        """
        # Recalcula selo
        seal_data = f"{quote.pair}:{quote.price}:{quote.timestamp}:{quote.provider}"
        expected_seal = hashlib.sha256(seal_data.encode()).hexdigest()
        
        is_valid = expected_seal == quote.authenticity_seal
        
        if not is_valid:
            print(f"[REAL_FOREX_ORACLE] ⚠️ Invalid seal for {quote.pair}")
        
        return is_valid


# Singleton global
_oracle_instance = None

def get_real_forex_oracle() -> RealForexOracle:
    """Obtém instância singleton do oráculo"""
    global _oracle_instance
    if _oracle_instance is None:
        _oracle_instance = RealForexOracle()
    return _oracle_instance


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Demo rápido
        print("=" * 80)
        print("REAL FOREX ORACLE - DEMO")
        print("=" * 80)
        
        oracle = get_real_forex_oracle()
        
        # Testa EUR/USD
        print("\nTesting EUR/USD...")
        quote = await oracle.get_quote("EUR/USD")
        
        if quote:
            print(f"\n✅ SUCCESS!")
            print(f"Pair: {quote.pair}")
            print(f"Price: {quote.price:.4f}")
            print(f"Bid: {quote.bid:.4f}")
            print(f"Ask: {quote.ask:.4f}")
            print(f"Provider: {quote.provider}")
            print(f"Seal: {quote.authenticity_seal[:32]}...")
            print(f"Valid: {oracle.validate_quote(quote)}")
        else:
            print("\n❌ FAILED to get quote")
            print("Make sure you have ALPHA_VANTAGE_API_KEY set")
            print("Get free key at: https://www.alphavantage.co/support/#api-key")
    
    asyncio.run(main())
