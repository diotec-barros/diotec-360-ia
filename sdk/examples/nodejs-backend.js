/**
 * DIOTEC 360 SDK - Node.js Backend Example
 * 
 * Express.js API with DIOTEC 360 verification
 */

const express = require('express');
const { createDiotec360SDK } = require('@diotec360/sdk');

const app = express();
app.use(express.json());

// Initialize DIOTEC 360 SDK
const diotec = createDiotec360SDK({
  apiKey: process.env.DIOTEC360_API_KEY || 'diotec_test_key',
  baseUrl: process.env.DIOTEC360_URL || 'http://localhost:8000'
});

// Simulated database
const accounts = new Map([
  ['ACC001', { name: 'João Silva', balance: 50000 }],
  ['ACC002', { name: 'Maria Santos', balance: 30000 }]
]);

/**
 * POST /api/transfer
 * Process a verified bank transfer
 */
app.post('/api/transfer', async (req, res) => {
  const { from, to, amount } = req.body;

  // Validate input
  if (!from || !to || !amount) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const fromAccount = accounts.get(from);
  if (!fromAccount) {
    return res.status(404).json({ error: 'Source account not found' });
  }

  try {
    // Verify with DIOTEC 360
    const verification = await diotec.verifyTransfer({
      from,
      to,
      amount,
      currency: 'AOA',
      balance: fromAccount.balance
    });

    if (!verification.verified) {
      return res.status(400).json({
        error: 'Verification failed',
        details: verification.error
      });
    }

    // Execute transfer (only if verified)
    fromAccount.balance -= amount;
    const toAccount = accounts.get(to);
    if (toAccount) {
      toAccount.balance += amount;
    }

    res.json({
      success: true,
      merkleProof: verification.merkleProof,
      certificateUrl: verification.certificateUrl,
      newBalance: fromAccount.balance
    });

  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
});

/**
 * GET /api/balance/:accountId
 * Get account balance
 */
app.get('/api/balance/:accountId', (req, res) => {
  const account = accounts.get(req.params.accountId);
  if (!account) {
    return res.status(404).json({ error: 'Account not found' });
  }
  res.json({ balance: account.balance });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`🏛️ DIOTEC 360 Banking API running on port ${PORT}`);
  console.log(`🛡️ Protected by mathematical proofs`);
});
