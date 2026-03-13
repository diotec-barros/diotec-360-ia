# 🚀 DEPLOY VERCEL - SOVEREIGN ARCHITECTURE

**Data:** 2026-02-12  
**Epoch:** 3.0.6  
**Objetivo:** Deploy do Frontend no Vercel com Arquitetura Soberana

---

## 🎯 VARIÁVEIS DE AMBIENTE

As seguintes variáveis serão configuradas no Vercel:

```env
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
ALPHA_VANTAGE_API_KEY=EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
```

---

## 📋 PASSO A PASSO

### 1. Acessar Vercel Dashboard

Vá para: https://vercel.com/dashboard

---

### 2. Selecionar o Projeto

Encontre o projeto do frontend Aethel (provavelmente já existe).

---

### 3. Configurar Environment Variables

**Caminho:** Settings → Environment Variables

Adicione as seguintes variáveis:

#### Variável 1: API URL (Sovereign Domain)
```
Name: NEXT_PUBLIC_API_URL
Value: https://api.diotec360.com
Environment: Production
```

#### Variável 2: Lattice Nodes (Triangle Resilience)
```
Name: NEXT_PUBLIC_LATTICE_NODES
Value: https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
Environment: Production
```

#### Variável 3: Alpha Vantage API Key
```
Name: ALPHA_VANTAGE_API_KEY
Value: EFQ0A2ZCKGNHFGTNAQVLOOL9,-1
Environment: Production
```

---

### 4. Fazer Deploy

**Opção A: Deploy via Git Push**
```bash
cd frontend
git add .
git commit -m "feat: Sovereign Architecture - api.diotec360.com"
git push origin main
```

O Vercel detectará automaticamente e fará o deploy.

---

**Opção B: Deploy Manual via CLI**
```bash
cd frontend
vercel --prod
```

---

**Opção C: Redeploy no Dashboard**

1. Vá em: Deployments
2. Clique nos 3 pontos do último deployment
3. Clique em "Redeploy"
4. Selecione "Use existing Build Cache" (opcional)
5. Clique em "Redeploy"

---

## 🔺 ARQUITETURA APÓS DEPLOY

```
┌─────────────────────────────────────────────────────────┐
│      DIOTEC360 TRIANGLE OF TRUTH - SOVEREIGN ARCHITECTURE  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  🌐 FRONTEND (Vercel) ✅ DEPLOYED                       │
│  └─ https://aethel.diotec360.com/                      │
│     └─ Conecta ao Nexo Soberano                        │
│     └─ Variáveis de Ambiente Configuradas              │
│                                                         │
│  🔺 BACKEND TRIANGLE                                    │
│                                                         │
│  ├─ 🟢 Node 1: Hugging Face                            │
│  │  └─ https://diotec-diotec360-judge.hf.space           │
│  │                                                      │
│  ├─ 🔵 Node 2: SOVEREIGN API ⭐                         │
│  │  └─ https://api.diotec360.com                       │
│  │     └─ NEXO CENTRAL                                 │
│  │                                                      │
│  └─ 🟣 Node 3: Vercel Backup                           │
│     └─ https://backup.diotec360.com                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 TESTAR APÓS DEPLOY

### 1. Acessar Frontend
```
https://aethel.diotec360.com/
```

### 2. Verificar Console do Navegador

Abra DevTools (F12) e verifique:
- ✅ Conexão com `api.diotec360.com`
- ✅ Fallback para `diotec-diotec360-judge.hf.space`
- ✅ Fallback para `backup.diotec360.com`

### 3. Testar Funcionalidades

- ✅ Carregar exemplos
- ✅ Executar provas
- ✅ Verificar sincronização do Triangle

---

## 📊 CONFIGURAÇÃO DNS NECESSÁRIA

Certifique-se de que o domínio está configurado no Vercel:

**Domínio:** `aethel.diotec360.com`

**Configuração:**
1. Vá em: Settings → Domains
2. Adicione: `aethel.diotec360.com`
3. Vercel fornecerá o CNAME
4. Configure no seu provedor DNS (já está configurado ✅)

---

## 🔒 SEGURANÇA

**Variáveis Públicas:**
- `NEXT_PUBLIC_API_URL` - Exposta no cliente (OK)
- `NEXT_PUBLIC_LATTICE_NODES` - Exposta no cliente (OK)

**Variáveis Privadas:**
- `ALPHA_VANTAGE_API_KEY` - Não exposta (OK)

**Nota:** Variáveis com prefixo `NEXT_PUBLIC_` são expostas no bundle do cliente. Isso é intencional para que o frontend possa se conectar aos nós do Triangle.

---

## 🎯 CHECKLIST DE DEPLOY

- [ ] Acessar Vercel Dashboard
- [ ] Ir em Settings → Environment Variables
- [ ] Adicionar `NEXT_PUBLIC_API_URL`
- [ ] Adicionar `NEXT_PUBLIC_LATTICE_NODES`
- [ ] Adicionar `ALPHA_VANTAGE_API_KEY`
- [ ] Fazer deploy (Git push ou Redeploy)
- [ ] Aguardar build (2-5 minutos)
- [ ] Acessar `https://aethel.diotec360.com/`
- [ ] Verificar conexão com `api.diotec360.com`
- [ ] Testar funcionalidades
- [ ] Confirmar Triangle operacional ✅

---

## 💡 DICAS

### Build Time

O build do Next.js leva aproximadamente 2-5 minutos.

### Cache

Se você fizer mudanças nas variáveis de ambiente, precisa fazer um novo deploy para que elas sejam aplicadas.

### Logs

Para ver os logs do build:
1. Vá em: Deployments
2. Clique no deployment
3. Veja a aba "Building"

### Rollback

Se algo der errado, você pode fazer rollback:
1. Vá em: Deployments
2. Encontre um deployment anterior que funcionava
3. Clique nos 3 pontos
4. Clique em "Promote to Production"

---

## 🏛️ BRANDED INTEGRITY

Após o deploy, o frontend estará conectado ao seu território soberano:

**Mensagem ao Mercado:**
> "Acesse **aethel.diotec360.com** para conectar-se à nossa infraestrutura principal em **api.diotec360.com**, com rede de prova distribuída em nexos globais."

---

## 🚀 COMANDO RÁPIDO

Se você já tem o Vercel CLI instalado:

```bash
cd frontend
vercel --prod
```

Isso fará o deploy automaticamente usando as variáveis de ambiente já configuradas no dashboard.

---

## 📞 SUPORTE

Se tiver problemas:

1. Verifique os logs do build no Vercel
2. Confirme que as variáveis de ambiente estão corretas
3. Teste localmente primeiro: `npm run build && npm start`
4. Verifique se o domínio está configurado corretamente

---

**🚀 PRONTO PARA DEPLOY! 🚀**

**Execute agora e o Frontend estará conectado à Arquitetura Soberana!**

**🏛️⚖️🛡️✨**
