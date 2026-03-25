/**
 * DIOTEC 360 IA - Lattice Data Hook
 * 
 * Real-time P2P network data management
 * Connects to Lattice Bridge API and WebSocket stream
 * 
 * "Where the Network Becomes Real"
 */

import { useEffect, useState, useCallback, useRef } from 'react';

export interface Peer {
  peer_id: string;
  location: string;
  status: 'connected' | 'syncing' | 'offline';
  uptime_seconds: number;
  proofs_validated: number;
  last_seen: number;
}

export interface ConsensusData {
  merkle_root: string;
  consensus_percentage: number;
  agreeing_peers: number;
  total_peers: number;
  last_update: number;
}

export interface VerificationEvent {
  event_id: string;
  type: 'proof_validated' | 'merkle_sync' | 'peer_connected' | 'peer_disconnected';
  message: string;
  peer_id: string;
  timestamp: number;
}

interface UseLatticeDataOptions {
  enabled: boolean;
  pollInterval?: number;
}

export function useLatticeData(options: UseLatticeDataOptions) {
  const { enabled, pollInterval = 5000 } = options;
  
  const [peers, setPeers] = useState<Peer[]>([]);
  const [consensus, setConsensus] = useState<ConsensusData | null>(null);
  const [events, setEvents] = useState<VerificationEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [syncStatus, setSyncStatus] = useState<'synced' | 'syncing' | 'out_of_sync'>('synced');
  
  const wsRef = useRef<WebSocket | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Fetch peers from API
  const fetchPeers = useCallback(async () => {
    try {
      const response = await fetch('/api/lattice/peers');
      const data = await response.json();
      
      if (data.ok && data.peers) {
        setPeers(data.peers);
        setError(null);
      } else {
        throw new Error('Failed to fetch peers');
      }
    } catch (err) {
      console.error('Error fetching peers:', err);
      setError('Failed to load peer data');
      
      // Fallback to cached data
      const cached = localStorage.getItem('diotec360-cached-peers');
      if (cached) {
        setPeers(JSON.parse(cached));
      }
    }
  }, []);

  // Fetch consensus from API
  const fetchConsensus = useCallback(async () => {
    try {
      const response = await fetch('/api/lattice/consensus');
      const data = await response.json();
      
      if (data.ok) {
        setConsensus(data);
        setError(null);
        
        // Update sync status based on consensus
        if (data.consensus_percentage >= 90) {
          setSyncStatus('synced');
        } else if (data.consensus_percentage >= 70) {
          setSyncStatus('syncing');
        } else {
          setSyncStatus('out_of_sync');
        }
      } else {
        throw new Error('Failed to fetch consensus');
      }
    } catch (err) {
      console.error('Error fetching consensus:', err);
      setError('Failed to load consensus data');
      
      // Fallback to cached data
      const cached = localStorage.getItem('diotec360-cached-consensus');
      if (cached) {
        setConsensus(JSON.parse(cached));
      }
    }
  }, []);

  // Fetch initial events
  const fetchEvents = useCallback(async () => {
    try {
      const response = await fetch('/api/lattice/events');
      const data = await response.json();
      
      if (data.ok && data.events) {
        setEvents(data.events);
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching events:', err);
      // Events are optional, don't set error
    }
  }, []);

  // Connect to WebSocket for real-time events
  const connectWebSocket = useCallback(() => {
    if (!enabled) return;

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'wss://diotec-360-diotec-360-ia-judge.hf.space/api/lattice/stream';
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected to Lattice stream');
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'verification_event' && data.event) {
            setEvents(prev => [data.event, ...prev].slice(0, 50));
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting in 5s...');
        
        // Auto-reconnect after 5 seconds
        setTimeout(() => {
          if (enabled && wsRef.current === ws) {
            connectWebSocket();
          }
        }, 5000);
      };

      wsRef.current = ws;
    } catch (err) {
      console.error('Error connecting WebSocket:', err);
      setError('Failed to connect to real-time stream');
    }
  }, [enabled]);

  // Manual sync function
  const manualSync = useCallback(async () => {
    setSyncStatus('syncing');
    
    try {
      await Promise.all([
        fetchPeers(),
        fetchConsensus(),
        fetchEvents(),
      ]);
      
      setTimeout(() => setSyncStatus('synced'), 2000);
    } catch (err) {
      console.error('Manual sync error:', err);
      setSyncStatus('out_of_sync');
    }
  }, [fetchPeers, fetchConsensus, fetchEvents]);

  // Initial data load
  useEffect(() => {
    if (!enabled) return;

    const loadData = async () => {
      setIsLoading(true);
      
      try {
        await Promise.all([
          fetchPeers(),
          fetchConsensus(),
          fetchEvents(),
        ]);
      } catch (err) {
        console.error('Error loading initial data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, [enabled, fetchPeers, fetchConsensus, fetchEvents]);

  // Setup polling
  useEffect(() => {
    if (!enabled) return;

    pollTimerRef.current = setInterval(() => {
      fetchPeers();
      fetchConsensus();
    }, pollInterval);

    return () => {
      if (pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
      }
    };
  }, [enabled, pollInterval, fetchPeers, fetchConsensus]);

  // Setup WebSocket
  useEffect(() => {
    if (!enabled) return;

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [enabled, connectWebSocket]);

  // Cache data to localStorage
  useEffect(() => {
    if (peers.length > 0) {
      localStorage.setItem('diotec360-cached-peers', JSON.stringify(peers));
    }
  }, [peers]);

  useEffect(() => {
    if (consensus) {
      localStorage.setItem('diotec360-cached-consensus', JSON.stringify(consensus));
    }
  }, [consensus]);

  return {
    peers,
    consensus,
    events,
    isLoading,
    error,
    syncStatus,
    manualSync,
  };
}
