# Requirements Document: Conservation Checker v1.3

## Introduction

The Conservation Checker is an automatic violation detection system for Aethel that ensures financial transactions obey the fundamental law of conservation: money cannot be created or destroyed from nothing. This system analyzes verify blocks in Aethel programs to detect when the sum of all balance changes does not equal zero, indicating a conservation violation.

## Glossary

- **Conservation_Checker**: The system component that analyzes verify blocks and detects conservation violations
- **Verify_Block**: A code block in Aethel that specifies post-conditions for financial transactions
- **Balance_Change**: The difference between a variable's old value and new value in a verify block
- **Conservation_Violation**: A state where the sum of all balance changes in a transaction does not equal zero
- **Judge**: The existing Aethel verification system that validates program correctness using Z3
- **Parser**: The component that converts Aethel source code into an Abstract Syntax Tree (AST)
- **Z3_Solver**: The SMT solver used by Aethel for formal verification

## Requirements

### Requirement 1: Automatic Balance Change Detection

**User Story:** As an Aethel developer, I want the system to automatically detect all balance changes in verify blocks, so that I don't need to manually annotate which variables represent money.

#### Acceptance Criteria

1. WHEN a verify block contains balance comparisons, THE Conservation_Checker SHALL identify all variables that represent financial balances
2. WHEN a variable is compared to its old value, THE Conservation_Checker SHALL calculate the balance change as (new_value - old_value)
3. WHEN multiple variables change in a verify block, THE Conservation_Checker SHALL track all balance changes independently
4. WHEN a verify block contains no balance changes, THE Conservation_Checker SHALL skip conservation checking for that block

### Requirement 2: Conservation Law Validation

**User Story:** As an Aethel developer, I want the system to validate that money is conserved in all transactions, so that I can detect bugs where money is created or destroyed.

#### Acceptance Criteria

1. WHEN all balance changes are detected, THE Conservation_Checker SHALL compute the sum of all changes
2. IF the sum of balance changes equals zero, THEN THE Conservation_Checker SHALL mark the transaction as valid
3. IF the sum of balance changes does not equal zero, THEN THE Conservation_Checker SHALL report a conservation violation
4. WHEN a transaction involves only one account, THE Conservation_Checker SHALL detect that money is being created or destroyed

### Requirement 3: Clear Violation Reporting

**User Story:** As an Aethel developer, I want clear error messages when conservation is violated, so that I can quickly identify and fix the bug.

#### Acceptance Criteria

1. WHEN a conservation violation is detected, THE Conservation_Checker SHALL report the exact amount created or destroyed
2. WHEN reporting violations, THE Conservation_Checker SHALL list all balance changes with their amounts
3. WHEN reporting violations, THE Conservation_Checker SHALL indicate whether money was created (positive sum) or destroyed (negative sum)
4. WHEN reporting violations, THE Conservation_Checker SHALL include the line numbers where balance changes occur

### Requirement 4: Judge System Integration

**User Story:** As an Aethel system architect, I want the Conservation Checker to integrate seamlessly with the existing Judge system, so that conservation checking happens automatically during verification.

#### Acceptance Criteria

1. WHEN the Judge verifies an intent, THE Conservation_Checker SHALL run automatically before Z3 verification
2. WHEN a conservation violation is detected, THE Judge SHALL fail verification immediately without calling Z3
3. WHEN conservation is valid, THE Judge SHALL proceed with normal Z3 verification
4. WHEN the Judge reports results, THE Conservation_Checker errors SHALL be included in the verification output

### Requirement 5: Performance Efficiency

**User Story:** As an Aethel developer, I want conservation checking to be fast, so that verification time remains acceptable for large programs.

#### Acceptance Criteria

1. WHEN analyzing a verify block, THE Conservation_Checker SHALL complete in O(n) time where n is the number of statements
2. WHEN conservation checking is enabled, THE total verification time SHALL increase by less than 10%
3. WHEN processing large programs, THE Conservation_Checker SHALL not cause memory issues
4. THE Conservation_Checker SHALL cache analysis results to avoid redundant computation

### Requirement 6: Arithmetic Expression Support

**User Story:** As an Aethel developer, I want conservation checking to work with arithmetic expressions, so that I can write natural balance change specifications.

#### Acceptance Criteria

1. WHEN a balance change uses addition (old_balance + amount), THE Conservation_Checker SHALL correctly extract the change amount
2. WHEN a balance change uses subtraction (old_balance - amount), THE Conservation_Checker SHALL correctly extract the change amount
3. WHEN a balance change uses multiplication or division, THE Conservation_Checker SHALL handle it correctly
4. WHEN expressions are nested, THE Conservation_Checker SHALL evaluate them to determine the net balance change

### Requirement 7: Multi-Party Transaction Support

**User Story:** As an Aethel developer, I want to write transactions involving multiple parties, so that I can model complex financial operations.

#### Acceptance Criteria

1. WHEN a transaction involves two parties, THE Conservation_Checker SHALL validate that one party's loss equals the other's gain
2. WHEN a transaction involves three or more parties, THE Conservation_Checker SHALL validate that the sum of all changes equals zero
3. WHEN a transaction splits funds among multiple recipients, THE Conservation_Checker SHALL validate conservation across all recipients
4. WHEN a transaction consolidates funds from multiple sources, THE Conservation_Checker SHALL validate conservation across all sources

### Requirement 8: Error Recovery and Diagnostics

**User Story:** As an Aethel developer, I want helpful diagnostics when conservation checking fails, so that I can understand what went wrong.

#### Acceptance Criteria

1. WHEN the Conservation_Checker cannot parse a balance expression, THE system SHALL report a clear error message
2. WHEN variable types are ambiguous, THE Conservation_Checker SHALL request type annotations
3. WHEN a verify block has syntax errors, THE Parser SHALL report errors before conservation checking
4. WHEN conservation checking encounters an internal error, THE system SHALL provide debugging information
