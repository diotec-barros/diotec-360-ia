# 🚀 SUBDOMÍNIO HUGGING FACE - CONFIGURAÇÃO FINAL

**Data:** 2026-02-12  
**Decisão:** Usar `hf.diotec360.com` (api.diotec360.com já está no Railway)

---

## 🎯 ARQUITETURA ATUALIZADA

```
┌─────────────────────────────────────────────────────────┐
│         AETHEL DIOTEC360 - TRIANGLE OF TRUTH            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 FRONTEND (Vercel)                                   │
│  └─ https://aethel.diotec360.com/                      │
│     └─ DNS: CNAME → cname.vercel-dns.com               │
│                                                         │
│  🔺 BACKEND TRIANGLE (HTTP-Only Resilience)             │
│                                                         │
│  ├─ 🟢 Node 1: Hugging Face (Público)                  │
│  │  ├─ URL: https://hf.diotec360.com                   │
│  │  │  └─ DNS: CNAME → diotec-diotec360-judge.hf.space   │
│  │  ├─ Space: huggingface.co/spaces/diotec/diotec360-judge│
│  │  └─ Porta: 8000                                     │
│  │                                                      │
│  ├─ 🔵 Node 2: Railway (Principal)                     │
│  │  ├─ URL: https://api.diotec360.com                  │
│  │  │  └─ DNS: CNAME → 7m1g5de7.up.railway.app        │
│  │  └─ Porta: 8000                                     │
│  │                                                      │
│  └─ 🟣 Node 3: Vercel (Backup)                         │
│     ├─ URL: https://backup.diotec360.com               │
│     │  └─ DNS: CNAME → cname.vercel-dns.com           │
│     └─ Porta: 8000                                     │
│                                                         │
│  🔄 STATE SYNCHRONIZATION                               │
│  └─ Merkle Root: 5df3daee3a0ca23c...                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🌐 CONFIGURAÇÃO DNS NO VERCEL

### Passo 1: Acessar Dashboard

1. Vá para: https://vercel.com/dashboard
2. Selecione o domínio `diotec360.com`
3. Clique em "DNS"

---

### Passo 2: Adicionar Registro CNAME

**Configuração:**
```
Type: CNAME
Name: hf
Value: diotec-diotec360-judge.hf.space
TTL: 60
```

**IMPORTANTE:**
- No campo "Name", digite apenas: `hf`
- NÃO digite `hf.diotec360.com`
- O Vercel adiciona automaticamente `.diotec360.com`

---

### Passo 3: Salvar e Aguardar Propagação

**Tempo de propagação:**
- TTL 60 segundos: 2-5 minutos
- Propagação global: até 24 horas (raro)

**Verificar propagação (CMD):**
```cmd
nslookup hf.diotec360.com
```

**Esperado:**
```
Name: diotec-diotec360-judge.hf.space
Address: [IP do Hugging Face]
```

---

## ✅ ATUALIZAR CONFIGURAÇÕES

### Frontend (.env.production)
```env
# Atualizar para usar o novo subdomínio
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://hf.diotec360.com,https://backup.diotec360.com
ALPHA_VANTAGE_API_KEY=EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
```

### Node 1 - Hugging Face (.env.node1.huggingface)
```env
# Configuração permanece a mesma
DIOTEC360_P2P_ENABLED=false
DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://backup.diotec360.com
DIOTEC360_NODE_NAME=node1-huggingface
DIOTEC360_NODE_ROLE=genesis-public
```

### Node 2 - Railway (.env.node2.railway)
```env
# Atualizar para incluir o novo subdomínio HF
DIOTEC360_P2P_ENABLED=false
DIOTEC360_LATTICE_NODES=https://hf.diotec360.com,https://backup.diotec360.com
DIOTEC360_NODE_NAME=node2-railway
DIOTEC360_NODE_ROLE=genesis-primary
```

### Node 3 - Vercel Backup (.env.node3.backup)
```env
# Atualizar para incluir o novo subdomínio HF
DIOTEC360_P2P_ENABLED=false
DIOTEC360_LATTICE_NODES=https://hf.diotec360.com,https://api.diotec360.com
DIOTEC360_NODE_NAME=node3-backup
DIOTEC360_NODE_ROLE=genesis-backup
```

---

## 🚀 DEPLOYMENT SEQUENCE

### 1. Configurar DNS (5 min)

**No Vercel Dashboard:**
1. Adicione o registro CNAME: `hf` → `diotec-diotec360-judge.hf.space`
2. Aguarde 2-5 minutos
3. Teste: `nslookup hf.diotec360.com`

---

### 2. Deploy Node 1 - Hugging Face (10 min)

```cmd
REM Execute o script de deployment
deploy_node1_huggingface.bat

