@echo off
REM ============================================================================
REM DIOTEC 360 IA - Teste Rápido de Conexão P2P com Manhattan
REM ============================================================================
REM 
REM Este script testa a conectividade com o relay público de Manhattan
REM e valida a sincronização P2P da rede Lattice.
REM 
REM Desenvolvido por: Kiro para Dionísio Sebastião Barros
REM Data: 25 de Março de 2026
REM ============================================================================

echo.
echo ========================================
echo   DIOTEC 360 IA - Teste P2P Manhattan
echo ========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "diotec360" (
    echo [ERRO] Execute este script na raiz do projeto!
    echo.
    pause
    exit /b 1
)

echo [1/4] Verificando conectividade com Manhattan...
echo.

REM Testar conexão com curl
curl -I https://gun-manhattan.herokuapp.com/gun 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] curl nao encontrado ou relay offline
    echo Tentando com PowerShell...
    powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://gun-manhattan.herokuapp.com/gun' -Method Head -UseBasicParsing; Write-Host '[OK] Relay Manhattan operacional!' -ForegroundColor Green } catch { Write-Host '[ERRO] Relay offline ou inacessivel' -ForegroundColor Red }"
) else (
    echo [OK] Relay Manhattan operacional!
)

echo.
echo [2/4] Verificando configuracao do .env...
echo.

REM Verificar se GUNDB_RELAY_URL está configurado
findstr /C:"GUNDB_RELAY_URL=https://gun-manhattan.herokuapp.com/gun" diotec360\.env >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend configurado para Manhattan
) else (
    echo [AVISO] Backend pode nao estar configurado corretamente
)

findstr /C:"NEXT_PUBLIC_GUNDB_RELAY=https://gun-manhattan.herokuapp.com/gun" diotec360\frontend\.env.local >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend configurado para Manhattan
) else (
    echo [AVISO] Frontend pode nao estar configurado corretamente
)

echo.
echo [3/4] Executando teste Python...
echo.

cd diotec360

REM Verificar se Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.8+ e tente novamente.
    cd ..
    pause
    exit /b 1
)

REM Executar script de teste
if exist "scripts\test_p2p_relay_v10.0.9.py" (
    echo Executando test_p2p_relay_v10.0.9.py...
    python scripts\test_p2p_relay_v10.0.9.py
) else (
    echo [AVISO] Script de teste nao encontrado
    echo Pulando teste Python...
)

cd ..

echo.
echo [4/4] Resumo do Teste
echo.
echo ========================================
echo   RESULTADO DO TESTE P2P
echo ========================================
echo.
echo Se voce viu mensagens de sucesso acima:
echo   [OK] Relay Manhattan esta acessivel
echo   [OK] Configuracao esta correta
echo   [OK] Rede Lattice pronta para uso
echo.
echo Proximos passos:
echo   1. Desenvolver com Logic Miner + P2P
echo   2. Demonstrar para investidores
echo   3. Migrar para relay soberano em 30 dias
echo.
echo ========================================
echo   A LATTICE RESPIRA
echo ========================================
echo.

pause
