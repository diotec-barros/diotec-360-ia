# 🚀 DEPLOY NODE 3 (BACKUP) NO VERCEL

**Data:** 2026-02-12  
**Objetivo:** Criar backup.diotec360.com no Vercel  
**Estratégia:** Opção A (Vercel Serverless) + Opção B (Fallback)

---

## 🎯 OPÇÃO A: DEPLOY NO VERCEL (RECOMENDADO)

### Por que Vercel para Node 3?
- ✅ Mesma infraestrutura do frontend
- ✅ Deploy automático via Git
- ✅ SSL grátis
- ✅ CDN global
- ✅ Fácil configuração de subdomínio

---

## 📋 PASSO A PASSO - OPÇÃO A

### 1. Preparar Projeto Backend para Vercel

Vamos criar uma configuração específica para o backend no Vercel:

```bash
# Criar diretório para backend
mkdir backend-node3
cd backend-node3

# Copiar arquivos necessários
cp -r ../aethel ./
cp -r ../api ./
cp ../requirements.txt ./
cp ../.env.node3.backup ./.env
```

### 2. Criar `vercel.json` para Backend

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
  "env": {
    "DIOTEC360_P2P_ENABLED": "false",
    "DIOTEC360_LATTICE_NODES": "https://diotec-diotec360-judge.hf.space,https://aethel.diotec360.com",
    "DIOTEC360_NODE_NAME": "node3-backup",
    "DIOTEC360_NODE_ROLE": "genesis-backup",
    "DIOTEC360_HEARTBEAT_INTERVAL": "5",
    "DIOTEC360_HTTP_POLL_INTERVAL": "10",
    "DIOTEC360_PEERLESS_TIMEOUT": "60"
  }
}
```

### 3. Criar `requirements.txt` Otimizado

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

### 4. Adaptar `api/main.py` para Vercel

Adicionar no final do arquivo:

```python
# Vercel handler
app = app  # Vercel procura por 'app'
```

### 5. Deploy no Vercel

#### Via CLI (Recomendado):

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd backend-node3
vercel

# Seguir prompts:
# - Set up and deploy? Yes
# - Which scope? Seu username
# - Link to existing project? No
# - Project name? aethel-backup
# - Directory? ./
# - Override settings? No

# Deploy para produção
vercel --prod
```

#### Via Dashboard:

1. Ir para https://vercel.com/new
2. Clicar "Import Git Repository"
3. Selecionar repositório (ou criar novo para backend)
4. Configurar:
   - **Project Name:** aethel-backup
   - **Framework:** Other
   - **Root Directory:** backend-node3 (ou deixar vazio se for repo separado)
   - **Build Command:** (deixar vazio)
   - **Output Directory:** (deixar vazio)
5. Adicionar Environment Variables (do vercel.json)
6. Clicar "Deploy"

### 6. Configurar Subdomínio no Vercel

Depois do deploy:

1. Ir para projeto → Settings → Domains
2. Clicar "Add Domain"
3. Digitar: `backup.diotec360.com`
4. Vercel vai mostrar instruções DNS

**Configuração DNS no Vercel:**

```
Type: CNAME
Name: backup
Value: cname.vercel-dns.com
TTL: 3600
```

OU (se preferir A record):

```
Type: A
Name: backup
Value: 76.76.21.21
TTL: 3600
```

### 7. Adicionar DNS no Painel Vercel

1. Ir para https://vercel.com/dashboard
2. Clicar em "Domains"
3. Encontrar diotec360.com
4. Clicar "Add"
5. Adicionar subdomínio: backup.diotec360.com
6. Vercel configura automaticamente

### 8. Verificar Deploy

```bash
# Aguardar 2-3 minutos
# Testar
curl https://backup.diotec360.com/health
```

**Esperado:**
```json
{"status":"healthy","version":"1.7.0"}
```

---

## 🔄 OPÇÃO B: FALLBACK (SERVIDOR TRADICIONAL)

Se Vercel não funcionar bem para backend (por limitações serverless), use servidor tradicional:

### 1. Escolher Provedor

Opções recomendadas:
- **Railway** - Fácil, $5/mês
- **Render** - Free tier disponível
- **DigitalOcean** - $6/mês
- **Linode** - $5/mês
- **Seu próprio VPS**

### 2. Deploy no Railway (Exemplo)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Criar projeto
railway init

# Deploy
railway up