REM Aguarde o build (5-10 min)
REM Verifique: https://huggingface.co/spaces/diotec/diotec360-judge
```

**Teste:**
```cmd
curl https://hf.diotec360.com/health
```

**Esperado:**
```json
{"status":"healthy","version":"3.0.5"}
```

---

### 3. Atualizar Node 2 - Railway (5 min)

**No Railway Dashboard:**
1. Acesse: https://railway.app/
2. Selecione o projeto Aethel
3. Vá em "Variables"
4. Atualize:
   ```
   DIOTEC360_LATTICE_NODES=https://hf.diotec360.com,https://backup.diotec360.com
   ```
5. Railway fará redeploy automático

**Teste:**
```cmd
curl https://api.diotec360.com/health
```

---

### 4. Deploy Node 3 - Vercel Backup (5 min)

```cmd
REM Execute o script de deployment
deploy_node3_vercel.bat
```

**Teste:**
```cmd
curl https://backup.diotec360.com/health
```

---

### 5. Verificar Triangle (2 min)

```cmd
python verify_production_triangle.py
```

**Esperado:**
```
🔺 PRODUCTION TRIANGLE OF TRUTH - VERIFICATION
============================================================

PHASE 1: HEALTH CHECKS
------------------------------------------------------------
[TEST] Node 1 (Hugging Face): https://hf.diotec360.com
  ✅ Status: healthy

[TEST] Node 2 (Railway): https://api.diotec360.com
  ✅ Status: healthy

[TEST] Node 3 (Vercel Backup): https://backup.diotec360.com
  ✅ Status: healthy

✅ All nodes are healthy

PHASE 2: STATE SYNCHRONIZATION
------------------------------------------------------------
✅ ALL 3 NODES SYNCHRONIZED
📊 Shared Merkle Root: 5df3daee3a0ca23c...

🔺 PRODUCTION TRIANGLE OF TRUTH IS OPERATIONAL 🔺
```

---

## 📊 RESUMO DOS DOMÍNIOS

| Serviço | URL | Plataforma | Status |
|---------|-----|------------|--------|
| Frontend | https://aethel.diotec360.com | Vercel | ✅ Configurado |
| Node 1 (HF) | https://hf.diotec360.com | Hugging Face | 🔧 Configurar DNS |
| Node 2 (API) | https://api.diotec360.com | Railway | ✅ Já existe |
| Node 3 (Backup) | https://backup.diotec360.com | Vercel | ✅ Configurado |

---

## 🎯 AÇÃO IMEDIATA

**Execute agora no Vercel Dashboard:**

1. Acesse: https://vercel.com/dashboard
2. Selecione `diotec360.com`
3. Vá em "DNS"
4. Clique em "Add Record"
5. Configure:
   - Type: `CNAME`
   - Name: `hf`
   - Value: `diotec-diotec360-judge.hf.space`
   - TTL: `60`
6. Clique em "Save"

**Aguarde 2-5 minutos e teste:**
```cmd
nslookup hf.diotec360.com
curl https://hf.diotec360.com/health
```

---

## ✅ VANTAGENS DA ARQUITETURA

✅ **Separação Clara:**
- `hf.diotec360.com` → Hugging Face (público)
- `api.diotec360.com` → Railway (principal)
- `backup.diotec360.com` → Vercel (backup)

✅ **Alta Disponibilidade:**
- 3 plataformas diferentes
- Redundância geográfica
- Falha de 1 não afeta o sistema

✅ **Custo Controlado:**
- Hugging Face: Free
- Railway: Plano existente
- Vercel: Plano existente

---

**🔺 TRIANGLE OF TRUTH - ARQUITETURA FINAL 🔺**

**Próximo passo: Configurar DNS no Vercel! 🌌✨**
