# 🔗 URLs do Webhook - DIOTEC 360 no Hugging Face

## 🎯 URL Principal do Backend

```
https://diotec-360-diotec-360-ia-judge.hf.space
```

## 💰 URL do Webhook PayPal (CRÍTICA)

```
https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
```

**⚠️ USE ESTA URL NO PAYPAL DEVELOPER DASHBOARD**

## 📡 Endpoints Disponíveis

### Health Check
```
GET https://diotec-360-diotec-360-ia-judge.hf.space/
```

### Verificar Intent
```
POST https://diotec-360-diotec-360-ia-judge.hf.space/verify
```

### Parse Intent
```
POST https://diotec-360-diotec-360-ia-judge.hf.space/parse
```

### Métricas do Sistema
```
GET https://diotec-360-diotec-360-ia-judge.hf.space/metrics
```

### State Root
```
GET https://diotec-360-diotec-360-ia-judge.hf.space/state
```

### Documentação Interativa (Swagger)
```
GET https://diotec-360-diotec-360-ia-judge.hf.space/docs
```

## 🔧 Configuração no Frontend

O arquivo `frontend/.env.local` foi atualizado com:

```env
NEXT_PUBLIC_API_URL=https://diotec-360-diotec-360-ia-judge.hf.space
NEXT_PUBLIC_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space
```

## 🧪 Como Testar

### 1. Testar Health Check
```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/
```

**Resposta esperada:**
```json
{
  "status": "operational",
  "service": "DIOTEC 360 IA - Sovereign Judge",
  "version": "1.0.0",
  "z3_available": true
}
```

### 2. Testar Verificação de Intent
```bash
curl -X POST https://diotec-360-diotec-360-ia-judge.hf.space/verify \
  -H "Content-Type: application/json" \
  -d '{
    "intent_name": "test",
    "code": "intent test() { guard { x > 0; } solve { priority: security; } verify { y == x; } }"
  }'
```

### 3. Testar Métricas
```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/metrics
```

## 📊 Status do Deploy

Para verificar o status do deploy:

1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
2. Verifique o status:
   - 🟢 **Running** = Deploy completo e funcionando
   - 🟡 **Building** = Container sendo construído
   - 🔴 **Build failed** = Erro no deploy

## 🔐 Configuração de Webhooks PayPal

### URL do Webhook (Cole no PayPal Developer Dashboard)

```
https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
```

### Eventos a Marcar no PayPal

Procure e marque os seguintes eventos:

**Grupo: Checkout**
- ✅ `CHECKOUT.ORDER.APPROVED` - Checkout order approved

**Grupo: Payments & Payouts**
- ✅ `PAYMENT.SALE.COMPLETED` - Payment sale completed (PRINCIPAL)

**Alternativa:** Se não encontrar, marque `All Events` no topo da lista.

## 📝 Notas Importantes

1. **CORS**: O backend está configurado para aceitar requisições do frontend
2. **Rate Limiting**: Hugging Face aplica rate limiting automático
3. **Timeout**: Requisições têm timeout de 60 segundos
4. **HTTPS**: Todas as conexões são via HTTPS (seguro)

## 🚀 Próximos Passos

1. ✅ URL configurada no frontend
2. ⏳ Aguardar deploy completar no Hugging Face
3. 🧪 Testar endpoints
4. 🎉 Integrar com frontend

## 📚 Links Úteis

- **Space no HF**: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
- **Documentação API**: https://diotec-360-diotec-360-ia-judge.hf.space/docs
- **Logs do Space**: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge/logs

---

**⚖️ The Sovereign Judge Awaits** 🏛️

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**  
**Data:** 27 de Fevereiro de 2026
