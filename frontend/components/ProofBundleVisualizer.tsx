'use client';

import { CheckCircle2, XCircle, FileKey2 } from 'lucide-react';

export type ProofBundleVisualizerProps = {
  proofHash: string;
  z3Verified: boolean;
  signed: boolean;
  publicKeyHex?: string;
  signatureHex?: string;
};

function shortHex(hex: string, n = 12) {
  if (!hex) return '';
  return hex.length <= n ? hex : `${hex.slice(0, n)}…`;
}

export default function ProofBundleVisualizer({
  proofHash,
  z3Verified,
  signed,
  publicKeyHex,
  signatureHex,
}: ProofBundleVisualizerProps) {
  return (
    <div className="bg-black/30 border border-gray-800 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-3">
        <FileKey2 className="w-4 h-4 text-amber-300" />
        <span className="text-sm font-semibold">Proof Bundle</span>
      </div>

      <div className="space-y-3">
        <div>
          <div className="text-xs text-gray-400 mb-1">proofHash (SHA-256)</div>
          <div className="font-mono text-sm text-gray-200 break-all">{proofHash || '—'}</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="flex items-center gap-2 bg-gray-900/50 border border-gray-800 rounded p-2">
            {z3Verified ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <XCircle className="w-4 h-4 text-red-400" />
            )}
            <div className="text-xs text-gray-300">
              Verified by Z3-WASM
              <span className={z3Verified ? 'text-emerald-400 font-semibold ml-2' : 'text-red-400 font-semibold ml-2'}>
                {z3Verified ? '✅' : '❌'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-gray-900/50 border border-gray-800 rounded p-2">
            {signed ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : (
              <XCircle className="w-4 h-4 text-red-400" />
            )}
            <div className="text-xs text-gray-300">
              Signed by ED25519
              <span className={signed ? 'text-emerald-400 font-semibold ml-2' : 'text-red-400 font-semibold ml-2'}>
                {signed ? '✅' : '❌'}
              </span>
            </div>
          </div>
        </div>

        {(publicKeyHex || signatureHex) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <div className="text-xs text-gray-400 mb-1">publicKey</div>
              <div className="font-mono text-xs text-gray-300 break-all">{publicKeyHex || '—'}</div>
            </div>
            <div>
              <div className="text-xs text-gray-400 mb-1">signature</div>
              <div className="font-mono text-xs text-gray-300 break-all">{signatureHex ? shortHex(signatureHex, 24) : '—'}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
