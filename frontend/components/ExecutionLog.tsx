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

import { useState } from 'react';
import { ChevronUp, ChevronDown, Download, Filter, Search, FileText } from 'lucide-react';

interface LogEntry {
  timestamp: number;
  layer: 'judge' | 'architect' | 'sentinel' | 'ghost' | 'oracle';
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  details?: string;
}

interface ExecutionLogProps {
  entries: LogEntry[];
  isOpen: boolean;
  onToggle: () => void;
}

export default function ExecutionLog({ entries, isOpen, onToggle }: ExecutionLogProps) {
  const [filter, setFilter] = useState<string>('all');
  const [search, setSearch] = useState('');

  const getLayerIcon = (layer: string) => {
    const icons = {
      judge: '🏛️',
      architect: '🤖',
      sentinel: '🛡️',
      ghost: '🎭',
      oracle: '🔮'
    };
    return icons[layer as keyof typeof icons] || '📝';
  };

  const getLayerColor = (layer: string) => {
    const colors = {
      judge: 'text-blue-400 bg-blue-900/20',
      architect: 'text-green-400 bg-green-900/20',
      sentinel: 'text-red-400 bg-red-900/20',
      ghost: 'text-purple-400 bg-purple-900/20',
      oracle: 'text-amber-400 bg-amber-900/20'
    };
    return colors[layer as keyof typeof colors] || 'text-gray-400 bg-gray-900/20';
  };

  const getLevelColor = (level: string) => {
    const colors = {
      info: 'text-blue-400',
      success: 'text-green-400',
      warning: 'text-yellow-400',
      error: 'text-red-400'
    };
    return colors[level as keyof typeof colors] || 'text-gray-400';
  };

  const getLevelIcon = (level: string) => {
    const icons = {
      info: 'ℹ️',
      success: '✅',
      warning: '⚠️',
      error: '❌'
    };
    return icons[level as keyof typeof icons] || '📝';
  };

  const filteredEntries = entries.filter(entry => {
    const matchesFilter = filter === 'all' || entry.layer === filter;
    const matchesSearch = search === '' || 
      entry.message.toLowerCase().includes(search.toLowerCase()) ||
      entry.layer.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const formatTimestamp = (timestamp: number) => {
    const seconds = (timestamp / 1000).toFixed(3);
    return `[${seconds}s]`;
  };

  const exportToPDF = () => {
    // TODO: Implement PDF export
    alert('Exporting audit certificate to PDF...');
  };

  return (
    <div className={`
      shrink-0 w-full border-t border-gray-800
      bg-black/95 supports-[backdrop-filter]:bg-black/80 supports-[backdrop-filter]:backdrop-blur
      transition-[height] duration-300 ease-in-out z-50
      ${isOpen ? 'h-80' : 'h-12'}
    `}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-black">
        <div className="flex items-center gap-4">
          <button
            onClick={onToggle}
            className="flex items-center gap-2 hover:text-white transition-colors"
          >
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
            <FileText className="w-4 h-4" />
            <span className="text-sm font-semibold">EXECUTION LOG</span>
            <span className="text-xs text-gray-500">
              ({filteredEntries.length} entries)
            </span>
          </button>

          {isOpen && (
            <>
              {/* Filter */}
              <div className="flex items-center gap-2">
                <Filter className="w-3 h-3 text-gray-400" />
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="bg-gray-800 text-xs text-white px-2 py-1 rounded border border-gray-700 focus:border-blue-500 focus:outline-none"
                >
                  <option value="all">All Layers</option>
                  <option value="judge">Judge</option>
                  <option value="architect">Architect</option>
                  <option value="sentinel">Sentinel</option>
                  <option value="ghost">Ghost</option>
                  <option value="oracle">Oracle</option>
                </select>
              </div>

              {/* Search */}
              <div className="flex items-center gap-2">
                <Search className="w-3 h-3 text-gray-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search logs..."
                  className="bg-gray-800 text-xs text-white px-2 py-1 rounded border border-gray-700 focus:border-blue-500 focus:outline-none w-48"
                />
              </div>
            </>
          )}
        </div>

        {isOpen && (
          <button
            onClick={exportToPDF}
            className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors"
          >
            <Download className="w-3 h-3" />
            Export Certificate (PDF)
          </button>
        )}
      </div>

      {/* Log Entries */}
      {isOpen && (
        <div className="h-full overflow-y-auto p-4 space-y-2 font-mono text-xs">
          {filteredEntries.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              No log entries found
            </div>
          ) : (
            filteredEntries.map((entry, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-2 rounded hover:bg-gray-800/50 transition-colors group"
              >
                {/* Timestamp */}
                <span className="text-gray-500 shrink-0">
                  {formatTimestamp(entry.timestamp)}
                </span>

                {/* Layer Badge */}
                <span className={`
                  shrink-0 px-2 py-0.5 rounded text-xs font-semibold uppercase
                  ${getLayerColor(entry.layer)}
                `}>
                  {getLayerIcon(entry.layer)} {entry.layer}
                </span>

                {/* Level Icon */}
                <span className={`shrink-0 ${getLevelColor(entry.level)}`}>
                  {getLevelIcon(entry.level)}
                </span>

                {/* Message */}
                <span className="text-gray-300 flex-1">
                  {entry.message}
                </span>

                {/* Details (expandable) */}
                {entry.details && (
                  <button className="text-blue-400 hover:text-blue-300 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                    Details
                  </button>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