# Adicionar domínio
railway domain
# Escolher: Custom Domain
# Digitar: backup.diotec360.com
```

**Configurar DNS:**
```
Type: CNAME
Name: backup
Value: [hostname fornecido pelo Railway]
```

### 3. Deploy no Render (Exemplo)

1. Ir para https://render.com
2. Clicar "New +" → "Web Service"
3. Conectar repositório
4. Configurar:
   - **Name:** aethel-backup
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. Adicionar Environment Variables
6. Deploy

**Configurar DNS:**
```
Type: CNAME
Name: backup
Value: [hostname fornecido pelo Render]
```

---

## 🔧 CONFIGURAÇÃO DNS (AMBAS OPÇÕES)

### No Painel Vercel (Gerenciador DNS)

1. Ir para https://vercel.com/dashboard
2. Clicar em "Domains"
3. Selecionar diotec360.com
4. Clicar "DNS Records"
5. Adicionar novo registro:

**Para Vercel (Opção A):**
```
Type: CNAME
Name: backup
Value: cname.vercel-dns.com
TTL: Auto
```

**Para Servidor Externo (Opção B):**
```
Type: CNAME
Name: backup
Value: [hostname do provedor]
TTL: Auto
```

### Verificar Propagação

```bash
# Verificar DNS
nslookup backup.diotec360.com

# Ou online
# https://dnschecker.org
```

---

## ✅ VERIFICAÇÃO COMPLETA

### Teste 1: Health Check

```bash
curl https://backup.diotec360.com/health
```

### Teste 2: Estado do Lattice

```bash
curl https://backup.diotec360.com/api/lattice/state
```

### Teste 3: Sincronização do Triângulo

```bash
python verify_production_triangle.py
```

**Esperado:**
```
🔺 PRODUCTION TRIANGLE OF TRUTH - VERIFICATION
============================================================

[TEST] Node 1 (Hugging Face): https://diotec-diotec360-judge.hf.space
  ✅ Healthy

[TEST] Node 2 (diotec360): https://aethel.diotec360.com
  ✅ Healthy

[TEST] Node 3 (Backup): https://backup.diotec360.com
  ✅ Healthy

✅ ALL NODES SYNCHRONIZED
📊 Shared Merkle Root: 5df3daee3a0ca23c...

🔺 PRODUCTION TRIANGLE OF TRUTH IS OPERATIONAL 🔺
```

---

## 🎯 QUAL OPÇÃO ESCOLHER?

### Use Opção A (Vercel) se:
- ✅ Quer simplicidade máxima
- ✅ Já usa Vercel para frontend
- ✅ Tráfego moderado (< 100k requests/mês no free tier)
- ✅ Não precisa de estado persistente complexo

### Use Opção B (Servidor) se:
- ✅ Precisa de mais controle
- ✅ Tráfego alto
- ✅ Precisa de estado persistente
- ✅ Quer garantir uptime 24/7

---

## 📊 COMPARAÇÃO

| Aspecto | Opção A (Vercel) | Opção B (Servidor) |
|---------|------------------|-------------------|
| **Custo** | Grátis (até limite) | $5-10/mês |
| **Setup** | 5 minutos | 15 minutos |
| **Manutenção** | Zero | Baixa |
| **Escalabilidade** | Automática | Manual |
| **Controle** | Limitado | Total |
| **SSL** | Automático | Automático |
| **Uptime** | 99.9% | 99.9% |

---

## 🚀 RECOMENDAÇÃO FINAL

**Para Node 3 (Backup), recomendo:**

1. **Começar com Opção A (Vercel)** - Mais rápido e simples
2. **Se tiver problemas**, migrar para Opção B (Railway/Render)
3. **Monitorar por 24 horas** para ver performance
4. **Ajustar conforme necessário**

---

## 📞 PRÓXIMOS PASSOS

### Depois do Deploy:

1. **Verificar Triangle:**
   ```bash
   python verify_production_triangle.py
   ```

2. **Testar Failover:**
   - Parar Node 2
   - Verificar se Node 1 e 3 continuam

3. **Monitorar:**
   - Logs no Vercel Dashboard
   - Performance metrics
   - Sincronização do Merkle Root

4. **Commit & Push:**
   ```bash
   git add .
   git commit -m "feat: Add Node 3 backup on Vercel"
   git push origin main
   ```

---

**🔺 GUIA COMPLETO PARA DEPLOY NO VERCEL 🔺**

**Escolha Opção A primeiro, depois B se necessário! 🌌✨**

