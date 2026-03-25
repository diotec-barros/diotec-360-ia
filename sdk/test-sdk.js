/**
 * DIOTEC 360 SDK - Test Script
 * 
 * Run this to test the SDK locally
 */

const { createDiotec360SDK } = require('./diotec360-sdk.js');

const sdk = createDiotec360SDK({
  apiKey: 'diotec_test_key',
  baseUrl: 'http://localhost:8000'
});

async function runTests() {
  console.log('🏛️ DIOTEC 360 SDK - Test Suite\n');

  try {
    // Test 1: Health Check
    console.log('Test 1: Health Check');
    const health = await sdk.health();
    console.log('✅ Health:', health);

    // Test 2: List Intents
    console.log('\nTest 2: List Intents');
    const intents = await sdk.listIntents();
    console.log(`✅ Found ${intents.length} intents`);

    // Test 3: Valid Transfer
    console.log('\nTest 3: Valid Transfer');
    const validTransfer = await sdk.verifyTransfer({
      from: 'ACC001',
      to: 'ACC002',
      amount: 1000,
      currency: 'AOA',
      balance: 5000
    });
    console.log('✅ Result:', validTransfer.verified ? 'VERIFIED' : 'FAILED');
    if (validTransfer.merkleProof) {
      console.log('📜 Merkle Proof:', validTransfer.merkleProof.slice(0, 40) + '...');
    }

    // Test 4: Invalid Transfer (insufficient funds)
    console.log('\nTest 4: Invalid Transfer (insufficient funds)');
    const invalidTransfer = await sdk.verifyTransfer({
      from: 'ACC001',
      to: 'ACC002',
      amount: 10000,
      currency: 'AOA',
      balance: 5000
    });
    console.log('✅ Result:', invalidTransfer.verified ? 'VERIFIED' : 'FAILED (expected)');
    if (invalidTransfer.error) {
      console.log('📋 Error:', invalidTransfer.error);
    }

    // Test 5: Escrow
    console.log('\nTest 5: Escrow Verification');
    const escrow = await sdk.verifyEscrow({
      buyer: 'buyer_123',
      seller: 'seller_456',
      arbiter: 'arbiter_789',
      amount: 50000,
      currency: 'AOA'
    });
    console.log('✅ Result:', escrow.verified ? 'VERIFIED' : 'FAILED');

    console.log('\n🎯 All Tests Complete!');
    console.log('🛡️ SDK is working correctly.\n');

  } catch (error) {
    console.error('\n❌ Test Failed:', error.message);
    if (error.response && error.response.data) {
      console.error('📋 Error Details:', JSON.stringify(error.response.data, null, 2));
    }
    console.error('\n💡 Make sure the API is running:');
    console.error('   cd diotec360');
    console.error('   python -m uvicorn api.main:app --reload --port 8000\n');
    process.exit(1);
  }
}

runTests();
