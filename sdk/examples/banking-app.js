/**
 * DIOTEC 360 SDK - Banking App Example
 * 
 * This example shows how to integrate DIOTEC 360
 * into a banking application for verified transfers.
 */

const { createDiotec360SDK } = require('@diotec360/sdk');

// Initialize SDK
const diotec = createDiotec360SDK({
  apiKey: process.env.DIOTEC360_API_KEY || 'diotec_test_key',
  baseUrl: process.env.DIOTEC360_URL || 'http://localhost:8000'
});

// Simulated database
const accounts = {
  'ACC001': { name: 'João Silva', balance: 50000 },
  'ACC002': { name: 'Maria Santos', balance: 30000 },
  'ACC003': { name: 'Pedro Costa', balance: 15000 }
};

/**
 * Process a bank transfer with DIOTEC 360 verification
 */
async function processTransfer(fromAccount, toAccount, amount) {
  console.log('\n🏦 Processing Transfer...');
  console.log(`From: ${fromAccount} (${accounts[fromAccount].name})`);
  console.log(`To: ${toAccount} (${accounts[toAccount].name})`);
  console.log(`Amount: ${amount} AOA`);

  try {
    // Step 1: Verify with DIOTEC 360
    console.log('\n🛡️ Verifying with Z3 Theorem Prover...');
    
    const verification = await diotec.verifyTransfer({
      from: fromAccount,
      to: toAccount,
      amount: amount,
      currency: 'AOA',
      balance: accounts[fromAccount].balance
    });

    if (!verification.verified) {
      console.error('❌ Verification FAILED:', verification.error);
      return { success: false, error: verification.error };
    }

    console.log('✅ Verification PASSED!');
    console.log('📜 Merkle Proof:', verification.merkleProof);
    console.log('🔗 Certificate:', verification.certificateUrl);

    // Step 2: Execute the transfer (only if verified)
    accounts[fromAccount].balance -= amount;
    accounts[toAccount].balance += amount;

    console.log('\n💰 Transfer Complete!');
    console.log(`${fromAccount} new balance: ${accounts[fromAccount].balance} AOA`);
    console.log(`${toAccount} new balance: ${accounts[toAccount].balance} AOA`);

    return {
      success: true,
      merkleProof: verification.merkleProof,
      certificateUrl: verification.certificateUrl
    };

  } catch (error) {
    console.error('❌ Transfer Error:', error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Run demo
 */
async function runDemo() {
  console.log('🏛️ DIOTEC 360 IA - Banking App Demo');
  console.log('⚖️ "The TCP/IP of Honesty"\n');

  // Check SDK health
  const health = await diotec.health();
  console.log('✅ SDK Connected:', health);

  // Test 1: Valid transfer
  await processTransfer('ACC001', 'ACC002', 5000);

  // Test 2: Invalid transfer (insufficient funds)
  await processTransfer('ACC003', 'ACC001', 20000);

  // Test 3: Another valid transfer
  await processTransfer('ACC002', 'ACC003', 3000);

  console.log('\n🎯 Demo Complete!');
  console.log('All transfers were mathematically verified by Z3.');
}

// Run if executed directly
if (require.main === module) {
  runDemo().catch(console.error);
}

module.exports = { processTransfer };
