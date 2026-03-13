# Proof-of-Proof Consensus Deployment Guide

This guide provides step-by-step instructions for deploying the Proof-of-Proof consensus protocol.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Genesis State Initialization](#genesis-state-initialization)
3. [Starting Validator Nodes](#starting-validator-nodes)
4. [Joining an Existing Network](#joining-an-existing-network)
5. [Monitoring the Network](#monitoring-the-network)
6. [Testnet Deployment](#testnet-deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- Network connectivity for P2P communication

### Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

Required packages:
- z3-solver (proof verification)
- hypothesis (property-based testing)
- cryptography (Ed25519 signatures)

## Genesis State Initialization

Before starting a new network, you must initialize the genesis state.

### Step 1: Configure Validators

Create or edit `config/validators.json`:

```json
{
  "validators": [
    {
      "node_id": "node_1",
      "stake": 10000,
      "initial_balance": 0
    },
    {
      "node_id": "node_2",
      "stake": 10000,
      "initial_balance": 0
    },
    {
      "node_id": "node_3",
      "stake": 10000,
      "initial_balance": 0
    },
    {
      "node_id": "node_4",
      "stake": 10000,
      "initial_balance": 0
    }
  ]
}
```

### Step 2: Initialize Genesis State

Run the genesis initialization script:

```bash
python scripts/init_genesis_state.py --validators config/validators.json --output data/genesis_state.json
```

This will:
- Create the genesis block
- Initialize validator stakes
- Set up the initial Merkle tree state
- Save the genesis configuration

### Step 3: Verify Genesis State

Check that the genesis state was created successfully:

```bash
cat data/genesis_state.json
```

You should see the genesis block hash and validator configurations.

## Starting Validator Nodes

### Option 1: Start with Configuration File

Create a node configuration file (e.g., `config/node_1.json`):

```json
{
  "node_id": "node_1",
  "stake": 10000,
  "network": {
    "listen_port": 8001,
    "bootstrap_peers": [
      {"node_id": "node_2", "address": "localhost:8002"},
      {"node_id": "node_3", "address": "localhost:8003"},
      {"node_id": "node_4", "address": "localhost:8004"}
    ]
  },
  "consensus": {
    "timeout": 10.0,
    "view_change_timeout": 5.0
  }
}
```

Start the node:

```bash
python scripts/start_validator.py --node-id node_1 --config config/node_1.json --genesis data/genesis_state.json
```

### Option 2: Start with Command-Line Arguments

```bash
python scripts/start_validator.py --node-id node_1 --stake 10000 --genesis data/genesis_state.json
```

### Starting Multiple Nodes

To run a local network, start multiple nodes in separate terminals:

**Terminal 1:**
```bash
python scripts/start_validator.py --node-id node_1 --stake 10000
```

**Terminal 2:**
```bash
python scripts/start_validator.py --node-id node_2 --stake 10000
```

**Terminal 3:**
```bash
python scripts/start_validator.py --node-id node_3 --stake 10000
```

**Terminal 4:**
```bash
python scripts/start_validator.py --node-id node_4 --stake 10000
```

### Verifying Node Status

Once a node is running, you should see output like:

```
Validator node node_1 is now running
Node status:
  Node ID: node_1
  Stake: 10000
  Connected peers: 3
  Is leader: True
  Current view: 0
  Current sequence: 0
```

## Joining an Existing Network

To join an existing consensus network as a new validator:

### Step 1: Discover Bootstrap Peers

Get the addresses of existing nodes in the network. You need at least one bootstrap peer.

### Step 2: Join the Network

```bash
python scripts/join_network.py \
  --node-id node_5 \
  --stake 10000 \
  --bootstrap node_1:8001 \
  --bootstrap node_2:8002 \
  --save-config config/node_5.json
```

This will:
- Validate your stake meets the minimum requirement
- Discover peers in the network
- Synchronize state from existing nodes
- Create a validator node configuration

### Step 3: Start Participating in Consensus

After joining, start your validator node:

```bash
python scripts/start_validator.py --node-id node_5 --config config/node_5.json
```

## Monitoring the Network

### Real-Time Dashboard

Start the monitoring dashboard to view network health:

```bash
python scripts/monitor_network.py --nodes node_1,node_2,node_3,node_4
```

The dashboard displays:
- **Network Health**: Active nodes, consensus status, Byzantine fault tolerance
- **Consensus Latency**: Average, min, max consensus times with graph
- **Proof Throughput**: Proofs processed per second
- **Validator Leaderboard**: Performance ranking by rounds participated
- **Mempool Status**: Pending proofs and processing rate

### Dashboard Output Example

```
================================================================================
                    PROOF-OF-PROOF CONSENSUS NETWORK MONITOR
================================================================================
Timestamp: 2026-02-10 14:30:45
Monitoring 4 nodes
================================================================================

📊 NETWORK HEALTH
--------------------------------------------------------------------------------
  Status: 🟢 HEALTHY
  Active Nodes: 4/4
  Total Consensus Rounds: 127
  Byzantine Fault Tolerance: Can tolerate 1 faulty nodes (33% of 4)

⏱️  CONSENSUS LATENCY
--------------------------------------------------------------------------------
  Average: 2.345s
  Minimum: 1.892s
  Maximum: 3.567s

📈 PROOF THROUGHPUT
--------------------------------------------------------------------------------
  Total Proofs Processed: 635
  Current Throughput: 5.23 proofs/second
  Average Throughput: 4.87 proofs/second

🏆 VALIDATOR PERFORMANCE LEADERBOARD
--------------------------------------------------------------------------------
  Rank   Node ID         Rounds     Accuracy    Rewards   
  ------------------------------------------------------------------------
  🥇 1   node_1          35         100.0%      350.00    
  🥈 2   node_2          33         100.0%      330.00    
  🥉 3   node_3          31         98.5%       310.00    
     4   node_4          28         100.0%      280.00    
```

## Testnet Deployment

For testing at scale, deploy a 100-node testnet:

### Quick Testnet (1 hour)

```bash
python scripts/deploy_testnet.py --nodes 100 --duration 1 --output data/testnet_1h.json
```

### Full Testnet (24 hours)

```bash
python scripts/deploy_testnet.py --nodes 100 --duration 24 --output data/testnet_24h.json
```

### Custom Testnet

```bash
python scripts/deploy_testnet.py \
  --nodes 50 \
  --duration 12 \
  --stake 5000 \
  --output data/testnet_custom.json
```

### Testnet Report

After the testnet completes, a detailed report is generated:

```json
{
  "deployment": {
    "num_nodes": 100,
    "stake_per_node": 10000,
    "duration_hours": 24.0
  },
  "metrics": {
    "consensus_rounds_completed": 8640,
    "total_proofs_processed": 43200,
    "average_consensus_time": 2.456,
    "proof_throughput": 0.5,
    "node_failures": 0,
    "view_changes": 3
  },
  "stability": {
    "uptime_percentage": 100.0,
    "consensus_success_rate": 100.0,
    "network_health": "HEALTHY"
  },
  "issues": [
    "No issues detected"
  ]
}
```

## Troubleshooting

### Node Won't Start

**Problem**: Node fails to start with "Insufficient stake" error

**Solution**: Ensure your stake meets the minimum requirement (default: 1000 tokens)

```bash
python scripts/start_validator.py --node-id node_1 --stake 10000
```

### Can't Connect to Peers

**Problem**: Node shows "Connected peers: 0"

**Solution**: 
1. Verify bootstrap peer addresses are correct
2. Ensure other nodes are running
3. Check network connectivity

### Consensus Timeout

**Problem**: Frequent "Consensus timeout, initiating view change" messages

**Solution**:
1. Check network latency between nodes
2. Increase consensus timeout in configuration:

```json
{
  "consensus": {
    "timeout": 20.0
  }
}
```

### Low Verification Accuracy

**Problem**: Node shows verification accuracy below 95%

**Solution**:
1. Check that Z3 solver is installed correctly
2. Verify proof blocks are valid
3. Review node logs for verification errors

### State Synchronization Failed

**Problem**: New node can't sync state when joining network

**Solution**:
1. Ensure at least one bootstrap peer is online
2. Verify network connectivity
3. Try syncing from a different peer

### High Memory Usage

**Problem**: Node consumes excessive memory

**Solution**:
1. Reduce mempool size
2. Limit proof block size
3. Enable state pruning (if available)

## Production Deployment Checklist

Before deploying to production:

- [ ] Genesis state initialized and backed up
- [ ] All validator nodes configured with correct stakes
- [ ] Network connectivity tested between all nodes
- [ ] Monitoring dashboard configured and accessible
- [ ] Backup and recovery procedures documented
- [ ] Security audit completed
- [ ] Performance benchmarks validated
- [ ] Disaster recovery plan in place
- [ ] Node operator training completed
- [ ] 24/7 monitoring and alerting configured

## Security Considerations

### Stake Management

- Keep validator stakes secure
- Use hardware wallets for production deployments
- Implement multi-signature requirements for stake changes

### Network Security

- Use TLS/SSL for P2P communication in production
- Implement firewall rules to restrict access
- Monitor for suspicious activity

### Key Management

- Rotate signing keys regularly
- Store private keys in secure hardware modules
- Implement key backup and recovery procedures

## Performance Tuning

### Consensus Timeout

Adjust based on network latency:
- Low latency (<50ms): 5-10 seconds
- Medium latency (50-200ms): 10-15 seconds
- High latency (>200ms): 15-30 seconds

### Proof Block Size

Balance throughput vs. verification time:
- Small blocks (5-10 proofs): Lower latency, higher overhead
- Medium blocks (10-50 proofs): Balanced performance
- Large blocks (50-100 proofs): Higher throughput, higher latency

### Mempool Configuration

Tune mempool size based on load:
- Light load: 100-500 pending proofs
- Medium load: 500-2000 pending proofs
- Heavy load: 2000-10000 pending proofs

## Support

For additional help:
- Review the [Consensus Protocol Documentation](CONSENSUS_PROTOCOL.md)
- Check the [Node Operator Guide](NODE_OPERATOR_GUIDE.md)
- Consult the [API Reference](API_REFERENCE.md)

## Next Steps

After successful deployment:
1. Monitor network health regularly
2. Participate in consensus rounds
3. Track validator performance
4. Optimize node configuration
5. Plan for scaling to more nodes
