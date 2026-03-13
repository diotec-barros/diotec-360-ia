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

/**
 * DIOTEC360 Mirror Frame
 * Instant Preview Component
 * 
 * "The app exists the moment the proof completes."
 */

'use client';

import { useEffect, useState } from 'react';
import { X, ExternalLink, Copy, Check } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface MirrorFrameProps {
  manifestId: string;
  onClose: () => void;
}

interface ManifestationData {
  manifest_id: string;
  code: string;
  wasm: string | null;
  merkle_root: string;
  status: string;
  created_at: number;
  access_count: number;
}

export default function MirrorFrame({ manifestId, onClose }: MirrorFrameProps) {
  const [data, setData] = useState<ManifestationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  
  const previewUrl = `${window.location.origin}/preview/${manifestId}`;
  
  useEffect(() => {
    loadManifestation();
  }, [manifestId]);
  
  const loadManifestation = async () => {
    try {
      const response = await fetch(`${API_URL}/api/mirror/preview/${manifestId}`);
      const result = await response.json();
      
      if (result.success) {
        setData(result);
      } else {
        setError('Manifestation not found or expired');
      }
    } catch (err) {
      setError(`Failed to load manifestation: ${err}`);
    } finally {
      setIsLoading(false);
    }
  };
  
  const copyUrl = () => {
    navigator.clipboard.writeText(previewUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  const openInNewTab = () => {
    window.open(previewUrl, '_blank');
  };
  
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-6xl h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className="text-2xl">🪞</div>
            <div>
              <h2 className="text-lg font-semibold text-white">
                DIOTEC360 Mirror - Instant Preview
              </h2>
              <p className="text-xs text-gray-400">
                Reality manifested without deployment
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={copyUrl}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
              title="Copy preview URL"
            >
              {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            </button>
            
            <button
              onClick={openInNewTab}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
              title="Open in new tab"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="animate-spin text-4xl mb-4">🌀</div>
                <div className="text-gray-400">Loading manifestation...</div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="text-4xl mb-4">❌</div>
                <div className="text-red-400">{error}</div>
              </div>
            </div>
          )}
          
          {data && !isLoading && !error && (
            <div className="h-full flex flex-col">
              {/* Preview Info */}
              <div className="bg-gray-800 p-3 border-b border-gray-700">
                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <div className="text-gray-500">Status</div>
                    <div className="text-green-400 font-semibold">{data.status}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Access Count</div>
                    <div className="text-blue-400 font-semibold">{data.access_count}</div>
                  </div>
                  <div>
                    <div className="text-gray-500">Merkle Root</div>
                    <div className="text-purple-400 font-mono truncate">
                      {data.merkle_root.substring(0, 16)}...
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Preview Frame */}
              <div className="flex-1 bg-white overflow-auto">
                <div className="p-8">
                  <div className="max-w-4xl mx-auto">
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-8 border-2 border-purple-200">
                      <div className="text-center mb-6">
                        <div className="text-6xl mb-4">✨</div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">
                          Instant Manifestation
                        </h1>
                        <p className="text-gray-600">
                          This app was manifested without build or deploy
                        </p>
                      </div>
                      
                      <div className="bg-white rounded-lg p-6 shadow-lg">
                        <h2 className="text-xl font-semibold text-gray-900 mb-4">
                          Verified Code
                        </h2>
                        <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto text-gray-800">
                          {data.code}
                        </pre>
                      </div>
                      
                      <div className="mt-6 text-center text-sm text-gray-600">
                        <p>
                          🌌 This is a live preview powered by DIOTEC360 Mirror
                        </p>
                        <p className="mt-2">
                          The code was mathematically proved and manifested instantly
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-3 border-t border-gray-700 bg-gray-800">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <div>
              Preview URL: <span className="text-purple-400 font-mono">{previewUrl}</span>
            </div>
            <div>
              Expires in 1 hour
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
