# 🧪 APEX DASHBOARD v2.0 - MANUAL TESTING GUIDE

**Purpose**: Step-by-step instructions to test all 7 components  
**Time Required**: 15 minutes  
**Prerequisites**: Frontend dev server running (`npm run dev`)

---

## 🚀 SETUP

1. Open terminal in `frontend` folder
2. Run: `npm run dev`
3. Open browser: `http://localhost:3000`
4. Open browser DevTools (F12) to check for errors

---

## TEST 1: Layer Sidebar Navigation (2 min)

### Steps:
1. Look at the left sidebar
2. Click each layer icon:
   - 🏛️ Judge (Blue)
   - 🧠 Architect (Green)
   - 🛡️ Sentinel (Red)
   - 🎭 Ghost (Purple)
   - 🔮 Oracle (Amber)

### Expected Results:
- ✅ Active layer badge changes color
- ✅ Header shows current layer name
- ✅ Footer text changes per layer
- ✅ Badge numbers update (if applicable)

### Screenshot Locations:
- Top header: Layer indicator
- Footer: Layer-specific status

---

## TEST 2: Architect Chat (CMD+K) (2 min)

### Steps:
1. Press `CMD+K` (Mac) or `CTRL+K` (Windows)
2. Modal should open
3. Type: "Create a simple transfer function"
4. Click "Generate Code"
5. Check if code appears in editor

### Expected Results:
- ✅ Modal opens on keyboard shortcut
- ✅ Chat interface is visible
- ✅ Code generation works (simulated)
- ✅ Editor updates with new code
- ✅ Modal closes after generation

### Alternative:
- Click "Architect" button in header (green button)

---

## TEST 3: Ghost Visualizer (3 min)

### Steps:
1. Click Ghost layer (purple icon) in sidebar
2. Paste this code in editor:

```aethel
intent verify_insurance(
    patient: Person,
    secret patient_balance: Balance,
    secret ssn: String
) {
    guard {
        patient_balance > 0;
    }
    
    solve {
        priority: privacy;
        target: ghost_protocol;
    }
    
    verify {
        patient_balance >= copay;
    }
}
```

3. Observe the editor

### Expected Results:
- ✅ Purple overlay appears on editor
- ✅ "Protected Variables" panel shows on right side
- ✅ Lists: `patient_balance` (Line 3), `ssn` (Line 4)
- ✅ Floating lock icons animate
- ✅ Purple particles drift upward
- ✅ Footer shows "Ghost Protocol: Enabled"
- ✅ Badge shows "2" (two secret variables)

### Visual Checklist:
- [ ] Glassmorphism effect (blurred background)
- [ ] Floating locks move up and down
- [ ] Particles animate from bottom to top
- [ ] "Verified without revealing" badge at bottom

---

## TEST 4: Sentinel Radar (3 min)

### Steps:
1. Click Sentinel layer (red icon) in sidebar
2. Use any valid code (or default transfer code)
3. Click "Verify" button
4. Watch the Proof Viewer panel (right side)

### Expected Results:
- ✅ Radar component appears below proof result
- ✅ 3 sine waves animate (blue, green, red)
- ✅ Radar sweep line rotates
- ✅ Status changes: idle → scanning → verified
- ✅ Threat meter shows percentage (0-100%)
- ✅ Metrics update: Scans, Blocked, Uptime

### Visual Checklist:
- [ ] Canvas element renders
- [ ] Waves move smoothly (60 FPS)
- [ ] Sweep line rotates continuously
- [ ] Colors change based on status:
  - Green = idle
  - Blue = scanning
  - Green = verified
  - Red = threat

---

## TEST 5: Oracle Atlas (3 min)

### Steps:
1. Click Oracle layer (amber icon) in sidebar
2. Paste this code in editor:

```aethel
intent check_liquidation(
    borrower: Account,
    external btc_price: Price,
    external eth_price: Price
) {
    guard {
        btc_price_verified == true;
        eth_price_verified == true;
    }
    
    solve {
        priority: security;
        target: oracle_sanctuary;
    }
    
    verify {
        collateral_value == (btc_amount * btc_price) + (eth_amount * eth_price);
    }
}
```

3. Observe the Proof Viewer panel

### Expected Results:
- ✅ World map appears (SVG)
- ✅ Oracle markers glow (NYC, Geneva, Singapore)
- ✅ Pulse lines animate from sources to center
- ✅ Status shows "2 Active Sources" (or more)
- ✅ Badge shows number of active oracles

### Visual Checklist:
- [ ] World map is visible
- [ ] Markers pulse (scale animation)
- [ ] Lines draw from markers to center
- [ ] Amber color scheme
- [ ] Glassmorphism on info panel

---

## TEST 6: Sovereign Identity (2 min)

