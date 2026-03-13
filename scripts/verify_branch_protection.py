#!/usr/bin/env python3
"""
Verify Branch Protection Rules

This script verifies that GitHub branch protection rules are properly configured
for the Diotec360 repository. It checks that all required protections are in place
and provides recommendations for improvements.

Usage:
    python scripts/verify_branch_protection.py

Requirements:
    pip install PyGithub

Environment Variables:
    GITHUB_TOKEN - GitHub personal access token with repo scope

Copyright © 2024-2026 DIOTEC 360
Licensed under Apache 2.0
"""

import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass

try:
    from github import Github, GithubException
except ImportError:
    print("❌ PyGithub not installed. Install with: pip install PyGithub")
    sys.exit(1)


@dataclass
class BranchProtectionConfig:
    """Expected branch protection configuration"""
    branch_pattern: str
    required_approvals: int
    required_status_checks: List[str]
    require_code_owner_reviews: bool
    dismiss_stale_reviews: bool
    require_linear_history: bool
    allow_force_pushes: bool
    allow_deletions: bool
    enforce_admins: bool


# Expected configurations for different branch patterns
EXPECTED_CONFIGS = {
    "main": BranchProtectionConfig(
        branch_pattern="main",
        required_approvals=2,
        required_status_checks=[
            "test / test (3.11)",
            "test / test (3.12)",
            "lint / lint",
            "property-tests / property-tests",
            "documentation / validate-docs",
            "CLA",
        ],
        require_code_owner_reviews=True,
        dismiss_stale_reviews=True,
        require_linear_history=True,
        allow_force_pushes=False,
        allow_deletions=False,
        enforce_admins=True,
    ),
    "release/*": BranchProtectionConfig(
        branch_pattern="release/*",
        required_approvals=1,
        required_status_checks=[
            "test / test (3.11)",
            "test / test (3.12)",
            "lint / lint",
            "CLA",
        ],
        require_code_owner_reviews=False,
        dismiss_stale_reviews=True,
        require_linear_history=True,
        allow_force_pushes=False,
        allow_deletions=False,
        enforce_admins=True,
    ),
    "develop": BranchProtectionConfig(
        branch_pattern="develop",
        required_approvals=1,
        required_status_checks=[
            "test / test (3.11)",
            "lint / lint",
        ],
        require_code_owner_reviews=False,
        dismiss_stale_reviews=True,
        require_linear_history=False,
        allow_force_pushes=False,
        allow_deletions=False,
        enforce_admins=False,
    ),
}


