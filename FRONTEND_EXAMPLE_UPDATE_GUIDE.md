# Frontend Example Update Guide - v1.9.0

**Purpose**: Update the Proof Viewer to show only parseable examples  
**Status**: Ready for implementation  
**Priority**: HIGH (UX issue)

---

## Problem

The Proof Viewer currently shows all 15 examples, but only 6 are parseable. Users clicking on documentation examples see parse errors, which damages trust in the system.

---

## Solution

Filter the example selector to show only the 6 parseable examples.

---

## Implementation

### Option 1: Filter in ExampleSelector Component (Recommended)

**File**: `frontend/components/ExampleSelector.tsx`

```typescript
// Add this constant at the top of the file
const PARSEABLE_EXAMPLES = [
  'simple_transfer.ae',
  'insurance_payout.ae',
  'defi_liquidation.ae',
  'batch_transfer.ae',
  'secret_payment.ae',
  'private_compliance.ae'
];

// In the component, filter the examples
const parseableExamples = examples.filter(ex => 
  PARSEABLE_EXAMPLES.includes(ex.filename)
);

// Use parseableExamples in the dropdown instead of examples
```

### Option 2: Update Example Metadata

**File**: `frontend/lib/examples.ts` (or wherever examples are defined)

Add a `parseable` flag to each example:

```typescript
export const examples = [
  {
    filename: 'simple_transfer.ae',
    title: 'Simple Transfer',
    description: 'Basic account transfer with conservation',
    parseable: true,  // ✅ Add this
    category: 'Banking'
  },
  {
    filename: 'adversarial_test.ae',
    title: 'Adversarial Test',
    description: 'Attack pattern demonstration',
    parseable: false,  // ❌ Add this
    category: 'Security'
  },
  // ... etc
];

// Then filter in the component
const parseableExamples = examples.filter(ex => ex.parseable);
```

### Option 3: Separate Example Lists

Create two separate lists:

```typescript
// frontend/lib/examples.ts

export const parseableExamples = [
  {
    filename: 'simple_transfer.ae',
    title: 'Simple Transfer',
    description: 'Basic account transfer',
    category: 'Banking'
  },
  // ... 5 more
];

export const documentationExamples = [
  {
    filename: 'adversarial_test.ae',
    title: 'Adversarial Test (Documentation)',
    description: 'Attack patterns (pseudo-code)',
    category: 'Security'
  },
  // ... 8 more
];

// In the component, use only parseableExamples
```

---

## Recommended Approach

**Use Option 1** (Filter in component) because:
- ✅ Minimal code changes
- ✅ Easy to revert if needed
- ✅ Centralized list of parseable examples
- ✅ Can be updated without touching example metadata

---

## Step-by-Step Instructions

### 1. Open the ExampleSelector Component

```bash
code frontend/components/ExampleSelector.tsx
```

### 2. Add the Parseable Examples List

At the top of the file, after imports:

```typescript
// List of examples that work in the Proof Viewer (v1.9.0)
const PARSEABLE_EXAMPLES = [
  'simple_transfer.ae',
  'insurance_payout.ae',
  'defi_liquidation.ae',
  'batch_transfer.ae',
  'secret_payment.ae',
  'private_compliance.ae'
];
```

### 3. Filter the Examples

Find where examples are used in the component and add the filter:

```typescript
// Before
const exampleList = examples;

// After
const exampleList = examples.filter(ex => 
  PARSEABLE_EXAMPLES.includes(ex.filename)
);
```

Or if examples come from props:

```typescript
// In the component function
const parseableExamples = useMemo(() => 
  examples.filter(ex => PARSEABLE_EXAMPLES.includes(ex.filename)),
  [examples]
);

// Then use parseableExamples in the JSX
```

### 4. Update the Dropdown

Make sure the dropdown uses the filtered list:

