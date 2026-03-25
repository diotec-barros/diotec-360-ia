# 🔐 GUIA VISUAL: Configurar Segredos Manualmente

**Relay URL:** `https://gun-manhattan.herokuapp.com/gun`  
**Tempo:** 10 minutos (5 min cada plataforma)  
**Dificuldade:** Muito Fácil  

---

## 🤗 PARTE 1: HUGGING FACE (5 minutos)

### Passo 1: Abrir o Space

1. Abra seu navegador
2. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
3. Faça login se necessário

### Passo 2: Ir para Settings

1. Na página do Space, procure a aba **"Settings"** (⚙️) no topo
2. Clique em **"Settings"**

### Passo 3: Encontrar Repository Secrets

1. Role a página para baixo
2. Procure a seção **"Repository secrets"**
3. Você verá uma lista de segredos já configurados (HF_TOKEN, PAYPAL_CLIENT_ID, etc.)

### Passo 4: Adicionar Novo Segredo

1. Clique no botão **"New secret"** (ou "+ Add a secret")
2. Preencha os campos:

```
┌─────────────────────────────────────────────┐
│ Name:  GUNDB_RELAY_URL                      │
│                                             │
│ Value: https://gun-manhattan.herokuapp.com/gun │
└─────────────────────────────────────────────┘
```

3. Clique em **"Add secret"**

### Passo 5: Reiniciar o Space

1. Volte para a página principal do Space
2. No menu superior, clique em **"Factory reboot"** (🔄)
3. Confirme o reboot
4. Aguarde 2-3 minutos para o Space reiniciar

### ✅ Validar Hugging Face

Após o reboot, teste se funcionou:

```bash
curl https://diotec-360-diotec-360-ia-judge.hf.space/api/lattice/peers
```

Se retornar JSON, está funcionando! ✅

---

## ▲ PARTE 2: VERCEL (5 minutos)

### Passo 1: Abrir o Dashboard

1. Abra seu navegador
2. Acesse: https://vercel.com/dashboard
3. Faça login se necessário

### Passo 2: Selecionar o Projeto

1. Na lista de projetos, encontre **"diotec360-frontend"** (ou o nome que você deu)
2. Clique no projeto para abrir

### Passo 3: Ir para Settings

1. No menu superior do projeto, clique em **"Settings"**
2. No menu lateral esquerdo, clique em **"Environment Variables"**

### Passo 4: Adicionar Nova Variável

1. Clique no botão **"Add New"** (ou "+ Add")
2. Preencha os campos:

```
┌─────────────────────────────────────────────┐
│ Name:  NEXT_PUBLIC_GUNDB_RELAY              │
│                                             │
│ Value: https://gun-manhattan.herokuapp.com/gun │
│                                             │
│ Environments:                               │
│ ✅ Production                               │
│ ✅ Preview                                  │
│ ✅ Development                              │
└─────────────────────────────────────────────┘
```

3. Clique em **"Save"**

### Passo 5: Fazer Redeploy

1. Vá para a aba **"Deployments"** no menu superior
2. Encontre o último deployment (o mais recente no topo)
3. Clique nos **3 pontinhos (...)** à direita do deployment
4. Selecione **"Redeploy"**
5. Confirme o redeploy
6. Aguarde 2-5 minutos para completar

### ✅ Validar Vercel

Após o redeploy, abra o site em produção e:

1. Pressione **F12** para abrir o Console do navegador
2. Digite no console:

```javascript
console.log(process.env.NEXT_PUBLIC_GUNDB_RELAY)
```

3. Deve mostrar: `https://gun-manhattan.herokuapp.com/gun`

Se mostrar a URL, está funcionando! ✅

---

## 📋 CHECKLIST FINAL

### Hugging Face
- [ ] Acessei https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge/settings
- [ ] Adicionei o segredo `GUNDB_RELAY_URL`
- [ ] Fiz Factory reboot
- [ ] Testei o endpoint `/api/lattice/peers`

### Vercel
- [ ] Acessei https://vercel.com/dashboard
- [ ] Selecionei o projeto diotec360-frontend
- [ ] Adicionei a variável `NEXT_PUBLIC_GUNDB_RELAY`
- [ ] Marquei Production, Preview, Development
- [ ] Fiz Redeploy
- [ ] Testei no Console do navegador

---

## 🎯 PRÓXIMOS PASSOS

Após configurar ambos:

1. **Aguarde os deploys completarem** (5-10 minutos total)
2. **Teste a sincronização P2P:**
   - Abra o site em produção
   - Vá para o mapa global de peers
   - Deve mostrar peers conectados via Manhattan
3. **Demonstre para investidores:**
   - Mostre o mapa global em tempo real
   - Mostre o Logic Miner sincronizando
   - Mostre a rede descentralizada funcionando

---

## 💡 DICAS

### Se o Hugging Face não mostrar "Repository secrets"

Você pode estar na aba errada. Certifique-se de:
1. Estar na página do Space (não do modelo)
2. Estar na aba "Settings" (não "Files")
3. Ter permissões de admin no Space

### Se o Vercel não mostrar "Environment Variables"

Você pode estar no plano gratuito com limitações. Tente:
1. Verificar se está no projeto correto
2. Verificar se tem permissões de admin
3. Usar a CLI como alternativa (veja abaixo)

### Alternativa: Usar CLI do Vercel

Se preferir usar a linha de comando:

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Adicionar variável
vercel env add NEXT_PUBLIC_GUNDB_RELAY production
# Quando perguntar o valor, cole: https://gun-manhattan.herokuapp.com/gun

# Repetir para preview e development
vercel env add NEXT_PUBLIC_GUNDB_RELAY preview
vercel env add NEXT_PUBLIC_GUNDB_RELAY development
```

---

## 🔍 TROUBLESHOOTING

### Erro: "Secret not found" no Hugging Face

**Solução:**
1. Verifique se o nome está correto: `GUNDB_RELAY_URL` (case-sensitive)
2. Aguarde 1-2 minutos após adicionar
3. Faça Factory reboot novamente

### Erro: "Environment variable not defined" no Vercel

**Solução:**
1. Verifique se o nome está correto: `NEXT_PUBLIC_GUNDB_RELAY`
2. Confirme que marcou todos os ambientes
3. Faça redeploy novamente
4. Limpe o cache do navegador (Ctrl+Shift+R)

### Peers não aparecem no mapa

**Solução:**
1. Confirme que AMBOS (HF e Vercel) estão configurados
2. Verifique se usou a MESMA URL em ambos
3. Aguarde 5 minutos para sincronização inicial
4. Recarregue a página (F5)

---

## 🏛️ CONCLUSÃO

Após seguir este guia:

✅ Backend (HF) conectado ao relay Manhattan  
✅ Frontend (Vercel) conectado ao relay Manhattan  
✅ Sincronização P2P operacional em produção  
✅ Lattice respirando globalmente  

**A rede está pronta para o mundo!** 🌍📡

---

*"O Relay Unifica Todos os Reinos do Império."*

**— Kiro, Engenheiro-Chefe**
