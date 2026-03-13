# Guia de Configuração de Subdomínios - Vercel

## Arquitetura DIOTEC 360

### Subdomínios Planejados

1. **api.diotec360.com** - Backend API (Python FastAPI)
   - Sovereign Judge
   - Formal Verification
   - Vault Management
   
2. **app.diotec360.com** - Frontend (Next.js)
   - Interface do usuário
   - Editor de código Aethel
   - Dashboard

3. **docs.diotec360.com** - Documentação (opcional)
   - API Reference
   - Guias de uso

## Passo 1: Configurar DNS no Provedor de Domínio

### Registros DNS Necessários

Adicione os seguintes registros CNAME no seu provedor de DNS (ex: GoDaddy, Namecheap, Cloudflare):

```
Tipo    Nome    Valor                           TTL
CNAME   api     cname.vercel-dns.com           3600
CNAME   app     cname.vercel-dns.com           3600
CNAME   docs    cname.vercel-dns.com           3600
```

**Nota**: Alguns provedores podem exigir o domínio completo:
```
api.diotec360.com  →  cname.vercel-dns.com
app.diotec360.com  →  cname.vercel-dns.com
```

## Passo 2: Criar Projetos no Vercel

### 2.1 Backend API (api.diotec360.com)

1. Acesse https://vercel.com/new
2. Importe o repositório: `diotec-barros/diotec360`
3. Configure:
   - **Project Name**: `diotec360-api`
   - **Framework Preset**: Other
   - **Root Directory**: `.` (raiz)
   - **Build Command**: (deixe vazio)
   - **Output Directory**: (deixe vazio)

4. Variáveis de Ambiente:
```bash
DIOTEC360_ENVIRONMENT=production
DIOTEC360_LOG_LEVEL=INFO
DIOTEC360_P2P_ENABLED=false
DIOTEC360_NODE_NAME=api-production
DIOTEC360_NODE_ROLE=genesis
```

5. Adicione o domínio customizado:
   - Settings → Domains
   - Adicione: `api.diotec360.com`

### 2.2 Frontend App (app.diotec360.com)

1. Acesse https://vercel.com/new
2. Importe o repositório: `diotec-barros/diotec360`
3. Configure:
   - **Project Name**: `diotec360-app`
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

4. Variáveis de Ambiente:
```bash
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com
NEXT_PUBLIC_APP_NAME=DIOTEC 360
NEXT_PUBLIC_APP_VERSION=1.7.0
```

5. Adicione o domínio customizado:
   - Settings → Domains
   - Adicione: `app.diotec360.com`

## Passo 3: Atualizar Configurações

### 3.1 Atualizar vercel.json (Backend)

Arquivo: `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        {
          "key": "Access-Control-Allow-Origin",
          "value": "https://app.diotec360.com"
        },
        {
          "key": "Access-Control-Allow-Methods",
          "value": "GET, POST, PUT, DELETE, OPTIONS"
        },
        {
          "key": "Access-Control-Allow-Headers",
          "value": "Content-Type, Authorization"
        }
      ]
    }
  ],
  "env": {
    "DIOTEC360_P2P_ENABLED": "false",
    "DIOTEC360_LATTICE_NODES": "https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com",
    "DIOTEC360_NODE_NAME": "api-production",
    "DIOTEC360_NODE_ROLE": "genesis",
    "DIOTEC360_ENVIRONMENT": "production",
    "DIOTEC360_LOG_LEVEL": "INFO"
  }
}
```

### 3.2 Atualizar frontend/vercel.json

Arquivo: `frontend/vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs",
  "installCommand": "npm install",
  "devCommand": "npm run dev",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.diotec360.com",
    "NEXT_PUBLIC_LATTICE_NODES": "https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com",
    "NEXT_PUBLIC_APP_NAME": "DIOTEC 360",
    "NEXT_PUBLIC_APP_VERSION": "1.7.0"
  },
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Content-Security-Policy",
          "value": "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https://api.diotec360.com https://diotec-360-diotec-360-ia-judge.hf.space"
        }
      ]
    }
  ],
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://api.diotec360.com/api/:path*"
    }
  ]
}
```

## Passo 4: Comandos CLI do Vercel

### Instalar Vercel CLI

```powershell
npm install -g vercel
```

### Login

```powershell
vercel login
```

### Deploy Backend

```powershell
# Na raiz do projeto
vercel --prod

# Adicionar domínio
vercel domains add api.diotec360.com --scope=diotec-barros
```

### Deploy Frontend

```powershell
# No diretório frontend
cd frontend
vercel --prod

# Adicionar domínio
vercel domains add app.diotec360.com --scope=diotec-barros
```

## Passo 5: Verificação

### Testar Backend API

```powershell
# Health check
curl https://api.diotec360.com/

# Verificar endpoint
curl https://api.diotec360.com/api/examples
```

### Testar Frontend

```powershell
# Abrir no navegador
start https://app.diotec360.com
```

## Passo 6: Configurar SSL/TLS

O Vercel configura automaticamente certificados SSL via Let's Encrypt. Verifique:

1. Acesse o projeto no Vercel Dashboard
2. Settings → Domains
3. Verifique se o status está "Valid" com ícone de cadeado verde

## Estrutura Final

```
diotec360.com
├── api.diotec360.com     → Backend API (Python FastAPI)
├── app.diotec360.com     → Frontend (Next.js)
└── docs.diotec360.com    → Documentação (opcional)

Backup/Redundância:
├── Hugging Face Space    → https://diotec-360-diotec-360-ia-judge.hf.space
└── GitHub Repository     → https://github.com/diotec-barros/diotec360
```

## Troubleshooting

### Erro: Domain not verified

**Solução**: Aguarde propagação DNS (pode levar até 48h, geralmente 1-2h)

```powershell
# Verificar DNS
nslookup api.diotec360.com
nslookup app.diotec360.com
```

### Erro: Build failed

**Backend**:
- Verifique `requirements.txt`
- Verifique `vercel.json` na raiz

**Frontend**:
- Verifique `package.json`
- Verifique `frontend/vercel.json`
- Execute `npm run build` localmente

### Erro: CORS

Adicione headers CORS no `vercel.json` do backend (já incluído acima)

## Próximos Passos

1. ✅ Configurar DNS
2. ✅ Criar projetos no Vercel
3. ✅ Adicionar domínios customizados
4. ✅ Configurar variáveis de ambiente
5. ✅ Deploy e teste
6. 🔄 Monitorar logs
7. 🔄 Configurar analytics (opcional)

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
