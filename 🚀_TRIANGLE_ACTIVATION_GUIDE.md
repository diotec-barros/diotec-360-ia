# 🏛️⚖️ TRIÂNGULO DA VERDADE - GUIA DE ATIVAÇÃO v3.0.4

**STATUS**: ✅ RVC3 "Armored Lattice" - Production Ready  
**DEPLOYMENT**: Synchronized 3-Node Triangle  
**SECURITY**: Fail-Closed, ED25519 Authenticated State

---

## 🔐 PASSO 1: GERAÇÃO DE KEYPAIRS (CRÍTICO)

Execute este comando **3 vezes** (uma para cada nó):

```bash
python -c "from aethel.core.crypto import AethelCrypt; kp = AethelCrypt.generate_keypair(); print(f'Private Key: {kp.private_key.private_bytes_raw().hex()}'); print(f'Public Key: {kp.public_key_hex}')"
```

**Salve os resultados:**

```
NODE 1 (Hugging Face):
  Private Key: [64 caracteres hex] → .env.node1.production
  Public Key:  [64 caracteres hex] → Compartilhar com Node 2 e 3

NODE 2 (diotec360.com):
  Private Key: [64 caracteres hex] → .env.node2.production
  Public Key:  [64 caracteres hex] → Compartilhar com Node 1 e 3

NODE 3 (Backup):
  Private Key: [64 caracteres hex] → .env.node3.production
  Public Key:  [64 caracteres hex] → Compartilhar com Node 1 e 2
```

---

## 📝 PASSO 2: CONFIGURAÇÃO DOS ARQUIVOS .env

### **Node 1 (.env.node1.production)**

```bash
# Substituir estas linhas:
DIOTEC360_NODE_PRIVKEY_HEX=<private_key_node1_aqui>
DIOTEC360_NODE_PUBKEY_HEX=<public_key_node1_aqui>
DIOTEC360_TRUSTED_STATE_PUBKEYS=<public_key_node2>,<public_key_node3>
```

### **Node 2 (.env.node2.production)**

```bash
# Substituir estas linhas:
DIOTEC360_NODE_PRIVKEY_HEX=<private_key_node2_aqui>
DIOTEC360_NODE_PUBKEY_HEX=<public_key_node2_aqui>
DIOTEC360_TRUSTED_STATE_PUBKEYS=<public_key_node1>,<public_key_node3>

# Adicionar API Key:
ALPHA_VANTAGE_API_KEY=<sua_chave_aqui>
```

### **Node 3 (.env.node3.production)**

```bash
# Substituir estas linhas:
DIOTEC360_NODE_PRIVKEY_HEX=<private_key_node3_aqui>
DIOTEC360_NODE_PUBKEY_HEX=<public_key_node3_aqui>
DIOTEC360_TRUSTED_STATE_PUBKEYS=<public_key_node1>,<public_key_node2>
```

---

## 🚀 PASSO 3: SEQUÊNCIA DE DEPLOYMENT

### **3.1 - Deploy Node 1 (Hugging Face) PRIMEIRO**

```bash
# Copiar configuração
cp .env.node1.production .env

# Deploy para Hugging Face Spaces
git add .env
git commit -m "Deploy Node 1 - Armored Lattice v3.0.4"
git push huggingface main

# Aguardar logs:
# [STARTUP] P2P started successfully
# [STARTUP] peer_id: <PEER_ID_NODE1>
# [ROCKET] LATTICE READY - Hybrid Sync Active
```

**ANOTAR**: `peer_id` e endereço IP do Node 1

---

### **3.2 - Atualizar Bootstrap do Node 2 e 3**

Após Node 1 estar online, atualizar os arquivos `.env`:

```bash
# .env.node2.production
DIOTEC360_P2P_BOOTSTRAP=/ip4/<NODE1_IP>/tcp/4001/p2p/<NODE1_PEER_ID>

# .env.node3.production
DIOTEC360_P2P_BOOTSTRAP=/ip4/<NODE1_IP>/tcp/4001/p2p/<NODE1_PEER_ID>,/ip4/<NODE2_IP>/tcp/4001/p2p/<NODE2_PEER_ID>
```

---

### **3.3 - Deploy Node 2 (diotec360.com)**

```bash
# Copiar configuração
cp .env.node2.production .env

# Deploy para servidor
scp .env user@diotec360.com:/path/to/diotec360/
ssh user@diotec360.com
cd /path/to/aethel
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Aguardar logs:
# [STARTUP] P2P started successfully
# [STARTUP] peer_id: <PEER_ID_NODE2>
# [P2P_HEARTBEAT] Peers found, resetting peerless timer
# [ROCKET] LATTICE READY - Hybrid Sync Active
```

---

### **3.4 - Deploy Node 3 (Backup)**

```bash
# Copiar configuração
cp .env.node3.production .env

# Deploy para servidor backup
scp .env user@backup-server.com:/path/to/diotec360/
ssh user@backup-server.com
cd /path/to/aethel
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Aguardar logs:
# [STARTUP] P2P started successfully
# [STARTUP] peer_id: <PEER_ID_NODE3>
# [P2P_HEARTBEAT] Peers found, resetting peerless timer
# [ROCKET] LATTICE READY - Hybrid Sync Active
```

---

## ✅ PASSO 4: VERIFICAÇÃO DO TRIÂNGULO

