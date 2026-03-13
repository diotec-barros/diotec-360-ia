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
Teste Rápido do MVP Comercial
Valida todos os componentes em menos de 1 minuto

Autor: Kiro AI - Engenheiro-Chefe
Versão: v2.2.6 "Real-Sense"
Data: 11 de Fevereiro de 2026
"""

import os
import sys
from datetime import datetime


def print_header(title: str) -> None:
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_api_key() -> bool:
    """Testa se a API key está configurada"""
    print("🔑 Testando API Key...")
    
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        print("❌ API key não configurada")
        print("\nComo configurar:")
        print("  Windows (PowerShell):")
        print('    $env:ALPHA_VANTAGE_API_KEY="SUA_CHAVE"')
        print("\n  Windows (CMD):")
        print('    set ALPHA_VANTAGE_API_KEY=SUA_CHAVE')
        print("\n  Linux/Mac:")
        print('    export ALPHA_VANTAGE_API_KEY="SUA_CHAVE"')
        print("\nObtenha chave grátis em:")
        print("  https://www.alphavantage.co/support/#api-key")
        return False
    
    if api_key == 'demo':
        print("⚠️  API key 'demo' detectada (não retorna dados reais)")
        print("   Configure sua chave real para testar com dados de mercado")
        return False
    
    print(f"✅ API key configurada: {api_key[:8]}...")
    return True


def test_real_forex_api() -> bool:
    """Testa a Real Forex API"""
    print("\n🌐 Testando Real Forex API...")
    
    try:
        from diotec360.core.real_forex_api import get_real_forex_oracle
        
        oracle = get_real_forex_oracle()
        print("✅ Oracle inicializado")
        
        # Tenta obter cotação
        print("   Consultando EUR/USD...")
        quote = oracle.get_quote("EUR/USD")
        
        if quote:
            print(f"✅ Dados reais capturados!")
            print(f"   • Par: {quote.pair}")
            print(f"   • Preço: {quote.price:.4f}")
            print(f"   • Provider: {quote.provider}")
            print(f"   • Selo: {quote.authenticity_seal[:16]}...")
            
            # Valida selo
            is_valid = oracle.validate_quote(quote)
            print(f"   • Selo válido: {'✅ SIM' if is_valid else '❌ NÃO'}")
            
            return True
        else:
            print("❌ Não foi possível obter dados")
            print("   Possíveis causas:")
            print("   • Rate limit excedido (25 requests/dia)")
            print("   • Problema de conexão")
            print("   • API key inválida")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_cognitive_memory() -> bool:
    """Testa a Cognitive Memory"""
    print("\n🧠 Testando Cognitive Memory...")
    
    try:
        from diotec360.core.memory import get_cognitive_memory
        
        memory = get_cognitive_memory()
        print("✅ Memory System inicializado")
        
        # Obtém estatísticas
        stats = memory.get_statistics()
        print(f"   • Total de memórias: {stats['total_memories']}")
        print(f"   • Tipos de memória: {len(stats['by_type'])}")
        
        # Testa armazenamento
        test_memory = memory.store_market_data(
            symbol="TEST/USD",
            price=1.0,
            timestamp=datetime.now().timestamp(),
            source="test"
        )
        print(f"✅ Memória de teste armazenada: {test_memory.memory_id[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def test_whatsapp_gateway() -> bool:
    """Testa o WhatsApp Gateway"""
    print("\n📱 Testando WhatsApp Gateway...")
    
    try:
        from demo_symbiont_simple import Message, process_message
        import time
        
        print("✅ Gateway inicializado")
        
        # Testa mensagem
        msg = Message(
            sender="test_user",
            content="Como está o Forex?",
            timestamp=time.time()
        )
        
        response = process_message(msg)
        print("✅ Mensagem processada")
        
        if response.signature:
            print(f"   • Assinatura: {response.signature[:16]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


def main():
    """Executa todos os testes"""
    print_header("MVP COMERCIAL - TESTE RÁPIDO")
    
    print(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("Versão: v2.2.6 'Real-Sense'")
    
    results = []
    
    # Teste 1: API Key
    print_header("TESTE 1: API Key Configuration")
    results.append(("API Key", test_api_key()))
    
    # Teste 2: Real Forex API
    print_header("TESTE 2: Real Forex API")
    results.append(("Real Forex API", test_real_forex_api()))
    
    # Teste 3: Cognitive Memory
    print_header("TESTE 3: Cognitive Memory")
    results.append(("Cognitive Memory", test_cognitive_memory()))
    
    # Teste 4: WhatsApp Gateway
    print_header("TESTE 4: WhatsApp Gateway")
    results.append(("WhatsApp Gateway", test_whatsapp_gateway()))
    
    # Resumo
    print_header("RESUMO DOS TESTES")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\nO MVP Comercial está 100% operacional!")
        print("\nPróximos passos:")
        print("  1. Selecionar 3 traders alpha")
        print("  2. Fornecer acesso ao sistema")
        print("  3. Coletar feedback")
        print("  4. Lançar beta com 10 traders")
    else:
        print("\n⚠️  Alguns testes falharam")
        print("\nVerifique os erros acima e:")
        print("  1. Configure a API key se necessário")
        print("  2. Verifique a conexão com internet")
        print("  3. Execute novamente: python test_mvp_quick.py")
    
    print("\n" + "=" * 80)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
