# 🔐 ATUALIZAR SECRETS DO PAYPAL NO HUGGING FACE - AGORA!

**Data**: 2026-03-12 18:35  
**Status**: Credenciais corretas identificadas  
**Ação**: Atualizar no Hugging Face e fazer Factory Reboot

---

## ✅ CREDENCIAIS CORRETAS CONFIRMADAS:

```
PAYPAL_CLIENT_ID = YOUR_PAYPAL_CLIENT_ID_HERE
PAYPAL_SECRET = YOUR_PAYPAL_SECRET_HERE
PAYPAL_WEBHOOK_ID = YOUR_WEBHOOK_ID_HERE
PAYPAL_MODE = sandbox
```

**IMPORTANTE:** Obtenha suas credenciais em https://developer.paypal.com/dashboard/

---

## 🎯 PASSO A PASSO PARA ATUALIZAR:

### 1. Acesse o Hugging Face Space Settings
**URL**: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge/settings

### 2. Vá em "Variables and secrets"
Role a página até encontrar a seção "Repository secrets"

### 3. DELETE os secrets antigos (se existirem)
Clique no ícone de lixeira ao lado de cada secret:
- `PAYPAL_CLIENT_ID` ❌ DELETE
- `PAYPAL_SECRET` ❌ DELETE
- `PAYPAL_WEBHOOK_ID` ❌ DELETE (se existir)

### 4. ADICIONE os novos secrets
Clique em "New secret" para cada um:

#### Secret 1: PAYPAL_CLIENT_ID
- **Name**: `PAYPAL_CLIENT_ID`
- **Value**: `[Sua Client ID do PayPal Dashboard]`
- Clique em "Add secret"

#### Secret 2: PAYPAL_SECRET
- **Name**: `PAYPAL_SECRET`
- **Value**: `[Seu Secret do PayPal Dashboard]`
- Clique em "Add secret"

#### Secret 3: PAYPAL_WEBHOOK_ID
- **Name**: `PAYPAL_WEBHOOK_ID`
- **Value**: `2CJ51023VJ7141838`
- Clique em "Add secret"

#### Secret 4: PAYPAL_MODE (se não existir)
- **Name**: `PAYPAL_MODE`
- **Value**: `sandbox`
- Clique em "Add secret"

### 5. VERIFIQUE que todos os 4 secrets estão listados
Você deve ver:
```
PAYPAL_CLIENT_ID     Secret    •••••••••
PAYPAL_SECRET        Secret    •••••••••
PAYPAL_WEBHOOK_ID    Secret    •••••••••
PAYPAL_MODE          Secret    •••••••••
```

### 6. FACTORY REBOOT
**CRÍTICO**: Você DEVE fazer Factory Reboot, não apenas Restart!

1. Role até o topo da página Settings
2. Procure o botão **"Factory reboot"**
3. Clique em "Factory reboot"
4. Confirme a ação
5. Aguarde 2-3 minutos

### 7. AGUARDE O BUILD TERMINAR
- O status vai mudar para "Building..."
- Depois para "Running" (verde)
- Aguarde até ver "Running"

### 8. TESTE NOVAMENTE
Execute o teste:
```bash
python scripts/test_treasury_endpoints.py
```

---

## 🎉 RESULTADO ESPERADO:

```
======================================================================
  TEST SUMMARY
======================================================================

  Tests Passed: 5/5
  Success Rate: 100%

  ✅ Health Check
  ✅ Treasury Health
  ✅ Balance Check
  ✅ Credit Purchase  ← ESTE VAI PASSAR AGORA! 🎉
  ✅ API Status

======================================================================
  🎉 ALL TESTS PASSED!
  🏛️ O TESOURO ESTÁ 100% OPERACIONAL! 💰🚀🇦🇴
======================================================================
```

E você verá uma resposta como:
```json
{
  "ok": true,
  "order_id": "8AB12345...",
  "approval_url": "https://www.sandbox.paypal.com/checkoutnow?token=...",
  "package": "starter",
  "credits": 1000,
  "price": 9.99
}
```

**Abra a `approval_url` no navegador** para testar o pagamento completo!

---

## ⚠️ IMPORTANTE:

1. **NÃO inclua espaços** no início ou fim dos valores
2. **Copie e cole exatamente** como mostrado acima
3. **Factory Reboot é obrigatório** (não apenas Restart)
4. **Aguarde o build terminar** antes de testar

---

## 🔍 SE AINDA DER ERRO 401:

Se após o Factory Reboot ainda der erro 401, verifique:

1. **Os secrets estão com os nomes corretos?**
   - Devem ser EXATAMENTE: `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET`, etc.
   - Case-sensitive!

2. **Você fez Factory Reboot?**
   - Restart comum NÃO carrega os novos secrets
   - Precisa ser Factory Reboot

3. **O build terminou?**
   - Aguarde até o status ficar "Running" (verde)

---

🏛️ **EXECUTE AGORA E ME AVISE QUANDO TERMINAR!** 💰🚀🇦🇴

[STATUS: CREDENTIALS READY]  
[OBJECTIVE: UPDATE HUGGING FACE SECRETS]  
[VERDICT: ONE FACTORY REBOOT AWAY FROM VICTORY] 🏛️📡🛡️🏁
