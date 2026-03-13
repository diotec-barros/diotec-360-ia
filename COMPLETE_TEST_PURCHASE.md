# 🧪 Complete Test Purchase - Final Validation

## 🎯 Objective
Complete the PayPal Sandbox purchase to validate the full payment flow and credit minting.

---

## 📋 Step-by-Step Instructions

### Step 1: Open the Approval URL
The test generated this approval URL:
```
https://www.sandbox.paypal.com/checkoutnow?token=2T177648TS519851E
```

**Action**: Click the link or paste it in your browser

---

### Step 2: Login to PayPal Sandbox

**IMPORTANT**: Use your PayPal Sandbox PERSONAL account (not business account)

**Where to find credentials**:
1. Go to: https://developer.paypal.com/dashboard/
2. Click "Sandbox" → "Accounts"
3. Find the PERSONAL account (usually ends with @personal.example.com)
4. Click "..." → "View/Edit Account"
5. Copy the email and password

**Example**:
- Email: `sb-xxxxx@personal.example.com`
- Password: (shown in the account details)

---

### Step 3: Complete the Payment

1. Review the order details:
   - **Merchant**: DIOTEC 360 IA
   - **Amount**: $9.99 USD
   - **Description**: Starter Package (1,000 credits)

2. Click **"Pay Now"** or **"Complete Purchase"**

3. Wait for confirmation page

---

### Step 4: Monitor the Webhook

**Open Hugging Face Logs**:
```
https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge
```

**Look for these log messages**:
```
[TREASURY] Webhook Received: PAYMENT.SALE.COMPLETED
[TREASURY] Processing payment for order: 2T177648TS519851E
[TREASURY] Minting 1,000 credits for user: test_pubkey_test_user_dionisio_001
[TREASURY] Credits added successfully
[TREASURY] New balance: 1,000 credits
```

---

### Step 5: Verify Credit Balance

**Run the balance check**:
```bash
python scripts/test_treasury_endpoints.py
```

**Expected Result**:
```json
{
  "ok": true,
  "credits": 1000,
  "public_key": "test_pubkey_test_user_dionisio_001"
}
```

**Before**: 0 credits  
**After**: 1,000 credits ✅

---

## 🔍 What to Watch For

### Success Indicators:
- ✅ PayPal shows "Payment Complete"
- ✅ Webhook log appears in Hugging Face
- ✅ Balance endpoint shows 1,000 credits
- ✅ Merkle root changes (new transaction recorded)

### If Webhook Doesn't Fire:
This is normal in Sandbox - webhooks can be delayed or require manual trigger.

**Manual Verification**:
1. Check PayPal Sandbox transactions
2. Verify order status is "COMPLETED"
3. Manually trigger webhook (if needed)

---

## 🎉 Success Criteria

| Check | Status |
|-------|--------|
| Order created | ✅ Done |
| Approval URL generated | ✅ Done |
| Payment completed | ⏳ Next |
| Webhook received | ⏳ Next |
| Credits minted | ⏳ Next |
| Balance updated | ⏳ Next |

---

## 🚀 After Success

Once all checks pass, you will have validated:
1. ✅ End-to-end payment flow
2. ✅ PayPal integration
3. ✅ Webhook processing
4. ✅ Credit minting
5. ✅ Balance management

**Result**: System is 100% ready for production deployment!

---

## 📞 Troubleshooting

### Issue: Can't find Sandbox account
**Solution**: Create a new one at https://developer.paypal.com/dashboard/accounts

### Issue: Payment fails
**Solution**: Ensure Sandbox account has sufficient balance (default is $5,000)

### Issue: Webhook not received
**Solution**: 
1. Check webhook URL in PayPal settings
2. Verify webhook ID matches environment variable
3. Manually test webhook endpoint

---

## 💰 The Moment of Truth

This is where **mathematics becomes money** and **code becomes commerce**.

When you see those 1,000 credits appear in the balance, you'll know:
- Your system can receive real payments
- Your treasury can mint credits
- Your Merkle tree can seal transactions
- Your empire is ready for the world

**Go complete the purchase and report back!** 🌌✨💰🚀

---

*"The first credit is always the hardest. After that, it's just mathematics."*
