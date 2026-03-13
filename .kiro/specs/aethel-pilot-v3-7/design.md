# Design Document: Aethel-Pilot v3.7

## Overview

The Aethel-Pilot v3.7 transforms the Aethel Explorer from a passive code analysis tool into an active development environment with real-time predictive autocomplete. The system integrates Monaco Editor (the same editor powering VS Code) into the frontend and connects it to the existing `autopilot_engine.py` backend through a new FastAPI endpoint.

The architecture follows a three-tier approach:
1. **Frontend**: Monaco Editor with custom Aethel language support and real-time UI feedback
2. **API Layer**: FastAPI endpoint that bridges frontend requests to backend services
3. **Backend**: Enhanced Autopilot Engine that leverages existing Judge and Ghost-Runner

Key design principles:
- **Sub-200ms latency**: Suggestions must feel instant to maintain developer flow
- **Reuse existing verification**: Leverage Judge and conservation validator for consistency
- **Progressive enhancement**: Start with basic autocomplete, add advanced features incrementally
- **Graceful degradation**: System continues working even if backend is slow or unavailable

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Monaco Editor Component                   │    │
│  │  - Syntax highlighting                              │    │
│  │  - IntelliSense provider                            │    │
│  │  - Traffic light decorator                          │    │
│  │  - Correction tooltip renderer                      │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↕                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Autopilot Client Service                    │    │
│  │  - Request debouncing (300ms)                       │    │
│  │  - Request cancellation                             │    │
│  │  - Response caching                                 │    │
│  │  - Error handling                                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │      /api/autopilot/suggestions                     │    │
│  │  - Request validation                               │    │
│  │  - Rate limiting                                    │    │
│  │  - Response formatting                              │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services                          │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Autopilot Engine                            │    │
│  │  - Context detection                                │    │
│  │  - Suggestion generation                            │    │
│  │  - Safety status analysis                           │    │
│  │  - Correction stream                                │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↕                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │    Existing Verification Services                   │    │
│  │  - Judge (formal verification)                      │    │
│  │  - Conservation Validator                           │    │
│  │  - Ghost Runner (prediction)                        │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Types**: Developer types in Monaco Editor
2. **Debounce**: Frontend waits 300ms for typing to pause
3. **Request**: Frontend sends `{ code, cursorPosition, selection }` to API
4. **Analysis**: Autopilot Engine analyzes context and generates suggestions
5. **Verification**: Engine uses Judge to validate safety status
6. **Response**: API returns `{ suggestions, safetyStatus, corrections }`
7. **Render**: Frontend updates Monaco Editor with suggestions and traffic light

### Technology Stack

- **Frontend**: Next.js 14, React 18, Monaco Editor, TypeScript
- **API**: FastAPI, Python 3.11+
- **Backend**: Existing Autopilot Engine (Python)
- **Communication**: REST API with JSON payloads
- **Styling**: Tailwind CSS (consistent with existing Explorer)

## Components and Interfaces

### 1. Monaco Editor Integration (Frontend)

**File**: `frontend/components/MonacoAutopilot.tsx`

```typescript
interface MonacoAutopilotProps {
  initialCode?: string;
  onCodeChange?: (code: string) => void;
  language?: 'aethel';
}

interface EditorState {
  code: string;
  cursorPosition: number;
  selection?: { start: number; end: number };
}

interface Suggestion {
  label: string;
  kind: 'keyword' | 'guard' | 'verify' | 'solve' | 'variable';
  insertText: string;
  detail: string;
  documentation?: string;
  sortText?: string;
}

interface SafetyStatus {
  status: 'safe' | 'unsafe' | 'analyzing' | 'unknown';
  violations: Array<{
    type: string;
    description: string;
    line?: number;
    severity: 'error' | 'warning';
  }>;
}

interface CorrectionSuggestion {
  message: string;
  fix: string;
  line: number;
  severity: 'error' | 'warning';
}
```

**Key Methods**:
- `setupMonacoEditor()`: Initialize Monaco with Aethel language support
- `registerCompletionProvider()`: Register custom IntelliSense provider
- `updateTrafficLight(status)`: Update background glow based on safety status
- `showCorrectionTooltip(correction)`: Display inline correction suggestion
- `applySuggestion(suggestion)`: Insert selected suggestion at cursor

### 2. Autopilot Client Service (Frontend)

**File**: `frontend/lib/autopilotClient.ts`

```typescript
interface AutopilotRequest {
  code: string;
  cursorPosition: number;
  selection?: { start: number; end: number };
}

interface AutopilotResponse {
  suggestions: Suggestion[];
  safetyStatus: SafetyStatus;
  corrections: CorrectionSuggestion[];
  analysisTime: number;
}

class AutopilotClient {
  private debounceTimer: NodeJS.Timeout | null;
  private currentRequest: AbortController | null;
  private cache: Map<string, AutopilotResponse>;
  
  async getSuggestions(state: EditorState): Promise<AutopilotResponse>;
  private debounce(fn: Function, delay: number): Function;
  private cancelPendingRequest(): void;
  private getCacheKey(state: EditorState): string;
}
```

