/**
 * DIOTEC 360 SDK - Next.js App Router Example
 * 
 * Full-stack example with API route and client component
 */

// app/api/verify-transfer/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createDiotec360SDK } from '@diotec360/sdk';

const sdk = createDiotec360SDK({
  apiKey: process.env.DIOTEC360_API_KEY!,
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  
  try {
    const result = await sdk.verifyTransfer(body);
    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}

// app/components/TransferForm.tsx
'use client';

import { useState } from 'react';

export default function TransferForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    const formData = new FormData(e.target);
    const data = {
      from: formData.get('from'),
      to: formData.get('to'),
      amount: parseFloat(formData.get('amount')),
      currency: 'AOA',
      balance: parseFloat(formData.get('balance'))
    };

    const response = await fetch('/api/verify-transfer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();
    setResult(result);
    setIsLoading(false);
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input name="from" placeholder="From Account" required />
        <input name="to" placeholder="To Account" required />
        <input name="amount" type="number" placeholder="Amount" required />
        <input name="balance" type="number" placeholder="Balance" required />
        
        <button 
          type="submit" 
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 rounded"
        >
          {isLoading ? 'Verifying...' : 'Verify Transfer'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-4 rounded ${
          result.verified ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {result.verified ? (
            <>
              <p className="font-bold text-green-800">✅ Verified!</p>
              <p className="text-sm text-gray-600 mt-2">
                Proof: {result.merkleProof?.slice(0, 20)}...
              </p>
            </>
          ) : (
            <p className="text-red-800">❌ {result.error}</p>
          )}
        </div>
      )}
    </div>
  );
}
