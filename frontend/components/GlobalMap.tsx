/**
 * DIOTEC 360 IA - Global Map Component v10.0.9
 * 
 * Interactive SVG world map showing P2P network peers
 * Real-time visualization of global node distribution
 * 
 * "Where Geography Meets Cryptography"
 */

"use client";

import { useState, useEffect, useRef } from 'react';
import { MapPin, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import type { GunPeer, ProofEvent } from '@/lib/useGunLattice';

interface GlobalMapProps {
  peers: GunPeer[];
  events: ProofEvent[];
  onPeerClick?: (peer: GunPeer) => void;
}

interface MapProjection {
  x: number;
  y: number;
}

export default function GlobalMap({ peers, events, onPeerClick }: GlobalMapProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [hoveredPeer, setHoveredPeer] = useState<string | null>(null);
  const [activeAnimations, setActiveAnimations] = useState<ProofEvent[]>([]);
  const svgRef = useRef<SVGSVGElement>(null);

  // Add new events to animation queue
  useEffect(() => {
    if (events.length > 0) {
      const latestEvent = events[0];
      
      // Only animate proof_validated and merkle_sync events
      if (latestEvent.type === 'proof_validated' || latestEvent.type === 'merkle_sync') {
        setActiveAnimations(prev => {
          // Limit to 10 concurrent animations
          const newAnimations = [latestEvent, ...prev].slice(0, 10);
          return newAnimations;
        });
        
        // Remove animation after 2 seconds
        setTimeout(() => {
          setActiveAnimations(prev => prev.filter(e => e.event_id !== latestEvent.event_id));
        }, 2000);
      }
    }
  }, [events]);

  // Convert lat/lon to SVG coordinates (Mercator projection)
  const projectToMap = (lat: number, lon: number): MapProjection => {
    // SVG viewBox: 0 0 1000 500
    const x = ((lon + 180) / 360) * 1000;
    const latRad = (lat * Math.PI) / 180;
    const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
    const y = 250 - (mercN * 250) / Math.PI;
    
    return { x, y };
  };

  // Get peer by ID
  const getPeerById = (peerId: string): GunPeer | undefined => {
    return peers.find(p => p.peer_id === peerId);
  };

  // Get status color
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'connected': return '#10b981'; // green-500
      case 'syncing': return '#f59e0b'; // amber-500
      case 'offline': return '#ef4444'; // red-500
      default: return '#6b7280'; // gray-500
    }
  };

  // Zoom controls
  const handleZoomIn = () => setZoomLevel(prev => Math.min(prev + 0.5, 3));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(prev - 0.5, 0.5));
  const handleResetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  return (
    <div className="relative w-full h-full bg-gray-950 rounded-lg overflow-hidden">
      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
        <button
          onClick={handleZoomIn}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4 text-gray-300" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4 text-gray-300" />
        </button>
        <button
          onClick={handleResetView}
          className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          title="Reset View"
        >
          <Maximize2 className="w-4 h-4 text-gray-300" />
        </button>
      </div>

      {/* Peer Count Badge */}
      <div className="absolute top-4 left-4 z-10 bg-gray-800/90 backdrop-blur-sm rounded-lg px-4 py-2 border border-gray-700">
        <div className="flex items-center space-x-2">
          <MapPin className="w-4 h-4 text-blue-400" />
          <span className="text-sm font-semibold text-white">{peers.length} Nodes</span>
        </div>
      </div>

      {/* SVG Map */}
      <svg
        ref={svgRef}
        viewBox="0 0 1000 500"
        className="w-full h-full"
        style={{
          transform: `scale(${zoomLevel}) translate(${panOffset.x}px, ${panOffset.y}px)`,
          transition: 'transform 0.3s ease-out',
        }}
      >
        {/* World Map Background (Simplified Continents) */}
        <g id="continents" opacity="0.3" fill="#1f2937" stroke="#374151" strokeWidth="1">
          {/* Africa */}
          <path d="M 520 250 L 540 230 L 560 240 L 570 260 L 580 280 L 570 300 L 550 320 L 530 310 L 520 290 Z" />
          
          {/* Europe */}
          <path d="M 500 200 L 520 190 L 540 200 L 550 210 L 540 220 L 520 215 Z" />
          
          {/* Asia */}
          <path d="M 600 200 L 650 190 L 700 200 L 720 220 L 710 240 L 680 250 L 650 240 L 620 230 Z" />
          
          {/* North America */}
          <path d="M 200 180 L 250 170 L 280 190 L 290 210 L 270 230 L 240 220 L 210 200 Z" />
          
          {/* South America */}
          <path d="M 280 280 L 300 270 L 310 290 L 320 310 L 310 330 L 290 320 L 280 300 Z" />
          
          {/* Australia */}
          <path d="M 750 320 L 780 315 L 800 330 L 790 350 L 760 345 Z" />
        </g>

        {/* Grid Lines */}
        <g id="grid" opacity="0.1" stroke="#4b5563" strokeWidth="0.5">
          {/* Latitude lines */}
          {[0, 100, 200, 300, 400, 500].map(y => (
            <line key={`lat-${y}`} x1="0" y1={y} x2="1000" y2={y} />
          ))}
          {/* Longitude lines */}
          {[0, 200, 400, 600, 800, 1000].map(x => (
            <line key={`lon-${x}`} x1={x} y1="0" x2={x} y2="500" />
          ))}
        </g>

        {/* Proof Flow Animations */}
        {activeAnimations.map(event => {
          const sourcePeer = getPeerById(event.source_peer_id);
          const destPeer = event.destination_peer_id ? getPeerById(event.destination_peer_id) : null;
          
          if (!sourcePeer) return null;
          
          const source = projectToMap(sourcePeer.location.lat, sourcePeer.location.lon);
          const dest = destPeer 
            ? projectToMap(destPeer.location.lat, destPeer.location.lon)
            : { x: 500, y: 250 }; // Center if no destination
          
          const color = event.type === 'proof_validated' ? '#3b82f6' : '#10b981';
          
          return (
            <g key={event.event_id}>
              {/* Animated line */}
              <line
                x1={source.x}
                y1={source.y}
                x2={dest.x}
                y2={dest.y}
                stroke={color}
                strokeWidth="2"
                opacity="0.6"
                strokeDasharray="5,5"
              >
                <animate
                  attributeName="stroke-dashoffset"
                  from="0"
                  to="100"
                  dur="2s"
                  repeatCount="1"
                />
                <animate
                  attributeName="opacity"
                  from="0.6"
                  to="0"
                  dur="2s"
                  repeatCount="1"
                />
              </line>
              
              {/* Animated particle */}
              <circle
                r="3"
                fill={color}
              >
                <animateMotion
                  path={`M ${source.x} ${source.y} L ${dest.x} ${dest.y}`}
                  dur="2s"
                  repeatCount="1"
                />
                <animate
                  attributeName="opacity"
                  from="1"
                  to="0"
                  dur="2s"
                  repeatCount="1"
                />
              </circle>
            </g>
          );
        })}

        {/* Peer Dots */}
        {peers.map(peer => {
          const pos = projectToMap(peer.location.lat, peer.location.lon);
          const color = getStatusColor(peer.status);
          const isHovered = hoveredPeer === peer.peer_id;
          
          return (
            <g
              key={peer.peer_id}
              onMouseEnter={() => setHoveredPeer(peer.peer_id)}
              onMouseLeave={() => setHoveredPeer(null)}
              onClick={() => onPeerClick?.(peer)}
              style={{ cursor: 'pointer' }}
            >
              {/* Pulse ring for connected peers */}
              {peer.status === 'connected' && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="8"
                  fill="none"
                  stroke={color}
                  strokeWidth="2"
                  opacity="0.5"
                >
                  <animate
                    attributeName="r"
                    from="8"
                    to="16"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                  <animate
                    attributeName="opacity"
                    from="0.5"
                    to="0"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </circle>
              )}
              
              {/* Peer dot */}
              <circle
                cx={pos.x}
                cy={pos.y}
                r={isHovered ? "6" : "4"}
                fill={color}
                stroke="#fff"
                strokeWidth="1"
                style={{ transition: 'r 0.2s ease-out' }}
              />
              
              {/* Hover tooltip */}
              {isHovered && (
                <g>
                  <rect
                    x={pos.x + 10}
                    y={pos.y - 30}
                    width="150"
                    height="50"
                    fill="#1f2937"
                    stroke="#374151"
                    strokeWidth="1"
                    rx="4"
                  />
                  <text
                    x={pos.x + 15}
                    y={pos.y - 15}
                    fill="#fff"
                    fontSize="12"
                    fontWeight="bold"
                  >
                    {peer.location.city}
                  </text>
                  <text
                    x={pos.x + 15}
                    y={pos.y - 2}
                    fill="#9ca3af"
                    fontSize="10"
                  >
                    {peer.proofs_validated.toLocaleString()} proofs
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 bg-gray-800/90 backdrop-blur-sm rounded-lg px-4 py-3 border border-gray-700">
        <div className="space-y-2 text-xs">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-gray-300">Connected</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-amber-500" />
            <span className="text-gray-300">Syncing</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-gray-300">Offline</span>
          </div>
        </div>
      </div>
    </div>
  );
}

