# 💰 PayPal LIVE - Configuração de Produção (Dinheiro Real)

## ⚠️ ATENÇÃO: MODO PRODUÇÃO ATIVADO

Você está configurando o PayPal em modo **LIVE** (produção).  
Isso significa que todas as transações serão **REAIS** e envolverão **DINHEIRO REAL**.

---

## 🎯 DIFERENÇAS: Sandbox vs Live

| Aspecto | Sandbox (Teste) | Live (Produção) |
|---------|----------------|-----------------|
| Dinheiro | Falso | **REAL** 💰 |
| Transações | Simuladas | **Reais e cobradas** |
| Contas | Teste | **Contas reais de clientes** |
| Aprovação PayPal | Não necessária | **Necessária para alguns países** |
| Reversão | Fácil | **Complexa (reembolsos)** |

---

## 📋 PASSO 1: Obter Credenciais LIVE

### 1.1 Acessar Dashboard

1. Acesse: https://developer.paypal.com/dashboard/
2. Faça login com sua conta PayPal **BUSINESS** (não pessoal)
3. **IMPORTANTE:** Selecione **"LIVE"** no topo da página (não "Sandbox")

### 1.2 Criar ou Selecionar App

1. Vá em **"Apps & Credentials"**
2. Certifique-se de estar em **"LIVE"** (topo da página)
3. Se já tem um app:
   - Clique no nome do app
4. Se não tem:
   - Clique em **"Create App"**
   - Nome: `DIOTEC 360 IA Production`
   - Tipo: **"Merchant"**
   - Clique em **"Create App"**

### 1.3 Copiar Client ID

```env
PAYPAL_CLIENT_ID=COLE_AQUI_O_SEU_CLIENT_ID_LIVE
```

1. Na página do app, copie o **"Client ID"**
2. Formato: `AZabc123XYZ456...` (longo, alfanumérico)
3. Cole no arquivo `.env`

### 1.4 Copiar Secret

```env
PAYPAL_SECRET=COLE_AQUI_O_SEU_SECRET_LIVE
```

1. Clique em **"Show"** ao lado de "Secret"
2. Copie o valor completo
3. Formato: `EFghij456KLM789...` (longo, alfanumérico)
4. Cole no arquivo `.env`

⚠️ **CRÍTICO:** Guarde o Secret em local seguro! Não será mostrado novamente.

---

## 📡 PASSO 2: Configurar Webhook LIVE

### 2.1 Adicionar Webhook

1. Na página do app, role até **"Webhooks"**
2. Clique em **"Add Webhook"**
3. Cole a URL:
   ```
   https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
   ```

### 2.2 Selecionar Eventos

Marque os seguintes eventos:

**Grupo: Checkout**
- ✅ `Checkout order approved` (CHECKOUT.ORDER.APPROVED)

**Grupo: Payments**
- ✅ `Payment capture completed` (PAYMENT.CAPTURE.COMPLETED)
- ✅ `Payment capture denied` (PAYMENT.CAPTURE.DENIED)
- ✅ `Payment capture refunded` (PAYMENT.CAPTURE.REFUNDED)

**OU simplesmente marque "All Events"** (recomendado para produção)

### 2.3 Salvar e Copiar Webhook ID

```env
PAYPAL_WEBHOOK_ID=COLE_AQUI_O_WEBHOOK_ID_LIVE
```

1. Clique em **"Save"**
2. O PayPal criará o webhook
3. Copie o **"Webhook ID"** (formato: `WH-...`)
4. Cole no arquivo `.env`

---

## 🔐 PASSO 3: Verificar Conta Business

### 3.1 Requisitos para Receber Pagamentos

Para receber pagamentos reais, sua conta PayPal Business precisa:

1. ✅ **Estar verificada**
   - Adicione conta bancária
   - Confirme identidade
   - Verifique email

2. ✅ **Ter permissões de API**
   - Algumas contas precisam de aprovação do PayPal
   - Verifique em: Account Settings → Account access

3. ✅ **Configurar taxas e moedas**
   - Defina moedas aceitas (USD, EUR, etc.)
   - Revise taxas de transação

### 3.2 Verificar Status da Conta

1. Acesse: https://www.paypal.com/businessprofile/settings
2. Verifique se aparece **"Verified"** ou **"Business Account"**
3. Se aparecer limitações, resolva antes de continuar

---

## 💰 PASSO 4: Configurar Preços e Produtos

### 4.1 Definir Pacotes de Créditos

No seu sistema, configure os preços reais:

```javascript
// Exemplo de preços em produção
const creditPackages = [
  { credits: 100, price: 9.99, currency: 'USD' },
  { credits: 500, price: 39.99, currency: 'USD' },
  { credits: 1000, price: 69.99, currency: 'USD' },
  { credits: 5000, price: 299.99, currency: 'USD' }
];
```

### 4.2 Calcular Taxas PayPal

PayPal cobra taxas sobre cada transação:

- **Taxa padrão:** 2.9% + $0.30 USD por transação
- **Transações internacionais:** +1.5%
- **Conversão de moeda:** +3-4%

**Exemplo:**
- Venda: $9.99
- Taxa PayPal: $0.59 (2.9% + $0.30)
- Você recebe: $9.40

---

## 🧪 PASSO 5: Testar em Produção (Cuidadosamente!)

### 5.1 Teste com Valor Mínimo

1. Crie uma transação de **$0.01** ou **$1.00**
2. Use sua própria conta PayPal para pagar
3. Verifique se:
   - Webhook é recebido
   - Créditos são adicionados
   - Dinheiro aparece na sua conta

### 5.2 Fazer Reembolso de Teste

