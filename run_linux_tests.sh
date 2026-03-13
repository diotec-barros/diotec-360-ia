#!/bin/bash
# Linux Test Execution Script for RVC-003 & RVC-004
# Task 12.1: Run all tests on Linux

set -e  # Exit on error

echo "========================================"
echo "RVC-003 & RVC-004 Linux Test Suite"
echo "========================================"
echo "Platform: $(uname -s)"
echo "Kernel: $(uname -r)"
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

# Check pthread support
echo "Checking pthread support..."
if ! python3 -c "import ctypes; ctypes.CDLL('libpthread.so.0')" 2>/dev/null; then
    echo "⚠️  Warning: libpthread not found. Some tests may fail."
fi

# Check thread CPU time support
echo "Checking thread CPU time support..."
python3 -c "
import time
try:
    clock_id = time.CLOCK_THREAD_CPUTIME_ID
    print('✅ CLOCK_THREAD_CPUTIME_ID supported')
except AttributeError:
    print('❌ CLOCK_THREAD_CPUTIME_ID not supported')
    print('   Your kernel may be too old for thread CPU time tracking')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Thread CPU time not supported on this system"
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
echo "  - test_results_linux.json"
echo "  - TEST_REPORT_LINUX.md"
echo ""
echo "✅ Linux testing complete!"
echo ""
echo "Next steps:"
echo "  1. Review TEST_REPORT_LINUX.md"
echo "  2. Update .kiro/specs/rvc-003-004-fixes/tasks.md"
echo "  3. Mark Task 12.1 as complete"
echo ""
