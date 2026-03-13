@echo off
REM ============================================================
REM DIOTEC360 LATTICE V2 - Dual Node com arquivos .env
REM ============================================================

echo.
echo ========================================
echo  DIOTEC360 LATTICE V2 - TWIN NODE
echo ========================================
echo.

REM Criar diretórios
if not exist logs mkdir logs

REM Limpar logs anteriores
if exist logs\nodeA.log del logs\nodeA.log
if exist logs\nodeB.log del logs\nodeB.log

echo [1/6] Verificando dependencias...
pip show python-dotenv >nul 2>&1
if errorlevel 1 (
    echo      Instalando python-dotenv...
    pip install python-dotenv
)
echo      OK - python-dotenv instalado

echo.
echo [2/6] Verificando arquivo .env.nodeA...
if not exist .env.nodeA (
    echo      ERRO: Arquivo .env.nodeA nao encontrado
    pause
    exit /b 1
)
echo      OK - .env.nodeA encontrado

echo.
echo [3/6] Iniciando Node A (porta 8000)...
echo      Usando configuracao: .env.nodeA

REM Copiar .env.nodeA para .env temporariamente
copy /Y .env.nodeA .env >nul

start "Diotec360 Node A" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 > logs\nodeA.log 2>&1"

echo      Aguardando Node A inicializar...
timeout /t 5 /nobreak >nul

REM Aguardar até que o Node A esteja respondendo
:wait_nodeA
curl -s http://127.0.0.1:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_nodeA
)
echo      OK - Node A respondendo

echo.
echo [4/6] Obtendo peer_id do Node A...

REM Aguardar até que peer_id esteja disponível
set RETRY_COUNT=0
:wait_peer_id
set /a RETRY_COUNT+=1
if %RETRY_COUNT% GTR 30 (
    echo      ERRO: peer_id nao disponivel apos 30 tentativas
    echo.
    echo      Verifique logs\nodeA.log
    echo      Procure por mensagens [LATTICE_P2P]
    echo.
    type logs\nodeA.log | findstr /C:"[LATTICE_P2P]"
    pause
    exit /b 1
)

REM Obter peer_id usando PowerShell
for /f "usebackq delims=" %%a in (`powershell -Command "$json = (Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/lattice/p2p/identity' -UseBasicParsing).Content | ConvertFrom-Json; $json.peer_id"`) do set PEER_ID=%%a

REM Verificar se peer_id é válido
if "%PEER_ID%"=="" (
    echo      Tentativa %RETRY_COUNT%: peer_id vazio, aguardando...
    timeout /t 1 /nobreak >nul
    goto wait_peer_id
)

echo %PEER_ID% | findstr /C:"null" >nul
if not errorlevel 1 (
    echo      Tentativa %RETRY_COUNT%: peer_id null, aguardando...
    timeout /t 1 /nobreak >nul
    goto wait_peer_id
)

echo      OK - peer_id: %PEER_ID%

echo.
echo [5/6] Criando .env.nodeB com peer_id...

REM Criar .env.nodeB a partir do template
powershell -Command "(Get-Content .env.nodeB.template) -replace '{PEER_ID}', '%PEER_ID%' | Set-Content .env.nodeB"

echo      OK - .env.nodeB criado

echo.
echo [6/6] Iniciando Node B (porta 8001)...
echo      Usando configuracao: .env.nodeB

REM Copiar .env.nodeB para .env temporariamente
copy /Y .env.nodeB .env >nul

start "Diotec360 Node B" cmd /c "python -m uvicorn api.main:app --host 127.0.0.1 --port 8001 > logs\nodeB.log 2>&1"

echo      Aguardando Node B inicializar...
timeout /t 5 /nobreak >nul

REM Aguardar até que o Node B esteja respondendo
:wait_nodeB
curl -s http://127.0.0.1:8001/health >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_nodeB
)
echo      OK - Node B respondendo

echo.
echo ========================================
echo  LATTICE ATIVADA
echo ========================================
echo.
echo Node A: http://127.0.0.1:8000
echo Node B: http://127.0.0.1:8001
echo.
echo Logs:
echo   - logs\nodeA.log
echo   - logs\nodeB.log
echo.
echo Verificando logs do P2P...
echo.
echo === Node A ===
type logs\nodeA.log | findstr /C:"[LATTICE_P2P]"
echo.
echo === Node B ===
type logs\nodeB.log | findstr /C:"[LATTICE_P2P]"
echo.
echo Pressione Ctrl+C para encerrar
pause
