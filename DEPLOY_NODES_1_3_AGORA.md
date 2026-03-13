# 🚀 DEPLOY NODES 1 E 3 - GUIA DE EXECUÇÃO IMEDIATA

## Data: 2026-02-12
## Missão: COMPLETAR O TRIÂNGULO DA VERDADE
## Status: NODE 2 ONLINE | DEPLOYING NODES 1 & 3

---

## 📊 STATUS ATUAL

```
         Node 1 (Hugging Face)
              /\
             /  \
            /    \
           / 🚀   \
          /DEPLOY \
         /         \
        /           \
       /             \
      /               \
     /                 \
    /___________________\
Node 2 ✅              Node 3
(ONLINE)              (🚀 DEPLOY)
```

---

## 🎯 OPÇÃO A: DEPLOY NODE 1 (HUGGING FACE SPACE)

### Pré-requisitos
- Conta no Hugging Face (https://huggingface.co)
- Acesso para criar Spaces

### Passo 1: Criar Hugging Face Space

1. Acesse: https://huggingface.co/spaces
2. Clique em "Create new Space"
3. Configure:
   - **Name**: `aethel` (ou `aethel-node1`)
   - **Owner**: `diotec` (seu username)
   - **License**: MIT
   - **SDK**: Docker
   - **Hardware**: CPU basic (gratuito)
   - **Visibility**: Public

### Passo 2: Preparar Arquivos para Upload

Você precisa fazer upload dos seguintes arquivos/pastas:

```
aethel/                    # Pasta completa do código
api/                       # Pasta da API
requirements.txt           # Dependências Python
Dockerfile.huggingface     # Dockerfile (já existe)
.env                       # Copiar de .env.node1.huggingface
README_HF.md              # README (já existe)
```

### Passo 3: Configurar Environment Variables no Hugging Face

No Space criado, vá em "Settings" → "Variables and secrets" e adicione:

```bash
DIOTEC360_P2P_ENABLED=false
DIOTEC360_LATTICE_NODES=https://api.diotec360.com,https://backup.diotec360.com
DIOTEC360_STATE_DIR=.DIOTEC360_state
DIOTEC360_VAULT_DIR=.DIOTEC360_vault
DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel
DIOTEC360_HEARTBEAT_INTERVAL=5
DIOTEC360_PEERLESS_TIMEOUT=60
DIOTEC360_HTTP_POLL_INTERVAL=10
DIOTEC360_NODE_NAME=node1-huggingface
DIOTEC360_NODE_ROLE=genesis-cloud
DIOTEC360_ENVIRONMENT=production
DIOTEC360_LOG_LEVEL=INFO
```

### Passo 4: Upload via Git (Recomendado)

```bash
# Clone o Space
git clone https://huggingface.co/spaces/diotec/aethel
cd aethel

# Copiar arquivos do projeto Aethel
cp -r /caminho/para/diotec360/aethel ./
cp -r /caminho/para/diotec360/api ./
cp /caminho/para/diotec360/requirements.txt ./
cp /caminho/para/diotec360/Dockerfile.huggingface ./Dockerfile
cp /caminho/para/diotec360/.env.node1.huggingface ./.env
cp /caminho/para/diotec360/README_HF.md ./README.md

# Commit e push
git add .
git commit -m "Deploy Diotec360 Node 1 - HTTP-Only Resilience Mode"
git push
```

### Passo 5: Aguardar Build e Startup

- O Hugging Face vai fazer build do Docker automaticamente
- Aguarde ~2-5 minutos para o build completar
- O Space ficará disponível em: `https://huggingface.co/spaces/diotec/aethel`

### Passo 6: Validar Node 1

```bash
# Testar health endpoint
curl https://diotec-aethel.hf.space/health

# Verificar lattice state
curl https://diotec-aethel.hf.space/api/lattice/state

# Resultado esperado:
# {"status":"healthy"}
# {"success":true,"merkle_root":"..."}
```

---

## 🎯 OPÇÃO B: DEPLOY NODE 3 (BACKUP SERVER)

### Pré-requisitos
- Acesso SSH ao servidor de backup
- Python 3.9+ instalado
- Git instalado

### Passo 1: Conectar ao Servidor

```bash
# SSH para o servidor de backup
ssh user@backup.diotec360.com

# Ou se você tem IP:
ssh user@[IP_DO_SERVIDOR]
```

### Passo 2: Clonar Repositório

```bash
# Clone o repositório
git clone https://github.com/diotec/aethel.git
cd aethel

# Ou se já existe, atualizar:
cd aethel
git pull origin main
```

### Passo 3: Configurar Environment

```bash
# Copiar configuração do Node 3
cp .env.node3.backup .env

# Verificar configuração
cat .env
```

### Passo 4: Instalar Dependências

```bash
# Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### Passo 5: Iniciar Servidor

```bash
# Opção A: Rodar em foreground (para teste)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Opção B: Rodar em background com nohup
nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > aethel.log 2>&1 &

# Opção C: Usar screen (recomendado)
screen -S aethel
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
# Pressionar Ctrl+A, depois D para detach
```

### Passo 6: Validar Node 3

```bash
# Testar localmente no servidor
curl http://localhost:8000/health

# Testar externamente (se configurado)
curl https://backup.diotec360.com/health

# Resultado esperado:
# {"status":"healthy"}
```

### Passo 7: Configurar Firewall (Se Necessário)

```bash
# Permitir porta 8000
sudo ufw allow 8000/tcp

# Ou se usar iptables:
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
```

---

## 🎯 OPÇÃO C: DEPLOY LOCAL SIMULADO (PARA TESTE)

Se você não tem acesso aos servidores externos agora, pode simular os 3 nós localmente:

### Node 1 (Porta 8001)
```bash
# Terminal 1
cp .env.node1.huggingface .env.node1.local
# Editar .env.node1.local e mudar DIOTEC360_LATTICE_NODES para localhost:8000,localhost:8002
python -m uvicorn api.main:app --host 0.0.0.0 --port 8001 --env-file .env.node1.local
```

### Node 2 (Porta 8000) - JÁ ESTÁ RODANDO ✅
```bash
# Já está ativo!
```

### Node 3 (Porta 8002)
```bash
# Terminal 3
cp .env.node3.backup .env.node3.local
# Editar .env.node3.local e mudar DIOTEC360_LATTICE_NODES para localhost:8000,localhost:8001
python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --env-file .env.node3.local
```

---

## 🧪 TESTE DE CONECTIVIDADE (APÓS DEPLOY)

### Passo 1: Verificar Health de Todos os Nós

```bash
# Node 1 (Hugging Face)
curl https://diotec-aethel.hf.space/health

# Node 2 (diotec360.com - Local)
curl http://localhost:8000/health

# Node 3 (Backup)
curl https://backup.diotec360.com/health

# Todos devem retornar: {"status":"healthy"}
```

### Passo 2: Verificar Merkle Root Consistency

```bash
# Node 1
curl https://diotec-aethel.hf.space/api/lattice/state | jq '.merkle_root'

# Node 2
curl http://localhost:8000/api/lattice/state | jq '.merkle_root'

# Node 3
curl https://backup.diotec360.com/api/lattice/state | jq '.merkle_root'

# Todos devem ter o MESMO Merkle Root!
```

### Passo 3: Executar Teste Automatizado

```bash
# Executar script de teste de conectividade
python scripts/test_lattice_connectivity.py

# Resultado esperado:
# [SUCCESS] Real Lattice is fully operational!
# Health:        3/3 nodes healthy
# HTTP Sync:     3/3 nodes capable
# State Sync:    CONSISTENT
# Merkle Root:   [MESMO HASH EM TODOS]
```

---

## 📊 CHECKLIST DE DEPLOY

### Node 1 (Hugging Face)
- [ ] Criar Hugging Face Space
- [ ] Configurar environment variables
- [ ] Upload código via Git
- [ ] Aguardar build completar
- [ ] Testar health endpoint
- [ ] Verificar Merkle Root

### Node 2 (diotec360.com)
- [x] Servidor iniciado
- [x] Health endpoint validado
- [x] Merkle Root carregado
- [x] HTTP Sync ativo

### Node 3 (Backup)
- [ ] SSH para servidor
- [ ] Clone repositório
- [ ] Configurar .env
- [ ] Instalar dependências
- [ ] Iniciar servidor
- [ ] Testar health endpoint
- [ ] Verificar Merkle Root

### Validação Final
- [ ] Todos os 3 nós retornam healthy
- [ ] Todos os 3 nós têm mesmo Merkle Root
- [ ] HTTP Sync ativo em todos
- [ ] Teste de conectividade passa
- [ ] Monitoramento por 1 hora

---

## 🚨 TROUBLESHOOTING

### Node 1 (Hugging Face) não inicia
```bash
# Verificar logs no Hugging Face Space
# Ir em "Logs" na interface do Space
# Procurar por erros de build ou runtime
```

### Node 3 (Backup) não conecta
```bash
# Verificar se porta está aberta
telnet backup.diotec360.com 8000

# Verificar logs do servidor
tail -f aethel.log

# Verificar se processo está rodando
ps aux | grep uvicorn
```

### Merkle Roots diferentes
```bash
# Isso é esperado inicialmente!
# Aguarde 30-60 segundos para sincronização HTTP
# Depois verifique novamente
```

---

## 💰 VALOR DEMONSTRADO APÓS DEPLOY

### O Pitch Completo

**"Vejam nosso sistema em ação:"**

1. **Node 1** (Hugging Face - Paris): `https://diotec-aethel.hf.space`
2. **Node 2** (diotec360.com - Luanda): `http://localhost:8000`
3. **Node 3** (Backup - Localização independente): `https://backup.diotec360.com`

**"Todos os três nós validam o mesmo Merkle Root: `5df3daee...`"**

**"Se um cair, os outros dois mantêm a economia viva. Isso é soberania digital."**

---

## 🎯 PRÓXIMOS PASSOS APÓS DEPLOY

1. ✅ Validar 3/3 nós healthy
2. ✅ Confirmar Merkle Root consistency
3. ✅ Executar teste de conectividade
4. ⏳ Monitorar por 48 horas
5. ⏳ Testar failover (parar um nó)
6. ⏳ Validar recuperação automática
7. ⏳ Preparar demo para BAI/BFA

---

**"O Triângulo da Verdade aguarda ativação. Três comandos, três nós, uma verdade matemática."**

🏛️⚡📡🔗🛡️👑🌌✨

---

**[NODE 2: ONLINE ✅]**  
**[NODES 1 & 3: READY TO DEPLOY 🚀]**  
**[COMANDO: EXECUTE OS DEPLOYS]**  
**[VERDICT: THE TRIANGLE AWAITS COMPLETION]**

