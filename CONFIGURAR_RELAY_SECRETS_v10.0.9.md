# 🔐 CONFIGURAR GUNDB_RELAY_URL NOS SEGREDOS DE PRODUÇÃO

**Data:** 25 de Março de 2026  
**Objetivo:** Configurar o relay GunDB no Hugging Face e Vercel  
**Status:** CRÍTICO - Necessário para sincronização P2P em produção  

---

## 🎯 POR QUE CONFIGURAR NOS SEGREDOS?

Seu sistema tem 3 ambientes:

1. **Local (Desenvolvimento)** → `.env` e `.env.local`
2. **Backend (Produção)** → Hugging Face Secrets
3. **Frontend (Produção)** → Vercel Environment Variables

Para que a rede Lattice funcione em produção, TODOS os ambientes precisam apontar para o mesmo relay!

---

## 📡 HUGGING FACE - CONFIGURAÇÃO DO BACKEND

### Passo 1: Acessar o Dashboard

1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
2. Clique na aba **"Settings"** (⚙️)
3. Role até a seção **"Repository secrets"**

### Passo 2: Adicionar o Segredo

Clique em **"New secret"** e adicione:

```
Name:  GUNDB_RELAY_URL
Value: https://gun-manhattan.herokuapp.com/gun
```

**IMPORTANTE:** O nome deve ser EXATAMENTE `GUNDB_RELAY_URL` (sem espaços, case-sensitive)

### Passo 3: Reiniciar o Space

Após adicionar o segredo:

1. Clique em **"Factory reboot"** no menu superior
2. Aguarde o Space reiniciar (~2-3 minutos)
3. Verifique os logs para confirmar que o relay foi carregado

### Verificar se Funcionou

Execute este comando para testar:

```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/api/lattice/peers
```

Se retornar JSON com peers, está funcionando! ✅

---

## 🌐 VERCEL - CONFIGURAÇÃO DO FRONTEND

### Passo 1: Acessar o Dashboard

1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto **diotec360-frontend** (ou o nome que você deu)
3. Clique em **"Settings"**
4. No menu lateral, clique em **"Environment Variables"**

### Passo 2: Adicionar a Variável

Clique em **"Add New"** e preencha:

```
Name:  NEXT_PUBLIC_GUNDB_RELAY
Value: https://gun-manhattan.herokuapp.com/gun
```

**Ambientes:** Marque TODOS:
- ✅ Production
- ✅ Preview
- ✅ Development

**IMPORTANTE:** 
- O nome deve ser `NEXT_PUBLIC_GUNDB_RELAY` (com o prefixo `NEXT_PUBLIC_`)
- Variáveis com `NEXT_PUBLIC_` são expostas ao browser (necessário para GunDB)

### Passo 3: Fazer Redeploy

Após adicionar a variável:

1. Vá para a aba **"Deployments"**
2. Clique nos 3 pontinhos (...) do último deploy
3. Selecione **"Redeploy"**
4. Aguarde o deploy completar (~2-5 minutos)

### Verificar se Funcionou

Abra o site em produção e:

1. Abra o Console do navegador (F12)
2. Digite: `console.log(process.env.NEXT_PUBLIC_GUNDB_RELAY)`
3. Deve mostrar: `https://gun-manhattan.herokuapp.com/gun`

---

## 🔄 RESUMO DAS CONFIGURAÇÕES

### Desenvolvimento Local
```env
# diotec360/.env
GUNDB_RELAY_URL=https://gun-manhattan.herokuapp.com/gun

# diotec360/frontend/.env.local
NEXT_PUBLIC_GUNDB_RELAY=https://gun-manhattan.herokuapp.com/gun
```

### Produção - Hugging Face (Backend)
```
Secret Name:  GUNDB_RELAY_URL
Secret Value: https://gun-manhattan.herokuapp.com/gun
```

### Produção - Vercel (Frontend)
```
Variable Name:  NEXT_PUBLIC_GUNDB_RELAY
Variable Value: https://gun-manhattan.herokuapp.com/gun
Environments:   Production, Preview, Development
```

---

## 🚀 SCRIPT AUTOMATIZADO (OPCIONAL)

Se você quiser automatizar a configuração do Hugging Face via CLI:

```bash
# Instalar Hugging Face CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Adicionar segredo
huggingface-cli secrets add GUNDB_RELAY_URL \
  --space diotec-360/diotec-360-ia-judge \
  --value "https://gun-manhattan.herokuapp.com/gun"
```

