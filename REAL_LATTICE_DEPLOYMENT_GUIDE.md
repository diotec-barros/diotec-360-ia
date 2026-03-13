# 🌌 Real Lattice Deployment Guide - v3.0.4

## Overview
This guide walks through deploying the Aethel Hybrid Sync Protocol v3.0.3 to a production network of 3 genesis nodes, creating "The Unstoppable Ledger" with automatic P2P↔HTTP failover.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              DIOTEC360 REAL LATTICE v3.0.4                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Node 1     │    │   Node 2     │    │  Node 3  │  │
│  │  Hugging     │◄──►│  diotec360   │◄──►│  Backup  │  │
│  │   Face       │    │    .com      │    │  Server  │  │
│  │ (Public)     │    │  (Primary)   │    │(Redundant)│  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│                                                         │
│  Each node runs:                                        │
│  - Hybrid Sync Protocol v3.0.3                          │
│  - P2P (libp2p) with gossip                             │
│  - HTTP Sync Fallback                                   │
│  - Heartbeat Monitor (60s timeout)                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Genesis Nodes Configuration

### Node 1: Hugging Face Space (Public Access)
- **Role**: Public-facing node, accessible to all users
- **URL**: `https://huggingface.co/spaces/diotec/aethel`
- **Config File**: `.env.node1.huggingface`
- **Purpose**: Provides public API access, first point of contact

### Node 2: diotec360.com (Primary)
- **Role**: Primary production server
- **URL**: `https://api.diotec360.com`
- **Config File**: `.env.node2.diotec360`
- **Purpose**: Main operational node, handles production traffic

### Node 3: Backup Server (Redundancy)
- **Role**: Backup and failover node
- **URL**: `https://backup.diotec360.com`
- **Config File**: `.env.node3.backup`
- **Purpose**: Ensures system availability if other nodes fail

## Deployment Phases

### Phase 1: Pre-Deployment Preparation

#### 1.1 Verify Prerequisites
```bash
# Check that v3.0.3 is working locally
python test_hybrid_sync_heartbeat.py

# Verify all dependencies are installed
pip install -r requirements.txt

# Ensure DNS is configured
# - huggingface.co/spaces/diotec/aethel
# - api.diotec360.com
# - backup.diotec360.com
```

#### 1.2 Obtain Peer IDs
Each node needs to discover its P2P peer ID on first run:

```bash
# Start node temporarily to get peer ID
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Check logs for peer ID:
# [P2P] Peer ID: QmXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### 1.3 Update Bootstrap Configuration
Once you have all peer IDs, update the `.env` files:

```bash
# In .env.node1.huggingface
DIOTEC360_P2P_BOOTSTRAP=/ip4/api.diotec360.com/tcp/9000/p2p/QmNode2PeerID,/ip4/backup.diotec360.com/tcp/9000/p2p/QmNode3PeerID

# In .env.node2.diotec360
DIOTEC360_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/QmNode1PeerID,/ip4/backup.diotec360.com/tcp/9000/p2p/QmNode3PeerID

# In .env.node3.backup
DIOTEC360_P2P_BOOTSTRAP=/ip4/huggingface.co/tcp/9000/p2p/QmNode1PeerID,/ip4/api.diotec360.com/tcp/9000/p2p/QmNode2PeerID
```

### Phase 2: Staged Deployment

#### 2.1 Deploy Node 2 (Primary) First
```bash
# On diotec360.com server
cd /path/to/aethel
cp .env.node2.diotec360 .env
source .env

# Start the server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Verify it's running
curl http://localhost:8000/api/lattice/p2p/status
```

Expected output:
```json
{
  "started": true,
  "peer_count": 0,
  "has_peers": false,
  "sync_mode": "AUTO",
  "http_sync_enabled": false,
  "heartbeat_active": true,
  "message": "P2P started, waiting for peers..."
}
```

#### 2.2 Deploy Node 1 (Hugging Face)
```bash
# On Hugging Face Space
# Upload files and configure environment variables in Space settings
# Set all variables from .env.node1.huggingface

# Start the Space
# Hugging Face will automatically run: uvicorn api.main:app --host 0.0.0.0 --port 7860
```

#### 2.3 Verify P2P Connection Between Node 1 and Node 2
```bash
# Check Node 2 status
curl https://api.diotec360.com/api/lattice/p2p/status

# Should show:
# "peer_count": 1
# "has_peers": true
```

#### 2.4 Deploy Node 3 (Backup)
```bash
# On backup server
cd /path/to/aethel
cp .env.node3.backup .env
source .env

