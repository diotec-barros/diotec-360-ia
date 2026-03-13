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
 * DIOTEC360 Ghost UI
 * Pre-Cognitive Execution Interface
 * 
 * "The answer exists before the question is complete."
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const LATTICE_NODES_RAW = process.env.NEXT_PUBLIC_LATTICE_NODES || '';

function getCandidateBaseUrls(): string[] {
  const nodes = LATTICE_NODES_RAW
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => s.replace(/\/$/, ''));

  const primary = API_URL.replace(/\/$/, '');

  const seen = new Set<string>();
  const out: string[] = [];

  for (const u of [primary, ...nodes]) {
    if (!seen.has(u)) {
      seen.add(u);
      out.push(u);
    }
  }

  return out;
}

async function fetchWithFallback(path: string, init: RequestInit): Promise<Response> {
  const bases = getCandidateBaseUrls();
  let lastError: unknown = null;

  for (const base of bases) {
    try {
      const resp = await fetch(`${base}${path}`, init);
      if (resp.ok) return resp;
      lastError = new Error(`HTTP error! status: ${resp.status}`);
    } catch (e) {
      lastError = e;
    }
  }

  throw lastError instanceof Error ? lastError : new Error('All lattice nodes failed');
}

export interface GhostState {
  variables: Record<string, any> | null;
  merkle_root: string | null;
}

export interface GhostPrediction {
  success: boolean;
  status: 'MANIFESTED' | 'IMPOSSIBLE' | 'UNCERTAIN' | 'ERROR';
  confidence: number;
  latency: number;
  eliminated_states: number;
  message: string;
  result: GhostState | null;
}

export class GhostUI {
  private debounceTimer: NodeJS.Timeout | null = null;
  private cache: Map<string, GhostPrediction> = new Map();
  
  /**
   * Manifests truth while user types.
   * Doesn't wait for click - truth already exists.
   */
  async manifestTruth(code: string): Promise<GhostPrediction> {
    // Check cache first - truth is eternal
    const cacheKey = this.hashCode(code);
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    // Debounce to avoid overwhelming the server
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer);
    }
    
    return new Promise((resolve) => {
      this.debounceTimer = setTimeout(async () => {
        try {
          const response = await fetchWithFallback(`/api/ghost/predict`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
          });
          
          const prediction: GhostPrediction = await response.json();
          
          // Cache the manifestation
          if (prediction.status === 'MANIFESTED') {
            this.cache.set(cacheKey, prediction);
          }
          
          resolve(prediction);
          
        } catch (error) {
          resolve({
            success: false,
            status: 'ERROR',
            confidence: 0,
            latency: 0,
            eliminated_states: 0,
            message: `Ghost-Runner error: ${error}`,
            result: null,
          });
        }
      }, 500); // 500ms debounce
    });
  }
  
  /**
   * Prevents typing impossible code.
   * Returns false if next character leads to impossible state.
   * 
   * This is the "cursor lock" feature.
   */
  async canTypeNextChar(code: string, nextChar: string): Promise<boolean> {
    try {
      const response = await fetchWithFallback(`/api/ghost/can-type`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          code, 
          nextChar 
        }),
      });
      
      const result = await response.json();
      return result.canType !== false; // Default to true if uncertain
      
    } catch {
      return true; // Fail open - allow typing if check fails
    }
  }
  
  /**
   * Gets confidence level as percentage
   */
  getConfidencePercent(prediction: GhostPrediction): number {
    return Math.round(prediction.confidence * 100);
  }
  
  /**
   * Gets status color for UI
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'MANIFESTED':
        return 'text-green-400';
      case 'IMPOSSIBLE':
        return 'text-red-400';
      case 'UNCERTAIN':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  }
  
  /**
   * Gets status icon
   */
  getStatusIcon(status: string): string {
    switch (status) {
      case 'MANIFESTED':
        return '✨';
      case 'IMPOSSIBLE':
        return '🚫';
      case 'UNCERTAIN':
        return '🔮';
      default:
        return '❓';
    }
  }
  
  private hashCode(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(36);
  }
}

// Singleton instance
let ghostInstance: GhostUI | null = null;

export function getGhostUI(): GhostUI {
  if (!ghostInstance) {
    ghostInstance = new GhostUI();
  }
  return ghostInstance;
}
