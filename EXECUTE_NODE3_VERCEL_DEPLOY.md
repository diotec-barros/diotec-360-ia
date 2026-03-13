# 🚀 EXECUTAR DEPLOY NODE 3 NO VERCEL - PASSO A PASSO

**Data:** 2026-02-12  
**Status:** PRONTO PARA EXECUTAR  
**Tempo Estimado:** 10-15 minutos

---

## 🎯 OPÇÃO A: DEPLOY NO VERCEL (EXECUTAR AGORA)

### Arquivos Criados ✅

- ✅ `vercel.json` - Configuração do Vercel para backend
- ✅ `requirements-vercel.txt` - Dependências otimizadas
- ✅ `deploy_node3_vercel.bat` - Script de deployment
- ✅ `.env.node3.backup` - Configuração do Node 3

---

## 📋 PASSO 1: PREPARAR VERCEL CLI (2 minutos)

### Instalar Vercel CLI

```bash
npm install -g vercel
```

### Login no Vercel

```bash
vercel login
```

Isso vai abrir o navegador para você fazer login.

---

## 📋 PASSO 2: EXECUTAR DEPLOYMENT (5 minutos)

### Opção 2A: Usar o Script Automático (RECOMENDADO)

```bash
deploy_node3_vercel.bat
```

O script vai:
1. Verificar se Vercel CLI está instalado
2. Copiar configurações
3. Fazer o deploy
4. Mostrar próximos passos

### Opção 2B: Deploy Manual

```bash
# Copiar environment
copy .env.node3.backup .env

# Deploy
vercel --prod
```

**Quando o Vercel perguntar:**

```
? Set up and deploy "~/aethel"? [Y/n] Y
? Which scope do you want to deploy to? [Seu username]
? Link to existing project? [y/N] N
? What's your project's name? aethel-backup
? In which directory is your code located? ./
? Want to override the settings? [y/N] N
```

---

## 📋 PASSO 3: CONFIGURAR DOMÍNIO (5 minutos)

### 3.1 Ir para o Dashboard do Vercel

1. Abrir: https://vercel.com/dashboard
2. Clicar no projeto `aethel-backup`
3. Ir para **Settings** → **Domains**

### 3.2 Adicionar Domínio Customizado

1. Clicar em **Add Domain**
2. Digitar: `backup.diotec360.com`
3. Clicar em **Add**

### 3.3 Configurar DNS

O Vercel vai mostrar as instruções. Você tem 2 opções:

**Opção A: CNAME (Recomendado)**
```
Type: CNAME
Name: backup
Value: cname.vercel-dns.com
TTL: 3600
```

**Opção B: A Record**
```
Type: A
Name: backup
Value: 76.76.21.21
TTL: 3600
```

### 3.4 Adicionar DNS no Painel Vercel

Se o domínio `diotec360.com` já está no Vercel:

1. Ir para **Domains** no dashboard
2. Clicar em `diotec360.com`
3. Clicar em **DNS Records**
4. Adicionar o registro CNAME ou A acima

---

## 📋 PASSO 4: AGUARDAR PROPAGAÇÃO (2-5 minutos)

```bash
# Verificar DNS
nslookup backup.diotec360.com

# Ou usar online
# https://dnschecker.org
```

Aguarde até ver o IP correto ou o CNAME apontando para Vercel.

---

## 📋 PASSO 5: VERIFICAR DEPLOYMENT (2 minutos)

### Teste 1: Health Check

```bash
curl https://backup.diotec360.com/health
```

**Esperado:**
```json
{"status":"healthy","version":"3.0.5"}
```

### Teste 2: Estado do Lattice

```bash
curl https://backup.diotec360.com/api/lattice/state
```

**Esperado:**
```json
{
  "merkle_root": "5df3daee3a0ca23c...",
  "entry_count": 7,
  ...
}
```

### Teste 3: Verificar Triangle Completo

```bash
python verify_production_triangle.py
```

