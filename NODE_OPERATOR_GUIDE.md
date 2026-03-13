# Diotec360 validator Node Operator Guide

## Introduction

This guide explains how to run a validator node in the Aethel Proof-of-Proof consensus network. As a validator, you'll earn rewards by verifying Z3 proofs and participating in Byzantine consensus.

**Prerequisites**:
- Python 3.9 or higher
- 4+ CPU cores (recommended for parallel verification)
- 8GB+ RAM
- 100GB+ disk space
- Stable internet connection (< 500ms latency recommended)
- Minimum 1,000 AETHEL tokens for staking

## Quick Start

### 1. Install Aethel

```bash
# Clone the repository
git clone https://github.com/your-org/aethel.git
cd aethel

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from aethel.consensus import ConsensusEngine; print('✓ Aethel installed')"
```

### 2. Generate Node Identity

```bash
# Generate Ed25519 keypair for your node
python scripts/generate_node_identity.py

# This creates:
# - ~/.aethel/node_id.txt (your node ID)
# - ~/.aethel/private_key.pem (keep this secret!)
# - ~/.aethel/public_key.pem (share with network)
```

**⚠️ IMPORTANT**: Back up your `private_key.pem` file securely. If you lose it, you lose access to your staked tokens!

### 3. Configure Your Node

Create a configuration file at `~/.aethel/config.yaml`:

```yaml
# Node Configuration
node:
  id: "your-node-id-here"  # From node_id.txt
  listen_port: 9000
  max_peers: 50

# Staking Configuration
staking:
  initial_stake: 1000  # Minimum required
  auto_restake_rewards: true

# Network Configuration
network:
  bootstrap_peers:
    - "/ip4/bootstrap1.aethel.network/tcp/9000/p2p/QmBootstrap1"
    - "/ip4/bootstrap2.aethel.network/tcp/9000/p2p/QmBootstrap2"
  
# Consensus Configuration
consensus:
  timeout_seconds: 10
  max_proof_block_size: 10
  parallel_verification: true
  max_workers: 4

# Monitoring Configuration
monitoring:
  enabled: true
  metrics_port: 9090
  log_level: "INFO"
```

### 4. Stake Your Tokens

Before participating in consensus, you must stake tokens:

```bash
# Stake 1,000 tokens (minimum required)
python scripts/stake_tokens.py --amount 1000

# Check your stake
python scripts/check_stake.py
# Output: Current stake: 1,000 AETHEL
```

### 5. Start Your Validator Node

```bash
# Start the validator node
python scripts/start_validator.py

# Or run as a background service
python scripts/start_validator.py --daemon

# Check node status
python scripts/node_status.py
```

You should see output like:

```
✓ Diotec360 validator Node Started
  Node ID: node_abc123
  Stake: 1,000 AETHEL
  Peers: 12 connected
  Status: Syncing state...
  
Waiting for consensus participation...
```

## Staking Requirements

### Minimum Stake

To participate in consensus, you must stake at least **1,000 AETHEL tokens**. This requirement:
- Prevents Sybil attacks (one entity controlling many nodes)
- Ensures validators have "skin in the game"
- Enables slashing penalties for malicious behavior

### Staking Process

1. **Acquire Tokens**: Obtain AETHEL tokens through:
   - Mining (verifying proofs)
   - Purchasing from exchanges
   - Receiving from other users

2. **Lock Tokens**: Stake tokens to your validator:
   ```bash
   python scripts/stake_tokens.py --amount 1000
   ```

3. **Verify Stake**: Confirm your stake is registered:
   ```bash
   python scripts/check_stake.py
   ```

4. **Start Validating**: Once staked, your node can participate in consensus

### Unstaking

To withdraw your stake:

```bash
# Initiate unstaking (7-day waiting period)
python scripts/unstake_tokens.py --amount 500

# Check unstaking status
python scripts/unstaking_status.py
# Output: Unstaking 500 AETHEL, available in 6 days

# Withdraw after waiting period
python scripts/withdraw_unstaked.py
```

**Note**: The 7-day waiting period prevents "nothing at stake" attacks where validators could quickly unstake and attack the network.

### Slashing Risks

Your stake can be reduced (slashed) if you:

