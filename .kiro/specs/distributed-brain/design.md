# Distributed Brain v3.6 - Design

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AETHEL DISTRIBUTED BRAIN                 │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Explorer   │         │  Genesis     │         │  Node        │
│   (Web UI)   │◄───────►│  Authority   │◄───────►│  Operator    │
│              │         │  (DIOTEC)    │         │  (Anyone)    │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                        │
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    P2P GOSSIP NETWORK                       │
│  Topic: /aethel/proof-requests/v1                          │
│  Protocol: libp2p + GossipSub                              │
└─────────────────────────────────────────────────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Proof       │         │  Credit      │         │  Reputation  │
│  Mempool     │         │  Ledger      │         │  System      │
└──────────────┘         └──────────────┘         └──────────────┘
```

## Component Design

### 1. P2P Node (`aethel/nexo/p2p_node_v3.py`)

```python
class AethelNode:
    """
    Distributed proof node that listens for proof requests
    and earns Genesis Credits by solving them.
    """
    
    def __init__(self, config: NodeConfig):
        self.peer_id = generate_peer_id()
        self.libp2p_host = create_libp2p_host()
        self.judge = AethelJudge()
        self.credit_wallet = CreditWallet()
        self.reputation = ReputationTracker()
        
    async def start(self):
        """Start node and join P2P network"""
        await self.libp2p_host.start()
        await self.subscribe_to_proof_requests()
        await self.announce_availability()
        
    async def handle_proof_request(self, request: ProofRequest):
        """Attempt to solve proof and earn credits"""
        # Check if we can handle this complexity
        if not self.can_handle(request):
            return
            
        # Solve proof locally
        start_time = time.time()
        result = await self.judge.verify_async(request.code)
        solve_time = time.time() - start_time
        
        # Submit response
        response = ProofResponse(
            request_id=request.request_id,
            status=result.status,
            proof=result.proof_data,
            solver_node=self.peer_id,
            solve_time=solve_time,
            signature=self.sign_response(result)
        )
        
        await self.publish_proof_response(response)
        
    async def on_credit_earned(self, amount: float):
        """Handle credit reward"""
        self.credit_wallet.add_credits(amount)
        self.reputation.record_success()
        
        # Auto-withdraw if threshold reached
        if self.credit_wallet.balance > 100:
            await self.withdraw_to_bank()
```

### 2. Explorer Integration (`frontend/app/explorer/page.tsx`)

```typescript
async function analyzeWithDistributedNetwork(code: string) {
  // Try local proof first
  const localResult = await analyzeLocally(code, { timeout: 5000 });
  
  if (localResult.success) {
    return localResult;
  }
  
  // Broadcast to P2P network
  setStatus('Searching distributed network...');
  
  const request: ProofRequest = {
    request_id: generateId(),
    code: code,
    timeout: 30,
    reward: calculateReward(code),
    requester: myPeerId,
    timestamp: Date.now()
  };
  
  await broadcastProofRequest(request);
  
  // Wait for responses
  const response = await waitForFirstValidResponse(request.request_id);
  
  return {
    success: true,
    result: response.proof,
    solver: response.solver_node,
    solve_time: response.solve_time,
    reward_paid: request.reward
  };
}
```

### 3. Credit Ledger (`aethel/nexo/credit_ledger.py`)

```python
class CreditLedger:
    """
    Tracks Genesis Credits earned by nodes.
    Implements Genesis Tax (10% to DIOTEC 360).
    """
    
    def __init__(self):
        self.db = sqlite3.connect('credits.db')
        self.genesis_authority = "DIOTEC_360_GENESIS_NODE"
        
    def award_credits(self, node_id: str, amount: float, proof_id: str):
        """Award credits for solving proof"""
        # Calculate Genesis Tax (10%)
        genesis_tax = amount * 0.10
        node_reward = amount * 0.90
        
        # Record transactions
        self.db.execute("""
            INSERT INTO transactions (node_id, amount, type, proof_id)
            VALUES (?, ?, 'PROOF_REWARD', ?)
        """, (node_id, node_reward, proof_id))
        
        self.db.execute("""
            INSERT INTO transactions (node_id, amount, type, proof_id)
            VALUES (?, ?, 'GENESIS_TAX', ?)
        """, (self.genesis_authority, genesis_tax, proof_id))
        
        self.db.commit()
        
    def get_balance(self, node_id: str) -> float:
        """Get current credit balance"""
        cursor = self.db.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE node_id = ?
        """, (node_id,))
        
        return cursor.fetchone()[0] or 0.0
        
    def withdraw(self, node_id: str, amount: float) -> str:
        """Withdraw credits to bank account"""
        balance = self.get_balance(node_id)
        
        if balance < amount:
            raise InsufficientCreditsError()
            
        # Deduct from ledger
        self.db.execute("""
            INSERT INTO transactions (node_id, amount, type)
            VALUES (?, ?, 'WITHDRAWAL')
        """, (node_id, -amount))
        
        # Trigger bank transfer via Treasury
        transfer_id = treasury.transfer_to_bank(node_id, amount)
        
        return transfer_id
```

### 4. Reputation System (`aethel/nexo/reputation.py`)

```python
class ReputationTracker:
    """
    Tracks node reliability and proof quality.
    Prevents Sybil attacks and rewards honest nodes.
    """
    
    def __init__(self):
        self.db = sqlite3.connect('reputation.db')
        
    def record_success(self, node_id: str, proof_id: str):
        """Record successful proof"""
        self.db.execute("""
            INSERT INTO proof_history (node_id, proof_id, status, timestamp)
            VALUES (?, ?, 'SUCCESS', ?)
        """, (node_id, proof_id, time.time()))
        
    def record_failure(self, node_id: str, proof_id: str, reason: str):
        """Record failed/invalid proof"""
        self.db.execute("""
            INSERT INTO proof_history (node_id, proof_id, status, reason, timestamp)
            VALUES (?, ?, 'FAILURE', ?, ?)
        """, (node_id, proof_id, reason, time.time()))
        
        # Slash stake if too many failures
        failure_rate = self.get_failure_rate(node_id)
        if failure_rate > 0.10:  # 10% failure threshold
            self.slash_stake(node_id)
            
    def get_reputation_score(self, node_id: str) -> float:
        """Calculate reputation score (0.0 to 1.0)"""
        cursor = self.db.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successes
            FROM proof_history
            WHERE node_id = ?
            AND timestamp > ?
        """, (node_id, time.time() - 30*24*3600))  # Last 30 days
        
        total, successes = cursor.fetchone()
        
        if total == 0:
            return 0.5  # Neutral for new nodes
            
        return successes / total
