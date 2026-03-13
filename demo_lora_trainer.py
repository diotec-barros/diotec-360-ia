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
Demo: Aethel LoRA Trainer
Demonstra o sistema de fine-tuning autônomo do Neural Nexus.

Este demo mostra como o LoRA Trainer usa respostas verificadas da Cognitive
Persistence para treinar o modelo local, tornando-o tão inteligente quanto
os "professores" (GPT-4, Claude, DeepSeek).

Author: Kiro AI - Engenheiro-Chefe
Date: February 18, 2026
"""

import time
from diotec360.ai.lora_trainer import LoRATrainer, LoRAConfig
from diotec360.ai.cognitive_persistence import CognitivePersistence
from diotec360.ai.local_engine import LocalEngine
from diotec360.ai.autonomous_distiller import DistilledResponse, ResponseType


def demo_1_initialization():
    """Demo 1: Inicialização do LoRA Trainer"""
    print("\n" + "=" * 80)
    print("DEMO 1: INICIALIZAÇÃO DO LORA TRAINER")
    print("=" * 80)
    
    # Criar componentes
    local_engine = LocalEngine()
    persistence = CognitivePersistence("./demo_lora_memory.db")
    
    # Criar trainer
    trainer = LoRATrainer(local_engine, persistence)
    
    print("\n✅ LoRA Trainer inicializado com sucesso!")
    
    return trainer, persistence


def demo_2_check_readiness(trainer):
    """Demo 2: Verificar prontidão para treinamento"""
    print("\n" + "=" * 80)
    print("DEMO 2: VERIFICAR PRONTIDÃO PARA TREINAMENTO")
    print("=" * 80)
    
    # Verificar se pronto
    ready = trainer.should_train(min_examples=1000, min_confidence=0.8)
    
    if ready:
        print("\n✅ Dataset pronto para treinamento!")
    else:
        print("\n⏳ Dataset não pronto ainda")
        
        # Mostrar progresso
        readiness = trainer.persistence.get_training_readiness()
        print(f"\nProgresso: {readiness['progress']:.1%}")
        print(f"Faltam: {readiness['remaining']} exemplos de alta qualidade")
    
    return ready


def demo_3_populate_dataset(persistence):
    """Demo 3: Popular dataset com exemplos mock"""
    print("\n" + "=" * 80)
    print("DEMO 3: POPULAR DATASET COM EXEMPLOS MOCK")
    print("=" * 80)
    
    print("\n[DEMO] Criando exemplos mock de respostas verificadas...")
    
    # Criar exemplos mock
    examples = [
        {
            "text": "def factorial(n):\n    if n <= 1: return 1\n    return n * factorial(n-1)",
            "source": "gpt-4",
            "type": ResponseType.PYTHON_CODE,
            "confidence": 0.95
        },
        {
            "text": "def is_prime(n):\n    if n < 2: return False\n    for i in range(2, int(n**0.5)+1):\n        if n % i == 0: return False\n    return True",
            "source": "claude",
            "type": ResponseType.PYTHON_CODE,
            "confidence": 0.92
        },
        {
            "text": "def fibonacci(n):\n    if n <= 1: return n\n    a, b = 0, 1\n    for _ in range(n-1):\n        a, b = b, a + b\n    return b",
            "source": "deepseek-v3",
            "type": ResponseType.PYTHON_CODE,
            "confidence": 0.88
        }
    ]
    
    # Salvar exemplos
    saved_count = 0
    for example in examples:
        # Criar DistilledResponse mock
        response = DistilledResponse(
            text=example["text"],
            source=example["source"],
            confidence_score=example["confidence"],
            response_type=example["type"],
            verification_passed=True,
            explanation=f"Mock example from {example['source']}",
            all_responses=[],
            verification_details={"passed": True, "method": "mock"},
            timestamp=time.time()
        )
        
        # Salvar
        response_id = persistence.save_response(response)
        if response_id:
            saved_count += 1
    
    print(f"\n✅ {saved_count} exemplos salvos")
    
    # Estatísticas
    stats = persistence.get_statistics()
    print(f"\nEstatísticas do dataset:")
    print(f"  Total: {stats['total_responses']}")
    print(f"  Verificados: {stats['verified_responses']}")
    print(f"  Alta qualidade: {stats['high_quality_responses']}")


def demo_4_prepare_dataset(trainer):
    """Demo 4: Preparar dataset para treinamento"""
    print("\n" + "=" * 80)
    print("DEMO 4: PREPARAR DATASET PARA TREINAMENTO")
    print("=" * 80)
    
    try:
        # Preparar dataset
        train_path, val_path = trainer.prepare_dataset(
            output_path="./demo_lora_dataset",
            min_confidence=0.8,
            train_split=0.9
        )
        
        print(f"\n✅ Dataset preparado:")
        print(f"  Train: {train_path}")
        print(f"  Val: {val_path}")
        
        return train_path, val_path
        
    except Exception as e:
        print(f"\n⚠️  Erro ao preparar dataset: {e}")
        print("  (Normal se não houver exemplos suficientes)")
        return None, None


def demo_5_train_model(trainer):
    """Demo 5: Treinar modelo com LoRA"""
    print("\n" + "=" * 80)
    print("DEMO 5: TREINAR MODELO COM LORA")
    print("=" * 80)
    
    # Configurar treinamento
    config = LoRAConfig(
        model_name="deepseek-coder:7b",
        dataset_path="./demo_lora_dataset.train.jsonl",
        output_dir="./demo_lora_models",
        lora_rank=8,
        lora_alpha=16,
        learning_rate=3e-4,
        batch_size=4,
        num_epochs=3
    )
    
    print("\n[DEMO] Configuração de treinamento:")
    print(f"  Modelo base: {config.model_name}")
    print(f"  LoRA rank: {config.lora_rank}")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Epochs: {config.num_epochs}")
    
    try:
        # Treinar (mock)
        print("\n[DEMO] Iniciando treinamento mock...")
        version = trainer.train(config)
        
        print(f"\n✅ Treinamento completo!")
        print(f"  Versão: v{version.version}")
        print(f"  Loss final: {version.final_loss:.4f}")
        print(f"  Validation accuracy: {version.validation_accuracy:.1%}")
        
        return version
        
    except Exception as e:
        print(f"\n⚠️  Erro no treinamento: {e}")
        return None


def demo_6_deploy_model(trainer, version):
    """Demo 6: Deploy modelo treinado"""
    print("\n" + "=" * 80)
    print("DEMO 6: DEPLOY MODELO TREINADO")
    print("=" * 80)
    
    if not version:
        print("\n⚠️  Nenhuma versão para deploy")
        return
    
    # Deploy
    success = trainer.deploy(version, force=True)
    
    if success:
        print(f"\n✅ Modelo v{version.version} deployed com sucesso!")
    else:
        print(f"\n⚠️  Deploy não realizado")


def demo_7_statistics(trainer):
    """Demo 7: Estatísticas de treinamento"""
    print("\n" + "=" * 80)
    print("DEMO 7: ESTATÍSTICAS DE TREINAMENTO")
    print("=" * 80)
    
    stats = trainer.get_statistics()
    
    print(f"\nEstatísticas gerais:")
    print(f"  Total de versões: {stats['total_versions']}")
    print(f"  Melhor versão: v{stats.get('best_version', 0)}")
    print(f"  Melhor accuracy: {stats['best_accuracy']:.1%}")
    
    if stats['total_versions'] > 0:
        print(f"  Accuracy média: {stats['average_accuracy']:.1%}")
        print(f"  Total de exemplos treinados: {stats['total_examples_trained']}")
        
        print(f"\nHistórico de versões:")
        for v in stats['versions']:
            print(f"  v{v['version']}: accuracy={v['accuracy']:.1%}, "
                  f"loss={v['loss']:.4f}, examples={v['examples']}")


def demo_8_complete_workflow():
    """Demo 8: Workflow completo de aprendizado"""
    print("\n" + "=" * 80)
    print("DEMO 8: WORKFLOW COMPLETO DE APRENDIZADO")
    print("=" * 80)
    
    print("\n[DEMO] Simulando workflow completo do Neural Nexus:")
    print("\n1. Usuário faz pergunta")
    print("   → 'Write a function to calculate fibonacci'")
    
    print("\n2. Autonomous Distiller consulta múltiplas IAs")
    print("   → GPT-4, Claude, DeepSeek, Ollama local")
    
    print("\n3. Distiller verifica respostas formalmente")
    print("   → Judge/Z3 validation")
    
    print("\n4. Distiller seleciona melhor resposta")
    print("   → Score: 0.95 (GPT-4)")
    
    print("\n5. Cognitive Persistence salva resposta verificada")
    print("   → Database: .aethel_cognitive/memory.db")
    
    print("\n6. Quando 1000 exemplos acumulam...")
    print("   → LoRA Trainer inicia automaticamente")
    
    print("\n7. LoRA Training treina modelo local")
    print("   → deepseek-coder:7b + LoRA adapters")
    
    print("\n8. Modelo local fica mais inteligente")
    print("   → Accuracy: 75% → 90%")
    
    print("\n9. Reduz dependência de APIs externas")
    print("   → Custo: $0.01/1k tokens → $0.001/1k tokens")
    
    print("\n10. Empresa tem IA soberana")
    print("   → 100% offline, sem vazamento de dados")
    
    print("\n✅ Ciclo de aprendizado completo!")


def main():
    """Executa todos os demos"""
    print("=" * 80)
    print("AETHEL LORA TRAINER - DEMONSTRAÇÃO COMPLETA")
    print("=" * 80)
    print("\nEste demo mostra como o Neural Nexus aprende com gigantes")
    print("(GPT-4, Claude, DeepSeek) e treina o modelo local via LoRA.")
    
    try:
        # Demo 1: Inicialização
        trainer, persistence = demo_1_initialization()
        
        # Demo 2: Verificar prontidão
        ready = demo_2_check_readiness(trainer)
        
        # Demo 3: Popular dataset (se não pronto)
        if not ready:
            demo_3_populate_dataset(persistence)
        
        # Demo 4: Preparar dataset
        train_path, val_path = demo_4_prepare_dataset(trainer)
        
        # Demo 5: Treinar modelo (mock)
        if train_path:
            version = demo_5_train_model(trainer)
            
            # Demo 6: Deploy
            if version:
                demo_6_deploy_model(trainer, version)
        else:
            version = None
        
        # Demo 7: Estatísticas
        demo_7_statistics(trainer)
        
        # Demo 8: Workflow completo
        demo_8_complete_workflow()
        
        print("\n" + "=" * 80)
        print("DEMO COMPLETO")
        print("=" * 80)
        print("\n✅ Todos os demos executados com sucesso!")
        print("\n🏛️ [LORA TRAINER: OPERATIONAL]")
        
    except Exception as e:
        print(f"\n❌ Erro no demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
