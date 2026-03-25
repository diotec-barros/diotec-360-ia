@echo off
echo.
echo ========================================
echo   DIOTEC 360 SDK - NPM Publisher
echo   "Integrity as a Service"
echo ========================================
echo.

echo [Step 1/5] Checking NPM login status...
call npm whoami
if errorlevel 1 (
    echo.
    echo You need to login to NPM first.
    echo Run: npm login
    echo.
    pause
    exit /b 1
)

echo.
echo [Step 2/5] Running tests...
call node test-sdk.js
if errorlevel 1 (
    echo.
    echo Tests failed! Fix errors before publishing.
    pause
    exit /b 1
)

echo.
echo [Step 3/5] Creating package tarball...
call npm pack

echo.
echo [Step 4/5] Package contents:
dir /b *.tgz

echo.
echo [Step 5/5] Ready to publish!
echo.
set /p CONFIRM="Publish @diotec360/sdk to NPM? (y/n): "
if /i "%CONFIRM%"=="y" (
    echo.
    echo Publishing...
    call npm publish --access public
    echo.
    echo ========================================
    echo   SUCCESS! SDK Published to NPM
    echo ========================================
    echo.
    echo Install anywhere with:
    echo   npm install @diotec360/sdk
    echo.
    echo View at:
    echo   https://www.npmjs.com/package/@diotec360/sdk
    echo.
) else (
    echo.
    echo Publication cancelled.
    echo.
)

pause
