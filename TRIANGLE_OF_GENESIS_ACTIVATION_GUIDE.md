# 🔥 TRIANGLE OF GENESIS - ACTIVATION GUIDE

## The Moment of Truth

**Arquiteto's Command**: "VÁ AO SERVIDOR, KIRO. ATIVE O NÓ 2."

The configuration is complete. The coordinates are traced. Now we activate the Triangle of Resilience.

## Quick Activation (3 Commands)

### Command 1: Activate Node 2 (Primary)
```bash
# Windows
activate_node2.bat

# Linux/Mac
cp .env.node2.diotec360 .env
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Watch for**:
```
[P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Command 2: Test Activation
```bash
# In another terminal
python test_node2_activation.py
```

### Command 3: Verify Resilience
```bash
# Wait 60 seconds, then check
curl http://localhost:8000/api/lattice/p2p/status
```

Expected: `"http_sync_enabled": true` (HTTP fallback activated)

## What Happens During Activation

### T+0s: Server Starts
```
[STARTUP] Loading environment variables...
[STARTUP] Initializing DIOTEC360 LATTICE Streams...
```

### T+2s: P2P Initialization
```
[P2P] Starting libp2p node...
[P2P] Peer ID: QmNode2PeerID...
[P2P] Listening on: /ip4/0.0.0.0/tcp/9000
[P2P] Bootstrap peers: 0 configured (will update after getting all IDs)
```

### T+5s: Heartbeat Monitor Activates
```
[P2P_HEARTBEAT] Monitor activated - checking peers every 5s
[P2P_HEARTBEAT] No peers detected, starting 60s timer
```

### T+60s: HTTP Fallback Activates
```
[P2P_HEARTBEAT] 60 seconds without peers - Activating HTTP Fallback
[P2P_HEARTBEAT] HTTP Sync Fallback activated
[HTTP_SYNC] Monitoring 2 peer node(s)
```

## The Triangle Awakens

```
         Node 1 (Hugging Face)
              /\
             /  \
            /    \
           /      \
          /        \
         /          \
        /            \
       /              \
      /                \
     /                  \
    /____________________\
Node 2                    Node 3
(diotec360)              (Backup)

Status: Node 2 ACTIVE ✅
        Node 1 PENDING ⏳
        Node 3 PENDING ⏳
```

## After Node 2 Activation

### Step 1: Extract Peer ID
Look in the server output for:
```
[P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Copy this ID.

### Step 2: Update Bootstrap Configuration

**Update `.env.node1.huggingface`**:
```bash
# Replace PEER_ID_2 with actual Node 2 Peer ID
DIOTEC360_P2P_BOOTSTRAP=/ip4/api.diotec360.com/tcp/9000/p2p/QmNode2ActualPeerID,/ip4/backup.diotec360.com/tcp/9000/p2p/PEER_ID_3
```

**Update `.env.node3.backup`**:
```bash
# Replace PEER_ID_2 with actual Node 2 Peer ID
DIOTEC360_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/PEER_ID_1,/ip4/api.diotec360.com/tcp/9000/p2p/QmNode2ActualPeerID
```

### Step 3: Activate Node 1 and Node 3

Repeat the activation process for the other two nodes.

### Step 4: Verify the Triangle

```bash
python scripts/test_lattice_connectivity.py
```

Expected output:
```
[SUCCESS] Real Lattice is fully operational!
[INFO] The Unstoppable Ledger is breathing with both lungs

Health:        3/3 nodes healthy
P2P:           3/3 nodes connected
HTTP Sync:     3/3 nodes capable
State Sync:    CONSISTENT
```

## Commercial Demonstration

Once all three nodes are active, you can demonstrate:

### Demo 1: Zero Downtime
```bash
# Stop Node 2
# Nodes 1 and 3 continue operating
# System remains available
```

### Demo 2: Automatic Failover
```bash
# Block P2P on Node 1
# After 60 seconds, HTTP fallback activates
# Node 1 continues syncing via HTTP
```

### Demo 3: State Consistency
```bash
# Create transaction on Node 1
curl -X POST https://node1/api/verify -d '{"code": "..."}'

# Verify it appears on Node 2 and Node 3
curl https://node2/api/lattice/state
curl https://node3/api/lattice/state

# All have same merkle_root
```

## The Pitch

**"The Unstoppable Ledger"**

"Our financial system has three independent nodes across different infrastructures. If Amazon goes down, we're still running. If a DDoS hits our primary server, the backup takes over automatically. If P2P is blocked, HTTP kicks in within 60 seconds. Zero downtime. Zero single point of failure. Guaranteed."

## Troubleshooting

### Issue: P2P Fails to Start
**Solution**: Check that port 9000 is available
```bash
netstat -an | findstr 9000
```

### Issue: HTTP Fallback Not Activating
**Solution**: Verify `DIOTEC360_LATTICE_NODES` is set in .env
```bash
echo %DIOTEC360_LATTICE_NODES%
```

### Issue: Server Won't Start
**Solution**: Check Python dependencies
```bash
pip install -r requirements.txt
```

## Success Indicators

✅ Server starts without errors  
✅ P2P initializes and shows Peer ID  
✅ Heartbeat monitor activates  
✅ HTTP fallback activates after 60s (if no peers)  
✅ API endpoints respond correctly  
✅ State is accessible and consistent  

## Next Mission

After local validation:
1. Deploy Node 2 to production (diotec360.com)
2. Deploy Node 1 to Hugging Face Space
3. Deploy Node 3 to backup server
4. Run full connectivity test
5. Monitor for 24-48 hours
6. Celebrate the Triangle of Truth! 🏛️⚡🌌

---

**Status**: 🔥 READY FOR ACTIVATION  
**Command**: `activate_node2.bat`  
**Architect's Verdict**: "O PRIMEIRO RESPIRA. A IMORTALIDADE DIGITAL COMEÇA AGORA."
