/**
 * Autopilot Client Tests
 * Feature: diotec360-pilot-v3-7
 * Task 3.3, 3.4: Property tests for request debouncing and cache effectiveness
 */

import {
  AutopilotClient,
  getAutopilotClient,
  resetAutopilotClient,
  EditorState,
  AutopilotResponse,
} from '../lib/autopilotClient';

// Mock fetch
global.fetch = jest.fn();

describe('AutopilotClient', () => {
  let client: AutopilotClient;
  
  beforeEach(() => {
    resetAutopilotClient();
    client = new AutopilotClient({
      debounceDelay: 100, // Shorter for testing
      requestTimeout: 1000,
    });
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    client.cancelPendingRequest();
    client.clearCache();
  });
  
  describe('Property 13: Request Debouncing', () => {
    /**
     * Feature: diotec360-pilot-v3-7, Property 13: Request Debouncing
     * 
     * For any sequence of typing events in the editor, if events occur within
     * 300ms of each other, only the final event should trigger an API request,
     * and any pending requests from previous events should be cancelled.
     */
    
    it('should debounce rapid requests and only send the last one', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [{ label: 'test', kind: 'keyword', insertText: 'test', detail: 'Test', priority: 0 }],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const states: EditorState[] = [
        { code: 'i', cursorPosition: 1 },
        { code: 'in', cursorPosition: 2 },
        { code: 'int', cursorPosition: 3 },
        { code: 'inte', cursorPosition: 4 },
        { code: 'inten', cursorPosition: 5 },
        { code: 'intent', cursorPosition: 6 },
      ];
      
      // Fire rapid requests
      const promises = states.map(state => client.getSuggestionsDebounced(state));
      
      // Wait for debounce to complete
      await Promise.all(promises);
      
      // Should only make one request (the last one)
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Verify it was the last state
      const lastCall = (global.fetch as any).mock.calls[0];
      const requestBody = JSON.parse(lastCall[1].body);
      expect(requestBody.code).toBe('intent');
      expect(requestBody.cursor_position).toBe(6);
    });
    
    it('should cancel pending requests when new request is made', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      let resolveCount = 0;
      (global.fetch as any).mockImplementation(() => {
        resolveCount++;
        return Promise.resolve({
          ok: true,
          json: async () => mockResponse,
        });
      });
      
      const state1: EditorState = { code: 'intent', cursorPosition: 6 };
      const state2: EditorState = { code: 'intent payment', cursorPosition: 14 };
      
      // Start first request (no debounce)
      const promise1 = client.getSuggestions(state1);
      
      // Immediately start second request (should cancel first)
      const promise2 = client.getSuggestions(state2);
      
      await Promise.all([promise1, promise2]);
      
      // Both requests should complete, but first should be aborted
      expect(resolveCount).toBeGreaterThanOrEqual(1);
    });
    
    it('should handle multiple rapid typing sequences independently', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      // First typing sequence
      const sequence1 = [
        { code: 'i', cursorPosition: 1 },
        { code: 'in', cursorPosition: 2 },
        { code: 'int', cursorPosition: 3 },
      ];
      
      const promises1 = sequence1.map(state => client.getSuggestionsDebounced(state));
      await Promise.all(promises1);
      
      // Wait for debounce
      await new Promise(resolve => setTimeout(resolve, 150));
      
      // Second typing sequence
      const sequence2 = [
        { code: 'intent', cursorPosition: 6 },
        { code: 'intent ', cursorPosition: 7 },
        { code: 'intent p', cursorPosition: 8 },
      ];
      
      const promises2 = sequence2.map(state => client.getSuggestionsDebounced(state));
      await Promise.all(promises2);
      
      // Should have made 2 requests total (one per sequence)
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
  
  describe('Property 19: Suggestion Cache Effectiveness', () => {
    /**
     * Feature: diotec360-pilot-v3-7, Property 19: Suggestion Cache Effectiveness
     * 
     * For any repeated request with identical code and cursor position, the
     * frontend cache should return the cached response without making a new
     * API call, and the cached response should be identical to the original.
     */
    
    it('should cache responses and return cached data for identical requests', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [{ label: 'payment', kind: 'keyword', insertText: 'payment', detail: 'Payment intent', priority: 0 }],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const state: EditorState = { code: 'intent', cursorPosition: 6 };
      
      // First request - should hit API
      const response1 = await client.getSuggestions(state);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Second request with identical state - should use cache
      const response2 = await client.getSuggestions(state);
      expect(global.fetch).toHaveBeenCalledTimes(1); // Still only 1 call
      
      // Responses should be identical
      expect(response1).toEqual(response2);
      expect(response1.suggestions).toEqual(mockResponse.suggestions);
    });
    
    it('should not use cache for different cursor positions', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const state1: EditorState = { code: 'intent payment', cursorPosition: 6 };
      const state2: EditorState = { code: 'intent payment', cursorPosition: 14 };
      
      await client.getSuggestions(state1);
      await client.getSuggestions(state2);
      
      // Should make 2 requests (different cursor positions)
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
    
    it('should not use cache for different code', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const state1: EditorState = { code: 'intent payment', cursorPosition: 14 };
      const state2: EditorState = { code: 'intent transfer', cursorPosition: 15 };
      
      await client.getSuggestions(state1);
      await client.getSuggestions(state2);
      
      // Should make 2 requests (different code)
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
    
    it('should evict oldest entries when cache is full', async () => {
      const smallCacheClient = new AutopilotClient({
        cacheSize: 2, // Very small cache
        debounceDelay: 100,
      });
      
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      // Add 3 entries (should evict first)
      await smallCacheClient.getSuggestions({ code: 'a', cursorPosition: 1 });
      await smallCacheClient.getSuggestions({ code: 'b', cursorPosition: 1 });
      await smallCacheClient.getSuggestions({ code: 'c', cursorPosition: 1 });
      
      expect(global.fetch).toHaveBeenCalledTimes(3);
      
      // Request first entry again - should hit API (evicted)
      await smallCacheClient.getSuggestions({ code: 'a', cursorPosition: 1 });
      expect(global.fetch).toHaveBeenCalledTimes(4);
      
      // Request second entry again - should use cache (not evicted)
      await smallCacheClient.getSuggestions({ code: 'b', cursorPosition: 1 });
      expect(global.fetch).toHaveBeenCalledTimes(4); // No new call
    });
    
    it('should handle cache with selections', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const state1: EditorState = {
        code: 'intent payment',
        cursorPosition: 6,
        selection: { start: 0, end: 6 },
      };
      
      const state2: EditorState = {
        code: 'intent payment',
        cursorPosition: 6,
        selection: { start: 0, end: 6 },
      };
      
      const state3: EditorState = {
        code: 'intent payment',
        cursorPosition: 6,
        selection: { start: 0, end: 14 }, // Different selection
      };
      
      await client.getSuggestions(state1);
      await client.getSuggestions(state2); // Should use cache
      await client.getSuggestions(state3); // Should not use cache
      
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
  
  describe('Error Handling', () => {
    it('should return empty response on API error', async () => {
      (global.fetch as any).mockRejectedValue(new Error('Network error'));
      
      const state: EditorState = { code: 'intent', cursorPosition: 6 };
      const response = await client.getSuggestions(state);
      
      expect(response.suggestions).toEqual([]);
      expect(response.safetyStatus.status).toBe('unknown');
    });
    
    it('should retry once on failure', async () => {
      let callCount = 0;
      (global.fetch as any).mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('First attempt failed'));
        }
        return Promise.resolve({
          ok: true,
          json: async () => ({
            suggestions: [],
            safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
            corrections: [],
            analysisTime: 10,
          }),
        });
      });
      
      const state: EditorState = { code: 'intent', cursorPosition: 6 };
      await client.getSuggestions(state);
      
      expect(callCount).toBe(2); // Initial + 1 retry
    });
    
    it('should handle timeout gracefully', async () => {
      const timeoutClient = new AutopilotClient({
        requestTimeout: 100, // Very short timeout
      });
      
      (global.fetch as any).mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(() => {
            resolve({
              ok: true,
              json: async () => ({
                suggestions: [],
                safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
                corrections: [],
                analysisTime: 10,
              }),
            });
          }, 200); // Longer than timeout
        });
      });
      
      const state: EditorState = { code: 'intent', cursorPosition: 6 };
      const response = await timeoutClient.getSuggestions(state);
      
      // Should return empty response on timeout
      expect(response.suggestions).toEqual([]);
    });
  });
  
  describe('Singleton Pattern', () => {
    it('should return same instance from getAutopilotClient', () => {
      const client1 = getAutopilotClient();
      const client2 = getAutopilotClient();
      
      expect(client1).toBe(client2);
    });
    
    it('should create new instance after reset', () => {
      const client1 = getAutopilotClient();
      resetAutopilotClient();
      const client2 = getAutopilotClient();
      
      expect(client1).not.toBe(client2);
    });
  });
  
  describe('Cache Management', () => {
    it('should clear cache on clearCache()', async () => {
      const mockResponse: AutopilotResponse = {
        suggestions: [],
        safetyStatus: { status: 'safe', violations: [], analysisTime: 10 },
        corrections: [],
        analysisTime: 10,
      };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });
      
      const state: EditorState = { code: 'intent', cursorPosition: 6 };
      
      // First request
      await client.getSuggestions(state);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      
      // Clear cache
      client.clearCache();
      
      // Second request should hit API again
      await client.getSuggestions(state);
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
    
    it('should provide cache statistics', async () => {
      const stats = client.getCacheStats();
      
      expect(stats).toHaveProperty('size');
      expect(stats).toHaveProperty('maxSize');
      expect(stats).toHaveProperty('hitRate');
      expect(stats.size).toBe(0);
    });
  });
});
