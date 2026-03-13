# 💰 Guia: Completar Teste de Pagamento PayPal

## 🎯 Objetivo
Completar a primeira transação de teste para validar o fluxo completo de pagamento e webhook.

---

## 📋 Passo a Passo

### 1. Abrir URL de Aprovação

**URL Gerada pelo Sistema**:
```
https://www.sandbox.paypal.com/checkoutnow?token=2T177648TS519851E
```

👉 **Ação**: Copie e cole esta URL no seu navegador

---

### 2. Login no PayPal Sandbox

Você precisa usar a conta **PERSONAL** (comprador) do Sandbox, NÃO a conta Business.

**Como encontrar as credenciais**:

1. Acesse: https://developer.paypal.com/dashboard/
2. Vá em: **Sandbox** → **Accounts**
3. Procure a conta com tipo **PERSONAL**
4. Clique nos 3 pontinhos (...) → **View/Edit Account**
5. Veja o **Email** e **Password**

**Exemplo de credenciais Sandbox**:
```
Email: sb-buyer47xxx@personal.example.com
Password: (gerada automaticamente pelo PayPal)
```

---

### 3. Completar o Pagamento

Na página do PayPal:

1. ✅ Revise os detalhes:
   - **Merchant**: DIOTEC 360 IA
   - **Amount**: $9.99 USD
   - **Description**: Starter Package (1,000 credits)

2. ✅ Clique em **"Pay Now"** ou **"Pagar Agora"**

3. ✅ Confirme a transação

---

### 4. Verificar Webhook (Logs do Hugging Face)

Após completar o pagamento, o PayPal enviará um webhook para o sistema.

**Como ver os logs**:

1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
2. Clique na aba **"Logs"**
3. Procure por estas mensagens:

```
[TREASURY] Webhook received from PayPal
[TREASURY] Event type: PAYMENT.SALE.COMPLETED
[TREASURY] Order ID: 2T177648TS519851E
[TREASURY] Minting 1,000 credits for user: test_pubkey_test_user_dionisio_001
[TREASURY] ✅ Credits added successfully
[TREASURY] New balance: 1,000 credits
```

---

### 5. Confirmar Saldo de Créditos

Teste o endpoint de balance para confirmar que os créditos foram adicionados:

**Opção A - Via Script**:
```powershell
cd diotec360
python scripts/test_treasury_endpoints.py
```

**Opção B - Via Browser**:
```
https://diotec-360-diotec-360-ia-judge.hf.space/api/treasury/balance?user_public_key=test_pubkey_test_user_dionisio_001
```

**Resposta Esperada**:
```json
{
  "ok": true,
  "credits": 1000,
  "public_key": "test_pubkey_test_user_dionisio_001"
}
```

---

## 🔍 Troubleshooting

### Problema: Não consigo fazer login no PayPal Sandbox

**Solução**:
1. Certifique-se de estar usando a conta **PERSONAL**, não a Business
2. Verifique se está usando o email completo (ex: `sb-xxxxx@personal.example.com`)
3. Se esqueceu a senha, você pode resetá-la no PayPal Developer Dashboard

### Problema: Webhook não aparece nos logs

**Solução**:
1. Verifique se o Webhook ID está configurado corretamente no Hugging Face
2. Confirme que a URL do webhook está correta: `https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook`
3. Aguarde até 30 segundos - webhooks podem ter delay

### Problema: Créditos não foram adicionados

**Solução**:
1. Verifique os logs para ver se houve erro no processamento
2. Confirme que o Order ID no webhook corresponde ao Order ID da compra
3. Teste manualmente o endpoint de balance

---

## 🎉 Sucesso!

Quando você ver:
- ✅ Pagamento completado no PayPal
- ✅ Webhook recebido nos logs
- ✅ Saldo mostrando 1,000 credits

**Parabéns!** O fluxo completo de pagamento está funcionando:
1. Criação de Order ✅
2. Pagamento via PayPal ✅
3. Webhook de confirmação ✅
4. Mintagem de créditos ✅
5. Atualização de saldo ✅

---

## 📊 Próximos Testes

Após o primeiro pagamento funcionar, você pode testar:

1. **Diferentes Pacotes**:
   - Professional: $49.99 (10,000 credits)
   - Enterprise: $199.99 (50,000 credits)

2. **Múltiplos Usuários**:
   - Criar orders para diferentes `user_public_key`
   - Verificar isolamento de saldos

3. **Cancelamento**:
   - Iniciar compra mas clicar em "Cancel"
   - Verificar que créditos NÃO são adicionados

4. **Produção**:
   - Trocar `PAYPAL_MODE=production`
   - Usar credenciais reais
   - Processar pagamentos reais

---

## 🔐 Segurança em Produção

Quando for para produção:

1. ✅ Trocar para credenciais de produção
2. ✅ Configurar `PAYPAL_MODE=production`
3. ✅ Atualizar Webhook URL para domínio real
4. ✅ Implementar rate limiting
5. ✅ Adicionar monitoramento de transações
6. ✅ Configurar alertas de fraude

---

**DIOTEC 360 IA - Treasury System v3.6.0**  
*Sovereign Intelligence, Global Payments* 🇦🇴💰🌍
