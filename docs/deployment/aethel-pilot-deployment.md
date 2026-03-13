# Aethel-Pilot v3.7 Deployment Guide

## Overview

This guide covers the deployment of Aethel-Pilot v3.7, which adds real-time autocomplete, safety feedback, and correction suggestions to the Diotec360 Explorer.

**Feature**: aethel-pilot-v3-7

**Components**:
- Backend: FastAPI Autopilot API endpoint
- Frontend: Monaco Editor with Aethel language support
- Integration: Autopilot Engine, Judge, Conservation Validator

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Steps](#deployment-steps)
3. [Configuration](#configuration)
4. [Monitoring and Alerting](#monitoring-and-alerting)
5. [Performance Tuning](#performance-tuning)
6. [Rollback Procedures](#rollback-procedures)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Backend**:
- Python 3.11+
- FastAPI 0.104+
- 2GB RAM minimum (4GB recommended)
- 2 CPU cores minimum (4 cores recommended)

**Frontend**:
- Node.js 18+
- Next.js 14+
- 1GB RAM minimum (2GB recommended)

**Network**:
- HTTPS enabled (required for production)
- WebSocket support (optional, for future features)
- CDN for static assets (recommended)

### Dependencies

**Backend Dependencies**:
```bash
pip install fastapi>=0.104.0
pip install pydantic>=2.0.0
pip install uvicorn>=0.24.0
```

**Frontend Dependencies**:
```bash
npm install @monaco-editor/react@^4.6.0
npm install monaco-editor@^0.45.0
```

### Environment Variables

Create `.env` file with:

```bash
# Backend
AUTOPILOT_API_URL=/api/autopilot/suggestions
AUTOPILOT_RATE_LIMIT=100
AUTOPILOT_TIMEOUT=250

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTOPILOT_DEBOUNCE=300
NEXT_PUBLIC_AUTOPILOT_CACHE_SIZE=100
```

## Deployment Steps

### Step 1: Backend Deployment

#### 1.1 Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

#### 1.2 Verify Autopilot Engine

```bash
python -c "from diotec360.ai.autopilot_engine import AethelAutopilot; print('OK')"
```

#### 1.3 Mount API Router

In `api/main.py`, add:

```python
from api.autopilot import router as autopilot_router

app.include_router(autopilot_router)
```

#### 1.4 Configure CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 1.5 Start Backend Server

**Development**:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Production**:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 1.6 Verify Backend

```bash
curl http://localhost:8000/api/autopilot/health
# Expected: {"status":"healthy","service":"autopilot","timestamp":"..."}
```

### Step 2: Frontend Deployment

#### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

#### 2.2 Configure API URL

In `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2.3 Build Frontend

**Development**:
```bash
npm run dev
```

**Production**:
```bash
npm run build
npm start
```

#### 2.4 Verify Frontend

Open browser to `http://localhost:3000/explorer` and verify:
- Monaco Editor loads
- Syntax highlighting works
- Autocomplete suggestions appear when typing
- Traffic light glow appears

### Step 3: Integration Testing

#### 3.1 Test Autocomplete

1. Open Explorer page
2. Type `intent payment {`
3. Press Enter and type `guard {`
4. Verify suggestions appear

#### 3.2 Test Traffic Light

1. Write safe code:
```aethel
intent payment {
  guard {
    amount > 0
  }
  verify {
    sender.balance_after == sender.balance_before - amount
  }
}
```
2. Verify green glow appears

3. Write unsafe code (remove verify block)
4. Verify red glow appears

#### 3.3 Test Corrections

1. Write code with conservation violation
2. Verify red underline appears
3. Hover over underline
4. Verify correction tooltip appears

#### 3.4 Run Integration Tests

```bash
# Backend tests
pytest test_task_4_checkpoint.py
pytest test_task_8_checkpoint.py
pytest test_task_17_integration.py

# Frontend tests
npm test -- MonacoAutopilot.test.tsx
npm test -- autopilotClient.test.ts
```

### Step 4: Production Deployment

#### 4.1 Backend Production Setup

**Using Docker**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Build and run:
```bash
docker build -t aethel-backend .
docker run -p 8000:8000 aethel-backend
```

**Using systemd**:

Create `/etc/systemd/system/aethel-backend.service`:

```ini
[Unit]
Description=Aethel Backend API
After=network.target

[Service]
Type=simple
User=aethel
WorkingDirectory=/opt/aethel
Environment="PATH=/opt/diotec360/venv/bin"
ExecStart=/opt/diotec360/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable aethel-backend
sudo systemctl start aethel-backend
```

#### 4.2 Frontend Production Setup

**Using Vercel** (Recommended):

```bash
npm install -g vercel
vercel --prod
```

**Using Docker**:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t aethel-frontend .
docker run -p 3000:3000 aethel-frontend
```

**Using Nginx**:

Build static files:
```bash
npm run build
npm run export
```

Nginx config:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    root /var/www/diotec360/out;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 4.3 SSL/TLS Setup

**Using Let's Encrypt**:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

**Using Cloudflare**:

1. Add domain to Cloudflare
2. Enable "Full (strict)" SSL mode
3. Enable "Always Use HTTPS"
4. Enable "Automatic HTTPS Rewrites"

## Configuration

### Backend Configuration

#### Rate Limiting

Adjust rate limit in `api/autopilot.py`:

```python
RATE_LIMIT = 100  # requests per minute
RATE_WINDOW = 60  # seconds
```

For production, consider using Redis:

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def check_rate_limit(client_ip: str) -> bool:
    key = f"rate_limit:{client_ip}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, RATE_WINDOW)
    return count <= RATE_LIMIT
```

#### Timeout Configuration

Adjust timeout in `api/autopilot.py`:

```python
# Wait for all tasks with timeout
suggestions, safety_status, corrections = await asyncio.wait_for(
    asyncio.gather(suggestions_task, safety_task, corrections_task),
    timeout=0.25  # 250ms timeout
)
```

#### Worker Configuration

For high traffic, increase workers:

```bash
# 4 workers (recommended for 4 CPU cores)
uvicorn api.main:app --workers 4

# Auto-scale based on CPU cores
uvicorn api.main:app --workers $(nproc)
```

### Frontend Configuration

#### Debounce Delay

Adjust in `frontend/lib/autopilotClient.ts`:

```typescript
const DEFAULT_CONFIG = {
  debounceDelay: 300, // Increase for slower networks
};
```

Or via environment variable:

```bash
NEXT_PUBLIC_AUTOPILOT_DEBOUNCE=500
```

#### Cache Size

Adjust in `frontend/lib/autopilotClient.ts`:

```typescript
const DEFAULT_CONFIG = {
  cacheSize: 100, // Increase for better performance
};
```

#### Request Timeout

Adjust in `frontend/lib/autopilotClient.ts`:

```typescript
const DEFAULT_CONFIG = {
  requestTimeout: 5000, // 5 seconds
};
```

## Monitoring and Alerting

### Metrics to Monitor

#### Backend Metrics

1. **Response Time**:
   - P50, P95, P99 latency
   - Target: P95 < 250ms

2. **Error Rate**:
   - 4xx errors (client errors)
   - 5xx errors (server errors)
   - Target: < 1% error rate

3. **Rate Limit Hits**:
   - Number of 429 responses
   - Target: < 5% of requests

4. **Resource Usage**:
   - CPU usage
   - Memory usage
   - Target: < 80% utilization

#### Frontend Metrics

1. **Cache Hit Rate**:
   - Percentage of cached responses
   - Target: > 50% hit rate

2. **API Call Frequency**:
   - Requests per minute
   - Target: < 100 per user

3. **User Experience**:
   - Time to first suggestion
   - Suggestion acceptance rate

### Monitoring Setup

#### Using Prometheus

Add metrics endpoint in `api/main.py`:

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('autopilot_requests_total', 'Total requests')
request_duration = Histogram('autopilot_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Using Grafana

Create dashboard with panels for:
- Request rate (requests/sec)
- Response time (P50, P95, P99)
- Error rate (%)
- Cache hit rate (%)

#### Using CloudWatch (AWS)

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def log_metric(name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='Aethel/Autopilot',
        MetricData=[{
            'MetricName': name,
            'Value': value,
            'Unit': unit
        }]
    )
```

### Alerting Rules

#### Critical Alerts

1. **High Error Rate**:
   - Condition: Error rate > 5% for 5 minutes
   - Action: Page on-call engineer

2. **High Latency**:
   - Condition: P95 latency > 500ms for 5 minutes
   - Action: Page on-call engineer

3. **Service Down**:
   - Condition: Health check fails for 2 minutes
   - Action: Page on-call engineer

#### Warning Alerts

1. **Elevated Error Rate**:
   - Condition: Error rate > 2% for 10 minutes
   - Action: Notify team channel

2. **Elevated Latency**:
   - Condition: P95 latency > 300ms for 10 minutes
   - Action: Notify team channel

3. **High Rate Limit Hits**:
   - Condition: Rate limit hits > 10% for 10 minutes
   - Action: Notify team channel

### Log Aggregation

#### Using ELK Stack

```python
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
```

#### Using Datadog

```python
from ddtrace import tracer

@tracer.wrap()
async def get_suggestions(request_data: SuggestionsRequest):
    # Function is automatically traced
    pass
```

## Performance Tuning

### Backend Optimization

#### 1. Enable Caching

Add caching to Autopilot Engine:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_code(code: str):
    # Analysis logic
    pass
```

#### 2. Use Connection Pooling

For database connections:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### 3. Enable Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 4. Optimize Judge Calls

Cache Judge results:

```python
from cachetools import TTLCache

judge_cache = TTLCache(maxsize=1000, ttl=300)

def get_safety_status(code: str):
    if code in judge_cache:
        return judge_cache[code]
    
    result = judge.verify(code)
    judge_cache[code] = result
    return result
```

### Frontend Optimization

#### 1. Code Splitting

Split Monaco Editor into separate chunk:

```typescript
import dynamic from 'next/dynamic';

const MonacoAutopilot = dynamic(
  () => import('@/components/MonacoAutopilot'),
  { ssr: false }
);
```

#### 2. Lazy Loading

Load Monaco only when needed:

```typescript
const [showEditor, setShowEditor] = useState(false);

return (
  <div>
    <button onClick={() => setShowEditor(true)}>
      Open Editor
    </button>
    {showEditor && <MonacoAutopilot />}
  </div>
);
```

#### 3. Service Worker

Cache Monaco assets:

```javascript
// public/sw.js
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open('monaco-v1').then((cache) => {
      return cache.addAll([
        '/monaco-editor/min/vs/loader.js',
        '/monaco-editor/min/vs/editor/editor.main.js',
      ]);
    })
  );
});
```

#### 4. CDN for Monaco

Use CDN instead of bundling:

```typescript
import { loader } from '@monaco-editor/react';

loader.config({
  paths: {
    vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs'
  }
});
```

### Database Optimization

If using database for caching:

```sql
-- Create index on cache key
CREATE INDEX idx_cache_key ON autopilot_cache(cache_key);

-- Create index on timestamp for cleanup
CREATE INDEX idx_cache_timestamp ON autopilot_cache(created_at);

-- Cleanup old entries
DELETE FROM autopilot_cache WHERE created_at < NOW() - INTERVAL '1 hour';
```

## Rollback Procedures

### Backend Rollback

#### 1. Identify Issue

Check logs and metrics:

```bash
# Check error logs
tail -f /var/log/diotec360/backend.log | grep ERROR

# Check metrics
curl http://localhost:8000/api/autopilot/stats
```

#### 2. Rollback Code

```bash
# Revert to previous version
git revert HEAD
git push

# Or checkout previous tag
git checkout v3.6.0
```

#### 3. Restart Service

```bash
# Using systemd
sudo systemctl restart aethel-backend

# Using Docker
docker stop aethel-backend
docker run -p 8000:8000 aethel-backend:v3.6.0
```

#### 4. Verify Rollback

```bash
curl http://localhost:8000/api/autopilot/health
```

### Frontend Rollback

#### 1. Rollback Deployment

**Vercel**:
```bash
vercel rollback
```

**Docker**:
```bash
docker stop aethel-frontend
docker run -p 3000:3000 aethel-frontend:v3.6.0
```

#### 2. Clear CDN Cache

```bash
# Cloudflare
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

#### 3. Verify Rollback

Open browser and verify old version is running.

### Database Rollback

If database schema changed:

```bash
# Run down migration
alembic downgrade -1

# Or restore from backup
pg_restore -d aethel backup.sql
```

## Troubleshooting

### Common Issues

#### 1. High Latency

**Symptoms**: P95 latency > 500ms

**Diagnosis**:
```bash
# Check backend logs
tail -f /var/log/diotec360/backend.log | grep "analysis_time"

# Check system resources
top
htop
```

**Solutions**:
- Increase worker count
- Enable caching
- Optimize Judge calls
- Add more CPU/RAM

#### 2. High Error Rate

**Symptoms**: Error rate > 5%

**Diagnosis**:
```bash
# Check error logs
tail -f /var/log/diotec360/backend.log | grep ERROR

# Check API stats
curl http://localhost:8000/api/autopilot/stats
```

**Solutions**:
- Check Judge service status
- Check database connections
- Check network connectivity
- Review recent code changes

#### 3. Rate Limit Issues

**Symptoms**: Many 429 responses

**Diagnosis**:
```bash
# Check rate limit stats
curl http://localhost:8000/api/autopilot/stats

# Check client IPs
tail -f /var/log/diotec360/backend.log | grep "Rate limit"
```

**Solutions**:
- Increase rate limit
- Implement per-user rate limiting
- Add Redis for distributed rate limiting
- Block abusive IPs

#### 4. Memory Leaks

**Symptoms**: Memory usage grows over time

**Diagnosis**:
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep uvicorn'

# Check Python memory
python -m memory_profiler api/main.py
```

**Solutions**:
- Clear cache periodically
- Restart workers periodically
- Fix memory leaks in code
- Increase memory limit

#### 5. Frontend Not Loading

**Symptoms**: Monaco Editor doesn't appear

**Diagnosis**:
```javascript
// Check browser console
console.log('Monaco loaded:', window.monaco);

// Check network tab
// Look for failed requests to Monaco CDN
```

**Solutions**:
- Check CDN availability
- Check CORS configuration
- Clear browser cache
- Use local Monaco bundle

### Debug Mode

Enable debug logging:

**Backend**:
```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```typescript
// In autopilotClient.ts
const DEBUG = true;

if (DEBUG) {
  console.log('Request:', state);
  console.log('Response:', response);
}
```

### Health Checks

#### Backend Health Check

```bash
curl http://localhost:8000/api/autopilot/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "autopilot",
  "timestamp": "2026-02-21T10:30:00.000Z"
}
```

#### Frontend Health Check

```bash
curl http://localhost:3000/api/health
```

#### End-to-End Health Check

```bash
# Test complete flow
curl -X POST http://localhost:8000/api/autopilot/suggestions \
  -H "Content-Type: application/json" \
  -d '{"code":"intent payment {","cursor_position":17}'
```

## Support

For deployment issues:

- GitHub Issues: [diotec360-lang/aethel](https://github.com/diotec360-lang/diotec360/issues)
- Documentation: [docs.diotec360-lang.org](https://docs.diotec360-lang.org)
- Email: support@diotec360-lang.org
- Slack: [aethel-community.slack.com](https://aethel-community.slack.com)

## Changelog

### Version 3.7.0 (2026-02-20)

- Initial deployment of Aethel-Pilot v3.7
- Monaco Editor integration
- Real-time autocomplete
- Traffic light safety feedback
- Correction suggestions
- Performance optimizations
