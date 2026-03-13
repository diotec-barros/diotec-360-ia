# Autopilot API Documentation

## Overview

The Autopilot API provides real-time autocomplete suggestions, safety status analysis, and correction suggestions for Aethel code as developers type in the Monaco Editor. This API is part of the Aethel-Pilot v3.7 feature.

**Base URL**: `/api/autopilot`

**Version**: 1.0.0

**Feature**: aethel-pilot-v3-7

## Endpoints

### POST /api/autopilot/suggestions

Get autocomplete suggestions and safety status for the current editor state.

**Performance Target**: 95% of requests complete within 250ms

**Rate Limit**: 100 requests per minute per IP address

#### Request

**Content-Type**: `application/json`

**Request Body**:

```json
{
  "code": "string",
  "cursor_position": "integer (>= 0)",
  "selection": {
    "start": "integer",
    "end": "integer"
  } | null
}
```

**Fields**:

- `code` (required): Current code in the editor
- `cursor_position` (required): Cursor position in the code (0-indexed)
- `selection` (optional): Selection range with start and end positions

**Example Request**:

```json
{
  "code": "intent payment {\n  guard {\n    ",
  "cursor_position": 35,
  "selection": null
}
```

#### Response

**Status Code**: `200 OK`

**Response Body**:

```json
{
  "suggestions": [
    {
      "label": "string",
      "kind": "string",
      "insert_text": "string",
      "detail": "string",
      "documentation": "string | null",
      "sort_text": "string | null",
      "priority": "integer"
    }
  ],
  "safety_status": {
    "status": "string",
    "violations": [
      {
        "type": "string",
        "description": "string",
        "line": "integer | null",
        "severity": "string"
      }
    ],
    "analysis_time": "float"
  },
  "corrections": [
    {
      "message": "string",
      "fix": "string",
      "line": "integer",
      "severity": "string"
    }
  ],
  "analysis_time": "float"
}
```

**Response Fields**:

- `suggestions`: Array of autocomplete suggestions
  - `label`: Display text for the suggestion
  - `kind`: Type of suggestion (`keyword`, `guard`, `verify`, `solve`, `variable`)
  - `insert_text`: Code to insert at cursor position
  - `detail`: Short description of the suggestion
  - `documentation`: Optional longer explanation
  - `sort_text`: Optional text for custom sorting
  - `priority`: Higher values appear first (default: 0)

- `safety_status`: Safety analysis of the code
  - `status`: One of `safe`, `unsafe`, `analyzing`, `unknown`
  - `violations`: Array of detected violations
    - `type`: Type of violation (e.g., `conservation`, `overflow`, `reentrancy`)
    - `description`: Human-readable description
    - `line`: Optional line number where violation occurs
    - `severity`: Either `error` or `warning`
  - `analysis_time`: Time taken for safety analysis (milliseconds)

- `corrections`: Array of correction suggestions for vulnerabilities
  - `message`: Human-readable description of the issue
  - `fix`: Suggested code fix
  - `line`: Line number of the issue
  - `severity`: Either `error` or `warning`

- `analysis_time`: Total time for request processing (milliseconds)

**Example Response**:

```json
{
  "suggestions": [
    {
      "label": "amount > 0",
      "kind": "guard",
      "insert_text": "amount > 0",
      "detail": "Guard condition: amount must be positive",
      "documentation": "Ensures the payment amount is positive before processing",
      "priority": 10
    },
    {
      "label": "sender.balance >= amount",
      "kind": "guard",
      "insert_text": "sender.balance >= amount",
      "detail": "Guard condition: sender has sufficient balance",
      "priority": 9
    }
  ],
  "safety_status": {
    "status": "safe",
    "violations": [],
    "analysis_time": 45.2
  },
  "corrections": [],
  "analysis_time": 123.5
}
```

#### Error Responses

**400 Bad Request**

Invalid request format or missing required fields.

```json
{
  "detail": "Field required: code"
}
```

**429 Too Many Requests**

Rate limit exceeded (more than 100 requests per minute).

```json
{
  "detail": "Rate limit exceeded. Maximum 100 requests per minute."
}
```

**503 Service Unavailable**

Service temporarily unavailable due to resource constraints.

```json
{
  "detail": "Service temporarily unavailable due to resource constraints"
}
```

**500 Internal Server Error**

Unexpected server error. The API will attempt to return partial results when possible.

```json
{
  "suggestions": [],
  "safety_status": {
    "status": "unknown",
    "violations": [],
    "analysis_time": 0
  },
  "corrections": [],
  "analysis_time": 150.0
}
```

### GET /api/autopilot/health

Health check endpoint to verify the service is running.

#### Response

**Status Code**: `200 OK`

