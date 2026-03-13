/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 */

'use client';

import { useState } from 'react';
import PayPalButton from '@/components/PayPalButton';
import Link from 'next/link';
import { Check, AlertCircle } from 'lucide-react';

export default function TestPaymentPage() {
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [paymentDetails, setPaymentDetails] = useState<any>(null);

  const handleSuccess = (details: any) => {
    console.log('Pagamento bem-sucedido:', details);
    setPaymentStatus('success');
    setPaymentDetails(details);
  };

  const handleError = (error: any) => {
    console.error('Erro no pagamento:', error);
    setPaymentStatus('error');
  };

  const handleCancel = () => {
    console.log('Pagamento cancelado');
    setPaymentStatus('idle');
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                DIOTEC 360
              </Link>
              <span className="text-sm text-gray-400">Teste de Pagamento</span>
            </div>
            
            <Link 
              href="/" 
              className="px-4 py-2 text-gray-300 hover:text-white transition-colors"
            >
              Voltar
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-16">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold mb-4 text-center">
            Teste de Pagamento{' '}
            <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              PayPal Sandbox
            </span>
          </h1>
          
          <p className="text-gray-400 text-center mb-8">
            Este é um ambiente de teste. Use as credenciais do PayPal Sandbox para testar.
          </p>

          {/* Alert Box */}
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 mb-8">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-400 font-semibold mb-2">Ambiente Sandbox</p>
                <p className="text-gray-400 text-sm">
                  Este é um teste com dinheiro fake. Nenhuma transação real será processada.
                  Use as contas de teste do PayPal Developer Dashboard.
                </p>
              </div>
            </div>
          </div>

          {/* Payment Card */}
          <div className="bg-gray-900/50 rounded-2xl p-8 border border-gray-800 mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-2">Comprar Créditos</h2>
              <p className="text-gray-400">
                Teste de compra de 100 créditos por $10.00 USD
              </p>
            </div>

            <div className="bg-gray-800/50 rounded-xl p-6 mb-6">
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-400">Produto:</span>
                <span className="font-semibold">100 Créditos DIOTEC 360</span>
              </div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-400">Preço unitário:</span>
                <span className="font-semibold">$0.10 / crédito</span>
              </div>
              <div className="border-t border-gray-700 pt-4 mt-4">
                <div className="flex justify-between items-center">
                  <span className="text-xl font-bold">Total:</span>
                  <span className="text-2xl font-bold text-blue-400">$10.00 USD</span>
                </div>
              </div>
            </div>

            {paymentStatus === 'idle' && (
              <PayPalButton
                amount="10.00"
                currency="USD"
                description="100 Créditos DIOTEC 360"
                onSuccess={handleSuccess}
                onError={handleError}
                onCancel={handleCancel}
              />
            )}

            {paymentStatus === 'success' && (
              <div className="bg-green-500/10 border border-green-500/20 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-green-500/20 rounded-full flex items-center justify-center">
                    <Check className="w-6 h-6 text-green-400" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-green-400">Pagamento Aprovado!</h3>
                    <p className="text-gray-400">Sua transação foi processada com sucesso</p>
                  </div>
                </div>
                
                {paymentDetails && (
                  <div className="bg-gray-800/50 rounded-lg p-4 mt-4">
                    <p className="text-sm text-gray-400 mb-2">Detalhes da transação:</p>
                    <pre className="text-xs text-gray-300 overflow-auto">
                      {JSON.stringify(paymentDetails, null, 2)}
                    </pre>
                  </div>
                )}

                <button
                  onClick={() => {
                    setPaymentStatus('idle');
                    setPaymentDetails(null);
                  }}
                  className="mt-4 w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
                >
                  Fazer Outro Teste
                </button>
              </div>
            )}

            {paymentStatus === 'error' && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <AlertCircle className="w-6 h-6 text-red-400" />
                  <div>
                    <h3 className="text-xl font-bold text-red-400">Erro no Pagamento</h3>
                    <p className="text-gray-400">Ocorreu um erro ao processar o pagamento</p>
                  </div>
                </div>

                <button
                  onClick={() => setPaymentStatus('idle')}
                  className="mt-4 w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-semibold transition-colors"
                >
                  Tentar Novamente
                </button>
              </div>
            )}
          </div>

          {/* Instructions */}
          <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-800">
            <h3 className="text-lg font-semibold mb-4">Como testar:</h3>
            <ol className="space-y-3 text-gray-400">
              <li className="flex gap-3">
                <span className="text-blue-400 font-bold">1.</span>
                <span>Clique no botão PayPal acima</span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400 font-bold">2.</span>
                <span>Faça login com uma conta Personal do PayPal Sandbox</span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400 font-bold">3.</span>
                <span>Complete o pagamento (dinheiro fake)</span>
              </li>
              <li className="flex gap-3">
                <span className="text-blue-400 font-bold">4.</span>
                <span>Verifique se o webhook foi recebido nos logs do backend</span>
              </li>
            </ol>

            <div className="mt-6 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
              <p className="text-sm text-blue-400">
                <strong>Dica:</strong> Acesse{' '}
                <a 
                  href="https://developer.paypal.com/dashboard/" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="underline hover:text-blue-300"
                >
                  PayPal Developer Dashboard
                </a>
                {' '}para obter as credenciais de teste (Sandbox &gt; Accounts)
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
