"use client";

/**
 * Credit Purchase Modal - v4.0.0
 * 
 * UI for purchasing Aethel Credits via PayPal
 * Backend: diotec360/api/treasury_api.py (✅ READY)
 * 
 * Packages:
 * - Starter: 1,000 credits @ $9.99
 * - Professional: 6,000 credits @ $49.99 (20% bonus)
 * - Enterprise: 30,000 credits @ $199.99 (50% bonus)
 */

import { useState } from 'react';
import { X, Coins, Check, Loader2, ExternalLink } from 'lucide-react';

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  currency: string;
  description: string;
  bonus?: string;
  popular?: boolean;
}

const PACKAGES: CreditPackage[] = [
  {
    id: 'starter',
    name: 'Starter',
    credits: 1000,
    price: 9.99,
    currency: 'USD',
    description: 'Perfect for trying out DIOTEC 360',
    bonus: undefined,
    popular: false
  },
  {
    id: 'professional',
    name: 'Professional',
    credits: 6000,
    price: 49.99,
    currency: 'USD',
    description: 'Best value for regular users',
    bonus: '20% bonus credits',
    popular: true
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    credits: 30000,
    price: 199.99,
    currency: 'USD',
    description: 'For power users and teams',
    bonus: '50% bonus credits',
    popular: false
  }
];

interface CreditPurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentBalance: number;
  onPurchaseComplete?: (newBalance: number) => void;
}

export default function CreditPurchaseModal({
  isOpen,
  onClose,
  currentBalance,
  onPurchaseComplete
}: CreditPurchaseModalProps) {
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handlePurchase = async (packageId: string) => {
    setIsProcessing(true);
    setError(null);

    try {
      // Get user's public key from localStorage
      const publicKey = localStorage.getItem('diotec360-user-public-key');
      
      if (!publicKey) {
        throw new Error('Sovereign Identity not configured. Please configure your identity first.');
      }

      // Get API URL from environment
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://diotec-360-diotec-360-ia-judge.hf.space';
      
      // Create PayPal order
      const response = await fetch(`${apiUrl}/api/treasury/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          package: packageId,
          user_public_key: publicKey,
          payment_method: 'paypal',
          return_url: `${window.location.origin}/studio?payment=success`,
          cancel_url: `${window.location.origin}/studio?payment=cancelled`
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to create PayPal order');
      }

      const data = await response.json();

      if (!data.ok || !data.approval_url) {
        throw new Error('Failed to create PayPal order');
      }

      // Store order ID for verification
      localStorage.setItem('diotec360-pending-order', data.order_id);

      // Redirect to PayPal
      window.location.href = data.approval_url;

    } catch (err) {
      console.error('Purchase error:', err);
      setError(err instanceof Error ? err.message : 'Failed to initiate purchase');
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-gray-900 rounded-2xl shadow-2xl border border-gray-700">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-4 bg-gray-800 border-b border-gray-700">
          <div>
            <h2 className="text-2xl font-bold text-white flex items-center">
              <Coins className="w-6 h-6 mr-2 text-yellow-400" />
              Purchase Aethel Credits
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              Current Balance: <span className="text-yellow-400 font-semibold">{currentBalance.toLocaleString()}</span> credits
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={isProcessing}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mx-6 mt-4 p-4 bg-red-900/20 border border-red-700/30 rounded-lg">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        {/* Packages */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {PACKAGES.map((pkg) => (
              <div
                key={pkg.id}
                className={`relative p-6 rounded-xl border-2 transition-all cursor-pointer ${
                  selectedPackage === pkg.id
                    ? 'border-blue-500 bg-blue-900/20'
                    : pkg.popular
                    ? 'border-purple-500 bg-purple-900/10'
                    : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                }`}
                onClick={() => setSelectedPackage(pkg.id)}
              >
                {/* Popular Badge */}
                {pkg.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="px-3 py-1 text-xs font-bold text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-full shadow-lg">
                      MOST POPULAR
                    </span>
                  </div>
                )}

                {/* Selected Indicator */}
                {selectedPackage === pkg.id && (
                  <div className="absolute top-4 right-4">
                    <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}

                {/* Package Info */}
                <div className="text-center">
                  <h3 className="text-xl font-bold text-white mb-2">{pkg.name}</h3>
                  
                  <div className="my-4">
                    <div className="text-4xl font-bold text-yellow-400 flex items-center justify-center">
                      <Coins className="w-8 h-8 mr-2" />
                      {pkg.credits.toLocaleString()}
                    </div>
                    <p className="text-sm text-gray-400 mt-1">Aethel Credits</p>
                  </div>

                  {pkg.bonus && (
                    <div className="mb-3">
                      <span className="px-3 py-1 text-xs font-semibold text-green-400 bg-green-900/30 rounded-full border border-green-700/30">
                        {pkg.bonus}
                      </span>
                    </div>
                  )}

                  <div className="text-3xl font-bold text-white mb-2">
                    ${pkg.price}
                    <span className="text-sm text-gray-400 font-normal ml-1">{pkg.currency}</span>
                  </div>

                  <p className="text-sm text-gray-400 mb-4">{pkg.description}</p>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePurchase(pkg.id);
                    }}
                    disabled={isProcessing}
                    className={`w-full py-3 rounded-lg font-semibold transition-all flex items-center justify-center ${
                      pkg.popular
                        ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {isProcessing && selectedPackage === pkg.id ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Buy with PayPal
                      </>
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Info Section */}
          <div className="mt-8 p-6 bg-gray-800 rounded-xl border border-gray-700">
            <h3 className="text-lg font-bold text-white mb-4">💳 Payment Information</h3>
            <div className="space-y-3 text-sm text-gray-300">
              <div className="flex items-start">
                <Check className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                <p>Secure payment processing via PayPal</p>
              </div>
              <div className="flex items-start">
                <Check className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                <p>Credits are added instantly after payment confirmation</p>
              </div>
              <div className="flex items-start">
                <Check className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                <p>All transactions are recorded on the Merkle Tree for transparency</p>
              </div>
              <div className="flex items-start">
                <Check className="w-5 h-5 text-green-400 mr-2 flex-shrink-0 mt-0.5" />
                <p>Angola compliant payment processing</p>
              </div>
            </div>
          </div>

          {/* Usage Info */}
          <div className="mt-4 p-6 bg-blue-900/20 rounded-xl border border-blue-700/30">
            <h3 className="text-lg font-bold text-blue-400 mb-3">🎯 What can you do with credits?</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>• Verify contracts with Z3 Theorem Prover (10 credits per verification)</li>
              <li>• Use Dual-Brain Mode for enhanced code generation (50 credits per session)</li>
              <li>• Export Intelligence Harvester training data (100 credits per export)</li>
              <li>• Access premium features and priority support</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
