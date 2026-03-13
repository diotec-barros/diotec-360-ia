# Hugging Face Space Deployment Guide

## 🚀 Quick Deploy to Hugging Face

Your Aethel Judge Space is ready to deploy! Follow these steps:

### 1. Clone Your Space Repository

```bash
git clone https://huggingface.co/spaces/diotec/diotec360-judge
cd diotec360-judge
```

### 2. Copy Files from Aethel Project

Copy these essential files to your Space directory:

```bash
# Core application files
cp -r aethel/ diotec360-judge/
cp -r api/ diotec360-judge/
cp requirements.txt diotec360-judge/
cp Dockerfile.huggingface diotec360-judge/Dockerfile
cp README_HF.md diotec360-judge/README.md
cp .dockerignore diotec360-judge/

# Create vault directories
mkdir -p diotec360-judge/.DIOTEC360_vault/bundles
mkdir -p diotec360-judge/.DIOTEC360_vault/certificates
```

### 3. Configure the Space

The `README.md` (from README_HF.md) contains the Space configuration in the frontmatter:

```yaml
---
title: Aethel Judge
emoji: ⚖️
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
app_port: 7860
---
```

### 4. Commit and Push

```bash
cd diotec360-judge
git add .
git commit -m "Initial deployment of Aethel Judge"
git push
```

### 5. Wait for Build

Hugging Face will automatically:
- Build your Docker image
- Start the container on port 7860
- Make your API available at: `https://huggingface.co/spaces/diotec/diotec360-judge`

## 🧪 Test Your Deployment

Once deployed, test the API:

```bash
# Health check
curl https://diotec-diotec360-judge.hf.space/health

# Get examples
curl https://diotec-diotec360-judge.hf.space/api/examples

# Verify code
curl -X POST https://diotec-diotec360-judge.hf.space/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "code": "intent transfer(sender: Account, receiver: Account, amount: Balance) { guard { sender_balance >= amount; amount > 0; } solve { priority: security; } verify { sender_balance == old_sender_balance - amount; receiver_balance == old_receiver_balance + amount; } }"
  }'
```

## 📊 Monitor Your Space

- **Build Logs**: Check the "Logs" tab in your Space
- **Status**: Green badge means it's running
- **Metrics**: View usage in the Space settings

## 🔧 Troubleshooting

### Build Fails

Check the logs for errors. Common issues:
- Missing dependencies in requirements.txt
- Port not set to 7860
- File permissions issues

### API Not Responding

- Verify the container is running (check logs)
- Ensure port 7860 is exposed in Dockerfile
- Check that uvicorn is binding to 0.0.0.0

### Import Errors

Make sure all Python modules are in the correct structure:
```
diotec360-judge/
├── aethel/
│   ├── core/
│   │   ├── parser.py
│   │   ├── judge.py
│   │   ├── vault.py
│   │   └── ...
│   └── __init__.py
├── api/
│   ├── main.py
│   └── requirements.txt
└── requirements.txt
```

## 🎯 Next Steps

1. **Update Frontend**: Point Aethel Studio to your HF Space URL
2. **Add Examples**: Upload more example .ae files
3. **Enable Analytics**: Track API usage
4. **Add Authentication**: Protect endpoints if needed

## 🔗 Useful Links

- [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- [Docker Spaces Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)
- [Aethel Documentation](https://github.com/diotec/aethel)

## 📝 Environment Variables (Optional)

If you need to add environment variables:

1. Go to your Space settings
2. Add secrets in the "Variables and secrets" section
3. Access them in your code via `os.environ`

Example:
```python
import os
API_KEY = os.environ.get("API_KEY", "default_value")
```

## 🚨 Important Notes

- **Port 7860**: Must be used for HF Spaces
- **User Permissions**: Container runs as user 1000
- **Build Time**: First build may take 5-10 minutes
- **Free Tier**: Limited to 2 CPU cores, 16GB RAM

## ✅ Deployment Checklist

- [ ] Space created on Hugging Face
- [ ] Repository cloned locally
- [ ] Files copied from Aethel project
- [ ] Dockerfile renamed (Dockerfile.huggingface → Dockerfile)
- [ ] README.md has correct frontmatter
- [ ] Vault directories created
- [ ] Changes committed and pushed
- [ ] Build completed successfully
- [ ] Health endpoint responding
- [ ] API endpoints tested
- [ ] Frontend updated with new URL

---

**Your Aethel Judge Space is now live! 🎉**

Share it with the community:
- Tweet about it
- Add to your GitHub README
- Submit to HF Spaces showcase