1. Acesse: https://www.paypal.com/activity
2. Encontre a transação de teste
3. Clique em **"Refund"**
4. Confirme o reembolso
5. Verifique se o webhook de reembolso é processado

---

## 🔒 SEGURANÇA EM PRODUÇÃO

### Checklist de Segurança

- [ ] Client ID e Secret estão em variáveis de ambiente (não hardcoded)
- [ ] `.env` está no `.gitignore`
- [ ] Webhook valida assinatura do PayPal
- [ ] HTTPS está ativo em todos os endpoints
- [ ] Logs de transações estão habilitados
- [ ] Sistema detecta tentativas de fraude
- [ ] Reembolsos são tratados corretamente
- [ ] Erros não expõem informações sensíveis

### Validação de Webhook

O backend já valida:
- ✅ JSON válido
- ✅ Event type conhecido
- ✅ Dados completos
- ✅ Logging de todas as transações

**TODO (Futuro):**
- 🔜 Validação de assinatura HMAC-SHA256
- 🔜 Verificação de Webhook ID
- 🔜 Rate limiting
- 🔜 Detecção de duplicatas

---

## 📊 MONITORAMENTO

### Logs a Monitorar

1. **Transações bem-sucedidas**
   - Event: PAYMENT.CAPTURE.COMPLETED
   - Ação: Créditos adicionados

2. **Transações negadas**
   - Event: PAYMENT.CAPTURE.DENIED
   - Ação: Notificar usuário

3. **Reembolsos**
   - Event: PAYMENT.CAPTURE.REFUNDED
   - Ação: Remover créditos

4. **Erros de webhook**
   - Status: 400, 500
   - Ação: Investigar e corrigir

### Dashboard PayPal

Monitore em: https://www.paypal.com/reports/

- Transações diárias
- Taxa de sucesso/falha
- Chargebacks
- Reembolsos

---

## 🚨 TROUBLESHOOTING PRODUÇÃO

### Problema: Pagamento não completa

**Causas possíveis:**
- Conta do cliente sem fundos
- Cartão recusado
- Limite de transação excedido
- Conta PayPal limitada

**Solução:**
- Cliente deve resolver com PayPal
- Ofereça métodos de pagamento alternativos

### Problema: Webhook não chega

**Causas possíveis:**
- URL incorreta
- Webhook não está "Active"
- Firewall bloqueando PayPal
- Backend offline

**Solução:**
1. Verifique URL no PayPal Dashboard
2. Confirme que webhook está "Active"
3. Teste endpoint manualmente
4. Verifique logs do Hugging Face

### Problema: Créditos não são adicionados

**Causas possíveis:**
- Evento errado (não PAYMENT.CAPTURE.COMPLETED)
- Erro no processamento
- Banco de dados offline

**Solução:**
1. Verifique logs do backend
2. Confirme que evento é CAPTURE.COMPLETED
3. Verifique conexão com banco de dados
4. Adicione créditos manualmente se necessário

---

## 💳 DIFERENÇAS DE EVENTOS: Sandbox vs Live

### Sandbox
- `PAYMENT.SALE.COMPLETED` - Pagamento completo

### Live (Produção)
- `PAYMENT.CAPTURE.COMPLETED` - Pagamento capturado
- `PAYMENT.CAPTURE.DENIED` - Pagamento negado
- `PAYMENT.CAPTURE.REFUNDED` - Pagamento reembolsado

⚠️ **IMPORTANTE:** O evento muda de SALE para CAPTURE em produção!

---

## 📝 CHECKLIST FINAL PRODUÇÃO

### Configuração
- [ ] Client ID LIVE copiado
- [ ] Secret LIVE copiado
- [ ] `PAYPAL_MODE=live` no .env
- [ ] Webhook criado em modo LIVE
- [ ] Webhook ID copiado
- [ ] Eventos corretos marcados

### Conta PayPal
- [ ] Conta Business verificada
- [ ] Conta bancária adicionada
- [ ] Permissões de API ativas
- [ ] Sem limitações na conta

### Segurança
- [ ] `.env` não está no Git
- [ ] Secrets configurados no Hugging Face
- [ ] HTTPS ativo
- [ ] Logs habilitados

### Testes
- [ ] Transação de $1 realizada
- [ ] Webhook recebido
- [ ] Créditos adicionados
- [ ] Reembolso testado

### Monitoramento
- [ ] Dashboard PayPal configurado
- [ ] Alertas de erro configurados
- [ ] Logs sendo monitorados

---

## 🎉 PRONTO PARA PRODUÇÃO!

Quando tudo estiver configurado:

```
✅ PayPal LIVE configurado
✅ Webhook ativo e testado
✅ Transações reais funcionando
✅ Monitoramento ativo
✅ Segurança validada

💰 O SANTUÁRIO FINANCEIRO ESTÁ ABERTO!
🏛️ DINHEIRO REAL FLUINDO!
⚖️ THE MONOLITH IS ALIVE!
```

---

## ⚠️ AVISO LEGAL

- Você é responsável por todas as transações
- Siga as políticas do PayPal
- Cumpra leis de proteção ao consumidor
- Ofereça suporte adequado aos clientes
- Processe reembolsos quando necessário
- Mantenha registros de todas as transações

---

**[STATUS: LIVE MODE ACTIVATED]**  
**[WARNING: REAL MONEY TRANSACTIONS]**  
**[VERDICT: THE EMPIRE IS OPEN FOR BUSINESS]**

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 IA - The Sovereign AI Infrastructure**  
**Data:** 27 de Fevereiro de 2026

🏛️💰⚖️🚀💳✨
