/**
 * DIOTEC 360 IA - Lattice Sync Panel v10.0.8
 * 
 * "The Global Vision" - See your empire breathing across the planet
 * Real-time P2P network visualization with LIVE DATA
 * 
 * "Where the Network Becomes Real"
 */

"use client";

import { useRef, useState, useEffect } from 'react';
import { X, Globe, Shield, Activity, Wifi, AlertCircle, RefreshCw, MapPin, CheckCircle } from 'lucide-react';
import { useLatticeData } from '@/lib/useLatticeData';

interface LatticeSyncPanelProps {
  isOpen: boolean;
  onClose: () => void;
  merkleRoot: string | null;
}

export default function LatticeSyncPanel({
  isOpen,
  onClose,
  merkleRoot,
}: LatticeSyncPanelProps) {
  const eventStreamRef = useRef<HTMLDivElement>(null);
  const [currentTime, setCurrentTime] = useState(() => Date.now());
  
  // Real-time data from Lattice network
  const {
    peers,
    consensus,
    events,
    isLoading,
    error,
    syncStatus,
    manualSync,
  } = useLatticeData({ enabled: isOpen });

  // Update current time when events change (for timestamp formatting)
  useEffect(() => {
    const timer = setTimeout(() => {
      setCurrentTime(Date.now());
    }, 0);
    return () => clearTimeout(timer);
  }, [events]);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
  };

  const formatTimestamp = (timestamp: number) => {
    const seconds = Math.floor((currentTime - timestamp) / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ago`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected': return 'bg-green-400';
      case 'syncing': return 'bg-yellow-400';
      case 'offline': return 'bg-red-400';
      default: return 'bg-gray-400';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-[900px] h-[700px] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gradient-to-r from-blue-900/30 to-purple-900/30">
          <div className="flex items-center space-x-3">
            <Globe className="w-6 h-6 text-blue-400 animate-pulse" />
            <div>
              <h2 className="text-xl font-bold text-white">Lattice P2P Network</h2>
              <p className="text-xs text-gray-400">Global Verification Mesh</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-lg transition-all"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left Section - Network Overview & Peers */}
          <div className="w-1/2 border-r border-gray-700 flex flex-col">
            {/* Network Overview */}
            <div className="p-6 border-b border-gray-700 bg-gradient-to-br from-gray-800 to-gray-900">
              <h3 className="text-sm font-bold text-gray-300 mb-4 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-blue-400" />
                Network Status
              </h3>
              
              {isLoading ? (
                <div className="text-center py-8">
                  <RefreshCw className="w-8 h-8 animate-spin text-blue-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-400">Connecting to Lattice...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Error Banner */}
                  {error && (
                    <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 mb-4">
                      <div className="flex items-center space-x-2">
                        <AlertCircle className="w-4 h-4 text-red-400" />
                        <span className="text-sm text-red-400">{error}</span>
                      </div>
                    </div>
                  )}

                  {/* Peer Count */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Connected Nodes</span>
                    <span className="text-2xl font-bold text-blue-400 flex items-center">
                      <Wifi className="w-5 h-5 mr-2" />
                      {peers.length}
                    </span>
                  </div>

                  {/* Consensus */}
                  {consensus && (
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-400">Consensus</span>
                        <span className="text-lg font-bold text-green-400">
                          {consensus.consensus_percentage}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${consensus.consensus_percentage}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {consensus.agreeing_peers} of {consensus.total_peers} nodes agree
                      </p>
                    </div>
                  )}

                  {/* Sync Status */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Sync Status</span>
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${
                        syncStatus === 'synced' ? 'bg-green-400 animate-pulse' :
                        syncStatus === 'syncing' ? 'bg-yellow-400 animate-pulse' :
                        'bg-red-400'
                      }`} />
                      <span className={`text-sm font-semibold ${
                        syncStatus === 'synced' ? 'text-green-400' :
                        syncStatus === 'syncing' ? 'text-yellow-400' :
                        'text-red-400'
                      }`}>
                        {syncStatus === 'synced' ? 'Synced' :
                         syncStatus === 'syncing' ? 'Syncing...' :
                         'Out of Sync'}
                      </span>
                    </div>
                  </div>

                  {/* Merkle Root */}
                  {merkleRoot && (
                    <div className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <div className="flex items-center space-x-2 mb-1">
                        <Shield className="w-4 h-4 text-blue-400" />
                        <span className="text-xs text-gray-400">Current Merkle Root</span>
                      </div>
                      <p className="text-xs font-mono text-blue-400 break-all">
                        {merkleRoot.slice(0, 16)}...{merkleRoot.slice(-16)}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Peer List */}
            <div className="flex-1 overflow-y-auto p-4">
              <h3 className="text-sm font-bold text-gray-300 mb-3 flex items-center sticky top-0 bg-gray-900 py-2">
                <MapPin className="w-4 h-4 mr-2 text-purple-400" />
                Active Peers
              </h3>
              <div className="space-y-2">
                {peers.map((peer) => (
                  <div
                    key={peer.peer_id}
                    className="bg-gray-800 rounded-lg p-3 border border-gray-700 hover:border-gray-600 transition-all cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`w-2 h-2 rounded-full ${getStatusColor(peer.status)} ${
                          peer.status === 'connected' ? 'animate-pulse' : ''
                        }`} />
                        <span className="text-sm font-semibold text-white">{peer.location}</span>
                      </div>
                      {peer.status === 'connected' && (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      )}
                    </div>
                    <p className="text-xs font-mono text-gray-500 mb-2">{peer.peer_id}</p>
                    <div className="flex items-center justify-between text-xs text-gray-400">
                      <span>Uptime: {formatUptime(peer.uptime_seconds)}</span>
                      <span>Proofs: {peer.proofs_validated.toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Section - Verification Stream */}
          <div className="w-1/2 flex flex-col">
            <div className="p-6 border-b border-gray-700 bg-gradient-to-br from-gray-800 to-gray-900">
              <h3 className="text-sm font-bold text-gray-300 flex items-center">
                <Activity className="w-4 h-4 mr-2 text-green-400 animate-pulse" />
                Live Verification Stream
              </h3>
              <p className="text-xs text-gray-500 mt-1">Real-time network activity</p>
            </div>

            {/* Event Feed */}
            <div
              ref={eventStreamRef}
              className="flex-1 overflow-y-auto p-4 space-y-2"
            >
              {events.length === 0 ? (
                <div className="text-center py-12">
                  <Activity className="w-12 h-12 text-gray-600 mx-auto mb-3 animate-pulse" />
                  <p className="text-sm text-gray-500">Waiting for network events...</p>
                </div>
              ) : (
                events.map((event) => (
                  <div
                    key={event.event_id}
                    className="bg-gray-800 rounded-lg p-3 border border-gray-700 animate-fade-in"
                  >
                    <p className="text-sm text-white mb-1">{event.message}</p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span className="font-mono">{event.peer_id.slice(0, 12)}...</span>
                      <span>{formatTimestamp(event.timestamp)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-gray-700 bg-gray-800">
          <div className="flex items-center space-x-4 text-xs text-gray-400">
            <span>Last update: {consensus ? formatTimestamp(consensus.last_update) : 'Never'}</span>
            {consensus && consensus.consensus_percentage < 80 && (
              <div className="flex items-center space-x-1 text-yellow-400">
                <AlertCircle className="w-3 h-3" />
                <span>Low consensus warning</span>
              </div>
            )}
          </div>
          <button
            onClick={manualSync}
            disabled={syncStatus === 'syncing'}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-all text-sm font-semibold"
          >
            <RefreshCw className={`w-4 h-4 ${syncStatus === 'syncing' ? 'animate-spin' : ''}`} />
            <span>Manual Sync</span>
          </button>
        </div>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}
