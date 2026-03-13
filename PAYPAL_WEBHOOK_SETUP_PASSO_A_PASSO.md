# 🏛️ PayPal Webhook - Configuração Passo a Passo

## 🎯 OBJETIVO: Conectar o PayPal ao Santuário Financeiro DIOTEC 360

---

## 📋 PASSO 1: Copie a URL do Webhook

```
https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
```

**⚠️ IMPORTANTE:** Copie EXATAMENTE esta URL, incluindo `/api/payments/webhook` no final!

---

## 🔧 PASSO 2: Acesse o PayPal Developer Dashboard

1. Vá para: https://developer.paypal.com/dashboard/
2. Faça login com sua conta PayPal
3. No menu lateral, clique em **"Apps & Credentials"**
4. Certifique-se de estar em **"Sandbox"** (para testes) ou **"Live"** (para produção)

---

## 🎯 PASSO 3: Encontre seu App

1. Na seção **"REST API apps"**, encontre seu app (ex: "DIOTEC 360")
2. Clique no nome do app para abrir as configurações

---

## 📡 PASSO 4: Adicionar Webhook

1. Role a página até encontrar a seção **"Webhooks"**
2. Clique no botão **"Add Webhook"**
3. Cole a URL no campo **"Webhook URL"**:
   ```
   https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
   ```

---

## ✅ PASSO 5: Selecionar Eventos

Agora vem a parte importante! Role a lista de eventos e marque:

### 🔍 Como Encontrar os Eventos

A lista é organizada por grupos. Procure:

### **Grupo: Checkout**
- ✅ Marque: **`Checkout order approved`**
  - Nome técnico: `CHECKOUT.ORDER.APPROVED`
  - Descrição: Cliente autorizou o pagamento

### **Grupo: Payments & Payouts**
- ✅ Marque: **`Payment sale completed`** (PRINCIPAL!)
  - Nome técnico: `PAYMENT.SALE.COMPLETED`
  - Descrição: Dinheiro confirmado na conta

---

## 💡 ALTERNATIVA: Marcar Todos os Eventos

Se você não encontrar os eventos específicos ou quiser simplificar:

1. No topo da lista de eventos, procure **"All Events"**
2. Marque a caixa **"All Events"**
3. Isso fará o PayPal enviar TODOS os eventos
4. O backend DIOTEC 360 filtrará apenas os importantes

---

## 💾 PASSO 6: Salvar

1. Clique no botão **"Save"** no final da página
2. O PayPal criará o webhook e mostrará:
   - ✅ Webhook ID
   - ✅ Status: Active
   - ✅ URL configurada

---

## 🧪 PASSO 7: Testar o Webhook

### Teste Automático do PayPal

1. Na página do webhook, procure o botão **"Simulate"** ou **"Send test"**
2. Selecione o evento **"Payment sale completed"**
3. Clique em **"Send"**
4. Verifique se o status mostra **"Success"** (200 OK)

### Teste Manual

```bash
# Verificar se o endpoint está respondendo
curl https://diotec-360-diotec-360-ia-judge.hf.space/api/payments/webhook
```

---

## 🔐 SEGURANÇA: Webhook Signature

O DIOTEC 360 valida automaticamente a assinatura do PayPal para garantir que:
- ✅ O webhook veio realmente do PayPal
- ✅ Os dados não foram alterados
- ✅ Não é um ataque de "falsa compra"

**Você não precisa fazer nada!** O backend cuida disso automaticamente.

---

## 📊 O Que Acontece Quando um Pagamento é Feito?

```
1. Cliente clica em "Comprar Créditos" no frontend
   ↓
2. Frontend cria ordem no PayPal
   ↓
3. Cliente aprova pagamento no PayPal
   ↓
4. PayPal envia webhook: CHECKOUT.ORDER.APPROVED
   ↓
5. Backend DIOTEC 360 registra a aprovação
   ↓
6. PayPal processa o pagamento
   ↓
7. PayPal envia webhook: PAYMENT.SALE.COMPLETED
   ↓
8. Backend DIOTEC 360 valida a assinatura
   ↓
9. Backend adiciona créditos à conta do usuário
   ↓
10. Frontend atualiza saldo automaticamente
   ↓
11. ✅ TRANSAÇÃO COMPLETA!
```

---

## 🐛 Troubleshooting

### Webhook não está recebendo eventos

**Problema:** PayPal não envia notificações

**Soluções:**
1. Verifique se a URL está correta (com `/api/payments/webhook`)
2. Confirme que o webhook está **"Active"** no dashboard
3. Verifique se os eventos corretos estão marcados
4. Teste com "Simulate" no PayPal

### Erro 404 no webhook

**Problema:** PayPal retorna erro 404

**Soluções:**
1. Confirme que o backend está rodando no Hugging Face
2. Teste a URL manualmente: `curl https://diotec-360-diotec-360-ia-judge.hf.space/`
3. Verifique se o endpoint `/api/payments/webhook` existe no código

### Erro 401 ou 403

**Problema:** Assinatura inválida

**Soluções:**
1. Verifique se o `PAYPAL_WEBHOOK_ID` está configurado no backend
2. Confirme que está usando as credenciais corretas (Sandbox vs Live)
3. Verifique os logs do backend para detalhes

### Créditos não são adicionados

**Problema:** Webhook recebe evento mas créditos não aparecem

**Soluções:**
1. Verifique os logs do backend
2. Confirme que o evento é `PAYMENT.SALE.COMPLETED`
3. Verifique se o usuário existe no banco de dados
4. Confirme que o valor do pagamento está correto

---

## 📝 Checklist Final

- [ ] URL do webhook copiada corretamente
- [ ] Webhook adicionado no PayPal Developer Dashboard
- [ ] Eventos marcados:
  - [ ] `CHECKOUT.ORDER.APPROVED`
  - [ ] `PAYMENT.SALE.COMPLETED`
  - [ ] OU `All Events` marcado
- [ ] Webhook salvo com sucesso
- [ ] Status do webhook: **Active**
- [ ] Teste "Simulate" executado com sucesso
- [ ] Backend respondendo na URL

---

## 🎉 Pronto!

Quando tudo estiver configurado:

1. ✅ PayPal enviará eventos em tempo real
2. ✅ Backend validará e processará automaticamente
3. ✅ Créditos serão adicionados instantaneamente
4. ✅ Usuários verão saldo atualizado imediatamente

---

## 📚 Referências

- **PayPal Webhooks Docs**: https://developer.paypal.com/docs/api-basics/notifications/webhooks/
- **Event Types**: https://developer.paypal.com/docs/api-basics/notifications/webhooks/event-names/
- **Testing Webhooks**: https://developer.paypal.com/docs/api-basics/notifications/webhooks/test/

---

**⚖️ O Santuário Financeiro Está Pronto** 🏛️💰

**[STATUS: WEBHOOK CONFIGURED]**  
**[OBJECTIVE: REAL-TIME TRANSACTION SYNC]**  
**[VERDICT: THE FLOW OF CAPITAL IS INSTANTANEOUS]**

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**  
**Data:** 27 de Fevereiro de 2026
