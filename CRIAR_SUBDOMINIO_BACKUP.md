# 🌐 CRIAR SUBDOMÍNIO backup.diotec360.com

**Data:** 2026-02-12  
**Objetivo:** Configurar Node 3 (Backup) do Triângulo

---

## 🎯 O QUE VAMOS CRIAR

**Subdomínio:** backup.diotec360.com  
**Função:** Node 3 - Servidor de Backup do Triângulo  
**Tipo:** Subdomínio A ou CNAME

---

## 📋 OPÇÕES DE CONFIGURAÇÃO

### Opção 1: Servidor Dedicado (Recomendado)

Se você tem um servidor separado para backup:

```
Type: A
Name: backup
Value: [IP do servidor backup]
TTL: 3600
```

### Opção 2: Mesmo Servidor, Porta Diferente

Se vai rodar no mesmo servidor que aethel.diotec360.com:

```
Type: CNAME
Name: backup
Value: aethel.diotec360.com
TTL: 3600
```

### Opção 3: Serviço Cloud (Railway, Render, etc.)

Se vai usar um serviço cloud:

```
Type: CNAME
Name: backup
Value: [hostname fornecido pelo serviço]
TTL: 3600
```

---

## 🔧 PASSO A PASSO - CONFIGURAÇÃO DNS

### 1. Acessar Painel DNS

Acesse o painel de controle do seu provedor de domínio (onde comprou diotec360.com):
- GoDaddy
- Namecheap
- Cloudflare
- Registro.br (se for .br)
- Outro provedor

### 2. Adicionar Registro DNS

**No painel DNS, adicione um novo registro:**

#### Se for servidor dedicado (IP próprio):
```
Tipo: A
Nome/Host: backup
Valor/Aponta para: 123.456.789.012  (seu IP)
TTL: 3600 (1 hora)
```

#### Se for CNAME (apontar para outro domínio):
```
Tipo: CNAME
Nome/Host: backup
Valor/Aponta para: aethel.diotec360.com
TTL: 3600 (1 hora)
```

### 3. Salvar e Aguardar Propagação

- Clique em "Salvar" ou "Add Record"
- Aguarde 5-30 minutos para propagação DNS
- Pode levar até 24 horas em alguns casos

### 4. Verificar Propagação

```bash
# Verificar se o DNS está propagado
nslookup backup.diotec360.com

# Ou usar dig
dig backup.diotec360.com

# Ou testar online
# https://dnschecker.org
```

---

## 🔐 CONFIGURAR SSL (Let's Encrypt)

### Depois que o DNS propagar:

```bash
# SSH no servidor
ssh user@backup.diotec360.com

# Instalar certbot (se ainda não tiver)
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d backup.diotec360.com

# Seguir as instruções na tela
# Escolher opção 2 (Redirect HTTP to HTTPS)
```

---

## 🌐 CONFIGURAR NGINX

### Criar configuração do Nginx:

```bash
# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/aethel-backup
```

### Adicionar esta configuração:

```nginx
# Diotec360 Node 3 - Backup Server
server {
    listen 80;
    server_name backup.diotec360.com;
    
    # Certbot vai adicionar SSL aqui automaticamente
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (se necessário)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Ativar configuração:

```bash
# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/aethel-backup /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Se OK, recarregar nginx
sudo systemctl reload nginx
```

---

## 🚀 DEPLOY DO NODE 3

### 1. Preparar Servidor

```bash
# SSH no servidor
ssh user@backup.diotec360.com

# Criar diretório
sudo mkdir -p /var/www/aethel
cd /var/www/aethel

# Clonar repositório
git clone https://github.com/diotec/aethel.git .

# Instalar dependências
pip3 install -r requirements.txt
```

### 2. Configurar Ambiente

```bash
# Copiar configuração do Node 3
cp .env.node3.backup .env

# Editar se necessário
nano .env
```

### 3. Criar Serviço Systemd

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/aethel-backup.service
```

### Adicionar esta configuração:

```ini
[Unit]
Description=DIOTEC360 LATTICE Node 3 (Backup)
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/aethel
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Iniciar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable aethel-backup

# Iniciar serviço
sudo systemctl start aethel-backup

# Verificar status
sudo systemctl status aethel-backup
```

---

## ✅ VERIFICAR FUNCIONAMENTO

### Teste 1: Health Check

```bash
# Local (no servidor)
curl http://localhost:8000/health

# Remoto (de qualquer lugar)
curl https://backup.diotec360.com/health
```

**Esperado:**
```json
{"status":"healthy","version":"1.7.0"}
```