### Steps:
1. Look at the editor header (top right)
2. Type any code in the editor
3. Observe the identicon (5x5 grid pattern)
4. Change the code slightly
5. Observe the identicon change
6. Restore original code
7. Verify identicon returns to original

### Expected Results:
- ✅ 5x5 grid pattern appears
- ✅ Pattern is unique per code
- ✅ Color is deterministic
- ✅ Hash shows first 8 characters
- ✅ Verification badge displays
- ✅ Same code = same pattern

### Visual Checklist:
- [ ] Grid cells are colored or empty
- [ ] Pattern is symmetrical (mirrored)
- [ ] Hash updates when code changes
- [ ] Tooltip shows "Sovereign Identity"

---

## TEST 7: Execution Log (2 min)

### Steps:
1. Use any layer and code
2. Click "Verify" button
3. Wait for verification to complete
4. Look at bottom of screen
5. Click "Execution Log" tab to expand
6. Observe log entries

### Expected Results:
- ✅ Drawer slides up from bottom
- ✅ Log entries appear with delays
- ✅ Timestamps are relative (0ms, 100ms, 300ms...)
- ✅ Layer badges are color-coded
- ✅ Level icons match (info, success, warning, error)
- ✅ "Export Certificate (PDF)" button exists
- ✅ Search and filter work

### Visual Checklist:
- [ ] Drawer height: 12px (collapsed) → 320px (expanded)
- [ ] Smooth transition (300ms)
- [ ] Entries appear in real-time
- [ ] Scroll works if many entries
- [ ] Export button is prominent

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: Components Not Rendering
**Symptom**: Blank screen or missing components  
**Fix**: 
```bash
cd frontend
rm -rf .next
npm run dev
```

### Issue 2: TypeScript Errors
**Symptom**: Red underlines in VSCode  
**Fix**:
```bash
cd frontend
npm run build
# Check for errors
```

### Issue 3: Animations Not Working
**Symptom**: Static elements, no movement  
**Fix**: Check `globals.css` has all `@keyframes` definitions

### Issue 4: CMD+K Not Working
**Symptom**: Keyboard shortcut doesn't open chat  
**Fix**: Check browser console for JavaScript errors

### Issue 5: Canvas Not Rendering (Sentinel)
**Symptom**: Blank space where radar should be  
**Fix**: Check browser supports Canvas API (all modern browsers do)

---

## 📊 TEST RESULTS TEMPLATE

Copy this and fill it out:

```
## TEST RESULTS - [Your Name] - [Date]

### Environment
- Browser: [Chrome/Firefox/Safari]
- OS: [Windows/Mac/Linux]
- Screen Resolution: [1920x1080]

### Test 1: Layer Sidebar
- Status: [PASS/FAIL]
- Notes: 

### Test 2: Architect Chat
- Status: [PASS/FAIL]
- Notes: 

### Test 3: Ghost Visualizer
- Status: [PASS/FAIL]
- Notes: 

### Test 4: Sentinel Radar
- Status: [PASS/FAIL]
- Notes: 

### Test 5: Oracle Atlas
- Status: [PASS/FAIL]
- Notes: 

### Test 6: Sovereign Identity
- Status: [PASS/FAIL]
- Notes: 

### Test 7: Execution Log
- Status: [PASS/FAIL]
- Notes: 

### Overall Assessment
- Critical Issues: [Number]
- Minor Issues: [Number]
- Recommendation: [SHIP IT / NEEDS WORK]
```

---

## 🎯 SUCCESS CRITERIA

**SHIP IT** if:
- ✅ All 7 tests pass
- ✅ No critical errors in console
- ✅ Animations are smooth (60 FPS)
- ✅ UI is responsive
- ✅ No visual glitches

**NEEDS WORK** if:
- ❌ Any test fails completely
- ❌ Critical errors in console
- ❌ Animations are choppy
- ❌ UI breaks on resize
- ❌ Visual glitches present

---

## 📸 SCREENSHOT CHECKLIST

Take screenshots of:
1. ✅ All 5 layers active (one screenshot each)
2. ✅ Ghost Visualizer with secret variables
3. ✅ Sentinel Radar during verification
4. ✅ Oracle Atlas with active sources
5. ✅ Sovereign Identity identicon
6. ✅ Execution Log expanded
7. ✅ Architect Chat modal open

Save to: `frontend/screenshots/` folder

---

## 🚀 AFTER TESTING

If all tests pass:
1. Create `TEST_RESULTS.md` with your findings
2. Take screenshots
3. Create demo video (optional)
4. Prepare for production deployment

If tests fail:
1. Document issues in `BUGS.md`
2. Prioritize critical vs. minor
3. Fix critical issues first
4. Re-test

---

**READY TO TEST?** Start with Test 1 and work your way down. Good luck! 🎯

