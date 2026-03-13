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

import { useState, useEffect, useRef } from 'react';
import { getExamples, type Example } from '@/lib/api';
import { ChevronDown, RefreshCw } from 'lucide-react';

interface ExampleSelectorProps {
  onSelect: (code: string) => void;
}

export default function ExampleSelector({ onSelect }: ExampleSelectorProps) {
  const [examples, setExamples] = useState<Example[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadExamples();
  }, []);

  useEffect(() => {
    if (!isOpen) return;

    const handleMouseDown = (e: MouseEvent) => {
      const el = containerRef.current;
      if (!el) return;
      if (e.target instanceof Node && !el.contains(e.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [isOpen]);

  const loadExamples = async (forceRefresh = false) => {
    setLoading(true);
    if (forceRefresh) setRefreshing(true);
    
    try {
      const data = await getExamples();
      setExamples(data);
      console.log('✅ Examples loaded from backend:', data.length);
    } catch (error) {
      console.error('❌ Failed to load examples:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleSelect = (example: Example) => {
    console.log('📝 Selected example:', example.name);
    onSelect(example.code);
    setIsOpen(false);
  };

  const handleRefresh = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await loadExamples(true);
  };

  return (
    <div ref={containerRef} className="flex flex-col items-stretch">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
      >
        <span>Examples</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="mt-2 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-xl overflow-hidden">
          {loading ? (
            <div className="p-4 text-center text-gray-400">Loading examples...</div>
          ) : examples.length === 0 ? (
            <div className="p-4 text-center">
              <div className="text-gray-400 mb-2">No examples available</div>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded text-sm mx-auto"
              >
                <RefreshCw className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          ) : (
            <>
              <div className="p-2 border-b border-gray-700 flex items-center justify-between bg-gray-900">
                <span className="text-xs text-gray-400">{examples.length} examples</span>
                <button
                  onClick={handleRefresh}
                  disabled={refreshing}
                  className="flex items-center gap-1 px-2 py-1 hover:bg-gray-700 rounded text-xs text-gray-300"
                  title="Refresh examples from backend"
                >
                  <RefreshCw className={`w-3 h-3 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
              <div className="max-h-96 overflow-y-auto">
                {examples.map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleSelect(example)}
                    className="w-full text-left p-4 hover:bg-gray-700 transition-colors border-b border-gray-700 last:border-b-0"
                  >
                    <div className="font-semibold text-white mb-1">{example.name}</div>
                    <div className="text-sm text-gray-400">{example.description}</div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