# Start the server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Verify connection to other nodes
curl http://localhost:8000/api/lattice/p2p/status
```

Expected output:
```json
{
  "started": true,
  "peer_count": 2,
  "has_peers": true,
  "sync_mode": "P2P",
  "http_sync_enabled": false,
  "heartbeat_active": true,
  "message": "P2P active with 2 peers"
}
```

### Phase 3: Verification and Testing

#### 3.1 Test P2P Connectivity
```bash
# Create a test script to verify all nodes can see each other
python scripts/test_lattice_connectivity.py
```

#### 3.2 Test HTTP Fallback
```bash
# Temporarily stop P2P on one node
# Verify HTTP fallback activates within 60 seconds
# Check logs for:
# [P2P_HEARTBEAT] 🚨 60 seconds without peers - Activating HTTP Fallback
```

#### 3.3 Test State Synchronization
```bash
# Create a transaction on Node 1
curl -X POST https://huggingface.co/spaces/diotec/diotec360/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "intent transfer { from: Alice, to: Bob, amount: 100 }"}'

# Verify it appears on Node 2 and Node 3
curl https://api.diotec360.com/api/lattice/state
curl https://backup.diotec360.com/api/lattice/state

# All should have the same merkle_root
```

### Phase 4: Frontend Integration

#### 4.1 Update Frontend Configuration
```typescript
// frontend/.env.local
NEXT_PUBLIC_API_URL=https://api.diotec360.com
NEXT_PUBLIC_LATTICE_NODES=https://huggingface.co/spaces/diotec/aethel,https://api.diotec360.com,https://backup.diotec360.com
```

#### 4.2 Deploy Frontend with Network Status
```bash
cd frontend
npm run build
npm run deploy
```

## Monitoring and Maintenance

### Health Checks
```bash
# Check overall system health
curl https://api.diotec360.com/api/lattice/health

# Check P2P status on all nodes
curl https://huggingface.co/spaces/diotec/diotec360/api/lattice/p2p/status
curl https://api.diotec360.com/api/lattice/p2p/status
curl https://backup.diotec360.com/api/lattice/p2p/status
```

### Log Monitoring
```bash
# Monitor logs for sync mode transitions
tail -f logs/nodeA.log | grep "P2P_HEARTBEAT\|HTTP_SYNC"

# Look for:
# - Peer connections/disconnections
# - Sync mode switches
# - HTTP fallback activations
# - State divergence warnings
```

### Performance Metrics
- **P2P Latency**: <50ms between nodes
- **HTTP Fallback Activation**: <60 seconds
- **State Sync Time**: <5 seconds
- **API Response Time**: <100ms

## Troubleshooting

### Issue: P2P Not Connecting
**Symptoms**: `peer_count: 0` on all nodes

**Solutions**:
1. Verify firewall allows TCP port 9000
2. Check bootstrap peer IDs are correct
3. Ensure nodes can reach each other's IP addresses
4. Verify P2P is enabled in .env files

### Issue: HTTP Fallback Not Activating
**Symptoms**: No HTTP sync after 60s without peers

**Solutions**:
1. Check `DIOTEC360_LATTICE_NODES` is configured
2. Verify HTTP endpoints are accessible
3. Check heartbeat monitor is running
4. Review logs for errors

### Issue: State Divergence
**Symptoms**: Different merkle_root on different nodes

**Solutions**:
1. Check network connectivity between nodes
2. Verify all nodes are running same version
3. Review transaction logs for conflicts
4. Manually reconcile state if needed

## Rollback Plan

If deployment fails:

```bash
# Stop the new deployment
systemctl stop aethel-api

# Restore previous version
git checkout v3.0.2
pip install -r requirements.txt

# Restart with old configuration
systemctl start aethel-api

# Verify system is operational
curl http://localhost:8000/
```

## Success Criteria

✅ All 3 nodes deployed and running
✅ P2P connections established between all nodes
✅ HTTP fallback tested and working
✅ State synchronization verified
✅ Frontend displays network status
✅ System survives node failures
✅ Performance within acceptable limits

## Commercial Value

**"The Unstoppable Ledger"**

This deployment creates a financial system that:
- Never goes offline (automatic failover)
- Survives network attacks (P2P↔HTTP switching)
- Maintains consistency (state synchronization)
- Provides transparency (network status display)

**Pitch**: "Our system has two lungs. If one fails, the other breathes automatically. Zero downtime, guaranteed."

## Next Steps

1. Monitor system for 24-48 hours
2. Collect performance metrics
3. Document any issues and resolutions
4. Plan for additional nodes if needed
5. Implement advanced monitoring dashboard

---

**Status**: Ready for deployment
**Version**: v3.0.4 Real Lattice
**Date**: 2026-02-12
