#!/usr/bin/env python3
"""
Setup Pre-Commit Hooks for Diotec360

This script installs and configures pre-commit hooks for the Diotec360 repository.
Pre-commit hooks help maintain code quality by running automated checks before
each commit.

Usage:
    python scripts/setup_pre_commit.py

Features:
    - Installs pre-commit package if not already installed
    - Configures pre-commit hooks from .pre-commit-config.yaml
    - Creates .secrets.baseline for detect-secrets
    - Validates hook configuration
    - Provides troubleshooting guidance

Copyright © 2024-2026 DIOTEC 360
Licensed under Apache 2.0
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(message: str) -> None:
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print an error message"""
    print(f"❌ {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print an info message"""
    print(f"ℹ️  {message}")


def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_git_repository() -> bool:
    """Check if current directory is a git repository"""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            check=True,
            capture_output=True,
            text=True
        )
        print_success("Git repository detected")
        return True
    except subprocess.CalledProcessError:
        print_error("Not a git repository. Please run from repository root.")
        return False


def install_pre_commit() -> bool:
    """Install pre-commit package if not already installed"""
    try:
        # Check if pre-commit is already installed
        result = subprocess.run(
            ["pre-commit", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success(f"pre-commit already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    # Install pre-commit
    print_info("Installing pre-commit package...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pre-commit"],
            check=True,
            capture_output=True
        )
        print_success("pre-commit package installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install pre-commit: {e}")
        return False


def create_secrets_baseline() -> bool:
    """Create .secrets.baseline file for detect-secrets"""
    baseline_file = Path(".secrets.baseline")
    
    if baseline_file.exists():
        print_success(".secrets.baseline already exists")
        return True
    
    print_info("Creating .secrets.baseline file...")
    try:
        subprocess.run(
            ["detect-secrets", "scan", "--baseline", ".secrets.baseline"],
            check=True,
            capture_output=True
        )
        print_success(".secrets.baseline created")
        return True
    except FileNotFoundError:
        print_info("detect-secrets not installed, will be installed by pre-commit")
        # Create empty baseline
        baseline_file.write_text("{}\n")
        print_success("Empty .secrets.baseline created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create .secrets.baseline: {e}")
        return False


def install_hooks() -> bool:
    """Install pre-commit hooks"""
    print_info("Installing pre-commit hooks...")
    try:
        subprocess.run(
            ["pre-commit", "install"],
            check=True,
            capture_output=True
        )
        print_success("Pre-commit hooks installed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install hooks: {e}")
        return False


def validate_config() -> bool:
    """Validate pre-commit configuration"""
    config_file = Path(".pre-commit-config.yaml")
    
    if not config_file.exists():
        print_error(".pre-commit-config.yaml not found")
        return False
    
    print_success(".pre-commit-config.yaml found")
    
    # Validate configuration
    print_info("Validating pre-commit configuration...")
    try:
        subprocess.run(
            ["pre-commit", "validate-config"],
            check=True,
            capture_output=True
        )
        print_success("Configuration is valid")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Configuration validation failed: {e}")
        return False


def run_sample_check() -> bool:
    """Run pre-commit on a sample file to test installation"""
    print_info("Running sample check on README.md...")
    try:
        result = subprocess.run(
            ["pre-commit", "run", "--files", "README.md"],
            capture_output=True,
            text=True
        )
        # pre-commit returns non-zero if hooks make changes or fail
        # We just want to verify it runs without errors
        if "error" in result.stderr.lower():
            print_error(f"Sample check encountered errors: {result.stderr}")
            return False
        print_success("Sample check completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Sample check failed: {e}")
        return False


def print_usage_guide() -> None:
    """Print usage guide for pre-commit hooks"""
    print_header("Pre-Commit Hooks Usage Guide")
    
    print("📝 Automatic Usage:")
    print("   Hooks run automatically on 'git commit'")
    print("   If hooks fail, commit is aborted")
    print("   Fix issues and commit again")
    print()
    
    print("🔧 Manual Usage:")
    print("   Run on all files:     pre-commit run --all-files")
    print("   Run specific hook:    pre-commit run <hook-id>")
    print("   Skip hooks:           git commit --no-verify")
    print()
    
    print("🔄 Maintenance:")
    print("   Update hooks:         pre-commit autoupdate")
    print("   Clean cache:          pre-commit clean")
    print("   Uninstall:            pre-commit uninstall")
    print()
    
    print("📋 Configured Hooks:")
    print("   ✓ black          - Python code formatting")
    print("   ✓ isort          - Python import sorting")
    print("   ✓ flake8         - Python linting")
    print("   ✓ mypy           - Python type checking")
    print("   ✓ pytest         - Fast unit tests")
    print("   ✓ bandit         - Security checks")
    print("   ✓ detect-secrets - Secret detection")
    print("   ✓ markdownlint   - Markdown linting")
    print("   ✓ copyright      - Copyright header validation")
    print("   ✓ validate-docs  - Documentation structure validation")
    print()
    
    print("💡 Tips:")
    print("   - Hooks run only on staged files")
    print("   - Some hooks auto-fix issues (black, isort, trailing-whitespace)")
    print("   - Review changes after auto-fixes before committing")
    print("   - Use --no-verify sparingly (only for emergencies)")
    print()


def print_troubleshooting() -> None:
    """Print troubleshooting guide"""
    print_header("Troubleshooting")
    
    print("❓ Hooks not running?")
    print("   → Check: git config core.hooksPath")
    print("   → Should be empty or .git/hooks")
    print("   → Fix: git config --unset core.hooksPath")
    print()
    
    print("❓ Hook fails with 'command not found'?")
    print("   → Install missing tool: pip install <tool-name>")
    print("   → Or update hooks: pre-commit autoupdate")
    print()
    
    print("❓ Hooks too slow?")
    print("   → Skip slow hooks: SKIP=pytest-fast git commit")
    print("   → Or run specific hooks: pre-commit run <hook-id>")
    print()
    
    print("❓ Need to bypass hooks temporarily?")
    print("   → Use: git commit --no-verify")
    print("   → WARNING: Only for emergencies!")
    print()
    
    print("❓ Want to run hooks manually?")
    print("   → All files: pre-commit run --all-files")
    print("   → Staged files: pre-commit run")
    print()


def main() -> int:
    """Main setup function"""
    print_header("Diotec360 Pre-Commit Hooks Setup")
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_git_repository():
        return 1
    
    # Install pre-commit
    if not install_pre_commit():
        return 1
    
    # Validate configuration
    if not validate_config():
        return 1
    
    # Create secrets baseline
    if not create_secrets_baseline():
        print_info("Continuing without .secrets.baseline (will be created on first run)")
    
    # Install hooks
    if not install_hooks():
        return 1
    
    # Run sample check
    if not run_sample_check():
        print_info("Sample check had issues, but hooks are installed")
    
    # Print usage guide
    print_usage_guide()
    
    # Print troubleshooting
    print_troubleshooting()
    
    # Success
    print_header("Setup Complete!")
    print_success("Pre-commit hooks are now active")
    print_info("Hooks will run automatically on 'git commit'")
    print_info("Run 'pre-commit run --all-files' to check all files now")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
