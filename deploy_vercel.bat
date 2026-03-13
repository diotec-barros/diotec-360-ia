@echo off
REM ========================================
REM Aethel Studio - Vercel Deployment
REM ========================================

echo.
echo ========================================
echo   AETHEL STUDIO - VERCEL DEPLOYMENT
echo ========================================
echo.

echo [1/5] Checking git status...
git status

echo.
echo [2/5] Adding all files to git...
git add .

echo.
echo [3/5] Committing changes...
git commit -m "feat: Deploy Aethel Studio v3.0.5 to Vercel with Triangle backend"

if errorlevel 1 (
    echo No changes to commit or commit failed
    echo Continuing with push...
)

echo.
echo [4/5] Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed!
    echo.
    echo Please check:
    echo   1. Git remote is configured
    echo   2. You have push permissions
    echo   3. Branch name is correct
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] Opening Vercel deployment guide...
echo.
echo ========================================
echo   GIT PUSH SUCCESSFUL!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Go to https://vercel.com
echo 2. Click "Add New Project"
echo 3. Import your GitHub repository
echo 4. Configure:
echo    - Root Directory: frontend
echo    - Framework: Next.js
echo    - Environment Variables:
echo      * NEXT_PUBLIC_API_URL=https://api.diotec360.com
echo      * NEXT_PUBLIC_LATTICE_NODES=https://diotec-aethel.hf.space,https://backup.diotec360.com
echo 5. Click "Deploy"
echo.
echo Your Aethel Studio will be live in 2-3 minutes!
echo.
echo Full guide: VERCEL_DEPLOY_GUIDE.md
echo.
pause
