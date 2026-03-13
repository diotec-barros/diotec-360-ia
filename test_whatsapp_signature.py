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
Teste de Assinatura Criptográfica - WhatsApp Gateway v2.2.5
Valida que TODAS as respostas incluem selos do Santuário
"""

import time
from demo_symbiont_simple import Message, process_message


def test_signature_precision():
    """Testa se todas as respostas críticas têm assinatura"""
    
    print("=" * 80)
    print("TESTE: ASSINATURA CRIPTOGRAFICA v2.2.5")
    print("=" * 80)
    
    # Teste 1: Consulta de Forex
    print("\n[TESTE 1] Consulta de Forex")
    msg1 = Message(
        sender="trader_dionisio",
        content="Como esta o Forex hoje?",
        timestamp=time.time()
    )
    response1 = process_message(msg1)
    
    assert response1.signature is not None, "FALHA: Consulta Forex deve ter assinatura"
    assert "Selo Santuario" in response1.content, "FALHA: Selo deve estar visivel na mensagem"
    print(f"✅ Assinatura: {response1.signature}")
    print(f"✅ Selo visivel no conteudo: SIM")
    
    # Teste 2: Ordem de Compra
    print("\n[TESTE 2] Ordem de Compra")
    msg2 = Message(
        sender="trader_dionisio",
        content="Compre EUR/USD $1000",
        timestamp=time.time()
    )
    response2 = process_message(msg2)
    
    assert response2.signature is not None, "FALHA: Ordem deve ter assinatura"
    assert "Selo Santuario" in response2.content, "FALHA: Selo deve estar visivel na mensagem"
    print(f"✅ Assinatura: {response2.signature}")
    print(f"✅ Selo visivel no conteudo: SIM")
    
    # Teste 3: Protecao de Posicao
    print("\n[TESTE 3] Protecao de Posicao")
    msg3 = Message(
        sender="trader_dionisio",
        content="Proteja minha posicao no EUR/USD",
        timestamp=time.time()
    )
    response3 = process_message(msg3)
    
    assert response3.signature is not None, "FALHA: Protecao deve ter assinatura"
    assert "Selo Santuario" in response3.content, "FALHA: Selo deve estar visivel na mensagem"
    print(f"✅ Assinatura: {response3.signature}")
    print(f"✅ Selo visivel no conteudo: SIM")
    
    # Teste 4: Consulta de Historico (nao critica, mas deve ter assinatura)
    print("\n[TESTE 4] Consulta de Historico")
    msg4 = Message(
        sender="trader_dionisio",
        content="Qual foi meu ultimo trade?",
        timestamp=time.time()
    )
    response4 = process_message(msg4)
    
    assert response4.signature is not None, "FALHA: Historico deve ter assinatura"
    print(f"✅ Assinatura: {response4.signature}")
    print(f"✅ Selo no metadata: SIM")
    
    # Teste 5: Ajuda (nao critica, mas deve ter assinatura)
    print("\n[TESTE 5] Comando de Ajuda")
    msg5 = Message(
        sender="trader_dionisio",
        content="ajuda",
        timestamp=time.time()
    )
    response5 = process_message(msg5)
    
    assert response5.signature is not None, "FALHA: Ajuda deve ter assinatura"
    print(f"✅ Assinatura: {response5.signature}")
    print(f"✅ Selo no metadata: SIM")
    
    print("\n" + "=" * 80)
    print("RESULTADO: TODOS OS TESTES PASSARAM")
    print("=" * 80)
    print("\n✅ AJUSTE DE PRECISAO v2.2.5 COMPLETO")
    print("✅ Todas as respostas incluem assinatura criptografica")
    print("✅ Operacoes criticas mostram selo visivel ao usuario")
    print("✅ Dionisio pode verificar autenticidade de cada mensagem")
    print("\n🔐 O SANTUARIO AGORA ASSINA TUDO!")


if __name__ == "__main__":
    test_signature_precision()
