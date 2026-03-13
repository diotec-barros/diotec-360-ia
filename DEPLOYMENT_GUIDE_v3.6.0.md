# Deployment Guide v3.6.0 🚀

**DIOTEC 360 IA - Production Deployment**

---

## Prerequisites

### 1. PayPal Business Account
1. Create account at https://www.paypal.com/businessmanage/account/aboutBusiness
2. Verify business information
3. Add bank account (Angola supported)

### 2. PayPal Developer Setup
1. Go to https://developer.paypal.com/dashboard/
2. Create REST API app
3. Get Client ID and Secret
4. Configure webhook endpoint
5. Subscribe to `PAYMENT.CAPTURE.COMPLETED` event
6. Get Webhook ID

### 3. Server Requirements
- Python 3.8+
- Node.js 16+
- FastAPI
- Uvicorn
- PostgreSQL (optional, SQLite works)

---

## Environment Configuration

Create `.env` file in `diotec360/` directory:

```bash
# PayPal Configuration
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_SECRET=your_secret_here
PAYPAL_WEBHOOK_ID=your_webhook_id_here
PAYPAL_MODE=sandbox  # Change to 'live' for production

# Server Configuration
DIOTEC360_SERVER_URL=https://your-domain.com
DIOTEC360_CORS_ORIGINS=*

# Node Configuration (for signing)
DIOTEC360_NODE_PRIVKEY_HEX=your_private_key_hex

# Database (optional)
DATABASE_URL=sqlite:///./diotec360.db
```

---

## Deployment Steps

### Step 1: Install Dependencies

```bash
# Backend
cd diotec360
pip install -r api/requirements.txt

# Frontend
cd ../Ango-IA
npm install
```

### Step 2: Run Tests

```bash
# Backend tests
cd diotec360
python -m pytest test_treasury_api.py -v
python -m pytest test_treasury.py -v
python -m pytest test_paypal_connector.py -v

# All tests should pass (27/27)
```

### Step 3: Build Frontend

```bash
cd Ango-IA
npm run compile
```

### Step 4: Start Backend (Sandbox Mode)

```bash
cd diotec360/api
python run.py
```

Server starts at `http://localhost:8000`

### Step 5: Test Purchase Flow

1. Open VS Code with extension installed
2. Run command: `DIOTEC 360: Configure Sovereign Identity`
3. Run command: `ANGO IA: Buy Credits`
4. Select package
5. Complete payment in PayPal sandbox
6. Verify credits appear

### Step 6: Switch to Production

1. Update `.env`:
   ```bash
   PAYPAL_MODE=live
   ```

2. Update PayPal webhook URL to production domain

3. Restart server

4. Test with small real payment

---

## Hugging Face Deployment

### Option 1: Hugging Face Spaces

1. Create new Space at https://huggingface.co/spaces
2. Select "Docker" template
3. Upload files:
   ```
   diotec360/
   ├── api/
   ├── diotec360/
   ├── Dockerfile
   └── requirements.txt
   ```

4. Configure secrets in Space settings:
   - `PAYPAL_CLIENT_ID`
   - `PAYPAL_SECRET`
   - `PAYPAL_WEBHOOK_ID`
   - `PAYPAL_MODE`

5. Deploy

### Option 2: Hugging Face Inference Endpoints

1. Create Dockerfile:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY diotec360/api/requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY diotec360 /app/diotec360
   COPY diotec360/api /app/api
   
   EXPOSE 8000
   
   CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. Build and push:
   ```bash
   docker build -t diotec360-api .
   docker tag diotec360-api huggingface/diotec360-api
   docker push huggingface/diotec360-api
   ```

3. Create endpoint at https://huggingface.co/inference-endpoints

---

## VS Code Extension Publishing

### Step 1: Prepare Package

```bash
cd Ango-IA
npm install -g vsce
vsce package
```

This creates `diotec-360-ia-extension-0.0.1.vsix`

### Step 2: Test Locally

```bash
code --install-extension diotec-360-ia-extension-0.0.1.vsix
```

### Step 3: Publish to Marketplace

1. Create publisher account at https://marketplace.visualstudio.com/
2. Get Personal Access Token
3. Login:
   ```bash
   vsce login your-publisher-name
   ```
4. Publish:
   ```bash
   vsce publish
   ```

---

## Monitoring

### Health Checks

```bash
# API health
curl https://your-domain.com/health

# Treasury health
curl https://your-domain.com/api/treasury/health
```

### Logs

```bash
# View logs
tail -f /var/log/diotec360/api.log

# Or with Docker
docker logs -f diotec360-api
```

### Metrics

Monitor:
- Request rate
- Error rate
- Response time
- PayPal webhook success rate
- Credit balance changes

---

## Troubleshooting

### PayPal Webhook Not Receiving Events

1. Check webhook URL is correct
2. Verify webhook is subscribed to `PAYMENT.CAPTURE.COMPLETED`
3. Check server logs for errors
4. Test webhook manually in PayPal dashboard

### Credits Not Minting

1. Check PayPal webhook logs
2. Verify signature verification is passing
3. Check treasury logs
4. Verify ProofOfPayment is valid

### Server Errors

1. Check environment variables are set
2. Verify database connection
3. Check PayPal credentials
4. Review error logs

---

## Security Checklist

- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] PayPal webhook signature verification enabled
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Database backups configured
- [ ] Error logging enabled
- [ ] Monitoring alerts configured

---

## Support

For deployment issues:
- Email: support@diotec360.com
- GitHub: https://github.com/diotec360/ango-ia/issues

---

**Good luck with your deployment!** 🚀
