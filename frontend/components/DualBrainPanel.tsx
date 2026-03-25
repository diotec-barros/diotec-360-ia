/**
 * DIOTEC 360 IA - Dual-Brain Panel
 * 
 * Visual interface for Writer-Critic architecture
 * Shows side-by-side comparison of Writer output vs Critic review
 */

"use client";

import { useState } from 'react';
import { X, Brain, Loader2, AlertTriangle, CheckCircle, XCircle, Settings } from 'lucide-react';
import { DualBrainResult, RiskLevel, ProviderId, getOrchestrator, saveOrchestratorConfig } from '@/lib/dualBrainOrchestrator';

interface DualBrainPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate?: (result: DualBrainResult) => void;
}

export default function DualBrainPanel({ isOpen, onClose, onGenerate }: DualBrainPanelProps) {
  const [prompt, setPrompt] = useState('');
  const [context, setContext] = useState('');
  const [result, setResult] = useState<DualBrainResult | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [writerProvider, setWriterProvider] = useState<ProviderId>('openai');
  const [criticProvider, setCriticProvider] = useState<ProviderId>('anthropic');

  if (!isOpen) return null;

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setResult(null);

    try {
      const orchestrator = getOrchestrator();
      const generatedResult = await orchestrator.generate(prompt, context || undefined);
      setResult(generatedResult);
      
      if (onGenerate) {
        onGenerate(generatedResult);
      }
    } catch (error) {
      console.error('Dual-Brain generation error:', error);
      alert(`Generation failed: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveSettings = () => {
    saveOrchestratorConfig({
      writer: { provider: writerProvider },
      critic: { provider: criticProvider, minChars: 50 },
    });
    setShowSettings(false);
  };

  const getRiskColor = (risk: RiskLevel | undefined) => {
    if (!risk) return 'text-gray-400';
    switch (risk) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
    }
  };

  const getRiskIcon = (risk: RiskLevel | undefined) => {
    if (!risk) return null;
    switch (risk) {
      case 'low': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'medium': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'high': return <XCircle className="w-5 h-5 text-red-400" />;
    }
  };

  const getJudgeIcon = (verdict: DualBrainResult['judgeVerdict']) => {
    if (!verdict) return null;
    switch (verdict) {
      case 'PROVED': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'UNSAT': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'TIMEOUT': return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      case 'ERROR': return <XCircle className="w-5 h-5 text-red-400" />;
    }
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 w-full max-w-7xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gradient-to-r from-purple-900/30 to-pink-900/30">
          <div className="flex items-center space-x-3">
            <Brain className="w-8 h-8 text-purple-400" />
            <div>
              <h2 className="text-2xl font-bold text-white">Dual-Brain Mode</h2>
              <p className="text-sm text-gray-400">Writer-Critic Architecture</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5 text-gray-400" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="px-6 py-4 border-b border-gray-700 bg-gray-800/50">
            <h3 className="text-lg font-semibold mb-3 text-white">Configuration</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Writer Provider
                </label>
                <select
                  value={writerProvider}
                  onChange={(e) => setWriterProvider(e.target.value as ProviderId)}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="ollama">Ollama (Local)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Critic Provider
                </label>
                <select
                  value={criticProvider}
                  onChange={(e) => setCriticProvider(e.target.value as ProviderId)}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="ollama">Ollama (Local)</option>
                </select>
              </div>
            </div>
            <button
              onClick={handleSaveSettings}
              className="mt-3 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm font-semibold transition-colors"
            >
              Save Settings
            </button>
          </div>
        )}

        {/* Input Section */}
        <div className="px-6 py-4 border-b border-gray-700 space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Prompt (What do you want to generate?)
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Create a secure banking deposit function with Z3 assertions"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Context (Optional - existing code or requirements)
            </label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Paste existing code or additional context here..."
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
              rows={2}
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim()}
            className="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg text-white font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Brain className="w-5 h-5 mr-2" />
                Generate with Dual-Brain
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="flex-1 overflow-y-auto p-6">
          {isGenerating && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Loader2 className="w-16 h-16 animate-spin text-purple-500 mb-4" />
              <p className="text-xl font-semibold text-white mb-2">Dual-Brain Processing...</p>
              <p className="text-sm text-gray-400">Writer → Critic → Judge</p>
            </div>
          )}

          {!isGenerating && !result && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Brain className="w-24 h-24 text-gray-700 mb-4" />
              <p className="text-xl font-semibold text-gray-400 mb-2">Ready to Generate</p>
              <p className="text-sm text-gray-500">Enter a prompt above to start</p>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Execution Stats */}
              <div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg border border-gray-700">
                <div className="flex items-center space-x-6">
                  <div>
                    <p className="text-xs text-gray-400">Execution Time</p>
                    <p className="text-lg font-semibold text-white">{result.executionTimeMs}ms</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <p className="text-xs text-gray-400">Risk Level:</p>
                    {getRiskIcon(result.criticRisk)}
                    <p className={`text-sm font-semibold ${getRiskColor(result.criticRisk)}`}>
                      {result.criticRisk?.toUpperCase() || 'N/A'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <p className="text-xs text-gray-400">Judge Verdict:</p>
                    {getJudgeIcon(result.judgeVerdict)}
                    <p className={`text-sm font-semibold ${
                      result.judgeVerdict === 'PROVED' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {result.judgeVerdict || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Writer vs Critic */}
              <div className="grid grid-cols-2 gap-4">
                {/* Writer Output */}
                <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                  <div className="px-4 py-3 bg-blue-900/30 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-blue-400">✍️ Writer Output</h3>
                    <p className="text-xs text-gray-400">Generated code</p>
                  </div>
                  <div className="p-4 overflow-auto max-h-96">
                    <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                      {result.writerOutput}
                    </pre>
                  </div>
                </div>

                {/* Critic Review */}
                <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                  <div className="px-4 py-3 bg-purple-900/30 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-purple-400">🔍 Critic Review</h3>
                    <p className="text-xs text-gray-400">Analysis & suggestions</p>
                  </div>
                  <div className="p-4 overflow-auto max-h-96">
                    {result.criticReview ? (
                      <div className="prose prose-invert prose-sm max-w-none">
                        <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                          {result.criticReview}
                        </pre>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No review generated</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Final Code */}
              <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                <div className="px-4 py-3 bg-green-900/30 border-b border-gray-700">
                  <h3 className="text-lg font-semibold text-green-400">✅ Final Code (with Review)</h3>
                  <p className="text-xs text-gray-400">Ready to use</p>
                </div>
                <div className="p-4 overflow-auto max-h-96">
                  <pre className="text-sm text-gray-300 whitespace-pre-wrap font-mono">
                    {result.finalCode}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
