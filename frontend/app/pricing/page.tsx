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
import { 
  Check, 
  Zap, 
  Shield, 
  Globe, 
  Users, 
  CreditCard, 
  BarChart3,
  Lock,
  Cloud,
  Cpu,
  Database,
  MessageSquare,
  Clock,
  Award,
  TrendingUp
} from 'lucide-react';
import PricingCard from '@/components/PricingCard';
import Link from 'next/link';

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  
  const monthlyPrices = {
    starter: '$10',
    professional: '$80',
    business: '$700',
    enterprise: 'Custom'
  };

  const annualPrices = {
    starter: '$96',
    professional: '$768',
    business: '$6,720',
    enterprise: 'Custom'
  };

  const prices = billingCycle === 'monthly' ? monthlyPrices : annualPrices;
  const savings = billingCycle === 'annual' ? 'Save 20% with annual billing' : '';

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                DIOTEC360 Apex
              </Link>
              <span className="text-sm text-gray-400">Pricing</span>
            </div>
            
            <div className="flex items-center gap-4">
              <Link 
                href="/" 
                className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
              >
                Back to Editor
              </Link>
              <Link 
                href="/contact" 
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
              >
                Contact Sales
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Simple, transparent{' '}
            <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              pricing
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 mb-12 max-w-2xl mx-auto">
            Pay only for what you use. No hidden fees, no surprises. 
            Start with credits and scale as you grow.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-gray-900 rounded-xl p-1 mb-12">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`
                px-6 py-3 rounded-lg font-semibold transition-all
                ${billingCycle === 'monthly' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
                }
              `}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`
                px-6 py-3 rounded-lg font-semibold transition-all
                ${billingCycle === 'annual' 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white'
                }
              `}
            >
              Annual
              <span className="ml-2 text-xs bg-green-500 text-white px-2 py-1 rounded-full">
                Save 20%
              </span>
            </button>
          </div>

          {savings && (
            <div className="mb-12 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
              <p className="text-green-400 font-semibold">
                🎉 {savings}
              </p>
            </div>
          )}
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-7xl mx-auto mb-20">
          <PricingCard
            title="Starter"
            price={prices.starter}
            description="For developers exploring DIOTEC360"
            features={[
              "100 credits included",
              "Basic proof verification",
              "Community support",
              "Up to 10 proofs/day",
              "Email support",
              "Basic examples"
            ]}
            ctaText="Start Free Trial"
            ctaLink="/signup?plan=starter"
            icon="zap"
            creditAmount={100}
          />

          <PricingCard
            title="Professional"
            price={prices.professional}
            description="For small teams and projects"
            features={[
              "1,000 credits included",
              "Batch verification",
              "Priority support",
              "Up to 100 proofs/day",
              "Basic monitoring",
              "API access",
              "Webhook support"
            ]}
            ctaText="Start Free Trial"
            ctaLink="/signup?plan=professional"
            icon="shield"
            highlighted={true}
            popular={true}
            creditAmount={1000}
          />

          <PricingCard
            title="Business"
            price={prices.business}
            description="For production systems"
            features={[
              "10,000 credits included",
              "Unlimited verification",
              "24/7 support",
              "Advanced monitoring",
              "Custom integrations",
              "SLA guarantee",
              "Team management",
              "Audit logs"
            ]}
            ctaText="Start Free Trial"
            ctaLink="/signup?plan=business"
            icon="globe"
            creditAmount={10000}
          />

          <PricingCard
            title="Enterprise"
            price={prices.enterprise}
            description="For large organizations"
            features={[
              "100,000+ credits",
              "Custom contract",
              "Dedicated support",
              "On-premise deployment",
              "Custom training",
              "Security review",
              "Compliance assistance",
              "White-label options"
            ]}
            ctaText="Contact Sales"
            ctaLink="/contact"
            icon="users"
            creditAmount={100000}
          />
        </div>

        {/* Credit System Explanation */}
        <div className="max-w-4xl mx-auto mb-20">
          <div className="bg-gray-900/50 rounded-2xl p-8 border border-gray-800">
            <h2 className="text-3xl font-bold mb-6 text-center">
              How credits work
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-800/50 p-6 rounded-xl">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
                  <CreditCard className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Purchase Credits</h3>
                <p className="text-gray-400">
                  Buy credits based on your needs. Each credit costs approximately $0.10.
                </p>
              </div>

              <div className="bg-gray-800/50 p-6 rounded-xl">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Cpu className="w-6 h-6 text-green-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Use Services</h3>
                <p className="text-gray-400">
                  Credits are consumed automatically as you use DIOTEC360 services.
                </p>
              </div>

              <div className="bg-gray-800/50 p-6 rounded-xl">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Monitor Usage</h3>
                <p className="text-gray-400">
                  Track your credit usage in real-time and receive alerts when running low.
                </p>
              </div>
            </div>

            <div className="bg-gray-800/30 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4">Credit Consumption Examples</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-400" />
                    <span>Simple proof verification</span>
                  </div>
                  <span className="font-semibold">1 credit</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-400" />
                    <span>Batch verification (1000 transactions)</span>
                  </div>
                  <span className="font-semibold">500 credits</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-400" />
                    <span>Sentinel monitoring (per hour)</span>
                  </div>
                  <span className="font-semibold">10 credits</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Check className="w-5 h-5 text-green-400" />
                    <span>Ghost identity operation</span>
                  </div>
                  <span className="font-semibold">20 credits</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="max-w-4xl mx-auto mb-20">
          <h2 className="text-3xl font-bold mb-8 text-center">
            Frequently asked questions
          </h2>
          
          <div className="space-y-4">
            <div className="bg-gray-900/50 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-3">
                What happens if I run out of credits?
              </h3>
              <p className="text-gray-400">
                You'll receive email notifications when your credits are running low. 
                If you run out, verification services will be paused until you purchase more credits. 
                No data is lost during this time.
              </p>
            </div>

            <div className="bg-gray-900/50 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-3">
                Can I switch plans at any time?
              </h3>
              <p className="text-gray-400">
                Yes! You can upgrade or downgrade your plan at any time. 
                When you upgrade, you'll get prorated credit for the remainder of your billing cycle. 
                When you downgrade, the change takes effect at the start of your next billing cycle.
              </p>
            </div>

            <div className="bg-gray-900/50 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-3">
                Is there a free trial?
              </h3>
              <p className="text-gray-400">
                Yes! All paid plans come with a 14-day free trial. 
                You get full access to all features during the trial period. 
                No credit card is required to start your trial.
              </p>
            </div>

            <div className="bg-gray-900/50 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-3">
                What payment methods do you accept?
              </h3>
              <p className="text-gray-400">
                We accept all major credit cards (Visa, MasterCard, American Express), 
                PayPal, and bank transfers for Enterprise plans. 
                We also support Multicaixa Express for customers in Angola.
              </p>
            </div>

            <div className="bg-gray-900/50 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-3">
                Do you offer discounts for non-profits or educational institutions?
              </h3>
              <p className="text-gray-400">
                Yes! We offer special pricing for non-profit organizations, 
                educational institutions, and open-source projects. 
                Please contact our sales team for more information.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-2xl p-12 border border-gray-800">
            <h2 className="text-4xl font-bold mb-6">
              Ready to eliminate bugs with mathematics?
            </h2>
            
            <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
              Join thousands of developers and companies who trust DIOTEC360 for 
              mathematically proven software correctness.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/signup"
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-xl font-bold text-lg transition-all shadow-lg shadow-blue-500/30"
              >
                Start Free Trial
              </Link>
              
              <Link
                href="/contact"
                className="px-8 py-4 bg-gray-800 hover:bg-gray-700 rounded-xl font-bold text-lg transition-all"
              >
                Schedule a Demo
              </Link>
            </div>

            <p className="text-gray-500 mt-6">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 bg-gray-900/50">
        <div className="container mx-auto px-6 py-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-4 md:mb-0">
              <div className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                DIOTEC360 Apex
              </div>
              <p className="text-gray-500 text-sm">
                © 2026 DIOTEC 360. All rights reserved.
              </p>
            </div>
            
            <div className="flex gap-6">
              <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="/terms" className="text-gray-400 hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link href="/contact" className="text-gray-400 hover:text-white transition-colors">
                Contact
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}