**Esperado:**
```
🔺 PRODUCTION TRIANGLE OF TRUTH - VERIFICATION
============================================================

[TEST] Node 1 (Hugging Face): https://diotec-diotec360-judge.hf.space
  ✅ Status: healthy

[TEST] Node 2 (diotec360): https://aethel.diotec360.com
  ✅ Status: healthy

[TEST] Node 3 (Backup): https://backup.diotec360.com
  ✅ Status: healthy

✅ ALL NODES SYNCHRONIZED
📊 Shared Merkle Root: 5df3daee3a0ca23c...

🔺 PRODUCTION TRIANGLE OF TRUTH IS OPERATIONAL 🔺
```

---

## ✅ CHECKLIST DE SUCESSO

### Deployment
- [ ] Vercel CLI instalado
- [ ] Login no Vercel feito
- [ ] Deploy executado com sucesso
- [ ] URL do Vercel funcionando

### Domínio
- [ ] Domínio customizado adicionado
- [ ] DNS configurado
- [ ] DNS propagado
- [ ] HTTPS funcionando

### Verificação
- [ ] `/health` retorna healthy
- [ ] `/api/lattice/state` retorna estado
- [ ] Merkle Root sincronizado com outros nodes
- [ ] Triangle verification passa

---

## 🚨 TROUBLESHOOTING

### Erro: "Vercel CLI not found"

```bash
# Instalar globalmente
npm install -g vercel

# Verificar instalação
vercel --version
```

### Erro: "Build failed"

Verifique se `requirements-vercel.txt` existe e tem as dependências corretas.

### Erro: "Domain not verified"

1. Aguarde 5-10 minutos para propagação DNS
2. Verifique se o registro DNS está correto
3. Use `nslookup backup.diotec360.com` para verificar

### Erro: "502 Bad Gateway"

1. Verifique logs no Vercel Dashboard
2. Verifique se as variáveis de ambiente estão configuradas
3. Tente fazer redeploy: `vercel --prod --force`

---

## 🔄 OPÇÃO B: FALLBACK (SE VERCEL NÃO FUNCIONAR)

Se o Vercel tiver problemas com o backend (limitações serverless), use um servidor tradicional:

### Railway (Recomendado)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Criar projeto
railway init

# Deploy
railway up

# Adicionar domínio
railway domain
```

### Render

1. Ir para https://render.com
2. Clicar "New +" → "Web Service"
3. Conectar repositório
4. Configurar:
   - Name: aethel-backup
   - Environment: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Adicionar variáveis de ambiente do `.env.node3.backup`
6. Deploy

---

## 📊 PRÓXIMOS PASSOS APÓS SUCESSO

### 1. Commit & Push

```bash
git add .
git commit -m "feat: Deploy Node 3 backup on Vercel"
git push origin main
```

### 2. Monitorar

```bash
# Criar script de monitoramento
cat > monitor_triangle.bat << 'EOF'
@echo off
echo === TRIANGLE MONITORING ===
echo Timestamp: %date% %time%
echo.

curl -s https://diotec-diotec360-judge.hf.space/health
curl -s https://aethel.diotec360.com/health
curl -s https://backup.diotec360.com/health

echo.
python verify_production_triangle.py
EOF
```

### 3. Deploy Nodes 1 e 2

Agora que Node 3 está funcionando, você pode fazer deploy dos outros:

```bash
# Node 1 (Hugging Face)
deploy_node1_huggingface.bat

# Node 2 (diotec360.com)
./deploy_node2_diotec360.sh
```

---

## 🎯 COMANDOS RÁPIDOS

```bash
# Deploy completo
deploy_node3_vercel.bat

# Verificar
curl https://backup.diotec360.com/health
python verify_production_triangle.py

# Logs
vercel logs aethel-backup --prod

# Redeploy
vercel --prod --force
```

---

## 📞 SUPORTE

### Vercel Dashboard
https://vercel.com/dashboard

### Vercel Docs
https://vercel.com/docs

### Logs em Tempo Real
```bash
vercel logs aethel-backup --prod --follow
```

---

**🔺 PRONTO PARA EXECUTAR! 🔺**

**Execute agora:**
```bash
deploy_node3_vercel.bat
```

**Depois configure o domínio no dashboard do Vercel e verifique! 🌌✨**
