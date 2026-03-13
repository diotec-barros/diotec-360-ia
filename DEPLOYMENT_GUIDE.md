# diotec360-studio Deployment Guide

Complete guide to deploy diotec360-studio to the web.

---

## 🎯 Overview

**diotec360-studio** consists of two parts:
1. **Backend API** (Python/FastAPI) → Railway or Render
2. **Frontend** (Next.js) → Vercel

---

## 📋 Prerequisites

- GitHub account
- Railway account (https://railway.app) OR Render account (https://render.com)
- Vercel account (https://vercel.com)
- Git installed locally

---

## 🚀 Part 1: Deploy Backend API

### Option A: Railway (Recommended)

**Why Railway?**
- Easiest deployment
- Automatic HTTPS
- $5/month starter plan
- Great for Python apps

**Steps**:

1. **Sign up for Railway**
   - Go to https://railway.app
   - Sign in with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `diotec360-lang` repository
   - Railway will auto-detect the Dockerfile

3. **Configure Environment**
   - No environment variables needed for MVP
   - (Optional) Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` for AI features

4. **Deploy**
   - Railway will automatically build and deploy
   - You'll get a URL like: `aethel-api.up.railway.app`

5. **Test API**
   ```bash
   curl https://aethel-api.up.railway.app/health
   ```

### Option B: Render

**Why Render?**
- Free tier available
- Good for open source
- Auto-deploy from GitHub

**Steps**:

1. **Sign up for Render**
   - Go to https://render.com
   - Sign in with GitHub

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `diotec360-lang`

3. **Configure Service**
   - **Name**: `aethel-api`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `api/Dockerfile`
   - **Plan**: Free (or Starter $7/month)

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy
   - You'll get a URL like: `aethel-api.onrender.com`

5. **Test API**
   ```bash
   curl https://aethel-api.onrender.com/health
   ```

---

## 🎨 Part 2: Deploy Frontend (Coming Soon)

The frontend (Next.js app) will be created in a future update.

For now, you can test the API directly:

### Test Verification Endpoint

```bash
curl -X POST https://your-api-url.com/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "intent transfer(sender: Account, receiver: Account, amount: Balance) { guard { sender_balance >= amount; } verify { sender_balance < old_sender_balance; } }"
  }'
```

### Test Examples Endpoint

```bash
curl https://your-api-url.com/api/examples
```

---

## 🔧 Local Development

### Run Backend Locally

```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Run server
uvicorn main:app --reload

# API will be available at http://localhost:8000
```

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get examples
curl http://localhost:8000/api/examples

# Verify code
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "intent test() { guard { true; } verify { true; } }"}'
```

---

## 📊 Monitoring

### Railway

- Dashboard: https://railway.app/dashboard
- View logs in real-time
- Monitor CPU/Memory usage
- Set up alerts

### Render

- Dashboard: https://dashboard.render.com
- View deployment logs
- Monitor metrics
- Set up health checks

---

## 🔐 Security

### API Rate Limiting

Add to `api/main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/verify")
@limiter.limit("10/minute")
async def verify_code(request: Request, verify_request: VerifyRequest):
    # ... existing code
```

### CORS Configuration

Update `api/main.py` for production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://diotec360-lang.vercel.app"],  # Your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 🐛 Troubleshooting

### Backend won't start

**Check logs**:
- Railway: Click on deployment → "View Logs"
- Render: Go to service → "Logs" tab

**Common issues**:
1. Missing dependencies → Check `requirements.txt`
2. Port binding → Ensure using `$PORT` environment variable
3. Import errors → Check Python path in `main.py`

### API returns 500 errors

**Check**:
1. Z3 solver installed correctly
2. Aethel modules importable
3. File permissions for vault directory

### Slow response times

**Solutions**:
1. Upgrade to paid tier (more CPU/RAM)
2. Add caching for verification results
3. Optimize Z3 solver timeout
4. Use connection pooling

---

## 💰 Cost Breakdown

### Free Tier (MVP)
- **Railway**: $0 (trial credits)
- **Render**: $0 (free tier)
- **Vercel**: $0 (open source)
- **Total**: $0/month

### Production
- **Railway**: $5-20/month
- **Render**: $7-25/month
- **Vercel**: $0 (open source)
- **Domain**: $12/year
- **Total**: ~$10-30/month

---

## 📈 Scaling

### When to scale?

- **100+ requests/day**: Stay on free tier
- **1,000+ requests/day**: Upgrade to Starter ($5-7/month)
- **10,000+ requests/day**: Upgrade to Pro ($20-25/month)
- **100,000+ requests/day**: Consider dedicated infrastructure

### Scaling strategies

1. **Horizontal**: Add more instances (Railway/Render auto-scale)
2. **Caching**: Cache verification results (Redis)
3. **CDN**: Use Vercel's CDN for static assets
4. **Database**: Add PostgreSQL for vault persistence

---

## 🎯 Next Steps

1. ✅ Deploy backend API to Railway/Render
2. ⏳ Create Next.js frontend (coming soon)
3. ⏳ Deploy frontend to Vercel
4. ⏳ Connect frontend to backend
5. ⏳ Add custom domain
6. ⏳ Set up monitoring
7. ⏳ Launch publicly

---

## 📞 Support

- **GitHub Issues**: https://github.com/diotec-barros/diotec360-lang/issues
- **Discussions**: https://github.com/diotec-barros/diotec360-lang/discussions
- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs

---

**Ready to deploy? Start with Part 1 (Backend API) now!**

The diotec360-studio will make formal verification accessible to everyone with just a web browser.
