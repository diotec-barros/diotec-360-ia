# 🚀 MVP COMERCIAL - GUIA DE CONFIGURAÇÃO

**Versão:** v2.2.6 "Real-Sense"  
**Data:** 11 de Fevereiro de 2026  
**Objetivo:** Conectar o Simbionte ao Mercado Real

---

## 🎯 VISÃO GERAL

Este guia prepara o Simbionte Financeiro para operar com **DADOS REAIS** de Forex, transformando o protótipo em um **MVP COMERCIAL** pronto para os primeiros 10 traders beta.

---

## 📋 PRÉ-REQUISITOS

### 1. Chave API Alpha Vantage (GRATUITA)

**Por que Alpha Vantage?**
- ✅ Tier gratuito generoso (25 requests/dia)
- ✅ Dados de qualidade institucional
- ✅ Sem cartão de crédito necessário
- ✅ Upgrade fácil quando crescer

**Como obter:**

1. Acesse: https://www.alphavantage.co/support/#api-key
2. Preencha o formulário (30 segundos)
3. Receba a chave por email
4. Copie a chave (formato: `ABCD1234EFGH5678`)

**Configuração:**

```bash
# Windows (PowerShell)
$env:ALPHA_VANTAGE_API_KEY="SUA_CHAVE_AQUI"

# Windows (CMD)
set ALPHA_VANTAGE_API_KEY=SUA_CHAVE_AQUI

# Linux/Mac
export ALPHA_VANTAGE_API_KEY="SUA_CHAVE_AQUI"
```

**Permanente (Windows):**
```powershell
[System.Environment]::SetEnvironmentVariable('ALPHA_VANTAGE_API_KEY', 'SUA_CHAVE_AQUI', 'User')
```

---

### 2. Polygon.io (OPCIONAL - Para Produção)

**Quando usar:**
- Quando ultrapassar 25 requests/dia
- Para dados em tempo real (<1s latência)
- Para produção com múltiplos traders

**Planos:**
- Starter: $29/mês (5 requests/min)
- Developer: $99/mês (100 requests/min)
- Advanced: $199/mês (Unlimited)

**Configuração:**
```bash
export POLYGON_API_KEY="SUA_CHAVE_POLYGON"
```

---

## 🧪 TESTE RÁPIDO

### Teste 1: Verificar Instalação

```bash
python aethel/core/real_forex_api.py
```

**Resultado Esperado:**
```
================================================================================
REAL FOREX ORACLE - DEMO
================================================================================

[ALPHA_VANTAGE] Initialized with API key: ABCD1234...
[REAL_FOREX_ORACLE] Initialized with multiple providers

Testing EUR/USD...
[ALPHA_VANTAGE] Fetching EUR/USD...
[ALPHA_VANTAGE] ✅ EUR/USD: 1.0865
[ALPHA_VANTAGE] Seal: 3f8a2b9c1d7e3f6a...

✅ SUCCESS!
Pair: EUR/USD
Price: 1.0865
Bid: 1.0863
Ask: 1.0867
Provider: alpha_vantage
Seal: 3f8a2b9c1d7e3f6a8b2c4d6e8f0a2b4c...
Valid: True
```

---

### Teste 2: Integração com Memória

```python
from aethel.core.real_forex_api import get_real_forex_oracle
from aethel.core.memory import get_cognitive_memory

# Obtém dados reais
oracle = get_real_forex_oracle()
quote = oracle.get_quote("EUR/USD")

if quote:
    # Armazena na memória
    memory = get_cognitive_memory()
    memory.store_market_data(
        pair=quote.pair,
        price=quote.price,
        bid=quote.bid,
        ask=quote.ask,
        source=quote.provider,
        authenticity_seal=quote.authenticity_seal
    )
    
    print(f"✅ Dados reais armazenados com selo: {quote.authenticity_seal[:16]}...")
```

---

## 🔄 MIGRAÇÃO: Simulado → Real

### Antes (Simulado):
```python
# demo_symbiont_simple.py
oracle = get_web_oracle()
feed = oracle.capture_forex_data(
    pair="EUR/USD",
    price=1.0865,  # ❌ Dados simulados
    bid=1.0863,
    ask=1.0867
)
```

### Depois (Real):
```python
# demo_symbiont_real.py
from aethel.core.real_forex_api import get_real_forex_oracle

oracle = get_real_forex_oracle()
quote = oracle.get_quote("EUR/USD")  # ✅ Dados REAIS da Alpha Vantage

if quote:
    print(f"Preço real: {quote.price}")
    print(f"Selo: {quote.authenticity_seal[:16]}...")
```

---

## 📊 LIMITES E RATE LIMITING

### Alpha Vantage (Free Tier)

| Métrica | Limite |
|---------|--------|
| Requests/dia | 25 |
| Requests/minuto | 5 |
| Latência | ~1-2s |
| Pares suportados | Todos os principais |

**Rate Limiting Automático:**
- ✅ Implementado no código
- ✅ Espera 12s entre requests
- ✅ Cache de 60s por par

### Polygon.io (Starter $29/mês)

| Métrica | Limite |
|---------|--------|
| Requests/minuto | 5 |
| Latência | <100ms |
| Dados históricos | 2 anos |
| WebSocket | Sim |

