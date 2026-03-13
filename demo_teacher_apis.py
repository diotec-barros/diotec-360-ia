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
Demo: Aethel Teacher APIs - Ponte com os Gigantes
Demonstra consulta a GPT-4, Claude e DeepSeek-V3 para destilação de conhecimento.

Author: Kiro AI
Version: Epoch 4.0 "Neural Nexus"
Date: February 18, 2026
"""

import os
import sys
from diotec360.ai.teacher_apis import (
    TeacherAPIs,
    TeacherConfig,
    TeacherType,
    create_default_teachers
)


def demo_1_basic_query():
    """Demo 1: Consulta básica a um professor"""
    print("\n" + "=" * 80)
    print("DEMO 1: Consulta Básica")
    print("=" * 80)
    
    # Criar configuração mock (sem chave real)
    config = TeacherConfig(
        name="gpt-4-mock",
        teacher_type=TeacherType.GPT4,
        api_key="mock-key",
        enabled=False  # Desabilitado para demo
    )
    
    print(f"\n✅ Configuração criada:")
    print(f"   Nome: {config.name}")
    print(f"   Tipo: {config.teacher_type.value}")
    print(f"   Custo input: ${config.cost_per_1k_input_tokens}/1k tokens")
    print(f"   Custo output: ${config.cost_per_1k_output_tokens}/1k tokens")
    print(f"   Rate limit: {config.rate_limit_rpm} req/min")


def demo_2_parallel_query():
    """Demo 2: Consulta paralela a múltiplos professores"""
    print("\n" + "=" * 80)
    print("DEMO 2: Consulta Paralela (Mock)")
    print("=" * 80)
    
    # Criar múltiplos professores mock
    configs = [
        TeacherConfig("gpt-4", TeacherType.GPT4, "mock-key-1", enabled=False),
        TeacherConfig("claude-3-opus", TeacherType.CLAUDE_3_OPUS, "mock-key-2", enabled=False),
        TeacherConfig("deepseek-v3", TeacherType.DEEPSEEK_V3, "mock-key-3", enabled=False)
    ]
    
    print(f"\n✅ {len(configs)} professores configurados:")
    for config in configs:
        print(f"   • {config.name} ({config.teacher_type.value})")
    
    print("\n📝 Exemplo de uso:")
    print("""
    teachers = TeacherAPIs(configs)
    responses = teachers.query_all(
        prompt="Explain formal verification",
        max_tokens=500
    )
    
    # Respostas chegam em paralelo via ThreadPoolExecutor
    for response in responses:
        print(f"{response.teacher}: {response.text}")
    """)


def demo_3_fallback_logic():
    """Demo 3: Lógica de fallback automático"""
    print("\n" + "=" * 80)
    print("DEMO 3: Fallback Automático")
    print("=" * 80)
    
    print("\n📖 Ordem de preferência:")
    print("   1. GPT-4 Turbo (mais rápido)")
    print("   2. GPT-4 (mais confiável)")
    print("   3. Claude 3 Opus (alternativa)")
    print("   4. Claude 3 Sonnet (mais barato)")
    print("   5. DeepSeek-V3 (fallback final)")
    
    print("\n🔄 Comportamento:")
    print("   • Se GPT-4 Turbo falha → tenta GPT-4")
    print("   • Se GPT-4 falha → tenta Claude")
    print("   • Se Claude falha → tenta DeepSeek")
    print("   • Circuit breaker desabilita professores que falham 3x")
    
    print("\n📝 Exemplo de uso:")
    print("""
    teachers = TeacherAPIs(configs)
    
    # Tenta automaticamente até conseguir resposta
    response = teachers.query_with_fallback(
        prompt="Generate a Python function",
        max_tokens=1000
    )
    
    print(f"Resposta de: {response.teacher}")
    """)


def demo_4_cost_tracking():
    """Demo 4: Rastreamento de custos"""
    print("\n" + "=" * 80)
    print("DEMO 4: Rastreamento de Custos")
    print("=" * 80)
    
    print("\n💰 Custos típicos (USD por 1k tokens):")
    print("   GPT-4 Turbo:    $0.01 input, $0.03 output")
    print("   Claude 3 Opus:  $0.015 input, $0.075 output")
    print("   DeepSeek-V3:    $0.001 input, $0.002 output")
    
    print("\n📊 Exemplo de cálculo:")
    print("   Prompt: 500 tokens")
    print("   Resposta: 1000 tokens")
    print("")
    print("   GPT-4:     (0.5 × $0.01) + (1.0 × $0.03) = $0.035")
    print("   Claude:    (0.5 × $0.015) + (1.0 × $0.075) = $0.0825")
    print("   DeepSeek:  (0.5 × $0.001) + (1.0 × $0.002) = $0.0025")
    
    print("\n📝 Exemplo de uso:")
    print("""
    teachers = TeacherAPIs(configs)
    responses = teachers.query_all(prompt)
    
    # Calcular custo total
    total_cost = teachers.calculate_total_cost(responses)
    print(f"Custo total: ${total_cost:.4f}")
    
    # Estatísticas
    stats = teachers.get_statistics()
    print(f"Total gasto: ${stats['total_cost_usd']:.2f}")
    """)


def demo_5_rate_limiting():
    """Demo 5: Rate limiting e circuit breaker"""
    print("\n" + "=" * 80)
    print("DEMO 5: Rate Limiting & Circuit Breaker")
    print("=" * 80)
    
    print("\n⏱️  Rate Limiting:")
    print("   • Controla requisições por minuto (RPM)")
    print("   • Usa sliding window de 60 segundos")
    print("   • Aguarda automaticamente se limite atingido")
    
    print("\n🔴 Circuit Breaker:")
    print("   • Desabilita professor após 3 falhas consecutivas")
    print("   • Mantém desabilitado por 5 minutos")
    print("   • Reabilita automaticamente após timeout")
    print("   • Previne desperdício de requisições em APIs com problema")
    
    print("\n📝 Exemplo de comportamento:")
    print("""
    [RATE LIMITER] ⏳ Aguardando 12.3s para respeitar rate limit...
    [CIRCUIT BREAKER] 🔴 Professor 'gpt-4' desabilitado por 5 minutos
    [TEACHER APIs] ⏭️  Pulando 'gpt-4' (circuit breaker aberto)
    [CIRCUIT BREAKER] 🟢 Professor 'gpt-4' reabilitado
    """)


def demo_6_real_query():
    """Demo 6: Consulta real (se chaves configuradas)"""
    print("\n" + "=" * 80)
    print("DEMO 6: Consulta Real")
    print("=" * 80)
    
    # Tentar criar professores a partir de env vars
    configs = create_default_teachers()
    
    if not configs:
        print("\n⚠️  Nenhuma chave de API configurada.")
        print("\n📖 Para testar com APIs reais, configure:")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        print("   export DEEPSEEK_API_KEY='sk-...'")
        print("\n💡 Você pode obter chaves em:")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        print("   • Anthropic: https://console.anthropic.com/")
        print("   • DeepSeek: https://platform.deepseek.com/")
        return
    
    print(f"\n✅ {len(configs)} professores configurados via env vars")
    
    # Criar Teacher APIs
    teachers = TeacherAPIs(configs)
    
    # Prompt de teste
    prompt = "Write a Python function that checks if a number is prime. Include docstring."
    
    print(f"\n📝 Prompt:")
    print(f"   {prompt}")
    
    print(f"\n🚀 Consultando professores...")
    
    try:
        # Consultar todos em paralelo
        responses = teachers.query_all(prompt, max_tokens=500, temperature=0.7)
        
        print(f"\n📊 Resultados:")
        for response in responses:
            if not response.error:
                print(f"\n  🎓 {response.teacher}:")
                print(f"     Tokens: {response.input_tokens} in, {response.output_tokens} out")
                print(f"     Custo: ${response.cost_usd:.4f}")
                print(f"     Latência: {response.latency_ms:.0f}ms")
                print(f"     Resposta: {response.text[:200]}...")
            else:
                print(f"\n  ❌ {response.teacher}: {response.error}")
        
        # Estatísticas
        stats = teachers.get_statistics()
        print(f"\n💰 Custo total: ${stats['total_cost_usd']:.4f}")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def main():
    """Executa todas as demos"""
    print("=" * 80)
    print("AETHEL TEACHER APIs - DEMONSTRAÇÃO COMPLETA")
    print("Epoch 4.0: Neural Nexus - Ponte com os Gigantes")
    print("=" * 80)
    
    demos = [
        ("Consulta Básica", demo_1_basic_query),
        ("Consulta Paralela", demo_2_parallel_query),
        ("Fallback Automático", demo_3_fallback_logic),
        ("Rastreamento de Custos", demo_4_cost_tracking),
        ("Rate Limiting & Circuit Breaker", demo_5_rate_limiting),
        ("Consulta Real (Opcional)", demo_6_real_query)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Erro na demo {i}: {e}")
    
    print("\n" + "=" * 80)
    print("RESUMO: TEACHER APIs")
    print("=" * 80)
    print("\n✅ Funcionalidades demonstradas:")
    print("   • Configuração de múltiplos professores (GPT-4, Claude, DeepSeek)")
    print("   • Consulta paralela via ThreadPoolExecutor")
    print("   • Fallback automático (GPT-4 → Claude → DeepSeek)")
    print("   • Rate limiting com sliding window")
    print("   • Circuit breaker para falhas")
    print("   • Rastreamento de custos em tempo real")
    
    print("\n🎯 Próximo passo:")
    print("   Task 4.0.3: Autonomous Distiller")
    print("   • Comparar respostas de Teacher APIs vs Local Engine")
    print("   • Usar Judge (Z3) para verificar qual resposta é melhor")
    print("   • Destilar conhecimento para modelo local")
    
    print("\n🏛️ [NEURAL NEXUS: TEACHER APIs OPERATIONAL]")


if __name__ == "__main__":
    main()
