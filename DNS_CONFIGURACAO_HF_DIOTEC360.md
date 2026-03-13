# 🌐 CONFIGURAÇÃO DNS - hf.diotec360.com

**Data:** 2026-02-12  
**Subdomínio:** hf.diotec360.com  
**Destino:** Hugging Face Space (diotec-diotec360-judge.hf.space)

---

## ✅ DECISÃO FINAL

**Subdomínio escolhido:** `hf.diotec360.com`

**Motivo:** `api.diotec360.com` já está em uso por outra plataforma backend

---

## 🎯 AÇÃO IMEDIATA - CONFIGURAR DNS NO VERCEL

### Passo 1: Acessar Dashboard do Vercel

1. Acesse: https://vercel.com/dashboard
2. Selecione o domínio `diotec360.com`
3. Clique em "DNS" ou "Domains"

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
- O Vercel adiciona automaticamente o domínio principal

---

### Passo 3: Salvar e Aguardar Propagação

1. Clique em "Save" ou "Add"
2. Aguarde 2-5 minutos para propagação DNS
3. Pode levar até 24 horas para propagação global (raro)

---

## 🧪 TESTAR A CONFIGURAÇÃO

### Teste 1: Verificar DNS

```bash
# Windows (CMD)
nslookup hf.diotec360.com

# Esperado:
# Name: diotec-diotec360-judge.hf.space
# Address: [IP do Hugging Face]
```

---

### Teste 2: Testar API

```bash
# Teste de health check
curl https://hf.diotec360.com/health

# Esperado:
{
  "status": "healthy",
  "version": "3.0.5"
}
```

---

## 📊 ARQUITETURA FINAL - TRIANGLE OF TRUTH

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
│  ├─ 🔵 Node 2: Local Principal                         │
│  │  ├─ URL: https://node2.diotec360.com                │
│  │  │  └─ DNS: A → [IP servidor local]                │
│  │  └─ Porta: 8000                                     │
│  │                                                      │
│  └─ 🟣 Node 3: Local Backup                            │
│     ├─ URL: https://backup.diotec360.com               │
│     │  └─ DNS: A → [IP servidor local]                │
│     └─ Porta: 8000                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 REGISTROS DNS NECESSÁRIOS

### 1. Frontend (Já existe)
```
Type: CNAME
Name: aethel
Value: cname.vercel-dns.com
TTL: 3600
Status: ✅ Configurado
```

### 2. Node 1 - Hugging Face (Criar agora)
```
Type: CNAME
Name: hf
Value: diotec-diotec360-judge.hf.space
TTL: 60
Status: ⏳ Pendente
```

### 3. Node 2 - Local Principal (Criar depois)
```
Type: A
Name: node2
Value: [IP do servidor local]
TTL: 60
Status: ⏳ Aguardando IP
```

### 4. Node 3 - Local Backup (Criar depois)
```
Type: A
Name: backup
Value: [IP do servidor local]
TTL: 60
Status: ⏳ Aguardando IP
```

---

## 🔄 PRÓXIMOS PASSOS

### 1. Configurar DNS (AGORA)
- [ ] Acessar Vercel Dashboard
- [ ] Adicionar registro CNAME para `hf`
- [ ] Aguardar propagação (2-5 min)
- [ ] Testar com `curl https://hf.diotec360.com/health`

### 2. Obter IP do Servidor Local
- [ ] Identificar IP público do servidor local
- [ ] Configurar registros A para `node2` e `backup`

### 3. Deploy Node 1 (Hugging Face)
- [ ] Executar `deploy_node1_huggingface.bat`
- [ ] Aguardar build (5-10 min)
- [ ] Verificar Space online

### 4. Iniciar Nodes Locais
- [ ] Iniciar Node 2 (porta 8000)
- [ ] Iniciar Node 3 (porta 8000)

### 5. Verificar Triangle
- [ ] Executar `python verify_production_triangle.py`
- [ ] Confirmar sincronização dos 3 nós

---

## ✅ VANTAGENS DO SUBDOMÍNIO hf.diotec360.com

✅ **Identificação Clara:**
- Nome indica claramente que é Hugging Face
- Separação de outros serviços (api.diotec360.com)

✅ **Profissionalismo:**
- URL limpa e memorável
- Marca própria (diotec360.com)

✅ **Flexibilidade:**
- Pode mudar backend sem alterar URL
- Fácil de migrar para outro serviço

---

## 🚀 EXECUTE AGORA

**Acesse o Vercel e configure o DNS:**

1. https://vercel.com/dashboard
2. Selecione `diotec360.com`
3. DNS → Add Record
4. Type: `CNAME`, Name: `hf`, Value: `diotec-diotec360-judge.hf.space`
5. Save

**Depois teste:**
```bash
curl https://hf.diotec360.com/health
```

---

**🌐 SUBDOMÍNIO hf.diotec360.com CONFIGURADO 🌐**

**Aguardando confirmação da configuração DNS! 🌌✨**
