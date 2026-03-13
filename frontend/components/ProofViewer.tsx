/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use client';

import { CheckCircle2, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import type { VerifyResponse } from '@/lib/api';

interface ProofViewerProps {
  result: VerifyResponse | null;
  isVerifying: boolean;
}

export default function ProofViewer({ result, isVerifying }: ProofViewerProps) {
  if (isVerifying) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-400">Verifying with Judge (Z3 Solver)...</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-500">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Write DIOTEC360 code and click Verify</p>
          <p className="text-sm mt-2">The Judge will prove your code is correct</p>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (result.status) {
      case 'PROVED':
        return <CheckCircle2 className="w-8 h-8 text-green-500" />;
      case 'FAILED':
        return <XCircle className="w-8 h-8 text-red-500" />;
      case 'ERROR':
        return <AlertCircle className="w-8 h-8 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (result.status) {
      case 'PROVED':
        return 'text-green-500';
      case 'FAILED':
        return 'text-red-500';
      case 'ERROR':
        return 'text-yellow-500';
    }
  };

  return (
    <div className="p-6 h-full overflow-auto">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          {getStatusIcon()}
          <h2 className={`text-2xl font-bold ${getStatusColor()}`}>
            {result.status}
          </h2>
        </div>
        <p className="text-gray-300">{result.message}</p>
      </div>

      {result.audit_trail && result.audit_trail.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Audit Trail</h3>
          <div className="bg-black/30 rounded-lg p-4 space-y-2">
            {result.audit_trail.map((entry, index) => (
              <div key={index} className="text-sm text-gray-400 font-mono">
                {entry}
              </div>
            ))}
          </div>
        </div>
      )}

      {result.proof && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3">Proof Details</h3>
          <div className="bg-black/30 rounded-lg p-4">
            <pre className="text-sm text-gray-400 overflow-auto">
              {JSON.stringify(result.proof, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {result.status === 'PROVED' && (
        <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
          <p className="text-green-400 text-sm">
            ✓ This code is <strong>mathematically proved</strong> to be correct.
            Bugs are impossible, not just unlikely.
          </p>
        </div>
      )}
    </div>
  );
}
