# Configuração de Domínios - DIOTEC 360

## Estrutura de Domínios

### Domínio Principal
- **diotec360.com** - Domínio raiz (pode redirecionar para app.diotec360.com)
- **www.diotec360.com** - Alias do domínio principal

### Subdomínios
- **api.diotec360.com** - Backend API (Python FastAPI)
- **app.diotec360.com** - Frontend (Next.js)

## Configuração DNS

### Registros Necessários

```
Tipo    Nome    Valor                           TTL
A       @       76.76.21.21 (Vercel IP)        3600
A       www     76.76.21.21 (Vercel IP)        3600
CNAME   api     cname.vercel-dns.com           3600
CNAME   app     cname.vercel-dns.com           3600
```

**Nota**: O IP do Vercel pode variar. Use `cname.vercel-dns.com` sempre que possível.

## Variáveis de Ambiente

### Backend (.env)

```bash
# Domain Configuration
DIOTEC360_DOMAIN=diotec360.com
DIOTEC360_API_DOMAIN=api.diotec360.com
DIOTEC360_APP_DOMAIN=app.diotec360.com

# CORS Configuration
DIOTEC360_CORS_ORIGINS=https://app.diotec360.com,https://diotec360.com,https://www.diotec360.com

# API Configuration
DIOTEC360_API_URL=https://api.diotec360.com
```

### Frontend (frontend/.env.production)

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=https://api.diotec360.com

# Domain Configuration
NEXT_PUBLIC_DOMAIN=diotec360.com
NEXT_PUBLIC_API_DOMAIN=api.diotec360.com
NEXT_PUBLIC_APP_DOMAIN=app.diotec360.com

# Lattice Nodes (Redundancy)
NEXT_PUBLIC_LATTICE_NODES=https://api.diotec360.com,https://diotec-360-diotec-360-ia-judge.hf.space
```

## Configuração no Vercel

### Projeto Backend (diotec360-api)

**Domínios a adicionar:**
1. `api.diotec360.com` (principal)
2. `diotec360.com` (opcional - pode redirecionar para app)

**Comandos:**
```powershell
vercel domains add api.diotec360.com
vercel domains add diotec360.com
```

**Variáveis de Ambiente:**
```
DIOTEC360_DOMAIN=diotec360.com
DIOTEC360_API_DOMAIN=api.diotec360.com
DIOTEC360_APP_DOMAIN=app.diotec360.com
DIOTEC360_CORS_ORIGINS=https://app.diotec360.com,https://diotec360.com,https://www.diotec360.com
```

### Projeto Frontend (diotec360-app)

**Domínios a adicionar:**
1. `app.diotec360.com` (principal)
2. `www.diotec360.com` (opcional)

**Comandos:**
```powershell
vercel domains add app.diotec360.com
vercel domains add www.diotec360.com
```

**Variáveis de Ambiente:**
```
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_DOMAIN=diotec360.com
NEXT_PUBLIC_API_DOMAIN=api.diotec360.com
NEXT_PUBLIC_APP_DOMAIN=app.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://api.diotec360.com,https://diotec-360-diotec-360-ia-judge.hf.space
ALPHA_VANTAGE_API_KEY=O3TC4CQU6GJWBNVL
```

## Redirecionamentos

### Domínio Principal → App

Configure no Vercel Dashboard (Settings → Domains):

```
diotec360.com → app.diotec360.com (301 redirect)
www.diotec360.com → app.diotec360.com (301 redirect)
```

Ou crie um projeto separado para o domínio raiz com `vercel.json`:

```json
{
  "redirects": [
    {
      "source": "/(.*)",
      "destination": "https://app.diotec360.com/$1",
      "permanent": true
    }
  ]
}
```

## Arquitetura Final

```
diotec360.com (domínio raiz)
│
├── @ (root)                    → Redireciona para app.diotec360.com
├── www.diotec360.com           → Redireciona para app.diotec360.com
│
├── api.diotec360.com           → Backend API (Python FastAPI)
│   ├── Vercel Project: diotec360-api
│   ├── Framework: Python
│   └── Endpoints: /api/*
│
└── app.diotec360.com           → Frontend (Next.js)
    ├── Vercel Project: diotec360-app
    ├── Framework: Next.js
    └── Pages: /, /editor, /vault, etc.
```

## URLs de Acesso

### Produção
- **API**: https://api.diotec360.com
- **App**: https://app.diotec360.com
- **Root**: https://diotec360.com (→ app)
- **WWW**: https://www.diotec360.com (→ app)

### Backup/Redundância
- **Hugging Face**: https://diotec-360-diotec-360-ia-judge.hf.space

### Desenvolvimento
- **API Local**: http://localhost:8000
- **App Local**: http://localhost:3000

## CORS Configuration

O backend aceita requisições de:
- `https://app.diotec360.com`
- `https://diotec360.com`
- `https://www.diotec360.com`

## SSL/TLS

Todos os domínios terão certificados SSL automáticos via Let's Encrypt (gerenciado pelo Vercel).

## Verificação

### Testar DNS
```powershell
nslookup api.diotec360.com
nslookup app.diotec360.com
nslookup diotec360.com
nslookup www.diotec360.com
```

### Testar APIs
```powershell
# Backend
curl https://api.diotec360.com/

# Frontend
curl https://app.diotec360.com/
```

## Troubleshooting

### Erro: CORS blocked

**Solução**: Verifique se o domínio está em `DIOTEC360_CORS_ORIGINS`

### Erro: API URL not found

**Solução**: Verifique `NEXT_PUBLIC_API_URL` no frontend

### Erro: Domain not verified

**Solução**: Aguarde propagação DNS (até 48h)

---

## Arquivos Atualizados

1. ✅ `.env` - Backend com domínios
2. ✅ `vercel.json` - Backend com CORS atualizado
3. ✅ `frontend/.env.local` - Desenvolvimento
4. ✅ `frontend/.env.production` - Produção
5. ✅ `frontend/vercel.json` - Frontend com variáveis

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**

**Data**: 26 de Fevereiro de 2026  
**Versão**: 1.7.0 "Oracle Sanctuary"
