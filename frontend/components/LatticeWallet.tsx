/**
 * DIOTEC 360 IA - Lattice Wallet Component v10.3.0
 * 
 * Real-time visualization of Genesis Authority revenue stream (30%)
 * Shows accumulated rewards from global network activity
 * 
 * "Where Sovereignty Becomes Wealth"
 */

"use client";

import { useState, useEffect } from 'react';
import { Wallet, TrendingUp, DollarSign, Clock, Zap, Crown } from 'lucide-react';

interface WalletBalance {
  genesis_authority: string;
  total_earned: number;
  current_balance: number;
  last_24h: number;
  last_7d: number;
  last_30d: number;
  currency: string;
  reward_percentage: number;
}

interface LatticeWalletProps {
  className?: string;
}

export default function LatticeWallet({ className = '' }: LatticeWalletProps) {
  const [balance, setBalance] = useState<WalletBalance | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch wallet balance
  const fetchBalance = async () => {
    try {
      const response = await fetch('/api/mobile/wallet/balance', {
        headers: {
          'Authorization': 'Bearer GENESIS_AUTHORITY_TOKEN'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch wallet balance');
      }

      const data = await response.json();
      setBalance(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch balance on mount and every 30 seconds
  useEffect(() => {
    fetchBalance();
    const interval = setInterval(fetchBalance, 30000);
    return () => clearInterval(interval);
  }, []);

  // Format currency
  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: balance?.currency || 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount);
  };

  // Calculate hourly rate
  const getHourlyRate = (): number => {
    if (!balance) return 0;
    return balance.last_24h / 24;
  };

  // Calculate growth percentage
  const getGrowthPercentage = (): number => {
    if (!balance || balance.last_7d === 0) return 0;
    const weeklyAverage = balance.last_7d / 7;
    const dailyGrowth = ((balance.last_24h - weeklyAverage) / weeklyAverage) * 100;
    return dailyGrowth;
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-8 ${className}`}>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className={`p-4 bg-red-900/20 border border-red-800 rounded-lg ${className}`}>
        <p className="text-sm text-red-400">⚠️ {error}</p>
      </div>
    );
  }

  if (!balance) {
    return null;
  }

  const growthPercentage = getGrowthPercentage();
  const hourlyRate = getHourlyRate();

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-amber-500/20 rounded-lg">
            <Crown className="w-6 h-6 text-amber-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Lattice Wallet</h2>
            <p className="text-xs text-gray-400">Genesis Authority Revenue Stream</p>
          </div>
        </div>
        
        <div className="text-right">
          <p className="text-xs text-gray-400">Last Update</p>
          <p className="text-xs text-gray-300">{lastUpdate.toLocaleTimeString()}</p>
        </div>
      </div>

      {/* Main Balance Card */}
      <div className="p-6 bg-gradient-to-br from-blue-900/40 to-purple-900/40 rounded-lg border border-blue-800/50">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Wallet className="w-5 h-5 text-blue-400" />
            <span className="text-sm text-gray-300">Current Balance</span>
          </div>
          <div className="px-3 py-1 bg-blue-500/20 rounded-full">
            <span className="text-xs font-semibold text-blue-300">
              {balance.reward_percentage}% Genesis Share
            </span>
          </div>
        </div>
        
        <div className="mb-2">
          <p className="text-4xl font-bold text-white">
            {formatCurrency(balance.current_balance)}
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <TrendingUp className={`w-4 h-4 ${growthPercentage >= 0 ? 'text-green-400' : 'text-red-400'}`} />
          <span className={`text-sm font-semibold ${growthPercentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {growthPercentage >= 0 ? '+' : ''}{growthPercentage.toFixed(2)}%
          </span>
          <span className="text-xs text-gray-400">vs. 7-day average</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Total Earned */}
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-2 mb-2">
            <DollarSign className="w-4 h-4 text-green-400" />
            <span className="text-xs text-gray-400">Total Earned</span>
          </div>
          <p className="text-xl font-bold text-white">
            {formatCurrency(balance.total_earned)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Since Genesis</p>
        </div>

        {/* Hourly Rate */}
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="w-4 h-4 text-blue-400" />
            <span className="text-xs text-gray-400">Hourly Rate</span>
          </div>
          <p className="text-xl font-bold text-white">
            {formatCurrency(hourlyRate)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Average per hour</p>
        </div>

        {/* Last 24 Hours */}
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-2 mb-2">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="text-xs text-gray-400">Last 24 Hours</span>
          </div>
          <p className="text-xl font-bold text-white">
            {formatCurrency(balance.last_24h)}
          </p>
          <p className="text-xs text-green-400 mt-1">
            +{((balance.last_24h / balance.last_7d) * 100).toFixed(1)}% of weekly
          </p>
        </div>

        {/* Last 30 Days */}
        <div className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
          <div className="flex items-center space-x-2 mb-2">
            <TrendingUp className="w-4 h-4 text-purple-400" />
            <span className="text-xs text-gray-400">Last 30 Days</span>
          </div>
          <p className="text-xl font-bold text-white">
            {formatCurrency(balance.last_30d)}
          </p>
          <p className="text-xs text-gray-500 mt-1">Monthly revenue</p>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700">
        <h3 className="text-sm font-semibold text-white mb-3">Revenue Breakdown</h3>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Genesis Authority (30%)</span>
            <span className="text-xs font-semibold text-amber-400">
              {formatCurrency(balance.last_24h)}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-400">Network Miners (70%)</span>
            <span className="text-xs font-semibold text-blue-400">
              {formatCurrency(balance.last_24h * (70/30))}
            </span>
          </div>
          
          <div className="pt-2 border-t border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-gray-300">Total Network Revenue</span>
              <span className="text-xs font-bold text-white">
                {formatCurrency(balance.last_24h + (balance.last_24h * (70/30)))}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Projections */}
      <div className="p-4 bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-lg border border-purple-800/50">
        <h3 className="text-sm font-semibold text-white mb-3">Projections</h3>
        
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs text-gray-400 mb-1">Next 7 Days</p>
            <p className="text-sm font-bold text-white">
              {formatCurrency(balance.last_24h * 7)}
            </p>
          </div>
          
          <div>
            <p className="text-xs text-gray-400 mb-1">Next 30 Days</p>
            <p className="text-sm font-bold text-white">
              {formatCurrency(balance.last_24h * 30)}
            </p>
          </div>
          
          <div>
            <p className="text-xs text-gray-400 mb-1">Annual</p>
            <p className="text-sm font-bold text-white">
              {formatCurrency(balance.last_24h * 365)}
            </p>
          </div>
        </div>
      </div>

      {/* Footer Note */}
      <div className="p-3 bg-blue-900/10 rounded-lg border border-blue-800/30">
        <p className="text-xs text-gray-400 text-center">
          💎 Revenue automatically distributed from network proof validation fees
        </p>
      </div>
    </div>
  );
}
