# Configuração PayPal - Resumo

## ✅ Arquivos Atualizados

### Backend

1. **`.env`** - Variáveis PayPal (Sandbox)
```bash
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
PAYPAL_WEBHOOK_ID=
```

2. **`.env.production`** - Variáveis PayPal (Live)
```bash
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=your-production-client-id
PAYPAL_CLIENT_SECRET=your-production-client-secret
PAYPAL_WEBHOOK_ID=your-webhook-id
PAYPAL_WEBHOOK_URL=https://api.diotec360.com/api/payment/paypal/webhook
```

3. **`vercel.json`** - Variáveis de ambiente Vercel
```json
{
  "env": {
    "PAYPAL_MODE": "live",
    "PAYPAL_CLIENT_ID": "",
    "PAYPAL_CLIENT_SECRET": "",
    "PAYPAL_WEBHOOK_ID": ""
  }
}
```

### Frontend

4. **`frontend/.env.local`** - Desenvolvimento
```bash
NEXT_PUBLIC_PAYPAL_CLIENT_ID=
NEXT_PUBLIC_PAYPAL_MODE=sandbox
```

5. **`frontend/.env.production`** - Produção
```bash
NEXT_PUBLIC_PAYPAL_CLIENT_ID=your-production-client-id
NEXT_PUBLIC_PAYPAL_MODE=live
NEXT_PUBLIC_ENABLE_PAYMENTS=true
NEXT_PUBLIC_ENABLE_PAYPAL=true
NEXT_PUBLIC_ENABLE_MULTICAIXA=true
```

6. **`frontend/vercel.json`** - Variáveis de ambiente Vercel
```json
{
  "env": {
    "NEXT_PUBLIC_PAYPAL_CLIENT_ID": "",
    "NEXT_PUBLIC_PAYPAL_MODE": "live",
    "NEXT_PUBLIC_ENABLE_PAYMENTS": "true",
    "NEXT_PUBLIC_ENABLE_PAYPAL": "true"
  }
}
```

## 📄 Documentação Criada

7. **`PAYPAL_SETUP_GUIDE.md`** - Guia completo de configuração
   - Como criar conta PayPal Business
   - Como obter credenciais API
   - Como configurar webhooks
   - Como testar integração
   - Troubleshooting

## 🔑 Variáveis Necessárias

### Para Obter no PayPal Developer Dashboard

1. **PAYPAL_CLIENT_ID** (Sandbox e Live)
   - Acesse: https://developer.paypal.com
   - Dashboard → My Apps & Credentials
   - Create App → Copie Client ID

2. **PAYPAL_CLIENT_SECRET** (Sandbox e Live)
   - Mesmo local do Client ID
   - Clique em "Show" para revelar

3. **PAYPAL_WEBHOOK_ID**
   - Selecione sua app
   - Webhooks → Add Webhook
   - URL: `https://api.diotec360.com/api/payment/paypal/webhook`
   - Copie o Webhook ID

## 🚀 Próximos Passos

### 1. Criar Conta PayPal Business
- Acesse: https://www.paypal.com/ao/business
- Tempo: 1-3 dias para verificação

### 2. Obter Credenciais
- Sandbox (testes): Imediato
- Live (produção): Após verificação da conta

### 3. Configurar Variáveis
- Adicione no `.env` local
- Adicione no Vercel Dashboard

### 4. Testar
```powershell
# Testar endpoint
curl -X POST https://api.diotec360.com/api/payment/create `
  -H "Content-Type: application/json" `
  -d '{"package":"starter","method":"paypal"}'
```

## 📊 Integração Existente

O projeto já possui:
- ✅ `diotec360/core/payment_gateway.py` - Gateway PayPal
- ✅ `diotec360/core/billing.py` - Sistema de créditos
- ✅ Testes unitários (11/11 passando)
- ✅ Suporte a múltiplas moedas (USD, EUR, AOA)

Falta apenas:
- 🔄 Obter credenciais PayPal
- 🔄 Configurar variáveis de ambiente
- 🔄 Testar em produção

## 🔒 Segurança

**IMPORTANTE**: Nunca commite credenciais no Git!

As variáveis estão configuradas como placeholders vazios:
```bash
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
```

Você deve:
1. Obter as credenciais no PayPal
2. Adicionar no Vercel Dashboard (marcadas como "Sensitive")
3. Adicionar no `.env` local (não commitado)

## 📝 Checklist

- [ ] Criar conta PayPal Business
- [ ] Verificar conta (1-3 dias)
- [ ] Obter Client ID (Sandbox)
- [ ] Obter Client Secret (Sandbox)
- [ ] Obter Client ID (Live)
- [ ] Obter Client Secret (Live)
- [ ] Configurar Webhook
- [ ] Obter Webhook ID
- [ ] Adicionar variáveis no Vercel (Backend)
- [ ] Adicionar variáveis no Vercel (Frontend)
- [ ] Testar em Sandbox
- [ ] Testar em Produção

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