| Violation | Penalty | How to Avoid |
|-----------|---------|--------------|
| **Invalid Verification** | 5% stake | Ensure your node has correct AethelJudge version |
| **Double-Signing** | 20% stake | Never run multiple nodes with same identity |
| **Offline** | 0% | No penalty for being offline (you just miss rewards) |

**Best Practices**:
- Keep your node software up to date
- Monitor your node's verification accuracy (should be > 95%)
- Never share your private key
- Never run duplicate nodes with the same identity

## Earning Rewards

### Reward Calculation

Rewards are calculated based on:

```
base_reward = 10 AETHEL per proof block
difficulty_multiplier = total_difficulty / 1,000,000
total_reward = base_reward × difficulty_multiplier
your_reward = total_reward / participating_nodes
```

**Example**:
- Proof block with difficulty = 5,000,000
- 10 nodes participate in consensus
- difficulty_multiplier = 5
- total_reward = 10 × 5 = 50 AETHEL
- your_reward = 50 / 10 = **5 AETHEL**

### Maximizing Rewards

To maximize your earnings:

1. **High Uptime**: Be online when consensus rounds occur
2. **Fast Verification**: Use powerful hardware for faster proof verification
3. **Low Latency**: Ensure good network connectivity (< 500ms latency)
4. **Correct Verification**: Maintain > 95% verification accuracy
5. **Participate Actively**: Don't miss consensus rounds

### Reward Distribution

Rewards are distributed automatically:
- **Timing**: Within 10 seconds of consensus finalization
- **Method**: Direct balance update in state store
- **Tracking**: View your rewards in the monitoring dashboard

```bash
# Check your rewards
python scripts/check_rewards.py

# Output:
# Total Rewards Earned: 1,250 AETHEL
# Last 24 Hours: 45 AETHEL
# Average per Round: 2.5 AETHEL
```

### Auto-Restaking

Enable auto-restaking to compound your rewards:

```yaml
# In config.yaml
staking:
  auto_restake_rewards: true
  restake_threshold: 100  # Restake when rewards reach 100 AETHEL
```

This automatically adds your rewards to your stake, increasing your influence in consensus.

## Monitoring Your Node

### Metrics Dashboard

Access your node's metrics at `http://localhost:9090/metrics`:

```
# Consensus Metrics
consensus_rounds_total: 1,234
consensus_duration_avg_ms: 8,500
consensus_success_rate: 0.99

# Verification Metrics
verifications_total: 12,340
verification_accuracy: 0.98
verification_time_avg_ms: 150

# Reward Metrics
rewards_earned_total: 1,250
rewards_last_24h: 45
rewards_per_round_avg: 2.5

# Network Metrics
peers_connected: 12
network_latency_avg_ms: 120
messages_sent_total: 45,678
messages_received_total: 46,123
```

### Health Checks

Monitor your node's health:

```bash
# Check node health
python scripts/health_check.py

# Output:
# ✓ Node is running
# ✓ Stake is sufficient (1,000 AETHEL)
# ✓ Peers connected (12/50)
# ✓ State is synced
# ✓ Verification accuracy: 98%
# ⚠ Network latency high: 550ms (recommended < 500ms)
```

### Alerts

Configure alerts for critical issues:

```yaml
# In config.yaml
monitoring:
  alerts:
    - type: "low_accuracy"
      threshold: 0.95
      action: "email"
      email: "operator@example.com"
    
    - type: "high_latency"
      threshold: 500  # ms
      action: "log"
    
    - type: "slashing_event"
      action: "email_urgent"
```

### Logs

View node logs:

```bash
# Tail logs in real-time
tail -f ~/.aethel/logs/validator.log

# Search for errors
grep ERROR ~/.aethel/logs/validator.log

# View consensus rounds
grep "Consensus finalized" ~/.aethel/logs/validator.log
```

## Troubleshooting

### Node Won't Start

**Problem**: Node fails to start with error "Address already in use"

**Solution**:
```bash
# Check if another process is using port 9000
lsof -i :9000

# Kill the process or change port in config.yaml
node:
  listen_port: 9001
```

### Can't Connect to Peers

**Problem**: Node shows "0 peers connected"

**Solution**:
1. Check firewall settings:
   ```bash
   # Allow incoming connections on port 9000
   sudo ufw allow 9000/tcp
   ```

2. Verify bootstrap peers are reachable:
   ```bash
   ping bootstrap1.aethel.network
   ```

