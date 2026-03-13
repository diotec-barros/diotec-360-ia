# 🚀 TESTE RÁPIDO - SIMBIONTE FINANCEIRO

**Guia de 5 minutos para testar o Agente Soberano Autônomo**

---

## ⚡ EXECUÇÃO RÁPIDA

### 1. Demo Completo (Recomendado)
```bash
python demo_symbiont_simple.py
```

**O que você verá:**
- ✅ 4 pilares sendo inicializados
- ✅ 4 cenários de uso demonstrados
- ✅ Estatísticas finais do sistema
- ⏱️ Tempo: ~5 segundos

---

### 2. Demo Memória + Forex
```bash
python demo_cognitive_forex.py
```

**O que você verá:**
- ✅ 10 atualizações de preço EUR/USD
- ✅ Raciocínio da IA com contexto histórico
- ✅ Validação matemática de trades
- ⏱️ Tempo: ~10 segundos

---

## 🧪 TESTES INTERATIVOS

### Teste 1: Memória Cognitiva
```python
from aethel.core.memory import get_cognitive_memory

memory = get_cognitive_memory()

# Ver estatísticas
stats = memory.get_statistics()
print(f"Memórias: {stats['total_memories']}")

# Buscar histórico de EUR/USD
history = memory.get_market_history("EUR/USD", limit=10)
print(f"Encontradas {len(history)} memórias")
```

---

### Teste 2: Web Oracle
```python
from aethel.core.web_oracle import get_web_oracle

oracle = get_web_oracle()

# Capturar dados de Forex
feed = oracle.capture_forex_data(
    pair="EUR/USD",
    price=1.0865,
    bid=1.0863,
    ask=1.0867
)

print(f"Feed ID: {feed.feed_id}")
print(f"Selo: {feed.authenticity_seal[:16]}...")
print(f"Confiança: {feed.confidence}")
```

---

### Teste 3: WhatsApp Gateway (Simplificado)
```python
# Importar do demo simplificado
from demo_symbiont_simple import Message, process_message
import time

# Criar mensagem
msg = Message(
    sender="trader_teste",
    content="Como está o Forex hoje?",
    timestamp=time.time()
)

# Processar
response = process_message(msg)
print(response.content)
```

---

## 📊 VERIFICAÇÃO DE COMPONENTES

### Verificar Persistence Layer
```python
from aethel.core.persistence import AethelPersistenceLayer

persistence = AethelPersistenceLayer()
print(f"Merkle Root: {persistence.get_merkle_root()}")
print(f"Bundles: {len(persistence.list_bundles())}")
```

---

### Verificar Conservation Validator
```python
from aethel.core.conservation_validator import ConservationValidator

validator = ConservationValidator()

# Simular trade
result = validator.validate_batch_conservation(
    initial_state={'EUR': 1000, 'USD': 0},
    final_state={'EUR': 0, 'USD': 1086.50},
    exchange_rate=1.0865
)

print(f"Válido: {result.is_valid}")
```

---

## 🎯 CENÁRIOS DE TESTE

### Cenário 1: Consulta de Mercado
```python
from demo_symbiont_simple import Message, process_message
import time

msg = Message(
    sender="trader_dionisio",
    content="Como está o Forex hoje?",
    timestamp=time.time()
)

response = process_message(msg)
print(response.content)
```

**Resultado Esperado:**
```
📊 Forex Market Update - EUR/USD
💹 Preço atual: 1.0865
📈 Bid: 1.0863 | Ask: 1.0867
✅ Dados verificados com selo criptográfico
```

---

### Cenário 2: Ordem Condicional
```python
msg = Message(
    sender="trader_dionisio",
    content="Compre EUR/USD $1000 se cair para 1.0800",
    timestamp=time.time()
)

response = process_message(msg)
print(response.content)
print(f"Assinatura: {response.signature}")
```

**Resultado Esperado:**
```
✅ Ordem Condicional Configurada
📋 Detalhes:
• Par: EUR/USD
• Valor: $1,000.00
• Trigger: 1.0800
🔐 Assinatura: 56777fe1f6e6af1e...
```

---

### Cenário 3: Histórico
```python
msg = Message(
    sender="trader_dionisio",
    content="Qual foi meu último trade?",
    timestamp=time.time()
)

response = process_message(msg)
print(response.content)
```