**Key Features**:
- Request debouncing (300ms default)
- Automatic request cancellation for outdated requests
- Response caching based on code + cursor position
- Retry logic with exponential backoff
- Error handling and fallback to empty suggestions

### 3. API Endpoint (Backend)

**File**: `api/autopilot.py` (new file)

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from aethel.ai.autopilot_engine import get_autopilot, EditorState, Suggestion

router = APIRouter(prefix="/api/autopilot", tags=["autopilot"])

class SuggestionsRequest(BaseModel):
    code: str
    cursor_position: int
    selection: Optional[Dict[str, int]] = None

class SuggestionsResponse(BaseModel):
    suggestions: List[Dict[str, Any]]
    safety_status: Dict[str, Any]
    corrections: List[Dict[str, Any]]
    analysis_time: float

@router.post("/suggestions")
async def get_suggestions(request: SuggestionsRequest) -> SuggestionsResponse:
    """
    Get autocomplete suggestions and safety status for current editor state.
    
    Returns suggestions within 200ms target, safety status, and any
    correction suggestions for detected vulnerabilities.
    """
    pass
```

**Key Features**:
- Request validation using Pydantic models
- Rate limiting (100 requests per minute per IP)
- Response time monitoring
- Error handling with appropriate HTTP status codes
- Integration with existing Autopilot Engine

### 4. Enhanced Autopilot Engine (Backend)

**File**: `aethel/ai/autopilot_engine.py` (existing, enhanced)

The existing engine already has the core methods:
- `get_suggestions(editor_state)`: Returns autocomplete suggestions
- `get_safety_status(code)`: Returns traffic light status
- `get_correction_stream(code)`: Returns correction suggestions

**Enhancements needed**:
- Performance optimization to meet 200ms target
- Better context detection for cursor position
- Integration with Judge for real-time verification
- Caching of analysis results
- Parallel processing of suggestions and safety status

## Data Models

### EditorState

```python
@dataclass
class EditorState:
    code: str
    cursor_position: int
    selection: Optional[tuple[int, int]] = None
    
    def get_current_line(self) -> str:
        """Get the line where cursor is located"""
        
    def get_context_before_cursor(self, chars: int = 100) -> str:
        """Get code context before cursor"""
        
    def get_context_after_cursor(self, chars: int = 100) -> str:
        """Get code context after cursor"""
```

### Suggestion

```python
@dataclass
class Suggestion:
    label: str  # Display text
    kind: str  # keyword, guard, verify, solve, variable
    insert_text: str  # Code to insert
    detail: str  # Short description
    documentation: Optional[str] = None  # Longer explanation
    sort_text: Optional[str] = None  # For ordering
    priority: int = 0  # Higher = shown first
```

### SafetyStatus

```python
@dataclass
class SafetyStatus:
    status: str  # safe, unsafe, analyzing, unknown
    violations: List[Violation]
    analysis_time: float
    
@dataclass
class Violation:
    type: str  # conservation, overflow, reentrancy, etc.
    description: str
    line: Optional[int] = None
    severity: str = "error"  # error or warning
```

### CorrectionSuggestion

```python
@dataclass
class CorrectionSuggestion:
    message: str  # Human-readable description
    fix: str  # Suggested code fix
    line: int  # Line number of issue
    severity: str = "error"  # error or warning
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Context-Aware Suggestion Filtering

*For any* editor state with a cursor position inside a specific Aethel block type (guard, verify, solve, or intent), the Autopilot Engine should return only suggestions that are appropriate for that block type, and all returned suggestions should be valid for that context.

**Validates: Requirements 2.2, 2.3, 2.4, 8.3, 8.4**

### Property 2: Suggestion Insertion Correctness

*For any* suggestion selected by the user, inserting the suggestion at the cursor position should result in syntactically valid code at that position, and the cursor should be positioned correctly after insertion.

**Validates: Requirements 2.7**

### Property 3: End-to-End Response Time

*For any* valid autocomplete request, the API endpoint should return a complete response (suggestions, safety status, and corrections) within 250ms, measured from request receipt to response sent.

**Validates: Requirements 2.8, 6.6, 10.1, 10.2**

### Property 4: Traffic Light Accuracy

*For any* code analyzed by the system, if the Judge determines the code is safe (no violations), the traffic light should display green; if the Judge determines the code has violations, the traffic light should display red; and the displayed status should match the Judge's verdict.

**Validates: Requirements 3.1, 3.2**

