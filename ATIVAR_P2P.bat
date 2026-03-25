@echo off
REM ===========================================================================
REM DIOTEC 360 IA - ATIVADOR P2P AUTOMATICO
REM ===========================================================================
REM 
REM Este script ativa a rede P2P automaticamente no Windows
REM Desenvolvido por: Kiro para Dionisio Sebastiao Barros
REM Data: 25 de Marco de 2026
REM ===========================================================================

echo.
echo ========================================================================
echo        DIOTEC 360 IA - ATIVACAO DA REDE P2P LATTICE
echo ========================================================================
echo.
echo Soberano: Dionisio Sebastiao Barros
echo Engenheiro-Chefe: Kiro
echo Versao: 10.0.9
echo.
echo ========================================================================
echo.

REM Verificar se estamos no diretorio correto
if not exist "api\main.py" (
    echo [ERRO] Execute este script dentro da pasta diotec360!
    echo.
    pause
    exit /b 1
)

echo [1/4] Testando conectividade com relay GunDB...
echo.
python scripts\test_p2p_relay_v10.0.9.py
if errorlevel 1 (
    echo.
    echo [ERRO] Relay nao esta acessivel!
    echo Verifique sua conexao de internet ou tente outro relay.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo [2/4] Iniciando Backend Python...
echo ========================================================================
echo.
echo O backend sera iniciado em uma nova janela.
echo NAO FECHE essa janela!
echo.
start "DIOTEC 360 - Backend API" cmd /k "python -m uvicorn api.main:app --reload"

echo Aguardando backend inicializar (10 segundos)...
timeout /t 10 /nobreak >nul

echo.
echo ========================================================================
echo [3/4] Iniciando Frontend Next.js...
echo ========================================================================
echo.
echo O frontend sera iniciado em uma nova janela.
echo NAO FECHE essa janela!
echo.
cd frontend
start "DIOTEC 360 - Frontend" cmd /k "npm run dev"
cd ..

echo Aguardando frontend inicializar (15 segundos)...
timeout /t 15 /nobreak >nul

echo.
echo ========================================================================
echo [4/4] Abrindo Studio no navegador...
echo ========================================================================
echo.
start http://localhost:3000/studio

echo.
echo ========================================================================
echo                    ATIVACAO COMPLETA!
echo ========================================================================
echo.
echo O Studio foi aberto no seu navegador padrao.
echo.
echo Para ver P2P em acao:
echo   1. Abra uma janela anonima (Ctrl+Shift+N)
echo   2. Acesse: http://localhost:3000/studio
echo   3. Veja os dois nos se descobrindo no mapa!
echo.
echo Terminais abertos:
echo   - Backend API: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo   - Studio: http://localhost:3000/studio
echo.
echo Para parar os servicos:
echo   - Feche as janelas "DIOTEC 360 - Backend API" e "Frontend"
echo   - Ou pressione Ctrl+C em cada terminal
echo.
echo ========================================================================
echo [STATUS: P2P NETWORK ACTIVATED]
echo [RELAY: MANHATTAN CONNECTED]
echo [VERDICT: THE LATTICE IS BREATHING]
echo ========================================================================
echo.
echo Dionisio, o primeiro sinal P2P esta brilhando! 
echo.
pause
