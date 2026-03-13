# 🌐 CONFIGURAR SUBDOMÍNIO PARA HUGGING FACE

**Data:** 2026-02-12  
**Objetivo:** Criar subdomínio personalizado para o Hugging Face Space

---

## 🎯 SUBDOMÍNIO PARA HUGGING FACE

**Space:** https://huggingface.co/spaces/diotec/diotec360-judge  
**URL Atual:** https://diotec-diotec360-judge.hf.space  
**Novo Subdomínio:** https://hf.diotec360.com

---

## 📋 CONFIGURAÇÃO DNS NO VERCEL

### Adicionar Registro CNAME

```
Tipo: CNAME
Nome: hf
Valor: diotec-diotec360-judge.hf.space
TTL: 60
```

**Passo a passo:**

1. Acesse: https://vercel.com/dashboard
2. Selecione o domínio `diotec360.com`
3. Vá em "DNS"
4. Clique em "Add Record"
5. Preencha:
   - Type: `CNAME`
   - Name: `hf`
   - Value: `diotec-diotec360-judge.hf.space`
   - TTL: `60`
6. Clique em "Save"

---

## ✅ RESULTADO

Após a configuração DNS (propagação em 2-5 minutos):

**Antes:**
- https://diotec-diotec360-judge.hf.space

**Depois:**
- https://hf.diotec360.com ✅ (seu domínio personalizado)
- https://diotec-diotec360-judge.hf.space (ainda funciona)

---

## 🔺 ARQUITETURA ATUALIZADA

```
┌─────────────────────────────────────────────────────────┐
│         DIOTEC360 TRIANGLE OF TRUTH - PRODUCTION           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 FRONTEND (Vercel)                                   │
│  └─ https://aethel.diotec360.com/                      │
│                                                         │
│  🔺 BACKEND TRIANGLE (HTTP-Only Resilience)             │
│                                                         │
│  ├─ 🟢 Node 1: Hugging Face                            │
│  │  ├─ URL Personalizada: https://hf.diotec360.com    │
│  │  │  └─ DNS: CNAME → diotec-diotec360-judge.hf.space  │
│  │  └─ URL Original: diotec-diotec360-judge.hf.space    │
│  │                                                      │
│  ├─ 🔵 Node 2: Diotec360 (Principal)                   │
│  │  ├─ URL: https://node2.diotec360.com                │
│  │  └─ Porta: 8000                                     │
│  │                                                      │
│  └─ 🟣 Node 3: Backup (Vercel)                         │
│     ├─ URL: https://backup.diotec360.com               │
│     └─ Porta: 8002                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 TESTAR APÓS CONFIGURAÇÃO

```bash
# Aguarde 2-5 minutos para propagação DNS

# Teste o novo subdomínio
curl https://hf.diotec360.com/health

# Deve retornar
{"status":"healthy","version":"3.0.5"}
```

---

## 📊 CONFIGURAÇÃO DNS COMPLETA

| Nome | Tipo | Valor | TTL | Função |
|------|------|-------|-----|--------|
| `hf` | CNAME | `diotec-diotec360-judge.hf.space` | 60 | Node 1 (HF) |
| `node2` | A | `[IP servidor]` | 60 | Node 2 (Local) |
| `backup` | CNAME | `cname.vercel-dns.com` | 60 | Node 3 (Vercel) |
| `aethel` | CNAME | `cname.vercel-dns.com` | 3600 | Frontend |

---

## 🔄 ATUALIZAR CONFIGURAÇÕES

Após criar o subdomínio, atualize as configurações para usar `hf.diotec360.com`:

### Frontend (.env.production)
```env
NEXT_PUBLIC_API_URL=https://hf.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://node2.diotec360.com,https://backup.diotec360.com
```

### Node 2 e Node 3
```env
DIOTEC360_LATTICE_NODES=https://hf.diotec360.com,...
```

---

## 🎯 AÇÃO IMEDIATA

**Execute agora no dashboard do Vercel:**

1. Vá em: https://vercel.com/dashboard
2. Selecione `diotec360.com`
3. Vá em "DNS"
4. Adicione o registro CNAME:
   - Nome: `hf`
   - Valor: `diotec-diotec360-judge.hf.space`
   - TTL: 60

**Depois compartilhe o resultado!**

---

**🌐 SUBDOMÍNIO PERSONALIZADO PARA HUGGING FACE 🌐**

**Aguardando configuração DNS! 🚀✨**
