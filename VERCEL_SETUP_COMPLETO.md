# Setup Vercel - DIOTEC 360 ✅

## Status Atual

✅ **Vercel CLI instalado**  
✅ **Autenticação realizada**  
✅ **DNS configurado**
- api.diotec360.com → CNAME configurado
- app.diotec360.com → CNAME configurado

## Próximos Passos

### 1. Deploy do Backend API

```powershell
# Na raiz do projeto
vercel --prod
```

Quando solicitado:
- **Set up and deploy**: Yes
- **Which scope**: Selecione sua conta/organização
- **Link to existing project**: No
- **Project name**: diotec360-api
- **Directory**: . (raiz)
- **Override settings**: No

Após o deploy:
```powershell
vercel domains add api.diotec360.com
```

### 2. Deploy do Frontend

```powershell
# Entrar no diretório frontend
cd frontend

# Deploy
vercel --prod
```

Quando solicitado:
- **Set up and deploy**: Yes
- **Which scope**: Selecione sua conta/organização
- **Link to existing project**: No
- **Project name**: diotec360-app
- **Directory**: . (frontend)
- **Override settings**: No

Após o deploy:
```powershell
vercel domains add app.diotec360.com
```

### 3. Configurar Variáveis de Ambiente

#### Backend (api.diotec360.com)

No Vercel Dashboard:
1. Acesse o projeto `diotec360-api`
2. Settings → Environment Variables
3. Adicione:

```
DIOTEC360_ENVIRONMENT=production
DIOTEC360_LOG_LEVEL=INFO
DIOTEC360_P2P_ENABLED=false
DIOTEC360_NODE_NAME=api-production
DIOTEC360_NODE_ROLE=genesis
DIOTEC360_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com
```

#### Frontend (app.diotec360.com)

No Vercel Dashboard:
1. Acesse o projeto `diotec360-app`
2. Settings → Environment Variables
3. Adicione:

```
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com
NEXT_PUBLIC_APP_NAME=DIOTEC 360
NEXT_PUBLIC_APP_VERSION=1.7.0
```

### 4. Redeploy com Variáveis

Após adicionar as variáveis de ambiente, faça redeploy:

```powershell
# Backend
vercel --prod

# Frontend
cd frontend
vercel --prod
```

## Verificação

### Testar Backend

```powershell
# Health check
curl https://api.diotec360.com/

# Resposta esperada:
# {"name":"DIOTEC 360 IA API","version":"1.7.0","status":"operational"}
```

### Testar Frontend

```powershell
# Abrir no navegador
start https://app.diotec360.com
```

## Arquitetura Final

```
DIOTEC 360 Infrastructure
│
├── Backend API
│   ├── URL: https://api.diotec360.com
│   ├── Plataforma: Vercel (Python FastAPI)
│   ├── Projeto: diotec360-api
│   └── Backup: https://diotec-360-diotec-360-ia-judge.hf.space
│
├── Frontend App
│   ├── URL: https://app.diotec360.com
│   ├── Plataforma: Vercel (Next.js)
│   └── Projeto: diotec360-app
│
└── Repositório
    ├── GitHub: https://github.com/diotec-barros/diotec360
    └── Branch: main
```

## Comandos Úteis

### Ver logs em tempo real

```powershell
# Backend
vercel logs diotec360-api --follow

# Frontend
vercel logs diotec360-app --follow
```

### Listar projetos

```powershell
vercel list
```

### Ver domínios

```powershell
vercel domains ls
```

### Remover domínio (se necessário)

```powershell
vercel domains rm api.diotec360.com
vercel domains rm app.diotec360.com
```

## Troubleshooting

### Erro: Domain already in use

**Solução**: O domínio já está associado a outro projeto. Remova-o primeiro:
```powershell
vercel domains rm api.diotec360.com
```

### Erro: Build failed

**Backend**:
- Verifique `requirements.txt`
- Verifique `vercel.json`
- Execute localmente: `python api/main.py`

**Frontend**:
- Verifique `package.json`
- Execute localmente: `npm run build`
- Verifique `frontend/vercel.json`

### Erro: DNS not configured

**Solução**: Aguarde propagação DNS (pode levar até 48h)
```powershell
nslookup api.diotec360.com
nslookup app.diotec360.com
```

## Documentação

- 📘 **Guia Completo**: `VERCEL_SUBDOMINIOS_GUIA.md`
- 🌐 **Configuração DNS**: `DNS_CONFIGURATION.md`
- 🔧 **Script de Setup**: `setup_vercel_domains.ps1`

## Monitoramento

### Vercel Dashboard

- Backend: https://vercel.com/diotec-barros/diotec360-api
- Frontend: https://vercel.com/diotec-barros/diotec360-app

### Status

- Backend API: https://api.diotec360.com/
- Frontend App: https://app.diotec360.com

## Próximas Melhorias

- [ ] Configurar Analytics (Vercel Analytics)
- [ ] Configurar Speed Insights
- [ ] Adicionar domínio docs.diotec360.com (documentação)
- [ ] Configurar Web Vitals monitoring
- [ ] Adicionar testes E2E (Playwright)

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**

**Status**: ✅ Pronto para deploy  
**Data**: 26 de Fevereiro de 2026  
**Versão**: 1.7.0 "Oracle Sanctuary"