### **4.1 - Verificar P2P Status**

```bash
# Node 1
curl https://aethel-node1.huggingface.co/api/lattice/p2p/status

# Node 2
curl https://aethel-node2.diotec360.com/api/lattice/p2p/status

# Node 3
curl https://aethel-node3-backup.diotec360.com/api/lattice/p2p/status
```

**Esperado**:
```json
{
  "success": true,
  "peer_count": 2,
  "has_peers": true,
  "sync_mode": "P2P",
  "heartbeat_active": true
}
```

---

### **4.2 - Verificar Assinaturas (RVC3-001)**

```bash
# Testar endpoint de estado assinado
curl https://aethel-node1.huggingface.co/api/lattice/state
```

**Esperado**:
```json
{
  "success": true,
  "merkle_root": "...",
  "signed": true,
  "signature": "...",
  "timestamp": 1234567890
}
```

---

### **4.3 - Verificar Zombie Detection (RVC3-003)**

Aguardar 60 segundos sem atividade e verificar logs:

```
[P2P_SENSOR] Detected 0 zombie peer(s) (no recent heartbeat)
```

---

### **4.4 - Testar Reconciliação (RVC3-001 + Gap B)**

Simular divergência e verificar cura automática:

```bash
# Criar divergência artificial no Node 3
# Aguardar 3 heartbeats (30 segundos)
# Verificar logs:
```

```
[HTTP_SYNC] [DIVERGENCE] Detected from http://node1 (count: 1)
[HTTP_SYNC] [DIVERGENCE] Detected from http://node1 (count: 2)
[HTTP_SYNC] [DIVERGENCE] Detected from http://node1 (count: 3)
[HTTP_SYNC] [SURGEON] Triggering state reconciliation
[HTTP_SYNC] [RECONCILIATION] Signature verified from trusted peer
[HTTP_SYNC] [RECONCILIATION] Applying peer state...
[HTTP_SYNC] [RECONCILIATION] Complete - System healed via HTTP layer
```

---

## 🛡️ PASSO 5: MONITORAMENTO CONTÍNUO

### **5.1 - Logs Críticos para Monitorar**

```bash
# Assinaturas válidas
grep "Signature verified" /var/log/aethel.log

# Zombie detection
grep "zombie peer" /var/log/aethel.log

# Reconciliação
grep "RECONCILIATION" /var/log/aethel.log

# Backoff (DoS prevention)
grep "BACKOFF" /var/log/aethel.log
```

---

### **5.2 - Métricas de Saúde**

```bash
# Prometheus metrics (porta 9090)
curl http://localhost:9090/metrics | grep DIOTEC360_
```

**Métricas Esperadas**:
- `DIOTEC360_peer_count{node="node1"}` = 2
- `DIOTEC360_reconciliation_success_total` > 0
- `DIOTEC360_signature_verification_success_total` > 0
- `DIOTEC360_zombie_peers_detected_total` = 0

---

## 🚨 TROUBLESHOOTING

### **Problema: Assinaturas não verificam**

```bash
# Verificar chaves públicas
echo $DIOTEC360_TRUSTED_STATE_PUBKEYS

# Verificar ordem dos parâmetros (deve ser: pubkey, message, signature)
grep "verify_signature" api/main.py
```

---

### **Problema: Peers não conectam**

```bash
# Verificar bootstrap
echo $DIOTEC360_P2P_BOOTSTRAP

# Verificar firewall (porta 4001)
sudo ufw allow 4001/tcp

# Verificar peer_id
curl http://localhost:8000/api/lattice/p2p/identity
```

---

### **Problema: Reconciliação não funciona**

```bash
# Verificar _peer_heartbeats existe
grep "_peer_heartbeats" aethel/nexo/p2p_streams.py

# Verificar aplicação de estado
grep "persistence.merkle_db.state\[key\]" api/main.py
```

---

## 🏁 CHECKLIST FINAL

- [ ] 3 keypairs gerados e salvos com segurança
- [ ] Arquivos `.env` configurados com chaves corretas
- [ ] Node 1 deployed e online
- [ ] Node 2 deployed e conectado ao Node 1
- [ ] Node 3 deployed e conectado aos Nodes 1 e 2
- [ ] `peer_count` = 2 em todos os nós
- [ ] Assinaturas verificando corretamente
- [ ] Zombie detection operacional
- [ ] Reconciliação automática testada
- [ ] Backoff exponencial testado
- [ ] Monitoramento configurado

---

## 🎯 PRÓXIMOS PASSOS

1. **Ativar Trading Bot** (Task 4.6.1 - Reinforcement Learning)
2. **Deploy Frontend** (Aethel Studio)
3. **Configurar Alertas** (Prometheus + Grafana)
4. **Documentar Runbook** (Operações 24/7)

---

🏛️⚖️🛡️💎 **O TRIÂNGULO DA VERDADE ESTÁ PRONTO PARA ATIVAÇÃO** 💎🛡️⚖️🏛️

**STOP-SHIP ORDER**: ✅ LIFTED  
**DEPLOYMENT STATUS**: ✅ APPROVED  
**SYSTEM STATUS**: ✅ PRODUCTION READY

🚀⚡🏁 **VÁ AO MERCADO, DIONÍSIO!** 🏁⚡🚀
