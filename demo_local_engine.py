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
Demo: Aethel Local Engine
Demonstração da integração com Ollama para inteligência local.

Este script demonstra:
1. Detecção automática do Ollama
2. Listagem de modelos instalados
3. Geração de código com modelo local
4. Streaming de resposta para UX responsiva

Author: Kiro AI - Engenheiro-Chefe
Version: Epoch 4.0 "Neural Nexus"
Date: February 5, 2026
"""

from diotec360.ai.local_engine import (
    LocalEngine,
    LocalInferenceRequest,
    OllamaNotAvailableError,
    ModelNotFoundError
)


def demo_basic_inference():
    """Demonstra inferência básica com modelo local"""
    print("\n" + "=" * 80)
    print("DEMO 1: INFERÊNCIA BÁSICA")
    print("=" * 80)
    
    engine = LocalEngine()
    
    try:
        # Verificar Ollama
        engine.check_ollama_available()
        
        # Listar modelos
        models = engine.list_models()
        
        if not models:
            print("\n❌ Nenhum modelo instalado.")
            print("\n📥 Para instalar DeepSeek-Coder:")
            print("   ollama pull deepseek-coder:7b")
            return
        
        # Usar primeiro modelo disponível
        model = models[0]
        print(f"\n🧠 Usando modelo: {model.name}")
        
        # Criar requisição
        request = LocalInferenceRequest(
            prompt="Write a Python function to check if a number is prime",
            model=model.name,
            temperature=0.7,
            max_tokens=300
        )
        
        print(f"\n💭 Prompt: {request.prompt}")
        print("\n⏳ Gerando resposta...")
        
        # Gerar resposta
        response = engine.generate(request)
        
        print(f"\n✅ Resposta gerada:")
        print("-" * 80)
        print(response.text)
        print("-" * 80)
        
        print(f"\n📊 Métricas:")
        print(f"   • Tokens gerados: {response.tokens_generated}")
        print(f"   • Latência: {response.latency_ms:.0f}ms")
        print(f"   • Throughput: {response.tokens_per_second:.1f} tokens/s")
        
    except OllamaNotAvailableError as e:
        print(f"\n❌ Erro: {e}")
        print("\n📖 Guia de instalação:")
        print("   1. Visite: https://ollama.ai")
        print("   2. Baixe e instale Ollama")
        print("   3. Execute: ollama pull deepseek-coder:7b")
        print("   4. Execute este script novamente")


def demo_streaming():
    """Demonstra streaming de resposta para UX responsiva"""
    print("\n" + "=" * 80)
    print("DEMO 2: STREAMING (UX RESPONSIVA)")
    print("=" * 80)
    
    engine = LocalEngine()
    
    try:
        models = engine.list_models()
        
        if not models:
            print("\n❌ Nenhum modelo instalado.")
            return
        
        model = models[0]
        print(f"\n🧠 Usando modelo: {model.name}")
        
        # Criar requisição
        request = LocalInferenceRequest(
            prompt="Explain how blockchain works in simple terms",
            model=model.name,
            temperature=0.8,
            max_tokens=200
        )
        
        print(f"\n💭 Prompt: {request.prompt}")
        print("\n✨ Resposta (streaming):")
        print("-" * 80)
        
        # Gerar com streaming
        for token in engine.stream_generate(request):
            print(token, end='', flush=True)
        
        print("\n" + "-" * 80)
        print("\n✅ Streaming completo!")
        
    except OllamaNotAvailableError as e:
        print(f"\n❌ Erro: {e}")


def demo_model_management():
    """Demonstra gerenciamento de modelos"""
    print("\n" + "=" * 80)
    print("DEMO 3: GERENCIAMENTO DE MODELOS")
    print("=" * 80)
    
    engine = LocalEngine()
    
    try:
        # Listar modelos instalados
        models = engine.list_models()
        
        print(f"\n📚 Modelos instalados: {len(models)}")
        
        for model in models:
            print(f"\n   🤖 {model.name}")
            print(f"      • Tamanho: {model.size_gb:.2f} GB")
            print(f"      • Parâmetros: ~{model.parameters/1e9:.1f}B")
            print(f"      • Família: {model.family}")
        
        # Mostrar modelos recomendados
        print("\n💡 Modelos recomendados:")
        recommendations = engine.get_recommended_models()
        
        for use_case, model_name in recommendations.items():
            installed = "✅" if any(m.name == model_name for m in models) else "❌"
            print(f"   {installed} {use_case.capitalize()}: {model_name}")
        
        # Estatísticas
        stats = engine.get_statistics()
        print(f"\n📊 Estatísticas:")
        print(f"   • Ollama disponível: {'✅' if stats['ollama_available'] else '❌'}")
        print(f"   • Modelos instalados: {stats['models_installed']}")
        print(f"   • Espaço total: {stats['total_size_gb']:.2f} GB")
        
    except OllamaNotAvailableError as e:
        print(f"\n❌ Erro: {e}")


def demo_code_generation():
    """Demonstra geração de código Aethel"""
    print("\n" + "=" * 80)
    print("DEMO 4: GERAÇÃO DE CÓDIGO AETHEL")
    print("=" * 80)
    
    engine = LocalEngine()
    
    try:
        models = engine.list_models()
        
        if not models:
            print("\n❌ Nenhum modelo instalado.")
            return
        
        # Preferir DeepSeek-Coder se disponível
        model = None
        for m in models:
            if 'deepseek' in m.name.lower() or 'code' in m.name.lower():
                model = m
                break
        
        if not model:
            model = models[0]
        
        print(f"\n🧠 Usando modelo: {model.name}")
        
        # Criar requisição com contexto Aethel
        request = LocalInferenceRequest(
            prompt="""Write an Aethel smart contract for a simple token transfer with conservation checking.
            
