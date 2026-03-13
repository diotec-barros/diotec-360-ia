# Branch Protection Rules Configuration

This document provides instructions for configuring GitHub branch protection rules for the Diotec360 repository. Branch protection rules ensure code quality and security by requiring specific checks before code can be merged.

## Overview

Branch protection rules enforce:
- **Passing tests** before merge
- **Code review** from maintainers
- **CLA signature** from contributors
- **Status checks** from CI/CD pipelines

## Prerequisites

- Repository admin access
- GitHub Actions workflows configured (see `.github/workflows/`)
- CLA bot configured (see `CLA.md`)

## Configuration Steps

### 1. Access Branch Protection Settings

1. Navigate to the Diotec360 repository on GitHub
2. Click **Settings** → **Branches**
3. Under "Branch protection rules", click **Add rule**

### 2. Configure Main Branch Protection

#### Branch Name Pattern
```
main
```

#### Protection Settings

**Require a pull request before merging**
- ✅ Enable this setting
- **Required approvals**: 2
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (if CODEOWNERS file exists)
- ✅ Require approval of the most recent reviewable push

**Require status checks to pass before merging**
- ✅ Enable this setting
- ✅ Require branches to be up to date before merging
- **Required status checks**:
  - `test / test (3.11)` - Python 3.11 tests
  - `test / test (3.12)` - Python 3.12 tests
  - `lint / lint` - Code linting
  - `property-tests / property-tests` - Property-based tests
  - `documentation / validate-docs` - Documentation validation
  - `CLA` - Contributor License Agreement check

**Require conversation resolution before merging**
- ✅ Enable this setting
- Ensures all review comments are addressed

**Require signed commits**
- ⚠️ Optional but recommended
- Enhances security by requiring GPG-signed commits

**Require linear history**
- ✅ Enable this setting
- Prevents merge commits, requires rebase or squash

**Include administrators**
- ✅ Enable this setting
- Applies rules to repository administrators

**Restrict who can push to matching branches**
- ✅ Enable this setting
- **Allowed to push**: Maintainers team only
- Prevents direct pushes to main branch

**Allow force pushes**
- ❌ Disable this setting
- Prevents history rewriting on main branch

**Allow deletions**
- ❌ Disable this setting
- Prevents accidental branch deletion

### 3. Configure Release Branch Protection

For release branches (e.g., `release/v1.x`, `release/v2.x`):

#### Branch Name Pattern
```
release/*
```

#### Protection Settings

Apply the same settings as main branch, with these modifications:

**Required approvals**: 1 (less strict than main)

**Required status checks**:
- `test / test (3.11)` - Python 3.11 tests
- `test / test (3.12)` - Python 3.12 tests
- `lint / lint` - Code linting
- `CLA` - Contributor License Agreement check

### 4. Configure Development Branch Protection

For development branches (e.g., `develop`, `dev`):

#### Branch Name Pattern
```
develop
```

#### Protection Settings

**Require a pull request before merging**
- ✅ Enable this setting
- **Required approvals**: 1

**Require status checks to pass before merging**
- ✅ Enable this setting
- **Required status checks**:
  - `test / test (3.11)` - Python 3.11 tests
  - `lint / lint` - Code linting

**Require conversation resolution before merging**
- ✅ Enable this setting

**Include administrators**
- ❌ Disable this setting (allow admins to bypass for hotfixes)

## Status Check Configuration

### GitHub Actions Workflows

Ensure the following workflows are configured in `.github/workflows/`:

**test.yml** - Run test suite
```yaml
name: test
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    # ... test steps
```

**lint.yml** - Run linting checks
```yaml
name: lint
on: [push, pull_request]
jobs:
  lint:
    # ... linting steps
```

**property-tests.yml** - Run property-based tests
```yaml
name: property-tests
on: [push, pull_request]
jobs:
  property-tests:
    # ... property test steps
```

**documentation.yml** - Validate documentation
```yaml
name: documentation
on: [push, pull_request]
jobs:
  validate-docs:
    # ... documentation validation steps
```

### CLA Bot Configuration

Configure the CLA Assistant bot:

