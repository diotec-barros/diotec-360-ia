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

import { useEffect, useState } from 'react';
import { Globe, Zap, CheckCircle, Clock } from 'lucide-react';

interface OracleSource {
  id: string;
  name: string;
  location: string;
  lat: number;
  lng: number;
  type: 'price' | 'weather' | 'event' | 'identity';
  verified: boolean;
  latency: number;
  lastUpdate: Date;
  active: boolean;
}

interface OracleAtlasProps {
  activeSources: string[];
}

export default function OracleAtlas({ activeSources }: OracleAtlasProps) {
  const [sources] = useState<OracleSource[]>([
    {
      id: 'chainlink-nyc',
      name: 'Chainlink',
      location: 'New York, USA',
      lat: 40.7128,
      lng: -74.0060,
      type: 'price',
      verified: true,
      latency: 42,
      lastUpdate: new Date(),
      active: false
    },
    {
      id: 'weather-london',
      name: 'Weather API',
      location: 'London, UK',
      lat: 51.5074,
      lng: -0.1278,
      type: 'weather',
      verified: true,
      latency: 38,
      lastUpdate: new Date(),
      active: false
    },
    {
      id: 'chainlink-geneva',
      name: 'Chainlink',
      location: 'Geneva, Switzerland',
      lat: 46.2044,
      lng: 6.1432,
      type: 'price',
      verified: true,
      latency: 28,
      lastUpdate: new Date(),
      active: false
    },
    {
      id: 'weather-houston',
      name: 'NOAA',
      location: 'Houston, USA',
      lat: 29.7604,
      lng: -95.3698,
      type: 'weather',
      verified: true,
      latency: 45,
      lastUpdate: new Date(),
      active: false
    },
    {
      id: 'chainlink-singapore',
      name: 'Chainlink',
      location: 'Singapore',
      lat: 1.3521,
      lng: 103.8198,
      type: 'price',
      verified: true,
      latency: 52,
      lastUpdate: new Date(),
      active: false
    }
  ]);

  const [activeSourcesState, setActiveSourcesState] = useState<Set<string>>(new Set());

  useEffect(() => {
    setActiveSourcesState(new Set(activeSources));
  }, [activeSources]);

  const getTypeColor = (type: string) => {
    const colors = {
      price: 'text-amber-400 bg-amber-900/20',
      weather: 'text-blue-400 bg-blue-900/20',
      event: 'text-purple-400 bg-purple-900/20',
      identity: 'text-green-400 bg-green-900/20'
    };
    return colors[type as keyof typeof colors] || 'text-gray-400 bg-gray-900/20';
  };

  const getTypeIcon = (type: string) => {
    const icons = {
      price: '💰',
      weather: '🌤️',
      event: '📡',
      identity: '🆔'
    };
    return icons[type as keyof typeof icons] || '📊';
  };

  // Convert lat/lng to SVG coordinates (simplified projection)
  const projectToSVG = (lat: number, lng: number) => {
    const x = ((lng + 180) / 360) * 800;
    const y = ((90 - lat) / 180) * 400;
    return { x, y };
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-600 flex items-center justify-center">
            <Globe className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Oracle Atlas</h3>
            <p className="text-xs text-gray-400">Global Data Sources</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-green-400">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <span>{sources.filter(s => activeSourcesState.has(s.id)).length} Active</span>
        </div>
      </div>

      {/* World Map SVG */}
      <div className="relative bg-black rounded-lg overflow-hidden border border-gray-800 mb-4">
        <svg
          viewBox="0 0 800 400"
          className="w-full h-48"
          style={{ background: 'radial-gradient(circle at 50% 50%, #0a0a0a, #000000)' }}
        >
          {/* Grid lines */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(100,100,100,0.1)" strokeWidth="1"/>
            </pattern>
          </defs>
          <rect width="800" height="400" fill="url(#grid)" />

          {/* Simplified continents (dark shapes) */}
          <g opacity="0.3" fill="#1a1a1a" stroke="#333" strokeWidth="1">
            {/* North America */}
            <path d="M 100,80 L 200,60 L 250,100 L 220,180 L 150,200 L 100,150 Z" />
            {/* Europe */}
            <path d="M 380,80 L 450,70 L 480,120 L 440,140 L 380,120 Z" />
            {/* Asia */}
            <path d="M 500,60 L 650,80 L 680,150 L 620,180 L 550,160 L 500,120 Z" />
            {/* South America */}
            <path d="M 200,220 L 240,240 L 230,320 L 190,340 L 180,280 Z" />
            {/* Africa */}
            <path d="M 380,160 L 450,180 L 460,280 L 400,300 L 370,240 Z" />
            {/* Australia */}
            <path d="M 620,260 L 680,270 L 670,310 L 610,300 Z" />
          </g>

          {/* Connection lines to center (Nexus) */}
          {sources.map(source => {
            const isActive = activeSourcesState.has(source.id);
            if (!isActive) return null;

            const { x, y } = projectToSVG(source.lat, source.lng);
            const centerX = 400;
            const centerY = 200;

            return (
              <g key={`line-${source.id}`}>
                {/* Animated pulse line */}
                <line
                  x1={x}
                  y1={y}
                  x2={centerX}
                  y2={centerY}
                  stroke="url(#pulse-gradient)"
                  strokeWidth="2"
                  opacity="0.6"
                >
                  <animate
                    attributeName="stroke-dasharray"
                    from="0,1000"
                    to="1000,0"
                    dur="2s"
                    repeatCount="indefinite"
                  />
                </line>
              </g>
            );
          })}

          {/* Gradient for pulse */}
          <defs>
            <linearGradient id="pulse-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f59e0b" stopOpacity="0" />
              <stop offset="50%" stopColor="#f59e0b" stopOpacity="1" />
              <stop offset="100%" stopColor="#f59e0b" stopOpacity="0" />
            </linearGradient>
          </defs>

          {/* Center Nexus */}
          <g>
            <circle cx="400" cy="200" r="8" fill="#3b82f6" opacity="0.3">
              <animate attributeName="r" from="8" to="16" dur="2s" repeatCount="indefinite" />
              <animate attributeName="opacity" from="0.3" to="0" dur="2s" repeatCount="indefinite" />
            </circle>
            <circle cx="400" cy="200" r="6" fill="#3b82f6" />
            <text x="400" y="205" textAnchor="middle" fill="white" fontSize="10" fontWeight="bold">
              NEXUS
            </text>
          </g>

          {/* Oracle source markers */}
          {sources.map(source => {
            const { x, y } = projectToSVG(source.lat, source.lng);
            const isActive = activeSourcesState.has(source.id);

            return (
              <g key={source.id}>
                {/* Glow effect when active */}
                {isActive && (
                  <circle cx={x} cy={y} r="12" fill="#f59e0b" opacity="0.2">
                    <animate attributeName="r" from="12" to="20" dur="1.5s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.2" to="0" dur="1.5s" repeatCount="indefinite" />
                  </circle>
                )}
                
                {/* Marker */}
                <circle
                  cx={x}
                  cy={y}
                  r="5"
                  fill={isActive ? '#f59e0b' : '#4b5563'}
                  stroke={isActive ? '#fbbf24' : '#6b7280'}
                  strokeWidth="2"
                  className="cursor-pointer"
                >
                  {isActive && (
                    <animate attributeName="r" from="5" to="6" dur="0.5s" repeatCount="indefinite" direction="alternate" />
                  )}
                </circle>

                {/* Verified checkmark */}
                {source.verified && (
                  <text x={x + 8} y={y - 8} fill="#10b981" fontSize="10">✓</text>
                )}
              </g>
            );
          })}
        </svg>

        {/* Legend */}
        <div className="absolute top-2 left-2 text-xs space-y-1">
          <div className="flex items-center gap-2 text-amber-400">
            <div className="w-2 h-2 bg-amber-500 rounded-full" />
            <span>Active Source</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <div className="w-2 h-2 bg-gray-500 rounded-full" />
            <span>Inactive</span>
          </div>
        </div>
      </div>

      {/* Source List */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {sources.map(source => {
          const isActive = activeSourcesState.has(source.id);
          
          return (
            <div
              key={source.id}
              className={`
                flex items-center justify-between p-2 rounded border transition-all
                ${isActive 
                  ? 'bg-amber-900/20 border-amber-500/30' 
                  : 'bg-gray-800/50 border-gray-700'
                }
              `}
            >
              <div className="flex items-center gap-3 flex-1">
                {/* Type Badge */}
                <span className={`px-2 py-1 rounded text-xs font-semibold ${getTypeColor(source.type)}`}>
                  {getTypeIcon(source.type)}
                </span>

                {/* Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{source.name}</span>
                    {source.verified && (
                      <CheckCircle className="w-3 h-3 text-green-400" />
                    )}
                  </div>
                  <div className="text-xs text-gray-400">{source.location}</div>
                </div>
              </div>

              {/* Metrics */}
              <div className="flex items-center gap-4 text-xs">
                <div className="flex items-center gap-1 text-gray-400">
                  <Zap className="w-3 h-3" />
                  <span>{source.latency}ms</span>
                </div>
                <div className="flex items-center gap-1 text-gray-400">
                  <Clock className="w-3 h-3" />
                  <span>{source.lastUpdate.toLocaleTimeString()}</span>
                </div>
                {isActive && (
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