The contract should:
1. Define a transfer function
2. Check sender has sufficient balance
3. Ensure conservation (total supply unchanged)
4. Use Aethel syntax with 'ensure' statements""",
            model=model.name,
            temperature=0.5,  # Mais determinístico para código
            max_tokens=400,
            system="You are an expert in Aethel, a formally verified smart contract language. Generate clean, correct Aethel code."
        )
        
        print(f"\n💭 Gerando contrato Aethel...")
        print("\n⏳ Aguarde...")
        
        # Gerar código
        response = engine.generate(request)
        
        print(f"\n✅ Código gerado:")
        print("=" * 80)
        print(response.text)
        print("=" * 80)
        
        print(f"\n📊 Métricas:")
        print(f"   • Tokens: {response.tokens_generated}")
        print(f"   • Latência: {response.latency_ms:.0f}ms")
        print(f"   • Throughput: {response.tokens_per_second:.1f} tokens/s")
        
        print(f"\n💡 Próximo passo: Enviar para Judge para verificação formal!")
        
    except OllamaNotAvailableError as e:
        print(f"\n❌ Erro: {e}")


def main():
    """Executa todas as demos"""
    print("\n" + "=" * 80)
    print("🌌 AETHEL LOCAL ENGINE - DEMONSTRAÇÃO COMPLETA")
    print("=" * 80)
    print("\nEste demo mostra a integração da Aethel com Ollama para")
    print("inteligência local sem dependência de APIs externas.")
    print("\n" + "=" * 80)
    
    # Demo 1: Inferência básica
    demo_basic_inference()
    
    # Demo 2: Streaming
    input("\n\n⏸️  Pressione ENTER para continuar para Demo 2...")
    demo_streaming()
    
    # Demo 3: Gerenciamento de modelos
    input("\n\n⏸️  Pressione ENTER para continuar para Demo 3...")
    demo_model_management()
    
    # Demo 4: Geração de código Aethel
    input("\n\n⏸️  Pressione ENTER para continuar para Demo 4...")
    demo_code_generation()
    
    print("\n" + "=" * 80)
    print("✅ DEMONSTRAÇÃO COMPLETA!")
    print("=" * 80)
    print("\n🚀 Próximos passos:")
    print("   1. Implementar Teacher APIs (GPT-4, Claude, DeepSeek)")
    print("   2. Implementar Destilador Autônomo (comparação + verificação)")
    print("   3. Implementar LoRA Training (fine-tuning local)")
    print("   4. Implementar Inference Sharding (distribuição P2P)")
    print("\n🌌 O Neural Nexus está nascendo!")
    print("=" * 80)


if __name__ == "__main__":
    main()
