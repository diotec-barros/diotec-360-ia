/**
 * DIOTEC 360 IA - GunDB Lattice Hook v10.0.9
 * 
 * Real-time P2P network synchronization via GunDB Gossip Protocol
 * Replaces HTTP polling with true peer-to-peer data flow
 * 
 * "Where Polling Dies and Gossip Lives"
 */

import { useEffect, useState, useCallback, useRef } from 'react';

// GunDB types (will be properly typed when gun is installed)
type GunInstance = any;
type GunNode = any;

export interface GunPeer {
  peer_id: string;
  ip_address: string;
  location: {
    city: string;
    country: string;
    country_code: string;
    lat: number;
    lon: number;
    continent: string;
  };
  status: 'connected' | 'syncing' | 'offline';
  uptime_seconds: number;
  proofs_validated: number;
  last_seen: number;
  heartbeat_interval: number;
}

export interface ProofEvent {
  event_id: string;
  type: 'proof_validated' | 'merkle_sync' | 'peer_connected' | 'peer_disconnected';
  message: string;
  source_peer_id: string;
  destination_peer_id?: string;
  timestamp: number;
  credits_earned?: number;
}

interface UseGunLatticeOptions {
  enabled: boolean;
  gunPeers?: string[]; // GunDB relay servers
  heartbeatTimeout?: number; // Milliseconds to consider peer offline
}

export function useGunLattice(options: UseGunLatticeOptions) {
  const {
    enabled,
    gunPeers = [
      process.env.NEXT_PUBLIC_GUNDB_RELAY || 'https://gun-manhattan.herokuapp.com/gun'
    ],
    heartbeatTimeout = 30000, // 30 seconds
  } = options;
  
  const [peers, setPeers] = useState<GunPeer[]>([]);
  const [events, setEvents] = useState<ProofEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const gunRef = useRef<GunInstance | null>(null);
  const peerSubscriptionsRef = useRef<Map<string, any>>(new Map());
  const heartbeatTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize GunDB connection
  useEffect(() => {
    if (!enabled) return;

    const initGun = async () => {
      try {
        // Dynamic import Gun.js (will be installed via npm)
        const Gun = (await import('gun')).default;
        
        // Initialize Gun instance
        const gun = Gun({
          peers: gunPeers,
          localStorage: false, // Don't persist locally (use server as source of truth)
          radisk: false,
        });
        
        gunRef.current = gun;
        setIsConnected(true);
        setError(null);
        
        console.log('🌐 Connected to GunDB network:', gunPeers);
        
        // Subscribe to peers
        subscribeToPeers(gun);
        
        // Subscribe to events
        subscribeToEvents(gun);
        
        // Start heartbeat monitor
        startHeartbeatMonitor();
        
      } catch (err) {
        console.error('Failed to initialize GunDB:', err);
        setError('Failed to connect to P2P network');
        setIsConnected(false);
        
        // Fallback to HTTP polling if GunDB fails
        console.warn('Falling back to HTTP polling...');
      }
    };

    initGun();

    return () => {
      // Cleanup subscriptions
      peerSubscriptionsRef.current.forEach((unsub) => {
        if (typeof unsub === 'function') unsub();
      });
      peerSubscriptionsRef.current.clear();
      
      // Stop heartbeat monitor
      if (heartbeatTimerRef.current) {
        clearInterval(heartbeatTimerRef.current);
      }
      
      gunRef.current = null;
      setIsConnected(false);
    };
  }, [enabled, gunPeers.join(',')]);

  // Subscribe to all peers in network
  const subscribeToPeers = useCallback((gun: GunInstance) => {
    // Get all peers
    gun.get('lattice').get('peers').map().on((peerData: GunPeer | null, peerId: string) => {
      if (!peerData) {
        // Peer was removed
        setPeers(prev => prev.filter(p => p.peer_id !== peerId));
        return;
      }
      
      // Validate peer data
      if (!peerData.peer_id || !peerData.location) {
        console.warn('Invalid peer data:', peerData);
        return;
      }
      
      // Update or add peer
      setPeers(prev => {
        const existing = prev.find(p => p.peer_id === peerId);
        
        if (existing) {
          // Update existing peer
          return prev.map(p => p.peer_id === peerId ? peerData : p);
        } else {
          // Add new peer
          console.log('🌍 New peer discovered:', peerData.location.city, peerData.location.country);
          return [...prev, peerData];
        }
      });
    });
  }, []);

  // Subscribe to proof events
  const subscribeToEvents = useCallback((gun: GunInstance) => {
    gun.get('lattice').get('events').map().on((eventData: ProofEvent | null, eventId: string) => {
      if (!eventData) return;
      
      // Validate event data
      if (!eventData.event_id || !eventData.type) {
        console.warn('Invalid event data:', eventData);
        return;
      }
      
      // Add event to feed (limit to 50)
      setEvents(prev => {
        // Check if event already exists
        if (prev.some(e => e.event_id === eventId)) {
          return prev;
        }
        
        console.log('⚡ New event:', eventData.message);
        return [eventData, ...prev].slice(0, 50);
      });
    });
  }, []);

  // Monitor peer heartbeats and remove stale peers
  const startHeartbeatMonitor = useCallback(() => {
    heartbeatTimerRef.current = setInterval(() => {
      const now = Date.now();
      
      setPeers(prev => {
        return prev.filter(peer => {
          const timeSinceLastSeen = now - peer.last_seen;
          
          if (timeSinceLastSeen > heartbeatTimeout) {
            console.log('💀 Peer timeout:', peer.location.city, peer.location.country);
            return false; // Remove stale peer
          }
          
          return true;
        });
      });
    }, 5000); // Check every 5 seconds
  }, [heartbeatTimeout]);

  // Announce local peer to network
  const announcePeer = useCallback(async (peerData: GunPeer) => {
    if (!gunRef.current) {
      console.error('GunDB not initialized');
      return;
    }
    
    try {
      await gunRef.current
        .get('lattice')
        .get('peers')
        .get(peerData.peer_id)
        .put(peerData);
      
      console.log('📡 Announced peer:', peerData.location.city);
    } catch (err) {
      console.error('Failed to announce peer:', err);
    }
  }, []);

  // Send heartbeat for local peer
  const sendHeartbeat = useCallback(async (peerId: string) => {
    if (!gunRef.current) return;
    
    try {
      await gunRef.current
        .get('lattice')
        .get('peers')
        .get(peerId)
        .get('last_seen')
        .put(Date.now());
    } catch (err) {
      console.error('Failed to send heartbeat:', err);
    }
  }, []);

  // Broadcast proof event to network
  const broadcastEvent = useCallback(async (eventData: ProofEvent) => {
    if (!gunRef.current) {
      console.error('GunDB not initialized');
      return;
    }
    
    try {
      await gunRef.current
        .get('lattice')
        .get('events')
        .get(eventData.event_id)
        .put(eventData);
      
      console.log('📢 Broadcasted event:', eventData.message);
    } catch (err) {
      console.error('Failed to broadcast event:', err);
    }
  }, []);

  // Calculate network metrics
  const metrics = {
    total_peers: peers.length,
    connected_peers: peers.filter(p => p.status === 'connected').length,
    peers_by_continent: peers.reduce((acc, peer) => {
      const continent = peer.location.continent || 'Unknown';
      acc[continent] = (acc[continent] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    total_proofs: peers.reduce((sum, peer) => sum + peer.proofs_validated, 0),
  };

  return {
    peers,
    events,
    isConnected,
    error,
    metrics,
    announcePeer,
    sendHeartbeat,
    broadcastEvent,
  };
}

