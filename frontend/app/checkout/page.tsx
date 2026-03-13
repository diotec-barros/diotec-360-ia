'use client';

import { useState } from 'react';
import { PayPalButtons, PayPalScriptProvider } from '@paypal/react-paypal-js';
import Link from 'next/link';

export default function CheckoutPage() {
  const [selectedPlan, setSelectedPlan] = useState('professional');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const plans = {
    starter: { name: 'Starter', price: 10, credits: 100 },
    professional: { name: 'Professional', price: 80, credits: 1000 },
    business: { name: 'Business', price: 700, credits: 10000 },
  };

  const plan = plans[selectedPlan as keyof typeof plans];

  const createOrder = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan: selectedPlan,
          amount: plan.price,
        }),
      });

      const data = await response.json();
      return data.id;
    } catch (err) {
      console.error('Error creating order:', err);
      setError('Erro ao criar pedido. Tente novamente.');
      throw err;
    }
  };

  const onApprove = async (data: any) => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/capture-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          orderID: data.orderID,
        }),
      });

      const details = await response.json();
      setSuccess(true);
      console.log('Payment successful:', details);
    } catch (err) {
      console.error('Error capturing order:', err);
      setError('Erro ao processar pagamento. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              DIOTEC 360
            </Link>
            <Link 
              href="/pricing" 
              className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              ← Voltar para Preços
            </Link>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-16">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-8 text-center">
            Finalizar Compra
          </h1>

          {success ? (
            <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-8 text-center">
              <div className="text-6xl mb-4">🎉</div>
              <h2 className="text-2xl font-bold mb-4 text-green-400">
                Pagamento Realizado com Sucesso!
              </h2>
              <p className="text-gray-400 mb-6">
                Seus {plan.credits} créditos foram adicionados à sua conta.
              </p>
              <Link
                href="/"
                className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
              >
                Voltar para o Editor
              </Link>
            </div>
          ) : (
            <>
              {/* Plan Selection */}
              <div className="bg-gray-900/50 rounded-xl p-6 mb-8 border border-gray-800">
                <h2 className="text-xl font-semibold mb-4">Selecione seu Plano</h2>
                <div className="space-y-3">
                  {Object.entries(plans).map(([key, p]) => (
                    <button
                      key={key}
                      onClick={() => setSelectedPlan(key)}
                      className={`
                        w-full p-4 rounded-lg border-2 transition-all text-left
                        ${selectedPlan === key
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-gray-700 hover:border-gray-600'
                        }
                      `}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="font-semibold text-lg">{p.name}</div>
                          <div className="text-gray-400 text-sm">{p.credits} créditos</div>
                        </div>
                        <div className="text-2xl font-bold">${p.price}</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Order Summary */}
              <div className="bg-gray-900/50 rounded-xl p-6 mb-8 border border-gray-800">
                <h2 className="text-xl font-semibold mb-4">Resumo do Pedido</h2>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Plano:</span>
                    <span className="font-semibold">{plan.name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Créditos:</span>
                    <span className="font-semibold">{plan.credits}</span>
                  </div>
                  <div className="border-t border-gray-700 pt-3 mt-3">
                    <div className="flex justify-between text-xl">
                      <span className="font-semibold">Total:</span>
                      <span className="font-bold text-blue-400">${plan.price}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* PayPal Button */}
              <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
                <h2 className="text-xl font-semibold mb-4">Método de Pagamento</h2>
                
                {error && (
                  <div className="mb-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400">
                    {error}
                  </div>
                )}

                <PayPalScriptProvider
                  options={{
                    clientId: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID || '',
                    currency: 'USD',
                  }}
                >
                  <PayPalButtons
                    createOrder={createOrder}
                    onApprove={onApprove}
                    onError={(err) => {
                      console.error('PayPal error:', err);
                      setError('Erro no PayPal. Tente novamente.');
                    }}
                    style={{
                      layout: 'vertical',
                      color: 'blue',
                      shape: 'rect',
                      label: 'pay',
                    }}
                  />
                </PayPalScriptProvider>

                <div className="mt-4 text-center text-sm text-gray-500">
                  <p>🔒 Pagamento seguro processado pelo PayPal</p>
                  <p className="mt-2">Modo: SANDBOX (Teste)</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
