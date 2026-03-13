# 💱 ALPHA_VANTAGE_API_KEY - O QUE É E COMO OBTER

**Data:** 2026-02-12  
**Contexto:** Frontend Aethel Studio - Dados Forex em Tempo Real

---

## 🎯 RESPOSTA RÁPIDA

`ALPHA_VANTAGE_API_KEY` é uma chave de API para acessar dados financeiros em tempo real (Forex, ações, criptomoedas) da Alpha Vantage.

**Você já tem uma chave configurada:**

```env
ALPHA_VANTAGE_API_KEY=EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
```

**Essa chave funciona, mas você pode obter sua própria chave gratuita em 2 minutos!**

---

## 📚 O QUE É ALPHA VANTAGE?

Alpha Vantage é um provedor de dados financeiros em tempo real que oferece:

- 📈 **Forex (Câmbio):** EUR/USD, USD/BRL, etc.
- 📊 **Ações:** Preços de ações em tempo real
- 💰 **Criptomoedas:** Bitcoin, Ethereum, etc.
- 📉 **Indicadores Técnicos:** RSI, MACD, Bollinger Bands

**API Gratuita:**
- ✅ 25 requisições por dia (tier gratuito)
- ✅ Dados em tempo real
- ✅ Sem cartão de crédito necessário
- ✅ Ativação instantânea

---

## 🔍 ONDE É USADO NO AETHEL?

### 1. Simbionte Financeiro (MVP Comercial)

O Simbionte usa Alpha Vantage para obter taxas de câmbio em tempo real:

```python
# aethel/core/real_forex_api.py
from aethel.core.web_oracle import WebOracle

oracle = WebOracle()
rate = oracle.get_forex_rate("USD", "BRL")
# Usa Alpha Vantage para obter taxa real
```

### 2. Frontend (Aethel Studio)

O frontend pode exibir dados financeiros em tempo real:

```typescript
// frontend/lib/api.ts
const forexRate = await fetch(
  `${API_URL}/api/forex/rate?from=USD&to=BRL`
);
```

### 3. Demos e Exemplos

Vários demos usam dados reais:
- `demo_symbiont_real.py` - Simbionte com Forex real
- `demo_cognitive_forex.py` - Análise cognitiva de Forex

---

## 🚀 COMO OBTER SUA PRÓPRIA CHAVE (2 MINUTOS)

### Passo 1: Acessar o Site

Vá para: https://www.alphavantage.co/support/#api-key

### Passo 2: Preencher o Formulário

```
┌─────────────────────────────────────────┐
│ Get Your Free API Key                   │
├─────────────────────────────────────────┤
│                                         │
│ Email: seu-email@exemplo.com           │
│                                         │
│ Organization: DIOTEC 360                │
│                                         │
│ [ ] I agree to the Terms of Service    │
│                                         │
│        [GET FREE API KEY]               │
│                                         │
└─────────────────────────────────────────┘
```

### Passo 3: Receber a Chave

Você receberá um email instantâneo com sua chave:

```
Your Alpha Vantage API Key:
ABC123XYZ456DEF789GHI012JKL345MNO
```

### Passo 4: Configurar no Projeto

**Backend (.env):**
```env
ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO
```

**Frontend (frontend/.env.production):**
```env
ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO
```

**Vercel Dashboard:**
- Settings → Environment Variables
- Adicione: `ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO`

---

## 🔑 CHAVE ATUAL vs NOVA CHAVE

### Chave Atual (Funciona)

```env
ALPHA_VANTAGE_API_KEY=EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
```

**Características:**
- ✅ Funciona para testes
- ⚠️ Compartilhada (pode ter rate limit)
- ⚠️ Não é sua (pode ser revogada)

### Sua Nova Chave (Recomendado)

```env
ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO
```

**Características:**
- ✅ Exclusiva para você
- ✅ 25 requisições/dia garantidas
- ✅ Controle total
- ✅ Pode fazer upgrade se precisar

---

## 📊 LIMITES DA API GRATUITA

| Plano | Requisições/Dia | Requisições/Minuto | Custo |
|-------|-----------------|-------------------|-------|
| **Free** | 25 | 5 | $0 |
| Premium | 75 | 15 | $49.99/mês |
| Enterprise | Ilimitado | Ilimitado | Customizado |

**Para o MVP Comercial, o plano gratuito é suficiente!**

---

## 🧪 TESTAR SUA CHAVE

### Teste 1: Requisição Direta

```bash
curl "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=USD&to_currency=BRL&apikey=SUA_CHAVE_AQUI"
```

