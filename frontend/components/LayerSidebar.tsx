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

import { useState } from 'react';
import { Tooltip } from './Tooltip';
import ExampleSelector from '@/components/ExampleSelector';

interface Layer {
  id: string;
  name: string;
  icon: string;
  description: string;
  active: boolean;
  badge?: number;
  color: string;
}

interface LayerSidebarProps {
  onLayerChange: (layerId: string) => void;
  onExampleSelect: (code: string) => void;
  onVerify: () => void;
  isVerifying: boolean;
  onChatToggle: () => void;
  activeLayer: string;
}

export default function LayerSidebar({ 
  onLayerChange, 
  onExampleSelect, 
  onVerify, 
  isVerifying, 
  onChatToggle,
  activeLayer 
}: LayerSidebarProps) {
  const [layers, setLayers] = useState<Layer[]>([
    {
      id: 'judge',
      name: 'Judge',
      icon: '🏛️',
      description: 'Mathematical proof engine',
      active: true,
      color: 'bg-blue-600'
    },
    {
      id: 'architect',
      name: 'Architect',
      icon: '🤖',
      description: 'AI code generation',
      active: false,
      color: 'bg-green-600'
    },
    {
      id: 'sentinel',
      name: 'Sentinel',
      icon: '🛡️',
      description: 'Security monitoring',
      active: false,
      badge: 3,
      color: 'bg-red-600'
    },
    {
      id: 'ghost',
      name: 'Ghost',
      icon: '🎭',
      description: 'Zero-knowledge privacy',
      active: false,
      color: 'bg-purple-600'
    },
    {
      id: 'oracle',
      name: 'Oracle',
      icon: '🔮',
      description: 'External data sources',
      active: false,
      color: 'bg-amber-600'
    }
  ]);

  const handleLayerClick = (layerId: string) => {
    setLayers(layers.map(layer => ({
      ...layer,
      active: layer.id === layerId
    })));
    onLayerChange(layerId);
  };

  const [examplesOpen, setExamplesOpen] = useState(false);

  return (
    <div className={`bg-gray-900 border-r border-gray-800 flex py-6 overflow-hidden transition-[width] duration-200 ${examplesOpen ? 'w-96' : 'w-20'}`}>
      <div className="w-20 flex flex-col items-center space-y-4">
      {/* Logo */}
      <div className="mb-4">
        <div className="text-2xl font-bold text-white">Æ</div>
      </div>

      {/* Divider */}
      <div className="w-12 h-px bg-gray-700" />

      {/* Layer Icons */}
      {layers.map((layer) => (
        <Tooltip key={layer.id} content={layer.description}>
          <button
            onClick={() => handleLayerClick(layer.id)}
            className={`
              relative w-14 h-14 rounded-xl flex items-center justify-center
              transition-all duration-200 group
              ${layer.active 
                ? `${layer.color} shadow-lg scale-110` 
                : 'bg-gray-800 hover:bg-gray-700 hover:scale-105'
              }
            `}
          >
            {/* Icon */}
            <span className="text-2xl">{layer.icon}</span>

            {/* Badge */}
            {layer.badge && layer.badge > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                {layer.badge}
              </span>
            )}

            {/* Active Indicator */}
            {layer.active && (
              <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-1 h-8 bg-white rounded-r" />
            )}

            {/* Hover Effect */}
            <div className={`
              absolute inset-0 rounded-xl opacity-0 group-hover:opacity-20
              transition-opacity duration-200
              ${layer.color}
            `} />
          </button>
        </Tooltip>
      ))}

      {/* Divider */}
      <div className="w-12 h-px bg-gray-700" />

      {/* Examples Button */}
      <Tooltip content="Examples">
        <button
          onClick={() => setExamplesOpen(!examplesOpen)}
          className={`
            relative w-14 h-14 rounded-xl flex items-center justify-center
            transition-all duration-200 group
            ${examplesOpen ? 'bg-gray-700' : 'bg-gray-800 hover:bg-gray-700 hover:scale-105'}
          `}
        >
          <span className="text-2xl">📚</span>
          {examplesOpen && (
            <div className="absolute -left-1 top-1/2 -translate-y-1/2 w-1 h-8 bg-white rounded-r" />
          )}
        </button>
      </Tooltip>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Action Buttons */}
      <Tooltip content="AI Chat (CMD+K)">
        <button 
          onClick={onChatToggle}
          className="w-14 h-14 rounded-xl bg-green-600 hover:bg-green-700 flex items-center justify-center transition-colors"
        >
          <span className="text-xl">🤖</span>
        </button>
      </Tooltip>

      <Tooltip content={isVerifying ? "Verifying..." : "Verify Code"}>
        <button 
          onClick={onVerify}
          disabled={isVerifying}
          className={`w-14 h-14 rounded-xl flex items-center justify-center transition-colors ${
            isVerifying 
              ? 'bg-gray-700 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          <span className="text-xl">{isVerifying ? '⏳' : '▶️'}</span>
        </button>
      </Tooltip>

      <Tooltip content="GitHub">
        <a
          href="https://github.com/diotec-barros/diotec360-lang"
          target="_blank"
          rel="noopener noreferrer"
          className="w-14 h-14 rounded-xl bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors"
        >
          <span className="text-xl">💻</span>
        </a>
      </Tooltip>

      <Tooltip content="Documentation">
        <a
          href="https://github.com/diotec-barros/diotec360-lang#readme"
          target="_blank"
          rel="noopener noreferrer"
          className="w-14 h-14 rounded-xl bg-gray-800 hover:bg-gray-700 flex items-center justify-center transition-colors"
        >
          <span className="text-xl">📖</span>
        </a>
      </Tooltip>
      </div>

      {examplesOpen && (
        <div className="flex-1 pr-4 pl-3">
          <div className="h-full flex flex-col">
            <div className="px-1 pb-3">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Examples</div>
              <div className="text-xs text-gray-500 mt-1">Select an example to load into the editor</div>
            </div>
            <div className="flex-1 overflow-auto">
              <ExampleSelector onSelect={onExampleSelect} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
