# 🌐 CONFIGURAÇÃO DOS DOMÍNIOS DIOTEC360

**Data:** 2026-02-12  
**Status:** CONFIGURADO E PRONTO

---

## 🎯 SEUS DOMÍNIOS

### Frontend
- **URL:** https://aethel.diotec360.com/
- **Plataforma:** Vercel
- **Status:** ✅ Já configurado

### Backend Triangle

#### Node 1 (Hugging Face - Público)
- **URL:** https://diotec-diotec360-judge.hf.space
- **Space:** https://huggingface.co/spaces/diotec/diotec360-judge
- **Função:** Ponto de acesso público
- **Status:** 🚀 Pronto para deploy

#### Node 2 (Railway API - Principal)
- **URL:** https://api.diotec360.com
- **Servidor:** Railway (7m1g5de7.up.railway.app)
- **Função:** Backend primário
- **Status:** 🚀 Pronto para deploy

#### Node 3 (Backup)
- **URL:** https://backup.diotec360.com
- **Servidor:** Servidor de backup
- **Função:** Redundância e failover
- **Status:** 🚀 Pronto para deploy

---

## 📋 ARQUITETURA CONFIGURADA

```
┌─────────────────────────────────────────────────────────┐
│         AETHEL DIOTEC360 - COMPLETE STACK               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  FRONTEND (Vercel)                                      │
│  └─ https://aethel.diotec360.com/                      │
│                                                         │
│  BACKEND TRIANGLE (HTTP-Only Resilience)                │
│  ├─ Node 1: https://diotec-diotec360-judge.hf.space      │
│  ├─ Node 2: https://api.diotec360.com (Railway)       │
│  └─ Node 3: https://backup.diotec360.com (Vercel)     │
│                                                         │
│  STATE SYNCHRONIZATION                                  │
│  └─ Merkle Root: 5df3daee3a0ca23c...                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ CONFIGURAÇÕES ATUALIZADAS

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
```

### Node 1 (Hugging Face)
```env
DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://backup.diotec360.com
DIOTEC360_NODE_NAME=node1-huggingface
DIOTEC360_NODE_ROLE=genesis-public
```

### Node 2 (Railway API)
```env
DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com
DIOTEC360_NODE_NAME=node2-diotec360
DIOTEC360_NODE_ROLE=genesis-primary
```

### Node 3 (Vercel Backup)
```env
DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://api.diotec360.com
DIOTEC360_NODE_NAME=node3-backup
DIOTEC360_NODE_ROLE=genesis-backup
```

---

## 🚀 DEPLOYMENT SEQUENCE

### 1. Deploy Node 1 (Hugging Face) - 10 min

```bash
# Execute o script de deployment
deploy_node1_huggingface.bat

# Aguarde o build no Hugging Face (5-10 min)
# Verifique: https://huggingface.co/spaces/diotec/diotec360-judge

# Teste o endpoint
curl https://diotec-diotec360-judge.hf.space/health
```

**Esperado:**
```json
{"status":"healthy","version":"1.7.0"}
```

---

### 2. Deploy Node 2 (api.diotec360.com - Railway) - 5 min

**Node 2 já está deployed no Railway!**

O DNS `api.diotec360.com` aponta para `7m1g5de7.up.railway.app`.

**Teste:**
```bash
curl https://api.diotec360.com/health
```

**Se precisar atualizar variáveis de ambiente no Railway:**
1. Acesse: https://railway.app/
2. Selecione o projeto Aethel
3. Vá em "Variables"
4. Adicione/atualize:
   - `DIOTEC360_LATTICE_NODES=https://diotec-diotec360-judge.hf.space,https://backup.diotec360.com`
   - `DIOTEC360_NODE_NAME=node2-diotec360`
   - `DIOTEC360_NODE_ROLE=genesis-primary`
   - `DIOTEC360_P2P_ENABLED=false`
5. Railway fará redeploy automático

---

### 3. Deploy Node 3 (backup.diotec360.com - Vercel) - 5 min

**Deploy no Vercel:**
```bash
# Execute o script de deployment
deploy_node3_vercel.bat

# Ou manualmente:
cd [diretório do projeto]
vercel --prod
```

**Configure o domínio no Vercel:**
1. Acesse: https://vercel.com/dashboard
2. Selecione o projeto
3. Vá em "Settings" → "Domains"
4. Adicione: `backup.diotec360.com`
5. Vercel fornecerá o CNAME (já configurado: `cname.vercel-dns.com`)

**Teste:**
```bash
curl https://backup.diotec360.com/health
```

---

### 4. Verificar Triangle - 2 min

```bash
# Execute o script de verificação
python verify_production_triangle.py
```

**Esperado:**
```
🔺 PRODUCTION TRIANGLE OF TRUTH - VERIFICATION
============================================================

PHASE 1: HEALTH CHECKS
------------------------------------------------------------
[TEST] Node 1 (Hugging Face): https://diotec-diotec360-judge.hf.space
  ✅ Status: healthy

[TEST] Node 2 (Railway API): https://api.diotec360.com
  ✅ Status: healthy

[TEST] Node 3 (Backup): https://backup.diotec360.com
  ✅ Status: healthy

✅ All nodes are healthy

PHASE 2: STATE SYNCHRONIZATION
------------------------------------------------------------
✅ ALL NODES SYNCHRONIZED
📊 Shared Merkle Root: 5df3daee3a0ca23c...

🔺 PRODUCTION TRIANGLE OF TRUTH IS OPERATIONAL 🔺
```

---

