/**
 * DIOTEC 360 IA - Sovereign Map Component v10.2.0
 * 
 * Real-time global visualization of DIOTEC 360 network nodes
 * Shows every computer mining logic proofs around the world
 * 
 * "Where Every Light is a Mind, Every Mind is Sovereign"
 */

"use client";

import { useState, useEffect } from 'react';
import { Globe, Users, Zap, TrendingUp, MapPin } from 'lucide-react';
import GlobalMap from './GlobalMap';
import { useGunLattice, type GunPeer, type ProofEvent } from '@/lib/useGunLattice';

interface SovereignMapProps {
  className?: string;
}

export default function SovereignMap({ className = '' }: SovereignMapProps) {
  const [selectedPeer, setSelectedPeer] = useState<GunPeer | null>(null);
  const [showStats, setShowStats] = useState(true);
  
  // Connect to GunDB P2P network
  const {
    peers,
    events,
    isConnected,
    error,
    metrics
  } = useGunLattice({
    enabled: true,
    gunPeers: [
      'https://gun-relay.diotec360.com/gun',
      'https://gun-us.herokuapp.com/gun',
      'https://gun-eu.herokuapp.com/gun'
    ],
    heartbeatTimeout: 30000
  });
  
  // Handle peer click
  const handlePeerClick = (peer: GunPeer) => {
    setSelectedPeer(peer);
  };
  
  // Close peer details
  const closePeerDetails = () => {
    setSelectedPeer(null);
  };
  
  // Format uptime
  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center space-x-3">
          <Globe className="w-6 h-6 text-blue-400" />
          <div>
            <h2 className="text-lg font-bold text-white">Sovereign Map</h2>
            <p className="text-xs text-gray-400">
              Real-time global network visualization
            </p>
          </div>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
          <span className="text-xs text-gray-400">
            {isConnected ? 'Connected to P2P Network' : 'Disconnected'}
          </span>
        </div>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-900/20 border-b border-red-800">
          <p className="text-sm text-red-400">⚠️ {error}</p>
        </div>
      )}
      
      {/* Stats Bar */}
      {showStats && (
        <div className="grid grid-cols-4 gap-4 p-4 bg-gray-900/50 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <Users className="w-5 h-5 text-blue-400" />
            <div>
              <p className="text-xs text-gray-400">Total Nodes</p>
              <p className="text-lg font-bold text-white">{metrics.total_peers}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-green-400" />
            <div>
              <p className="text-xs text-gray-400">Active Miners</p>
              <p className="text-lg font-bold text-white">{metrics.connected_peers}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-5 h-5 text-purple-400" />
            <div>
              <p className="text-xs text-gray-400">Proofs Validated</p>
              <p className="text-lg font-bold text-white">
                {metrics.total_proofs.toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <MapPin className="w-5 h-5 text-amber-400" />
            <div>
              <p className="text-xs text-gray-400">Continents</p>
              <p className="text-lg font-bold text-white">
                {Object.keys(metrics.peers_by_continent).length}
              </p>
            </div>
          </div>
        </div>
      )}
      
      {/* Map Container */}
      <div className="flex-1 relative">
        <GlobalMap
          peers={peers}
          events={events}
          onPeerClick={handlePeerClick}
        />
        
        {/* Peer Details Sidebar */}
        {selectedPeer && (
          <div className="absolute top-4 right-4 w-80 bg-gray-900/95 backdrop-blur-sm rounded-lg border border-gray-700 shadow-2xl">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-800">
              <h3 className="text-sm font-bold text-white">Node Details</h3>
              <button
                onClick={closePeerDetails}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            
            {/* Content */}
            <div className="p-4 space-y-4">
              {/* Location */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Location</p>
                <p className="text-sm font-semibold text-white">
                  {selectedPeer.location.city}, {selectedPeer.location.country}
                </p>
                <p className="text-xs text-gray-500">
                  {selectedPeer.location.continent}
                </p>
              </div>
              
              {/* Node ID */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Node ID</p>
                <p className="text-xs font-mono text-blue-400 break-all">
                  {selectedPeer.peer_id}
                </p>
              </div>
              
              {/* IP Address */}
              <div>
                <p className="text-xs text-gray-400 mb-1">IP Address</p>
                <p className="text-xs font-mono text-gray-300">
                  {selectedPeer.ip_address}
                </p>
              </div>
              
              {/* Status */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Status</p>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${
                    selectedPeer.status === 'connected' ? 'bg-green-500' :
                    selectedPeer.status === 'syncing' ? 'bg-amber-500' :
                    'bg-red-500'
                  }`} />
                  <span className="text-sm text-white capitalize">
                    {selectedPeer.status}
                  </span>
                </div>
              </div>
              
              {/* Uptime */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Uptime</p>
                <p className="text-sm text-white">
                  {formatUptime(selectedPeer.uptime_seconds)}
                </p>
              </div>
              
              {/* Proofs Validated */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Proofs Validated</p>
                <p className="text-lg font-bold text-green-400">
                  {selectedPeer.proofs_validated.toLocaleString()}
                </p>
              </div>
              
              {/* Last Seen */}
              <div>
                <p className="text-xs text-gray-400 mb-1">Last Seen</p>
                <p className="text-xs text-gray-300">
                  {formatTimestamp(selectedPeer.last_seen)}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Event Feed */}
      <div className="h-48 bg-gray-900 border-t border-gray-800 overflow-hidden">
        <div className="p-3 border-b border-gray-800">
          <h3 className="text-sm font-bold text-white">Network Activity</h3>
        </div>
        
        <div className="h-[calc(100%-3rem)] overflow-y-auto">
          {events.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <p className="text-sm text-gray-500">No recent activity</p>
            </div>
          ) : (
            <div className="space-y-1 p-2">
              {events.map((event) => (
                <div
                  key={event.event_id}
                  className="p-2 bg-gray-800/50 rounded text-xs hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`font-semibold ${
                      event.type === 'proof_validated' ? 'text-blue-400' :
                      event.type === 'merkle_sync' ? 'text-green-400' :
                      event.type === 'peer_connected' ? 'text-purple-400' :
                      'text-red-400'
                    }`}>
                      {event.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="text-gray-500">
                      {formatTimestamp(event.timestamp)}
                    </span>
                  </div>
                  <p className="text-gray-300">{event.message}</p>
                  {event.credits_earned && (
                    <p className="text-green-400 mt-1">
                      +{event.credits_earned} credits
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


