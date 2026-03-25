/**
 * DIOTEC 360 IA - Sovereign Key Manager
 * 
 * BYOK (Bring Your Own Keys) - Total sovereignty over AI providers
 * Keys are stored ONLY in user's browser (localStorage)
 * Never touch the server - Zero trust architecture
 * 
 * "Your Keys, Your Intelligence, Your Empire"
 */

"use client";

import { useState, useEffect } from 'react';
import { X, Key, Eye, EyeOff, Save, Trash2, CheckCircle, AlertTriangle, Shield, Lock } from 'lucide-react';

interface KeyManagerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onKeysUpdated?: () => void;
}

interface APIKeys {
  openai: string;
  anthropic: string;
  ollamaUrl: string;
}

const STORAGE_KEY = 'diotec360-api-keys';

export default function KeyManagerModal({ isOpen, onClose, onKeysUpdated }: KeyManagerModalProps) {
  const [keys, setKeys] = useState<APIKeys>({
    openai: '',
    anthropic: '',
    ollamaUrl: 'http://localhost:11434',
  });

  const [showKeys, setShowKeys] = useState({
    openai: false,
    anthropic: false,
  });

  const [validationStatus, setValidationStatus] = useState<{
    openai: 'valid' | 'invalid' | 'unknown';
    anthropic: 'valid' | 'invalid' | 'unknown';
    ollama: 'valid' | 'invalid' | 'unknown';
  }>({
    openai: 'unknown',
    anthropic: 'unknown',
    ollama: 'unknown',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Load keys from localStorage on mount
  useEffect(() => {
    if (isOpen) {
      const savedKeys = localStorage.getItem(STORAGE_KEY);
      if (savedKeys) {
        try {
          const parsed = JSON.parse(savedKeys);
          setKeys(parsed);
          // Auto-validate on load
          validateKeys(parsed);
        } catch (error) {
          console.error('Failed to load API keys:', error);
        }
      }
    }
  }, [isOpen]);

  const validateKeys = async (keysToValidate: APIKeys) => {
    // Validate OpenAI key format
    if (keysToValidate.openai) {
      const isValidFormat = keysToValidate.openai.startsWith('sk-') && keysToValidate.openai.length > 20;
      setValidationStatus(prev => ({ ...prev, openai: isValidFormat ? 'valid' : 'invalid' }));
    } else {
      setValidationStatus(prev => ({ ...prev, openai: 'unknown' }));
    }

    // Validate Anthropic key format
    if (keysToValidate.anthropic) {
      const isValidFormat = keysToValidate.anthropic.startsWith('sk-ant-') && keysToValidate.anthropic.length > 20;
      setValidationStatus(prev => ({ ...prev, anthropic: isValidFormat ? 'valid' : 'invalid' }));
    } else {
      setValidationStatus(prev => ({ ...prev, anthropic: 'unknown' }));
    }

    // Validate Ollama URL format
    if (keysToValidate.ollamaUrl) {
      const isValidUrl = keysToValidate.ollamaUrl.startsWith('http://') || keysToValidate.ollamaUrl.startsWith('https://');
      setValidationStatus(prev => ({ ...prev, ollama: isValidUrl ? 'valid' : 'invalid' }));
    } else {
      setValidationStatus(prev => ({ ...prev, ollama: 'unknown' }));
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);

    try {
      // Save to localStorage (client-side only)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
      
      // Validate keys
      await validateKeys(keys);
      
      setSaveSuccess(true);
      
      if (onKeysUpdated) {
        onKeysUpdated();
      }

      // Auto-close after 1.5 seconds
      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (error) {
      console.error('Failed to save API keys:', error);
      alert('Failed to save keys. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleClear = (provider: keyof APIKeys) => {
    setKeys(prev => ({ ...prev, [provider]: provider === 'ollamaUrl' ? 'http://localhost:11434' : '' }));
    setValidationStatus(prev => ({ ...prev, [provider === 'ollamaUrl' ? 'ollama' : provider]: 'unknown' }));
  };

  const getStatusIcon = (status: 'valid' | 'invalid' | 'unknown') => {
    switch (status) {
      case 'valid':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'invalid':
        return <AlertTriangle className="w-5 h-5 text-red-400" />;
      default:
        return <Key className="w-5 h-5 text-gray-400" />;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl shadow-2xl border border-gray-700 w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-700 bg-gradient-to-r from-blue-900/30 to-purple-900/30">
          <div className="flex items-center space-x-3">
            <Shield className="w-8 h-8 text-blue-400" />
            <div>
              <h2 className="text-2xl font-bold text-white">Sovereign Key Manager</h2>
              <p className="text-sm text-gray-400">BYOK - Bring Your Own Keys</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Security Notice */}
        <div className="px-6 py-4 bg-blue-900/20 border-b border-gray-700">
          <div className="flex items-start space-x-3">
            <Lock className="w-5 h-5 text-blue-400 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-blue-300 font-semibold">Zero Trust Architecture</p>
              <p className="text-xs text-gray-400 mt-1">
                Your API keys are stored ONLY in your browser&apos;s localStorage. They never touch our servers.
                You have complete sovereignty over your AI providers.
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* OpenAI */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-semibold text-white">OpenAI API Key</label>
                {getStatusIcon(validationStatus.openai)}
              </div>
              {keys.openai && (
                <button
                  onClick={() => handleClear('openai')}
                  className="text-xs text-red-400 hover:text-red-300 flex items-center space-x-1"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Clear</span>
                </button>
              )}
            </div>
            <div className="relative">
              <input
                type={showKeys.openai ? 'text' : 'password'}
                value={keys.openai}
                onChange={(e) => setKeys(prev => ({ ...prev, openai: e.target.value }))}
                placeholder="sk-..."
                className="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
              <button
                onClick={() => setShowKeys(prev => ({ ...prev, openai: !prev.openai }))}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-700 rounded transition-colors"
              >
                {showKeys.openai ? (
                  <EyeOff className="w-4 h-4 text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-400" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Get your key from: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">platform.openai.com/api-keys</a>
            </p>
          </div>

          {/* Anthropic */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-semibold text-white">Anthropic API Key</label>
                {getStatusIcon(validationStatus.anthropic)}
              </div>
              {keys.anthropic && (
                <button
                  onClick={() => handleClear('anthropic')}
                  className="text-xs text-red-400 hover:text-red-300 flex items-center space-x-1"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Clear</span>
                </button>
              )}
            </div>
            <div className="relative">
              <input
                type={showKeys.anthropic ? 'text' : 'password'}
                value={keys.anthropic}
                onChange={(e) => setKeys(prev => ({ ...prev, anthropic: e.target.value }))}
                placeholder="sk-ant-..."
                className="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 font-mono text-sm"
              />
              <button
                onClick={() => setShowKeys(prev => ({ ...prev, anthropic: !prev.anthropic }))}
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-700 rounded transition-colors"
              >
                {showKeys.anthropic ? (
                  <EyeOff className="w-4 h-4 text-gray-400" />
                ) : (
                  <Eye className="w-4 h-4 text-gray-400" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Get your key from: <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:underline">console.anthropic.com/settings/keys</a>
            </p>
          </div>

          {/* Ollama */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <label className="text-sm font-semibold text-white">Ollama URL (Local)</label>
                {getStatusIcon(validationStatus.ollama)}
              </div>
              {keys.ollamaUrl !== 'http://localhost:11434' && (
                <button
                  onClick={() => handleClear('ollamaUrl')}
                  className="text-xs text-red-400 hover:text-red-300 flex items-center space-x-1"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Reset</span>
                </button>
              )}
            </div>
            <input
              type="text"
              value={keys.ollamaUrl}
              onChange={(e) => setKeys(prev => ({ ...prev, ollamaUrl: e.target.value }))}
              placeholder="http://localhost:11434"
              className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-sm"
            />
            <p className="text-xs text-gray-500">
              Run Ollama locally for free AI: <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer" className="text-green-400 hover:underline">ollama.ai</a>
            </p>
          </div>

          {/* Success Message */}
          {saveSuccess && (
            <div className="flex items-center space-x-2 p-4 bg-green-900/20 border border-green-700 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <p className="text-sm text-green-300 font-semibold">Keys saved successfully!</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-700 bg-gray-800/50 flex items-center justify-between">
          <p className="text-xs text-gray-500">
            🛡️ Sovereign Identity - Your keys, your control
          </p>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white text-sm font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 rounded-lg text-white text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Save Keys</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
