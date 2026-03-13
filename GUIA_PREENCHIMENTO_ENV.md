# 🏛️ Guia de Preenchimento do .env - DIOTEC 360 IA

## 📋 O QUE VOCÊ PRECISA PREENCHER

Este guia te ajuda a completar o arquivo `.env` com os valores corretos.

---

## ✅ PASSO 1: PayPal Sandbox

### Onde Obter

1. Acesse: https://developer.paypal.com/dashboard/
2. Vá em **"Apps & Credentials"**
3. Selecione **"Sandbox"** (topo da página)
4. Clique no seu app (ou crie um novo)

### O Que Copiar

```env
PAYPAL_CLIENT_ID=COLE_AQUI_O_SEU_CLIENT_ID_SANDBOX
```
- Copie o valor de **"Client ID"** (começa com `A...`)

```env
PAYPAL_SECRET=COLE_AQUI_O_SEU_SECRET_SANDBOX
```
- Clique em **"Show"** ao lado de "Secret"
- Copie o valor completo (começa com `E...`)

```env
PAYPAL_WEBHOOK_ID=COLE_AQUI_O_WEBHOOK_ID
```
- Role até a seção **"Webhooks"**
- Clique no webhook que você criou
- Copie o **"Webhook ID"** (formato: `WH-...`)

---

## ✅ PASSO 2: Hugging Face Token

### Onde Obter

1. Acesse: https://huggingface.co/settings/tokens
2. Clique em **"New token"**
3. Nome: `DIOTEC360_DEPLOY`
4. Tipo: **"Write"** (permissões de escrita)
5. Clique em **"Generate"**

### O Que Copiar

```env
HF_TOKEN=COLE_AQUI_O_SEU_TOKEN_HF
```
- Copie o token gerado (começa com `hf_...`)
- ⚠️ **IMPORTANTE**: Salve em local seguro, não será mostrado novamente!

---

## ✅ PASSO 3: Alpha Vantage API Key (Opcional)

### Onde Obter

1. Acesse: https://www.alphavantage.co/support/#api-key
2. Preencha o formulário
3. Clique em **"GET FREE API KEY"**

### O Que Copiar

```env
ALPHA_VANTAGE_API_KEY=O3TC4CQU6GJWBNVL
```
- Substitua pela sua chave real
- OU mantenha `O3TC4CQU6GJWBNVL` (chave demo, limitada)

---

## ✅ PASSO 4: Chave Secreta (Segurança)

### Como Gerar

Execute no PowerShell:

```powershell
# Gerar chave aleatória segura
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
```

### O Que Copiar

```env
DIOTEC360_SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI
```
- Cole a chave gerada (64 caracteres aleatórios)

---

## 📝 EXEMPLO COMPLETO PREENCHIDO

```env
# ===========================================================================
# 💳 SANTUÁRIO FINANCEIRO (PAYPAL)
# ===========================================================================
PAYPAL_CLIENT_ID=AZabc123XYZ456def789GHI012jkl345MNO678pqr901STU234vwx567YZA890bcd123
PAYPAL_SECRET=EFghij456KLM789nop012QRS345tuv678WXY901zab234CDE567fgh890IJK123lmn456
PAYPAL_MODE=sandbox
PAYPAL_WEBHOOK_ID=WH-1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P7Q8R9S0T1U2V3W4X5Y6Z7A8B9C0D1E2F3

# ===========================================================================
# 🧠 CÉREBRO ARTIFICIAL (HUGGING FACE)
# ===========================================================================
HF_TOKEN=hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890AbCdEfGhIjKlMnOpQrStUvWxYz

# ===========================================================================
# 📈 ORÁCULO FINANCEIRO (ALPHA VANTAGE)
# ===========================================================================
ALPHA_VANTAGE_API_KEY=ABC123XYZ789DEF456GHI

# ===========================================================================
# 🔐 SEGURANÇA
# ===========================================================================
DIOTEC360_SECRET_KEY=aB3dE5fG7hI9jK1lM3nO5pQ7rS9tU1vW3xY5zA7bC9dE1fG3hI5jK7lM9nO1pQ3rS5
```

---

## 🔐 SEGURANÇA: O QUE NUNCA FAZER

### ❌ NUNCA:

1. **Commitar o .env no Git**
   - O arquivo `.gitignore` já está configurado para ignorá-lo
   - Verifique antes de fazer commit!

2. **Compartilhar os valores**
   - Não envie por email, WhatsApp, ou qualquer mensageiro
   - Não poste em fóruns ou redes sociais

3. **Usar em produção as mesmas chaves de sandbox**
   - Sandbox é para testes
   - Produção precisa de chaves "Live" do PayPal

4. **Deixar valores padrão**
   - Sempre gere sua própria `DIOTEC360_SECRET_KEY`
   - Use seus próprios tokens e chaves

