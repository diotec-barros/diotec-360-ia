# 🚀 DIOTEC 360 SDK - Quick Start

Get up and running in 5 minutes.

## Step 1: Install

```bash
npm install @diotec360/sdk
```

## Step 2: Initialize

```javascript
import { createDiotec360SDK } from '@diotec360/sdk';

const sdk = createDiotec360SDK({
  apiKey: 'your_api_key_here'
});
```

## Step 3: Verify

```javascript
const result = await sdk.verifyTransfer({
  from: 'account_123',
  to: 'account_456',
  amount: 1000,
  currency: 'AOA',
  balance: 5000
});

if (result.verified) {
  console.log('✅ Verified!', result.merkleProof);
} else {
  console.error('❌ Failed:', result.error);
}
```

## That's It!

Your app now has mathematical proof verification.

---

## 🎓 Next Steps

- Read the [Integration Guide](./INTEGRATION_GUIDE.md)
- Explore [Examples](./examples/)
- Get your [API Key](https://diotec360.com/signup)

---

🏛️ **DIOTEC 360 IA** - The TCP/IP of Honesty