3. Check your internet connection

### Low Verification Accuracy

**Problem**: Verification accuracy < 95%

**Solution**:
1. Update to latest Diotec360 version:
   ```bash
   git pull origin main
   pip install -r requirements.txt --upgrade
   ```

2. Check AethelJudge is working:
   ```bash
   python -c "from aethel.core.judge import AethelJudge; j = AethelJudge(); print('✓ Judge OK')"
   ```

3. Review error logs:
   ```bash
   grep "Verification failed" ~/.aethel/logs/validator.log
   ```

### High Network Latency

**Problem**: Network latency > 500ms causing timeouts

**Solution**:
1. Check your internet connection speed
2. Increase consensus timeout in config:
   ```yaml
   consensus:
     timeout_seconds: 15  # Increase from 10
   ```

3. Consider using a VPS closer to other validators

### Slashing Event

**Problem**: Your stake was slashed

**Solution**:
1. Check the slashing reason:
   ```bash
   python scripts/check_slashing_events.py
   ```

2. Review the evidence:
   ```bash
   python scripts/view_slashing_evidence.py --event-id <event_id>
   ```

3. Fix the issue:
   - **Invalid Verification**: Update your software
   - **Double-Signing**: Ensure you're not running duplicate nodes

4. Monitor your node closely to prevent future slashing

### State Sync Issues

**Problem**: Node stuck on "Syncing state..."

**Solution**:
1. Check peer connectivity:
   ```bash
   python scripts/list_peers.py
   ```

2. Manually trigger state sync:
   ```bash
   python scripts/force_state_sync.py
   ```

3. If still stuck, reset and resync:
   ```bash
   python scripts/reset_state.py
   python scripts/start_validator.py
   ```

## Security Best Practices

### Protect Your Private Key

Your private key is the most critical asset:

1. **Never share it**: Not even with Aethel support
2. **Back it up securely**: Use encrypted storage
3. **Use hardware security**: Consider HSM for production
4. **Rotate regularly**: Generate new keys periodically

```bash
# Backup your key (encrypted)
gpg --encrypt ~/.aethel/private_key.pem > private_key.pem.gpg

# Store backup in multiple secure locations
```

### Firewall Configuration

Secure your node with proper firewall rules:

```bash
# Allow only necessary ports
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 9000/tcp  # P2P network
sudo ufw allow 9090/tcp  # Metrics (restrict to trusted IPs)
sudo ufw enable
```

### DDoS Protection

Protect against denial-of-service attacks:

```yaml
# In config.yaml
network:
  rate_limiting:
    enabled: true
    max_messages_per_second: 100
    max_connections_per_ip: 5
```

### Monitoring for Attacks

Watch for suspicious activity:

```bash
# Monitor for unusual message patterns
grep "Rate limit exceeded" ~/.aethel/logs/validator.log

# Check for Byzantine behavior detection
grep "Byzantine incident" ~/.aethel/logs/validator.log
```

## Performance Optimization

### Hardware Recommendations

For optimal performance:

| Component | Minimum | Recommended | High-Performance |
|-----------|---------|-------------|------------------|
| **CPU** | 2 cores | 4 cores | 8+ cores |
| **RAM** | 4GB | 8GB | 16GB+ |
| **Disk** | 50GB SSD | 100GB SSD | 500GB NVMe |
| **Network** | 10 Mbps | 100 Mbps | 1 Gbps |

### Parallel Verification

Enable parallel proof verification:

```yaml
# In config.yaml
consensus:
  parallel_verification: true
  max_workers: 4  # Match your CPU core count
```

This can provide 4x speedup on multi-core systems.

### Merkle Tree Caching

Optimize state access with caching:

```yaml
# In config.yaml
state:
  cache_enabled: true
  cache_size_mb: 512
  cache_ttl_seconds: 300
```

### Network Optimization

Reduce network overhead:

```yaml
# In config.yaml
network:
  message_batching:
    enabled: true
    batch_size: 10
    batch_timeout_ms: 100
  
  compression:
    enabled: true
    algorithm: "zstd"
```

## Upgrading Your Node

### Software Updates

Keep your node up to date:

```bash
# Check for updates
python scripts/check_updates.py

# Upgrade to latest version
git pull origin main
pip install -r requirements.txt --upgrade

# Restart node
python scripts/restart_validator.py
```