**Resposta esperada:**
```json
{
  "Realtime Currency Exchange Rate": {
    "1. From_Currency Code": "USD",
    "2. From_Currency Name": "United States Dollar",
    "3. To_Currency Code": "BRL",
    "4. To_Currency Name": "Brazilian Real",
    "5. Exchange Rate": "5.12345678",
    "6. Last Refreshed": "2026-02-12 10:30:00",
    "7. Time Zone": "UTC",
    "8. Bid Price": "5.12300000",
    "9. Ask Price": "5.12400000"
  }
}
```

### Teste 2: Via Backend Aethel

```bash
# Configurar a chave no .env
ALPHA_VANTAGE_API_KEY=SUA_CHAVE_AQUI

# Executar o demo
python demo_symbiont_real.py
```

### Teste 3: Via Frontend

```bash
# Configurar no Vercel Dashboard
# Acessar: https://aethel.diotec360.com/
# Testar funcionalidade de Forex
```

---

## 🔧 TROUBLESHOOTING

### Erro: "Invalid API call"

**Causa:** Chave inválida ou formato incorreto

**Solução:**
1. Verifique se copiou a chave completa
2. Não adicione espaços ou quebras de linha
3. Use apenas a chave, sem aspas

### Erro: "API rate limit reached"

**Causa:** Excedeu 25 requisições/dia

**Solução:**
1. Aguarde até o próximo dia (reset às 00:00 UTC)
2. Ou faça upgrade para Premium
3. Ou use cache para reduzir requisições

### Erro: "Thank you for using Alpha Vantage!"

**Causa:** Chave demo ou limite atingido

**Solução:**
1. Obtenha sua própria chave gratuita
2. Verifique se não está usando a chave demo

---

## 💡 DICAS DE USO

### 1. Cache de Dados

Implemente cache para reduzir requisições:

```python
# Cache por 1 hora
@cache(ttl=3600)
def get_forex_rate(from_currency, to_currency):
    return oracle.get_forex_rate(from_currency, to_currency)
```

### 2. Fallback para Dados Mock

Se a API falhar, use dados mock:

```python
try:
    rate = oracle.get_forex_rate("USD", "BRL")
except Exception:
    rate = 5.0  # Fallback para taxa fixa
```

### 3. Monitorar Uso

Acompanhe quantas requisições você fez:

```python
# Alpha Vantage não fornece contador
# Implemente seu próprio contador local
```

---

## 🏛️ PARA O MVP COMERCIAL

### Configuração Recomendada

**Backend (.env):**
```env
# Sua chave pessoal
ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO

# Fallback para dados mock se API falhar
FOREX_FALLBACK_ENABLED=true
```

**Frontend (Vercel):**
```env
# Mesma chave
ALPHA_VANTAGE_API_KEY=ABC123XYZ456DEF789GHI012JKL345MNO
```

### Estratégia de Uso

1. **Cache agressivo:** 1 hora para taxas de câmbio
2. **Fallback:** Dados mock se API falhar
3. **Monitoramento:** Log de requisições
4. **Upgrade:** Se precisar de mais requisições

---

## 📝 CHECKLIST

- [ ] Acessar https://www.alphavantage.co/support/#api-key
- [ ] Preencher formulário com seu email
- [ ] Receber chave por email
- [ ] Configurar no `.env` (backend)
- [ ] Configurar no `frontend/.env.production`
- [ ] Configurar no Vercel Dashboard
- [ ] Testar com `curl` ou `demo_symbiont_real.py`
- [ ] Verificar que funciona no frontend

---

## 🎯 RESUMO EXECUTIVO

| Pergunta | Resposta |
|----------|----------|
| **O que é?** | Chave de API para dados financeiros em tempo real |
| **Onde obter?** | https://www.alphavantage.co/support/#api-key |
| **Quanto custa?** | Gratuito (25 req/dia) |
| **Preciso agora?** | Não urgente, mas recomendado |
| **Chave atual funciona?** | Sim, mas obtenha a sua |
| **Onde configurar?** | `.env`, `frontend/.env.production`, Vercel |

---

## 🚀 AÇÃO IMEDIATA

**Para o deploy do Vercel:**

Você pode usar a chave atual por enquanto:

```env
ALPHA_VANTAGE_API_KEY=EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
```

**Depois do deploy:**

1. Obtenha sua própria chave (2 minutos)
2. Atualize no Vercel Dashboard
3. Redeploy (opcional, ou aguarde próximo deploy)

---

## 📚 REFERÊNCIAS

- **Site Oficial:** https://www.alphavantage.co/
- **Documentação:** https://www.alphavantage.co/documentation/
- **Obter Chave:** https://www.alphavantage.co/support/#api-key
- **Código Aethel:** `aethel/core/web_oracle.py`, `aethel/core/real_forex_api.py`

---

**💱 ALPHA VANTAGE - DADOS FINANCEIROS EM TEMPO REAL 💱**

**Continue com o deploy! A chave atual funciona para começar.**

**🏛️⚖️✨**