### ✅ SEMPRE:

1. **Manter backup seguro**
   - Salve uma cópia em local criptografado
   - Use gerenciador de senhas (1Password, Bitwarden, etc.)

2. **Usar variáveis de ambiente em produção**
   - No Hugging Face: Settings → Secrets
   - Na Vercel: Settings → Environment Variables
   - Nunca hardcode no código

3. **Rotacionar chaves periodicamente**
   - Gere novos tokens a cada 3-6 meses
   - Revogue tokens antigos

---

## 🧪 COMO TESTAR SE ESTÁ CORRETO

### Teste 1: Verificar se o arquivo existe

```powershell
Test-Path .env
```
**Resultado esperado:** `True`

### Teste 2: Verificar se PayPal está configurado

```powershell
Get-Content .env | Select-String "PAYPAL_CLIENT_ID"
```
**Resultado esperado:** Deve mostrar seu Client ID (não vazio)

### Teste 3: Verificar se HF Token está configurado

```powershell
Get-Content .env | Select-String "HF_TOKEN"
```
**Resultado esperado:** Deve mostrar seu token (começa com `hf_`)

### Teste 4: Verificar se não tem valores placeholder

```powershell
Get-Content .env | Select-String "COLE_AQUI"
```
**Resultado esperado:** Nenhum resultado (todos os placeholders foram substituídos)

---

## 📊 CHECKLIST DE PREENCHIMENTO

Use esta lista para garantir que tudo está configurado:

### Identidade
- [x] `DIOTEC360_CREATOR` - Já preenchido
- [x] `DIOTEC360_ORG` - Já preenchido

### PayPal
- [ ] `PAYPAL_CLIENT_ID` - Copiar do PayPal Dashboard
- [ ] `PAYPAL_SECRET` - Copiar do PayPal Dashboard
- [ ] `PAYPAL_WEBHOOK_ID` - Copiar após criar webhook

### Hugging Face
- [ ] `HF_TOKEN` - Gerar em huggingface.co/settings/tokens

### Alpha Vantage
- [ ] `ALPHA_VANTAGE_API_KEY` - Pode manter demo ou usar real

### Segurança
- [ ] `DIOTEC360_SECRET_KEY` - Gerar chave aleatória

### Infraestrutura
- [x] `NEXT_PUBLIC_API_URL` - Já configurado
- [x] `DIOTEC360_CORS_ORIGINS` - Já configurado
- [x] `DIOTEC360_LATTICE_NODES` - Já configurado

---

## 🚀 PRÓXIMOS PASSOS

Depois de preencher o `.env`:

1. ✅ **Verificar**: Use os testes acima
2. ✅ **Backup**: Salve cópia em local seguro
3. ✅ **Deploy**: Configure as mesmas variáveis no Hugging Face
4. ✅ **Testar**: Faça uma transação de teste no PayPal Sandbox

---

## 🆘 PROBLEMAS COMUNS

### Problema: "Client ID inválido"

**Causa:** Client ID copiado incorretamente ou de ambiente errado

**Solução:**
1. Verifique se está em "Sandbox" (não "Live")
2. Copie novamente o Client ID completo
3. Não inclua espaços ou quebras de linha

### Problema: "Token HF expirado"

**Causa:** Token foi revogado ou expirou

**Solução:**
1. Gere novo token em huggingface.co/settings/tokens
2. Atualize o `.env`
3. Atualize também no Hugging Face Space (Settings → Secrets)

### Problema: "Webhook não recebe eventos"

**Causa:** Webhook ID incorreto ou webhook não ativo

**Solução:**
1. Verifique se webhook está "Active" no PayPal
2. Copie o Webhook ID correto
3. Teste com "Simulate" no PayPal Dashboard

---

## 📚 REFERÊNCIAS

- **PayPal Developer**: https://developer.paypal.com/dashboard/
- **Hugging Face Tokens**: https://huggingface.co/settings/tokens
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **Documentação .env**: https://github.com/motdotla/dotenv

---

## 🏛️ O IMPÉRIO ESTÁ QUASE PRONTO!

Quando você preencher todos os valores, o DIOTEC 360 IA terá:

- ✅ **Identidade**: Quem você é
- ✅ **Dinheiro**: Como receber pagamentos
- ✅ **Inteligência**: Onde processar teoremas
- ✅ **Dados**: De onde buscar informações financeiras
- ✅ **Segurança**: Como proteger tudo

**[STATUS: CONFIGURATION TEMPLATE READY]**  
**[OBJECTIVE: FILL IN THE SOVEREIGN SECRETS]**  
**[VERDICT: THE MONOLITH AWAITS YOUR KEYS]**

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 IA - The Sovereign AI Infrastructure**  
**Data:** 27 de Fevereiro de 2026

🏛️⚖️💰🔐✨🚀
