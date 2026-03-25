"use client";

/**
 * DIOTEC 360 IA Editor Studio - v4.0.0
 * 
 * "Your IDE Everywhere"
 * 
 * Full-featured web IDE with:
 * - Monaco Editor (VS Code's editor)
 * - Z3 Theorem Prover
 * - Dual-Brain Mode (Writer-Critic)
 * - Lattice P2P Sync
 * - Intelligence Harvester
 * - Project Dashboard
 * - Sovereign Identity
 * - Logic Miner Status
 * - Merkle Root Viewer
 */

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Loader2, Download, Settings, Brain, Shield, Zap, User, Coins, ShoppingCart, Database, Key, Globe } from 'lucide-react';
import { getHarvester } from '@/lib/intelligenceHarvester';
import { getMiner } from '@/lib/logicMiner';

// Dynamic imports for heavy components
const MonacoAutopilot = dynamic(() => import('@/components/MonacoAutopilot'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-gray-900">
      <div className="text-center">
        <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
        <p className="text-white text-lg">Loading DIOTEC 360 Studio...</p>
        <p className="text-gray-400 text-sm mt-2">Initializing Monaco Editor & Z3 Prover</p>
      </div>
    </div>
  ),
});

const KeyManagerModal = dynamic(() => import('@/components/KeyManagerModal'), {
  ssr: false,
});

const ProofViewer = dynamic(() => import('@/components/ProofViewer'), {
  ssr: false,
});

const SovereignControlPanel = dynamic(() => import('@/components/SovereignControlPanel'), {
  ssr: false,
});

const CreditPurchaseModal = dynamic(() => import('@/components/CreditPurchaseModal'), {
  ssr: false,
});

const IntelligenceHarvesterPanel = dynamic(() => import('@/components/IntelligenceHarvesterPanel'), {
  ssr: false,
});

const DualBrainPanel = dynamic(() => import('@/components/DualBrainPanel'), {
  ssr: false,
});

const CouncilStatusBar = dynamic(() => import('@/components/CouncilStatusBar'), {
  ssr: false,
});

const LatticeSyncPanel = dynamic(() => import('@/components/LatticeSyncPanel'), {
  ssr: false,
});

// Genesis Template - Proven Banking Contract
const GENESIS_TEMPLATE = `// 🏛️ DIOTEC 360 IA Editor Studio - Genesis Template
// "Your IDE Everywhere" - Code with Mathematical Proofs
// 
// This is a PROVEN banking contract template
// Every assertion is verified by Z3 Theorem Prover

intent secure_deposit(amount: decimal, account_id: string) -> bool {
  // Pre-conditions (Security Guards)
  require amount > 0;
  require amount <= 1000000;  // Max deposit limit
  require account_id != "";
  require account_exists(account_id);
  
  // Get current state
  let old_balance = get_balance(account_id);
  let old_total = total_supply();
  
  // Execute transaction
  let new_balance = old_balance + amount;
  set_balance(account_id, new_balance);
  
  // Post-conditions (Mathematical Proofs)
  assert new_balance == old_balance + amount;  // Balance increased correctly
  assert total_supply() == old_total + amount; // Conservation law
  assert get_balance(account_id) > old_balance; // Monotonic increase
  
  emit DepositEvent(account_id, amount, new_balance);
  
  return true;
}

intent secure_withdraw(amount: decimal, account_id: string) -> bool {
  // Pre-conditions
  require amount > 0;
  require account_id != "";
  require account_exists(account_id);
  
  let old_balance = get_balance(account_id);
  require old_balance >= amount;  // Sufficient funds
  
  let old_total = total_supply();
  
  // Execute transaction
  let new_balance = old_balance - amount;
  set_balance(account_id, new_balance);
  
  // Post-conditions (Mathematical Proofs)
  assert new_balance == old_balance - amount;
  assert total_supply() == old_total - amount;
  assert get_balance(account_id) < old_balance;
  assert new_balance >= 0;  // No negative balances
  
  emit WithdrawEvent(account_id, amount, new_balance);
  
  return true;
}

// 🛡️ DIOTEC 360 CERTIFIED
// This code has been mathematically proven to be correct
// No bugs, no exploits, no vulnerabilities
`;

