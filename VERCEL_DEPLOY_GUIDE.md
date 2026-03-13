# 🚀 VERCEL DEPLOYMENT GUIDE - AETHEL STUDIO

**Date:** 2026-02-12  
**Version:** Diotec360 v3.0.5  
**Frontend:** Next.js 14 + TypeScript

---

## 🎯 QUICK DEPLOY TO VERCEL

### Prerequisites
- ✅ GitHub account
- ✅ Vercel account (free at https://vercel.com)
- ✅ Backend Triangle deployed (Nodes 1, 2, 3)
- ✅ Git repository pushed to GitHub

---

## 📋 DEPLOYMENT STEPS

### Step 1: Prepare Repository (2 minutes)

```bash
# Make sure all changes are committed
git status

# Add all frontend files
git add frontend/

# Add deployment configuration
git add VERCEL_DEPLOY_GUIDE.md

# Commit
git commit -m "feat: Prepare Aethel Studio for Vercel deployment"

# Push to GitHub
git push origin main
```

### Step 2: Connect to Vercel (3 minutes)

1. Go to https://vercel.com
2. Click **"Add New Project"**
3. Click **"Import Git Repository"**
4. Select your `aethel` repository
5. Click **"Import"**

### Step 3: Configure Project (2 minutes)

In the Vercel project configuration screen:

**Framework Preset:**
- Select: `Next.js`

**Root Directory:**
- Click "Edit"
- Enter: `frontend`
- Click "Continue"

**Build Settings:**
- Build Command: `npm run build` (auto-detected)
- Output Directory: `.next` (auto-detected)
- Install Command: `npm install` (auto-detected)

### Step 4: Environment Variables (1 minute)

Click **"Environment Variables"** and add:

| Name | Value |
|------|-------|
| `NEXT_PUBLIC_API_URL` | `https://api.diotec360.com` |
| `NEXT_PUBLIC_LATTICE_NODES` | `https://diotec-aethel.hf.space,https://backup.diotec360.com` |

**Note:** These are already in `.env.production` but adding them here ensures they're used.

### Step 5: Deploy! (3 minutes)

1. Click **"Deploy"**
2. Wait for build to complete (2-3 minutes)
3. Vercel will show build logs in real-time
4. Once complete, you'll see: **"Congratulations! Your project has been deployed."**

### Step 6: Get Your URL

Your Aethel Studio will be live at:
```
https://your-project-name.vercel.app
```

Example:
```
https://diotec360-studio.vercel.app
```

---

## 🔗 PRODUCTION URLS

After deployment, your stack will be:

**Frontend (Vercel):**
- https://diotec360-studio.vercel.app

**Backend Triangle:**
- Node 1 (HF): https://diotec-aethel.hf.space
- Node 2 (Primary): https://api.diotec360.com
- Node 3 (Backup): https://backup.diotec360.com

---

## ✅ POST-DEPLOYMENT VERIFICATION

### Test 1: Frontend Loads
```bash
curl https://diotec360-studio.vercel.app
```
**Expected:** HTML page loads successfully

### Test 2: API Connection
Open browser console on your Vercel URL and check:
- Network tab shows successful API calls
- No CORS errors
- Examples load correctly

### Test 3: Code Verification
1. Go to https://diotec360-studio.vercel.app
2. Click "Examples" → Select an example
3. Click "Verify"
4. Should see proof result

### Test 4: Lattice Fallback
1. Open browser DevTools → Network tab
2. Verify code
3. Check which backend node responded
4. Should see requests to Triangle nodes

---

## 🎨 CUSTOM DOMAIN (Optional)

### Add Custom Domain

1. Go to Vercel Dashboard → Your Project
2. Click **"Settings"** → **"Domains"**
3. Click **"Add Domain"**
4. Enter your domain: `studio.diotec360.com`
5. Follow DNS configuration instructions

### DNS Configuration

Add these records to your DNS provider:

**For subdomain (studio.diotec360.com):**
```
Type: CNAME
Name: studio
Value: cname.vercel-dns.com
```

**For apex domain (diotec360.com):**
```
Type: A
Name: @
Value: 76.76.21.21
```

### SSL Certificate

Vercel automatically provisions SSL certificates via Let's Encrypt.
- Wait 5-10 minutes after DNS configuration
- Certificate will auto-renew

---

## 📊 MONITORING & ANALYTICS

### Vercel Dashboard

Access at: https://vercel.com/dashboard

**Available Metrics:**
- Deployment history
- Build logs
- Runtime logs
- Performance analytics
- Error tracking
- Bandwidth usage

### Real-Time Logs

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# View logs
vercel logs
```

---

## 🔧 CONTINUOUS DEPLOYMENT

Vercel automatically deploys on every push to `main`:

```bash
# Make changes
git add .
git commit -m "feat: Add new feature"
git push origin main

# Vercel automatically:
# 1. Detects push
# 2. Builds project
# 3. Deploys to production
# 4. Updates URL
```

### Preview Deployments

Every pull request gets a preview URL:
```
https://diotec360-studio-git-feature-branch.vercel.app
```

---

## 🚨 TROUBLESHOOTING

### Build Fails

**Check build logs in Vercel dashboard:**
```
Error: Module not found
```
**Solution:** Ensure all dependencies are in `package.json`

```
Error: TypeScript compilation failed
```
**Solution:** Run `npm run build` locally to fix TypeScript errors

### API Calls Fail

**CORS Error:**
- Ensure backend has CORS enabled
- Check `Access-Control-Allow-Origin` header

**Connection Refused:**
- Verify backend URLs are correct
- Test backend directly: `curl https://api.diotec360.com/health`

### Environment Variables Not Working

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Verify variables are set
3. Click **"Redeploy"** to apply changes

---

## 💰 VERCEL PRICING

### Free Tier (Hobby)
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Preview deployments
- ✅ Perfect for open source

### Pro Tier ($20/month)
- Everything in Free
- 1TB bandwidth/month
- Team collaboration
- Advanced analytics
- Password protection

**Recommendation:** Start with Free tier

---

## 🎯 OPTIMIZATION TIPS

### 1. Enable Edge Functions
```typescript
// app/api/route.ts
export const runtime = 'edge';
```

### 2. Image Optimization
```typescript
import Image from 'next/image';

<Image 
  src="/logo.png" 
  width={200} 
  height={50}
  alt="Aethel"
/>
```

### 3. Static Generation
```typescript
// app/page.tsx
export const revalidate = 3600; // Revalidate every hour
```

---

## 📱 MOBILE OPTIMIZATION

Vercel automatically optimizes for mobile:
- Responsive images
- Code splitting
- Lazy loading
- Service worker caching

Test on mobile:
```
https://diotec360-studio.vercel.app
```

---

## 🔐 SECURITY

Vercel provides:
- ✅ Automatic HTTPS
- ✅ DDoS protection
- ✅ Firewall
- ✅ Security headers (configured in `vercel.json`)

---

## 📈 PERFORMANCE

Expected metrics:
- **First Contentful Paint:** < 1s
- **Time to Interactive:** < 2s
- **Lighthouse Score:** 90+

Check performance:
```
https://pagespeed.web.dev/
```

---

## 🎉 SUCCESS CHECKLIST

After deployment, verify:

- [ ] Frontend loads at Vercel URL
- [ ] Examples load correctly
- [ ] Code verification works
- [ ] Lattice fallback works
- [ ] No console errors
- [ ] Mobile responsive
- [ ] HTTPS enabled
- [ ] Custom domain configured (optional)
- [ ] Analytics working
- [ ] Continuous deployment working

---

## 🚀 NEXT STEPS

1. **Share Your URL**
   - Tweet about it
   - Add to GitHub README
   - Share on LinkedIn

2. **Monitor Usage**
   - Check Vercel analytics
   - Monitor error rates
   - Track user engagement

3. **Gather Feedback**
   - Add feedback form
   - Monitor GitHub issues
   - Engage with users

4. **Iterate**
   - Add new features
   - Fix bugs
   - Optimize performance

---

## 📞 SUPPORT

### Vercel Support
- Documentation: https://vercel.com/docs
- Community: https://github.com/vercel/vercel/discussions
- Twitter: @vercel

### Aethel Support
- GitHub: https://github.com/diotec/aethel
- Email: support@diotec360.com

---

## 🔗 USEFUL LINKS

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Next.js Docs:** https://nextjs.org/docs
- **Aethel Docs:** https://docs.diotec360.com
- **GitHub Repo:** https://github.com/diotec/aethel

---

**🎨 AETHEL STUDIO - READY FOR THE WORLD 🎨**

**Deploy now and let the world experience the future of formal verification!**

