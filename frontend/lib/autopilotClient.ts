/**
 * Autopilot Client Service
 * Feature: diotec360-pilot-v3-7
 * Task 3: Implement frontend Autopilot client service
 * 
 * Provides debounced, cached, and resilient communication with the Autopilot API
 */

// Types
export interface EditorState {
  code: string;
  cursorPosition: number;
  selection?: { start: number; end: number };
}

export interface Suggestion {
  label: string;
  kind: 'keyword' | 'guard' | 'verify' | 'solve' | 'variable';
  insertText: string;
  detail: string;
  documentation?: string;
  sortText?: string;
  priority: number;
}

export interface Violation {
  type: string;
  description: string;
  line?: number;
  severity: 'error' | 'warning';
}

export interface SafetyStatus {
  status: 'safe' | 'unsafe' | 'analyzing' | 'unknown';
  violations: Violation[];
  analysisTime: number;
}

export interface CorrectionSuggestion {
  message: string;
  fix: string;
  line: number;
  severity: 'error' | 'warning';
}

export interface AutopilotResponse {
  suggestions: Suggestion[];
  safetyStatus: SafetyStatus;
  corrections: CorrectionSuggestion[];
  analysisTime: number;
}

// Configuration
interface AutopilotClientConfig {
  apiUrl: string;
  debounceDelay: number;
  maxRetries: number;
  retryDelay: number;
  cacheSize: number;
  requestTimeout: number;
}

const DEFAULT_CONFIG: AutopilotClientConfig = {
  apiUrl: '/api/autopilot/suggestions',
  debounceDelay: 300, // 300ms debounce
  maxRetries: 1,
  retryDelay: 1000,
  cacheSize: 100,
  requestTimeout: 5000, // 5 seconds
};

/**
 * Autopilot Client
 * 
 * Manages communication with the Autopilot API with:
 * - Request debouncing (300ms default)
 * - Response caching
 * - Automatic retries
 * - Request cancellation
 */
export class AutopilotClient {
  private config: AutopilotClientConfig;
  private debounceTimer: NodeJS.Timeout | null = null;
  private currentRequest: AbortController | null = null;
  private cache: Map<string, AutopilotResponse> = new Map();
  private cacheOrder: string[] = [];
  
  constructor(config?: Partial<AutopilotClientConfig>) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }
  
  /**
   * Get suggestions for current editor state
   * 
   * This method is debounced to prevent excessive API calls during typing.
   * It also caches responses and cancels outdated requests.
   */
  async getSuggestions(state: EditorState): Promise<AutopilotResponse> {
    // Check cache first
    const cacheKey = this.getCacheKey(state);
    const cached = this.cache.get(cacheKey);
    if (cached) {
      return cached;
    }
    
    // Cancel any pending request
    this.cancelPendingRequest();
    
    // Create new abort controller
    this.currentRequest = new AbortController();
    const signal = this.currentRequest.signal;
    
    try {
      // Make request with timeout
      const response = await this.fetchWithTimeout(
        this.config.apiUrl,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code: state.code,
            cursor_position: state.cursorPosition,
            selection: state.selection,
          }),
          signal,
        },
        this.config.requestTimeout
      );
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }
      
      const data: AutopilotResponse = await response.json();
      
      // Cache the response
      this.cacheResponse(cacheKey, data);
      
      return data;
    } catch (error) {
      // If request was aborted, return empty response
      if (error instanceof Error && error.name === 'AbortError') {
        return this.getEmptyResponse();
      }
      
      // Retry once on error
      if (this.config.maxRetries > 0) {
        await this.sleep(this.config.retryDelay);
        return this.retryRequest(state);
      }
      
      // Return empty response on error
      console.error('Autopilot request failed:', error);
      return this.getEmptyResponse();
    }
  }
  
  /**
   * Get suggestions with debouncing
   * 
   * This method debounces requests to prevent excessive API calls during
   * rapid typing. Only the last request within the debounce window is sent.
   */
  async getSuggestionsDebounced(state: EditorState): Promise<AutopilotResponse> {
    return new Promise((resolve) => {
      // Clear existing timer
      if (this.debounceTimer) {
        clearTimeout(this.debounceTimer);
      }
      
      // Set new timer
      this.debounceTimer = setTimeout(async () => {
        const response = await this.getSuggestions(state);
        resolve(response);
      }, this.config.debounceDelay);
    });
  }
  
  /**
   * Cancel any pending request
   */
  cancelPendingRequest(): void {
    if (this.currentRequest) {
      this.currentRequest.abort();
      this.currentRequest = null;
    }
  }
  
  /**
   * Clear the response cache
   */
  clearCache(): void {
    this.cache.clear();
    this.cacheOrder = [];
  }
  
  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number; maxSize: number; hitRate: number } {
    return {
      size: this.cache.size,
      maxSize: this.config.cacheSize,
      hitRate: 0, // TODO: Track hit rate
    };
  }
  
  // Private methods
  
  private getCacheKey(state: EditorState): string {
    const selectionKey = state.selection
      ? `${state.selection.start}-${state.selection.end}`
      : 'none';
    return `${state.code}:${state.cursorPosition}:${selectionKey}`;
  }
  
  private cacheResponse(key: string, response: AutopilotResponse): void {
    // Add to cache
    this.cache.set(key, response);
    this.cacheOrder.push(key);
    
    // Evict oldest entry if cache is full
    if (this.cache.size > this.config.cacheSize) {
      const oldestKey = this.cacheOrder.shift();
      if (oldestKey) {
        this.cache.delete(oldestKey);
      }
    }
  }
  
  private async retryRequest(state: EditorState): Promise<AutopilotResponse> {
    try {
      // Create new abort controller
      this.currentRequest = new AbortController();
      const signal = this.currentRequest.signal;
      
      const response = await this.fetchWithTimeout(
        this.config.apiUrl,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code: state.code,
            cursor_position: state.cursorPosition,
            selection: state.selection,
          }),
          signal,
        },
        this.config.requestTimeout
      );
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const data: AutopilotResponse = await response.json();
      
      // Cache the response
      const cacheKey = this.getCacheKey(state);
      this.cacheResponse(cacheKey, data);
      
      return data;
    } catch (error) {
      console.error('Autopilot retry failed:', error);
      return this.getEmptyResponse();
    }
  }
  
  private async fetchWithTimeout(
    url: string,
    options: RequestInit,
    timeout: number
  ): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }
  
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
  
  private getEmptyResponse(): AutopilotResponse {
    return {
      suggestions: [],
      safetyStatus: {
        status: 'unknown',
        violations: [],
        analysisTime: 0,
      },
      corrections: [],
      analysisTime: 0,
    };
  }
}

// Singleton instance
let autopilotClientInstance: AutopilotClient | null = null;

/**
 * Get the singleton Autopilot client instance
 */
export function getAutopilotClient(config?: Partial<AutopilotClientConfig>): AutopilotClient {
  if (!autopilotClientInstance) {
    autopilotClientInstance = new AutopilotClient(config);
  }
  return autopilotClientInstance;
}

/**
 * Reset the singleton instance (useful for testing)
 */
export function resetAutopilotClient(): void {
  if (autopilotClientInstance) {
    autopilotClientInstance.cancelPendingRequest();
    autopilotClientInstance.clearCache();
  }
  autopilotClientInstance = null;
}
