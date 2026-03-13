@echo off
REM ============================================================
REM DIOTEC360 LATTICE TEST - Dual Node Gossip Protocol
REM ============================================================

echo.
echo ========================================
echo  DIOTEC360 LATTICE - TWIN NODE ACTIVATION
echo ========================================
echo.

REM Criar diretórios de logs
if not exist logs mkdir logs

REM Limpar logs anteriores
if exist logs\nodeA.log del logs\nodeA.log
if exist logs\nodeB.log del logs\nodeB.log

echo [1/5] Instalando dependencias...
pip install -r api\requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)
echo      OK - Dependencias instaladas

echo.
echo [2/5] Iniciando Node A (porta 8000)...
set DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeA
set DIOTEC360_VAULT_DIR=.DIOTEC360_vault_nodeA
set DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_nodeA
set DIOTEC360_P2P_ENABLED=true
set DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9000
set DIOTEC360_P2P_TOPIC=aethel/lattice/v1
set DIOTEC360_P2P_BOOTSTRAP=
set DIOTEC360_LATTICE_NODES=

start "Diotec360 Node A" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 > logs\nodeA.log 2>&1"

echo      Aguardando Node A inicializar...
timeout /t 3 /nobreak >nul

REM Aguardar até que o Node A esteja respondendo
:wait_nodeA
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_nodeA
)
echo      OK - Node A respondendo

echo.
echo [3/5] Obtendo identidade do Node A...

REM Aguardar até que peer_id esteja disponível (máximo 20 tentativas)
set RETRY_COUNT=0
:wait_peer_id
set /a RETRY_COUNT+=1
if %RETRY_COUNT% GTR 20 (
    echo      ERRO: peer_id nao disponivel apos 20 tentativas
    echo      Verifique logs\nodeA.log para detalhes
    pause
    exit /b 1
)

REM Obter peer_id
for /f "tokens=*" %%i in ('curl -s http://127.0.0.1:8000/api/lattice/p2p/identity') do set IDENTITY_JSON=%%i

REM Verificar se peer_id está presente e não é null
echo %IDENTITY_JSON% | findstr /C:"\"peer_id\":null" >nul
if not errorlevel 1 (
    echo      Tentativa %RETRY_COUNT%: peer_id ainda null, aguardando...
    timeout /t 1 /nobreak >nul
    goto wait_peer_id
)

echo %IDENTITY_JSON% | findstr /C:"\"peer_id\":\"" >nul
if errorlevel 1 (
    echo      Tentativa %RETRY_COUNT%: peer_id nao encontrado, aguardando...
    timeout /t 1 /nobreak >nul
    goto wait_peer_id
)

REM Extrair peer_id (método simplificado para Windows)
REM Usar PowerShell para parsing JSON confiável
for /f "usebackq delims=" %%a in (`powershell -Command "$json = '%IDENTITY_JSON%' | ConvertFrom-Json; $json.peer_id"`) do set PEER_ID=%%a

if "%PEER_ID%"=="" (
    echo      Tentativa %RETRY_COUNT%: peer_id vazio, aguardando...
    timeout /t 1 /nobreak >nul
    goto wait_peer_id
)

echo      OK - peer_id: %PEER_ID%

REM Construir multiaddr de bootstrap
set BOOTSTRAP_ADDR=/ip4/127.0.0.1/tcp/9000/p2p/%PEER_ID%
echo      Bootstrap: %BOOTSTRAP_ADDR%

echo.
echo [4/5] Iniciando Node B (porta 8001)...
set DIOTEC360_STATE_DIR=.DIOTEC360_state_nodeB
set DIOTEC360_VAULT_DIR=.DIOTEC360_vault_nodeB
set DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_nodeB
set DIOTEC360_P2P_ENABLED=true
set DIOTEC360_P2P_LISTEN=/ip4/127.0.0.1/tcp/9001
set DIOTEC360_P2P_TOPIC=aethel/lattice/v1
set DIOTEC360_P2P_BOOTSTRAP=%BOOTSTRAP_ADDR%
set DIOTEC360_LATTICE_NODES=http://127.0.0.1:8000

start "Diotec360 Node B" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 > logs\nodeB.log 2>&1"

echo      Aguardando Node B inicializar...
timeout /t 3 /nobreak >nul

REM Aguardar até que o Node B esteja respondendo
:wait_nodeB
curl -s http://127.0.0.1:8001/health >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_nodeB
)
echo      OK - Node B respondendo

echo.
echo [5/5] Executando teste de gossip...
timeout /t 2 /nobreak >nul

python test_lattice_gossip_flow.py

echo.
echo ========================================
echo  LATTICE ATIVADA - Monitoramento
echo ========================================
echo.
echo Node A: http://127.0.0.1:8000
echo Node B: http://127.0.0.1:8001
echo.
echo Logs:
echo   - logs\nodeA.log
echo   - logs\nodeB.log
echo.
echo Pressione Ctrl+C para encerrar os nos
echo.

REM Manter o script rodando para monitorar logs
:monitor
timeout /t 5 /nobreak >nul
echo [%TIME%] Lattice ativa - Nodes rodando...
goto monitor
