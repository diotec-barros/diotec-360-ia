/**
 * Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 */

'use client';

import { useEffect, useRef, useState } from 'react';

interface PayPalButtonProps {
  amount: string;
  currency?: string;
  description?: string;
  onSuccess?: (details: any) => void;
  onError?: (error: any) => void;
  onCancel?: () => void;
}

declare global {
  interface Window {
    paypal?: any;
  }
}

export default function PayPalButton({
  amount,
  currency = 'USD',
  description = 'DIOTEC 360 Credits',
  onSuccess,
  onError,
  onCancel
}: PayPalButtonProps) {
  const paypalRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Carrega o script do PayPal
    const script = document.createElement('script');
    script.src = `https://www.paypal.com/sdk/js?client-id=${process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID}&currency=${currency}`;
    script.async = true;
    
    script.onload = () => {
      setIsLoading(false);
      
      if (window.paypal && paypalRef.current) {
        window.paypal.Buttons({
          createOrder: async (data: any, actions: any) => {
            try {
              // Cria a ordem no backend
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/create-order`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  amount,
                  currency,
                  description
                }),
              });

              const order = await response.json();
              return order.id;
            } catch (err) {
              console.error('Erro ao criar ordem:', err);
              setError('Erro ao criar ordem de pagamento');
              throw err;
            }
          },
          
          onApprove: async (data: any, actions: any) => {
            try {
              // Captura o pagamento no backend
              const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payments/capture-order`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                  orderID: data.orderID
                }),
              });

              const details = await response.json();
              
              if (onSuccess) {
                onSuccess(details);
              }
              
              return details;
            } catch (err) {
              console.error('Erro ao capturar pagamento:', err);
              setError('Erro ao processar pagamento');
              if (onError) {
                onError(err);
              }
              throw err;
            }
          },
          
          onError: (err: any) => {
            console.error('Erro no PayPal:', err);
            setError('Erro no processamento do PayPal');
            if (onError) {
              onError(err);
            }
          },
          
          onCancel: () => {
            console.log('Pagamento cancelado pelo usuário');
            if (onCancel) {
              onCancel();
            }
          },
          
          style: {
            layout: 'vertical',
            color: 'blue',
            shape: 'rect',
            label: 'paypal'
          }
        }).render(paypalRef.current);
      }
    };

    script.onerror = () => {
      setIsLoading(false);
      setError('Erro ao carregar PayPal SDK');
    };

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, [amount, currency, description, onSuccess, onError, onCancel]);

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4">
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {isLoading && (
        <div className="bg-gray-800/50 rounded-xl p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Carregando PayPal...</p>
        </div>
      )}
      <div ref={paypalRef} className={isLoading ? 'hidden' : ''}></div>
    </div>
  );
}
