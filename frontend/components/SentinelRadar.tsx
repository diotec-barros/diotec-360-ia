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

import { useEffect, useState, useRef } from 'react';
import { Activity, Shield, AlertTriangle } from 'lucide-react';

interface SentinelRadarProps {
  isActive: boolean;
  threatLevel: number; // 0-100
  status: 'idle' | 'scanning' | 'verified' | 'threat';
}

export default function SentinelRadar({ isActive, threatLevel, status }: SentinelRadarProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [intensity, setIntensity] = useState(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;

    let animationFrame: number;
    let time = 0;

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      // Background grid
      ctx.strokeStyle = 'rgba(100, 100, 100, 0.1)';
      ctx.lineWidth = 1;
      for (let i = 0; i < width; i += 20) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, height);
        ctx.stroke();
      }
      for (let i = 0; i < height; i += 20) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(width, i);
        ctx.stroke();
      }

      // Determine color based on status
      let waveColor = 'rgba(34, 197, 94, 0.8)'; // Green
      let glowColor = 'rgba(34, 197, 94, 0.3)';
      
      if (status === 'scanning') {
        waveColor = 'rgba(59, 130, 246, 0.8)'; // Blue
        glowColor = 'rgba(59, 130, 246, 0.3)';
        setIntensity(Math.min(intensity + 0.05, 1));
      } else if (status === 'threat') {
        waveColor = 'rgba(239, 68, 68, 0.8)'; // Red
        glowColor = 'rgba(239, 68, 68, 0.3)';
        setIntensity(1);
      } else if (status === 'verified') {
        waveColor = 'rgba(34, 197, 94, 0.8)'; // Green
        glowColor = 'rgba(34, 197, 94, 0.3)';
        setIntensity(Math.max(intensity - 0.02, 0.2));
      } else {
        setIntensity(Math.max(intensity - 0.02, 0));
      }

      // Draw sine waves
      const numWaves = 3;
      const amplitude = isActive ? 20 * (1 + intensity) : 10;
      const frequency = isActive ? 0.02 * (1 + intensity * 2) : 0.01;

      for (let wave = 0; wave < numWaves; wave++) {
        ctx.beginPath();
        ctx.strokeStyle = waveColor;
        ctx.lineWidth = 2;

        const offset = (wave * Math.PI * 2) / numWaves;

        for (let x = 0; x < width; x++) {
          const y = centerY + Math.sin(x * frequency + time + offset) * amplitude;
          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.stroke();

        // Glow effect
        ctx.strokeStyle = glowColor;
        ctx.lineWidth = 4;
        ctx.stroke();
      }

      // Radar sweep (only when scanning)
      if (status === 'scanning') {
        const sweepAngle = (time * 0.05) % (Math.PI * 2);
        const sweepLength = Math.min(width, height) / 2;

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(sweepAngle);

        // Sweep line
        const gradient = ctx.createLinearGradient(0, 0, sweepLength, 0);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0)');
        gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.5)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0)');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(sweepLength, 0);
        ctx.stroke();

        ctx.restore();
      }

      time += 0.1;
      animationFrame = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [isActive, status, intensity]);

  const getStatusColor = () => {
    switch (status) {
      case 'scanning': return 'text-blue-400';
      case 'verified': return 'text-green-400';
      case 'threat': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'scanning': return <Activity className="w-4 h-4 animate-pulse" />;
      case 'verified': return <Shield className="w-4 h-4" />;
      case 'threat': return <AlertTriangle className="w-4 h-4 animate-bounce" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'scanning': return 'SCANNING';
      case 'verified': return 'VERIFIED';
      case 'threat': return 'THREAT DETECTED';
      default: return 'IDLE';
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Sentinel Radar</h3>
            <p className="text-xs text-gray-400">Real-time Monitoring</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 ${getStatusColor()}`}>
          {getStatusIcon()}
          <span className="text-xs font-bold uppercase">{getStatusText()}</span>
        </div>
      </div>

      {/* Radar Canvas */}
      <div className="relative bg-black rounded-lg overflow-hidden border border-gray-800">
        <canvas
          ref={canvasRef}
          width={300}
          height={120}
          className="w-full"
        />
        
        {/* Overlay Info */}
        <div className="absolute top-2 left-2 text-xs font-mono text-green-400">
          <div>FREQ: {(0.02 * (1 + intensity * 2)).toFixed(3)} Hz</div>
          <div>AMP: {(20 * (1 + intensity)).toFixed(1)} px</div>
        </div>

        <div className="absolute top-2 right-2 text-xs font-mono text-green-400">
          <div>TIME: {Date.now().toString().slice(-6)}</div>
        </div>
      </div>

      {/* Threat Level Meter */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-400">Threat Level</span>
          <span className={`font-bold ${
            threatLevel > 75 ? 'text-red-400' :
            threatLevel > 50 ? 'text-yellow-400' :
            threatLevel > 25 ? 'text-blue-400' :
            'text-green-400'
          }`}>
            {threatLevel.toFixed(2)}%
          </span>
        </div>
        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              threatLevel > 75 ? 'bg-red-500' :
              threatLevel > 50 ? 'bg-yellow-500' :
              threatLevel > 25 ? 'bg-blue-500' :
              'bg-green-500'
            }`}
            style={{ width: `${threatLevel}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-gray-400">Scans</div>
          <div className="text-white font-bold">1,247</div>
        </div>
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-gray-400">Blocked</div>
          <div className="text-red-400 font-bold">3</div>
        </div>
        <div className="bg-gray-800 rounded px-2 py-1">
          <div className="text-gray-400">Uptime</div>
          <div className="text-green-400 font-bold">99.9%</div>
        </div>
      </div>
    </div>
  );
}
