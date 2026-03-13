# Guia de Configuração PayPal - DIOTEC 360

## Visão Geral

O DIOTEC 360 suporta pagamentos via PayPal para clientes internacionais. Este guia mostra como configurar as credenciais do PayPal.

## Pré-requisitos

- Conta PayPal Business (ou criar uma)
- Acesso ao PayPal Developer Dashboard
- Domínio verificado (api.diotec360.com)

---

## Passo 1: Criar Conta PayPal Business

### 1.1 Criar Conta

1. Acesse: https://www.paypal.com/ao/business
2. Clique em "Criar Conta Business"
3. Preencha os dados:
   - **Tipo de negócio**: Serviços de Software/Tecnologia
   - **Nome da empresa**: DIOTEC 360
   - **Email**: seu-email@diotec360.com
   - **Telefone**: +244 XXX XXX XXX

### 1.2 Verificar Conta

1. Confirme o email
2. Adicione conta bancária (para receber pagamentos)
3. Complete a verificação de identidade

**Tempo estimado**: 1-3 dias úteis

---

## Passo 2: Obter Credenciais API

### 2.1 Acessar Developer Dashboard

1. Acesse: https://developer.paypal.com
2. Login com sua conta PayPal Business
3. Vá para "Dashboard" → "My Apps & Credentials"

### 2.2 Criar App (Sandbox - Testes)

1. Na aba "Sandbox", clique em "Create App"
2. Configure:
   - **App Name**: DIOTEC 360 Sandbox
   - **Sandbox Business Account**: Selecione sua conta
3. Clique em "Create App"

4. Copie as credenciais:
   - **Client ID**: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`
   - **Secret**: `EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`

### 2.3 Criar App (Live - Produção)

1. Na aba "Live", clique em "Create App"
2. Configure:
   - **App Name**: DIOTEC 360 Production
   - **Live Business Account**: Selecione sua conta
3. Clique em "Create App"

4. Copie as credenciais:
   - **Client ID**: `AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`
   - **Secret**: `EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx`

---

## Passo 3: Configurar Webhooks

### 3.1 Adicionar Webhook URL

1. No PayPal Developer Dashboard
2. Selecione sua app (Live)
3. Vá para "Webhooks"
4. Clique em "Add Webhook"
5. Configure:
   - **Webhook URL**: `https://api.diotec360.com/api/payment/paypal/webhook`
   - **Event types**: Selecione:
     - `PAYMENT.CAPTURE.COMPLETED`
     - `PAYMENT.CAPTURE.DENIED`
     - `PAYMENT.CAPTURE.REFUNDED`
     - `CHECKOUT.ORDER.APPROVED`
     - `CHECKOUT.ORDER.COMPLETED`

6. Clique em "Save"
7. Copie o **Webhook ID**: `WH-XXXXXXXXXXXXXXXXX`

---

## Passo 4: Configurar Variáveis de Ambiente

### 4.1 Backend (.env)

Adicione as credenciais no arquivo `.env`:

```bash
# PayPal Configuration - SANDBOX (Development)
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_CLIENT_SECRET=EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_WEBHOOK_ID=WH-XXXXXXXXXXXXXXXXX
```

### 4.2 Backend (.env.production)

Para produção, use as credenciais Live:

```bash
# PayPal Configuration - LIVE (Production)
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_CLIENT_SECRET=EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_WEBHOOK_ID=WH-XXXXXXXXXXXXXXXXX
PAYPAL_WEBHOOK_URL=https://api.diotec360.com/api/payment/paypal/webhook
```

### 4.3 Frontend (frontend/.env.local)

Para desenvolvimento:

```bash
# PayPal Configuration - SANDBOX
NEXT_PUBLIC_PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
NEXT_PUBLIC_PAYPAL_MODE=sandbox
```

### 4.4 Frontend (frontend/.env.production)

Para produção:

```bash
# PayPal Configuration - LIVE
NEXT_PUBLIC_PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
NEXT_PUBLIC_PAYPAL_MODE=live
NEXT_PUBLIC_ENABLE_PAYMENTS=true
NEXT_PUBLIC_ENABLE_PAYPAL=true
```

---

## Passo 5: Configurar no Vercel

### 5.1 Backend (diotec360-api)

No Vercel Dashboard → Settings → Environment Variables:

```
PAYPAL_MODE=live
PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_CLIENT_SECRET=EXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
PAYPAL_WEBHOOK_ID=WH-XXXXXXXXXXXXXXXXX
```

**Importante**: Marque como "Production" e "Sensitive"

### 5.2 Frontend (diotec360-app)

No Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_PAYPAL_CLIENT_ID=AXXXXXXXXXXXXXXXXXXXXXXXXXXXXXx
NEXT_PUBLIC_PAYPAL_MODE=live
NEXT_PUBLIC_ENABLE_PAYMENTS=true
NEXT_PUBLIC_ENABLE_PAYPAL=true
```

---

## Passo 6: Testar Integração

### 6.1 Testar em Sandbox

1. Use as credenciais Sandbox
2. Crie uma conta de teste no PayPal Sandbox
3. Faça um pagamento de teste

```powershell
# Testar endpoint
curl -X POST https://api.diotec360.com/api/payment/create `
  -H "Content-Type: application/json" `
  -d '{"package":"starter","method":"paypal"}'
```

### 6.2 Contas de Teste Sandbox

O PayPal cria automaticamente contas de teste:

- **Comprador**: sb-xxxxx@personal.example.com
- **Vendedor**: sb-xxxxx@business.example.com

Acesse: https://developer.paypal.com/dashboard/accounts

---

## Estrutura de Pagamento

### Fluxo de Pagamento

```
Cliente → Frontend → API → PayPal
                              ↓
                         Aprovação
                              ↓
                         Captura
                              ↓
                         Webhook
                              ↓
                    Atualizar Créditos
```

### Endpoints da API

```
POST /api/payment/create          - Criar pagamento
POST /api/payment/capture         - Capturar pagamento
POST /api/payment/paypal/webhook  - Webhook PayPal
GET  /api/payment/status/:id      - Status do pagamento
```

---

## Pacotes e Preços

### Pacotes Disponíveis

| Pacote       | Preço (USD) | Créditos | Descrição                    |
|--------------|-------------|----------|------------------------------|
| Starter      | $10         | 1,000    | Para começar                 |
| Professional | $80         | 10,000   | Para desenvolvedores         |
| Business     | $700        | 100,000  | Para empresas                |
| Enterprise   | $6,000      | 1,000,000| Para grandes organizações    |

### Taxas PayPal

- **Taxa padrão**: 2.9% + $0.30 por transação
- **Taxa internacional**: +1.5% adicional
- **Conversão de moeda**: Taxa variável

---

## Segurança

### Boas Práticas

1. ✅ Nunca commite credenciais no Git
2. ✅ Use variáveis de ambiente
3. ✅ Valide webhooks com assinatura
4. ✅ Use HTTPS em produção
5. ✅ Implemente rate limiting
6. ✅ Log todas as transações

### Validação de Webhook

O PayPal envia uma assinatura no header:

```python
# Verificar assinatura do webhook
def verify_webhook_signature(headers, body):
    # Implementado em diotec360/core/payment_gateway.py
    pass
```

---

## Troubleshooting

### Erro: "Invalid credentials"

**Solução**: Verifique se está usando as credenciais corretas (Sandbox vs Live)

### Erro: "Webhook not verified"

**Solução**: Verifique se o Webhook ID está correto

### Erro: "Payment declined"

**Solução**: Verifique o saldo da conta de teste ou use outro cartão

### Erro: "CORS blocked"

**Solução**: Verifique se o domínio está em `DIOTEC360_CORS_ORIGINS`

---

## Monitoramento

### Logs PayPal

Acesse: https://developer.paypal.com/dashboard/webhooks

- Ver webhooks recebidos
- Ver erros de webhook
- Reenviar webhooks

### Logs da API

```powershell
# Ver logs do Vercel
vercel logs diotec360-api --follow
```

---

## Recursos Úteis

### Documentação

- [PayPal Developer Docs](https://developer.paypal.com/docs)
- [PayPal Checkout Integration](https://developer.paypal.com/docs/checkout)
- [PayPal Webhooks Guide](https://developer.paypal.com/docs/api-basics/notifications/webhooks)

### Suporte

- **PayPal Angola**: https://www.paypal.com/ao/smarthelp/contact-us
- **Developer Support**: https://developer.paypal.com/support

---

## Checklist de Configuração

- [ ] Criar conta PayPal Business
- [ ] Verificar conta (1-3 dias)
- [ ] Criar app no Developer Dashboard
- [ ] Obter Client ID e Secret (Sandbox)
- [ ] Obter Client ID e Secret (Live)
- [ ] Configurar Webhooks
- [ ] Adicionar variáveis no .env
- [ ] Adicionar variáveis no Vercel
- [ ] Testar em Sandbox
- [ ] Testar em Produção
- [ ] Monitorar transações

---

## Próximos Passos

Após configurar o PayPal:

1. 🔄 Configurar Multicaixa Express (pagamentos em Angola)
2. 🔄 Criar página de pricing no frontend
3. 🔄 Implementar dashboard de billing
4. 🔄 Adicionar histórico de transações

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**

**Data**: 26 de Fevereiro de 2026  
**Versão**: 1.7.0 "Oracle Sanctuary"
