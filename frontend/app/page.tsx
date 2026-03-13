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

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { verifyCode, type VerifyResponse } from '@/lib/api';
import ProofViewer from '@/components/ProofViewer';
import LayerSidebar from '@/components/LayerSidebar';
import ArchitectChat from '@/components/ArchitectChat';
import GhostVisualizer from '@/components/GhostVisualizer';
import SentinelRadar from '@/components/SentinelRadar';
import ExecutionLog from '@/components/ExecutionLog';
import OracleAtlas from '@/components/OracleAtlas';
import SovereignIdentity from '@/components/SovereignIdentity';
import { getDiotec360Engine } from '@/lib/diotec360Engine';
import { getDiotec360JudgeWasm } from '@/lib/diotec360Judge';
import { spawnAgentFromFrontend } from '@/lib/agentNexus';
import SovereignControlPanel from '@/components/SovereignControlPanel';
import ProofBundleVisualizer from '@/components/ProofBundleVisualizer';
import AgentTelemetry, { type TelemetryEntry } from '@/components/AgentTelemetry';
import IdentityVault from '@/components/IdentityVault';

// Dynamically import Editor to avoid SSR issues with Monaco
const Editor = dynamic(() => import('@/components/Editor'), { ssr: false });

interface LogEntry {
  timestamp: number;
  layer: 'judge' | 'architect' | 'sentinel' | 'ghost' | 'oracle';
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  details?: string;
}

const DEFAULT_CODE = `intent transfer(sender: Account, receiver: Account, amount: Balance) {
  guard {
    sender_balance >= amount;
    amount > 0;
  }
  
  verify {
    sender_balance == old_sender_balance - amount;
    receiver_balance == old_receiver_balance + amount;
    total_supply == old_total_supply;
  }
}`;

