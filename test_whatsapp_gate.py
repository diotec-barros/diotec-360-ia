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
Teste do Diotec360-WhatsApp-Gate

Testa a integração do WhatsApp Gate com o sistema de memória cognitiva.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diotec360.core.whatsapp_gate import WhatsAppGate, create_whatsapp_message


def test_whatsapp_gate_basic():
    """Teste básico do WhatsApp Gate"""
    print("🧪 Testando Diotec360-WhatsApp-Gate...")
    
    # Inicializa WhatsApp Gate
    gate = WhatsAppGate()
    
    # Testa mensagem de consulta de mercado
    print("\n1. Testando consulta de mercado...")
    message = create_whatsapp_message(
        sender_id="test_user",
        content="Como está o Forex hoje?",
        message_type="text"
    )
    
    response = gate.process_message(message)
    
    print(f"   Resposta tipo: {response.response_type}")
    print(f"   Resposta tamanho: {len(response.content)} caracteres")
    print(f"   Anexos: {len(response.attachments)}")
    
    assert response.response_type == "text"
    assert len(response.content) > 0
    print("   ✅ Consulta de mercado funcionando")
    
    # Testa comando de trading
    print("\n2. Testando comando de trading...")
    message = create_whatsapp_message(
        sender_id="test_user",
        content="Compre EUR/USD $100",
        message_type="text"
    )
    
    response = gate.process_message(message)
    
    print(f"   Resposta tipo: {response.response_type}")
    print(f"   Resposta contém 'TRADE': {'TRADE' in response.content}")
    
    assert response.response_type == "receipt"
    assert "TRADE" in response.content
    print("   ✅ Comando de trading funcionando")
    
    # Testa consulta de histórico
    print("\n3. Testando consulta de histórico...")
    message = create_whatsapp_message(
        sender_id="test_user",
        content="Qual foi meu último trade?",
        message_type="text"
    )
    
    response = gate.process_message(message)
    
    print(f"   Resposta tipo: {response.response_type}")
    print(f"   Resposta contém 'HISTÓRICO': {'HISTÓRICO' in response.content}")
    
    assert response.response_type == "text"
    assert len(response.content) > 0
    print("   ✅ Consulta de histórico funcionando")
    
    # Testa ajuda
    print("\n4. Testando pedido de ajuda...")
    message = create_whatsapp_message(
        sender_id="test_user",
        content="Ajuda",
        message_type="text"
    )
    
    response = gate.process_message(message)
    
    print(f"   Resposta tipo: {response.response_type}")
    print(f"   Resposta contém 'AJUDA': {'AJUDA' in response.content}")
    
    assert response.response_type == "text"
    assert "AJUDA" in response.content
    print("   ✅ Pedido de ajuda funcionando")
    
    print("\n✅ Todos os testes do WhatsApp Gate passaram!")


def test_whatsapp_gate_integration():
    """Teste de integração com memória cognitiva"""
    print("\n🧠 Testando integração com memória cognitiva...")
    
    from diotec360.core.memory import get_cognitive_memory
    
    gate = WhatsAppGate()
    memory = get_cognitive_memory()
    
    # Processa algumas mensagens
    test_messages = [
        "Como está o Forex?",
        "Compre EUR/USD $50",
        "Qual meu histórico?"
    ]
    
    for msg in test_messages:
        message = create_whatsapp_message("test_user", msg)
        gate.process_message(message)
    
    # Verifica se as memórias foram armazenadas
    stats = memory.get_statistics()
    
    print(f"   Memórias totais: {stats['total_memories']}")
    print(f"   Entradas de contexto: {stats['total_context_entries']}")
    
    assert stats['total_context_entries'] >= len(test_messages) * 2  # Mensagens + respostas
    print("   ✅ Integração com memória cognitiva funcionando")


if __name__ == "__main__":
    print("="*60)
    print("🧪 TESTE DO DIOTEC360-WHATSAPP-GATE")
    print("="*60)
    
    try:
        test_whatsapp_gate_basic()
        test_whatsapp_gate_integration()
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("="*60)
        print("\n🎯 WhatsApp Gate está funcionando corretamente:")
        print("   • Processamento de mensagens ✓")
        print("   • Análise de intenções ✓")
        print("   • Integração com Forex ✓")
        print("   • Integração com memória ✓")
        print("   • Geração de comprovantes ✓")
        
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)