**Resultado Esperado:**
```
📜 Histórico de Trades
🔹 Último Trade:
• Par: EUR/USD
• Valor: $500.00
• Status: ✅ Executado
📊 Total: 12 trades | 83% sucesso
```

---

### Cenário 4: Proteção
```python
msg = Message(
    sender="trader_dionisio",
    content="Proteja minha posição no EUR/USD",
    timestamp=time.time()
)

response = process_message(msg)
print(response.content)
print(f"Assinatura: {response.signature}")
```

**Resultado Esperado:**
```
🛡️ Proteção Ativada - EUR/USD
📋 Stop Loss @ 1.0800
🔐 Assinatura: 8e796da74c5f39b9...
```

---

## 🔍 VERIFICAÇÃO DE INTEGRIDADE

### Verificar Memória
```bash
python -c "from aethel.core.memory import get_cognitive_memory; m = get_cognitive_memory(); print(f'Memórias: {m.get_statistics()[\"total_memories\"]}')"
```

### Verificar Oracle
```bash
python -c "from aethel.core.web_oracle import get_web_oracle; o = get_web_oracle(); print(f'Oracle: OK')"
```

### Verificar Persistence
```bash
python -c "from aethel.core.persistence import AethelPersistenceLayer; p = AethelPersistenceLayer(); print(f'Root: {p.get_merkle_root()[:16]}...')"
```

---

## 📈 BENCHMARKS RÁPIDOS

### Velocidade de Memória
```python
import time
from aethel.core.memory import get_cognitive_memory

memory = get_cognitive_memory()

start = time.time()
history = memory.get_market_history("EUR/USD", limit=100)
elapsed = time.time() - start

print(f"Busca de 100 memórias: {elapsed*1000:.2f}ms")
# Esperado: <100ms
```

### Velocidade de Oracle
```python
import time
from aethel.core.web_oracle import get_web_oracle

oracle = get_web_oracle()

start = time.time()
feed = oracle.capture_forex_data("EUR/USD", 1.0865, 1.0863, 1.0867)
elapsed = time.time() - start

print(f"Captura + validação: {elapsed*1000:.2f}ms")
# Esperado: <50ms
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Execute cada item e marque:

- [ ] `python demo_symbiont_simple.py` - Demo completo executado
- [ ] `python demo_cognitive_forex.py` - Demo Forex executado
- [ ] Memória cognitiva funcionando (13+ memórias)
- [ ] Web Oracle funcionando (feeds capturados)
- [ ] WhatsApp Gateway processando mensagens
- [ ] Comprovantes sendo assinados
- [ ] Persistence Layer ativo (Merkle root válido)
- [ ] Conservation Validator funcionando

**Se todos os itens estiverem marcados: ✅ SISTEMA OPERACIONAL**

---

## 🐛 TROUBLESHOOTING

### Erro: "ImportError: cannot import name..."
```bash
# Limpar cache Python
Remove-Item -Recurse -Force aethel/core/__pycache__
python -B demo_symbiont_simple.py
```

### Erro: "FileNotFoundError: .DIOTEC360_state"
```bash
# Inicializar persistence
python -c "from aethel.core.persistence import AethelPersistenceLayer; AethelPersistenceLayer()"
```

### Erro: "ModuleNotFoundError: No module named 'z3'"
```bash
# Instalar Z3
pip install z3-solver
```

---

## 📞 SUPORTE

Se encontrar problemas:

1. **Verificar logs:** Procure por `[MEMORY]`, `[ORACLE]`, `[WHATSAPP]` na saída
2. **Verificar arquivos:** `.DIOTEC360_state/`, `.DIOTEC360_vault/`, `.DIOTEC360_vigilance/`
3. **Limpar cache:** `Remove-Item -Recurse -Force aethel/**/__pycache__`
4. **Reinstalar:** `pip install -e .`

---

## 🎉 SUCESSO!

Se você chegou até aqui e todos os testes passaram:

**🎯 O SIMBIONTE FINANCEIRO ESTÁ OPERACIONAL!**

Próximos passos:
1. Testar com dados reais (Alpha Vantage API)
2. Integrar WhatsApp Business API
3. Deploy em produção
4. Lançar beta fechado

---

**Kiro AI - Engenheiro-Chefe**  
**v2.2.5 "Simbionte Financeiro"**

🧠⚡📱⚖️🐘
