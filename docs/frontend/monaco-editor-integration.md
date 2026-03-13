# Monaco Editor Integration Documentation

## Overview

The Aethel-Pilot v3.7 integrates Monaco Editor (the same editor powering VS Code) into the Diotec360 Explorer, providing real-time autocomplete suggestions, safety feedback, and correction tooltips as developers write Aethel code.

**Component**: `MonacoAutopilot.tsx`

**Client Service**: `autopilotClient.ts`

**Feature**: aethel-pilot-v3-7

## Table of Contents

1. [Quick Start](#quick-start)
2. [Component API](#component-api)
3. [Client Service](#client-service)
4. [Configuration](#configuration)
5. [Features](#features)
6. [Customization](#customization)
7. [Performance](#performance)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Basic Usage

```tsx
import MonacoAutopilot from '@/components/MonacoAutopilot';

function MyEditor() {
  const [code, setCode] = useState('');

  return (
    <div style={{ height: '600px' }}>
      <MonacoAutopilot
        initialCode="intent payment {\n  \n}"
        onCodeChange={setCode}
        language="aethel"
      />
    </div>
  );
}
```

### With Custom Styling

```tsx
<div className="w-full h-screen bg-gray-900 p-4">
  <MonacoAutopilot
    initialCode={savedCode}
    onCodeChange={handleCodeChange}
  />
</div>
```

## Component API

### MonacoAutopilot Props

```typescript
interface MonacoAutopilotProps {
  initialCode?: string;
  onCodeChange?: (code: string) => void;
  language?: 'aethel';
}
```

#### Props

- **initialCode** (optional): Initial code to display in the editor
  - Type: `string`
  - Default: `''`
  - Example: `"intent payment {\n  guard {\n    amount > 0\n  }\n}"`

- **onCodeChange** (optional): Callback fired when code changes
  - Type: `(code: string) => void`
  - Called on every keystroke (debounced internally)
  - Example: `(code) => console.log('Code changed:', code)`

- **language** (optional): Editor language
  - Type: `'aethel'`
  - Default: `'aethel'`
  - Currently only supports Aethel language

### Component Features

#### 1. Syntax Highlighting

The editor provides syntax highlighting for Aethel language constructs:

- **Keywords**: `intent`, `guard`, `verify`, `solve`, `using`, `let`, `const`, `if`, `else`, `return`
- **Intent Types**: `payment`, `transfer`, `swap`, `mint`, `burn`, `deposit`, `withdraw`, `stake`, `unstake`
- **Operators**: `=`, `>`, `<`, `!`, `==`, `<=`, `>=`, `!=`, `+`, `-`, `*`, `/`, `%`, `&&`, `||`
- **Comments**: Line comments (`//`) and block comments (`/* */`)
- **Strings**: Double-quoted strings with escape sequences
- **Numbers**: Integers and floating-point numbers

#### 2. IntelliSense Autocomplete

Real-time autocomplete suggestions appear as you type:

- **Trigger Characters**: Space, `.`, `(`, `{`
- **Suggestion Types**:
  - Keywords (intent, guard, verify, solve)
  - Guard conditions (amount > 0, balance >= amount)
  - Verify assertions (conservation laws)
  - Solve options (formal verification methods)
  - Variables (in-scope variables)

**Example**:

```aethel
intent payment {
  guard {
    // Type "am" and suggestions appear:
    // - amount > 0
    // - amount <= max_amount
  }
}
```

#### 3. Traffic Light Safety Feedback

Visual feedback shows code safety status:

- **Green Glow**: Code is safe (no violations detected)
- **Red Glow**: Code has vulnerabilities
- **Blue Glow**: Code is being analyzed
- **No Glow**: Status unknown

The glow transitions smoothly (100ms) when status changes.

**CSS Classes**:

```css
/* Safe - Green glow */
shadow-[0_0_20px_rgba(34,197,94,0.4)]

/* Unsafe - Red glow */
shadow-[0_0_20px_rgba(239,68,68,0.4)]

/* Analyzing - Blue glow */
shadow-[0_0_20px_rgba(59,130,246,0.3)]
```

#### 4. Correction Tooltips

Inline tooltips show correction suggestions for vulnerabilities:

- **Error Decorations**: Red wavy underline with error glyph
- **Warning Decorations**: Yellow wavy underline with warning glyph
- **Hover Message**: Shows vulnerability description and suggested fix
- **Click to Apply**: Clicking applies the correction (future feature)

**Example Tooltip**:

```
**Conservation Violation Detected**

```aethel
verify {
  sender.balance_after == sender.balance_before - amount
  receiver.balance_after == receiver.balance_before + amount
}
```

*Click to apply fix*
```

## Client Service

### AutopilotClient

The `AutopilotClient` class manages communication with the Autopilot API.

#### Creating a Client

```typescript
import { getAutopilotClient } from '@/lib/autopilotClient';

// Get singleton instance with default config
const client = getAutopilotClient();

// Or with custom config
const client = getAutopilotClient({
  apiUrl: '/api/autopilot/suggestions',
  debounceDelay: 500, // 500ms debounce
  maxRetries: 2,
  cacheSize: 200,
});
```

#### Getting Suggestions

```typescript
// Immediate request (no debouncing)
const response = await client.getSuggestions({
  code: 'intent payment {\n  ',
  cursorPosition: 20,
  selection: undefined,
});

// Debounced request (recommended for typing)
const response = await client.getSuggestionsDebounced({
  code: 'intent payment {\n  ',
  cursorPosition: 20,
});
```

#### Response Format

```typescript
interface AutopilotResponse {
  suggestions: Suggestion[];
  safetyStatus: SafetyStatus;
  corrections: CorrectionSuggestion[];
  analysisTime: number;
}

interface Suggestion {
  label: string;
  kind: 'keyword' | 'guard' | 'verify' | 'solve' | 'variable';
  insertText: string;
  detail: string;
  documentation?: string;
  sortText?: string;
  priority: number;
}

interface SafetyStatus {
  status: 'safe' | 'unsafe' | 'analyzing' | 'unknown';
  violations: Violation[];
  analysisTime: number;
}

interface CorrectionSuggestion {
  message: string;
  fix: string;
  line: number;
  severity: 'error' | 'warning';
}
```

#### Client Methods

##### getSuggestions(state: EditorState)

Get suggestions immediately without debouncing.

```typescript
const response = await client.getSuggestions({
  code: 'intent payment {\n  ',
  cursorPosition: 20,
});
```

##### getSuggestionsDebounced(state: EditorState)

Get suggestions with debouncing (300ms default). Recommended for typing.

```typescript
const response = await client.getSuggestionsDebounced({
  code: 'intent payment {\n  ',
  cursorPosition: 20,
});
```

##### cancelPendingRequest()

Cancel any pending request.

```typescript
client.cancelPendingRequest();
```

##### clearCache()

Clear the response cache.

```typescript
client.clearCache();
```

##### getCacheStats()

Get cache statistics.

```typescript
const stats = client.getCacheStats();
console.log(`Cache size: ${stats.size}/${stats.maxSize}`);
```

## Configuration

### Client Configuration

```typescript
interface AutopilotClientConfig {
  apiUrl: string;           // API endpoint URL
  debounceDelay: number;    // Debounce delay in ms
  maxRetries: number;       // Maximum retry attempts
  retryDelay: number;       // Delay between retries in ms
  cacheSize: number;        // Maximum cache entries
  requestTimeout: number;   // Request timeout in ms
}

// Default configuration
const DEFAULT_CONFIG = {
  apiUrl: '/api/autopilot/suggestions',
  debounceDelay: 300,
  maxRetries: 1,
  retryDelay: 1000,
  cacheSize: 100,
  requestTimeout: 5000,
};
```

### Editor Options

The Monaco Editor is configured with these options:

```typescript
{
  minimap: { enabled: false },
  fontSize: 14,
  lineNumbers: 'on',
  roundedSelection: true,
  scrollBeyondLastLine: false,
  automaticLayout: true,
  tabSize: 2,
  wordWrap: 'on',
  wrappingIndent: 'indent',
  padding: { top: 16, bottom: 16 },
  suggestOnTriggerCharacters: true,
  quickSuggestions: {
    other: true,
    comments: false,
    strings: false
  },
  acceptSuggestionOnCommitCharacter: true,
  acceptSuggestionOnEnter: 'on',
  snippetSuggestions: 'top',
  glyphMargin: true,
}
```

## Features

### 1. Request Debouncing

Prevents excessive API calls during rapid typing:

- **Default Delay**: 300ms
- **Behavior**: Only the last request within the debounce window is sent
- **Cancellation**: Previous requests are automatically cancelled

**Example**:

```
User types: "a" -> "am" -> "amo" -> "amou" -> "amoun" -> "amount"
Time:       0ms   50ms   100ms   150ms   200ms    250ms

Only one request is sent at 550ms (250ms + 300ms debounce)
```

### 2. Response Caching

Caches responses to improve performance:

- **Cache Key**: `code:cursorPosition:selection`
- **Cache Size**: 100 entries (configurable)
- **Eviction**: LRU (Least Recently Used)

**Example**:

```typescript
// First request - hits API
await client.getSuggestions({ code: 'intent payment', cursorPosition: 14 });

// Second request - uses cache
await client.getSuggestions({ code: 'intent payment', cursorPosition: 14 });
```

### 3. Request Cancellation

Automatically cancels outdated requests:

- **Trigger**: New request is made before previous completes
- **Behavior**: Previous request is aborted using AbortController
- **Result**: Only the latest request completes

### 4. Error Handling

Graceful error handling with fallback behavior:

- **Network Error**: Returns empty response, logs error
- **Timeout**: Returns empty response after 5 seconds
- **API Error**: Retries once, then returns empty response
- **Abort**: Returns empty response silently

### 5. Retry Logic

Automatic retry on transient failures:

- **Max Retries**: 1 (configurable)
- **Retry Delay**: 1000ms (configurable)
- **Retry Conditions**: Network errors, 5xx status codes
- **No Retry**: 4xx status codes, aborted requests

## Customization

### Custom Theme

Define a custom Monaco theme:

```typescript
monaco.editor.defineTheme('my-theme', {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'keyword', foreground: 'FF00FF', fontStyle: 'bold' },
    { token: 'type.identifier', foreground: '00FFFF' },
  ],
  colors: {
    'editor.background': '#000000',
    'editor.foreground': '#FFFFFF',
  }
});

monaco.editor.setTheme('my-theme');
```

### Custom Completion Provider

Register a custom completion provider:

```typescript
monaco.languages.registerCompletionItemProvider('aethel', {
  triggerCharacters: [' ', '.'],
  
  provideCompletionItems: async (model, position) => {
    // Custom logic here
    return {
      suggestions: [
        {
          label: 'my_suggestion',
          kind: monaco.languages.CompletionItemKind.Keyword,
          insertText: 'my_suggestion',
          detail: 'My custom suggestion',
        }
      ]
    };
  }
});
```

### Custom Decorations

Add custom decorations to the editor:

```typescript
const decorations = editor.deltaDecorations([], [
  {
    range: new monaco.Range(1, 1, 1, 10),
    options: {
      inlineClassName: 'my-decoration',
      hoverMessage: { value: 'My hover message' },
    }
  }
]);
```

## Performance

### Optimization Strategies

1. **Debouncing**: Reduces API calls by 90%+ during typing
2. **Caching**: Eliminates redundant API calls for identical requests
3. **Request Cancellation**: Prevents processing of outdated requests
4. **Parallel Processing**: Suggestions, safety, and corrections run concurrently
5. **Lazy Loading**: Monaco Editor is loaded only when needed

### Performance Metrics

- **Debounce Delay**: 300ms (configurable)
- **API Response Time**: <250ms (95th percentile)
- **Cache Hit Rate**: ~60% for typical usage
- **Memory Usage**: ~50MB for Monaco + ~5MB for cache

### Performance Tips

1. **Increase Debounce Delay**: For slower networks, increase to 500ms
2. **Increase Cache Size**: For large files, increase to 200+ entries
3. **Disable Features**: Disable minimap, word wrap for better performance
4. **Reduce Font Size**: Smaller fonts render faster

## Troubleshooting

### Common Issues

#### 1. Suggestions Not Appearing

**Symptoms**: No autocomplete suggestions when typing

**Causes**:
- API endpoint not responding
- Network error
- Rate limit exceeded

**Solutions**:
```typescript
// Check API health
fetch('/api/autopilot/health')
  .then(r => r.json())
  .then(console.log);

// Check browser console for errors
// Check network tab for failed requests
```

#### 2. Slow Performance

**Symptoms**: Editor feels sluggish, suggestions delayed

**Causes**:
- Debounce delay too short
- Cache size too small
- Large file size

**Solutions**:
```typescript
// Increase debounce delay
const client = getAutopilotClient({
  debounceDelay: 500, // Increase to 500ms
});

// Increase cache size
const client = getAutopilotClient({
  cacheSize: 200, // Increase to 200 entries
});
```

#### 3. Traffic Light Not Updating

**Symptoms**: Safety status glow doesn't change

**Causes**:
- Judge service not responding
- API returning unknown status
- CSS not loaded

**Solutions**:
```typescript
// Check safety status in response
const response = await client.getSuggestions(state);
console.log('Safety status:', response.safetyStatus);

// Check CSS classes are applied
// Inspect element in browser DevTools
```

#### 4. Corrections Not Showing

**Symptoms**: No correction tooltips for unsafe code

**Causes**:
- No corrections in API response
- Decorations not applied
- Line numbers incorrect

**Solutions**:
```typescript
// Check corrections in response
const response = await client.getSuggestions(state);
console.log('Corrections:', response.corrections);

// Check decorations are applied
console.log('Decorations:', decorationsRef.current);
```

### Debug Mode

Enable debug logging:

```typescript
// In autopilotClient.ts, add logging
console.log('Request:', state);
console.log('Response:', response);
console.log('Cache stats:', client.getCacheStats());
```

### Browser Compatibility

- **Chrome**: ✅ Fully supported
- **Firefox**: ✅ Fully supported
- **Safari**: ✅ Fully supported
- **Edge**: ✅ Fully supported
- **IE11**: ❌ Not supported

### Known Limitations

1. **Large Files**: Performance degrades for files >1000 lines
2. **Mobile**: Touch support is limited
3. **Offline**: Requires network connection for suggestions
4. **Language**: Only Aethel language is supported

## Examples

### Example 1: Basic Editor

```tsx
import MonacoAutopilot from '@/components/MonacoAutopilot';

export default function BasicEditor() {
  return (
    <div className="h-screen">
      <MonacoAutopilot
        initialCode="intent payment {\n  \n}"
      />
    </div>
  );
}
```

### Example 2: Editor with Save

```tsx
import { useState } from 'react';
import MonacoAutopilot from '@/components/MonacoAutopilot';

export default function EditorWithSave() {
  const [code, setCode] = useState('');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('aethel-code', code);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="h-screen flex flex-col">
      <div className="p-4 bg-gray-800">
        <button
          onClick={handleSave}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          {saved ? 'Saved!' : 'Save'}
        </button>
      </div>
      <div className="flex-1">
        <MonacoAutopilot
          initialCode={localStorage.getItem('aethel-code') || ''}
          onCodeChange={setCode}
        />
      </div>
    </div>
  );
}
```

### Example 3: Editor with Custom Client

```tsx
import { useEffect, useState } from 'react';
import MonacoAutopilot from '@/components/MonacoAutopilot';
import { getAutopilotClient } from '@/lib/autopilotClient';

export default function CustomClientEditor() {
  const [client, setClient] = useState(null);

  useEffect(() => {
    // Create client with custom config
    const customClient = getAutopilotClient({
      debounceDelay: 500,
      cacheSize: 200,
      maxRetries: 2,
    });
    setClient(customClient);
  }, []);

  return (
    <div className="h-screen">
      <MonacoAutopilot
        initialCode="intent payment {\n  \n}"
      />
    </div>
  );
}
```

## API Reference

See [Autopilot API Documentation](../api/autopilot-api.md) for complete API reference.

## Support

For issues or questions:

- GitHub Issues: [diotec360-lang/aethel](https://github.com/diotec360-lang/diotec360/issues)
- Documentation: [docs.diotec360-lang.org](https://docs.diotec360-lang.org)
- Email: support@diotec360-lang.org
