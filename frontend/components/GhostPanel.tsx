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
 * Ghost Panel Component
 * Displays pre-cognitive execution results
 * 
 * Shows the manifestation of truth before execution
 */

'use client';

import { useEffect, useState } from 'react';
import { GhostPrediction, getGhostUI } from '@/lib/ghost';

interface GhostPanelProps {
  code: string;
  enabled?: boolean;
}

export default function GhostPanel({ code, enabled = true }: GhostPanelProps) {
  const [prediction, setPrediction] = useState<GhostPrediction | null>(null);
  const [isManifesting, setIsManifesting] = useState(false);
  const ghost = getGhostUI();
  
  useEffect(() => {
    if (!enabled || !code.trim()) {
      setPrediction(null);
      return;
    }
    
    const manifest = async () => {
      setIsManifesting(true);
      const result = await ghost.manifestTruth(code);
      setPrediction(result);
      setIsManifesting(false);
    };
    
    manifest();
  }, [code, enabled]);
  
  if (!enabled) {
    return null;
  }
  
  return (
    <div className="ghost-panel bg-gray-900 border border-gray-700 rounded-lg p-4 mt-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
          <span className="text-purple-400">🌌</span>
          Ghost-Runner
          <span className="text-xs text-gray-500">(Pre-Cognitive Execution)</span>
        </h3>
        
        {isManifesting && (
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <div className="animate-spin">⚡</div>
            Manifesting...
          </div>
        )}
      </div>
      
      {prediction && (
        <div className="space-y-3">
          {/* Status Banner */}
          <div className={`p-3 rounded-lg border ${
            prediction.status === 'MANIFESTED' 
              ? 'bg-green-900/20 border-green-700' 
              : prediction.status === 'IMPOSSIBLE'
              ? 'bg-red-900/20 border-red-700'
              : 'bg-yellow-900/20 border-yellow-700'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-2xl">
                  {ghost.getStatusIcon(prediction.status)}
                </span>
                <div>
                  <div className={`font-semibold ${ghost.getStatusColor(prediction.status)}`}>
                    {prediction.status}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {prediction.message}
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-xs text-gray-500">Confidence</div>
                <div className={`text-lg font-bold ${ghost.getStatusColor(prediction.status)}`}>
                  {ghost.getConfidencePercent(prediction)}%
                </div>
              </div>
            </div>
          </div>
          
          {/* Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-gray-800 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">Latency</div>
              <div className="text-lg font-bold text-purple-400">
                {prediction.latency.toFixed(1)}ms
              </div>
              <div className="text-xs text-gray-600 mt-1">
                (Zero-latency computing)
              </div>
            </div>
            
            <div className="bg-gray-800 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-1">States Eliminated</div>
              <div className="text-lg font-bold text-blue-400">
                {prediction.eliminated_states.toLocaleString()}
              </div>
              <div className="text-xs text-gray-600 mt-1">
                (Impossibilities subtracted)
              </div>
            </div>
          </div>
          
          {/* Result */}
          {prediction.result && prediction.result.variables && (
            <div className="bg-gray-800 p-3 rounded-lg">
              <div className="text-xs text-gray-500 mb-2">Manifested State</div>
              <pre className="text-xs text-green-400 overflow-x-auto">
                {JSON.stringify(prediction.result.variables, null, 2)}
              </pre>
              
              {prediction.result.merkle_root && (
                <div className="mt-2 pt-2 border-t border-gray-700">
                  <div className="text-xs text-gray-500">Merkle Root</div>
                  <div className="text-xs text-purple-400 font-mono mt-1 break-all">
                    {prediction.result.merkle_root}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Explanation */}
          <div className="text-xs text-gray-500 italic border-l-2 border-purple-500 pl-3">
            {prediction.status === 'MANIFESTED' && (
              <>
                ✨ The result was <strong>manifested</strong> by eliminating all impossible states.
                No execution needed - the truth already existed in the mathematical proof.
              </>
            )}
            {prediction.status === 'IMPOSSIBLE' && (
              <>
                🚫 All possible states were eliminated. This intent is <strong>mathematically impossible</strong>.
                The cursor will prevent you from completing this code.
              </>
            )}
            {prediction.status === 'UNCERTAIN' && (
              <>
                🔮 Multiple valid states remain. Add more constraints to manifest a unique truth.
              </>
            )}
          </div>
        </div>
      )}
      
      {!prediction && !isManifesting && code.trim() && (
        <div className="text-center text-gray-500 text-sm py-8">
          <div className="text-4xl mb-2">🌌</div>
          <div>Start typing to manifest truth...</div>
          <div className="text-xs mt-2 text-gray-600">
            The Ghost-Runner will predict the outcome before execution
          </div>
        </div>
      )}
    </div>
  );
}
