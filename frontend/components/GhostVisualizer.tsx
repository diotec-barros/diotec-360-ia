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

import { useMemo } from 'react';
import { Lock } from 'lucide-react';

interface GhostVisualizerProps {
  code: string;
}

export default function GhostVisualizer({ code }: GhostVisualizerProps) {
  // Detect secret variables in the code
  const secretVariables = useMemo(() => {
    const secrets: Array<{ name: string; line: number; column: number }> = [];
    const lines = code.split('\n');
    
    lines.forEach((line, lineIndex) => {
      const secretMatch = line.match(/secret\s+(\w+)/);
      if (secretMatch) {
        const varName = secretMatch[1];
        const column = line.indexOf('secret');
        secrets.push({
          name: varName,
          line: lineIndex + 1,
          column
        });
      }
    });
    
    return secrets;
  }, [code]);

  if (secretVariables.length === 0) {
    return null;
  }

  return (
    <div className="absolute inset-0 pointer-events-none z-10">
      {/* Glassmorphism Overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/10 via-transparent to-purple-900/10" />
      
      {/* Secret Variable Indicators */}
      <div className="absolute top-4 right-4 pointer-events-auto">
        <div className="bg-purple-900/80 backdrop-blur-xl border border-purple-500/30 rounded-xl p-4 shadow-2xl">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center">
              <Lock className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">Ghost Protocol</h3>
              <p className="text-xs text-purple-300">Zero-Knowledge Privacy</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <div className="text-xs text-purple-200 font-semibold mb-1">
              Protected Variables:
            </div>
            {secretVariables.map((secret, index) => (
              <div
                key={index}
                className="flex items-center gap-2 px-3 py-2 bg-purple-800/50 rounded-lg border border-purple-500/20"
              >
                <Lock className="w-3 h-3 text-purple-300" />
                <span className="text-xs font-mono text-purple-100">{secret.name}</span>
                <span className="text-xs text-purple-400">Line {secret.line}</span>
              </div>
            ))}
          </div>

          <div className="mt-3 pt-3 border-t border-purple-500/20">
            <div className="flex items-center gap-2 text-xs text-purple-300">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Verified without revealing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Lock Icons */}
      {secretVariables.map((secret, index) => (
        <div
          key={index}
          className="absolute animate-float"
          style={{
            top: `${20 + index * 15}%`,
            left: `${10 + index * 20}%`,
            animationDelay: `${index * 0.5}s`
          }}
        >
          <div className="relative">
            {/* Glow Effect */}
            <div className="absolute inset-0 bg-purple-500/30 blur-xl rounded-full" />
            {/* Lock Icon */}
            <div className="relative w-12 h-12 rounded-full bg-purple-900/80 backdrop-blur-xl border border-purple-500/30 flex items-center justify-center">
              <Lock className="w-6 h-6 text-purple-300" />
            </div>
          </div>
        </div>
      ))}

      {/* Privacy Shield Badge */}
      <div className="absolute bottom-4 left-4 pointer-events-auto">
        <div className="bg-purple-900/80 backdrop-blur-xl border border-purple-500/30 rounded-lg px-4 py-2 shadow-lg">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-purple-200">
              {secretVariables.length} variable{secretVariables.length !== 1 ? 's' : ''} protected by ZKP
            </span>
          </div>
        </div>
      </div>

      {/* Particle Effect */}
      <div className="absolute inset-0 overflow-hidden">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-purple-400/30 rounded-full animate-particle"
            style={{
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${3 + Math.random() * 4}s`
            }}
          />
        ))}
      </div>
    </div>
  );
}
