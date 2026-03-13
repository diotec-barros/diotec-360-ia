# 🌐 Configurar Domínio Personalizado - diotec360.com

**Domínio**: diotec360.com  
**Backend**: api.diotec360.com (Railway)  
**Frontend**: aethel.diotec360.com (Vercel)

---

## 🎯 ESTRUTURA RECOMENDADA

```
diotec360.com
├── api.diotec360.com      → Railway (Backend Aethel API)
└── aethel.diotec360.com   → Vercel (Frontend Aethel Studio)
```

**Alternativa**:
```
diotec360.com              → Vercel (Frontend)
└── api.diotec360.com      → Railway (Backend)
```

---

## 📋 PARTE 1: CONFIGURAR BACKEND (Railway)

### 1.1 No Railway Dashboard

1. Acesse seu projeto Aethel no Railway
2. Vá em **"Settings"**
3. Clique em **"Networking"** → **"Custom Domain"**
4. Digite: `api.diotec360.com`
5. Railway vai mostrar um **CNAME** (exemplo: `xxx.up.railway.app`)

### 1.2 No seu Provedor de DNS (onde comprou o domínio)

**Adicione um registro CNAME**:

```
Tipo:    CNAME
Nome:    api
Valor:   [o-cname-que-railway-mostrou].up.railway.app
TTL:     3600 (ou automático)
```

**Exemplo**:
```
CNAME   api   →   aethel-api-production.up.railway.app
```

### 1.3 Aguardar Propagação

- Tempo: 5 minutos a 24 horas (geralmente 15-30 minutos)
- Teste: `curl https://api.diotec360.com/health`

---

## 📋 PARTE 2: CONFIGURAR FRONTEND (Vercel)

### 2.1 No Vercel Dashboard

1. Acesse o projeto "diotec360-lang" no Vercel
2. Vá em **"Settings"** → **"Domains"**
3. Clique em **"Add"**
4. Digite: `aethel.diotec360.com` (ou `diotec360.com`)
5. Vercel vai mostrar registros DNS para adicionar

### 2.2 No seu Provedor de DNS

**Para subdomínio (aethel.diotec360.com)**:

```
Tipo:    CNAME
Nome:    aethel
Valor:   cname.vercel-dns.com
TTL:     3600
```

**Para domínio raiz (diotec360.com)**:

```
Tipo:    A
Nome:    @
Valor:   76.76.21.21
TTL:     3600
```

### 2.3 Atualizar Variável de Ambiente

No Vercel:
1. **Settings** → **Environment Variables**
2. Edite `NEXT_PUBLIC_API_URL`
3. Novo valor: `https://api.diotec360.com`
4. **Save** → **Redeploy**

---

## 📋 PARTE 3: TESTAR TUDO

### 3.1 Testar Backend
```bash
curl https://api.diotec360.com/health
```

**Deve retornar**:
```json
{"status": "healthy"}
```

### 3.2 Testar Frontend
1. Acesse: https://aethel.diotec360.com
2. Carregue um exemplo
3. Clique em "Verify"
4. Deve funcionar!

---

## 🔐 CERTIFICADO SSL (HTTPS)

### Railway
- ✅ **Automático** - Railway gera certificado SSL gratuito
- Tempo: 5-10 minutos após DNS propagar

### Vercel
- ✅ **Automático** - Vercel gera certificado SSL gratuito
- Tempo: Instantâneo após DNS propagar

---

## 📊 RESUMO DOS REGISTROS DNS

No seu provedor de DNS (GoDaddy, Namecheap, Cloudflare, etc.):

```
# Backend (Railway)
CNAME   api      →   [railway-url].up.railway.app

# Frontend (Vercel) - Opção 1: Subdomínio
CNAME   aethel   →   cname.vercel-dns.com

# Frontend (Vercel) - Opção 2: Domínio raiz
A       @        →   76.76.21.21
```

---

## 🎯 QUAL OPÇÃO ESCOLHER?

### Opção 1: Subdomínio (RECOMENDADO)
```
Frontend: https://aethel.diotec360.com
Backend:  https://api.diotec360.com
```

**Vantagens**:
- Deixa diotec360.com livre para outros projetos
- Mais organizado
- Fácil de lembrar

### Opção 2: Domínio Raiz
```
Frontend: https://diotec360.com
Backend:  https://api.diotec360.com
```

**Vantagens**:
- URL mais curta
- Mais profissional
- Diotec360 é o projeto principal

---

## 🚀 ORDEM DE EXECUÇÃO

1. ✅ **Backend já está no ar** (Railway)
2. 🔄 **Configure DNS para api.diotec360.com** (5-30 min)
3. 🔄 **Configure DNS para aethel.diotec360.com** (5-30 min)
4. 🔄 **Atualize variável no Vercel** (2 min)
5. 🔄 **Redeploy frontend** (2 min)
6. ✅ **Teste tudo!**

---

## 📞 PROVEDORES DE DNS COMUNS

### GoDaddy
1. Meu Painel → Domínios → Gerenciar DNS
2. Adicionar → CNAME/A
3. Salvar

### Namecheap
1. Domain List → Manage → Advanced DNS
2. Add New Record → CNAME/A
3. Save

### Cloudflare
1. DNS → Add Record
2. Type: CNAME/A
3. Save

### Registro.br
1. Painel → DNS → Adicionar Entrada
2. Tipo: CNAME/A
3. Salvar

---

## 🐛 TROUBLESHOOTING

### DNS não propaga
- Aguarde até 24h (geralmente 30 min)
- Teste: `nslookup api.diotec360.com`
- Limpe cache DNS: `ipconfig /flushdns` (Windows)

### SSL não funciona
- Aguarde 10-15 minutos após DNS propagar
- Railway/Vercel geram automaticamente
- Verifique se DNS está correto

### Frontend não conecta com Backend
- Verifique variável `NEXT_PUBLIC_API_URL` no Vercel
- Deve ser: `https://api.diotec360.com`
- Redeploy após mudar

---

## 🎉 RESULTADO FINAL

Quando tudo estiver configurado:

```
✅ https://api.diotec360.com/health
   → {"status": "healthy"}

✅ https://aethel.diotec360.com
   → Aethel Studio funcionando

✅ Certificados SSL automáticos
✅ URLs profissionais
✅ Pronto para produção!
```

---

## 💡 DICA PRO

Adicione também:
```
CNAME   www.aethel   →   cname.vercel-dns.com
```

Para que `www.aethel.diotec360.com` também funcione!

---

**Quer que eu te ajude a configurar? Me diga qual provedor de DNS você usa!**
