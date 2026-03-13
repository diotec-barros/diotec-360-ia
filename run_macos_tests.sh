#!/bin/bash
# macOS Test Execution Script for RVC-003 & RVC-004
# Task 12.3: Run all tests on macOS

set -e  # Exit on error

echo "========================================"
echo "RVC-003 & RVC-004 macOS Test Suite"
echo "========================================"
echo "Platform: $(uname -s)"
echo "Version: $(sw_vers -productVersion)"
echo "Python: $(python3 --version)"
echo "========================================"

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check pytest
if ! python3 -c "import pytest" 2>/dev/null; then
    echo "❌ pytest not found. Installing..."
    pip3 install pytest hypothesis psutil
fi

# Check macOS version (need 10.14+)
macos_version=$(sw_vers -productVersion | cut -d. -f1,2)
macos_major=$(echo $macos_version | cut -d. -f1)
macos_minor=$(echo $macos_version | cut -d. -f2)

if [ "$macos_major" -lt 10 ] || ([ "$macos_major" -eq 10 ] && [ "$macos_minor" -lt 14 ]); then
    echo "❌ macOS 10.14 (Mojave) or later required"
    echo "   Current version: $macos_version"
    exit 1
fi

echo "✅ macOS version: $macos_version (supported)"

# Check thread_info support
echo "Checking thread_info support..."
python3 -c "
import ctypes
import ctypes.util

# Try to load libsystem_kernel
libsystem = ctypes.CDLL(ctypes.util.find_library('System'))

# Check if thread_info is available
try:
    thread_info = libsystem.thread_info
    print('✅ thread_info API available')
except AttributeError:
    print('❌ thread_info API not available')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ thread_info not supported on this system"
    exit 1
fi

echo ""
echo "✅ All prerequisites met"
echo ""

# Run tests
echo "========================================"
echo "Running Test Suite"
echo "========================================"

# Run quick tests first
echo ""
echo "Step 1: Quick Tests (5 minutes)"
echo "--------------------------------"
python3 run_cross_platform_tests.py --quick

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Quick tests failed. Stopping."
    exit 1
fi

echo ""
echo "✅ Quick tests passed"
echo ""

# Ask user if they want to run full tests
read -p "Run full test suite? (30+ minutes) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Step 2: Full Test Suite (30+ minutes)"
    echo "--------------------------------------"
    python3 run_cross_platform_tests.py --full
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Full tests failed"
        exit 1
    fi
    
    echo ""
    echo "✅ Full tests passed"
fi

# Generate final report
echo ""
echo "========================================"
echo "Test Execution Complete"
echo "========================================"
echo ""
echo "Results saved to:"
echo "  - test_results_macos.json"
echo "  - TEST_REPORT_MACOS.md"
echo ""
echo "✅ macOS testing complete!"
echo ""
echo "Next steps:"
echo "  1. Review TEST_REPORT_MACOS.md"
echo "  2. Update .kiro/specs/rvc-003-004-fixes/tasks.md"
echo "  3. Mark Task 12.3 as complete"
echo ""
