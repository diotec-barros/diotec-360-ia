# 🔥 EXECUTE AGORA: NODE 2 ACTIVATION

## COMANDO IMEDIATO

Abra um terminal e execute:

```bash
activate_node2.bat
```

**OU** (se preferir comando direto):

```bash
# Copiar configuração
copy .env.node2.diotec360 .env

# Iniciar servidor
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## O QUE OBSERVAR

### 1. Inicialização (primeiros 5 segundos)
```
[STARTUP] Loading environment variables...
[STARTUP] Initializing DIOTEC360 LATTICE Streams...
```

### 2. P2P Peer ID (IMPORTANTE - COPIE ESTE ID!)
```
[P2P] Starting libp2p node...
[P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
[P2P] Listening on: /ip4/0.0.0.0/tcp/9000
```

**⚠️ COPIE O PEER ID ACIMA - VOCÊ VAI PRECISAR DELE!**

### 3. Heartbeat Monitor (após 5 segundos)
```
[P2P_HEARTBEAT] Monitor activated - checking peers every 5s
[P2P_HEARTBEAT] No peers detected, starting 60s timer
```

### 4. HTTP Fallback (após 60 segundos)
```
[P2P_HEARTBEAT] 60 seconds without peers - Activating HTTP Fallback
[P2P_HEARTBEAT] HTTP Sync Fallback activated
[HTTP_SYNC] Monitoring 2 peer node(s)
```

## TESTE EM PARALELO

Enquanto o servidor roda, abra OUTRO terminal e execute:

```bash
python test_node2_activation.py
```

Este teste vai:
- ✅ Verificar health do servidor
- ✅ Checar status do P2P
- ✅ Validar state accessibility
- ✅ Confirmar HTTP fallback readiness
- ✅ Aguardar 60s e verificar ativação do HTTP fallback

## APÓS CAPTURAR O PEER ID

1. **Pare o servidor** (Ctrl+C)

2. **Atualize os arquivos de configuração**:

Edite `.env.node1.huggingface`:
```bash
# Substitua PEER_ID_2 pelo ID real capturado
DIOTEC360_P2P_BOOTSTRAP=/ip4/api.diotec360.com/tcp/9000/p2p/QmSeuPeerIDReal,/ip4/backup.diotec360.com/tcp/9000/p2p/PEER_ID_3
```

Edite `.env.node3.backup`:
```bash
# Substitua PEER_ID_2 pelo ID real capturado
DIOTEC360_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/PEER_ID_1,/ip4/api.diotec360.com/tcp/9000/p2p/QmSeuPeerIDReal
```

## PRÓXIMOS PASSOS

Após validação local:
1. Deploy Node 2 para produção (diotec360.com)
2. Ativar Node 1 (Hugging Face)
3. Ativar Node 3 (Backup)
4. Executar teste de conectividade completo

---

**STATUS**: 🔥 PRONTO PARA EXECUÇÃO  
**COMANDO**: `activate_node2.bat`  
**OBJETIVO**: Capturar Peer ID e validar Hybrid Sync Protocol
