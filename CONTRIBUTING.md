# Contributing to Aethel Protocol

Thank you for your interest in contributing to Aethel! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Submitting Contributions](#submitting-contributions)
- [Governance Model](#governance-model)
- [Contributor License Agreement](#contributor-license-agreement)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Z3 Theorem Prover (installed automatically with dependencies)

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/aethel.git
cd aethel
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

4. **Run tests to verify setup**

```bash
python -m pytest
```

5. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

## Development Process

### Finding Issues to Work On

- Check the [Issues](https://github.com/diotec360/diotec360/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### Making Changes

1. **Write clear, focused commits**
   - Each commit should represent a single logical change
   - Write descriptive commit messages

2. **Follow the coding standards** (see below)

3. **Add tests for new functionality**
   - Unit tests for individual components
   - Property-based tests for universal correctness properties
   - Integration tests for component interactions

4. **Update documentation**
   - Update relevant documentation files
   - Add docstrings to new functions and classes
   - Update examples if applicable

5. **Keep your branch up to date**

```bash
git fetch upstream
git rebase upstream/main
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Code Quality Tools

We use the following tools to maintain code quality:

```bash
# Format code
black aethel/

# Check style
flake8 aethel/

# Type checking
mypy aethel/

# Sort imports
isort aethel/
```

### Documentation

- All public functions and classes must have docstrings
- Use Google-style docstrings
- Include examples in docstrings where helpful

Example:

```python
def verify_proof(code: str, context: dict) -> Verdict:
    """Verify an Aethel proof for correctness.
    
    Args:
        code: Aethel source code containing solve block
        context: Execution context with variable bindings
        
    Returns:
        Verdict object containing verification result
        
    Raises:
        ParseError: If code cannot be parsed
        VerificationError: If proof verification fails
        
    Example:
        >>> verdict = verify_proof("solve transfer { ... }", {})
        >>> print(verdict.is_valid)
        True
    """
    pass
```

## Testing Requirements

### Test Coverage

- All new code must have test coverage
- Aim for at least 80% code coverage
- Critical paths (security, conservation) require 100% coverage

### Test Types

#### 1. Unit Tests

Test individual functions and classes:

```python
def test_conservation_validator():
    validator = ConservationValidator()
    result = validator.validate(transaction)
    assert result.is_valid
```

#### 2. Property-Based Tests

Test universal properties with many inputs:

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition should be commutative."""
    assert a + b == b + a
```

#### 3. Integration Tests

Test component interactions:

```python
def test_end_to_end_transaction():
    judge = Judge()
    runtime = Runtime()
    
    verdict = judge.verify(code)
    assert verdict.is_valid
    
    result = runtime.execute(verdict)
    assert result.success
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_judge.py

# Run with coverage
python -m pytest --cov=aethel --cov-report=html

# Run property-based tests
python -m pytest test_properties_*.py
```

## Submitting Contributions

### Pull Request Process

1. **Ensure all tests pass**

```bash
python -m pytest
```

2. **Update documentation**
   - Update CHANGELOG.md with your changes
   - Update relevant documentation files

3. **Sign the Contributor License Agreement (CLA)**
   - See [CLA section](#contributor-license-agreement) below

4. **Create a pull request**
   - Use a clear, descriptive title
   - Fill out the pull request template
   - Reference any related issues

5. **Respond to review feedback**
   - Address reviewer comments promptly
   - Make requested changes
   - Re-request review when ready

### Pull Request Template

When creating a pull request, include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Checklist**:
  - [ ] Tests added/updated
  - [ ] Documentation updated
  - [ ] CHANGELOG.md updated
  - [ ] CLA signed
  - [ ] All tests passing
  - [ ] Code follows style guidelines

### Review Process

1. **Automated checks** run on every PR:
   - Tests must pass
   - Code coverage must meet threshold
   - Linting must pass
   - CLA must be signed

2. **Code review** by maintainers:
   - At least one maintainer must approve
   - Reviews typically completed within 3-5 business days
   - Be patient and respectful during review

3. **Merge**:
   - Maintainers will merge approved PRs
   - PRs are typically squashed into a single commit

## Governance Model

### Authority Structure

**DIOTEC 360** maintains final authority over the Aethel Protocol standard. This ensures:
- Consistent vision and direction
- Quality and security standards
- Brand integrity and trust

### Roles

#### Maintainers
- Core team members with commit access
- Review and merge pull requests
- Make technical decisions
- Employed or contracted by DIOTEC 360

#### Committers
- Trusted contributors with specialized expertise
- Can approve PRs in their area of expertise
- Nominated by maintainers

#### Contributors
- Anyone who submits code, documentation, or bug reports
- All contributions are valued and appreciated

#### Users
- Anyone using Aethel Protocol
- Feedback and bug reports are essential contributions

### Decision Making

1. **Technical Decisions**:
   - Maintainers discuss and reach consensus
   - DIOTEC 360 has final say on protocol changes
   - Community input is valued and considered

2. **Feature Requests**:
   - Submitted as GitHub issues
   - Discussed by community and maintainers
   - Prioritized based on strategic goals

3. **Breaking Changes**:
   - Require extensive discussion
   - Must be justified by significant benefits
   - Require approval from DIOTEC 360 leadership

### Conflict Resolution

If disagreements arise:

1. **Discussion**: Try to reach consensus through respectful discussion
2. **Escalation**: Escalate to senior maintainers if needed
3. **Final Decision**: DIOTEC 360 makes final decision if consensus cannot be reached

## Contributor License Agreement

### Why a CLA?

The CLA ensures:
- DIOTEC 360 can distribute your contributions
- Your contributions can be relicensed if needed
- Patent protection for all users
- Clear legal status of contributions

### Signing the CLA

**Individual Contributors**:

1. Read the [CLA](CLA.md)
2. Sign electronically at: https://cla.diotec360.com
3. Or email signed CLA to: legal@diotec360.com

**Corporate Contributors**:

If contributing on behalf of your employer:
1. Your employer must sign a Corporate CLA
2. Contact: legal@diotec360.com

### CLA Verification

- Automated bot checks CLA status on every PR
- PRs cannot be merged without signed CLA
- CLA covers all future contributions

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Discord**: Real-time chat (https://discord.gg/aethel)
- **Twitter**: [@AethelProtocol](https://twitter.com/AethelProtocol)
- **Email**: community@diotec360.com

### Getting Help

- **Documentation**: Start with the [docs/](docs/) directory
- **Examples**: Check [examples/](examples/) for code samples
- **Discussions**: Ask questions in GitHub Discussions
- **Discord**: Get real-time help from the community

### Reporting Bugs

Use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, Diotec360 version)
- Minimal code example demonstrating the issue

### Requesting Features

Use the feature request template and include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)
- Willingness to contribute implementation

### Security Issues

**Do NOT report security issues publicly.**

- Email: security@diotec360.com
- See [SECURITY.md](SECURITY.md) for details
- We respond within 24 hours

## Recognition

### Contributors

All contributors are recognized in:
- CHANGELOG.md for each release
- GitHub contributors page
- Annual contributor recognition posts

### Hall of Fame

Exceptional contributors may be featured in:
- Project README
- Blog posts and announcements
- Conference presentations

## Commercial Opportunities

### Certification

DIOTEC 360 offers certification for:
- Aethel implementations
- Aethel developers
- Aethel architects

Contact: certification@diotec360.com

### Partnership

Interested in commercial partnership?
- Managed hosting resellers
- Training providers
- Integration partners

Contact: partnerships@diotec360.com

### Employment

DIOTEC 360 hires from the contributor community.

- Careers: https://diotec360.com/careers
- Email: careers@diotec360.com

## Questions?

If you have questions about contributing:

- **Technical**: Ask in GitHub Discussions
- **Process**: Email community@diotec360.com
- **Legal**: Email legal@diotec360.com

---

**Thank you for contributing to Aethel Protocol!**

Together, we're building the mathematical foundation for trustless financial systems.

**Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360**
