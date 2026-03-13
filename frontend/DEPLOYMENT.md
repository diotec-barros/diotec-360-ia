# Aethel Studio - Deployment Guide

## 🚀 Quick Deploy to Vercel

### Prerequisites
- GitHub account
- Vercel account (free at https://vercel.com)
- Backend API deployed (Railway/Render)

### Steps

1. **Push to GitHub** (if not already done)
   ```bash
   git add frontend/
   git commit -m "feat: Add Aethel Studio frontend"
   git push origin main
   ```

2. **Deploy to Vercel**
   - Go to https://vercel.com
   - Click "New Project"
   - Import your `diotec360-lang` repository
   - Configure:
     - **Root Directory**: `frontend`
     - **Framework Preset**: Next.js
     - **Build Command**: `npm run build`
     - **Output Directory**: `.next`

3. **Add Environment Variable**
   - In Vercel project settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = `https://your-api.up.railway.app`

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your site will be live at `https://your-project.vercel.app`

## 🔧 Local Development

```bash
# Install dependencies
cd frontend
npm install

# Set up environment
cp .env.local.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL

# Run dev server
npm run dev
```

Open http://localhost:3000

## 🌐 Custom Domain

1. Go to Vercel project → Settings → Domains
2. Add your custom domain (e.g., `studio.diotec360-lang.org`)
3. Follow DNS configuration instructions
4. Wait for DNS propagation (5-30 minutes)

## 📊 Monitoring

Vercel provides:
- Real-time logs
- Performance analytics
- Error tracking
- Deployment history

Access via: https://vercel.com/dashboard

## 🐛 Troubleshooting

### Build fails
- Check that all dependencies are in `package.json`
- Verify TypeScript has no errors: `npm run build`

### API calls fail
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS is enabled on backend
- Test API directly: `curl https://your-api-url.com/health`

### Monaco Editor not loading
- Ensure dynamic import is used in `page.tsx`
- Check browser console for errors

## 💰 Cost

- **Vercel Free Tier**: Perfect for open source projects
  - Unlimited deployments
  - 100GB bandwidth/month
  - Automatic HTTPS
  - Global CDN

## 🎯 Next Steps

After deployment:
1. Test all features
2. Share the URL on social media
3. Add to README.md
4. Monitor usage and errors
5. Gather user feedback

---

**Your Aethel Studio will be live at**: `https://your-project.vercel.app`

The future is not written in code. It is proved in theorems.
