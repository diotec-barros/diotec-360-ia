"use client";

/**
 * Intelligence Harvester Panel - v4.0.0
 * 
 * UI for viewing and exporting training data
 */

import { useState, useEffect } from 'react';
import { Brain, Download, Trash2, BarChart3, FileJson, Check, X } from 'lucide-react';
import { getHarvester, TrainingSeed } from '@/lib/intelligenceHarvester';

interface IntelligenceHarvesterPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function IntelligenceHarvesterPanel({
  isOpen,
  onClose
}: IntelligenceHarvesterPanelProps) {
  const [seeds, setSeeds] = useState<TrainingSeed[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [selectedSeed, setSelectedSeed] = useState<TrainingSeed | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = () => {
    const harvester = getHarvester();
    setSeeds(harvester.getSeeds());
    setStats(harvester.getStats());
  };

  const handleExport = () => {
    const harvester = getHarvester();
    const blob = harvester.exportForTraining();
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diotec360-training-seeds-${Date.now()}.jsonl`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear all training seeds? This cannot be undone.')) {
      const harvester = getHarvester();
      harvester.clearSeeds();
      loadData();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-6xl max-h-[90vh] overflow-hidden bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 bg-gray-800 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center">
              <Brain className="w-6 h-6 mr-2 text-purple-400" />
              Intelligence Harvester
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Proven code patterns ready for AI training
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="px-6 py-4 bg-gray-800/50 border-b border-gray-700">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 rounded-xl p-4 border border-purple-700/30">
                <div className="text-3xl font-bold text-purple-400">{stats.total}</div>
                <div className="text-sm text-gray-400 mt-1">Total Seeds</div>
              </div>
              
              <div className="bg-gradient-to-br from-blue-900/20 to-cyan-900/20 rounded-xl p-4 border border-blue-700/30">
                <div className="text-3xl font-bold text-blue-400">
                  {Object.keys(stats.byCategory).length}
                </div>
                <div className="text-sm text-gray-400 mt-1">Categories</div>
              </div>
              
              <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 rounded-xl p-4 border border-green-700/30">
                <div className="text-3xl font-bold text-green-400">
                  {Object.keys(stats.byLanguage).length}
                </div>
                <div className="text-sm text-gray-400 mt-1">Languages</div>
              </div>
              
              <div className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-xl p-4 border border-yellow-700/30">
                <div className="text-3xl font-bold text-yellow-400">100%</div>
                <div className="text-sm text-gray-400 mt-1">Proven</div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="px-6 py-4 bg-gray-800/30 border-b border-gray-700 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={handleExport}
              disabled={seeds.length === 0}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="w-4 h-4" />
              <span className="text-sm font-medium">Export JSONL</span>
            </button>
            
            <button
              onClick={() => setSelectedSeed(null)}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all"
            >
              <BarChart3 className="w-4 h-4" />
              <span className="text-sm font-medium">View Stats</span>
            </button>
          </div>
          
          <button
            onClick={handleClear}
            disabled={seeds.length === 0}
            className="flex items-center space-x-2 px-4 py-2 bg-red-900/20 hover:bg-red-900/30 text-red-400 rounded-lg transition-all border border-red-700/30 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Trash2 className="w-4 h-4" />
            <span className="text-sm font-medium">Clear All</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Seeds List */}
          <div className="w-1/3 border-r border-gray-700 overflow-y-auto">
            {seeds.length === 0 ? (
              <div className="p-6 text-center text-gray-400">
                <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No training seeds yet</p>
                <p className="text-sm mt-2">Verify code with Z3 to start harvesting</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-700">
                {seeds.map((seed) => (
                  <button
                    key={seed.id}
                    onClick={() => setSelectedSeed(seed)}
                    className={`w-full p-4 text-left hover:bg-gray-800 transition-colors ${
                      selectedSeed?.id === seed.id ? 'bg-gray-800 border-l-4 border-purple-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        seed.category === 'financial' ? 'bg-green-900/30 text-green-400 border border-green-700/30' :
                        seed.category === 'security' ? 'bg-red-900/30 text-red-400 border border-red-700/30' :
                        seed.category === 'algorithm' ? 'bg-blue-900/30 text-blue-400 border border-blue-700/30' :
                        'bg-gray-700 text-gray-400'
                      }`}>
                        {seed.category}
                      </span>
                      <Check className="w-4 h-4 text-green-400" />
                    </div>
                    <p className="text-sm text-white font-medium line-clamp-2 mb-1">
                      {seed.prompt}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                      <span>{seed.language}</span>
                      <span>•</span>
                      <span>{seed.complexity}</span>
                      <span>•</span>
                      <span>{new Date(seed.timestamp).toLocaleDateString()}</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Seed Detail */}
          <div className="flex-1 overflow-y-auto p-6">
            {selectedSeed ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-white mb-2">Prompt</h3>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <p className="text-sm text-gray-300">{selectedSeed.prompt}</p>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white mb-2">AI Output</h3>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                      {selectedSeed.aiOutput}
                    </pre>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white mb-2">Final Code (Proven)</h3>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                    <pre className="text-sm text-green-400 whitespace-pre-wrap font-mono">
                      {selectedSeed.finalCode}
                    </pre>
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white mb-2">Metadata</h3>
                  <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Verdict:</span>
                      <span className="text-green-400 font-semibold">{selectedSeed.judgeVerdict}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">AI Provider:</span>
                      <span className="text-white">{selectedSeed.aiProvider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">AI Model:</span>
                      <span className="text-white">{selectedSeed.aiModel}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Category:</span>
                      <span className="text-white">{selectedSeed.category}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Language:</span>
                      <span className="text-white">{selectedSeed.language}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Complexity:</span>
                      <span className="text-white">{selectedSeed.complexity}</span>
                    </div>
                    {selectedSeed.merkleRoot && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Merkle Root:</span>
                        <span className="text-green-400 font-mono text-xs">{selectedSeed.merkleRoot.substring(0, 16)}...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : stats ? (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white mb-4">By Category</h3>
                  <div className="space-y-2">
                    {Object.entries(stats.byCategory).map(([category, count]) => (
                      <div key={category} className="flex items-center justify-between">
                        <span className="text-gray-300 capitalize">{category}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-600 to-pink-600"
                              style={{ width: `${((count as number) / stats.total) * 100}%` }}
                            />
                          </div>
                          <span className="text-white font-semibold w-12 text-right">{count as number}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white mb-4">By Language</h3>
                  <div className="space-y-2">
                    {Object.entries(stats.byLanguage).map(([language, count]) => (
                      <div key={language} className="flex items-center justify-between">
                        <span className="text-gray-300">{language}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-blue-600 to-cyan-600"
                              style={{ width: `${((count as number) / stats.total) * 100}%` }}
                            />
                          </div>
                          <span className="text-white font-semibold w-12 text-right">{count as number}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-bold text-white mb-4">By Complexity</h3>
                  <div className="space-y-2">
                    {Object.entries(stats.byComplexity).map(([complexity, count]) => (
                      <div key={complexity} className="flex items-center justify-between">
                        <span className="text-gray-300 capitalize">{complexity}</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-32 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-green-600 to-emerald-600"
                              style={{ width: `${((count as number) / stats.total) * 100}%` }}
                            />
                          </div>
                          <span className="text-white font-semibold w-12 text-right">{count as number}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <FileJson className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Select a seed to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