export default function StudioPage() {
  const [code, setCode] = useState(GENESIS_TEMPLATE);
  const [proofResult, setProofResult] = useState<{
    verdict?: string; 
    proof?: string; 
    merkle_root?: string; 
    error?: string;
    status?: string;
    message?: string;
  } | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [showDashboard, setShowDashboard] = useState(true);
  const [dualBrainMode, setDualBrainMode] = useState(false);
  const [creditBalance, setCreditBalance] = useState(0);
  const [miningActive, setMiningActive] = useState(false);
  const [merkleRoot, setMerkleRoot] = useState<string | null>(null);
  const [userName, setUserName] = useState('Dionísio Sebastião');
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [showHarvesterPanel, setShowHarvesterPanel] = useState(false);
  const [showDualBrainPanel, setShowDualBrainPanel] = useState(false);
  const [showKeyManager, setShowKeyManager] = useState(false);
  const [showSyncPanel, setShowSyncPanel] = useState(false);

  // Auto-save to localStorage
  useEffect(() => {
    const timer = setTimeout(() => {
      localStorage.setItem('diotec360-studio-code', code);
    }, 1000);
    return () => clearTimeout(timer);
  }, [code]);

  // Load saved state
  useEffect(() => {
    const saved = localStorage.getItem('diotec360-studio-code');
    if (saved) {
      setCode(saved);
    }

    const credits = localStorage.getItem('diotec360-credits');
    if (credits) {
      setCreditBalance(parseInt(credits));
    }

    const mining = localStorage.getItem('diotec360-mining-active');
    const isMiningActive = mining === 'true';
    setMiningActive(isMiningActive);

    const lastMerkle = localStorage.getItem('diotec360-last-merkle-root');
    if (lastMerkle) {
      setMerkleRoot(lastMerkle);
    }

    const name = localStorage.getItem('diotec360-user-name');
    if (name) {
      setUserName(name);
    }

    // Setup Logic Miner event listener
    const miner = getMiner();
    
    // Auto-start mining if it was active
    if (isMiningActive) {
      miner.startMining();
    }

    const unsubscribe = miner.onMiningEvent((event) => {
      if (event.type === 'credits_earned') {
        const newBalance = event.data.total;
        setCreditBalance(newBalance);
        localStorage.setItem('diotec360-credits', newBalance.toString());
      }
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });
      const result = await response.json();
      setProofResult(result);
      
      if (result.verdict === 'PROVED' && result.merkle_root) {
        setMerkleRoot(result.merkle_root);
        localStorage.setItem('diotec360-last-merkle-root', result.merkle_root);
        
        // Award credits for successful proof
        const newCredits = creditBalance + 10;
        setCreditBalance(newCredits);
        localStorage.setItem('diotec360-credits', newCredits.toString());
        
        // Harvest proven code for training
        const harvester = getHarvester();
        await harvester.harvest({
          prompt: 'User verification request',
          aiOutput: code,
          finalCode: code,
          judgeVerdict: 'PROVED',
          z3Proof: result.proof,
          aiProvider: 'user',
          aiModel: 'manual',
          language: 'diotec360'
        });
      }
    } catch (error) {
      console.error('Verification error:', error);
      setProofResult({ error: 'Failed to verify code' });
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSyncToCloud = async () => {
    setIsSyncing(true);
    try {
      const response = await fetch('/api/lattice/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          code,
          timestamp: Date.now(),
          device: 'web-studio',
          merkle_root: merkleRoot
        }),
      });
      const result = await response.json();
      console.log('Synced to Lattice:', result);
    } catch (error) {
      console.error('Sync error:', error);
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'contract.ae';
    a.click();
    URL.revokeObjectURL(url);
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 bg-gray-800 border-b border-gray-700 shadow-lg">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-blue-400" />
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
                DIOTEC 360 IA Studio
              </h1>
              <p className="text-xs text-gray-400">Your IDE Everywhere</p>
            </div>
          </div>
          <span className="px-2 py-1 text-xs bg-blue-600 rounded-full">v4.0.0</span>
        </div>

        <div className="flex items-center space-x-2">
          {/* Dual-Brain Toggle */}
          <button
            onClick={() => {
              setDualBrainMode(!dualBrainMode);
              setShowDualBrainPanel(!dualBrainMode);
            }}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
              dualBrainMode
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 shadow-lg'
                : 'bg-gray-700 hover:bg-gray-600'
            }`}
            title="Toggle Dual-Brain Mode (Writer-Critic)"
          >
            <Brain className="w-4 h-4" />
            <span className="text-sm font-medium">Dual-Brain</span>
          </button>

          {/* Key Manager Button */}
          <button
            onClick={() => setShowKeyManager(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all"
            title="Manage API Keys (BYOK)"
          >
            <Key className="w-4 h-4" />
            <span className="text-sm font-medium">Keys</span>
          </button>

          {/* Network Button */}
          <button
            onClick={() => setShowSyncPanel(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all shadow-lg"
            title="View Lattice P2P Network"
          >
            <Globe className="w-4 h-4" />
            <span className="text-sm font-medium">Network</span>
          </button>

          {/* Verify Button */}
          <button
            onClick={handleVerify}
            disabled={isVerifying}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-lg transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isVerifying ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Shield className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">Verify with Z3</span>
          </button>

          {/* Sync Button */}
          <button
            onClick={handleSyncToCloud}
            disabled={isSyncing}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-lg transition-all shadow-lg disabled:opacity-50"
            title="Sync to Lattice P2P Network"
          >
            {isSyncing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">Sync</span>
          </button>

          {/* Download Button */}
          <button
            onClick={handleDownload}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-all"
          >
            <Download className="w-4 h-4" />
          </button>

          {/* Dashboard Toggle */}
          <button
            onClick={() => setShowDashboard(!showDashboard)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
              showDashboard ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-700 hover:bg-gray-600'
            }`}
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Editor */}
        <div className={`flex-1 transition-all ${showDashboard ? 'mr-96' : ''}`}>
          <MonacoAutopilot
            initialCode={code}
            onCodeChange={setCode}
            language="DIOTEC360"
          />
        </div>

        {/* Sidebar - Dashboard */}
        {showDashboard && (
          <div className="w-96 border-l border-gray-700 overflow-y-auto bg-gray-800 shadow-2xl">
            {/* Sovereign Identity */}
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <User className="w-5 h-5 mr-2 text-blue-400" />
                Sovereign Identity
              </h3>
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {getInitials(userName)}
                  </div>
                  <div>
                    <p className="text-sm font-semibold">{userName}</p>
                    <p className="text-xs text-gray-400">Sovereign Creator</p>
                    <p className="text-xs text-blue-400 mt-1">🏛️ DIOTEC 360</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Credit Balance & Mining */}
            <div className="p-6 border-b border-gray-700">
              <h3 className="text-lg font-bold mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2 text-yellow-400" />
                Logic Miner
              </h3>
              <div className="space-y-3">
                <div className="bg-gradient-to-br from-yellow-900/20 to-orange-900/20 rounded-xl p-4 border border-yellow-700/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-300">Credits</span>
                    <span className="text-3xl font-bold text-yellow-400 flex items-center">
                      <Coins className="w-6 h-6 mr-2" />
                      {creditBalance}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400 mb-3">+10 per proven contract</p>
                  <button
                    onClick={() => setShowPurchaseModal(true)}
                    className="w-full flex items-center justify-center px-4 py-2 bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 rounded-lg transition-all text-sm font-semibold text-white"
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    Buy More Credits
                  </button>
                </div>
                <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl p-4 border border-gray-700">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm text-gray-300">Mining Status</span>
                    <button
                      onClick={() => {
                        const miner = getMiner();
                        if (miningActive) {
                          miner.stopMining();
                          setMiningActive(false);
                          localStorage.setItem('diotec360-mining-active', 'false');
                        } else {
                          miner.startMining();
                          setMiningActive(true);
                          localStorage.setItem('diotec360-mining-active', 'true');
                        }
                      }}
                      className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                        miningActive
                          ? 'bg-green-600 hover:bg-green-700 text-white'
                          : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                      }`}
                    >
                      {miningActive ? 'Stop Mining' : 'Start Mining'}
                    </button>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`w-2 h-2 rounded-full ${
                      miningActive ? 'bg-green-400 animate-pulse' : 'bg-gray-500'
                    }`} />
                    <span className={`text-sm font-semibold ${
                      miningActive ? 'text-green-400' : 'text-gray-500'
                    }`}>
                      {miningActive ? 'Active' : 'Idle'}
                    </span>
                  </div>
                  {miningActive && (
                    <p className="text-xs text-gray-400 mt-2">
                      Mining when idle (30s)
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Merkle Root */}
            {merkleRoot && (
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-green-400" />
                  Merkle Root
                </h3>
                <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 rounded-xl p-4 border border-green-700/30">
                  <p className="text-xs font-mono text-green-400 break-all leading-relaxed">
                    {merkleRoot}
                  </p>
                  <p className="text-xs text-gray-400 mt-2">✅ Cryptographically Sealed</p>
                </div>
              </div>
            )}

            {/* Proof Result */}
            {proofResult && (
              <div className="p-6 border-b border-gray-700">
                <h3 className="text-lg font-bold mb-4 flex items-center">
                  <Shield className="w-5 h-5 mr-2 text-blue-400" />
                  Proof Result
                </h3>
                <ProofViewer 
                  result={{
                    status: (proofResult.verdict === 'PROVED' ? 'PROVED' : proofResult.error ? 'ERROR' : 'FAILED') as 'PROVED' | 'ERROR' | 'FAILED',
                    message: proofResult.message || (proofResult.verdict === 'PROVED' ? 'Code verified successfully' : proofResult.error || 'Verification failed'),
                    proof: proofResult.proof,
                    audit_trail: []
                  }} 
                  isVerifying={isVerifying} 
                />
              </div>
            )}

            {/* Control Panel */}
            <div className="p-6">
              <h3 className="text-lg font-bold mb-4">Control Panel</h3>
              <SovereignControlPanel 
                onSpawn={async () => {}}
                onKill={async () => {}}
                isSpawning={false}
                canKill={false}
              />
              
              {/* Intelligence Harvester Button */}
              <button
                onClick={() => setShowHarvesterPanel(true)}
                className="w-full mt-4 flex items-center justify-center px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg transition-all text-sm font-semibold text-white"
              >
                <Database className="w-4 h-4 mr-2" />
                View Training Data
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Council Status Bar - The Eye of Providence */}
      <CouncilStatusBar
        creditBalance={creditBalance}
        miningActive={miningActive}
        merkleRoot={merkleRoot}
        dualBrainMode={dualBrainMode}
        writerProvider="openai"
        criticProvider="anthropic"
      />

      {/* Credit Purchase Modal */}
      <CreditPurchaseModal
        isOpen={showPurchaseModal}
        onClose={() => setShowPurchaseModal(false)}
        currentBalance={creditBalance}
        onPurchaseComplete={(newBalance) => {
          setCreditBalance(newBalance);
          localStorage.setItem('diotec360-credits', newBalance.toString());
        }}
      />

      {/* Intelligence Harvester Panel */}
      <IntelligenceHarvesterPanel
        isOpen={showHarvesterPanel}
        onClose={() => setShowHarvesterPanel(false)}
      />

      {/* Dual-Brain Panel */}
      <DualBrainPanel
        isOpen={showDualBrainPanel}
        onClose={() => {
          setShowDualBrainPanel(false);
          setDualBrainMode(false);
        }}
        onGenerate={(result) => {
          // Update editor with final code
          setCode(result.finalCode);
          
          // Auto-verify if Judge proved it
          if (result.judgeVerdict === 'PROVED') {
            setProofResult({
              verdict: 'PROVED',
              proof: result.z3Proof,
            });
          }
          
          // Harvest the proven code
          if (result.judgeVerdict === 'PROVED') {
            const harvester = getHarvester();
            harvester.harvest({
              prompt: 'Dual-Brain generation',
              aiOutput: result.writerOutput,
              finalCode: result.finalCode,
              judgeVerdict: 'PROVED',
              z3Proof: result.z3Proof,
              aiProvider: 'dual-brain',
              aiModel: 'writer-critic',
              language: 'diotec360'
            });
          }
        }}
      />

      {/* Key Manager Modal */}
      <KeyManagerModal
        isOpen={showKeyManager}
        onClose={() => setShowKeyManager(false)}
        onKeysUpdated={() => {
          console.log('API keys updated');
        }}
      />

      {/* Lattice Sync Panel */}
      <LatticeSyncPanel
        isOpen={showSyncPanel}
        onClose={() => setShowSyncPanel(false)}
        merkleRoot={merkleRoot}
      />
    </div>
  );
}