```json
{
  "status": "healthy",
  "service": "autopilot",
  "timestamp": "2026-02-21T10:30:00.000Z"
}
```

### GET /api/autopilot/stats

Get API usage statistics.

#### Response

**Status Code**: `200 OK`

```json
{
  "total_requests": 1234,
  "active_clients": 15,
  "rate_limit": 100,
  "rate_window": 60
}
```

**Response Fields**:

- `total_requests`: Total number of requests in the current time window
- `active_clients`: Number of unique clients with active requests
- `rate_limit`: Maximum requests per client per time window
- `rate_window`: Time window in seconds

## Error Handling

The Autopilot API implements graceful degradation to ensure the system continues functioning even when errors occur:

1. **Invalid Code**: Returns empty suggestions with `unknown` status instead of crashing
2. **Timeout**: Returns partial results if analysis exceeds 250ms timeout
3. **Judge Failure**: Returns suggestions without safety status if Judge is unavailable
4. **Resource Exhaustion**: Returns 503 status code with retry-after header

All errors are logged server-side for debugging and monitoring.

## Performance Characteristics

- **Target Response Time**: 95% of requests complete within 250ms
- **Timeout**: Requests are cancelled after 250ms, returning partial results
- **Parallel Processing**: Suggestions, safety analysis, and corrections run concurrently
- **Caching**: Analysis results are cached for identical code to improve performance

## Rate Limiting

- **Limit**: 100 requests per minute per IP address
- **Window**: 60 seconds rolling window
- **Response**: 429 status code when limit exceeded
- **Headers**: No rate limit headers currently implemented

## Integration Examples

### JavaScript/TypeScript (Frontend)

```typescript
async function getSuggestions(code: string, cursorPosition: number) {
  try {
    const response = await fetch('/api/autopilot/suggestions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code,
        cursor_position: cursorPosition,
        selection: null
      })
    });

    if (!response.ok) {
      if (response.status === 429) {
        console.warn('Rate limit exceeded');
        return null;
      }
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to get suggestions:', error);
    return null;
  }
}
```

### Python

```python
import requests

def get_suggestions(code: str, cursor_position: int):
    try:
        response = requests.post(
            'http://localhost:8000/api/autopilot/suggestions',
            json={
                'code': code,
                'cursor_position': cursor_position,
                'selection': None
            },
            timeout=1.0
        )
        
        if response.status_code == 429:
            print('Rate limit exceeded')
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f'Failed to get suggestions: {e}')
        return None
```

### cURL

```bash
curl -X POST http://localhost:8000/api/autopilot/suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "code": "intent payment {\n  guard {\n    ",
    "cursor_position": 35,
    "selection": null
  }'
```

## Best Practices

1. **Debouncing**: Implement client-side debouncing (300ms recommended) to avoid overwhelming the API during rapid typing

2. **Request Cancellation**: Cancel pending requests when new ones are made to avoid processing outdated requests

3. **Caching**: Cache responses based on code + cursor position to reduce API calls

4. **Error Handling**: Always handle errors gracefully and provide fallback behavior

5. **Retry Logic**: Implement exponential backoff for retries on transient failures

6. **Timeout**: Set client-side timeout to 1-2 seconds to avoid hanging requests

## Monitoring and Observability

The API logs the following events:

- **Request Timeout**: When analysis exceeds 250ms
- **Invalid Code**: When code cannot be parsed
- **Resource Exhaustion**: When memory limits are reached
- **Unexpected Errors**: All unhandled exceptions

Monitor these metrics:

- **Response Time**: P50, P95, P99 latency
- **Error Rate**: Percentage of failed requests
- **Rate Limit Hits**: Number of 429 responses
- **Cache Hit Rate**: Percentage of cached responses (client-side)

## Security Considerations

1. **Rate Limiting**: Prevents abuse and DoS attacks
2. **Input Validation**: All inputs are validated using Pydantic models
3. **Code Size Limit**: Maximum code size is 10KB (enforced by FastAPI)
4. **Timeout Protection**: Analysis is cancelled after 250ms to prevent resource exhaustion
5. **Error Information**: Internal errors are not exposed to clients

## Changelog

### Version 1.0.0 (2026-02-20)

- Initial release
- POST /api/autopilot/suggestions endpoint
- GET /api/autopilot/health endpoint
- GET /api/autopilot/stats endpoint
- Rate limiting (100 req/min per IP)
- Graceful error handling
- Parallel processing of suggestions, safety, and corrections
- 250ms timeout with partial results

## Support

For issues or questions:

- GitHub Issues: [diotec360-lang/aethel](https://github.com/diotec360-lang/diotec360/issues)
- Documentation: [docs.diotec360-lang.org](https://docs.diotec360-lang.org)
- Email: support@diotec360-lang.org
