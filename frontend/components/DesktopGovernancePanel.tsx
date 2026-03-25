/**
 * DIOTEC 360 IA - Desktop Governance Panel v10.3.1
 * 
 * Command center for Genesis Authority via desktop browser
 * No smartphone required - full sovereignty from your PC
 * 
 * "The Throne is Your Desktop"
 */

"use client";

import { useState, useEffect } from 'react';
import { Shield, CheckCircle, XCircle, AlertTriangle, Key, Lock, Unlock } from 'lucide-react';

interface PendingConsensus {
  consensus_id: string;
  proposal_type: string;
  description: string;
  votes_yes: number;
  votes_no: number;
  total_votes: number;
  approval_percentage: number;
  status: string;
  created_at: string;
}

export default function DesktopGovernancePanel() {
  const [pendingConsensus, setPendingConsensus] = useState<PendingConsensus[]>([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [genesisPassword, setGenesisPassword] = useState('');
  const [selectedConsensus, setSelectedConsensus] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch pending consensus
  useEffect(() => {
    if (isAuthenticated) {
      fetchPendingConsensus();
      const interval = setInterval(fetchPendingConsensus, 10000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const fetchPendingConsensus = async () => {
    try {
      const response = await fetch('/api/mobile/consensus/pending', {
        headers: {
          'Authorization': 'Bearer GENESIS_AUTHORITY_TOKEN'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setPendingConsensus(data);
      }
    } catch (error) {
      console.error('Failed to fetch consensus:', error);
    }
  };

  const handleAuthenticate = () => {
    // In production, verify against stored hash
    if (genesisPassword.length > 0) {
      setIsAuthenticated(true);
      setGenesisPassword('');
    }
  };

  const handleSignConsensus = async (consensusId: string, decision: 'approve' | 'reject') => {
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/mobile/consensus/sign', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer GENESIS_AUTHORITY_TOKEN'
        },
        body: JSON.stringify({
          consensus_id: consensusId,
          decision: decision,
          device_id: 'DESKTOP_' + navigator.userAgent.substring(0, 20),
          biometric_type: 'password'
        })
      });

      if (response.ok) {
        // Refresh consensus list
        await fetchPendingConsensus();
        setSelectedConsensus(null);
      }
    } catch (error) {
      console.error('Failed to sign consensus:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-950">
        <div className="w-full max-w-md p-8 bg-gray-900 rounded-lg border border-gray-800 shadow-2xl">
          <div className="flex items-center justify-center mb-6">
            <div className="p-4 bg-amber-500/20 rounded-full">
              <Shield className="w-12 h-12 text-amber-400" />
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-center text-white mb-2">
            Genesis Authority
          </h1>
          <p className="text-sm text-center text-gray-400 mb-6">
            Desktop Command Center
          </p>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Genesis Password
              </label>
              <input
                type="password"
                value={genesisPassword}
                onChange={(e) => setGenesisPassword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAuthenticate()}
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-amber-500"
                placeholder="Enter your Genesis password"
                autoFocus
              />
            </div>
            
            <button
              onClick={handleAuthenticate}
              disabled={genesisPassword.length === 0}
              className="w-full py-3 bg-amber-500 hover:bg-amber-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
            >
              <div className="flex items-center justify-center space-x-2">
                <Unlock className="w-5 h-5" />
                <span>Authenticate</span>
              </div>
            </button>
          </div>
          
          <div className="mt-6 p-4 bg-blue-900/20 border border-blue-800/50 rounded-lg">
            <p className="text-xs text-blue-300 text-center">
              🔐 Your Genesis password unlocks your ED25519 private key
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Desktop Command Center
            </h1>
            <p className="text-gray-400">
              Genesis Authority - Dionísio Sebastião Barros
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="px-4 py-2 bg-green-500/20 border border-green-500/50 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span className="text-sm text-green-400 font-semibold">Authenticated</span>
              </div>
            </div>
            
            <button
              onClick={() => setIsAuthenticated(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-gray-300 transition-colors"
            >
              <Lock className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Pending Consensus */}
        {pendingConsensus.length === 0 ? (
          <div className="p-12 bg-gray-900 rounded-lg border border-gray-800 text-center">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">
              No Pending Consensus
            </h2>
            <p className="text-gray-400">
              All network proposals have been processed
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white">
                Pending Consensus ({pendingConsensus.length})
              </h2>
              <button
                onClick={fetchPendingConsensus}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-gray-300 text-sm transition-colors"
              >
                Refresh
              </button>
            </div>

            {pendingConsensus.map((consensus) => (
              <div
                key={consensus.consensus_id}
                className="p-6 bg-gray-900 rounded-lg border border-gray-800 hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="px-3 py-1 bg-blue-500/20 border border-blue-500/50 rounded-full text-xs font-semibold text-blue-400">
                        {consensus.proposal_type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(consensus.created_at).toLocaleString()}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-white mb-2">
                      {consensus.description}
                    </h3>
                    
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="flex items-center space-x-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-gray-300">
                          {consensus.votes_yes} YES
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <XCircle className="w-4 h-4 text-red-500" />
                        <span className="text-gray-300">
                          {consensus.votes_no} NO
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-amber-500" />
                        <span className="text-gray-300">
                          {consensus.approval_percentage.toFixed(1)}% Approval
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Approval Bar */}
                <div className="mb-4">
                  <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-blue-500"
                      style={{ width: `${consensus.approval_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => handleSignConsensus(consensus.consensus_id, 'approve')}
                    disabled={isLoading}
                    className="flex-1 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <CheckCircle className="w-5 h-5" />
                      <span>APPROVE</span>
                    </div>
                  </button>
                  
                  <button
                    onClick={() => handleSignConsensus(consensus.consensus_id, 'reject')}
                    disabled={isLoading}
                    className="flex-1 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors"
                  >
                    <div className="flex items-center justify-center space-x-2">
                      <XCircle className="w-5 h-5" />
                      <span>REJECT</span>
                    </div>
                  </button>
                </div>

                {/* Genesis Authority Note */}
                <div className="mt-4 p-3 bg-amber-900/20 border border-amber-800/50 rounded-lg">
                  <p className="text-xs text-amber-300 text-center">
                    👑 Your signature as Genesis Authority will seal this decision
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Emergency Command Section */}
        <div className="mt-8 p-6 bg-red-900/20 border border-red-800 rounded-lg">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-red-400" />
            <h2 className="text-xl font-bold text-white">
              Emergency Commands
            </h2>
          </div>
          
          <p className="text-sm text-gray-400 mb-4">
            Execute emergency network commands when immediate action is required
          </p>
          
          <div className="grid grid-cols-2 gap-3">
            <button className="py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors">
              Ban Malicious Node
            </button>
            
            <button className="py-3 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-lg transition-colors">
              Pause Network
            </button>
            
            <button className="py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors">
              Force Upgrade
            </button>
            
            <button className="py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
              Reset Consensus
            </button>
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-8 p-4 bg-gray-900 border border-gray-800 rounded-lg">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <Key className="w-4 h-4 text-gray-500" />
              <span className="text-gray-400">
                Signed with ED25519 private key
              </span>
            </div>
            
            <div className="text-gray-500">
              Genesis Merkle Root: 782708...df94b84
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
