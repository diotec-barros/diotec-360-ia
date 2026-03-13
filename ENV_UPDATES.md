# Atualizações no .env - DIOTEC 360

## Variáveis Atualizadas ✅

### 1. DIOTEC360_LATTICE_NODES
**Antes:**
```
DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
```

**Depois:**
```
DIOTEC360_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com
```

**Motivo:** URL correta do Hugging Face e novo domínio de produção

---

### 2. Storage Directories
**Antes:**
```
DIOTEC360_STATE_DIR=.DIOTEC360_state
DIOTEC360_VAULT_DIR=.DIOTEC360_vault
DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel
```

**Depois:**
```
DIOTEC360_STATE_DIR=.diotec360_state
DIOTEC360_VAULT_DIR=.diotec360_vault
DIOTEC360_SENTINEL_DIR=.diotec360_sentinel
```

**Motivo:** Padronização lowercase (já existem no sistema)

---

### 3. Node Identity
**Antes:**
```
DIOTEC360_NODE_NAME=node2-diotec360
DIOTEC360_NODE_ROLE=genesis-primary
```

**Depois:**
```
DIOTEC360_NODE_NAME=api-production
DIOTEC360_NODE_ROLE=genesis
```

**Motivo:** Nome mais descritivo para produção

---

## Variáveis Adicionadas ✅

### 4. CORS Configuration (NOVA)
```
DIOTEC360_CORS_ORIGINS=https://app.diotec360.com,https://diotec360.com
```

**Motivo:** Permitir requisições do frontend

---

### 5. API Configuration (NOVA)
```
DIOTEC360_API_HOST=0.0.0.0
DIOTEC360_API_PORT=8000
```

**Motivo:** Configuração explícita do servidor

---

### 6. Monitoring (NOVA)
```
DIOTEC360_ENABLE_METRICS=true
DIOTEC360_ENABLE_TELEMETRY=true
```

**Motivo:** Habilitar monitoramento em produção

---

## Variáveis Mantidas ✅

As seguintes variáveis permanecem inalteradas:

```bash
# P2P Configuration
DIOTEC360_P2P_ENABLED=false
DIOTEC360_P2P_LISTEN=/ip4/0.0.0.0/tcp/9000
DIOTEC360_P2P_TOPIC=aethel/lattice/v1
DIOTEC360_P2P_BOOTSTRAP=

# Heartbeat Configuration
DIOTEC360_HEARTBEAT_INTERVAL=5
DIOTEC360_PEERLESS_TIMEOUT=60
DIOTEC360_HTTP_POLL_INTERVAL=10

# Production Settings
DIOTEC360_ENVIRONMENT=production
DIOTEC360_LOG_LEVEL=INFO

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=O3TC4CQU6GJWBNVL
```

---

## Variáveis Opcionais (Para Configurar Depois)

### PayPal (Pagamentos)
```bash
# PAYPAL_CLIENT_ID=
# PAYPAL_CLIENT_SECRET=
# PAYPAL_MODE=sandbox
```

### Database (Se necessário)
```bash
# DIOTEC360_DATABASE_URL=
```

### Redis (Cache)
```bash
# DIOTEC360_REDIS_URL=
```

### Security (Recomendado)
```bash
# DIOTEC360_SECRET_KEY=your-secret-key-here
# DIOTEC360_ALLOWED_HOSTS=api.diotec360.com
```

---

## Configuração no Vercel

No Vercel Dashboard, adicione as seguintes variáveis de ambiente:

### Environment Variables (Settings → Environment Variables)

```
DIOTEC360_ENVIRONMENT=production
DIOTEC360_LOG_LEVEL=INFO
DIOTEC360_P2P_ENABLED=false
DIOTEC360_NODE_NAME=api-production
DIOTEC360_NODE_ROLE=genesis
DIOTEC360_LATTICE_NODES=https://diotec-360-diotec-360-ia-judge.hf.space,https://api.diotec360.com
DIOTEC360_HEARTBEAT_INTERVAL=5
DIOTEC360_HTTP_POLL_INTERVAL=10
DIOTEC360_PEERLESS_TIMEOUT=60
DIOTEC360_CORS_ORIGINS=https://app.diotec360.com,https://diotec360.com
DIOTEC360_API_HOST=0.0.0.0
DIOTEC360_API_PORT=8000
DIOTEC360_ENABLE_METRICS=true
DIOTEC360_ENABLE_TELEMETRY=true
ALPHA_VANTAGE_API_KEY=O3TC4CQU6GJWBNVL
```

**Importante:** Marque todas como "Production" e "Preview" environments.

---

## Arquivos Criados

1. ✅ `.env` - Atualizado com novas variáveis
2. ✅ `.env.production` - Template completo para produção
3. ✅ `ENV_UPDATES.md` - Este documento

---

## Verificação

Após atualizar, verifique se o arquivo `.env` está correto:

```powershell
# Verificar variáveis
Get-Content .env | Select-String "DIOTEC360"
```

---

## Próximos Passos

1. ✅ Variáveis atualizadas no `.env`
2. 🔄 Deploy no Vercel: `vercel --prod`
3. 🔄 Adicionar variáveis no Vercel Dashboard
4. 🔄 Testar API: `curl https://api.diotec360.com/`

---

**Desenvolvido por Kiro para Dionísio Sebastião Barros**  
**DIOTEC 360 - The Sovereign AI Infrastructure**
