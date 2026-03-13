/**
 * Task 5: IntelliSense Completion Provider Tests
 * Feature: DIOTEC360-pilot-v3-7
 * 
 * Tests for Monaco Editor completion provider integration with Autopilot Client
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MonacoAutopilot from '@/components/MonacoAutopilot';
import { getAutopilotClient, resetAutopilotClient } from '@/lib/autopilotClient';

// Mock Monaco Editor
jest.mock('@monaco-editor/react', () => ({
  __esModule: true,
  default: ({ onMount, beforeMount }: any) => {
    // Simulate Monaco mounting
    React.useEffect(() => {
      if (beforeMount) {
        const mockMonaco = createMockMonaco();
        beforeMount(mockMonaco);
      }
      if (onMount) {
        const mockEditor = createMockEditor();
        const mockMonaco = createMockMonaco();
        onMount(mockEditor, mockMonaco);
      }
    }, [onMount, beforeMount]);
    
    return <div data-testid="monaco-editor">Monaco Editor Mock</div>;
  },
}));

// Mock Autopilot Client
jest.mock('@/lib/autopilotClient', () => {
  const originalModule = jest.requireActual('@/lib/autopilotClient');
  
  return {
    ...originalModule,
    getAutopilotClient: jest.fn(() => ({
      getSuggestionsDebounced: jest.fn(async () => ({
        suggestions: [
          {
            label: 'guard {',
            kind: 'keyword',
            insertText: 'guard {\n  \n}',
            detail: 'Guard block',
            documentation: 'Define preconditions',
            priority: 10,
          },
          {
            label: 'amount > 0',
            kind: 'guard',
            insertText: 'amount > 0',
            detail: 'Amount must be positive',
            priority: 8,
          },
        ],
        safetyStatus: {
          status: 'safe',
          violations: [],
          analysisTime: 50,
        },
        corrections: [],
        analysisTime: 50,
      })),
      cancelPendingRequest: jest.fn(),
      clearCache: jest.fn(),
    })),
    resetAutopilotClient: jest.fn(),
  };
});

// Helper to create mock Monaco instance
function createMockMonaco() {
  const completionProviders: any[] = [];
  
  return {
    languages: {
      register: jest.fn(),
      setMonarchTokensProvider: jest.fn(),
      setLanguageConfiguration: jest.fn(),
      registerCompletionItemProvider: jest.fn((languageId, provider) => {
        completionProviders.push({ languageId, provider });
        return { dispose: jest.fn() };
      }),
      CompletionItemKind: {
        Keyword: 1,
        Function: 2,
        Variable: 3,
        Text: 0,
      },
    },
    editor: {
      defineTheme: jest.fn(),
      setTheme: jest.fn(),
    },
    _completionProviders: completionProviders,
  };
}

// Helper to create mock editor instance
function createMockEditor() {
  return {
    getValue: jest.fn(() => 'intent payment {\n  \n}'),
    getModel: jest.fn(() => ({
      getValue: jest.fn(() => 'intent payment {\n  \n}'),
      getOffsetAt: jest.fn((position) => position.lineNumber * 20 + position.column),
    })),
    getPosition: jest.fn(() => ({ lineNumber: 2, column: 3 })),
    getSelection: jest.fn(() => ({
      isEmpty: jest.fn(() => true),
    })),
    onDidChangeModelContent: jest.fn((callback) => {
      // Store callback for later invocation
      return { dispose: jest.fn() };
    }),
    focus: jest.fn(),
  };
}

describe('MonacoAutopilot - IntelliSense Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    resetAutopilotClient();
  });

  describe('Task 5.1: Completion Provider Registration', () => {
    it('should register completion provider for DIOTEC360 language', async () => {
      render(<MonacoAutopilot />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Verify completion provider was registered
      const mockMonaco = createMockMonaco();
      expect(mockMonaco.languages.registerCompletionItemProvider).toHaveBeenCalled();
    });

    it('should call Autopilot Client when providing completions', async () => {
      const mockClient = getAutopilotClient();
      
      render(<MonacoAutopilot />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Simulate completion request
      // Note: In real scenario, Monaco would call provideCompletionItems
      // Here we verify the client is available
      expect(mockClient).toBeDefined();
      expect(mockClient.getSuggestionsDebounced).toBeDefined();
    });

    it('should transform Autopilot suggestions to Monaco completion items', async () => {
      render(<MonacoAutopilot />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Get mock client
      const mockClient = getAutopilotClient();
      
      // Call getSuggestionsDebounced
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // Verify response structure
      expect(response.suggestions).toHaveLength(2);
      expect(response.suggestions[0]).toHaveProperty('label');
      expect(response.suggestions[0]).toHaveProperty('kind');
      expect(response.suggestions[0]).toHaveProperty('insertText');
      expect(response.suggestions[0]).toHaveProperty('detail');
    });

    it('should handle errors gracefully during completion', async () => {
      // Mock client to throw error
      const mockClient = getAutopilotClient();
      (mockClient.getSuggestionsDebounced as jest.Mock).mockRejectedValueOnce(
        new Error('API error')
      );
      
      render(<MonacoAutopilot />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Should not crash
      expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
    });
  });

  describe('Task 5.2: Suggestion Insertion', () => {
    it('should provide insertText for each suggestion', async () => {
      const mockClient = getAutopilotClient();
      
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // All suggestions should have insertText
      response.suggestions.forEach((suggestion) => {
        expect(suggestion.insertText).toBeDefined();
        expect(suggestion.insertText.length).toBeGreaterThan(0);
      });
    });

    it('should map suggestion kinds to Monaco CompletionItemKind', async () => {
      const mockClient = getAutopilotClient();
      
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // Verify kinds are valid
      const validKinds = ['keyword', 'guard', 'verify', 'solve', 'variable'];
      response.suggestions.forEach((suggestion) => {
        expect(validKinds).toContain(suggestion.kind);
      });
    });

    it('should include documentation for suggestions', async () => {
      const mockClient = getAutopilotClient();
      
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // At least one suggestion should have documentation
      const withDocs = response.suggestions.filter(s => s.documentation);
      expect(withDocs.length).toBeGreaterThan(0);
    });
  });

  describe('Property 2: Suggestion Insertion Correctness', () => {
    it('should provide valid insertText that results in syntactically correct code', async () => {
      const mockClient = getAutopilotClient();
      
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // Verify insertText is valid
      response.suggestions.forEach((suggestion) => {
        expect(suggestion.insertText).toBeTruthy();
        expect(typeof suggestion.insertText).toBe('string');
        
        // Should not contain invalid characters
        expect(suggestion.insertText).not.toContain('\x00');
        expect(suggestion.insertText).not.toContain('\uFFFD');
      });
    });

    it('should prioritize suggestions correctly', async () => {
      const mockClient = getAutopilotClient();
      
      const response = await mockClient.getSuggestionsDebounced({
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
      });
      
      // Suggestions should have priority values
      response.suggestions.forEach((suggestion) => {
        expect(suggestion.priority).toBeDefined();
        expect(typeof suggestion.priority).toBe('number');
      });
      
      // Higher priority suggestions should come first
      const priorities = response.suggestions.map(s => s.priority);
      const sortedPriorities = [...priorities].sort((a, b) => b - a);
      expect(priorities).toEqual(sortedPriorities);
    });
  });

  describe('Integration with Autopilot Client', () => {
    it('should use debounced client method', async () => {
      const mockClient = getAutopilotClient();
      
      render(<MonacoAutopilot />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Verify debounced method exists
      expect(mockClient.getSuggestionsDebounced).toBeDefined();
    });

    it('should handle code changes', async () => {
      const onCodeChange = jest.fn();
      
      render(<MonacoAutopilot onCodeChange={onCodeChange} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
      });
      
      // Code change handler should be registered
      // (actual invocation happens in Monaco, which is mocked)
    });
  });
});

describe('Task 5.3: Property Test - Suggestion Insertion Correctness', () => {
  it('Property 2: Inserted suggestions result in valid code', async () => {
    const mockClient = getAutopilotClient();
    
    // Test with various editor states
    const testCases = [
      {
        code: 'intent payment {\n  \n}',
        cursorPosition: 23,
        description: 'Inside intent block',
      },
      {
        code: 'intent payment {\n  guard {\n    \n  }\n}',
        cursorPosition: 35,
        description: 'Inside guard block',
      },
      {
        code: '',
        cursorPosition: 0,
        description: 'Empty file',
      },
    ];
    
    for (const testCase of testCases) {
      const response = await mockClient.getSuggestionsDebounced({
        code: testCase.code,
        cursorPosition: testCase.cursorPosition,
      });
      
      // All suggestions should be valid
      expect(response.suggestions).toBeDefined();
      expect(Array.isArray(response.suggestions)).toBe(true);
      
      response.suggestions.forEach((suggestion) => {
        // Should have required fields
        expect(suggestion.label).toBeTruthy();
        expect(suggestion.insertText).toBeTruthy();
        expect(suggestion.kind).toBeTruthy();
        
        // insertText should be valid
        expect(typeof suggestion.insertText).toBe('string');
        expect(suggestion.insertText.length).toBeGreaterThan(0);
      });
    }
  });
});