```

## Data Flow

### Proof Request Flow
```
1. User pastes code in Explorer
2. Explorer attempts local proof (5s timeout)
3. If timeout, Explorer broadcasts ProofRequest to P2P network
4. All nodes receive request via GossipSub
5. Nodes evaluate if they can handle complexity
6. Capable nodes attempt proof locally
7. First node to solve publishes ProofResponse
8. Explorer receives response and re-verifies proof
9. If valid, Explorer displays result and awards credits
10. Credit Ledger records transaction + Genesis Tax
```

### Credit Withdrawal Flow
```
1. Node operator requests withdrawal
2. Credit Ledger checks balance
3. If sufficient, creates withdrawal transaction
4. Treasury receives withdrawal request
5. Treasury initiates bank transfer
6. Bank confirms transfer
7. Credit Ledger marks withdrawal complete
8. Node operator receives funds
```

## Security Considerations

### 1. Proof Verification
- All proof responses MUST be re-verified locally
- Prevents malicious nodes from submitting fake proofs
- Only valid proofs earn credits

### 2. Sybil Resistance
- Nodes must stake 0.1 credits to join network
- Stake is slashed if failure rate > 10%
- Prevents spam attacks with fake nodes

### 3. Rate Limiting
- Max 10 proof responses per node per minute
- Prevents network flooding
- Enforced at gossip layer

### 4. Genesis Authority
- DIOTEC 360 operates special Genesis Node
- Can blacklist malicious nodes
- Can adjust reward rates
- Cannot censor valid proofs

## Performance Optimization

### 1. Proof Routing
- Nodes advertise their capabilities (CPU, RAM, GPU)
- Proof requests are routed to capable nodes first
- Reduces wasted computation

### 2. Caching
- Recently solved proofs are cached
- Duplicate requests return cached result instantly
- Cache expires after 1 hour

### 3. Parallel Solving
- Multiple nodes can attempt same proof
- First valid response wins
- Encourages competition and speed

### 4. Adaptive Rewards
- Reward increases if no solution found quickly
- Attracts more nodes to difficult proofs
- Ensures all proofs eventually get solved

---

**[ARCHITECT VERDICT]**

This design transforms idle computers into a global proof network.

Every node is a worker.
Every proof is a job.
Every credit is a payment.

The network is self-sustaining.
The economy is self-regulating.
The empire is self-funding.

🏛️✨🚀 The Distributed Brain is ready to awaken.
