/**
 * DIOTEC 360 IA - Network Metrics Component v10.0.9
 * 
 * Aggregate network statistics and health indicators
 * Geographic diversity scoring and continent distribution
 * 
 * "Where Numbers Tell the Story of Global Consensus"
 */

"use client";

import { useMemo } from 'react';
import { Globe, Activity, Shield, TrendingUp, AlertCircle } from 'lucide-react';
import type { GunPeer } from '@/lib/useGunLattice';

interface NetworkMetricsProps {
  peers: GunPeer[];
}

interface ContinentStats {
  [continent: string]: number;
}

export default function NetworkMetrics({ peers }: NetworkMetricsProps) {
  // Calculate metrics
  const metrics = useMemo(() => {
    const total = peers.length;
    const connected = peers.filter(p => p.status === 'connected').length;
    const syncing = peers.filter(p => p.status === 'syncing').length;
    
    // Peers by continent
    const byContinent: ContinentStats = {};
    peers.forEach(peer => {
      const continent = peer.location.continent || 'Unknown';
      byContinent[continent] = (byContinent[continent] || 0) + 1;
    });
    
    // Total proofs validated
    const totalProofs = peers.reduce((sum, peer) => sum + peer.proofs_validated, 0);
    
    // Geographic diversity score (0-100)
    // Higher score = more evenly distributed across continents
    const continents = Object.keys(byContinent).length;
    let diversityScore = 0;
    
    if (continents > 0 && total > 0) {
      // Calculate entropy
      const entropy = Object.values(byContinent)
        .map(count => {
          const p = count / total;
          return p > 0 ? -p * Math.log2(p) : 0;
        })
        .reduce((a, b) => a + b, 0);
      
      // Normalize to 0-100 (max entropy = log2(continents))
      const maxEntropy = Math.log2(continents);
      diversityScore = Math.round((entropy / maxEntropy) * 100);
    }
    
    // Consensus percentage (connected / total)
    const consensusPercentage = total > 0 ? Math.round((connected / total) * 100) : 0;
    
    return {
      total,
      connected,
      syncing,
      offline: total - connected - syncing,
      byContinent,
      totalProofs,
      diversityScore,
      consensusPercentage,
    };
  }, [peers]);

  // Get continent emoji
  const getContinentEmoji = (continent: string): string => {
    const emojiMap: Record<string, string> = {
      'Africa': '🌍',
      'Europe': '🇪🇺',
      'Asia': '🌏',
      'North America': '🌎',
      'South America': '🌎',
      'Oceania': '🌏',
      'Antarctica': '🧊',
      'Unknown': '❓',
    };
    return emojiMap[continent] || '🌐';
  };

  // Get diversity score color
  const getDiversityColor = (score: number): string => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-4">
      {/* Overall Stats */}
      <div className="grid grid-cols-2 gap-3">
        {/* Total Peers */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Total Nodes</span>
            <Globe className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{metrics.total}</div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.connected} connected
          </div>
        </div>

        {/* Consensus */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Consensus</span>
            <Shield className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-2xl font-bold text-green-400">
            {metrics.consensusPercentage}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {metrics.connected}/{metrics.total} agree
          </div>
        </div>

        {/* Total Proofs */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Proofs Validated</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {metrics.totalProofs.toLocaleString()}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            All-time total
          </div>
        </div>

        {/* Diversity Score */}
        <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-400">Diversity</span>
            <TrendingUp className="w-4 h-4 text-yellow-400" />
          </div>
          <div className={`text-2xl font-bold ${getDiversityColor(metrics.diversityScore)}`}>
            {metrics.diversityScore}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Geographic spread
          </div>
        </div>
      </div>

      {/* Continent Distribution */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center">
          <Globe className="w-4 h-4 mr-2 text-blue-400" />
          Geographic Distribution
        </h3>
        
        <div className="space-y-2">
          {Object.entries(metrics.byContinent)
            .sort(([, a], [, b]) => b - a)
            .map(([continent, count]) => {
              const percentage = metrics.total > 0 ? (count / metrics.total) * 100 : 0;
              
              return (
                <div key={continent}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-400 flex items-center">
                      <span className="mr-1">{getContinentEmoji(continent)}</span>
                      {continent}
                    </span>
                    <span className="text-gray-300 font-semibold">
                      {count} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
        </div>
      </div>

      {/* Health Alerts */}
      {(metrics.diversityScore < 50 || metrics.consensusPercentage < 80) && (
        <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
          <div className="flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-xs font-semibold text-yellow-400 mb-1">
                Network Health Warning
              </p>
              <div className="text-xs text-yellow-300 space-y-1">
                {metrics.diversityScore < 50 && (
                  <p>• Low geographic diversity ({metrics.diversityScore}/100)</p>
                )}
                {metrics.consensusPercentage < 80 && (
                  <p>• Low consensus ({metrics.consensusPercentage}% agreement)</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Status Breakdown */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <h3 className="text-sm font-semibold text-gray-300 mb-3">
          Node Status
        </h3>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-gray-400">Connected</span>
            </div>
            <span className="text-gray-300 font-semibold">{metrics.connected}</span>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              <span className="text-gray-400">Syncing</span>
            </div>
            <span className="text-gray-300 font-semibold">{metrics.syncing}</span>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-gray-400">Offline</span>
            </div>
            <span className="text-gray-300 font-semibold">{metrics.offline}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

