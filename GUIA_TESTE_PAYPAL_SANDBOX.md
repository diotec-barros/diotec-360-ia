# 🧪 GUIA DE TESTE - PAYPAL SANDBOX

## 📋 Objetivo
Testar toda a integração PayPal em ambiente sandbox (dinheiro fake) antes de ir para produção.

---

## 🔧 PASSO 1: Configurar Webhook no Sandbox

### 1.1 Acessar o Dashboard PayPal
1. Acesse: https://developer.paypal.com/dashboard/
2. **IMPORTANTE**: Certifique-se de estar em modo **SANDBOX** (canto superior direito)

### 1.2 Criar Webhook
1. No menu lateral, clique em **"Apps & Credentials"**
2. Certifique-se de estar na aba **"Sandbox"**
3. Role até a seção **"Webhooks"**
4. Clique em **"Add Webhook"**

### 1.3 Configurar o Webhook
```
Webhook URL: https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
```

### 1.4 Selecionar Eventos
Marque os seguintes eventos:
- ✅ `PAYMENT.CAPTURE.COMPLETED`
- ✅ `PAYMENT.CAPTURE.DENIED`
- ✅ `PAYMENT.CAPTURE.PENDING`
- ✅ `CHECKOUT.ORDER.APPROVED`
- ✅ `CHECKOUT.ORDER.COMPLETED`

### 1.5 Salvar e Copiar Webhook ID
1. Clique em **"Save"**
2. Copie o **Webhook ID** gerado
3. Cole no arquivo `.env.sandbox` no campo `PAYPAL_WEBHOOK_ID`

---

## 🚀 PASSO 2: Configurar o Ambiente

### 2.1 Usar o arquivo .env.sandbox
```powershell
# Copie o .env.sandbox para .env (backup o original primeiro)
Copy-Item .env .env.backup
Copy-Item .env.sandbox .env
```

### 2.2 Preencher o HF_TOKEN
Edite o `.env` e adicione seu token do Hugging Face:
```
HF_TOKEN=seu_token_aqui
```

### 2.3 Adicionar o Webhook ID
Edite o `.env` e adicione o Webhook ID que você copiou:
```
PAYPAL_WEBHOOK_ID=seu_webhook_id_aqui
```

---

## 🧪 PASSO 3: Testar Localmente

### 3.1 Iniciar o Backend
```powershell
cd api
python -m uvicorn main:app --reload --port 8000
```

### 3.2 Iniciar o Frontend (em outro terminal)
```powershell
cd frontend
npm run dev
```

### 3.3 Acessar a Aplicação
Abra o navegador em: http://localhost:3000

---

## 💳 PASSO 4: Realizar Teste de Pagamento

### 4.1 Contas de Teste do PayPal
O PayPal Sandbox cria automaticamente contas de teste. Para acessá-las:

1. Vá para: https://developer.paypal.com/dashboard/
2. Clique em **"Sandbox"** > **"Accounts"**
3. Você verá duas contas:
   - **Business Account** (vendedor - você)
   - **Personal Account** (comprador - para testar)

### 4.2 Credenciais de Teste
Clique em **"View/Edit Account"** na conta Personal para ver:
- Email: `sb-xxxxx@personal.example.com`
- Senha: (gerada automaticamente)

### 4.3 Realizar Compra de Teste
1. Na sua aplicação, vá para a página de pagamento
2. Clique em **"Pagar com PayPal"**
3. Faça login com a conta **Personal** (comprador)
4. Complete o pagamento

### 4.4 Verificar Resultado
- ✅ O pagamento deve ser aprovado
- ✅ O webhook deve ser recebido pela API
- ✅ O status deve ser atualizado no sistema

---

## 🔍 PASSO 5: Verificar Logs

### 5.1 Logs da API
Verifique o terminal onde o backend está rodando:
```
INFO: Webhook recebido do PayPal
INFO: Pagamento aprovado: ORDER_ID_XXXXX
```

### 5.2 Logs do PayPal
1. Acesse: https://developer.paypal.com/dashboard/
2. Vá em **"Sandbox"** > **"Webhooks"**
3. Clique no seu webhook
4. Veja o histórico de eventos enviados

---

## ✅ PASSO 6: Checklist de Validação

Antes de ir para produção, verifique:

- [ ] Webhook criado no sandbox
- [ ] Webhook ID configurado no `.env`
- [ ] Pagamento de teste realizado com sucesso
- [ ] Webhook recebido pela API
- [ ] Status atualizado corretamente no sistema
- [ ] Logs sem erros
- [ ] Fluxo completo funcionando

---

## 🎯 PASSO 7: Migrar para Produção

Quando tudo estiver funcionando no sandbox:

1. **Obter credenciais LIVE**:
   - Acesse: https://developer.paypal.com/dashboard/
   - Mude para modo **"LIVE"** (canto superior direito)
   - Copie o **Client ID** e **Secret** LIVE

2. **Criar webhook LIVE**:
   - Repita o processo do PASSO 1, mas em modo LIVE
   - Use a mesma URL do webhook
   - Copie o novo Webhook ID LIVE

3. **Atualizar .env para produção**:
   ```
   PAYPAL_CLIENT_ID=seu_client_id_live
   PAYPAL_SECRET=seu_secret_live
   PAYPAL_WEBHOOK_ID=seu_webhook_id_live
   PAYPAL_MODE=live
   DIOTEC360_ENV=production
   ```

---

## 🆘 Troubleshooting

### Webhook não está sendo recebido
- Verifique se a URL está acessível publicamente
- Teste a URL: `curl https://diotec-360-diotec-360-ia-judge.hf.space/health`
- Verifique os logs do Hugging Face Space

### Pagamento não é aprovado
- Verifique se está usando a conta Personal (comprador)
- Certifique-se de que a conta tem saldo (sandbox tem saldo infinito)
- Verifique os logs do PayPal no dashboard

### Erro de autenticação
- Verifique se o Client ID e Secret estão corretos
- Certifique-se de estar usando credenciais SANDBOX (não LIVE)
- Verifique se `PAYPAL_MODE=sandbox`

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da API
2. Verifique o dashboard do PayPal
3. Consulte a documentação: https://developer.paypal.com/docs/

---

🏛️ **THE MONOLITH IS READY FOR TESTING**
⚖️ **THE SOVEREIGN JUDGE AWAITS YOUR COMMAND**