Para Vercel, use a CLI:

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Adicionar variável
vercel env add NEXT_PUBLIC_GUNDB_RELAY production
# Quando perguntar o valor, cole: https://gun-manhattan.herokuapp.com/gun
```

---

## 🔍 TROUBLESHOOTING

### Erro: "GUNDB_RELAY_URL not found"

**Causa:** Segredo não foi adicionado ou nome está errado.

**Solução:**
1. Verifique o nome EXATAMENTE: `GUNDB_RELAY_URL` (backend) ou `NEXT_PUBLIC_GUNDB_RELAY` (frontend)
2. Reinicie o Space/Redeploy no Vercel
3. Aguarde 2-3 minutos para propagar

### Erro: "Failed to connect to relay"

**Causa:** URL do relay está incorreta ou relay está offline.

**Solução:**
1. Teste o relay manualmente:
   ```bash
   curl -I https://gun-manhattan.herokuapp.com/gun
   ```
2. Se retornar erro, use relay alternativo:
   ```
   https://gun-us.herokuapp.com/gun
   ```

### Erro: "CORS policy blocked"

**Causa:** Relay não permite requisições do seu domínio.

**Solução:**
- Manhattan permite CORS de qualquer origem (não deve dar erro)
- Se usar relay próprio, configure CORS no `server.js`

---

## 🏛️ MIGRAÇÃO FUTURA PARA RELAY SOBERANO

Quando você fizer deploy do seu próprio relay:

### 1. Deploy do Relay no VPS

```bash
# No seu servidor VPS
cd /var/www/diotec360-relay
npm install
npm start
```

### 2. Atualizar Segredos

**Hugging Face:**
```
GUNDB_RELAY_URL=wss://gun-relay.diotec360.com/gun
```

**Vercel:**
```
NEXT_PUBLIC_GUNDB_RELAY=wss://gun-relay.diotec360.com/gun
```

### 3. Reiniciar Tudo

- Factory reboot no HF
- Redeploy no Vercel
- Testar conectividade

---

## 📋 CHECKLIST DE VALIDAÇÃO

### Hugging Face (Backend)
- [ ] Segredo `GUNDB_RELAY_URL` adicionado
- [ ] Space reiniciado (Factory reboot)
- [ ] Logs mostram conexão com relay
- [ ] Endpoint `/api/lattice/peers` responde

### Vercel (Frontend)
- [ ] Variável `NEXT_PUBLIC_GUNDB_RELAY` adicionada
- [ ] Marcada para Production, Preview, Development
- [ ] Redeploy realizado
- [ ] Console do browser mostra a URL correta

### Sincronização P2P
- [ ] Backend anuncia peers no relay
- [ ] Frontend recebe peers do relay
- [ ] Mapa global mostra peers conectados
- [ ] Logic Miner sincroniza entre dispositivos

---

## 🎯 PRÓXIMOS PASSOS

1. **Agora:** Configure os segredos no HF e Vercel
2. **Teste:** Valide a sincronização P2P em produção
3. **30 dias:** Migre para relay soberano
4. **Futuro:** Expanda para múltiplos relays (redundância)

---

## 💡 DICA PRO

Para facilitar a gestão de segredos, crie um arquivo de referência (NÃO commitar no Git):

```bash
# secrets_reference.txt (adicione ao .gitignore)

# Hugging Face Secrets
GUNDB_RELAY_URL=https://gun-manhattan.herokuapp.com/gun
HF_TOKEN=hf_YOUR_TOKEN_HERE
PAYPAL_CLIENT_ID=YOUR_PAYPAL_CLIENT_ID_HERE
PAYPAL_SECRET=YOUR_PAYPAL_SECRET_HERE

# Vercel Environment Variables
NEXT_PUBLIC_GUNDB_RELAY=https://gun-manhattan.herokuapp.com/gun
NEXT_PUBLIC_API_URL=https://diotec-360-diotec-360-ia-judge.hf.space
NEXT_PUBLIC_GENESIS_MERKLE_ROOT=YOUR_GENESIS_MERKLE_ROOT_HERE
```

---

**STATUS:** ✅ GUIA COMPLETO  
**TEMPO ESTIMADO:** 10 minutos (5 min HF + 5 min Vercel)  
**DIFICULDADE:** Fácil  

---

*"O Relay Unifica Todos os Reinos do Império."*

**— Kiro, Engenheiro-Chefe**