1. Install [CLA Assistant](https://github.com/apps/cla-assistant) GitHub App
2. Configure with `CLA.md` file
3. Add CLA check to required status checks

**CLA Assistant Configuration** (`.clabot`):
```json
{
  "contributors": [],
  "message": "Thank you for your contribution! Please sign our Contributor License Agreement (CLA) before we can merge your pull request.",
  "label": "cla-signed",
  "recheckComment": "I have read the CLA Document and I hereby sign the CLA"
}
```

## Verification

After configuring branch protection rules, verify they work:

### Test 1: Direct Push Prevention
```bash
# This should fail
git checkout main
git commit --allow-empty -m "Test direct push"
git push origin main
# Expected: Error - protected branch
```

### Test 2: PR Without Approval
1. Create a test branch and PR
2. Try to merge without approval
3. Expected: Merge button disabled

### Test 3: PR Without Passing Tests
1. Create a PR with failing tests
2. Try to merge
3. Expected: Merge blocked by status checks

### Test 4: PR Without CLA
1. Create a PR from a new contributor without CLA
2. Try to merge
3. Expected: Merge blocked by CLA check

## Troubleshooting

### Status Checks Not Appearing

**Problem**: Required status checks don't appear in PR

**Solutions**:
1. Ensure GitHub Actions workflows are triggered on `pull_request` events
2. Check workflow names match exactly in branch protection settings
3. Verify workflows have run at least once on the branch

### CLA Check Not Working

**Problem**: CLA check doesn't appear or always fails

**Solutions**:
1. Verify CLA Assistant app is installed
2. Check `.clabot` configuration file exists
3. Ensure `CLA.md` file exists in repository root
4. Re-trigger CLA check by commenting on PR

### Administrators Bypassing Rules

**Problem**: Admins can bypass protection rules

**Solutions**:
1. Enable "Include administrators" in branch protection settings
2. Educate team on importance of following rules
3. Use audit logs to monitor bypasses

### Merge Conflicts

**Problem**: PR has merge conflicts

**Solutions**:
1. Enable "Require branches to be up to date before merging"
2. Contributor must rebase or merge main into their branch
3. Re-run status checks after resolving conflicts

## Maintenance

### Regular Reviews

Review branch protection rules quarterly:
- ✅ Verify all required checks are still relevant
- ✅ Add new checks as CI/CD evolves
- ✅ Remove deprecated checks
- ✅ Update approval requirements as team grows

### Audit Logs

Monitor branch protection bypasses:
1. Navigate to **Settings** → **Audit log**
2. Filter by "branch protection" events
3. Review any bypasses or rule changes
4. Investigate unauthorized changes

### Team Permissions

Ensure proper team permissions:
- **Maintainers**: Can approve PRs, merge to main
- **Committers**: Can approve PRs, cannot merge to main
- **Contributors**: Can create PRs, cannot approve

## Best Practices

### For Maintainers

1. **Always require reviews**: Never merge your own PRs
2. **Wait for all checks**: Don't bypass status checks
3. **Review thoroughly**: Check code, tests, and documentation
4. **Communicate**: Explain rejection reasons clearly
5. **Be responsive**: Review PRs within 48 hours

### For Contributors

1. **Sign CLA first**: Sign before submitting PR
2. **Run tests locally**: Use pre-commit hooks
3. **Keep PRs small**: Easier to review and merge
4. **Respond to feedback**: Address review comments promptly
5. **Rebase regularly**: Keep branch up to date with main

### For Administrators

1. **Lead by example**: Follow rules even when you can bypass
2. **Document bypasses**: Explain why in commit message
3. **Emergency only**: Only bypass for critical hotfixes
4. **Audit regularly**: Review protection rule changes
5. **Educate team**: Ensure everyone understands rules

## Emergency Procedures

### Critical Hotfix Process

For critical security or production issues:

1. **Create hotfix branch** from main
   ```bash
   git checkout main
   git pull
   git checkout -b hotfix/critical-issue
   ```

2. **Make minimal fix** - Only fix the critical issue

3. **Test thoroughly** - Run all tests locally

4. **Create PR** with "HOTFIX" label

5. **Fast-track review** - Request immediate review from 2+ maintainers

6. **Merge with admin override** if necessary (document reason)

7. **Post-merge review** - Review hotfix in next team meeting

### Rollback Procedure

If a merged PR causes issues:

1. **Revert commit** on main branch
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

2. **Create rollback PR** with explanation

3. **Fast-track merge** after quick review

4. **Investigate root cause** - Why did checks pass?

5. **Improve checks** - Add tests to prevent recurrence

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [CLA Assistant Documentation](https://github.com/cla-assistant/cla-assistant)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Aethel Contributing Guide](../../CONTRIBUTING.md)
- [Aethel Governance Model](../../GOVERNANCE.md)

## Checklist

Use this checklist when configuring branch protection:

- [ ] Main branch protection configured
- [ ] Release branch protection configured
- [ ] Development branch protection configured
- [ ] All required status checks added
- [ ] CLA check configured
- [ ] Review requirements set
- [ ] Administrator inclusion enabled
- [ ] Force push disabled
- [ ] Branch deletion disabled
- [ ] Linear history required
- [ ] Conversation resolution required
- [ ] Protection rules tested
- [ ] Team permissions verified
- [ ] Documentation updated
- [ ] Team notified of changes

---

**Copyright © 2024-2026 DIOTEC 360**  
Licensed under Apache 2.0