```typescript
<select onChange={handleExampleChange}>
  <option value="">Select an example...</option>
  {parseableExamples.map(ex => (
    <option key={ex.filename} value={ex.filename}>
      {ex.title}
    </option>
  ))}
</select>
```

### 5. Test

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` and verify:
- ✅ Only 6 examples appear in dropdown
- ✅ All 6 examples parse successfully
- ✅ No parse errors when clicking "Prove"

---

## Alternative: Add Documentation Tab

If you want to keep all examples visible, add a tab system:

```typescript
const [tab, setTab] = useState<'parseable' | 'documentation'>('parseable');

// In JSX
<div className="tabs">
  <button onClick={() => setTab('parseable')}>
    Parseable Examples (6)
  </button>
  <button onClick={() => setTab('documentation')}>
    Documentation (9)
  </button>
</div>

{tab === 'parseable' ? (
  <ExampleList examples={parseableExamples} />
) : (
  <ExampleList examples={documentationExamples} />
)}
```

Add a warning for documentation examples:

```typescript
{tab === 'documentation' && (
  <div className="warning">
    ⚠️ These examples contain pseudo-code for documentation purposes.
    They may not parse in the Proof Viewer until v2.0.0.
  </div>
)}
```

---

## Testing Checklist

After making changes:

- [ ] All 6 parseable examples appear in dropdown
- [ ] No documentation examples appear (or they're in separate tab)
- [ ] Each example loads without errors
- [ ] "Prove" button works for all examples
- [ ] No console errors
- [ ] UI looks clean and professional

---

## Example Descriptions

Use these descriptions in the UI:

### simple_transfer.ae
**Title**: Simple Transfer  
**Description**: Basic account transfer with conservation proof  
**Category**: Banking  
**Features**: Balance validation, conservation, overflow protection

### insurance_payout.ae
**Title**: Insurance Payout  
**Description**: Parametric insurance with oracle data  
**Category**: Insurance  
**Features**: External oracle, threshold triggers, pool management

### defi_liquidation.ae
**Title**: DeFi Liquidation  
**Description**: Collateral liquidation with price oracle  
**Category**: DeFi  
**Features**: Price feeds, under-collateralization detection, liquidator rewards

### batch_transfer.ae
**Title**: Batch Transfer  
**Description**: Atomic batch payroll processing  
**Category**: Enterprise  
**Features**: Parallel execution, atomic commits, conservation across batch

### secret_payment.ae
**Title**: Secret Payment  
**Description**: Zero-knowledge transfer  
**Category**: Privacy  
**Features**: Secret balances, ZKP verification, privacy-preserving

### private_compliance.ae
**Title**: Private Compliance  
**Description**: Medical compliance without revealing data  
**Category**: Privacy  
**Features**: Secret diagnosis, ZKP verification, regulatory compliance

---

## Future Work (v2.0.0)

When the grammar is expanded:

1. Update `PARSEABLE_EXAMPLES` list to include all 15 examples
2. Remove the filter (or keep it for backwards compatibility)
3. Update example descriptions
4. Add new examples showcasing v2.0.0 features

---

## Rollback Plan

If issues arise:

1. Remove the filter: `const exampleList = examples;`
2. Commit and push
3. Deploy

The original examples are still in the repository, so rollback is instant.

---

## Documentation Updates

After implementing:

1. Update `README.md` to mention only 6 examples work in Proof Viewer
2. Add note to `DIOTEC360_V1_9_0_EXAMPLE_STANDARDS.md` about frontend changes
3. Update any user-facing documentation

---

## Summary

**Change Required**: 1 file (`ExampleSelector.tsx`)  
**Lines of Code**: ~10 lines  
**Risk**: Low (easy to rollback)  
**Impact**: High (fixes UX issue)  
**Time Estimate**: 15 minutes  

**Verdict**: ✅ Ready to implement

---

**Status**: Ready for frontend team  
**Priority**: HIGH  
**Complexity**: LOW  
**Impact**: HIGH

🚀 Let's ship it!
