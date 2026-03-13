# 🔺 NOVA ARQUITETURA SIMPLIFICADA - TRIANGLE OF TRUTH

**Data:** 2026-02-12  
**Status:** ARQUITETURA REDEFINIDA

---

## 🎯 DECISÃO: REMOVER RAILWAY

**Removido:**
- ❌ `api.diotec360.com` → Railway (Node 2)

**Nova Configuração:**
- Todos os 3 nós rodando na porta 8000
- Criar subdomínio para Hugging Face

---

## 🔺 NOVA ARQUITETURA - 3 NODES

```
┌─────────────────────────────────────────────────────────┐
│         AETHEL DIOTEC360 - SIMPLIFIED STACK             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 FRONTEND (Vercel)                                   │
│  └─ https://aethel.diotec360.com/                      │
│     └─ DNS: CNAME → cname.vercel-dns.com               │
│                                                         │
│  🔺 BACKEND TRIANGLE (HTTP-Only Resilience)             │
│                                                         │
│  ├─ 🟢 Node 1: Hugging Face (Público)                  │
│  │  ├─ URL: https://api.diotec360.com                  │
│  │  │  └─ DNS: CNAME → diotec-diotec360-judge.hf.space   │
│  │  ├─ Space: huggingface.co/spaces/diotec/diotec360-judge│
│  │  └─ Porta: 8000                                     │
│  │                                                      │
│  ├─ 🔵 Node 2: Vercel Serverless (Principal)           │
│  │  ├─ URL: https://node2.diotec360.com                │
│  │  │  └─ DNS: CNAME → cname.vercel-dns.com           │
│  │  └─ Porta: 8000 (serverless)                        │
│  │                                                      │
│  └─ 🟣 Node 3: Vercel Serverless (Backup)              │
│     ├─ URL: https://backup.diotec360.com               │
│     │  └─ DNS: CNAME → cname.vercel-dns.com            │
│     └─ Porta: 8000 (serverless)                        │
│                                                         │
│  🔄 STATE SYNCHRONIZATION                               │
│  └─ Target Merkle Root: 5df3daee3a0ca23c...            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 NOVOS SUBDOMÍNIOS NECESSÁRIOS

### 1. api.diotec360.com → Hugging Face
```
Type: CNAME
Name: api
Value: diotec-diotec360-judge.hf.space
TTL: 60
```

**Função:** Proxy para Hugging Face Space (Node 1)

---

### 2. node2.diotec360.com → Vercel (Novo)
```
Type: CNAME
Name: node2
Value: cname.vercel-dns.com
TTL: 60
```

**Função:** Node 2 principal no Vercel

---

### 3. backup.diotec360.com → Vercel (Já existe)
```
Type: CNAME
Name: backup
Value: cname.vercel-dns.com
TTL: 60
```

**Função:** Node 3 backup no Vercel

---

## ✅ CONFIGURAÇÃO DNS ATUALIZADA

| Nome | Tipo | Valor | TTL | Função |
|------|------|-------|-----|--------|
| `api` | CNAME | `diotec-diotec360-judge.hf.space` | 60 | Node 1 (HF) |
| `node2` | CNAME | `cname.vercel-dns.com` | 60 | Node 2 (Vercel) |
| `backup` | CNAME | `cname.vercel-dns.com` | 60 | Node 3 (Vercel) |
| `aethel` | CNAME | `cname.vercel-dns.com` | 3600 | Frontend |

---

## 🚀 PRÓXIMOS PASSOS

### 1. Configurar DNS no Vercel

**Adicionar 2 novos registros:**

```
1. api.diotec360.com → diotec-diotec360-judge.hf.space
2. node2.diotec360.com → cname.vercel-dns.com
```

**No dashboard do Vercel:**
1. Acesse: https://vercel.com/dashboard
2. Vá em "Domains" do projeto diotec360.com
3. Clique em "Add"
4. Adicione os 2 novos subdomínios

---

### 2. Deploy Node 1 (Hugging Face)

```bash
# Execute o script
deploy_node1_huggingface.bat

# Aguarde build (5-10 min)
# Verifique: https://huggingface.co/spaces/diotec/diotec360-judge
```

---

### 3. Deploy Node 2 (Vercel)

```bash
# Execute o script
deploy_node3_vercel.bat

# Configure domínio no Vercel: node2.diotec360.com
```

---

### 4. Deploy Node 3 (Vercel)

```bash
# Execute o script
deploy_node3_vercel.bat

# Configure domínio no Vercel: backup.diotec360.com
```

---

### 5. Verificar Triangle

```bash
python verify_production_triangle.py
```

---

## 📊 VANTAGENS DA NOVA ARQUITETURA

✅ **Simplicidade:**
- Todos os nós na porta 8000
- Sem Railway (menos complexidade)
- Apenas Vercel + Hugging Face

✅ **Custo:**
- Vercel: Free tier (serverless)
- Hugging Face: Free tier
- Railway: Removido (economia)

✅ **Manutenção:**
- Menos plataformas para gerenciar
- Configuração unificada
- Deploy mais simples

✅ **Escalabilidade:**
- Vercel serverless auto-scale
- Hugging Face auto-scale
- Sem limites de servidor

---

## 🎯 AÇÃO IMEDIATA

**Execute agora no dashboard do Vercel:**

1. Adicione o registro DNS:
   - Nome: `api`
   - Tipo: CNAME
   - Valor: `diotec-diotec360-judge.hf.space`
   - TTL: 60

2. Adicione o registro DNS:
   - Nome: `node2`
   - Tipo: CNAME
   - Valor: `cname.vercel-dns.com`
   - TTL: 60

3. Confirme que `backup` já existe

**Depois compartilhe o resultado para prosseguir com os deploys!**

---

**🔺 ARQUITETURA SIMPLIFICADA - PRONTA PARA CONFIGURAR 🔺**

**Aguardando configuração DNS no Vercel! 🌌✨**