### Teste 2: Estado do Lattice

```bash
curl https://backup.diotec360.com/api/lattice/state
```

**Esperado:**
```json
{
  "success": true,
  "merkle_root": "5df3daee3a0ca23c388a16c3db2c2388...",
  "entry_count": 6
}
```

### Teste 3: HTTP Sync Status

```bash
curl https://backup.diotec360.com/api/lattice/p2p/status
```

**Esperado:**
```json
{
  "http_sync_enabled": true,
  "peer_count": 2,
  "mode": "http"
}
```

---

## 🔍 TROUBLESHOOTING

### DNS não propaga

```bash
# Verificar configuração DNS
nslookup backup.diotec360.com

# Se não resolver, aguardar mais tempo
# Ou verificar se o registro foi criado corretamente no painel DNS
```

### SSL não funciona

```bash
# Verificar se certbot rodou corretamente
sudo certbot certificates

# Tentar novamente
sudo certbot --nginx -d backup.diotec360.com

# Verificar logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Serviço não inicia

```bash
# Verificar logs
sudo journalctl -u aethel-backup -f

# Verificar se porta 8000 está livre
sudo lsof -i :8000

# Se ocupada, matar processo
sudo kill -9 <PID>

# Reiniciar serviço
sudo systemctl restart aethel-backup
```

### Nginx erro 502

```bash
# Verificar se o serviço está rodando
sudo systemctl status aethel-backup

# Verificar logs do nginx
sudo tail -f /var/log/nginx/error.log

# Verificar se pode conectar localmente
curl http://localhost:8000/health
```

---

## 📊 MONITORAMENTO

### Script de Monitoramento

```bash
# Criar script
cat > /usr/local/bin/monitor-backup.sh << 'EOF'
#!/bin/bash

echo "=== BACKUP NODE MONITORING ==="
echo "Timestamp: $(date)"

# Check service
systemctl is-active aethel-backup
if [ $? -eq 0 ]; then
  echo "✅ Service: Running"
else
  echo "❌ Service: Stopped"
  sudo systemctl start aethel-backup
fi

# Check health
curl -s https://backup.diotec360.com/health | jq .status

# Check disk space
df -h /var/www/aethel

echo "=== MONITORING COMPLETE ==="
EOF

chmod +x /usr/local/bin/monitor-backup.sh

# Adicionar ao cron (executar a cada 5 minutos)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor-backup.sh >> /var/log/aethel-backup-monitor.log 2>&1") | crontab -
```

---

## 🎯 CHECKLIST FINAL

### Antes do Deploy
- [ ] DNS configurado (A ou CNAME)
- [ ] DNS propagado (verificado com nslookup)
- [ ] Servidor acessível via SSH
- [ ] Nginx instalado
- [ ] Python 3.11+ instalado

### Durante o Deploy
- [ ] Repositório clonado
- [ ] Dependências instaladas
- [ ] .env configurado
- [ ] Serviço systemd criado
- [ ] Nginx configurado
- [ ] SSL certificado obtido

### Após o Deploy
- [ ] Health check responde
- [ ] Estado do lattice acessível
- [ ] HTTP Sync ativo
- [ ] Merkle Root sincronizado
- [ ] Monitoramento ativo

---

## 🚀 COMANDOS RÁPIDOS

```bash
# Deploy completo (executar no servidor)
git clone https://github.com/diotec/aethel.git /var/www/aethel
cd /var/www/aethel
pip3 install -r requirements.txt
cp .env.node3.backup .env
sudo systemctl start aethel-backup

# Verificar
curl https://backup.diotec360.com/health

# Logs
sudo journalctl -u aethel-backup -f
```

---

## 📞 SUPORTE

### Se precisar de ajuda:

1. **DNS:** Contate seu provedor de domínio
2. **SSL:** Verifique logs do certbot
3. **Nginx:** Teste configuração com `nginx -t`
4. **Serviço:** Verifique logs com `journalctl`

---

## 🎉 PRÓXIMOS PASSOS

Depois que backup.diotec360.com estiver funcionando:

1. **Verificar Triangle:**
   ```bash
   python verify_production_triangle.py
   ```

2. **Testar Failover:**
   - Parar Node 2
   - Verificar se Node 1 e 3 continuam sincronizados

3. **Monitorar por 24 horas:**
   - Verificar logs
   - Verificar sincronização
   - Verificar performance

---

**🔺 GUIA COMPLETO PARA CRIAR backup.diotec360.com 🔺**

**Siga os passos e seu Node 3 estará no ar! 🌌✨**

