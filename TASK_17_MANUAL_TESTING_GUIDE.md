# Task 17.2: Manual Testing Guide
## Aethel-Pilot v3.7 - Integration and End-to-End Testing

This guide provides step-by-step instructions for manual testing of the Aethel-Pilot v3.7 system in a real browser environment.

## Prerequisites

1. Backend API server running (`python api/main.py` or similar)
2. Frontend development server running (`npm run dev` in frontend directory)
3. Browser with developer tools (Chrome, Firefox, or Edge recommended)

## Test Scenarios

### Scenario 1: Basic Autocomplete Functionality

**Objective**: Verify that autocomplete suggestions appear as you type

**Steps**:
1. Open browser and navigate to the Explorer page with Monaco Editor
2. Start typing: `intent payment {`
3. Press Enter to go to next line
4. Start typing: `  sender`

**Expected Results**:
- Suggestions should appear after typing "sender"
- Suggestions should include parameter types (Account, Balance, etc.)
- Suggestions should be relevant to the context

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 2: Guard Block Suggestions

**Objective**: Verify context-aware suggestions in guard blocks

**Steps**:
1. Type the following code:
```aethel
intent payment {
  sender: Account,
  receiver: Account,
  amount: Balance
}

guard {
  
}
```
2. Place cursor inside the guard block (after the opening brace)
3. Start typing: `amount`

**Expected Results**:
- Suggestions should include guard-specific completions
- Should suggest: `amount > 0`, `amount <= MAX_AMOUNT`, etc.
- Suggestions should have descriptions explaining their purpose

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 3: Traffic Light - Safe Code

**Objective**: Verify traffic light shows green for safe code

**Steps**:
1. Type complete, safe code:
```aethel
intent payment {
  sender: Account,
  receiver: Account,
  amount: Balance
}

guard {
  amount > 0;
  sender_balance >= amount;
}

verify {
  sender_balance == old_sender_balance - amount;
  receiver_balance == old_receiver_balance + amount;
}
```
2. Wait for analysis to complete (should be < 1 second)

**Expected Results**:
- Editor should have a green glow/border
- No error indicators should be visible
- Status should indicate "safe" or "verified"

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 4: Traffic Light - Unsafe Code

**Objective**: Verify traffic light shows red for unsafe code

**Steps**:
1. Type incomplete/unsafe code:
```aethel
intent payment {
  sender: Account,
  receiver: Account,
  amount: Balance
}

verify {
  sender_balance == old_sender_balance - amount;
}
```
2. Wait for analysis to complete

**Expected Results**:
- Editor should have a red glow/border
- Error indicators should be visible
- Status should indicate "unsafe" or "vulnerabilities detected"

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 5: Correction Tooltips

**Objective**: Verify correction suggestions appear for vulnerable code

**Steps**:
1. Type code with missing guards:
```aethel
intent payment {
  sender: Account,
  receiver: Account,
  amount: Balance
}

verify {
  sender_balance == old_sender_balance - amount;
}
```
2. Hover over the intent declaration or guard block area

**Expected Results**:
- Tooltip should appear with correction suggestion
- Tooltip should explain the vulnerability (e.g., "Missing guard block")
- Tooltip should provide a fix (e.g., suggested guard conditions)
- Tooltip should not obscure the code

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 6: Rapid Typing Performance

**Objective**: Verify system doesn't interrupt during rapid typing

**Steps**:
1. Start with empty editor
2. Type rapidly without pausing:
```aethel
intent payment { sender: Account, receiver: Account, amount: Balance }
guard { amount > 0; sender_balance >= amount; }
verify { sender_balance == old_sender_balance - amount; }
```
3. Type continuously without stopping

**Expected Results**:
- No suggestion popups should interrupt typing
- Suggestions should only appear after pausing (300ms)
- Editor should remain responsive
- No lag or stuttering

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 7: Error Handling - Invalid Code

**Objective**: Verify graceful handling of invalid code

**Steps**:
1. Type malformed code:
```aethel
intent payment {
  sender: Account
  receiver: Account  // Missing comma
  amount: Balance
}

guard {
  amount > 0
  // Missing semicolon
}
```
2. Wait for analysis

**Expected Results**:
- System should not crash
- Should show appropriate error messages
- Should continue to provide suggestions where possible
- Editor should remain functional

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 8: Error Handling - API Unavailable

**Objective**: Verify graceful handling when API is down

**Steps**:
1. Stop the backend API server
2. Try typing in the editor
3. Wait for requests to timeout

**Expected Results**:
- Editor should show "API unavailable" message
- Autocomplete should be disabled gracefully
- Editor should remain functional for typing
- No console errors should crash the page

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 9: Context Detection - Intent Signature

**Objective**: Verify suggestions in intent signature