### Property 5: Traffic Light Transition Performance

*For any* change in safety status, the visual feedback transition should complete within 100ms of the status change being detected.

**Validates: Requirements 3.4**

### Property 6: Correction Generation Completeness

*For any* code that contains detectable vulnerabilities (conservation violations, overflow risks, underflow risks, reentrancy patterns, or missing guards), the Autopilot Engine should generate at least one correction suggestion that addresses the vulnerability.

**Validates: Requirements 4.1, 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 7: Correction Content Completeness

*For any* correction suggestion generated, the correction should include both a vulnerability type description and a recommended fix, and the fix should be non-empty valid code.

**Validates: Requirements 4.3**

### Property 8: Correction Application Correctness

*For any* correction suggestion applied by the user, the resulting code should have the fix inserted at the correct location, and the modified code should pass Judge validation (no new violations introduced).

**Validates: Requirements 4.4, 9.3**

### Property 9: Correction Timing

*For any* vulnerability detected during analysis, a correction suggestion should be generated and made available to the frontend within 200ms of detection.

**Validates: Requirements 4.5**

### Property 10: API Request Validation

*For any* request received by the API endpoint, if the request is missing required fields (code or cursor_position), the endpoint should return a 400 Bad Request status with an error message; if the request is valid, the endpoint should invoke the Autopilot Engine.

**Validates: Requirements 6.2, 6.3**

### Property 11: API Response Format

*For any* successful API response, the response should be valid JSON containing suggestions array, safety_status object, and corrections array, and the JSON should be parseable by the frontend.

**Validates: Requirements 6.4**

### Property 12: API Error Handling

*For any* error that occurs during request processing (engine failure, timeout, invalid input), the API endpoint should return an appropriate HTTP error status (4xx for client errors, 5xx for server errors) and a JSON error message.

**Validates: Requirements 6.5**

### Property 13: Request Debouncing

*For any* sequence of typing events in the editor, if events occur within 300ms of each other, only the final event should trigger an API request, and any pending requests from previous events should be cancelled.

**Validates: Requirements 7.1, 7.2, 7.4**

### Property 14: UI Update Consistency

*For any* API response received by the frontend, the UI should be updated to reflect all three components: suggestions should be available in the completion provider, safety status should update the traffic light, and corrections should be displayed as tooltips.

**Validates: Requirements 7.3**

### Property 15: Keyword Suggestion at Line Start

*For any* cursor position at the start of a line (after only whitespace), the Autopilot Engine should include Aethel keywords (intent, guard, verify, solve) in the suggestions.

**Validates: Requirements 8.1**

### Property 16: Intent Type Suggestions

*For any* cursor position immediately after the keyword "intent" (with optional whitespace), the Autopilot Engine should suggest valid intent types (payment, transfer, swap, etc.).

**Validates: Requirements 8.2, 2.5**

### Property 17: Variable Scope Inclusion

*For any* editor state where variables are defined in the current scope, those variables should be included in the suggestions list with appropriate metadata (name, type if available).

**Validates: Requirements 8.5**

### Property 18: Judge Integration Consistency

*For any* code analyzed by the Autopilot Engine, the safety status should be determined by calling the existing Judge, and the result should be consistent with calling `/api/verify` with the same code.

**Validates: Requirements 9.1, 9.2, 9.5**

### Property 19: Suggestion Cache Effectiveness

*For any* repeated request with identical code and cursor position, the frontend cache should return the cached response without making a new API call, and the cached response should be identical to the original response.

**Validates: Requirements 10.4**

### Property 20: Concurrent User Handling

*For any* load test with 10 concurrent users making autocomplete requests, the system should maintain response times within acceptable limits (95th percentile under 250ms) and no requests should fail due to resource exhaustion.

**Validates: Requirements 10.5**

### Property 21: Rapid Typing Non-Interruption

*For any* sequence of rapid typing events (less than 300ms apart), the system should not display suggestion popups or tooltips until typing pauses, ensuring the user's flow is not interrupted.

**Validates: Requirements 11.4**

### Property 22: Graceful Invalid Input Handling

*For any* invalid or malformed Aethel code submitted to the Autopilot Engine, the system should return an empty suggestions array rather than throwing an exception or crashing.

**Validates: Requirements 12.3**

### Property 23: Error Logging and Continuation

*For any* unexpected error that occurs during processing, the system should log the error with sufficient detail for debugging and continue functioning for subsequent requests.

**Validates: Requirements 12.4**

## Error Handling

### Frontend Error Handling

1. **API Unavailable**: Display error banner, disable autocomplete, retry connection every 30 seconds
2. **Request Timeout**: Cancel request after 5 seconds, retry once, then show error
3. **Invalid Response**: Log error, fall back to empty suggestions, continue functioning
4. **Network Error**: Show offline indicator, queue requests for retry when connection restored

