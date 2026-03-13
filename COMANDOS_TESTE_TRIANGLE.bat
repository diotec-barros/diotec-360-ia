@echo off
REM Quick Test Commands for Triangle of Truth
REM Run these commands to verify the deployment

echo ========================================
echo DIOTEC360 TRIANGLE OF TRUTH - QUICK TESTS
echo ========================================
echo.

echo [1/5] Testing Node 2 (Sovereign API)...
curl -s https://api.diotec360.com/health
echo.
echo.

echo [2/5] Testing Node 1 (Hugging Face)...
curl -s https://diotec-diotec360-judge.hf.space/health
echo.
echo.

echo [3/5] Testing Node 3 (Vercel Backup)...
curl -s https://backup.diotec360.com/health
echo.
echo.

echo [4/5] Testing Frontend...
curl -s -I https://aethel.diotec360.com/ | findstr "HTTP"
echo.
echo.

echo [5/5] Running Full Triangle Verification...
python verify_production_triangle.py
echo.

echo ========================================
echo TESTS COMPLETE
echo ========================================
echo.
echo Next: Open https://aethel.diotec360.com/ in your browser
echo.
pause
