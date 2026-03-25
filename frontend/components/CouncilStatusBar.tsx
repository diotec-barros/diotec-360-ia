/**
 * DIOTEC 360 IA - Council Status Bar
 * 
 * The Eye of Providence - Real-time telemetry of the empire
 * Shows the system "breathing" with live indicators
 * 
 * "Where Intelligence Becomes Visible Wealth"
 */

"use client";

import { useEffect, useState, useRef } from 'react';
import { Brain, Zap, Shield, Activity, Coins, Database, CheckCircle } from 'lucide-react';

interface CouncilStatusBarProps {
  creditBalance: number;
  miningActive: boolean;
  merkleRoot: string | null;
  dualBrainMode: boolean;
  writerProvider?: string;
  criticProvider?: string;
}

export default function CouncilStatusBar({
  creditBalance,
  miningActive,
  merkleRoot,
  dualBrainMode,
  writerProvider = 'openai',
  criticProvider = 'anthropic',
}: CouncilStatusBarProps) {
  const [creditPulse, setCreditPulse] = useState(false);
  const [syncPulse, setSyncPulse] = useState(false);
  const [earnedToday, setEarnedToday] = useState(0);
  const lastCreditBalanceRef = useRef(creditBalance);
  const lastMerkleRootRef = useRef(merkleRoot);

  // Pulse animation when credits increase
  useEffect(() => {
    if (creditBalance > lastCreditBalanceRef.current) {
      const earned = creditBalance - lastCreditBalanceRef.current;
      lastCreditBalanceRef.current = creditBalance;
      
      // Schedule state updates asynchronously to avoid cascading renders
      const pulseTimer = setTimeout(() => {
        setEarnedToday(prev => prev + earned);
        setCreditPulse(true);
      }, 0);
      
      const resetTimer = setTimeout(() => setCreditPulse(false), 1000);
      
      return () => {
        clearTimeout(pulseTimer);
        clearTimeout(resetTimer);
      };
    }
    lastCreditBalanceRef.current = creditBalance;
  }, [creditBalance]);

  // Sync pulse animation when merkle root changes
  useEffect(() => {
    if (merkleRoot && merkleRoot !== lastMerkleRootRef.current) {
      lastMerkleRootRef.current = merkleRoot;
      
      // Schedule state update asynchronously
      const pulseTimer = setTimeout(() => setSyncPulse(true), 0);
      const resetTimer = setTimeout(() => setSyncPulse(false), 2000);
      
      return () => {
        clearTimeout(pulseTimer);
        clearTimeout(resetTimer);
      };
    }
  }, [merkleRoot]);

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'openai':
        return '🤖';
      case 'anthropic':
        return '🧠';
      case 'ollama':
        return '🦙';
      default:
        return '🤖';
    }
  };

  const getProviderName = (provider: string) => {
    switch (provider) {
      case 'openai':
        return 'GPT-4';
      case 'anthropic':
        return 'Claude';
      case 'ollama':
        return 'Llama';
      default:
        return provider;
    }
  };

  const formatMerkleRoot = (root: string | null) => {
    if (!root) return 'Not synced';
    return `${root.slice(0, 8)}...${root.slice(-8)}`;
  };

  const calculateEarnings = (credits: number) => {
    // 1 credit = $0.01
    return (credits * 0.01).toFixed(2);
  };

  return (
    <div className="flex items-center justify-between px-6 py-2 bg-gray-800 border-t border-gray-700 text-sm shadow-lg">
      {/* Left Section: System Status */}
      <div className="flex items-center space-x-6">
        {/* Dual-Brain Status */}
        {dualBrainMode && (
          <div className="flex items-center space-x-2 text-purple-400">
            <Brain className="w-4 h-4 animate-pulse" />
            <span className="font-semibold">Dual-Brain Active</span>
            <div className="flex items-center space-x-1 ml-2">
              <span className="text-xs">✍️ {getProviderIcon(writerProvider)} {getProviderName(writerProvider)}</span>
              <span className="text-gray-600">|</span>
              <span className="text-xs">🔍 {getProviderIcon(criticProvider)} {getProviderName(criticProvider)}</span>
            </div>
          </div>
        )}

        {/* Mining Status */}
        <div className="flex items-center space-x-2">
          <Activity className={`w-4 h-4 ${miningActive ? 'text-green-400 animate-pulse' : 'text-gray-500'}`} />
          <span className={`text-xs font-medium ${miningActive ? 'text-green-400' : 'text-gray-500'}`}>
            {miningActive ? 'Mining Active' : 'Mining Idle'}
          </span>
        </div>

        {/* Merkle Sync Status */}
        <div className="flex items-center space-x-2">
          <Shield 
            className={`w-4 h-4 ${syncPulse ? 'text-blue-400 animate-spin' : merkleRoot ? 'text-blue-400' : 'text-gray-500'}`} 
          />
          <span className="text-xs text-gray-400 font-mono">
            {formatMerkleRoot(merkleRoot)}
          </span>
          {merkleRoot && (
            <CheckCircle className="w-3 h-3 text-green-400" />
          )}
        </div>
      </div>

      {/* Right Section: Earnings Dashboard */}
      <div className="flex items-center space-x-6">
        {/* Credits Counter */}
        <div className={`flex items-center space-x-2 transition-all ${creditPulse ? 'scale-110' : 'scale-100'}`}>
          <Coins className={`w-4 h-4 ${creditPulse ? 'text-yellow-300 animate-bounce' : 'text-yellow-400'}`} />
          <div className="flex flex-col">
            <div className="flex items-center space-x-1">
              <span className="text-xs text-gray-400">Credits:</span>
              <span className={`text-sm font-bold ${creditPulse ? 'text-yellow-300' : 'text-yellow-400'}`}>
                {creditBalance.toLocaleString()}
              </span>
            </div>
          </div>
        </div>

        {/* Earnings Counter */}
        <div className="flex items-center space-x-2">
          <Zap className="w-4 h-4 text-green-400" />
          <div className="flex flex-col">
            <div className="flex items-center space-x-1">
              <span className="text-xs text-gray-400">Earned:</span>
              <span className="text-sm font-bold text-green-400">
                ${calculateEarnings(earnedToday)}
              </span>
            </div>
          </div>
        </div>

        {/* Total Value */}
        <div className="flex items-center space-x-2 px-3 py-1 bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-lg border border-green-700/30">
          <Database className="w-4 h-4 text-emerald-400" />
          <div className="flex items-center space-x-1">
            <span className="text-xs text-gray-400">Value:</span>
            <span className="text-sm font-bold text-emerald-400">
              ${calculateEarnings(creditBalance)}
            </span>
          </div>
        </div>

        {/* Lattice Connection */}
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          <span className="text-xs text-green-400 font-semibold">Connected to Lattice</span>
        </div>
      </div>
    </div>
  );
}
