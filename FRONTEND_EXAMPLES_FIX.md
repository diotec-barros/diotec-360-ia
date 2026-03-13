# 🔧 FRONTEND EXAMPLES - BACKEND CONNECTION REQUIRED

## 🚨 THE ISSUE

The error you're seeing is because:
1. The **backend API is not running** (`http://localhost:8000`)
2. The frontend can't fetch the v1.9.0-compliant examples
3. You're either typing code manually or seeing cached old examples

## ✅ THE SOLUTION

### Start the Backend API Server:

```bash
# In a NEW terminal (keep frontend running in another)
cd C:\Users\DIOTEC\AETHEL
python -m uvicorn api.main:app --reload --port 8000
```

### Verify It's Working:

Open your browser and go to:
```
http://localhost:8000
```

You should see:
```json
{
  "name": "Aethel API",
  "version": "1.7.0",
  "status": "operational"
}
```

### Test the Examples Endpoint:

```
http://localhost:8000/api/examples
```

You should see 4 examples, all with the `solve` block.

---

## 📝 ALL EXAMPLES ARE ALREADY v1.9.0 COMPLIANT

The examples in `api/main.py` are **already fixed**:

### ✅ Example 1: Financial Transfer
```aethel
intent transfer(sender: Account, receiver: Account, amount: Balance) {
    guard { ... }
    solve {
        priority: security;
        target: secure_ledger;
    }
    verify { ... }
}
```

### ✅ Example 2: DeFi Liquidation (Oracle)
```aethel
intent check_liquidation(...) {
    guard { ... }
    solve {
        priority: security;
        target: defi_vault;
    }
    verify {
        collateral_value == (collateral_amount * btc_price);
        (debt > (collateral_value * 0.75)) ==> (liquidation_allowed == true);
    }
}
```

### ✅ Example 3: Weather Insurance (Oracle)
```aethel
intent process_crop_insurance(...) {
    guard { ... }
    solve {
        priority: security;
        target: oracle_sanctuary;
    }
    verify { ... }
}
```

### ✅ Example 4: Private Compliance (ZKP)
```aethel
intent verify_insurance_coverage(...) {
    guard { ... }
    solve {
        priority: privacy;
        target: ghost_protocol;
    }
    verify { ... }
}
```

---

## 🎯 QUICK FIX STEPS

1. **Open a NEW terminal** (don't close the frontend terminal)
2. **Run**: `python -m uvicorn api.main:app --reload --port 8000`
3. **Wait** for "Application startup complete"
4. **Refresh** your browser at `http://localhost:3000`
5. **Click** "Examples" dropdown
6. **Select** any example - they all have `solve` blocks now!

---

## 🔍 WHY THIS HAPPENED

- Frontend: `http://localhost:3000` (Next.js) ✅ Running
- Backend: `http://localhost:8000` (FastAPI) ❌ Not Running

The frontend **needs** the backend to:
- Fetch examples
- Verify code with Z3
- Run the Judge
- Access the Vault

---

## 💡 TIP: Run Both Servers

**Terminal 1 (Frontend)**:
```bash
cd frontend
npm run dev
```

**Terminal 2 (Backend)**:
```bash
cd C:\Users\DIOTEC\AETHEL
python -m uvicorn api.main:app --reload --port 8000
```

Now both will work together! 🚀

---

**STATUS**: Examples are v1.9.0 compliant. Just start the backend API server!

