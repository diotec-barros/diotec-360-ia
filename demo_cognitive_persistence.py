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
Demo: Aethel Cognitive Persistence - Memória de Destilação
Demonstra armazenamento e gerenciamento de respostas verificadas.

Author: Kiro AI
Version: Epoch 4.0 "Neural Nexus"
Date: February 18, 2026
"""

import sys
import time
from pathlib import Path
from diotec360.ai.cognitive_persistence import (
    CognitivePersistence,
    StoredResponse,
    create_persistence_from_env
)


def demo_1_basic_storage():
    """Demo 1: Armazenamento básico"""
    print("\n" + "=" * 80)
    print("DEMO 1: Armazenamento Básico")
    print("=" * 80)
    
    # Criar persistence
    persistence = CognitivePersistence("./demo_cognitive_1.db")
    
    # Criar resposta mock
    from diotec360.ai.autonomous_distiller import DistilledResponse, ResponseType
    
    mock_response = DistilledResponse(
        text="def is_prime(n):\n    if n < 2: return False\n    return all(n % i != 0 for i in range(2, int(n**0.5)+1))",
        source="gpt-4",
        confidence_score=0.95,
        response_type=ResponseType.PYTHON_CODE,
        verification_passed=True,
        explanation="High confidence, verified by heuristic",
        all_responses=[],
        verification_details={"method": "heuristic", "passed": True},
        timestamp=time.time()
    )
    
    # Salvar
    response_id = persistence.save_response(mock_response)
    
    print(f"\n✅ Resposta salva com ID: {response_id}")
    
    # Tentar salvar duplicata
    print("\n🔄 Tentando salvar duplicata...")
    dup_id = persistence.save_response(mock_response)
    
    if dup_id is None:
        print("✅ Deduplicação funcionando!")


def demo_2_categories():
    """Demo 2: Organização por categorias"""
    print("\n" + "=" * 80)
    print("DEMO 2: Organização por Categorias")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    # Criar respostas de diferentes categorias
    from diotec360.ai.autonomous_distiller import DistilledResponse, ResponseType
    
    categories_examples = [
        ("code", ResponseType.PYTHON_CODE, "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"),
        ("code", ResponseType.AETHEL_CODE, "solve { x + y == 100 }"),
        ("math", ResponseType.MATHEMATICAL, "∫x²dx = x³/3 + C"),
        ("logic", ResponseType.LOGICAL, "∀x. P(x) → Q(x)"),
        ("text", ResponseType.TEXT, "Recursion is a programming technique...")
    ]
    
    print("\n📝 Salvando respostas de diferentes categorias...")
    
    for category, resp_type, text in categories_examples:
        mock = DistilledResponse(
            text=text,
            source="gpt-4",
            confidence_score=0.85,
            response_type=resp_type,
            verification_passed=True,
            explanation="Test response",
            all_responses=[],
            verification_details={"method": "test"},
            timestamp=time.time()
        )
        
        response_id = persistence.save_response(mock)
        print(f"  ✅ {category}: {response_id}")
    
    # Recuperar por categoria
    print("\n📊 Respostas por categoria:")
    
    for cat in ["code", "math", "logic", "text"]:
        responses = persistence.get_by_category(cat, limit=10)
        print(f"  • {cat}: {len(responses)} respostas")


def demo_3_statistics():
    """Demo 3: Estatísticas do dataset"""
    print("\n" + "=" * 80)
    print("DEMO 3: Estatísticas")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    stats = persistence.get_statistics()
    
    print(f"\n📊 Estatísticas do Dataset:")
    print(f"   Total de respostas: {stats['total_responses']}")
    print(f"   Respostas verificadas: {stats['verified_responses']}")
    print(f"   Taxa de verificação: {stats['verification_rate']:.1%}")
    print(f"   Score médio: {stats['average_confidence']:.3f}")
    print(f"   Alta qualidade (>0.8): {stats['high_quality_responses']}")
    
    print(f"\n📂 Por categoria:")
    for cat, count in stats['by_category'].items():
        print(f"   • {cat}: {count}")
    
    print(f"\n🎓 Por fonte:")
    for source, count in stats['by_source'].items():
        print(f"   • {source}: {count}")


def demo_4_training_readiness():
    """Demo 4: Prontidão para treinamento"""
    print("\n" + "=" * 80)
    print("DEMO 4: Prontidão para Treinamento")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    readiness = persistence.get_training_readiness()
    
    print(f"\n🎯 Status de Treinamento:")
    print(f"   {readiness['message']}")
    print(f"   Progresso: {readiness['progress']:.1%}")
    print(f"   Exemplos de alta qualidade: {readiness['high_quality_count']}")
    print(f"   Threshold: {readiness['threshold']}")
    
    if not readiness['ready']:
        print(f"   Faltam: {readiness['remaining']} exemplos")
    
    print(f"\n💡 Como funciona:")
    print(f"   • Threshold: 1000 exemplos de alta qualidade")
    print(f"   • Alta qualidade: score ≥ 0.8 + verificado")
    print(f"   • Quando atingir threshold → pronto para LoRA training")


def demo_5_export_lora():
    """Demo 5: Exportação para LoRA"""
    print("\n" + "=" * 80)
    print("DEMO 5: Exportação para LoRA")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    output_path = "./demo_lora_dataset.jsonl"
    
    print(f"\n📤 Exportando para formato LoRA...")
    print(f"   Output: {output_path}")
    
    count = persistence.export_for_lora(output_path, min_confidence=0.8)
    
    print(f"\n✅ {count} exemplos exportados")
    
    # Mostrar exemplo
    if count > 0:
        print(f"\n📝 Exemplo do arquivo:")
        with open(output_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            import json
            example = json.loads(first_line)
            print(f"   Prompt: {example['prompt'][:50]}...")
            print(f"   Completion: {example['completion'][:50]}...")
            print(f"   Metadata: {example['metadata']}")
    
    # Verificar arquivo comprimido
    compressed = output_path + '.gz'
    if Path(compressed).exists():
        import os
        original_size = os.path.getsize(output_path)
        compressed_size = os.path.getsize(compressed)
        ratio = (1 - compressed_size / original_size) * 100
        
        print(f"\n🗜️  Compressão:")
        print(f"   Original: {original_size:,} bytes")
        print(f"   Comprimido: {compressed_size:,} bytes")
        print(f"   Economia: {ratio:.1f}%")


def demo_6_search():
    """Demo 6: Busca de respostas"""
    print("\n" + "=" * 80)
    print("DEMO 6: Busca")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    queries = ["factorial", "prime", "recursion"]
    
    print(f"\n🔍 Buscando respostas...")
    
    for query in queries:
        results = persistence.search(query, limit=5)
        print(f"\n  Query: '{query}'")
        print(f"  Resultados: {len(results)}")
        
        for i, resp in enumerate(results[:2], 1):
            print(f"    {i}. {resp.source} (score: {resp.confidence_score:.3f})")
            print(f"       {resp.response[:60]}...")


def demo_7_maintenance():
    """Demo 7: Manutenção do banco"""
    print("\n" + "=" * 80)
    print("DEMO 7: Manutenção")
    print("=" * 80)
    
    persistence = CognitivePersistence("./demo_cognitive_2.db")
    
    # Estatísticas antes
    stats_before = persistence.get_statistics()
    print(f"\n📊 Antes da limpeza:")
    print(f"   Total: {stats_before['total_responses']}")
    
    # Remover baixa qualidade
    print(f"\n🗑️  Removendo respostas de baixa qualidade...")
    deleted = persistence.delete_low_quality(max_confidence=0.5)
    
    # Estatísticas depois
    stats_after = persistence.get_statistics()
    print(f"\n📊 Depois da limpeza:")
    print(f"   Total: {stats_after['total_responses']}")
    print(f"   Removidas: {deleted}")
    
    # Otimizar banco
    print(f"\n🧹 Otimizando banco de dados...")
    persistence.vacuum()
    
    # Backup
    backup_path = "./demo_cognitive_backup.db"
    print(f"\n💾 Criando backup...")
    persistence.backup(backup_path)


def demo_8_integration():
    """Demo 8: Integração com Distiller"""
    print("\n" + "=" * 80)
    print("DEMO 8: Integração com Distiller")
    print("=" * 80)
    
    print("\n📖 Fluxo de integração:")
    print("""
    1. Autonomous Distiller destila resposta
       ↓
    2. Cognitive Persistence salva resposta
       ↓
    3. Quando atingir 1000 exemplos de alta qualidade
       ↓
    4. Exportar para formato LoRA
       ↓
    5. LoRA Training treina modelo local
       ↓
    6. Local Engine fica mais inteligente
    """)
    
    print("\n📝 Exemplo de código:")
    print("""
    from diotec360.ai.autonomous_distiller import create_distiller_from_env
    from diotec360.ai.cognitive_persistence import create_persistence_from_env
    
    # Criar componentes
    distiller = create_distiller_from_env()
    persistence = create_persistence_from_env()
    
    # Destilar resposta
    result = distiller.distill("Write a Python function to check prime")
    
    # Salvar se passou na verificação
    if result.verification_passed and result.confidence_score >= 0.8:
        persistence.save_response(result)
    
    # Verificar se pronto para treinamento
    readiness = persistence.get_training_readiness()
    if readiness['ready']:
        persistence.export_for_lora("./lora_dataset.jsonl")
        print("Dataset pronto para LoRA training!")
    """)


def main():
    """Executa todas as demos"""
    print("=" * 80)
    print("AETHEL COGNITIVE PERSISTENCE - DEMONSTRAÇÃO COMPLETA")
    print("Epoch 4.0: Neural Nexus - Memória de Destilação")
    print("=" * 80)
    
    demos = [
        ("Armazenamento Básico", demo_1_basic_storage),
        ("Organização por Categorias", demo_2_categories),
        ("Estatísticas", demo_3_statistics),
        ("Prontidão para Treinamento", demo_4_training_readiness),
        ("Exportação para LoRA", demo_5_export_lora),
        ("Busca", demo_6_search),
        ("Manutenção", demo_7_maintenance),
        ("Integração com Distiller", demo_8_integration)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Erro na demo {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("RESUMO: COGNITIVE PERSISTENCE")
    print("=" * 80)
    print("\n✅ Funcionalidades demonstradas:")
    print("   • Armazenamento com deduplicação")
    print("   • Organização por categoria")
    print("   • Estatísticas de dataset")
    print("   • Prontidão para treinamento")
    print("   • Exportação para LoRA (JSON Lines)")
    print("   • Busca de respostas")
    print("   • Manutenção e otimização")
    print("   • Integração com Distiller")
    
    print("\n🎯 Próximo passo:")
    print("   Task 4.0.5: LoRA Training")
    print("   • Treinar modelo local com dataset")
    print("   • Fine-tuning eficiente")
    print("   • Validação de performance")
    
    print("\n🏛️ [COGNITIVE PERSISTENCE: OPERATIONAL]")


if __name__ == "__main__":
    main()
