@echo off
REM Deploy Node 3 (Backup) to Vercel
REM Diotec360 v3.0.5 - Production Deployment

echo ========================================
echo Diotec360 Node 3 - VERCEL DEPLOYMENT
echo ========================================
echo.

echo [STEP 1] Checking Vercel CLI...
where vercel >nul 2>&1
if %errorlevel% neq 0 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Vercel CLI
        echo Please install manually: npm install -g vercel
        pause
        exit /b 1
    )
)
echo ✓ Vercel CLI found

echo.
echo [STEP 2] Verifying configuration files...
if not exist "vercel.json" (
    echo ERROR: vercel.json not found
    pause
    exit /b 1
)
if not exist "requirements-vercel.txt" (
    echo ERROR: requirements-vercel.txt not found
    pause
    exit /b 1
)
if not exist ".env.node3.backup" (
    echo ERROR: .env.node3.backup not found
    pause
    exit /b 1
)
echo ✓ Configuration files found

echo.
echo [STEP 3] Copying environment file...
copy /Y .env.node3.backup .env
echo ✓ Environment configured

echo.
echo [STEP 4] Deploying to Vercel...
echo.
echo IMPORTANT: When prompted:
echo   - Project name: aethel-backup
echo   - Framework: Other
echo   - Build command: (leave empty)
echo   - Output directory: (leave empty)
echo.
pause

vercel --prod
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Deployment failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ DEPLOYMENT COMPLETE
echo ========================================
echo.
echo Next steps:
echo 1. Configure custom domain in Vercel dashboard
echo 2. Add backup.diotec360.com to your project
echo 3. Wait for DNS propagation (2-5 minutes)
echo 4. Run: python verify_production_triangle.py
echo.
echo Vercel Dashboard: https://vercel.com/dashboard
echo.
pause
