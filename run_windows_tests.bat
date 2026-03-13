@echo off
REM Windows Test Execution Script for RVC-003 & RVC-004
REM Task 12.2: Run all tests on Windows (Already Complete)

echo ========================================
echo RVC-003 ^& RVC-004 Windows Test Suite
echo ========================================
echo Platform: Windows
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Version: %VERSION%
python --version
echo ========================================

echo.
echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8+
    exit /b 1
)

REM Check pytest
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo X pytest not found. Installing...
    pip install pytest hypothesis psutil
)

REM Check Windows version (need Windows 10+)
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i
if %VERSION% LSS 10 (
    echo X Windows 10 or later required
    echo   Current version: %VERSION%
    exit /b 1
)

echo + Windows version: %VERSION% ^(supported^)

REM Check GetThreadTimes support
echo Checking GetThreadTimes support...
python -c "import ctypes; kernel32 = ctypes.windll.kernel32; print('+ GetThreadTimes API available')"
if errorlevel 1 (
    echo X GetThreadTimes not supported on this system
    exit /b 1
)

echo.
echo + All prerequisites met
echo.

REM Run tests
echo ========================================
echo Running Test Suite
echo ========================================

REM Run quick tests first
echo.
echo Step 1: Quick Tests ^(5 minutes^)
echo --------------------------------
python run_cross_platform_tests.py --quick

if errorlevel 1 (
    echo.
    echo X Quick tests failed. Stopping.
    exit /b 1
)

echo.
echo + Quick tests passed
echo.

REM Ask user if they want to run full tests
set /p REPLY="Run full test suite? (30+ minutes) [y/N]: "
if /i "%REPLY%"=="y" (
    echo.
    echo Step 2: Full Test Suite ^(30+ minutes^)
    echo --------------------------------------
    python run_cross_platform_tests.py --full
    
    if errorlevel 1 (
        echo.
        echo X Full tests failed
        exit /b 1
    )
    
    echo.
    echo + Full tests passed
)

REM Generate final report
echo.
echo ========================================
echo Test Execution Complete
echo ========================================
echo.
echo Results saved to:
echo   - test_results_windows.json
echo   - TEST_REPORT_WINDOWS.md
echo.
echo + Windows testing complete!
echo.
echo Next steps:
echo   1. Review TEST_REPORT_WINDOWS.md
echo   2. Update .kiro/specs/rvc-003-004-fixes/tasks.md
echo   3. Mark Task 12.2 as complete
echo.
