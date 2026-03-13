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

// API client for DIOTEC360 backend

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

export interface VerifyRequest {
  code: string;
}

export interface VerifyResponse {
  status: 'PROVED' | 'FAILED' | 'ERROR';
  message: string;
  proof?: any;
  audit_trail?: string[];
}

export interface Example {
  name: string;
  code: string;
  description: string;
}

export async function verifyCode(code: string): Promise<VerifyResponse> {
  try {
    const response = await fetchWithFallback(`/api/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Verification error:', error);
    return {
      status: 'ERROR',
      message: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
}

export async function getExamples(): Promise<Example[]> {
  try {
    // Add cache-busting timestamp to force fresh data
    const timestamp = new Date().getTime();
    const response = await fetchWithFallback(`/api/examples?_t=${timestamp}`, {
      cache: 'no-store', // Disable caching
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Fetched examples from backend:', data.examples?.length || 0);
    // API returns { success: true, examples: [...], count: 3 }
    return data.examples || [];
  } catch (error) {
    console.error('❌ Failed to fetch examples:', error);
    return [];
  }
}

export async function compileCode(code: string): Promise<any> {
  try {
    const response = await fetchWithFallback(`/api/compile`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Compilation error:', error);
    throw error;
  }
}