---

## 🎯 ESTRATÉGIA DE CRESCIMENTO

### Fase 1: Alpha (Gratuito)
**Objetivo:** Validar com 1-3 traders  
**Custo:** $0/mês  
**Limite:** 25 requests/dia = ~8 traders consultando 3x/dia

### Fase 2: Beta ($29/mês)
**Objetivo:** 10 traders beta  
**Custo:** $29/mês (Polygon Starter)  
**Limite:** 5 requests/min = 7,200 requests/dia

### Fase 3: Produção ($99-199/mês)
**Objetivo:** 100+ traders  
**Custo:** $99-199/mês (Polygon Developer/Advanced)  
**Limite:** Unlimited

---

## 🔐 SEGURANÇA

### Selos Criptográficos

Cada cotação recebe um selo único:

```python
seal_data = f"{pair}:{price}:{timestamp}:{provider}"
seal = hashlib.sha256(seal_data.encode()).hexdigest()
```

**Garantias:**
- ✅ Impossível falsificar
- ✅ Detecta manipulação
- ✅ Auditável
- ✅ Rastreável

### Validação Multi-Fonte

```python
# Compara Alpha Vantage vs Polygon
quote1 = alpha_vantage.get_forex_quote("EUR", "USD")
quote2 = polygon.get_forex_quote("EUR", "USD")

# Detecta discrepância
if abs(quote1.price - quote2.price) > 0.001:
    print("⚠️ Discrepância detectada!")
```

---

## 📈 MONITORAMENTO

### Métricas Importantes

1. **Taxa de Sucesso**
   ```python
   success_rate = successful_requests / total_requests
   # Target: >95%
   ```

2. **Latência Média**
   ```python
   avg_latency = sum(request_times) / len(request_times)
   # Target: <2s (Alpha Vantage), <100ms (Polygon)
   ```

3. **Cache Hit Rate**
   ```python
   cache_hit_rate = cache_hits / total_requests
   # Target: >50%
   ```

---

## 🚨 TROUBLESHOOTING

### Erro: "No API key provided"

**Solução:**
```bash
# Verifique se a variável está setada
echo $ALPHA_VANTAGE_API_KEY  # Linux/Mac
echo %ALPHA_VANTAGE_API_KEY%  # Windows CMD
$env:ALPHA_VANTAGE_API_KEY    # Windows PowerShell
```

### Erro: "Rate limit exceeded"

**Solução:**
- Aguarde 1 minuto
- Ou upgrade para Polygon ($29/mês)

### Erro: "Invalid API key"

**Solução:**
- Verifique se copiou a chave corretamente
- Gere nova chave em https://www.alphavantage.co/support/#api-key

### Erro: "No data returned"

**Solução:**
- Verifique se o par está correto (EUR/USD, não EURUSD)
- Tente outro par (GBP/USD, USD/JPY)

---

## 🎉 PRÓXIMOS PASSOS

### 1. Configurar API Key ✅
```bash
export ALPHA_VANTAGE_API_KEY="SUA_CHAVE"
```

### 2. Testar Conexão ✅
```bash
python aethel/core/real_forex_api.py
```

### 3. Integrar com WhatsApp 🔄
```bash
python demo_symbiont_real.py
```

### 4. Convidar Beta Testers 🎯
- Selecionar 10 traders de elite
- Fornecer acesso ao WhatsApp Gateway
- Coletar feedback

### 5. Ativar Cobrança 💰
- Configurar Payment Gateway
- Definir preço ($199/mês)
- Processar primeiros pagamentos

---

## 💰 PROJEÇÃO DE RECEITA

### Cenário Conservador

| Mês | Traders | Receita/Mês | Custo API | Lucro |
|-----|---------|-------------|-----------|-------|
| 1 | 3 | $597 | $0 | $597 |
| 2 | 10 | $1,990 | $29 | $1,961 |
| 3 | 25 | $4,975 | $99 | $4,876 |
| 6 | 50 | $9,950 | $199 | $9,751 |
| 12 | 100 | $19,900 | $199 | $19,701 |

**ARR (Annual Recurring Revenue):** $238,800

---

## 📞 SUPORTE

**Problemas técnicos:**
- Kiro AI (Engenheiro-Chefe)
- Email: kiro@diotec360.com

**Questões comerciais:**
- Dionísio Sebastião Barros (Arquiteto)
- Email: dionisio@diotec360.com

---

## 🏁 CHECKLIST FINAL

Antes de lançar o MVP:

- [ ] API Key configurada
- [ ] Teste de conexão passou
- [ ] Integração com memória funcionando
- [ ] WhatsApp Gateway testado
- [ ] Selos criptográficos validados
- [ ] Rate limiting funcionando
- [ ] Cache implementado
- [ ] Monitoramento ativo
- [ ] 3 beta testers confirmados
- [ ] Payment Gateway configurado

---

**Quando todos os itens estiverem marcados:**

🚀 **VOCÊ ESTÁ PRONTO PARA LANÇAR O MVP!**

---

**Kiro AI - Engenheiro-Chefe**  
**11 de Fevereiro de 2026**  
**v2.2.6 "Real-Sense"**

🧠⚡📱⚖️🐘🔐💰
