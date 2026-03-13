# Diotec360 validation Tools

This directory contains validation tools for preparing Aethel for open source release. These tools ensure that the repository meets all requirements for professional open source distribution.

## Available Validators

### 1. Documentation Validator (`validate_documentation.py`)

Validates that all required documentation files exist, contain required sections, have valid internal links, and include required badges.

**Usage:**
```bash
python scripts/validate_documentation.py [repo_root]
```

**Checks:**
- Required files exist (README.md, LICENSE, CONTRIBUTING.md, etc.)
- Required sections present in each document
- Internal links are valid
- README contains required badges
- Documentation directory structure is complete

### 2. Copyright Header Validator (`validate_copyright.py`)

Scans source files and validates that they contain proper copyright headers attributing ownership to DIOTEC 360.

**Usage:**
```bash
# Validate only
python scripts/validate_copyright.py [repo_root]

# Validate and automatically add missing headers
python scripts/validate_copyright.py [repo_root] --add-headers

# Specify copyright year
python scripts/validate_copyright.py [repo_root] --add-headers --year 2024
```

**Checks:**
- All source files (.py, .js, .ts, etc.) have copyright headers
- Headers attribute ownership to DIOTEC 360

**Features:**
- Automatic header insertion
- Respects shebang lines
- Configurable copyright year

### 3. Repository Structure Validator (`validate_repository_structure.py`)

Validates that the repository has the correct structure, all core components are available in the open source codebase, and commercial code is properly separated.

**Usage:**
```bash
python scripts/validate_repository_structure.py [repo_root]
```

**Checks:**
- Required directories exist
- Core open source components are present
- Commercial code is not in open source areas
- Documentation structure is complete

### 4. Version Management Validator (`validate_version_management.py`)

Validates semantic versioning compliance, release tags, changelog entries, and release branch existence.

**Usage:**
```bash
python scripts/validate_version_management.py [repo_root]
```

**Checks:**
- Release tags follow semantic versioning (MAJOR.MINOR.PATCH)
- All releases have changelog entries
- Major versions have release branches

### 5. Master Validator (`validate_all.py`)

Runs all validation checks and provides a comprehensive report.

**Usage:**
```bash
# Run all validators
python scripts/validate_all.py [repo_root]

# Skip specific validators
python scripts/validate_all.py [repo_root] --skip-docs
python scripts/validate_all.py [repo_root] --skip-copyright
python scripts/validate_all.py [repo_root] --skip-structure
python scripts/validate_all.py [repo_root] --skip-version
```

## Exit Codes

All validators follow standard Unix exit code conventions:
- `0`: All checks passed
- `1`: One or more checks failed

This allows integration with CI/CD pipelines.

## Integration with CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Validate Open Source Preparation
  run: python scripts/validate_all.py
```

## Validation Reports

Each validator produces a detailed report showing:
- **Errors**: Critical issues that must be fixed
- **Warnings**: Non-critical issues that should be addressed
- **Missing Components**: Required files or sections that are missing
- **Status**: Overall pass/fail status

## Example Output

```
================================================================================
DOCUMENTATION VALIDATION REPORT
================================================================================

ERRORS (2):
--------------------------------------------------------------------------------
  X Required file missing: TRADEMARK.md
  X Required file missing: ROADMAP.md

MISSING SECTIONS (1):
--------------------------------------------------------------------------------
  X CONTRIBUTING.md: Code Review Process

BROKEN LINKS (3):
--------------------------------------------------------------------------------
  X README.md: docs/missing-file.md
  X SECURITY.md: tools/security-scanner.py
  X docs/api-reference/judge.md: ../examples/banking.md

================================================================================
STATUS: FAILED
================================================================================
```

## Troubleshooting

### Unicode Errors on Windows

The validators use ASCII-compatible symbols (X, !, OK) to avoid Unicode encoding issues on Windows terminals.

### Git Not Available

The version management validator requires git. If git is not available, it will skip git-based checks and issue a warning.

### Permission Errors

Ensure you have read permissions for all files in the repository. The copyright validator requires write permissions when using `--add-headers`.

## Development

### Adding New Validators

1. Create a new validator script following the pattern of existing validators
2. Implement a validation class with a `validate_all()` method
3. Return a report dataclass with `is_valid`, `errors`, and `warnings` fields
4. Add a `print_report()` function for formatted output
5. Update `validate_all.py` to include the new validator

### Testing Validators

Run validators on the Aethel repository:

```bash
python scripts/validate_documentation.py
python scripts/validate_copyright.py
python scripts/validate_repository_structure.py
python scripts/validate_version_management.py
```

## License

Copyright (c) 2024 DIOTEC 360. All rights reserved.
