@echo off
chcp 65001 >nul
echo ========================================
echo 🧪 TESTANDO Diotec360 v1.1
echo ========================================
echo.

echo [1/5] 🔍 Testando DNS...
echo.
nslookup api.diotec360.com
echo.
timeout /t 2 >nul

echo [2/5] 🏥 Testando Backend Health...
echo.
curl -s https://api.diotec360.com/health
echo.
echo.
timeout /t 2 >nul

echo [3/5] 📋 Testando Examples...
echo.
curl -s https://api.diotec360.com/api/examples
echo.
echo.
timeout /t 2 >nul

echo [4/5] ✅ Testando Verify...
echo.
curl -s -X POST https://api.diotec360.com/api/verify -H "Content-Type: application/json" -d "{\"code\":\"intent test() { verify { true; } }\"}"
echo.
echo.
timeout /t 2 >nul

echo [5/5] 🌐 Abrindo Frontend...
echo.
start https://aethel.diotec360.com
echo Frontend aberto no navegador!
echo.

echo ========================================
echo ✅ TESTES CONCLUIDOS!
echo ========================================
echo.
echo Verifique:
echo - Backend respondeu? (JSON acima)
echo - Frontend carregou? (navegador)
echo - SSL ativo? (cadeado verde)
echo.
pause
