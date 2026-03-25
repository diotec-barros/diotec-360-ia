/**
 * DIOTEC 360 IA - Key Manager Utility
 * 
 * Centralized key management for AI providers
 * Zero trust - keys never leave the browser
 */

export interface APIKeys {
  openai: string;
  anthropic: string;
  ollamaUrl: string;
}

const STORAGE_KEY = 'diotec360-api-keys';

const DEFAULT_KEYS: APIKeys = {
  openai: '',
  anthropic: '',
  ollamaUrl: 'http://localhost:11434',
};

/**
 * Get API keys from localStorage
 */
export function getAPIKeys(): APIKeys {
  if (typeof window === 'undefined') return DEFAULT_KEYS;
  
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return { ...DEFAULT_KEYS, ...JSON.parse(saved) };
    }
  } catch (error) {
    console.error('Failed to load API keys:', error);
  }
  
  return DEFAULT_KEYS;
}

/**
 * Save API keys to localStorage
 */
export function saveAPIKeys(keys: APIKeys): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(keys));
  } catch (error) {
    console.error('Failed to save API keys:', error);
    throw error;
  }
}

/**
 * Check if a provider has a valid key configured
 */
export function hasValidKey(provider: 'openai' | 'anthropic' | 'ollama'): boolean {
  const keys = getAPIKeys();
  
  switch (provider) {
    case 'openai':
      return keys.openai.startsWith('sk-') && keys.openai.length > 20;
    case 'anthropic':
      return keys.anthropic.startsWith('sk-ant-') && keys.anthropic.length > 20;
    case 'ollama':
      return keys.ollamaUrl.startsWith('http://') || keys.ollamaUrl.startsWith('https://');
    default:
      return false;
  }
}

/**
 * Get available providers (those with valid keys)
 */
export function getAvailableProviders(): Array<'openai' | 'anthropic' | 'ollama'> {
  const providers: Array<'openai' | 'anthropic' | 'ollama'> = [];
  
  if (hasValidKey('openai')) providers.push('openai');
  if (hasValidKey('anthropic')) providers.push('anthropic');
  if (hasValidKey('ollama')) providers.push('ollama');
  
  return providers;
}

/**
 * Clear all API keys
 */
export function clearAPIKeys(): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear API keys:', error);
  }
}

/**
 * Get headers for API requests (includes user's keys if available)
 */
export function getAPIHeaders(provider: 'openai' | 'anthropic' | 'ollama'): Record<string, string> {
  const keys = getAPIKeys();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add user's key if available (for direct API calls)
  switch (provider) {
    case 'openai':
      if (keys.openai) {
        headers['X-User-OpenAI-Key'] = keys.openai;
      }
      break;
    case 'anthropic':
      if (keys.anthropic) {
        headers['X-User-Anthropic-Key'] = keys.anthropic;
      }
      break;
    case 'ollama':
      if (keys.ollamaUrl) {
        headers['X-User-Ollama-URL'] = keys.ollamaUrl;
      }
      break;
  }
  
  return headers;
}