**Steps**:
1. Type: `intent payment {`
2. Press Enter
3. Start typing parameter names

**Expected Results**:
- Should suggest common parameter patterns
- Should suggest: `sender: Account`, `receiver: Account`, `amount: Balance`
- Suggestions should be relevant to payment intents

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 10: Context Detection - Verify Block

**Objective**: Verify suggestions in verify block

**Steps**:
1. Type complete intent with guard block
2. Add verify block:
```aethel
verify {
  
}
```
3. Place cursor inside verify block
4. Start typing: `sender_balance`

**Expected Results**:
- Should suggest verification conditions
- Should suggest: `sender_balance == old_sender_balance - amount`
- Should suggest conservation checks
- Suggestions should be verify-specific

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 11: Performance - Response Time

**Objective**: Verify response time meets 250ms target

**Steps**:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Type in editor and trigger suggestions
4. Check network request timing for `/api/autopilot/suggestions`

**Expected Results**:
- Most requests should complete in < 250ms
- 95% of requests should be under 250ms
- No requests should take > 1 second (except on slow connections)

**Pass/Fail**: ___________

**Measured Times**: ___________________________________________

---

### Scenario 12: Caching Behavior

**Objective**: Verify response caching works

**Steps**:
1. Type some code
2. Move cursor to a position
3. Wait for suggestions
4. Move cursor away and back to same position
5. Check Network tab in developer tools

**Expected Results**:
- Second request to same position should use cache
- Should see fewer network requests
- Response should be instant (no network delay)

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

### Scenario 13: Multiple Code Examples

**Objective**: Test with various Aethel code patterns

**Test Cases**:

#### A. Simple Transfer
```aethel
intent transfer {
  sender: Account,
  receiver: Account,
  amount: Balance
}

guard {
  amount > 0;
  sender_balance >= amount;
}

verify {
  sender_balance == old_sender_balance - amount;
  receiver_balance == old_receiver_balance + amount;
}
```

#### B. Token Swap
```aethel
intent swap {
  account: Account,
  token_in: Token,
  token_out: Token,
  amount_in: Balance,
  amount_out: Balance
}

guard {
  amount_in > 0;
  amount_out > 0;
  account_balance_in >= amount_in;
}

verify {
  account_balance_in == old_account_balance_in - amount_in;
  account_balance_out == old_account_balance_out + amount_out;
}
```

#### C. Deposit
```aethel
intent deposit {
  account: Account,
  amount: Balance
}

guard {
  amount > 0;
  account_balance + amount <= MAX_BALANCE;
}

verify {
  account_balance == old_account_balance + amount;
  total_supply == old_total_supply + amount;
}
```

**Expected Results**:
- All examples should parse correctly
- Suggestions should be context-appropriate
- Traffic light should show correct status
- No crashes or errors

**Pass/Fail**: ___________

**Notes**: ___________________________________________

---

## Browser Compatibility Testing

Test in multiple browsers:

### Chrome/Edge (Chromium)
- Version: ___________
- Autocomplete: Pass/Fail
- Traffic Light: Pass/Fail
- Tooltips: Pass/Fail
- Performance: Pass/Fail

### Firefox
- Version: ___________
- Autocomplete: Pass/Fail
- Traffic Light: Pass/Fail
- Tooltips: Pass/Fail
- Performance: Pass/Fail

### Safari (if available)
- Version: ___________
- Autocomplete: Pass/Fail
- Traffic Light: Pass/Fail
- Tooltips: Pass/Fail
- Performance: Pass/Fail

---

## Known Issues and Bugs

### Issue 1: [Title]
**Description**: ___________________________________________
**Steps to Reproduce**: ___________________________________________
**Expected**: ___________________________________________
**Actual**: ___________________________________________
**Severity**: Critical / High / Medium / Low
**Status**: Open / Fixed / Won't Fix

### Issue 2: [Title]
**Description**: ___________________________________________
**Steps to Reproduce**: ___________________________________________
**Expected**: ___________________________________________
**Actual**: ___________________________________________
**Severity**: Critical / High / Medium / Low
**Status**: Open / Fixed / Won't Fix

---

## Test Summary

**Total Scenarios**: 13
**Passed**: ___________
**Failed**: ___________
**Blocked**: ___________

**Overall Status**: Pass / Fail / Needs Work

**Tester Name**: ___________________________________________
**Test Date**: ___________________________________________
**Environment**: ___________________________________________

---

## Recommendations

Based on manual testing, the following improvements are recommended:

1. ___________________________________________
2. ___________________________________________
3. ___________________________________________

---

## Sign-off

**Tested By**: ___________________________________________
**Date**: ___________________________________________
**Signature**: ___________________________________________

**Approved By**: ___________________________________________
**Date**: ___________________________________________
**Signature**: ___________________________________________