## 🔧 CONFIGURAÇÃO DNS

### Se precisar configurar DNS:

#### Para aethel.diotec360.com
```
Type: A ou CNAME
Name: aethel
Value: [IP do seu servidor] ou [hostname]
TTL: 3600
```

#### Para backup.diotec360.com
```
Type: A ou CNAME
Name: backup
Value: [IP do servidor backup] ou [hostname]
TTL: 3600
```

---

## 🔐 CONFIGURAÇÃO SSL

### Certbot (Let's Encrypt)

```bash
# Instalar certbot
sudo apt-get install certbot python3-certbot-nginx

# Obter certificado para aethel.diotec360.com
sudo certbot --nginx -d aethel.diotec360.com

# Obter certificado para backup.diotec360.com
sudo certbot --nginx -d backup.diotec360.com

# Renovação automática já está configurada
```

---

## 🌐 CONFIGURAÇÃO NGINX

### Para aethel.diotec360.com

```nginx
# /etc/nginx/sites-available/aethel
server {
    listen 443 ssl http2;
    server_name aethel.diotec360.com;
    
    ssl_certificate /etc/letsencrypt/live/aethel.diotec360.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aethel.diotec360.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name aethel.diotec360.com;
    return 301 https://$server_name$request_uri;
}
```

### Para backup.diotec360.com

```nginx
# /etc/nginx/sites-available/aethel-backup
server {
    listen 443 ssl http2;
    server_name backup.diotec360.com;
    
    ssl_certificate /etc/letsencrypt/live/backup.diotec360.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/backup.diotec360.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name backup.diotec360.com;
    return 301 https://$server_name$request_uri;
}
```

**Ativar configurações:**
```bash
sudo ln -s /etc/nginx/sites-available/aethel /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/aethel-backup /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## ✅ TESTES DE VERIFICAÇÃO

### Teste Individual dos Nós

```bash
# Node 1 (Hugging Face)
curl https://diotec-diotec360-judge.hf.space/health
curl https://diotec-diotec360-judge.hf.space/api/lattice/state

# Node 2 (Railway API)
curl https://api.diotec360.com/health
curl https://api.diotec360.com/api/lattice/state

# Node 3 (Vercel Backup)
curl https://backup.diotec360.com/health
curl https://backup.diotec360.com/api/lattice/state
```

### Teste de Sincronização

```bash
# Verificar Merkle Roots
curl https://diotec-diotec360-judge.hf.space/api/lattice/state | jq .merkle_root
curl https://api.diotec360.com/api/lattice/state | jq .merkle_root
curl https://backup.diotec360.com/api/lattice/state | jq .merkle_root

# Devem ser idênticos!
```

### Teste do Frontend

```bash
# Verificar se o frontend carrega
curl https://aethel.diotec360.com/

# Testar no navegador
# 1. Abrir https://aethel.diotec360.com/
# 2. Clicar em "Examples"
# 3. Selecionar um exemplo
# 4. Clicar em "Verify"
# 5. Deve mostrar resultado da prova
```

---

## 📊 MONITORAMENTO

### Script de Monitoramento Contínuo

```bash
# Criar script de monitoramento
cat > monitor_diotec360.sh << 'EOF'
#!/bin/bash

echo "=== AETHEL DIOTEC360 - MONITORING ==="
echo "Timestamp: $(date)"
echo ""

# Check Node 1
echo "[Node 1] Hugging Face"
curl -s https://diotec-diotec360-judge.hf.space/health | jq .status

# Check Node 2
echo "[Node 2] api.diotec360.com"
curl -s https://api.diotec360.com/health | jq .status

# Check Node 3
echo "[Node 3] backup.diotec360.com"
curl -s https://backup.diotec360.com/health | jq .status

# Check synchronization
echo ""
echo "=== SYNCHRONIZATION CHECK ==="
python verify_production_triangle.py

echo ""
echo "=== MONITORING COMPLETE ==="
EOF

chmod +x monitor_diotec360.sh

# Executar a cada 5 minutos
*/5 * * * * /path/to/monitor_diotec360.sh >> /var/log/aethel-monitor.log 2>&1
```

---

## 🎯 CHECKLIST FINAL

### Antes do Deploy
- [ ] DNS configurado para aethel.diotec360.com
- [ ] DNS configurado para backup.diotec360.com
- [ ] SSL certificados instalados
- [ ] Nginx configurado
- [ ] Servidores acessíveis via SSH

### Durante o Deploy
- [ ] Node 1 (HF) deployed e healthy
- [ ] Node 2 (Principal) deployed e healthy
- [ ] Node 3 (Backup) deployed e healthy
- [ ] Todos com mesmo Merkle Root
- [ ] HTTP Sync ativo em todos

### Após o Deploy
- [ ] Frontend carrega em https://aethel.diotec360.com/
- [ ] Exemplos funcionam
- [ ] Verificação de código funciona
- [ ] Monitoramento ativo
- [ ] Logs sendo coletados

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Deploy completo
deploy_node1_huggingface.bat
./deploy_node2_diotec360.sh
./deploy_node3_backup.sh
python verify_production_triangle.py

# Verificação rápida
curl https://diotec-diotec360-judge.hf.space/health
curl https://api.diotec360.com/health
curl https://backup.diotec360.com/health

# Monitoramento
./monitor_diotec360.sh
```

---

**🔺 CONFIGURAÇÃO COMPLETA PARA DIOTEC360.COM 🔺**

**Seus domínios estão configurados e prontos para deploy! Execute quando quiser! 🌌✨**

