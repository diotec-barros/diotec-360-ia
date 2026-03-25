# 🚀 GUIA DE DEPLOY COMPLETO v10.0.9

**Versão:** Lattice P2P Network v10.0.9  
**Data:** 25 de Março de 2026  
**Objetivo:** Deploy completo para GitHub + Hugging Face + Vercel  

---

## 📋 PRÉ-REQUISITOS

Antes de fazer o deploy, certifique-se de ter:

- [x] Git instalado e configurado
- [x] Autenticado no GitHub (git config user.name e user.email)
- [x] Repositório remoto configurado (origin)
- [x] Conta no Hugging Face
- [x] Conta no Vercel (para frontend)
- [x] Todas as mudanças testadas localmente

---

## 🚀 OPÇÃO 1: DEPLOY AUTOMATIZADO (RECOMENDADO)

### Passo Único: Execute o Script

```bash
DEPLOY_COMPLETO_v10.0.9.bat
```

O script fará automaticamente:

1. ✅ Verificação de segurança (.gitignore, .env)
2. ✅ Git status e confirmação
3. ✅ Commit com mensagem personalizada
4. ✅ Push para GitHub
5. ✅ Trigger automático do Hugging Face
6. ✅ Instruções para próximos passos

**Tempo estimado:** 2-3 minutos

---

## 🛠️ OPÇÃO 2: DEPLOY MANUAL

### Passo 1: Verificar Segurança

```bash
cd diotec360

# Verificar .gitignore
cat .gitignore | grep ".env"

# Verificar status
git status
```

### Passo 2: Commit e Push para GitHub

```bash
# Adicionar arquivos
git add .

# Criar commit
git commit -m "feat: Lattice P2P Network v10.0.9 - Estratégia Híbrida"

# Push para GitHub
git push origin main
```

### Passo 3: Deploy no Hugging Face

O Hugging Face está configurado para deploy automático a partir do GitHub.

1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
2. Aguarde o deploy automático (2-3 minutos)
3. Verifique os logs para confirmar sucesso

**Alternativa: Factory Reboot Manual**

Se o deploy automático não funcionar:

1. Vá para o Space
2. Clique em "Factory reboot"
3. Aguarde 2-3 minutos

### Passo 4: Deploy no Vercel (Frontend)

O Vercel também está configurado para deploy automático.

1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto diotec360-frontend
3. Aguarde o deploy automático (2-5 minutos)

**Alternativa: Redeploy Manual**

Se o deploy automático não funcionar:

1. Vá para Deployments
2. Clique nos 3 pontinhos (...) do último deploy
3. Selecione "Redeploy"

---

## 🔐 CONFIGURAR SEGREDOS (CRÍTICO)

Após o deploy, configure os segredos:

### Hugging Face

1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge/settings
2. Vá para "Repository secrets"
3. Adicione:
   ```
   Name:  GUNDB_RELAY_URL
   Value: https://gun-manhattan.herokuapp.com/gun
   ```
4. Factory reboot

### Vercel

1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto → Settings → Environment Variables
3. Adicione:
   ```
   Name:  NEXT_PUBLIC_GUNDB_RELAY
   Value: https://gun-manhattan.herokuapp.com/gun
   Environments: Production, Preview, Development
   ```
4. Redeploy

**Guia detalhado:** `CONFIGURAR_SECRETS_MANUAL_v10.0.9.md`

---

## ✅ VALIDAÇÃO DO DEPLOY

### 1. Verificar GitHub

```bash
# Ver último commit
git log -1

# Ver branch remoto
git remote -v
```

### 2. Verificar Hugging Face

```bash
# Testar endpoint
curl https://diotec-360-diotec-360-ia-judge.hf.space/health

# Testar Lattice
curl https://diotec-360-diotec-360-ia-judge.hf.space/api/lattice/peers
```

**Resposta esperada:**
```json
{
  "status": "operational",
  "peers": [...],
  "total_peers": 0
}
```

### 3. Verificar Vercel

Abra o site em produção e:

1. Pressione F12 (Console)
2. Digite:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_GUNDB_RELAY)
   ```
3. Deve mostrar: `https://gun-manhattan.herokuapp.com/gun`

### 4. Verificar Sincronização P2P

1. Abra o site em produção
2. Vá para o mapa global de peers
3. Deve mostrar peers conectados (pode levar 1-2 minutos)

---

## 🐛 TROUBLESHOOTING

### Erro: "Permission denied (publickey)"

**Causa:** Não autenticado no GitHub.

