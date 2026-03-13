# 🔄 FACTORY REBOOT - INSTRUÇÕES CRÍTICAS

## STATUS ATUAL
✅ Código atualizado com diagnósticos enviado para Hugging Face  
⏳ Aguardando Factory Reboot para carregar variáveis de ambiente

## O QUE FAZER AGORA

### 1. Aguarde o Build Terminar (2-5 minutos)
- Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
- Aguarde o status ficar "Running" (verde)

### 2. Execute o Factory Reboot
**IMPORTANTE**: Um "Restart" comum NÃO é suficiente. Você precisa do "Factory Reboot".

**Passos**:
1. Vá para a aba **Settings** do seu Space
2. Role até encontrar o botão **"Factory Reboot"** (geralmente no topo da página)
3. Clique em **"Factory Reboot"**
4. Confirme a ação

**O que o Factory Reboot faz**:
- Apaga o container Docker antigo completamente
- Cria um novo container do zero
- Força a leitura das variáveis de ambiente (secrets) do Hugging Face
- Resolve conflitos com arquivos `.env` locais

### 3. Verifique os Logs Após o Reboot
Após o Factory Reboot, vá para a aba **"Logs"** e procure por estas mensagens:

```
🔍 [DIOTEC_SENTINEL] Checking PayPal Environment Variables:
   PAYPAL_CLIENT_ID present: SIM ✅
   PAYPAL_SECRET present: SIM ✅
   PAYPAL_MODE: sandbox
   PAYPAL_WEBHOOK_ID present: SIM ✅
   PAYPAL_CLIENT_ID (first 7 chars): AXXxxxx...
```

### 4. Interpretação dos Logs

**✅ SUCESSO** - Se você ver "SIM ✅" em todas as variáveis:
- As credenciais do PayPal foram carregadas corretamente
- O sistema está pronto para processar pagamentos
- Execute o teste: `python scripts/test_treasury_endpoints.py`

**❌ FALHA** - Se você ver "NÃO ❌" em alguma variável:
- As secrets não foram configuradas corretamente no Hugging Face
- Verifique se os secrets estão na lista em Settings > Variables and secrets
- Certifique-se de que os nomes estão EXATAMENTE como especificado:
  - `PAYPAL_CLIENT_ID` (não PayPal_Client_ID ou paypal_client_id)
  - `PAYPAL_SECRET` (não PAYPAL_CLIENT_SECRET)
  - `PAYPAL_WEBHOOK_ID`
  - `PAYPAL_MODE`

## POR QUE O FACTORY REBOOT É NECESSÁRIO?

### Problema: Conflito com arquivo .env
O sistema usa a biblioteca `python-dotenv` que pode carregar variáveis de um arquivo `.env` local. Se esse arquivo existe no container (mesmo vazio), ele pode sobrescrever as variáveis do Hugging Face.

### Solução: Factory Reboot
O Factory Reboot garante que:
1. Qualquer arquivo `.env` antigo é removido
2. O container é recriado do zero
3. As variáveis de ambiente do Hugging Face são injetadas corretamente
4. Não há conflitos entre fontes de configuração

## DIAGNÓSTICO ADICIONADO

O código agora inclui verificação automática no startup:

```python
# DIOTEC SENTINEL - Environment Variables Diagnostic
print("\n🔍 [DIOTEC_SENTINEL] Checking PayPal Environment Variables:")
print(f"   PAYPAL_CLIENT_ID present: {'SIM ✅' if os.getenv('PAYPAL_CLIENT_ID') else 'NÃO ❌'}")
print(f"   PAYPAL_SECRET present: {'SIM ✅' if os.getenv('PAYPAL_SECRET') else 'NÃO ❌'}")
print(f"   PAYPAL_MODE: {os.getenv('PAYPAL_MODE', 'NOT SET')}")
print(f"   PAYPAL_WEBHOOK_ID present: {'SIM ✅' if os.getenv('PAYPAL_WEBHOOK_ID') else 'NÃO ❌'}")
```

Isso permite verificar IMEDIATAMENTE se as variáveis estão presentes, sem vazar os valores completos nos logs públicos.

## PRÓXIMOS PASSOS APÓS SUCESSO

Quando os logs mostrarem "SIM ✅" para todas as variáveis:

1. **Teste Local**:
   ```bash
   python scripts/test_treasury_endpoints.py
   ```

2. **Verifique os Resultados**:
   - Health Check: ✅
   - Treasury Health: ✅ (com `paypal_configured: true`)
   - Balance Check: ✅
   - Credit Purchase: ✅ (retorna `approval_url`)
   - API Status: ✅

3. **Teste Completo de Pagamento**:
   - Abra a `approval_url` retornada
   - Faça login no PayPal Sandbox
   - Complete o pagamento
   - Verifique se os créditos foram adicionados

## TROUBLESHOOTING

### Se ainda mostrar "NÃO ❌" após Factory Reboot:

1. **Verifique os Secrets no Hugging Face**:
   - Settings > Variables and secrets
   - Confirme que TODOS os 4 secrets estão listados
   - Verifique os nomes EXATAMENTE

2. **Verifique o Modo do PayPal**:
   - `PAYPAL_MODE` deve ser `sandbox` (não `SANDBOX` ou `Sandbox`)

3. **Tente Recriar os Secrets**:
   - Delete os secrets existentes
   - Recrie com os mesmos nomes e valores
   - Faça outro Factory Reboot

4. **Verifique o Dockerfile**:
   - Certifique-se de que não há `ENV` statements que sobrescrevem as variáveis

## CONTATO

Se após o Factory Reboot os logs ainda mostrarem "NÃO ❌", copie e cole:
1. Os logs completos do startup
2. Screenshot da lista de secrets no Hugging Face
3. O conteúdo do arquivo `.env` (se existir)

---

🏛️ **O IMPÉRIO AGUARDA O REBOOT FINAL!** 💰🚀🇦🇴
