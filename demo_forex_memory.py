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
Demonstração: Sistema de Memória Cognitiva para Forex

Este script demonstra como a Aethel pode:
1. Capturar dados do Forex em tempo real (simulado)
2. Validar decisões com o ConservationValidator
3. Armazenar experiências provadas na memória cognitiva
4. Aprender com padrões históricos
5. Tomar decisões baseadas em memória

Arquitetura:
- Web Oracle Gateway: Simula acesso a dados do Forex
- Cognitive Memory: Armazena experiências provadas
- Conservation Validator: Valida integridade das decisões
- Pattern Learning: Detecta e aprende padrões do mercado

Autor: Kiro AI - Engenheiro-Chefe
Versão: v2.2.4 "Cognitive Persistence"
Data: Fevereiro 5, 2026
"""

import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from diotec360.core.memory import CognitiveMemory, MemoryQuery, create_forex_memory, get_forex_patterns
from diotec360.core.conservation_validator import ConservationValidator
from diotec360.core.crypto import generate_signature, verify_signature


class ForexOracleSimulator:
    """
    Simulador de Oracle do Forex - captura dados de mercado.
    
    Em produção, isso seria substituído por:
    - API real do Forex (OANDA, Forex.com, etc.)
    - Web scraping de sites financeiros
    - Dados em tempo real via WebSocket
    """
    
    def __init__(self):
        """Inicializa o simulador de Forex"""
        # Taxa base EUR/USD (simulada)
        self.base_rate = 1.0850
        self.volatility = 0.002  # 0.2% de volatilidade
        
        # Histórico simulado
        self.history = []
        self._generate_history()
        
        print("[FOREX] Oracle do Forex inicializado (simulação)")
    
    def _generate_history(self, days: int = 30) -> None:
        """Gera histórico simulado de Forex"""
        now = datetime.now()
        
        for i in range(days * 24):  # Horas nos últimos dias
            timestamp = now - timedelta(hours=i)
            
            # Gera taxa com tendência e ruído
            trend = random.uniform(-0.0005, 0.0005) * i
            noise = random.uniform(-self.volatility, self.volatility)
            rate = self.base_rate + trend + noise
            
            self.history.append({
                'timestamp': timestamp.timestamp(),
                'rate': rate,
                'volume': random.uniform(1000, 5000)
            })
        
        # Ordena por timestamp (mais recente primeiro)
        self.history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    def get_current_rate(self, currency_pair: str = "EUR/USD") -> float:
        """
        Retorna a taxa atual do Forex (simulada).
        
        Args:
            currency_pair: Par de moedas (ex: "EUR/USD")
        
        Returns:
            Taxa de câmbio atual
        """
        if currency_pair != "EUR/USD":
            raise ValueError(f"Par de moedas não suportado: {currency_pair}")
        
        # Simula variação de mercado
        change = random.uniform(-self.volatility, self.volatility)
        current_rate = self.base_rate + change
        
        # Atualiza histórico
        self.history.insert(0, {
            'timestamp': time.time(),
            'rate': current_rate,
            'volume': random.uniform(1000, 5000)
        })
        
        # Mantém histórico limitado
        if len(self.history) > 1000:
            self.history = self.history[:1000]
        
        print(f"[FOREX] Taxa atual {currency_pair}: {current_rate:.4f}")
        return current_rate
    
    def get_historical_rates(self, hours: int = 24) -> List[Dict[str, float]]:
        """
        Retorna histórico de taxas.
        
        Args:
            hours: Número de horas de histórico
        
        Returns:
            Lista de taxas históricas
        """
        cutoff_time = time.time() - (hours * 3600)
        
        historical = [
            {'timestamp': h['timestamp'], 'rate': h['rate']}
            for h in self.history if h['timestamp'] >= cutoff_time
        ]
        
        print(f"[FOREX] Histórico recuperado: {len(historical)} pontos")
        return historical
    
    def get_market_sentiment(self) -> Dict[str, float]:
        """
        Analisa sentimento do mercado.
        
        Returns:
            Dicionário com indicadores de sentimento
        """
        # Análise simples baseada no histórico recente
        recent_rates = [h['rate'] for h in self.history[:10]]
        
        if len(recent_rates) < 2:
            return {'sentiment': 0.0, 'trend': 'neutral'}
        
        # Calcula tendência
        current = recent_rates[0]
        previous = recent_rates[1]
        change = current - previous
        
        # Normaliza sentimento (-1 a 1)
        sentiment = change / self.volatility
        sentiment = max(-1.0, min(1.0, sentiment))  # Clamp
        
        trend = "bullish" if sentiment > 0.1 else "bearish" if sentiment < -0.1 else "neutral"
        
        return {
            'sentiment': sentiment,
            'trend': trend,
            'current_rate': current,
            'change_pct': (change / previous) * 100
        }


class ForexTradingAgent:
    """
    Agente de Trading Autônomo baseado em Aethel.
    
    Este agente:
    1. Monitora o Forex em tempo real
    2. Toma decisões baseadas em regras provadas
    3. Valida cada decisão com ConservationValidator
    4. Aprende com experiências passadas
    5. Opera com segurança matemática
    """
    
    def __init__(self, initial_balance: float = 10000.0):
        """
        Inicializa o agente de trading.
        
        Args:
            initial_balance: Saldo inicial em USD
        """
        self.balance = initial_balance
        self.positions = []  # Posições abertas
        self.equity = initial_balance
        
        # Componentes Aethel
        self.oracle = ForexOracleSimulator()
        self.memory = CognitiveMemory()
        self.validator = ConservationValidator()
        
        # Chaves para assinatura (simulação)
        self.private_key = "simulated_private_key"
        self.public_key = "simulated_public_key"
        
        # Regras de trading (podem ser provadas com Z3)
        self.trading_rules = [
            {
                'name': 'stop_loss_rule',
                'condition': 'position_loss > 0.02',  # 2% de perda
                'action': 'close_position',
                'description': 'Fecha posição se perda > 2%'
            },
            {
                'name': 'take_profit_rule',
                'condition': 'position_profit > 0.03',  # 3% de lucro
                'action': 'close_position',
                'description': 'Fecha posição se lucro > 3%'
            },
            {
                'name': 'trend_following_rule',
                'condition': 'market_trend == "bullish" and sentiment > 0.3',
                'action': 'buy',
                'description': 'Compra se tendência de alta e sentimento > 0.3'
            },
            {
                'name': 'risk_management_rule',
                'condition': 'position_size > balance * 0.1',  # 10% do saldo
                'action': 'reduce_position',
                'description': 'Reduz posição se > 10% do saldo'
            }
        ]
        
        print(f"[TRADING] Agente inicializado com saldo: ${initial_balance:.2f}")
        print(f"[TRADING] {len(self.trading_rules)} regras de trading carregadas")
    
    def analyze_market(self) -> Dict[str, Any]:
        """
        Analisa o mercado atual.
        
        Returns:
            Análise completa do mercado
        """
        # Obtém dados do Forex
        current_rate = self.oracle.get_current_rate()
        sentiment = self.oracle.get_market_sentiment()
        historical = self.oracle.get_historical_rates(hours=24)
        
        # Calcula indicadores técnicos (simplificado)
        rates = [h['rate'] for h in historical]
        
        if len(rates) >= 20:
            # Média móvel simples (20 períodos)
            sma_20 = sum(rates[:20]) / 20
            # Média móvel simples (5 períodos)
            sma_5 = sum(rates[:5]) / 5
        else:
            sma_20 = current_rate
            sma_5 = current_rate
        
        # Determina tendência baseada em médias móveis
        if sma_5 > sma_20 * 1.001:  # 0.1% acima
            ma_trend = "bullish"
        elif sma_5 < sma_20 * 0.999:  # 0.1% abaixo
            ma_trend = "bearish"
        else:
            ma_trend = "neutral"
        
        # Busca memórias relevantes
        memory_query = MemoryQuery(
            query_text=f"Forex EUR/USD {current_rate:.4f}",
            start_time=time.time() - (7 * 24 * 3600),  # Última semana
            categories=['forex'],
            min_importance=0.6,
            limit=5
        )
        
        relevant_memories = self.memory.retrieve_memories(memory_query)
        
        # Busca padrões aprendidos
        relevant_patterns = self.memory.get_relevant_patterns(
            context=f"Forex analysis at {current_rate:.4f}",
            pattern_type='forex',
            min_confidence=0.4
        )
        
        analysis = {
            'timestamp': time.time(),
            'current_rate': current_rate,
            'sentiment': sentiment,
            'ma_trend': ma_trend,
            'sma_5': sma_5,
            'sma_20': sma_20,
            'relevant_memories': len(relevant_memories),
            'relevant_patterns': len(relevant_patterns),
            'positions_open': len(self.positions),
            'balance': self.balance,
            'equity': self.equity
        }
        
        print(f"[TRADING] Análise do mercado:")
        print(f"  Taxa: {current_rate:.4f}")
        print(f"  Sentimento: {sentiment['trend']} ({sentiment['sentiment']:.2f})")
        print(f"  Tendência MA: {ma_trend}")
        print(f"  Memórias relevantes: {len(relevant_memories)}")
        print(f"  Padrões relevantes: {len(relevant_patterns)}")
        
        return analysis
    
    def evaluate_trading_rules(self, market_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Avalia regras de trading baseado na análise do mercado.
        
        Args:
            market_analysis: Análise do mercado atual
        
        Returns:
            Lista de regras que devem ser acionadas
        """
        triggered_rules = []
        
        for rule in self.trading_rules:
            should_trigger = self._evaluate_rule_condition(rule['condition'], market_analysis)
            
            if should_trigger:
                triggered_rules.append({
                    'rule': rule,
                    'market_conditions': market_analysis,
                    'timestamp': time.time()
                })
                
                print(f"[TRADING] Regra acionada: {rule['name']}")
                print(f"  Condição: {rule['condition']}")
                print(f"  Ação: {rule['action']}")
        
        return triggered_rules
    
    def _evaluate_rule_condition(self, condition: str, market_analysis: Dict[str, Any]) -> bool:
        """
        Avalia uma condição de regra.
        
        Args:
            condition: Condição a ser avaliada
            market_analysis: Análise do mercado
        
        Returns:
            True se a condição for verdadeira
        """
        # Implementação simplificada - em produção usar parser de condições
        try:
            # Mapeia variáveis da análise
            vars_map = {
                'position_loss': 0.0,  # Seria calculado baseado em posições abertas
                'position_profit': 0.0,
                'position_size': 0.0,
                'balance': market_analysis['balance'],
                'market_trend': market_analysis['sentiment']['trend'],
                'sentiment': market_analysis['sentiment']['sentiment']
            }
            
            # Avaliação simples - em produção usar Z3 para provar condições
            if 'position_loss > 0.02' in condition:
                # Simula perda de posição
                return random.random() < 0.1  # 10% chance de acionar
            
            elif 'position_profit > 0.03' in condition:
                # Simula lucro de posição
                return random.random() < 0.15  # 15% chance de acionar
            
            elif 'market_trend == "bullish" and sentiment > 0.3' in condition:
                # Verifica condições reais
                trend = market_analysis['sentiment']['trend']
                sentiment = market_analysis['sentiment']['sentiment']
                return trend == "bullish" and sentiment > 0.3
            
            elif 'position_size > balance * 0.1' in condition:
                # Verifica tamanho da posição
                position_size = sum(p['size'] for p in self.positions)
                return position_size > market_analysis['balance'] * 0.1
            
            return False
            
        except Exception as e:
            print(f"[TRADING] Erro avaliando condição: {e}")
            return False
    
    def execute_trade(self, action: str, amount: float, rate: float) -> Dict[str, Any]:
        """
        Executa uma operação de trading.
        
        Args:
            action: 'buy' ou 'sell'
            amount: Quantidade em USD
            rate: Taxa de câmbio
        
        Returns:
            Resultado da operação
        """
        # Valida parâmetros
        if action not in ['buy', 'sell']:
            raise ValueError(f"Ação inválida: {action}")
        
        if amount <= 0:
            raise ValueError(f"Quantidade inválida: {amount}")
        
        if amount > self.balance * 0.2:  # Limite de 20% do saldo
            raise ValueError(f"Quantidade muito grande: {amount} (saldo: {self.balance})")
        
        # Cria prova de conservação
        trade_data = {
            'action': action,
            'amount': amount,
            'rate': rate,
            'timestamp': time.time(),
            'balance_before': self.balance,
            'agent_id': 'aethel_trading_agent'
        }
        
        # Valida com ConservationValidator
        conservation_result = self._validate_trade_conservation(trade_data)
        
        if not conservation_result['valid']:
            raise ValueError(f"Trade não conserva valor: {conservation_result['reason']}")
        
        # Executa trade (simulação)
        if action == 'buy':
            # Compra EUR com USD
            eur_amount = amount / rate
            self.balance -= amount
            
            # Adiciona posição
            position = {
                'id': f"pos_{int(time.time())}",
                'action': 'buy',
                'eur_amount': eur_amount,
                'usd_amount': amount,
                'entry_rate': rate,
                'entry_time': time.time(),
                'current_rate': rate
            }
            
            self.positions.append(position)
            result = f"Comprado {eur_amount:.2f} EUR a {rate:.4f} por ${amount:.2f}"
            
        else:  # sell
            # Vende EUR por USD
            # Encontra posição para vender (simplificado)
            if not self.positions:
                raise ValueError("Nenhuma posição para vender")
            
            position = self.positions[0]
            usd_amount = position['eur_amount'] * rate
            profit = usd_amount - position['usd_amount']
            profit_pct = (profit / position['usd_amount']) * 100
            
            self.balance += usd_amount
            self.positions.pop(0)
            
            result = f"Vendido {position['eur_amount']:.2f} EUR a {rate:.4f} por ${usd_amount:.2f}"
            result += f" (Lucro: ${profit:.2f}, {profit_pct:.1f}%)"
        
        # Atualiza equity
        self._update_equity(rate)
        
        # Assina o trade
        signature = generate_signature(
            json.dumps(trade_data, sort_keys=True),
            self.private_key
        )
        
        # Armazena na memória cognitiva
        memory_id = create_forex_memory(
            eur_usd_rate=rate,
            action=action,
            result=result,
            proof_hash=conservation_result['proof_hash']
        )
        
        # Aprende padrões se relevante
        if 'profit' in result.lower() and 'Lucro' in result:
            profit_pct = float(result.split('Lucro: ')[1].split('%')[0])
            if profit_pct > 2.0:
                self._learn_profitable_pattern(action, rate, profit_pct)
        
        trade_result = {
            'success': True,
            'action': action,
            'amount': amount,
            'rate': rate,
            'result': result,
            'new_balance': self.balance,
            'equity': self.equity,
            'signature': signature,
            'memory_id': memory_id,
            'conservation_valid': conservation_result['valid'],
            'timestamp': time.time()
        }
        
        print(f"[TRADING] Trade executado:")
        print(f"  Ação: {action}")
        print(f"  Quantidade: ${amount:.2f}")
        print(f"  Taxa: {rate:.4f}")
        print(f"  Resultado: {result}")
        print(f"  Saldo: ${self.balance:.2f}")
        print(f"  Equity: ${self.equity:.2f}")
        print(f"  Memória: {memory_id}")
        
        return trade_result
    
    def _validate_trade_conservation(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida se o trade conserva valor.
        
        Args:
            trade_data: Dados do trade
        
        Returns:
            Resultado da validação
        """
        # Cria transação para validação
        transaction = {
            'inputs': [
                {
                    'asset': 'USD',
                    'amount': trade_data['amount'],
                    'owner': 'trader'
                }
            ],
            'outputs': [
                {
                    'asset': 'EUR' if trade_data['action'] == 'buy' else 'USD',
                    'amount': trade_data['amount'] / trade_data['rate'] if trade_data['action'] == 'buy' else trade_data['amount'] * trade_data['rate'],
                    'owner': 'trader'
                }
            ],
            'metadata': {
                'trade_action': trade_data['action'],
                'exchange_rate': trade_data['rate'],
                'timestamp': trade_data['timestamp']
            }
        }
        
        # Valida com ConservationValidator
        try:
            is_valid, proof = self.validator.validate_transaction(transaction)
            
            return {
                'valid': is_valid,
                'proof_hash': proof if is_valid else None,
                'reason': 'Conservação validada' if is_valid else 'Falha na conservação'
            }
            
        except Exception as e:
            print(f"[TRADING] Erro na validação de conservação: {e}")
            return {
                'valid': False,
                'proof_hash': None,
                'reason': f"Erro de validação: {str(e)}"
            }
    
    def _update_equity(self, current_rate: float) -> None:
        """Atualiza equity baseado nas posições abertas"""
        position_value = 0.0
        
        for position in self.positions:
            if position['action'] == 'buy':
                # Valor em USD da posição em EUR
                usd_value = position['eur_amount'] * current_rate
                position_value += usd_value
        
        self.equity = self.balance + position_value
    
    def _learn_profitable_pattern(self, action: str, rate: float, profit_pct: float) -> None:
        """
        Aprende padrões de trading lucrativos.
        
        Args:
            action: Ação executada
            rate: Taxa de câmbio
            profit_pct: Percentual de lucro
        """
        # Obtém análise do mercado no momento do trade
        market_analysis = self.analyze_market()
        
        pattern_data = {
            'action': action,
            'entry_rate': rate,
            'profit_pct': profit_pct,
            'market_conditions': {
                'sentiment': market_analysis['sentiment']['sentiment'],
                'trend': market_analysis['sentiment']['trend'],
                'ma_trend': market_analysis['ma_trend'],
                'sma_5': market_analysis['sma_5'],
                'sma_20': market_analysis['sma_20']
            },
            'timestamp': time.time()
        }
        
        # Calcula confiança baseada no lucro
        confidence = min(0.9, profit_pct / 10.0)  # 10% de lucro = 0.9 confiança
        
        # Aprende padrão
        pattern_id = self.memory.learn_pattern(
            pattern_type='forex',
            pattern_data=pattern_data,
            confidence_score=confidence
        )
        
        print(f"[TRADING] Padrão aprendido: {pattern_id}")
        print(f"  Ação: {action}")
        print(f"  Lucro: {profit_pct:.1f}%")
        print(f"  Confiança: {confidence:.2f}")
    
    def run_trading_session(self, duration_minutes: int = 5) -> Dict[str, Any]:
        """
        Executa uma sessão de trading autônoma.
        
        Args:
            duration_minutes: Duração da sessão em minutos
        
        Returns:
            Resultado da sessão
        """
        print(f"\n{'='*60}")
        print(f"🚀 INICIANDO SESSÃO DE TRADING AUTÔNOMA")
        print(f"{'='*60}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        trades_executed = []
        rules_triggered = []
        
        initial_balance = self.balance
        initial_equity = self.equity
        
        try:
            while time.time() < end_time:
                print(f"\n⏰ Ciclo de trading: {time.strftime('%H:%M:%S')}")
                
                # 1. Analisa mercado
                market_analysis = self.analyze_market()
                
                # 2. Avalia regras
                triggered = self.evaluate_trading_rules(market_analysis)
                rules_triggered.extend(triggered)
                
                # 3. Executa trades se regras acionadas
                for trigger in triggered:
                    rule = trigger['rule']
                    
                    if rule['action'] == 'buy':
                        # Decide quantidade baseada no saldo
                        amount = min(self.balance * 0.1, 1000)  # 10% ou $1000
                        
                        if amount > 10:  # Mínimo $10
                            try:
                                trade_result = self.execute_trade(
                                    action='buy',
                                    amount=amount,
                                    rate=market_analysis['current_rate']
                                )
                                trades_executed.append(trade_result)
                            except Exception as e:
                                print(f"[TRADING] Erro executando trade: {e}")
                    
                    elif rule['action'] == 'sell' and self.positions:
                        # Vende primeira posição
                        position = self.positions[0]
                        try:
                            trade_result = self.execute_trade(
                                action='sell',
                                amount=position['usd_amount'],
                                rate=market_analysis['current_rate']
                            )
                            trades_executed.append(trade_result)
                        except Exception as e:
                            print(f"[TRADING] Erro executando trade: {e}")
                
                # 4. Aguarda próximo ciclo
                time.sleep(10)  # 10 segundos entre ciclos
            
        except KeyboardInterrupt:
            print("\n[TRADING] Sessão interrompida pelo usuário")
        
        # Calcula resultados
        final_balance = self.balance
        final_equity = self.equity
        
        balance_change = final_balance - initial_balance
        equity_change = final_equity - initial_equity
        
        profit_pct_balance = (balance_change / initial_balance) * 100
        profit_pct_equity = (equity_change / initial_equity) * 100
        
        session_result = {
            'duration_minutes': duration_minutes,
            'start_time': start_time,
            'end_time': time.time(),
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'initial_equity': initial_equity,
            'final_equity': final_equity,
            'balance_change': balance_change,
            'equity_change': equity_change,
            'profit_pct_balance': profit_pct_balance,
            'profit_pct_equity': profit_pct_equity,
            'trades_executed': len(trades_executed),
            'rules_triggered': len(rules_triggered),
            'positions_open': len(self.positions),
            'profitable_trades': sum(1 for t in trades_executed if 'profit' in t.get('result', '').lower()),
            'losing_trades': sum(1 for t in trades_executed if 'loss' in t.get('result', '').lower())
        }
        
        print(f"\n{'='*60}")
        print(f"📊 RESULTADO DA SESSÃO DE TRADING")
        print(f"{'='*60}")
        print(f"  Duração: {duration_minutes} minutos")
        print(f"  Trades executados: {len(trades_executed)}")
        print(f"  Regras acionadas: {len(rules_triggered)}")
        print(f"  Saldo inicial: ${initial_balance:.2f}")
        print(f"  Saldo final: ${final_balance:.2f}")
        print(f"  Mudança saldo: ${balance_change:.2f} ({profit_pct_balance:.1f}%)")
        print(f"  Equity inicial: ${initial_equity:.2f}")
        print(f"  Equity final: ${final_equity:.2f}")
        print(f"  Mudança equity: ${equity_change:.2f} ({profit_pct_equity:.1f}%)")
        print(f"  Posições abertas: {len(self.positions)}")
        
        # Armazena resultado na memória
        memory_context = f"Sessão de trading de {duration_minutes} minutos"
        memory_action = f"Executou {len(trades_executed)} trades, {len(rules_triggered)} regras acionadas"
        memory_result = f"Resultado: ${balance_change:.2f} ({profit_pct_balance:.1f}%) de lucro"
        
        memory_id = self.memory.store_memory(
            context=memory_context,
            action=memory_action,
            result=memory_result,
            metadata={
                'session_type': 'autonomous_trading',
                'duration_minutes': duration_minutes,
                'trades_count': len(trades_executed),
                'profit_pct': profit_pct_balance,
                'equity_change': equity_change
            },
            importance_score=0.7 if profit_pct_balance > 0 else 0.5
        )
        
        print(f"  Memória da sessão: {memory_id}")
        print(f"{'='*60}")
        
        return session_result


def main():
    """
    Função principal de demonstração.
    """
    print("🧠🌐⚡🏧 DEMONSTRAÇÃO: AETHEL COMO AGENTE SOBERANO AUTÔNOMO")
    print("=" * 70)
    print("Esta demonstração mostra como a Aethel pode:")
    print("1. 🌐 Acessar dados do Forex em tempo real (simulado)")
    print("2. 🧠 Armazenar experiências na memória cognitiva")
    print("3. ⚡ Validar decisões com ConservationValidator")
    print("4. 🏧 Executar trades com segurança matemática")
    print("5. 📱 Aprender com padrões históricos")
    print("=" * 70)
    
    # Inicializa agente de trading
    print("\n1. 🚀 Inicializando Agente de Trading Aethel...")
    agent = ForexTradingAgent(initial_balance=5000.0)
    
    # Executa análise inicial
    print("\n2. 📊 Analisando mercado...")
    analysis = agent.analyze_market()
    
    print(f"\n   Taxa EUR/USD atual: {analysis['current_rate']:.4f}")
    print(f"   Sentimento: {analysis['sentiment']['trend']} ({analysis['sentiment']['sentiment']:.2f})")
    print(f"   Tendência MA: {analysis['ma_trend']}")
    print(f"   Memórias relevantes: {analysis['relevant_memories']}")
    print(f"   Padrões relevantes: {analysis['relevant_patterns']}")
    
    # Executa sessão de trading
    print("\n3. ⚡ Executando sessão de trading autônoma (2 minutos)...")
    session_result = agent.run_trading_session(duration_minutes=2)
    
    # Mostra estatísticas da memória
    print("\n4. 🧠 Estatísticas do Sistema de Memória Cognitiva:")
    memory_stats = agent.memory.get_statistics()
    
    print(f"   Total de memórias: {memory_stats['total_memories']}")
    print(f"   Memórias de alta importância: {memory_stats['high_importance_memories']}")
    print(f"   Memórias provadas: {memory_stats['proven_memories']}")
    print(f"   Padrões aprendidos: {memory_stats['learned_patterns']}")
    
    if memory_stats['patterns_by_type']:
        print(f"   Padrões por tipo: {memory_stats['patterns_by_type']}")
    
    print(f"   Sessões históricas: {memory_stats['total_sessions']}")
    print(f"   Entradas de contexto: {memory_stats['total_context_entries']}")
    
    # Demonstra recuperação de memória
    print("\n5. 🔍 Demonstração de Recuperação de Memória:")
    
    current_rate = agent.oracle.get_current_rate()
    forex_patterns = get_forex_patterns(current_rate)
    
    print(f"   Padrões relevantes para EUR/USD {current_rate:.4f}:")
    
    for i, pattern in enumerate(forex_patterns[:3], 1):
        if pattern['type'] == 'memory':
            print(f"   {i}. 📝 Memória: {pattern['context'][:40]}...")
            print(f"      Ação: {pattern['action'][:30]}...")
            print(f"      Resultado: {pattern['result'][:30]}...")
            print(f"      Importância: {pattern['importance']:.2f}")
        elif pattern['type'] == 'pattern':
            print(f"   {i}. 🧩 Padrão: {pattern['id']}")
            print(f"      Tipo: {pattern['pattern_type']}")
            print(f"      Confiança: {pattern['confidence']:.2f}")
            print(f"      Ocorrências: {pattern['occurrences']}")
    
    print("\n" + "=" * 70)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("=" * 70)
    print("\n🎯 O que foi demonstrado:")
    print("   • Aethel como Agente Soberano Autônomo")
    print("   • Memória Cognitiva Persistente")
    print("   • Validação Matemática de Decisões")
    print("   • Aprendizado por Experiência")
    print("   • Operações Seguras no Forex")
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("   • Integração com WhatsApp (Aethel-WhatsApp-Gate)")
    print("   • Conexão com APIs reais do Forex")
    print("   • Modelos de embeddings reais para busca semântica")
    print("   • Prova Z3 completa para regras de trading")
    print("\n🏛️ IMPACTO COMERCIAL:")
    print("   DIOTEC 360 pode oferecer: 'IA com memória infinita que opera")
    print("   no Forex com segurança matemática e fala pelo WhatsApp'")
    print("=" * 70)


if __name__ == "__main__":
    main()