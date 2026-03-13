# Task 3: Hard-Reject Parsing - Documentation Complete

## Status: ✅ COMPLETE

### Task: Documentation lists all supported constraint syntax

**Completion Date**: 2026-02-22

---

## What Was Implemented

Updated `docs/language-reference/conservation-laws.md` with a comprehensive "Supported Constraint Syntax" section that includes:

### 1. Overview
- Explanation of hard-reject parsing (RVC2-004)
- Security rationale for explicit whitelisting

### 2. Supported Operations Tables

#### Arithmetic Operators
- Addition (+)
- Subtraction (-)
- Multiplication (*)
- Division (/)
- Modulo (%)

#### Comparison Operators
- Equal (==)
- Not Equal (!=)
- Less Than (<)
- Less or Equal (<=)
- Greater Than (>)
- Greater or Equal (>=)

#### Unary Operators
- Unary Minus (-)
- Unary Plus (+)

#### Literals and Variables
- Integers
- Floats
- Variable names

### 3. Code Examples

#### Supported Examples
- Simple arithmetic constraints
- Comparison operations
- Complex nested expressions
- Unary operations

#### Unsupported Examples
- Bitwise operations (|, &, ^, <<, >>)
- Logical operations (and, or, not)
- Advanced operations (**, //, abs(), in)

### 4. Error Messages
- Example of clear error message when unsupported operation is used
- Shows violation type, node type, and recovery hint

### 5. Migration Guide
- How to rewrite unsupported operations using supported syntax
- 4 practical examples with before/after code

### 6. Why Hard-Reject?
- Security benefits explained
- Principle: "Better to reject than to lie"

### 7. Extending Support
- Process for requesting new operations
- Evaluation criteria for extensions

---

## Verification

The documentation now provides:

✅ Complete list of all supported AST node types from SUPPORTED_AST_NODES whitelist
✅ Clear examples of supported constraint syntax
✅ Clear examples of unsupported operations
✅ Error message format
✅ Migration guide for developers
✅ Security rationale

---

## Files Modified

- `docs/language-reference/conservation-laws.md` - Added comprehensive "Supported Constraint Syntax" section

---

## Task Acceptance Criteria

From tasks.md:
- [x] Documentation lists all supported constraint syntax

**Status**: ✅ COMPLETE

All acceptance criteria met. The documentation now comprehensively lists all supported constraint syntax with examples, error messages, and migration guidance.

---

## Next Steps

This completes the documentation subtask of Task 3 (Hard-Reject Parsing). The parent task still has one remaining acceptance criterion:

- [ ] 100% test coverage for AST node handling

This will need to be addressed separately to fully complete Task 3.

---

*"Better to reject than to lie"* - RVC v2 Hardening Principle
