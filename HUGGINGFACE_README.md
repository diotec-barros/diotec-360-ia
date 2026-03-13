# Hugging Face Deployment Files

This directory contains everything needed to deploy Aethel Judge to Hugging Face Spaces.

## 🚀 Quick Deploy

```bash
deploy_to_huggingface.bat
```

That's it! The script handles everything automatically.

## 📁 File Overview

### Core Deployment Files

- **Dockerfile.huggingface** - Docker configuration for HF Spaces
  - Port 7860 (HF requirement)
  - Non-root user (security)
  - Optimized for fast builds

- **README_HF.md** - Space documentation
  - Metadata (emoji, colors, SDK)
  - API documentation
  - Usage examples
  - Links and resources

- **.dockerignore** - Build optimization
  - Excludes test files
  - Reduces image size
  - Faster builds

### Deployment Scripts

- **deploy_to_huggingface.bat** - Automated deployment
  - Clones Space repository
  - Copies all files
  - Commits and pushes
  - Interactive prompts

- **test_docker_local.bat** - Local testing
  - Builds Docker image
  - Runs container locally
  - Tests on port 7860
  - Validates before deploy

- **test_huggingface_deployment.py** - API test suite
  - Tests all endpoints
  - Validates responses
  - Comprehensive checks
  - Detailed reporting

### Documentation

- **HUGGINGFACE_SUMMARY.md** - Quick overview
- **HUGGINGFACE_QUICKSTART.md** - Fast start guide
- **HUGGINGFACE_DEPLOY_GUIDE.md** - Detailed instructions
- **HUGGINGFACE_DEPLOYMENT_COMPLETE.md** - Complete reference
- **DEPLOYMENT_CHECKLIST.txt** - Step-by-step checklist

## 🎯 Deployment Process

### 1. Prepare (Done!)
All files are ready. No additional setup needed.

### 2. Deploy
```bash
deploy_to_huggingface.bat
```

### 3. Monitor
- Go to: https://huggingface.co/spaces/diotec/diotec360-judge
- Check "Logs" tab
- Wait for "Running" badge

### 4. Test
```bash
python test_huggingface_deployment.py
```

## 🔗 URLs

After deployment:
- **Space**: https://huggingface.co/spaces/diotec/diotec360-judge
- **API**: https://diotec-diotec360-judge.hf.space
- **Docs**: https://diotec-diotec360-judge.hf.space/docs

## 📊 What Gets Deployed

- Aethel Judge API (FastAPI)
- Z3 Theorem Prover
- Ghost-Runner (prediction engine)
- Mirror Frame (instant preview)
- Conservation Checker
- Vault System
- Example Library

## 🧪 Testing

### Local Testing (Optional)
```bash
test_docker_local.bat
curl http://localhost:7860/health
```

### Production Testing
```bash
python test_huggingface_deployment.py
```

### Manual Testing
```bash
# Health check
curl https://diotec-diotec360-judge.hf.space/health

# Get examples
curl https://diotec-diotec360-judge.hf.space/api/examples

# Verify code
curl -X POST https://diotec-diotec360-judge.hf.space/api/verify \
  -H "Content-Type: application/json" \
  -d '{"code": "intent test() { guard { x > 0; } solve { priority: security; } verify { x > 0; } }"}'
```

## 🐛 Troubleshooting

### Build Fails
1. Check Logs tab in Space
2. Verify all files copied correctly
3. Test locally first: `test_docker_local.bat`

### API Not Responding
1. Wait 2-3 minutes after build
2. Check container is running (Logs tab)
3. Verify port 7860 in Dockerfile

### Import Errors
1. Ensure aethel/ directory structure intact
2. Check all __init__.py files present
3. Verify requirements.txt is complete

## 💡 Tips

- **First deployment takes longer** (~10 min)
- **Test locally first** to catch issues early
- **Monitor build logs** for errors
- **Use test suite** to validate deployment
- **Update frontend** with new API URL

## 📚 Documentation

Read these in order:
1. `HUGGINGFACE_SUMMARY.md` - Overview
2. `HUGGINGFACE_QUICKSTART.md` - Quick start
3. `HUGGINGFACE_DEPLOY_GUIDE.md` - Detailed guide
4. `DEPLOYMENT_CHECKLIST.txt` - Step-by-step

## 🎉 Success Criteria

- [ ] Space shows "Running" status
- [ ] Health endpoint returns 200
- [ ] All test suite tests pass (6/6)
- [ ] Frontend connects successfully
- [ ] No errors in logs

## 📞 Support

- **HF Docs**: https://huggingface.co/docs/hub/spaces
- **Aethel GitHub**: https://github.com/diotec/aethel
- **Issues**: https://github.com/diotec/diotec360/issues

---

**Ready to deploy? Run `deploy_to_huggingface.bat`** 🚀
