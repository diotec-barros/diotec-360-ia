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
Demo: Aethel Autonomous Distiller - O Cérebro que Aprende
Demonstra comparação e verificação de respostas de múltiplas IAs.

Author: Kiro AI
Version: Epoch 4.0 "Neural Nexus"
Date: February 18, 2026
"""

import sys
from diotec360.ai.autonomous_distiller import (
    AutonomousDistiller,
    ResponseType,
    create_distiller_from_env
)


def demo_1_basic_comparison():
    """Demo 1: Comparação básica de respostas"""
    print("\n" + "=" * 80)
    print("DEMO 1: Comparação Básica")
    print("=" * 80)
    
    distiller = AutonomousDistiller()
    
    # Respostas mock para comparar
    responses = [
        {
            "source": "gpt-4",
            "text": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
            "tokens": 20,
            "latency_ms": 1000
        },
        {
            "source": "claude",
            "text": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
            "tokens": 25,
            "latency_ms": 1200
        },
        {
            "source": "local-llama",
            "text": "def factorial(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i\n    return result",
            "tokens": 30,
            "latency_ms": 500
        }
    ]
    
    print(f"\n📊 Comparando {len(responses)} respostas...")
    
    comparison = distiller.compare_responses(responses)
    
    print(f"\n✅ Tipo detectado: {comparison['response_type']}")
    print(f"\n🏆 Ranking:")
    
    for i, resp in enumerate(comparison['responses'], 1):
        print(f"\n  {i}. {resp['source']}")
        print(f"     Score: {resp['score']:.3f}")
        print(f"     Verificação: {'✅ PASSOU' if resp['verification_passed'] else '❌ FALHOU'}")
        print(f"     Tamanho: {resp['text_length']} chars")


def demo_2_confidence_scoring():
    """Demo 2: Sistema de confidence scoring"""
    print("\n" + "=" * 80)
    print("DEMO 2: Confidence Scoring")
    print("=" * 80)
    
    print("\n📖 Formula do Confidence Score:")
    print("   score = 0.5 × verification + 0.3 × consistency + 0.2 × history")
    
    print("\n🔍 Componentes:")
    print("   • Verification (50%): Passou na verificação formal?")
    print("   • Consistency (30%): Outras IAs concordam?")
    print("   • History (20%): Fonte tem histórico de acertos?")
    
    print("\n📊 Exemplo de cálculo:")
    print("   GPT-4:")
    print("     Verification: 1.0 (passou no Judge)")
    print("     Consistency: 0.8 (2 de 3 IAs concordam)")
    print("     History: 0.9 (90% de acertos históricos)")
    print("     Score final: 0.5×1.0 + 0.3×0.8 + 0.2×0.9 = 0.92")
    
    print("\n   Local Llama:")
    print("     Verification: 0.7 (passou parcialmente)")
    print("     Consistency: 0.3 (resposta diferente)")
    print("     History: 0.6 (60% de acertos)")
    print("     Score final: 0.5×0.7 + 0.3×0.3 + 0.2×0.6 = 0.56")


def demo_3_response_types():
    """Demo 3: Detecção de tipos de resposta"""
    print("\n" + "=" * 80)
    print("DEMO 3: Detecção de Tipos")
    print("=" * 80)
    
    distiller = AutonomousDistiller()
    
    test_cases = [
        {
            "prompt": "Write an Aethel contract to verify balance",
            "expected": ResponseType.AETHEL_CODE
        },
        {
            "prompt": "Write a Python function to sort a list",
            "expected": ResponseType.PYTHON_CODE
        },
        {
            "prompt": "Calculate the derivative of x^2 + 3x + 5",
            "expected": ResponseType.MATHEMATICAL
        },
        {
            "prompt": "Prove that if P implies Q and Q implies R, then P implies R",
            "expected": ResponseType.LOGICAL
        },
        {
            "prompt": "Explain the concept of recursion",
            "expected": ResponseType.TEXT
        }
    ]
    
    print("\n🔍 Testando detecção de tipos:")
    
    for tc in test_cases:
        # Criar resposta mock
        mock_responses = [{
            "source": "test",
            "text": tc["prompt"],
            "tokens": 10,
            "latency_ms": 100
        }]
        
        detected = distiller._detect_response_type(tc["prompt"], mock_responses)
        match = "✅" if detected == tc["expected"] else "❌"
        
        print(f"\n  {match} Prompt: {tc['prompt'][:50]}...")
        print(f"     Esperado: {tc['expected'].value}")
        print(f"     Detectado: {detected.value}")


def demo_4_verification_methods():
    """Demo 4: Métodos de verificação"""
    print("\n" + "=" * 80)
    print("DEMO 4: Métodos de Verificação")
    print("=" * 80)
    
    print("\n🔬 Métodos disponíveis:")
    
    print("\n  1. Judge (Z3 Prover)")
    print("     • Para: Código Aethel")
    print("     • Verifica: Invariantes, provas formais")
    print("     • Exemplo: solve { x + y == 100 }")
    
    print("\n  2. Z3 Solver")
    print("     • Para: Matemática e lógica")
    print("     • Verifica: Equações, teoremas")
    print("     • Exemplo: ∀x. x + 0 = x")
    
    print("\n  3. Heuristic")
    print("     • Para: Código Python e texto")
    print("     • Verifica: Sintaxe, padrões")
    print("     • Exemplo: Código Python válido")
    
    print("\n  4. None")
    print("     • Para: Texto geral")
    print("     • Verifica: Nada (score neutro)")
    print("     • Exemplo: Explicações, documentação")


def demo_5_historical_learning():
    """Demo 5: Aprendizado histórico"""
    print("\n" + "=" * 80)
    print("DEMO 5: Aprendizado Histórico")
    print("=" * 80)
    
    distiller = AutonomousDistiller()
    
    print("\n📚 Simulando histórico de acertos:")
    
    # Simular histórico
    sources = ["gpt-4", "claude", "local-llama"]
    accuracies = [0.95, 0.90, 0.75]
    
    for source, acc in zip(sources, accuracies):
        # Adicionar histórico simulado
        for _ in range(10):
            import random
            passed = random.random() < acc
            distiller._update_history(source, passed)
    
    print("\n✅ Histórico atualizado:")
    
    for source in sources:
        hist_score = distiller._get_historical_accuracy(source)
        print(f"  • {source}: {hist_score:.1%} de acertos")
    
    print("\n💡 Como funciona:")
    print("   • Cada destilação atualiza o histórico")
    print("   • Mantém últimos 100 resultados")
    print("   • Score usa média dos últimos 10")
    print("   • Fontes novas começam com 50%")


def demo_6_full_distillation():
    """Demo 6: Destilação completa (mock)"""
    print("\n" + "=" * 80)
    print("DEMO 6: Destilação Completa")
    print("=" * 80)
    
    print("\n⚠️  Esta demo requer:")
    print("   • Ollama instalado e rodando")
    print("   • Chaves de API configuradas (opcional)")
    print("   • Judge disponível (opcional)")
    
    print("\n📝 Para testar com APIs reais:")
    print("""
    from diotec360.ai.autonomous_distiller import create_distiller_from_env
    
    # Criar distiller (detecta automaticamente o que está disponível)
    distiller = create_distiller_from_env()
    
    # Destilar resposta
    result = distiller.distill(
        prompt="Write a Python function to check if a number is prime"
    )
    
    # Ver resultado
    print(f"Melhor: {result.source}")
    print(f"Score: {result.confidence_score:.3f}")
    print(f"Explicação: {result.explanation}")
    print(f"Resposta: {result.text}")
    """)
    
    print("\n🔄 Fluxo de destilação:")
    print("   1. Consulta Local Engine (Ollama)")
    print("   2. Consulta Teacher APIs (GPT-4, Claude, DeepSeek)")
    print("   3. Detecta tipo de resposta")
    print("   4. Verifica com Judge/Z3")
    print("   5. Calcula confidence scores")
    print("   6. Seleciona melhor resposta")
    print("   7. Gera explicação")
    print("   8. Atualiza histórico")


def demo_7_statistics():
    """Demo 7: Estatísticas do distiller"""
    print("\n" + "=" * 80)
    print("DEMO 7: Estatísticas")
    print("=" * 80)
    
    distiller = AutonomousDistiller()
    
    # Simular algumas destilações
    print("\n🔬 Simulando destilações...")
    
    for i in range(5):
        import random
        source = random.choice(["gpt-4", "claude", "local-llama"])
        passed = random.random() > 0.3
        distiller._update_history(source, passed)
        distiller.total_distillations += 1
        if passed:
            distiller.verification_passes += 1
        else:
            distiller.verification_failures += 1
    
    # Obter estatísticas
    stats = distiller.get_statistics()
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de destilações: {stats['total_distillations']}")
    print(f"   Verificações aprovadas: {stats['verification_passes']}")
    print(f"   Verificações reprovadas: {stats['verification_failures']}")
    print(f"   Taxa de aprovação: {stats['pass_rate']:.1%}")
    print(f"   Fontes rastreadas: {stats['sources_tracked']}")
    
    print(f"\n🎯 Acurácia por fonte:")
    for source, acc in stats['accuracy_by_source'].items():
        print(f"   • {source}: {acc:.1%}")


def main():
    """Executa todas as demos"""
    print("=" * 80)
    print("AETHEL AUTONOMOUS DISTILLER - DEMONSTRAÇÃO COMPLETA")
    print("Epoch 4.0: Neural Nexus - O Cérebro que Aprende")
    print("=" * 80)
    
    demos = [
        ("Comparação Básica", demo_1_basic_comparison),
        ("Confidence Scoring", demo_2_confidence_scoring),
        ("Detecção de Tipos", demo_3_response_types),
        ("Métodos de Verificação", demo_4_verification_methods),
        ("Aprendizado Histórico", demo_5_historical_learning),
        ("Destilação Completa", demo_6_full_distillation),
        ("Estatísticas", demo_7_statistics)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Erro na demo {i}: {e}")
    
    print("\n" + "=" * 80)
    print("RESUMO: AUTONOMOUS DISTILLER")
    print("=" * 80)
    print("\n✅ Funcionalidades demonstradas:")
    print("   • Comparação de múltiplas respostas")
    print("   • Confidence scoring (verification + consistency + history)")
    print("   • Detecção automática de tipo de resposta")
    print("   • Verificação formal com Judge/Z3")
    print("   • Aprendizado histórico por fonte")
    print("   • Estatísticas de performance")
    
    print("\n🎯 Próximo passo:")
    print("   Task 4.0.4: Cognitive Persistence")
    print("   • Salvar respostas verificadas")
    print("   • Organizar por categoria")
    print("   • Preparar dataset para LoRA training")
    
    print("\n🏛️ [AUTONOMOUS DISTILLER: OPERATIONAL]")


if __name__ == "__main__":
    main()