### Backward Compatibility

Aethel maintains backward compatibility:
- Old nodes can participate with new nodes
- State format is versioned
- Consensus protocol is versioned

### Migration Guide

When major updates require migration:

1. **Backup your state**:
   ```bash
   python scripts/backup_state.py
   ```

2. **Stop your node**:
   ```bash
   python scripts/stop_validator.py
   ```

3. **Run migration script**:
   ```bash
   python scripts/migrate_to_v3.py
   ```

4. **Restart your node**:
   ```bash
   python scripts/start_validator.py
   ```

## Advanced Topics

### Running Multiple Validators

You can run multiple validators with different identities:

```bash
# Generate second identity
python scripts/generate_node_identity.py --output ~/.aethel/node2/

# Start second validator
python scripts/start_validator.py --config ~/.aethel/node2/config.yaml
```

**⚠️ WARNING**: Never run multiple validators with the same identity! This will result in double-signing and 20% stake slash.

### Custom Proof Verification

Implement custom verification logic:

```python
from aethel.consensus import ProofVerifier

class CustomProofVerifier(ProofVerifier):
    def verify_proof(self, proof):
        # Add custom validation logic
        if not self.custom_check(proof):
            return VerificationResult(valid=False, error="Custom check failed")
        
        # Call parent verification
        return super().verify_proof(proof)
```

### Monitoring Integration

Integrate with external monitoring systems:

```yaml
# In config.yaml
monitoring:
  prometheus:
    enabled: true
    port: 9090
  
  grafana:
    enabled: true
    dashboard_url: "http://localhost:3000"
  
  alertmanager:
    enabled: true
    webhook_url: "http://localhost:9093/api/v1/alerts"
```

### High Availability Setup

Run validators in HA configuration:

1. **Primary-Backup**: Run backup node that takes over if primary fails
2. **Load Balancing**: Distribute verification across multiple nodes
3. **Geographic Distribution**: Run nodes in multiple regions

**Note**: Ensure only one node with each identity participates in consensus at a time to avoid double-signing.

## Support and Community

### Getting Help

- **Documentation**: https://docs.aethel.network
- **Discord**: https://discord.gg/aethel
- **Forum**: https://forum.aethel.network
- **GitHub Issues**: https://github.com/your-org/diotec360/issues

### Reporting Issues

When reporting issues, include:

```bash
# Generate diagnostic report
python scripts/generate_diagnostic_report.py

# This creates: ~/.aethel/diagnostic_report.txt
# Share this file when asking for help
```

### Contributing

Help improve Aethel:
- Report bugs
- Suggest features
- Submit pull requests
- Write documentation
- Help other operators

See `CONTRIBUTING.md` for guidelines.

## Conclusion

Running an Diotec360 validator node is a rewarding way to participate in the network while earning tokens. By following this guide, you'll:

- ✅ Set up a secure validator node
- ✅ Stake tokens and participate in consensus
- ✅ Earn rewards for verifying proofs
- ✅ Monitor your node's performance
- ✅ Troubleshoot common issues

Welcome to the Diotec360 validator community! 🚀

## Appendix: Command Reference

### Node Management

```bash
# Start validator
python scripts/start_validator.py

# Stop validator
python scripts/stop_validator.py

# Restart validator
python scripts/restart_validator.py

# Check status
python scripts/node_status.py

# View logs
tail -f ~/.aethel/logs/validator.log
```

### Staking Commands

```bash
# Stake tokens
python scripts/stake_tokens.py --amount <amount>

# Check stake
python scripts/check_stake.py

# Unstake tokens
python scripts/unstake_tokens.py --amount <amount>

# Withdraw unstaked
python scripts/withdraw_unstaked.py
```

### Monitoring Commands

```bash
# Health check
python scripts/health_check.py

# Check rewards
python scripts/check_rewards.py

# View metrics
curl http://localhost:9090/metrics

# Generate diagnostic report
python scripts/generate_diagnostic_report.py
```

### Maintenance Commands

```bash
# Backup state
python scripts/backup_state.py

# Restore state
python scripts/restore_state.py --backup <backup_file>

# Force state sync
python scripts/force_state_sync.py

# Reset state
python scripts/reset_state.py
```
