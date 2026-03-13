# Branch Protection Quick Reference

Quick reference for Aethel repository branch protection rules.

## Main Branch (`main`)

**Protection Level**: Maximum

| Setting | Value |
|---------|-------|
| Required Approvals | 2 |
| Dismiss Stale Reviews | ✅ Yes |
| Code Owner Review | ✅ Yes |
| Require Up-to-Date | ✅ Yes |
| Linear History | ✅ Yes |
| Enforce Admins | ✅ Yes |
| Allow Force Push | ❌ No |
| Allow Deletion | ❌ No |

**Required Status Checks**:
- `test / test (3.11)` - Python 3.11 tests
- `test / test (3.12)` - Python 3.12 tests  
- `lint / lint` - Code linting
- `property-tests / property-tests` - Property-based tests
- `documentation / validate-docs` - Documentation validation
- `CLA` - Contributor License Agreement

## Release Branches (`release/*`)

**Protection Level**: High

| Setting | Value |
|---------|-------|
| Required Approvals | 1 |
| Dismiss Stale Reviews | ✅ Yes |
| Code Owner Review | ❌ No |
| Require Up-to-Date | ✅ Yes |
| Linear History | ✅ Yes |
| Enforce Admins | ✅ Yes |
| Allow Force Push | ❌ No |
| Allow Deletion | ❌ No |

**Required Status Checks**:
- `test / test (3.11)` - Python 3.11 tests
- `test / test (3.12)` - Python 3.12 tests
- `lint / lint` - Code linting
- `CLA` - Contributor License Agreement

## Development Branch (`develop`)

**Protection Level**: Medium

| Setting | Value |
|---------|-------|
| Required Approvals | 1 |
| Dismiss Stale Reviews | ✅ Yes |
| Code Owner Review | ❌ No |
| Require Up-to-Date | ✅ Yes |
| Linear History | ❌ No |
| Enforce Admins | ❌ No |
| Allow Force Push | ❌ No |
| Allow Deletion | ❌ No |

**Required Status Checks**:
- `test / test (3.11)` - Python 3.11 tests
- `lint / lint` - Code linting

## Common Commands

### Verify Protection
```bash
# Set GitHub token
export GITHUB_TOKEN=your_token_here

# Run verification script
python scripts/verify_branch_protection.py
```

### Test Protection
```bash
# Should fail - direct push to main
git checkout main
git commit --allow-empty -m "Test"
git push origin main

# Should succeed - via PR
git checkout -b test-branch
git commit --allow-empty -m "Test"
git push origin test-branch
# Create PR on GitHub
```

## Emergency Bypass

**Only for critical hotfixes!**

1. Create hotfix branch
2. Make minimal fix
3. Create PR with "HOTFIX" label
4. Get 2+ maintainer approvals
5. Admin can merge with override if needed
6. Document reason in commit message

## Quick Links

- [Full Documentation](branch-protection.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Governance Model](../../GOVERNANCE.md)
- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)

---

**Copyright © 2024-2026 DIOTEC 360**  
Licensed under Apache 2.0

