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

import { useState, useEffect, useRef } from 'react';
import { Send, Sparkles, X } from 'lucide-react';

interface Message {
  role: 'user' | 'architect';
  content: string;
  timestamp: Date;
  codeGenerated?: string;
}

interface ArchitectChatProps {
  isOpen: boolean;
  onClose: () => void;
  onCodeGenerated: (code: string) => void;
}

export default function ArchitectChat({ isOpen, onClose, onCodeGenerated }: ArchitectChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'architect',
      content: 'Hello! I\'m the DIOTEC360 Architect. Describe what you want to build, and I\'ll generate the code for you.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (!isOpen) {
          // Open chat (handled by parent)
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleSend = async () => {
    if (!input.trim() || isGenerating) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsGenerating(true);

    try {
      // TODO: Call actual API
      // Simulate AI response
      await new Promise(resolve => setTimeout(resolve, 1500));

      const generatedCode = `intent payment(
    sender: Account,
    receiver: Account,
    amount: Balance
) {
    guard {
        old_sender_balance >= amount;
        amount > 0;
    }
    
    solve {
        priority: security;
        target: defi_vault;
    }
    
    verify {
        fee == amount * 0.02;
        sender_balance == old_sender_balance - amount - fee;
        receiver_balance == old_receiver_balance + amount;
        platform_balance == old_platform_balance + fee;
    }
}`;

      const architectMessage: Message = {
        role: 'architect',
        content: 'I\'ve created a payment intent with a 2% fee. The fee is automatically calculated and sent to the platform balance. All balances are conserved.',
        timestamp: new Date(),
        codeGenerated: generatedCode
      };

      setMessages(prev => [...prev, architectMessage]);
    } catch (error) {
      console.error('Error generating code:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleUseCode = (code: string) => {
    onCodeGenerated(code);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="h-full w-full bg-gray-900 border border-gray-800 overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800 bg-black">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl bg-green-600 flex items-center justify-center shrink-0">
            <span className="text-xl">🤖</span>
          </div>
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-white truncate">DIOTEC360 Architect</h2>
            <p className="text-xs text-gray-400 truncate">AI-Powered Code Generation</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          aria-label="Close Architect"
        >
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto p-5 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`
                max-w-[80%] rounded-2xl px-4 py-3
                ${message.role === 'user' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-800 text-gray-100'
                }
              `}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {message.codeGenerated && (
                  <div className="mt-3 pt-3 border-t border-gray-700">
                    <pre className="text-xs bg-gray-900 p-3 rounded-lg overflow-x-auto">
                      <code>{message.codeGenerated}</code>
                    </pre>
                    <button
                      onClick={() => handleUseCode(message.codeGenerated!)}
                      className="mt-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded-lg transition-colors flex items-center gap-2"
                    >
                      <Sparkles className="w-4 h-4" />
                      Use This Code
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isGenerating && (
            <div className="flex justify-start">
              <div className="bg-gray-800 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-sm text-gray-400">Generating code...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-4 border-t border-gray-800 bg-black">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Describe what you want to build..."
            className="flex-1 bg-gray-900 text-white px-4 py-3 rounded-xl border border-gray-700 focus:border-green-500 focus:outline-none transition-colors"
            disabled={isGenerating}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isGenerating}
            className="px-5 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-xl transition-colors flex items-center gap-2"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press <kbd className="px-2 py-1 bg-gray-800 rounded">CMD+K</kbd> to open • <kbd className="px-2 py-1 bg-gray-800 rounded">ESC</kbd> to close
        </p>
      </div>
    </div>
  );
}
