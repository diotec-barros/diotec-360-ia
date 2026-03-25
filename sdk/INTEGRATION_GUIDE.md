# 🏛️ DIOTEC 360 SDK - Guia de Integração Completo

**Versão:** 1.0.0  
**Data:** 23 de Março de 2026

---

## 🎯 O Que é o DIOTEC 360 SDK?

O SDK permite que qualquer aplicação (web, mobile, backend) integre **verificação matemática** de operações críticas usando o **Z3 Theorem Prover**.

**Casos de Uso:**
- 🏦 Banking: Transferências verificadas
- 🤝 Escrow: Transações multi-parte
- 🗳️ Voting: Governança digital
- 📦 Logistics: Confirmação de entrega
- 🏥 Healthcare: Prescrições médicas

---

## 📦 Instalação

### NPM
```bash
npm install @diotec360/sdk
```

### Yarn
```bash
yarn add @diotec360/sdk
```

### CDN (Browser)
```html
<script src="https://cdn.diotec360.com/sdk/v1/diotec360-sdk.min.js"></script>
<script>
  const sdk = window.createDiotec360SDK({
    apiKey: 'your_api_key'
  });
</script>
```

---

## 🔑 Obter API Key

### Desenvolvimento (Sandbox)
```javascript
const sdk = createDiotec360SDK({
  apiKey: 'diotec_test_key',
  baseUrl: 'http://localhost:8000'
});
```

### Produção
1. Acesse: https://diotec360.com/signup
2. Crie sua conta
3. Copie sua API key
4. Configure no seu `.env`:

```env
DIOTEC360_API_KEY=diotec_prod_xxxxxxxxxxxxx
```

---

## 💻 Exemplos de Integração

### 1. React/Next.js

```typescript
import { createDiotec360SDK } from '@diotec360/sdk';

const sdk = createDiotec360SDK({
  apiKey: process.env.NEXT_PUBLIC_DIOTEC360_API_KEY!
});

async function handleTransfer(from: string, to: string, amount: number) {
  const result = await sdk.verifyTransfer({
    from,
    to,
    amount,
    currency: 'AOA',
    balance: 50000
  });

  if (result.verified) {
    // Execute transfer
    await executeTransfer(from, to, amount);
    return result.merkleProof;
  } else {
    throw new Error(result.error);
  }
}
```

### 2. Node.js/Express

```javascript
const express = require('express');
const { createDiotec360SDK } = require('@diotec360/sdk');

const app = express();
const sdk = createDiotec360SDK({
  apiKey: process.env.DIOTEC360_API_KEY
});

app.post('/api/transfer', async (req, res) => {
  const { from, to, amount, balance } = req.body;
  
  const verification = await sdk.verifyTransfer({
    from, to, amount,
    currency: 'AOA',
    balance
  });

  if (verification.verified) {
    // Execute transfer in your database
    res.json({ success: true, proof: verification.merkleProof });
  } else {
    res.status(400).json({ error: verification.error });
  }
});
```

### 3. Python/Django

```python
import requests

class Diotec360Client:
    def __init__(self, api_key, base_url='https://api.diotec360.com'):
        self.api_key = api_key
        self.base_url = base_url
    
    def verify_transfer(self, from_acc, to_acc, amount, currency, balance):
        response = requests.post(
            f'{self.base_url}/api/sdk/verify',
            json={
                'intent': 'transfer',
                'params': {
                    'from': from_acc,
                    'to': to_acc,
                    'amount': amount,
                    'currency': currency,
                    'balance': balance
                }
            },
            headers={'X-API-Key': self.api_key}
        )
        return response.json()

# Usage
sdk = Diotec360Client(api_key=os.getenv('DIOTEC360_API_KEY'))
result = sdk.verify_transfer('ACC001', 'ACC002', 1000, 'AOA', 5000)
```

---

## 🎯 Intents Disponíveis

### Financial Intents

#### Transfer
```javascript
await sdk.verifyTransfer({
  from: 'account_id',
  to: 'account_id',
  amount: 1000,
  currency: 'AOA',
  balance: 5000
});
```

#### Escrow
```javascript
await sdk.verifyEscrow({
  buyer: 'buyer_id',
  seller: 'seller_id',
  arbiter: 'arbiter_id',
  amount: 10000,
  currency: 'AOA'
});
```

#### Multisig
```javascript
await sdk.verifyMultisig({
  signers: ['signer1', 'signer2', 'signer3'],
  threshold: 2,
  signed: ['signer1', 'signer2']
});
```

#### Loan
```javascript
await sdk.verifyLoan({
  principal: 100000,
  rate: 0.05,
  term: 12,
  currency: 'AOA'
});
```

### Governance Intents

#### Vote
```javascript
await sdk.verifyVote({
  voter_id: 'voter_123',
  proposal_id: 'prop_456',
  vote: 'yes',
  voted_before: false
});
```

### Logistics Intents

#### Delivery
```javascript
await sdk.verifyDelivery({
  package_id: 'PKG123',
  gps_lat: -8.8383,
  gps_lon: 13.2344,
  target_lat: -8.8400,
  target_lon: 13.2350,
  tolerance_meters: 100
});
```

---

## 🛡️ Response Format

### Success Response
```json
{
  "verified": true,
  "merkleProof": "0x1a2b3c...",
  "certificateUrl": "https://diotec360.com/cert/abc123",
  "z3Proof": "...",
  "timestamp": 1711234567890
}
```

### Error Response
```json
{
  "verified": false,
  "error": "Insufficient balance: 1000 > 500"
}
```

---

## 🔧 Advanced Configuration

```javascript
const sdk = createDiotec360SDK({
  apiKey: 'your_key',
  baseUrl: 'https://api.diotec360.com',
  timeout: 30000 // 30 seconds
});
```

---

## 📊 Rate Limits

| Plan | Requests/min | Requests/day |
|------|--------------|--------------|
| Free | 10 | 1,000 |
| Starter | 100 | 10,000 |
| Pro | 1,000 | 100,000 |
| Enterprise | Unlimited | Unlimited |

---

## 🧪 Testing

```bash
# Run SDK tests
npm test

# Run example
node examples/banking-app.js
```

---

## 🌐 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sdk/health` | GET | Health check |
| `/api/sdk/intents` | GET | List intents |
| `/api/sdk/verify` | POST | Verify intent |

---

## 🎓 Learn More

- 📖 Full Docs: https://diotec360.com/docs
- 🎥 Video Tutorial: https://youtube.com/diotec360
- 💬 Discord: https://discord.gg/diotec360
- 📧 Email: contact@diotec360.com

---

🏛️ **DIOTEC 360 IA** - The TCP/IP of Honesty  
⚖️ **Sovereign SDK** - Every App, Everywhere  
🛡️ **"DIOTEC Inside"** - Integrity as a Service