def print_header(message: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"✅ {message}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"⚠️  {message}")


def print_error(message: str) -> None:
    """Print an error message"""
    print(f"❌ {message}")


def print_info(message: str) -> None:
    """Print an info message"""
    print(f"ℹ️  {message}")


def get_github_client() -> Optional[Github]:
    """Get authenticated GitHub client"""
    token = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        print_error("GITHUB_TOKEN environment variable not set")
        print_info("Create a token at: https://github.com/settings/tokens")
        print_info("Required scopes: repo")
        print_info("Set with: export GITHUB_TOKEN=your_token_here")
        return None
    
    try:
        client = Github(token)
        # Test authentication
        client.get_user().login
        print_success("GitHub authentication successful")
        return client
    except GithubException as e:
        print_error(f"GitHub authentication failed: {e}")
        return None


def verify_branch_protection(
    repo,
    branch_name: str,
    expected: BranchProtectionConfig
) -> bool:
    """Verify branch protection configuration"""
    print_header(f"Verifying Branch: {branch_name}")
    
    try:
        branch = repo.get_branch(branch_name)
        protection = branch.get_protection()
    except GithubException as e:
        if e.status == 404:
            print_error(f"Branch '{branch_name}' not found or not protected")
            return False
        print_error(f"Error accessing branch protection: {e}")
        return False
    
    all_checks_passed = True
    
    # Check required approvals
    try:
        required_reviews = protection.required_pull_request_reviews
        if required_reviews:
            actual_approvals = required_reviews.required_approving_review_count
            if actual_approvals >= expected.required_approvals:
                print_success(
                    f"Required approvals: {actual_approvals} "
                    f"(expected: {expected.required_approvals})"
                )
            else:
                print_warning(
                    f"Required approvals: {actual_approvals} "
                    f"(expected: {expected.required_approvals})"
                )
                all_checks_passed = False
            
            # Check dismiss stale reviews
            if required_reviews.dismiss_stale_reviews == expected.dismiss_stale_reviews:
                print_success(
                    f"Dismiss stale reviews: {required_reviews.dismiss_stale_reviews}"
                )
            else:
                print_warning(
                    f"Dismiss stale reviews: {required_reviews.dismiss_stale_reviews} "
                    f"(expected: {expected.dismiss_stale_reviews})"
                )
                all_checks_passed = False
            
            # Check code owner reviews
            if required_reviews.require_code_owner_reviews == expected.require_code_owner_reviews:
                print_success(
                    f"Require code owner reviews: {required_reviews.require_code_owner_reviews}"
                )
            else:
                print_warning(
                    f"Require code owner reviews: {required_reviews.require_code_owner_reviews} "
                    f"(expected: {expected.require_code_owner_reviews})"
                )
                all_checks_passed = False
        else:
            print_error("Pull request reviews not required")
            all_checks_passed = False
    except Exception as e:
        print_error(f"Error checking required reviews: {e}")
        all_checks_passed = False
    
    # Check required status checks
    try:
        required_checks = protection.required_status_checks
        if required_checks:
            actual_checks = set(required_checks.contexts)
            expected_checks = set(expected.required_status_checks)
            
            missing_checks = expected_checks - actual_checks
            extra_checks = actual_checks - expected_checks
            
            if not missing_checks and not extra_checks:
                print_success(f"Required status checks: {len(actual_checks)} configured")
                for check in sorted(actual_checks):
                    print(f"    ✓ {check}")
            else:
                if missing_checks:
                    print_warning(f"Missing status checks: {len(missing_checks)}")
                    for check in sorted(missing_checks):
                        print(f"    ✗ {check}")
                    all_checks_passed = False
                
                if extra_checks:
                    print_info(f"Extra status checks: {len(extra_checks)}")
                    for check in sorted(extra_checks):
                        print(f"    + {check}")
            
            # Check strict status checks
            if required_checks.strict:
                print_success("Strict status checks: enabled (branches must be up to date)")
            else:
                print_warning("Strict status checks: disabled (branches can be outdated)")
                all_checks_passed = False
        else:
            print_error("Status checks not required")
            all_checks_passed = False
    except Exception as e:
        print_error(f"Error checking status checks: {e}")
        all_checks_passed = False
    
    # Check enforce admins
    try:
        if protection.enforce_admins.enabled == expected.enforce_admins:
            print_success(f"Enforce admins: {protection.enforce_admins.enabled}")
        else:
            print_warning(
                f"Enforce admins: {protection.enforce_admins.enabled} "
                f"(expected: {expected.enforce_admins})"
            )
            all_checks_passed = False
    except Exception as e:
        print_error(f"Error checking enforce admins: {e}")
        all_checks_passed = False
    
    # Check restrictions
    try:
        restrictions = protection.get_restrictions()
        if restrictions:
            print_success("Push restrictions: enabled")
        else:
            print_warning("Push restrictions: not configured")
            all_checks_passed = False
    except Exception as e:
        # Restrictions might not be available in all plans
        print_info("Push restrictions: not available or not configured")
    
    return all_checks_passed


def verify_workflows(repo) -> bool:
    """Verify that required GitHub Actions workflows exist"""
    print_header("Verifying GitHub Actions Workflows")
    
    required_workflows = [
        ".github/workflows/test.yml",
        ".github/workflows/lint.yml",
        ".github/workflows/property-tests.yml",
        ".github/workflows/documentation.yml",
    ]
    
    all_exist = True
    
    for workflow_path in required_workflows:
        try:
            repo.get_contents(workflow_path)
            print_success(f"Workflow exists: {workflow_path}")
        except GithubException:
            print_error(f"Workflow missing: {workflow_path}")
            all_exist = False
    
    return all_exist


def verify_cla_configuration(repo) -> bool:
    """Verify CLA configuration"""
    print_header("Verifying CLA Configuration")
    
    try:
        repo.get_contents("CLA.md")
        print_success("CLA.md exists")
    except GithubException:
        print_error("CLA.md not found")
        return False
    
    try:
        repo.get_contents(".clabot")
        print_success(".clabot configuration exists")
    except GithubException:
        print_warning(".clabot configuration not found (optional)")
    
    return True


def print_summary(results: Dict[str, bool]) -> None:
    """Print verification summary"""
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print()
    
    if failed == 0:
        print_success("All branch protection checks passed!")
    else:
        print_warning(f"{failed} check(s) failed")
        print_info("See docs/maintainers/branch-protection.md for configuration guide")


def main() -> int:
    """Main verification function"""
    print_header("Aethel Branch Protection Verification")
    
    # Get GitHub client
    client = get_github_client()
    if not client:
        return 1
    
    # Get repository
    try:
        repo = client.get_repo("diotec360/diotec360")
        print_success(f"Repository found: {repo.full_name}")
    except GithubException as e:
        print_error(f"Repository not found: {e}")
        print_info("Update repository name in script if different")
        return 1
    
    # Verify workflows
    workflows_ok = verify_workflows(repo)
    
    # Verify CLA
    cla_ok = verify_cla_configuration(repo)
    
    # Verify branch protections
    results = {
        "workflows": workflows_ok,
        "cla": cla_ok,
    }
    
    for branch_name, expected_config in EXPECTED_CONFIGS.items():
        # For wildcard patterns, check if any matching branches exist
        if "*" in branch_name:
            print_info(f"Skipping wildcard pattern: {branch_name}")
            print_info("Manually verify release branches have protection")
            continue
        
        branch_ok = verify_branch_protection(repo, branch_name, expected_config)
        results[f"branch_{branch_name}"] = branch_ok
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())

