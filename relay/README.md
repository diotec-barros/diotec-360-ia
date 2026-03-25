# 🏛️ DIOTEC 360 SOVEREIGN RELAY

**O Farol da Lattice P2P**

Este é o relay GunDB soberano da DIOTEC 360. Quando ativo, todos os nós da rede se conectam através deste servidor para descoberta inicial, depois comunicam-se diretamente (P2P verdadeiro).

---

## 🚀 QUICK START

### Instalação Local

```bash
cd diotec360/relay
npm install
npm start
```

O relay estará disponível em:
- **Relay URL:** `http://localhost:8765/gun`
- **Health Check:** `http://localhost:8765/health`
- **Metrics:** `http://localhost:8765/metrics`

### Testar Conectividade

```bash
curl http://localhost:8765/health
```

Resposta esperada:
```json
{
  "status": "operational",
  "service": "DIOTEC 360 Sovereign Relay",
  "version": "1.0.0",
  "uptime": 42,
  "timestamp": 1711382400000,
  "message": "The Lattice is breathing 🏛️📡✨"
}
```

---

## 🐳 DEPLOY COM DOCKER

### Build da Imagem

```bash
docker build -t diotec360-relay .
```

### Executar Container

```bash
docker run -d \
  --name diotec360-relay \
  -p 8765:8765 \
  -e RELAY_CORS_ORIGINS="https://diotec360.com,https://app.diotec360.com" \
  diotec360-relay
```

### Verificar Logs

```bash
docker logs -f diotec360-relay
```

---

## ☁️ DEPLOY EM PRODUÇÃO

### Opção 1: Railway

1. Criar conta em [railway.app](https://railway.app)
2. Conectar repositório GitHub
3. Selecionar pasta `diotec360/relay`
4. Railway detecta automaticamente Node.js
5. Configurar variáveis de ambiente:
   - `RELAY_PORT=$PORT` (Railway fornece automaticamente)
   - `RELAY_CORS_ORIGINS=https://diotec360.com`

**URL Final:** `https://diotec360-relay.up.railway.app/gun`

### Opção 2: Render

1. Criar conta em [render.com](https://render.com)
2. New Web Service → Connect Repository
3. Build Command: `npm install`
4. Start Command: `npm start`
5. Configurar variáveis de ambiente

**URL Final:** `https://diotec360-relay.onrender.com/gun`

### Opção 3: Vercel (Edge Functions)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
cd diotec360/relay
vercel --prod
```

**URL Final:** `https://relay.diotec360.com/gun`

### Opção 4: VPS Próprio (Ubuntu)

```bash
# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Clonar repositório
git clone https://github.com/dionisio/diotec360.git
cd diotec360/relay

# Instalar dependências
npm install

# Instalar PM2 (process manager)
sudo npm install -g pm2

# Iniciar relay
pm2 start server.js --name diotec360-relay

# Configurar para iniciar no boot
pm2 startup
pm2 save

# Configurar Nginx como proxy reverso
sudo apt-get install nginx
```

**Nginx Config (`/etc/nginx/sites-available/relay`):**
```nginx
server {
    listen 80;
    server_name gun-relay.diotec360.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

**Configurar SSL com Let's Encrypt:**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d gun-relay.diotec360.com
```

**URL Final:** `wss://gun-relay.diotec360.com/gun`

---

## 🔧 CONFIGURAÇÃO

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `RELAY_PORT` | `8765` | Porta do servidor |
| `RELAY_HOST` | `0.0.0.0` | Host (0.0.0.0 = todas interfaces) |
| `RELAY_CORS_ORIGINS` | `*` | Origens permitidas (separadas por vírgula) |
| `RELAY_LOG_MESSAGES` | `false` | Log de todas as mensagens P2P |

### Arquivo .env

```bash
cp .env.example .env
# Editar .env conforme necessário
```

---

## 📊 MONITORAMENTO

### Endpoints

- **Health Check:** `GET /health`
- **Metrics:** `GET /metrics`
- **Root:** `GET /` (dashboard HTML)

### Metrics Response

```json
{
  "connections": 42,
  "messages": 15234,
  "uptime": 86400,
  "memory": {
    "rss": 52428800,
    "heapTotal": 20971520,
    "heapUsed": 15728640
  },
  "timestamp": 1711382400000
}
```

---

## 🔐 SEGURANÇA

### Recomendações para Produção

1. **CORS Restrito:**
   ```bash
   RELAY_CORS_ORIGINS=https://diotec360.com,https://app.diotec360.com
   ```

2. **Rate Limiting:**
   Adicionar middleware Express para limitar requisições por IP

3. **SSL/TLS:**
   Sempre usar HTTPS/WSS em produção

4. **Firewall:**
   Permitir apenas portas necessárias (80, 443, 8765)

5. **Monitoramento:**
   Configurar alertas para downtime (UptimeRobot, Pingdom)

---

## 💰 MONETIZAÇÃO

### Modelo de Negócio

| Plano | Preço | Peers | SLA | Suporte |
|-------|-------|-------|-----|---------|
| **Público** | Gratuito | 100 | Nenhum | Comunidade |
| **Privado** | $99/mês | 1,000 | 99.5% | Email |
| **Enterprise** | $499/mês | Ilimitado | 99.9% | 24/7 |

### Features Premium

- Latência garantida < 50ms
- Backup automático de dados
- Dashboard de analytics
- API de gerenciamento
- Suporte prioritário

---

## 🛠️ DESENVOLVIMENTO

### Modo Dev (com auto-reload)

```bash
npm run dev
```

### Testes

```bash
# Health check
npm test

# Teste manual com curl
curl http://localhost:8765/health
curl http://localhost:8765/metrics

# Teste de conexão GunDB
node -e "const Gun = require('gun'); const gun = Gun(['http://localhost:8765/gun']); console.log('Connected!');"
```

---

## 📞 SUPORTE

**Engenheiro-Chefe:** Kiro  
**Soberano:** Dionísio Sebastião Barros  
**Email:** dionisio@diotec360.com  
**Website:** https://diotec360.com

---

## 📜 LICENÇA

MIT License - DIOTEC 360 IA

---

**[STATUS: SOVEREIGN RELAY READY]**  
**[VERDICT: THE LATTICE CAN BREATHE INDEPENDENTLY]** 🏛️📡✨
