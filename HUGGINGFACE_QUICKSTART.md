# Hugging Face Deployment - Quick Start

## 🚀 Deploy in 3 Steps

### Step 1: Run Deployment Script
```bash
deploy_to_huggingface.bat
```

### Step 2: Wait for Build
- Go to: https://huggingface.co/spaces/diotec/diotec360-judge
- Check "Logs" tab for build progress
- Wait for green "Running" badge

### Step 3: Test Deployment
```bash
python test_huggingface_deployment.py
```

## 📋 Manual Deployment (Alternative)

```bash
# Clone your Space
git clone https://huggingface.co/spaces/diotec/diotec360-judge
cd diotec360-judge

# Copy files
xcopy /E /I /Y ..\aethel aethel
xcopy /E /I /Y ..\api api
copy ..\requirements.txt requirements.txt
copy ..\Dockerfile.huggingface Dockerfile
copy ..\README_HF.md README.md

# Create vault
mkdir .DIOTEC360_vault\bundles
mkdir .DIOTEC360_vault\certificates

# Deploy
git add .
git commit -m "Deploy Aethel Judge"
git push
```

## 🧪 Quick Test

```bash
# Health check
curl https://diotec-diotec360-judge.hf.space/health

# Verify code
curl -X POST https://diotec-diotec360-judge.hf.space/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "intent test() { guard { x > 0; } solve { priority: security; } verify { x > 0; } }"}'
```

## 🔗 Your Space URLs

- **Space**: https://huggingface.co/spaces/diotec/diotec360-judge
- **API**: https://diotec-diotec360-judge.hf.space
- **Docs**: https://diotec-diotec360-judge.hf.space/docs

## 📊 Key Files

| File | Purpose |
|------|---------|
| `Dockerfile.huggingface` | Docker configuration for HF |
| `README_HF.md` | Space README with metadata |
| `deploy_to_huggingface.bat` | Automated deployment script |
| `test_huggingface_deployment.py` | Test all endpoints |

## ⚙️ Configuration

The Space is configured via README.md frontmatter:

```yaml
---
title: Aethel Judge
emoji: ⚖️
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
---
```

## 🐛 Troubleshooting

### Build Fails
- Check Logs tab in Space
- Verify all files copied correctly
- Ensure requirements.txt is complete

### API Not Responding
- Verify port 7860 in Dockerfile
- Check container is running (Logs tab)
- Wait 2-3 minutes after build completes

### Import Errors
- Ensure aethel/ directory structure is intact
- Check __init__.py files exist
- Verify Python path in Dockerfile

## 📞 Support

- [HF Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Aethel GitHub](https://github.com/diotec/aethel)
- [Issues](https://github.com/diotec/diotec360/issues)

## ✅ Checklist

- [ ] Space created on HuggingFace
- [ ] Files deployed
- [ ] Build completed (green badge)
- [ ] Health endpoint works
- [ ] Verification endpoint works
- [ ] Frontend updated with new URL

---

**Ready to verify code formally! ⚖️**
