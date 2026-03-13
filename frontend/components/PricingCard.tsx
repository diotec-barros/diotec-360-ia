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

import { Check, X, Zap, Shield, Globe, Users } from 'lucide-react';
import { useState } from 'react';

interface PricingCardProps {
  title: string;
  price: string;
  description: string;
  features: string[];
  ctaText: string;
  ctaLink: string;
  highlighted?: boolean;
  icon?: 'zap' | 'shield' | 'globe' | 'users';
  creditAmount?: number;
  popular?: boolean;
}

const iconMap = {
  zap: Zap,
  shield: Shield,
  globe: Globe,
  users: Users,
};

export default function PricingCard({
  title,
  price,
  description,
  features,
  ctaText,
  ctaLink,
  highlighted = false,
  icon = 'zap',
  creditAmount,
  popular = false,
}: PricingCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const IconComponent = iconMap[icon];

  const handleCtaClick = () => {
    if (ctaLink.startsWith('/')) {
      // Navegação interna
      window.location.href = ctaLink;
    } else if (ctaLink.startsWith('http')) {
      // Link externo
      window.open(ctaLink, '_blank');
    } else if (ctaLink === 'contact') {
      // Abrir formulário de contato
      window.location.href = '/contact';
    }
  };

  return (
    <div
      className={`
        relative flex flex-col h-full
        rounded-2xl border-2
        transition-all duration-300
        ${highlighted 
          ? 'border-blue-500 bg-gradient-to-br from-blue-900/20 to-gray-900 shadow-2xl shadow-blue-500/20' 
          : 'border-gray-800 bg-gray-900/50 hover:border-gray-700 hover:bg-gray-900/70'
        }
        ${isHovered ? 'scale-[1.02]' : 'scale-100'}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Badge Popular */}
      {popular && (
        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-lg">
            MOST POPULAR
          </div>
        </div>
      )}

      <div className="p-8 flex-1">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className={`
              p-3 rounded-xl
              ${highlighted 
                ? 'bg-blue-500/20 text-blue-400' 
                : 'bg-gray-800 text-gray-400'
              }
            `}>
              <IconComponent className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{title}</h3>
              <p className="text-sm text-gray-400">{description}</p>
            </div>
          </div>
        </div>

        {/* Price */}
        <div className="mb-8">
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-bold text-white">{price}</span>
            {price.includes('/') && (
              <span className="text-gray-400">per month</span>
            )}
          </div>
          
          {creditAmount && (
            <div className="mt-2 flex items-center gap-2 text-sm text-gray-400">
              <div className="w-2 h-2 rounded-full bg-green-500"></div>
              <span>Includes {creditAmount.toLocaleString()} credits</span>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="space-y-4 mb-8">
          <h4 className="text-lg font-semibold text-white">What's included:</h4>
          <ul className="space-y-3">
            {features.map((feature, index) => (
              <li key={index} className="flex items-start gap-3">
                <div className={`
                  mt-1 p-1 rounded-full
                  ${highlighted 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-gray-800 text-gray-400'
                  }
                `}>
                  <Check className="w-4 h-4" />
                </div>
                <span className="text-gray-300">{feature}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Not Included (for contrast) */}
        {!highlighted && (
          <div className="space-y-3 mb-8">
            <h4 className="text-lg font-semibold text-gray-400">Not included:</h4>
            <ul className="space-y-2">
              <li className="flex items-center gap-3 text-gray-500">
                <X className="w-4 h-4" />
                <span>24/7 Priority Support</span>
              </li>
              <li className="flex items-center gap-3 text-gray-500">
                <X className="w-4 h-4" />
                <span>Custom Integrations</span>
              </li>
            </ul>
          </div>
        )}
      </div>

      {/* CTA Button */}
      <div className="p-8 pt-0">
        <button
          onClick={handleCtaClick}
          className={`
            w-full py-4 px-6 rounded-xl
            font-semibold text-lg
            transition-all duration-300
            flex items-center justify-center gap-3
            ${highlighted
              ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg shadow-blue-500/30'
              : 'bg-gray-800 hover:bg-gray-700 text-white'
            }
            ${isHovered ? 'shadow-2xl' : 'shadow-lg'}
          `}
        >
          {ctaText}
          {highlighted && <Zap className="w-5 h-5" />}
        </button>

        {/* Additional Info */}
        <div className="mt-4 text-center">
          <p className="text-sm text-gray-400">
            {highlighted ? '30-day money back guarantee' : 'No credit card required to start'}
          </p>
          {creditAmount && (
            <p className="text-xs text-gray-500 mt-1">
              ${(creditAmount * 0.10).toFixed(2)} value at $0.10 per credit
            </p>
          )}
        </div>
      </div>

      {/* Gradient Border Effect */}
      {highlighted && (
        <div className="absolute inset-0 -z-10 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 blur-xl"></div>
      )}
    </div>
  );
}