### Backend Error Handling

1. **Invalid Code**: Return empty suggestions with status "unknown"
2. **Judge Failure**: Return suggestions without safety status, log error
3. **Timeout**: Cancel analysis after 200ms, return partial results if available
4. **Resource Exhaustion**: Return 503 Service Unavailable, implement backpressure

### Error Recovery

- Frontend automatically retries failed requests with exponential backoff
- Backend implements circuit breaker pattern for Judge integration
- System health monitoring alerts on error rate > 5%
- Graceful degradation: suggestions work even if safety analysis fails

## Testing Strategy

### Dual Testing Approach

The testing strategy employs both unit tests and property-based tests as complementary approaches:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs
- Together they provide comprehensive coverage

### Unit Testing Focus

Unit tests should focus on:
- Specific example scenarios (e.g., "typing 'intent payment' suggests 'amount' parameter")
- Integration points between components (Monaco ↔ Client ↔ API ↔ Engine)
- Edge cases (empty code, cursor at end of file, malformed requests)
- Error conditions (API down, timeout, invalid response)

Avoid writing too many unit tests for scenarios that property tests cover comprehensively.

### Property-Based Testing Configuration

- **Library**: Use `hypothesis` for Python backend, `fast-check` for TypeScript frontend
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each test must reference its design property

Tag format: `# Feature: aethel-pilot-v3-7, Property {number}: {property_text}`

Example:
```python
@given(editor_state=editor_states(), block_type=sampled_from(['guard', 'verify', 'solve']))
def test_property_1_context_aware_suggestions(editor_state, block_type):
    """
    Feature: aethel-pilot-v3-7, Property 1: Context-Aware Suggestion Filtering
    
    For any editor state with cursor inside a specific block type,
    suggestions should only include context-appropriate options.
    """
    # Test implementation
```

### Test Coverage Requirements

1. **Property 1-2**: Test suggestion generation and insertion
2. **Property 3, 5, 9**: Test performance and timing requirements
3. **Property 4, 6-8**: Test safety analysis and corrections
4. **Property 10-14**: Test API layer behavior
5. **Property 15-17**: Test context detection
6. **Property 18**: Test Judge integration
7. **Property 19-21**: Test frontend behavior
8. **Property 22-23**: Test error handling

### Integration Testing

- End-to-end tests with real Monaco Editor instance
- API integration tests with real Autopilot Engine
- Load testing with 10+ concurrent users
- Performance testing to verify 200ms target

### Performance Testing

- Measure P50, P95, P99 response times
- Test with various code sizes (10 lines to 1000 lines)
- Test with various cursor positions
- Monitor memory usage and CPU utilization

## Implementation Notes

### Phase 1: Core Integration (MVP)
1. Monaco Editor component with basic Aethel syntax
2. API endpoint with request/response handling
3. Basic suggestion generation (keywords only)
4. Simple traffic light (green/red based on Judge)

### Phase 2: Enhanced Suggestions
1. Context-aware suggestions (guard, verify, solve)
2. Variable extraction and suggestion
3. Intent parameter suggestions
4. Suggestion prioritization and sorting

### Phase 3: Corrections and Polish
1. Correction suggestion generation
2. Inline tooltip rendering
3. One-click correction application
4. Performance optimization

### Phase 4: Advanced Features
1. Caching and optimization
2. WebSocket for real-time updates (optional)
3. Suggestion learning from user behavior
4. Advanced vulnerability pattern detection

### Performance Optimization Strategies

1. **Caching**: Cache analysis results for identical code
2. **Debouncing**: Prevent excessive API calls during typing
3. **Parallel Processing**: Run suggestions and safety analysis concurrently
4. **Incremental Analysis**: Only re-analyze changed portions of code
5. **Request Cancellation**: Cancel outdated requests immediately

### Security Considerations

1. **Rate Limiting**: 100 requests per minute per IP
2. **Input Validation**: Sanitize code input, limit size to 10KB
3. **Resource Limits**: Timeout analysis after 200ms
4. **Error Information**: Don't expose internal errors to frontend
5. **CORS**: Restrict API access to known origins

## Deployment Considerations

### Frontend Deployment
- Monaco Editor bundle size: ~2MB (use code splitting)
- Lazy load Monaco only when Explorer page is accessed
- CDN for Monaco assets
- Service worker for offline support (optional)

### Backend Deployment
- API endpoint deployed with existing FastAPI app
- No additional infrastructure required
- Monitor response times and error rates
- Scale horizontally if needed (stateless design)

### Monitoring and Observability
- Log all API requests with timing
- Track suggestion acceptance rate
- Monitor traffic light accuracy
- Alert on error rate > 5% or P95 latency > 300ms