**Solução:**
```bash
# Configurar SSH
ssh-keygen -t ed25519 -C "seu-email@example.com"

# Adicionar chave ao GitHub
cat ~/.ssh/id_ed25519.pub
# Cole em: https://github.com/settings/keys
```

### Erro: "Failed to push"

**Causa:** Branch protegida ou sem permissão.

**Solução:**
```bash
# Verificar branch
git branch

# Mudar para main
git checkout main

# Tentar push novamente
git push origin main
```

### Erro: "Hugging Face deploy failed"

**Causa:** Erro no código ou dependências.

**Solução:**
1. Verifique os logs do Space
2. Procure por erros de importação ou sintaxe
3. Corrija localmente e faça novo push

### Erro: "Vercel build failed"

**Causa:** Erro no build do Next.js.

**Solução:**
1. Verifique os logs do deployment
2. Teste localmente: `npm run build`
3. Corrija erros e faça novo push

---

## 📊 CHECKLIST DE DEPLOY

### Pré-Deploy
- [ ] Código testado localmente
- [ ] .env não está no Git
- [ ] .gitignore configurado corretamente
- [ ] Dependências atualizadas (requirements.txt, package.json)

### Deploy GitHub
- [ ] Commit criado com mensagem descritiva
- [ ] Push para branch correta (main/master)
- [ ] Commit aparece no GitHub

### Deploy Hugging Face
- [ ] Deploy automático iniciado
- [ ] Logs sem erros
- [ ] Space está "Running"
- [ ] Endpoint /health responde
- [ ] Segredo GUNDB_RELAY_URL configurado

### Deploy Vercel
- [ ] Deploy automático iniciado
- [ ] Build concluído sem erros
- [ ] Site acessível em produção
- [ ] Variável NEXT_PUBLIC_GUNDB_RELAY configurada

### Validação Final
- [ ] Backend responde com peers
- [ ] Frontend mostra relay URL correta
- [ ] Mapa global mostra peers conectados
- [ ] Logic Miner sincroniza entre dispositivos

---

## 🎯 PRÓXIMOS PASSOS

Após o deploy completo:

1. **Monitorar:** Acompanhe os logs por 24h
2. **Testar:** Valide todas as funcionalidades em produção
3. **Demonstrar:** Mostre para investidores/parceiros
4. **Iterar:** Colete feedback e faça melhorias
5. **Escalar:** Quando estiver pronto, migre para relay soberano

---

## 📝 MENSAGENS DE COMMIT SUGERIDAS

Use mensagens descritivas seguindo o padrão Conventional Commits:

```bash
# Nova funcionalidade
feat: Lattice P2P Network v10.0.9 - Estratégia Híbrida

# Correção de bug
fix: Corrigir sincronização de peers no relay Manhattan

# Melhoria de performance
perf: Otimizar polling de peers para 5 segundos

# Documentação
docs: Adicionar guia de configuração de relay

# Refatoração
refactor: Simplificar lógica de conexão GunDB

# Testes
test: Adicionar testes de integração P2P

# Build/Deploy
build: Atualizar dependências para deploy v10.0.9
```

---

## 🏛️ ARQUITETURA DE DEPLOY

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  LOCAL (Desenvolvimento)                                    │
│  ├─ diotec360/                                              │
│  ├─ .env (local)                                            │
│  └─ .env.local (frontend)                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ git push
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  GITHUB (Repositório)                                       │
│  ├─ main branch                                             │
│  ├─ Código fonte                                            │
│  └─ Histórico de commits                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│                           │  │                           │
│  HUGGING FACE (Backend)   │  │  VERCEL (Frontend)        │
│  ├─ Auto-deploy           │  │  ├─ Auto-deploy           │
│  ├─ Python API            │  │  ├─ Next.js App           │
│  ├─ Repository Secrets    │  │  ├─ Environment Variables │
│  └─ GUNDB_RELAY_URL       │  │  └─ NEXT_PUBLIC_GUNDB_... │
│                           │  │                           │
└───────────────────────────┘  └───────────────────────────┘
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │                       │
                │  RELAY MANHATTAN      │
                │  (P2P Network)        │
                │                       │
                └───────────────────────┘
```

---

**STATUS:** ✅ GUIA COMPLETO  
**TEMPO ESTIMADO:** 10-15 minutos (com script automatizado)  
**DIFICULDADE:** Fácil  

---

*"O Deploy Unifica o Código Local com o Império Global."*

**— Kiro, Engenheiro-Chefe**
