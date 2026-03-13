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
import { Shield, Key } from 'lucide-react';

interface SovereignIdentityProps {
  code: string;
}

export default function SovereignIdentity({ code }: SovereignIdentityProps) {
  // Generate deterministic hash from code
  const hash = useMemo(() => {
    let h = 0;
    for (let i = 0; i < code.length; i++) {
      h = ((h << 5) - h) + code.charCodeAt(i);
      h = h & h; // Convert to 32bit integer
    }
    return Math.abs(h).toString(16).padStart(8, '0');
  }, [code]);

  // Generate identicon pattern from hash
  const pattern = useMemo(() => {
    const cells: boolean[][] = [];
    const size = 5;
    
    for (let y = 0; y < size; y++) {
      cells[y] = [];
      for (let x = 0; x < size; x++) {
        // Mirror pattern for symmetry
        const index = x < 3 ? x : 4 - x;
        const charIndex = (y * 3 + index) % hash.length;
        const value = parseInt(hash[charIndex], 16);
        cells[y][x] = value > 7;
      }
    }
    
    return cells;
  }, [hash]);

  // Generate color from hash
  const color = useMemo(() => {
    const hue = parseInt(hash.slice(0, 3), 16) % 360;
    return `hsl(${hue}, 70%, 60%)`;
  }, [hash]);

  const shortHash = hash.slice(0, 8);

  return (
    <div className="flex items-center gap-3 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg">
      {/* Identicon */}
      <div 
        className="relative w-10 h-10 rounded border-2 overflow-hidden"
        style={{ borderColor: color }}
      >
        {/* Background */}
        <div className="absolute inset-0 bg-gray-900" />
        
        {/* Pattern */}
        <div className="absolute inset-0 grid grid-cols-5 grid-rows-5 p-0.5 gap-0.5">
          {pattern.map((row, y) =>
            row.map((cell, x) => (
              <div
                key={`${x}-${y}`}
                className="rounded-sm"
                style={{
                  backgroundColor: cell ? color : 'transparent'
                }}
              />
            ))
          )}
        </div>

        {/* Glow effect */}
        <div 
          className="absolute inset-0 opacity-20 blur-sm"
          style={{ backgroundColor: color }}
        />
      </div>

      {/* Identity Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <Shield className="w-3 h-3 text-blue-400" />
          <span className="text-xs font-semibold text-white">Sovereign Identity</span>
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <Key className="w-3 h-3 text-gray-400" />
          <span className="text-xs font-mono text-gray-400">
            {shortHash}...
          </span>
        </div>
      </div>

      {/* Verification Badge */}
      <div className="flex flex-col items-center gap-1">
        <div className="w-6 h-6 rounded-full bg-green-900/30 border border-green-500/30 flex items-center justify-center">
          <span className="text-xs">✓</span>
        </div>
        <span className="text-xs text-green-400 font-semibold">Signed</span>
      </div>
    </div>
  );
}
