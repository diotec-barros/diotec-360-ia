/**
 * DIOTEC 360 SDK - React Integration Example
 * 
 * This example shows how to use DIOTEC 360 SDK
 * in a React application with hooks.
 */

import React, { useState, useEffect } from 'react';
import { createDiotec360SDK, Diotec360SDK, VerifyResponse } from '@diotec360/sdk';

// Initialize SDK (do this once, outside component or in context)
const sdk = createDiotec360SDK({
  apiKey: process.env.NEXT_PUBLIC_DIOTEC360_API_KEY || 'diotec_test_key',
  baseUrl: process.env.NEXT_PUBLIC_DIOTEC360_URL || 'http://localhost:8000'
});

interface TransferFormData {
  from: string;
  to: string;
  amount: number;
  balance: number;
}

export default function BankingApp() {
  const [formData, setFormData] = useState<TransferFormData>({
    from: 'ACC001',
    to: 'ACC002',
    amount: 1000,
    balance: 50000
  });
  const [isVerifying, setIsVerifying] = useState(false);
  const [result, setResult] = useState<VerifyResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setResult(null);

    try {
      const verification = await sdk.verifyTransfer({
        from: formData.from,
        to: formData.to,
        amount: formData.amount,
        currency: 'AOA',
        balance: formData.balance
      });

      setResult(verification);

      if (verification.verified) {
        // Execute the actual transfer in your backend
        console.log('✅ Transfer verified, executing...');
        // await executeTransfer(formData);
      }
    } catch (error) {
      setResult({
        verified: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setIsVerifying(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center mb-6">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-4">
            <span className="text-white text-2xl">🏛️</span>
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              DIOTEC 360 Banking
            </h1>
            <p className="text-sm text-gray-600">Mathematically Verified Transfers</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              From Account
            </label>
            <input
              type="text"
              value={formData.from}
              onChange={(e) => setFormData({ ...formData, from: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ACC001"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              To Account
            </label>
            <input
              type="text"
              value={formData.to}
              onChange={(e) => setFormData({ ...formData, to: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="ACC002"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount (AOA)
            </label>
            <input
              type="number"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="1000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Balance (AOA)
            </label>
            <input
              type="number"
              value={formData.balance}
              onChange={(e) => setFormData({ ...formData, balance: parseFloat(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="50000"
            />
          </div>

          <button
            type="submit"
            disabled={isVerifying}
            className="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isVerifying ? (
              <>
                <span className="animate-spin mr-2">⏳</span>
                Verifying with Z3...
              </>
            ) : (
              <>
                <span className="mr-2">🛡️</span>
                Verify & Transfer
              </>
            )}
          </button>
        </form>

        {/* Result Display */}
        {result && (
          <div className={`mt-6 p-4 rounded-lg ${
            result.verified 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-2">
                {result.verified ? '✅' : '❌'}
              </span>
              <h3 className={`text-lg font-bold ${
                result.verified ? 'text-green-800' : 'text-red-800'
              }`}>
                {result.verified ? 'Verification Passed' : 'Verification Failed'}
              </h3>
            </div>

            {result.verified ? (
              <div className="space-y-2 text-sm">
                <p className="text-gray-700">
                  <strong>Merkle Proof:</strong>
                  <br />
                  <code className="text-xs bg-white px-2 py-1 rounded mt-1 inline-block break-all">
                    {result.merkleProof}
                  </code>
                </p>
                {result.certificateUrl && (
                  <p className="text-gray-700">
                    <strong>Certificate:</strong>
                    <br />
                    <a 
                      href={result.certificateUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-xs"
                    >
                      {result.certificateUrl}
                    </a>
                  </p>
                )}
              </div>
            ) : (
              <p className="text-red-700 text-sm">
                {result.error || 'Unknown error occurred'}
              </p>
            )}
          </div>
        )}
      </div>

      {/* DIOTEC Badge */}
      <div className="mt-8 text-center">
        <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full text-white text-sm font-semibold shadow-lg">
          <span className="mr-2">🛡️</span>
          Protected by DIOTEC 360
        </div>
        <p className="text-gray-600 text-xs mt-2">
          All transactions mathematically verified
        </p>
      </div>
    </div>
  );
}