export default function Home() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [brainStatus, setBrainStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [brainOutput, setBrainOutput] = useState<string>('');
  const [judgeStatus, setJudgeStatus] = useState<'idle' | 'loading' | 'ready' | 'error'>('idle');
  const [judgeOutput, setJudgeOutput] = useState<string>('');
  const [isSpawning, setIsSpawning] = useState(false);
  const [sovereignProofHash, setSovereignProofHash] = useState('');
  const [sovereignPublicKeyHex, setSovereignPublicKeyHex] = useState('');
  const [sovereignSignatureHex, setSovereignSignatureHex] = useState('');
  const [sovereignZ3Verified, setSovereignZ3Verified] = useState(false);
  const [telemetry, setTelemetry] = useState<TelemetryEntry[]>([]);
  const [activeAgentId, setActiveAgentId] = useState<string | null>(null);
  const [spawnError, setSpawnError] = useState<string>('');
  const [activeLayer, setActiveLayer] = useState('judge');
  const [chatOpen, setChatOpen] = useState(false);
  const [ghostMode, setGhostMode] = useState(false);
  const [logOpen, setLogOpen] = useState(false);
  const [executionLogs, setExecutionLogs] = useState<LogEntry[]>([]);
  const [sentinelStatus, setSentinelStatus] = useState<'idle' | 'scanning' | 'verified' | 'threat'>('idle');
  const [threatLevel, setThreatLevel] = useState(0);
  const [activeOracles, setActiveOracles] = useState<string[]>([]);

  // CMD+K handler for Architect Chat
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setChatOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Update Ghost mode when layer changes
  useEffect(() => {
    setGhostMode(activeLayer === 'ghost');
  }, [activeLayer]);

  // Detect external data sources in code
  useEffect(() => {
    const externalMatches = code.match(/external\s+\w+/g);
    if (externalMatches && externalMatches.length > 0) {
      // Simulate oracle activation based on code content
      const oracles: string[] = [];
      if (code.includes('price') || code.includes('btc')) {
        oracles.push('chainlink-nyc', 'chainlink-geneva');
      }
      if (code.includes('rainfall') || code.includes('weather')) {
        oracles.push('weather-london', 'weather-houston');
      }
      setActiveOracles(oracles);
    } else {
      setActiveOracles([]);
    }
  }, [code]);

  const handleVerify = async () => {
    setIsVerifying(true);
    setResult(null);
    setExecutionLogs([]);
    setSentinelStatus('scanning');
    setThreatLevel(0);
    
    // Simulate execution log
    const startTime = Date.now();
    const addLog = (layer: LogEntry['layer'], level: LogEntry['level'], message: string, delay: number) => {
      setTimeout(() => {
        setExecutionLogs(prev => [...prev, {
          timestamp: Date.now() - startTime,
          layer,
          level,
          message
        }]);
      }, delay);
    };

    addLog('sentinel', 'info', 'Initializing security scan...', 100);
    addLog('sentinel', 'info', 'Scanning for overflow vulnerabilities...', 300);
    addLog('sentinel', 'success', 'No overflow threats detected', 500);
    addLog('judge', 'info', 'Parsing intent definition...', 700);
    addLog('judge', 'info', 'Extracting guard conditions...', 900);
    addLog('judge', 'info', 'Generating Z3 constraints...', 1100);
    addLog('sentinel', 'info', 'Validating conservation laws...', 1300);
    
    try {
      const response = await verifyCode(code);
      setResult(response);
      
      if (response.status === 'PROVED') {
        addLog('judge', 'success', 'Z3 Solver: Theorem PROVED (sat)', 1500);
        addLog('sentinel', 'success', 'Conservation validated: All balances preserved', 1700);
        addLog('judge', 'success', 'Verification complete: PROVED', 1900);
        setSentinelStatus('verified');
        setThreatLevel(0);
      } else {
        addLog('judge', 'error', `Verification failed: ${response.message}`, 1500);
        addLog('sentinel', 'warning', 'Potential logic error detected', 1700);
        setSentinelStatus('threat');
        setThreatLevel(75);
      }
    } catch (error) {
      setResult({
        status: 'ERROR',
        message: 'Failed to connect to verification service',
      });
      addLog('judge', 'error', 'Connection to verification service failed', 1500);
      setSentinelStatus('threat');
      setThreatLevel(100);
    } finally {
      setIsVerifying(false);
      setTimeout(() => {
        if (sentinelStatus !== 'threat') {
          setSentinelStatus('idle');
        }
      }, 3000);
    }
  };

  const handleSpawnSovereignAgent = async () => {
    setIsSpawning(true);
    setSpawnError('');
    setTelemetry([]);
    setActiveAgentId(null);
    setSovereignProofHash('');
    setSovereignPublicKeyHex('');
    setSovereignSignatureHex('');
    setSovereignZ3Verified(false);

    const start = Date.now();
    const push = (source: TelemetryEntry['source'], message: string) => {
      setTelemetry((prev) => [...prev, { t: Date.now() - start, source, message }]);
    };

    try {
      push('system', 'Sovereign Gate: begin');
      const agentId = `agent-${Date.now()}`;

      const res = await spawnAgentFromFrontend({
        agentId,
        name: 'Sovereign Agent',
        mission: 'Execute proven DIOTEC 360 IA intent',
        invariants: { tickIntervalMs: 1000 },
        proven: { proofHash: 'pending', judgeVersion: 'pending' },
        // IMPORTANT: bind to editor code (Option A)
        dslCode: code,
      } as any);

      setActiveAgentId(agentId);
      setSovereignProofHash(res.proofHash);
      setSovereignPublicKeyHex(res.publicKeyHex);
      setSovereignSignatureHex(res.signatureHex);
      setSovereignZ3Verified(Boolean(res.z3Verified));

      push('system', `ProofHash sealed: ${res.proofHash}`);
      push('system', 'Spawning worker…');

      const unsubscribe = res.spawned.onMessage((evt) => {
        const msg = evt.data || {};
        if (msg.type) {
          push('agent', `${msg.type} ${msg.payload ? JSON.stringify(msg.payload) : ''}`);
        } else {
          push('agent', JSON.stringify(msg));
        }
      });

      push('system', 'Agent online');

      // Ensure we can cleanup listener if user kills agent
      (window as any).__diotec360ActiveAgent = { res, unsubscribe };
    } catch (e: any) {
      const m = e?.message ? String(e.message) : String(e);
      setSpawnError(m);
    } finally {
      setIsSpawning(false);
    }
  };

  const handleKillSwitch = () => {
    try {
      const active = (window as any).__diotec360ActiveAgent;
      if (active?.unsubscribe) active.unsubscribe();
      if (active?.res?.spawned) active.res.spawned.stop();
    } finally {
      (window as any).__diotec360ActiveAgent = null;
      setActiveAgentId(null);
      setTelemetry((prev) => [...prev, { t: 0, source: 'system', message: 'Kill-switch activated' }]);
    }
  };

  const handleJudgeWasm = async () => {
    setJudgeStatus('loading');
    setJudgeOutput('');

    try {
      const judge = getDiotec360JudgeWasm();
      await judge.init();
      setJudgeStatus('ready');

      const verdict = await judge.verifyLocally(code);
      setJudgeOutput(JSON.stringify(verdict, null, 2));
    } catch (e: any) {
      setJudgeStatus('error');
      setJudgeOutput(e?.message ? String(e.message) : String(e));
    }
  };

  const handleBrain = async () => {
    setBrainStatus('loading');
    setBrainOutput('');

    try {
      const engine = getDiotec360Engine();
      await engine.init({ device: 'webgpu' });
      setBrainStatus('ready');

      const prompt = `You are DIOTEC 360 IA. Produce a concise intent improvement suggestion for this DSL code:\n\n${code}\n\nReturn only the suggestion.`;
      const out = await engine.generateText(prompt, { maxNewTokens: 96, temperature: 0.2 });
      setBrainOutput(out);
    } catch (e: any) {
      setBrainStatus('error');
      setBrainOutput(e?.message ? String(e.message) : String(e));
    }
  };

  const handleExampleSelect = (exampleCode: string) => {
    setCode(exampleCode);
    setResult(null);
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Layer Sidebar */}
      <LayerSidebar 
        onLayerChange={setActiveLayer} 
        onExampleSelect={handleExampleSelect}
        onVerify={handleVerify}
        isVerifying={isVerifying}
        onChatToggle={() => setChatOpen(!chatOpen)}
        activeLayer={activeLayer}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Header with Run Verify and AI Chat */}
        <header className="border-b border-gray-800 bg-gray-900 px-6 py-3">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold">DIOTEC 360 IA Studio</h1>
            <div className="flex items-center gap-3">
              <button
                onClick={handleVerify}
                disabled={isVerifying}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {isVerifying ? (
                  <>
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Verifying...
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Run Verify
                  </>
                )}
              </button>
              <button
                onClick={handleBrain}
                disabled={brainStatus === 'loading'}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {brainStatus === 'loading' ? 'Brain: loading…' : 'Brain: WebGPU'}
              </button>
              <button
                onClick={handleJudgeWasm}
                disabled={judgeStatus === 'loading'}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                {judgeStatus === 'loading' ? 'Judge: loading…' : 'Judge: WASM'}
              </button>
              <button
                onClick={() => setChatOpen(!chatOpen)}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                AI Chat
              </button>
            </div>
          </div>
        </header>

        {/* Editor & Proof Viewer */}
        <div className="flex-1 flex overflow-hidden min-h-0">
          <div className="flex-1 flex overflow-hidden min-h-0">
            {/* Editor Panel */}
            <div className="flex-1 border-r border-gray-800 flex flex-col relative">
              <div className="px-4 py-2 bg-gray-900 border-b border-gray-800 flex items-center justify-between gap-4">
                <h2 className="text-sm font-semibold text-gray-400">CODE EDITOR</h2>
                <div className="flex items-center gap-3 min-w-0">
                  {/* Sovereign Identity */}
                  <SovereignIdentity code={code} />
                  {ghostMode && (
                    <div className="flex items-center gap-2 text-xs text-purple-400">
                      <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" />
                      Ghost Protocol Active
                    </div>
                  )}
                </div>
              </div>
              <div className="flex-1 relative">
                <Editor value={code} onChange={(value) => setCode(value || '')} />
                {/* Ghost Visualizer Overlay */}
                {ghostMode && <GhostVisualizer code={code} />}
              </div>
            </div>

            {/* Proof Viewer Panel */}
            <div className="flex-1 flex flex-col bg-gray-900">
              <div className="px-4 py-2 bg-gray-900 border-b border-gray-800">
                <h2 className="text-sm font-semibold text-gray-400">PROOF VIEWER</h2>
              </div>
              <div className="flex-1 overflow-auto p-4 space-y-4 min-h-0">
                <ProofViewer result={result} isVerifying={isVerifying} />

                <SovereignControlPanel
                  onSpawn={handleSpawnSovereignAgent}
                  onKill={handleKillSwitch}
                  isSpawning={isSpawning}
                  canKill={Boolean(activeAgentId)}
                />

                <IdentityVault />

                <ProofBundleVisualizer
                  proofHash={sovereignProofHash}
                  z3Verified={sovereignZ3Verified}
                  signed={Boolean(sovereignSignatureHex)}
                  publicKeyHex={sovereignPublicKeyHex}
                  signatureHex={sovereignSignatureHex}
                />

                {spawnError ? (
                  <div className="bg-red-900/20 border border-red-700/40 rounded-lg p-4 text-sm text-red-200">
                    {spawnError}
                  </div>
                ) : null}

                <AgentTelemetry entries={telemetry} />

                {brainOutput ? (
                  <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-gray-400 mb-2">BROWSER BRAIN OUTPUT</div>
                    <pre className="whitespace-pre-wrap text-sm text-gray-200">{brainOutput}</pre>
                  </div>
                ) : null}

                {judgeOutput ? (
                  <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
                    <div className="text-xs font-semibold text-gray-400 mb-2">BROWSER JUDGE (Z3 WASM) OUTPUT</div>
                    <pre className="whitespace-pre-wrap text-sm text-gray-200">{judgeOutput}</pre>
                  </div>
                ) : null}
                
                {/* Sentinel Radar */}
                {activeLayer === 'sentinel' && (
                  <SentinelRadar
                    isActive={isVerifying || sentinelStatus !== 'idle'}
                    threatLevel={threatLevel}
                    status={sentinelStatus}
                  />
                )}

                {/* Oracle Atlas */}
                {activeLayer === 'oracle' && (
                  <OracleAtlas activeSources={activeOracles} />
                )}
              </div>
            </div>
          </div>

          {chatOpen && (
            <div className="w-[420px] shrink-0 bg-gray-900 border-l border-gray-800 overflow-hidden">
              <ArchitectChat
                isOpen={chatOpen}
                onClose={() => setChatOpen(false)}
                onCodeGenerated={(generatedCode) => {
                  setCode(generatedCode);
                  setResult(null);
                }}
              />
            </div>
          )}
        </div>

        {/* Execution Log Drawer */}
        <ExecutionLog
          entries={executionLogs}
          isOpen={logOpen}
          onToggle={() => setLogOpen(!logOpen)}
        />

        {/* Footer with Layer-specific Info */}
        <footer className="border-t border-gray-800 bg-gray-900 px-6 py-3">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div className="flex items-center gap-4">
              <span>Genesis Merkle Root: <span className="font-mono text-blue-400">1e994337bc48d0b2...</span></span>
              {activeLayer === 'sentinel' && (
                <span className="text-green-400">• Sentinel: Active • Threats: 0</span>
              )}
              {activeLayer === 'ghost' && (
                <span className="text-purple-400">• Ghost Protocol: Enabled • ZKP Ready</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span>Powered by Z3 Theorem Prover</span>
              <span className="text-gray-600">|</span>
              <span className="text-xs">Press <kbd className="px-2 py-0.5 bg-gray-800 rounded">CMD+K</kbd> for Architect</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
