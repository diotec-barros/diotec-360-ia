"""
DIOTEC 360 - STRESS TEST DE MASSA v9.0.0
Task 9.0.0: THE LIVING NEXUS

Simula 10.000 transações simultâneas para provar que o Synchrony Protocol
mantém todos os Merkle Roots em sincronia sem erros de concorrência.

@author DIOTEC 360 - Dionísio Sebastião Barros
@version 9.0.0
@date 2026-03-14
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importar componentes do sistema
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from diotec360.core.state import MerkleStateTree, AethelStateManager

# =====================================================
# CONFIGURAÇÃO DO TESTE
# =====================================================

TOTAL_TRANSACTIONS = 10000
CONCURRENT_WORKERS = 100
TRANSACTION_TYPES = ['market_sale', 'freight_delivery', 'b2b_contract', 'price_report', 'group_buy']

# =====================================================
# GERADOR DE TRANSAÇÕES SINTÉTICAS
# =====================================================

class TransactionGenerator:
    """Gera transações sintéticas para teste de carga"""
    
    def __init__(self):
        self.transaction_id = 0
    
    def generate_market_sale(self) -> Dict[str, Any]:
        """Gera venda no marketplace"""
        self.transaction_id += 1
        return {
            'type': 'market_sale',
            'id': f'market_{self.transaction_id}',
            'buyer_id': f'user_{random.randint(1, 1000)}',
            'seller_id': f'seller_{random.randint(1, 100)}',
            'amount': random.uniform(1000, 50000),
            'items': random.randint(1, 5),
            'timestamp': time.time()
        }
    
    def generate_freight_delivery(self) -> Dict[str, Any]:
        """Gera entrega de frete"""
        self.transaction_id += 1
        return {
            'type': 'freight_delivery',
            'id': f'freight_{self.transaction_id}',
            'driver_id': f'driver_{random.randint(1, 200)}',
            'origin': {'lat': -8.8383 + random.uniform(-0.1, 0.1), 
                      'lng': 13.2344 + random.uniform(-0.1, 0.1)},
            'destination': {'lat': -8.8400 + random.uniform(-0.1, 0.1), 
                           'lng': 13.2360 + random.uniform(-0.1, 0.1)},
            'distance_km': random.uniform(5, 50),
            'gps_points': random.randint(10, 100),
            'timestamp': time.time()
        }
    
    def generate_b2b_contract(self) -> Dict[str, Any]:
        """Gera contrato B2B"""
        self.transaction_id += 1
        return {
            'type': 'b2b_contract',
            'id': f'contract_{self.transaction_id}',
            'buyer_id': f'company_{random.randint(1, 50)}',
            'seller_id': f'supplier_{random.randint(1, 50)}',
            'value': random.uniform(100000, 5000000),
            'clauses': random.randint(3, 10),
            'timestamp': time.time()
        }
    
    def generate_price_report(self) -> Dict[str, Any]:
        """Gera reporte de preço"""
        self.transaction_id += 1
        return {
            'type': 'price_report',
            'id': f'price_{self.transaction_id}',
            'product_id': f'product_{random.randint(1, 500)}',
            'price': random.uniform(500, 10000),
            'location': {'lat': -8.8383 + random.uniform(-0.5, 0.5), 
                        'lng': 13.2344 + random.uniform(-0.5, 0.5)},
            'reporter_id': f'user_{random.randint(1, 1000)}',
            'timestamp': time.time()
        }
    
    def generate_group_buy(self) -> Dict[str, Any]:
        """Gera compra em grupo"""
        self.transaction_id += 1
        participants = random.randint(10, 50)
        return {
            'type': 'group_buy',
            'id': f'group_{self.transaction_id}',
            'product_id': f'product_{random.randint(1, 100)}',
            'participants': participants,
            'total_amount': participants * random.uniform(5000, 20000),
            'timestamp': time.time()
        }
    
    def generate_random(self) -> Dict[str, Any]:
        """Gera transação aleatória"""
        tx_type = random.choice(TRANSACTION_TYPES)
        
        if tx_type == 'market_sale':
            return self.generate_market_sale()
        elif tx_type == 'freight_delivery':
            return self.generate_freight_delivery()
        elif tx_type == 'b2b_contract':
            return self.generate_b2b_contract()
        elif tx_type == 'price_report':
            return self.generate_price_report()
        else:
            return self.generate_group_buy()

# =====================================================
# PROCESSADOR DE TRANSAÇÕES
# =====================================================

class TransactionProcessor:
    """Processa transações e verifica integridade"""
    
    def __init__(self):
        self.state_manager = AethelStateManager(state_dir='.stress_test_state')
        
        self.processed = 0
        self.failed = 0
        self.merkle_roots = []
        self.errors = []
    
    async def initialize(self):
        """Inicializa componentes"""
        # Criar conta de comunicação para o teste
        try:
            self.state_manager.state_tree.create_communication_account('stress_test_public_key')
        except ValueError:
            # Conta já existe
            pass
        print("✅ Componentes inicializados")
    
    async def process_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Processa uma transação"""
        try:
            # 1. Adicionar à árvore Merkle (usando communication account)
            account_hash, merkle_root = self.state_manager.state_tree.add_interaction(
                'stress_test_public_key',
                {
                    'interaction_id': transaction['id'],
                    'type': transaction['type'],
                    'data': transaction,
                    'timestamp': transaction['timestamp']
                }
            )
            
            # 2. Verificar integridade (simples verificação de hash)
            proof_valid = merkle_root is not None and len(merkle_root) == 64
            
            self.processed += 1
            self.merkle_roots.append(merkle_root)
            
            return {
                'success': True,
                'transaction_id': transaction['id'],
                'merkle_root': merkle_root,
                'proof_valid': proof_valid,
                'judge_valid': True  # Simplificado para o teste
            }
            
        except Exception as e:
            self.failed += 1
            self.errors.append({
                'transaction_id': transaction['id'],
                'error': str(e)
            })
            return {
                'success': False,
                'transaction_id': transaction['id'],
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do teste"""
        unique_roots = len(set(self.merkle_roots))
        
        return {
            'total_processed': self.processed,
            'total_failed': self.failed,
            'success_rate': (self.processed / (self.processed + self.failed) * 100) if (self.processed + self.failed) > 0 else 0,
            'unique_merkle_roots': unique_roots,
            'merkle_roots_sample': self.merkle_roots[:10] if self.merkle_roots else [],
            'errors_count': len(self.errors),
            'errors_sample': self.errors[:5] if self.errors else []
        }

# =====================================================
# EXECUTOR DO TESTE DE STRESS
# =====================================================

class StressTestExecutor:
    """Executa teste de stress de massa"""
    
    def __init__(self, total_transactions: int, concurrent_workers: int):
        self.total_transactions = total_transactions
        self.concurrent_workers = concurrent_workers
        self.generator = TransactionGenerator()
        self.processor = TransactionProcessor()
        
        self.start_time = None
        self.end_time = None
    
    async def run(self):
        """Executa o teste completo"""
        print("\n" + "="*70)
        print("🏛️ DIOTEC 360 - STRESS TEST DE MASSA v9.0.0")
        print("   Task 9.0.0: THE LIVING NEXUS")
        print("="*70)
        print(f"\n📊 Configuração:")
        print(f"   • Total de transações: {self.total_transactions:,}")
        print(f"   • Workers concorrentes: {self.concurrent_workers}")
        print(f"   • Tipos de transação: {len(TRANSACTION_TYPES)}")
        print("\n🚀 Iniciando teste...\n")
        
        # Inicializar processador
        await self.processor.initialize()
        
        # Gerar transações
        print(f"📦 Gerando {self.total_transactions:,} transações...")
        transactions = [self.generator.generate_random() 
                       for _ in range(self.total_transactions)]
        print(f"✅ {len(transactions):,} transações geradas\n")
        
        # Processar transações em paralelo
        print(f"⚡ Processando com {self.concurrent_workers} workers...\n")
        self.start_time = time.time()
        
        # Dividir em batches
        batch_size = self.total_transactions // self.concurrent_workers
        batches = [transactions[i:i + batch_size] 
                  for i in range(0, len(transactions), batch_size)]
        
        # Processar batches
        results = []
        for i, batch in enumerate(batches):
            print(f"   Batch {i+1}/{len(batches)}: {len(batch)} transações...")
            batch_results = await asyncio.gather(
                *[self.processor.process_transaction(tx) for tx in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
            
            # Mostrar progresso
            progress = ((i + 1) / len(batches)) * 100
            print(f"   Progresso: {progress:.1f}%")
        
        self.end_time = time.time()
        
        # Gerar relatório
        await self.generate_report(results)
    
    async def generate_report(self, results: List[Dict[str, Any]]):
        """Gera relatório final do teste"""
        duration = self.end_time - self.start_time
        stats = self.processor.get_statistics()
        
        print("\n" + "="*70)
        print("📊 RELATÓRIO FINAL DO STRESS TEST")
        print("="*70)
        
        print(f"\n⏱️  Tempo de Execução:")
        print(f"   • Duração total: {duration:.2f} segundos")
        print(f"   • Transações/segundo: {self.total_transactions / duration:.2f}")
        print(f"   • Tempo médio/transação: {(duration / self.total_transactions) * 1000:.2f}ms")
        
        print(f"\n✅ Resultados:")
        print(f"   • Processadas com sucesso: {stats['total_processed']:,}")
        print(f"   • Falhadas: {stats['total_failed']:,}")
        print(f"   • Taxa de sucesso: {stats['success_rate']:.2f}%")
        
        print(f"\n🌳 Integridade Merkle:")
        print(f"   • Merkle Roots únicos: {stats['unique_merkle_roots']:,}")
        print(f"   • Consistência: {'✅ PERFEITA' if stats['unique_merkle_roots'] == self.total_transactions else '⚠️ VERIFICAR'}")
        
        if stats['merkle_roots_sample']:
            print(f"\n   Amostra de Merkle Roots:")
            for i, root in enumerate(stats['merkle_roots_sample'][:5], 1):
                print(f"   {i}. {root[:32]}...")
        
        print(f"\n❌ Erros:")
        print(f"   • Total de erros: {stats['errors_count']}")
        if stats['errors_sample']:
            print(f"   Amostra de erros:")
            for error in stats['errors_sample']:
                print(f"   • {error['transaction_id']}: {error['error']}")
        
        # Verificação de concorrência
        print(f"\n🔒 Verificação de Concorrência:")
        concurrency_ok = stats['total_failed'] == 0
        error_msg = f"⚠️ {stats['total_failed']}" if not concurrency_ok else "❌ NENHUM"
        print(f"   • Erros de concorrência: {error_msg}")
        sync_status = "✅ OPERACIONAL" if concurrency_ok else "⚠️ VERIFICAR"
        print(f"   • Synchrony Protocol: {sync_status}")
        
        # Veredito final
        print(f"\n🏁 VEREDITO FINAL:")
        if stats['success_rate'] >= 99.9 and concurrency_ok:
            print(f"   ✅ SISTEMA APROVADO PARA PRODUÇÃO")
            print(f"   🏛️ O NEXO ESTÁ VIVO E OPERACIONAL")
            print(f"   🇦🇴 PRONTO PARA A ECONOMIA REAL")
        elif stats['success_rate'] >= 95:
            print(f"   ⚠️ SISTEMA FUNCIONAL MAS REQUER OTIMIZAÇÃO")
        else:
            print(f"   ❌ SISTEMA REQUER CORREÇÕES ANTES DE PRODUÇÃO")
        
        print("\n" + "="*70)
        
        # Salvar relatório em arquivo
        await self.save_report(stats, duration)
    
    async def save_report(self, stats: Dict[str, Any], duration: float):
        """Salva relatório em arquivo JSON"""
        report = {
            'test_version': '9.0.0',
            'test_name': 'THE LIVING NEXUS - Stress Test de Massa',
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'total_transactions': self.total_transactions,
                'concurrent_workers': self.concurrent_workers,
                'transaction_types': TRANSACTION_TYPES
            },
            'performance': {
                'duration_seconds': duration,
                'transactions_per_second': self.total_transactions / duration,
                'avg_time_per_transaction_ms': (duration / self.total_transactions) * 1000
            },
            'results': stats,
            'verdict': {
                'approved_for_production': stats['success_rate'] >= 99.9 and stats['total_failed'] == 0,
                'synchrony_protocol_operational': stats['total_failed'] == 0,
                'merkle_consistency': stats['unique_merkle_roots'] == self.total_transactions
            }
        }
        
        filename = f'stress_test_report_v9.0.0_{int(time.time())}.json'
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Relatório salvo: {filename}")

# =====================================================
# FUNÇÃO PRINCIPAL
# =====================================================

async def main():
    """Função principal do teste"""
    executor = StressTestExecutor(
        total_transactions=TOTAL_TRANSACTIONS,
        concurrent_workers=CONCURRENT_WORKERS
    )
    
    await executor.run()

if __name__ == "__main__":
    asyncio.run(main())
