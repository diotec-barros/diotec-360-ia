# ⚡ QUICK START - APEX DASHBOARD TESTING

**Time Required**: 15 minutes  
**Goal**: Verify all 7 components work correctly

---

## 🚀 START HERE

```bash
cd frontend
npm run dev
```

Open: `http://localhost:3000`

---

## ✅ QUICK TEST CHECKLIST

### 1. Layer Sidebar (30 seconds)
- [ ] Click each layer icon (Judge, Architect, Sentinel, Ghost, Oracle)
- [ ] Verify colors change (Blue, Green, Red, Purple, Amber)
- [ ] Check badge numbers update

### 2. Architect Chat (30 seconds)
- [ ] Press `CMD+K` (or `CTRL+K`)
- [ ] Modal opens
- [ ] Type anything and click "Generate Code"
- [ ] Code appears in editor

### 3. Ghost Visualizer (2 minutes)
- [ ] Click Ghost layer (purple icon)
- [ ] Paste this code:
```aethel
intent test(secret balance: Balance) {
    guard { balance > 0; }
    solve { priority: privacy; }
    verify { balance > 0; }
}
```
- [ ] Purple overlay appears
- [ ] Floating locks animate
- [ ] "Protected Variables" panel shows

### 4. Sentinel Radar (2 minutes)
- [ ] Click Sentinel layer (red icon)
- [ ] Click "Verify" button
- [ ] Radar appears with 3 waves
- [ ] Status changes: idle → scanning → verified
- [ ] Threat meter shows percentage

### 5. Oracle Atlas (2 minutes)
- [ ] Click Oracle layer (amber icon)
- [ ] Paste this code:
```aethel
intent test(external price: Price) {
    guard { price > 0; }
    solve { priority: security; }
    verify { price > 0; }
}
```
- [ ] World map appears
- [ ] Oracle markers glow
- [ ] Pulse lines animate

### 6. Sovereign Identity (1 minute)
- [ ] Look at editor header (top right)
- [ ] See 5x5 grid pattern (identicon)
- [ ] Change code
- [ ] Identicon changes
- [ ] Restore code
- [ ] Identicon returns to original

### 7. Execution Log (1 minute)
- [ ] Click "Verify" button
- [ ] Look at bottom of screen
- [ ] Click "Execution Log" to expand
- [ ] Log entries appear with timestamps
- [ ] Layer badges are color-coded
- [ ] "Export Certificate (PDF)" button exists

---

## 🎯 PASS/FAIL CRITERIA

### ✅ PASS IF:
- All 7 tests work
- No errors in browser console (F12)
- Animations are smooth
- UI is responsive

### ❌ FAIL IF:
- Any component doesn't render
- Console shows errors
- Animations are choppy
- UI breaks

---

## 📸 TAKE SCREENSHOTS

1. Ghost layer with secret variables
2. Sentinel radar during verification
3. Oracle atlas with active sources
4. Sovereign identity identicon
5. Execution log expanded

Save to: `frontend/screenshots/`

---

## 🐛 IF SOMETHING BREAKS

1. Check browser console (F12)
2. Restart dev server
3. Clear cache: `rm -rf .next`
4. Document issue in `BUGS.md`

---

## 📚 FULL DOCUMENTATION

- **Detailed Guide**: `MANUAL_TEST_GUIDE.md`
- **Test Scenarios**: `APEX_DASHBOARD_INTEGRATION_TEST.md`
- **Status Report**: `APEX_DASHBOARD_STATUS_FINAL.md`

---

## ⏱️ ESTIMATED TIME

- Setup: 1 minute
- Testing: 10 minutes
- Screenshots: 2 minutes
- Documentation: 2 minutes
- **Total**: 15 minutes

---

**Ready? Start the dev server and begin testing!** 🚀

