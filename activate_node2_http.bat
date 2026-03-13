@echo off
REM HTTP-Only Activation Script for Node 2 (Primary Genesis Node)
REM DIOTEC360 REAL LATTICE v3.0.4 - HTTP Resilience Mode

echo ========================================
echo DIOTEC360 TRIANGLE - NODE 2 HTTP ACTIVATION
echo ========================================
echo.
echo [INFO] Activating Primary Genesis Node (HTTP-Only Mode)
echo [INFO] P2P is DISABLED by design - HTTP Sync is the foundation
echo.

REM Copy HTTP-Only configuration
echo [STEP 1] Loading HTTP-Only configuration...
copy /Y .env.node2.diotec360 .env
if errorlevel 1 (
    echo [ERROR] Failed to copy configuration file
    pause
    exit /b 1
)
echo [OK] HTTP-Only configuration loaded
echo.

REM Display configuration
echo [STEP 2] Configuration Summary:
echo   - Node Name: node2-diotec360
echo   - Role: genesis-primary
echo   - Mode: HTTP-ONLY RESILIENCE
echo   - P2P: DISABLED (by design)
echo   - HTTP Sync: ENABLED
echo   - Peer Nodes: 2 (Hugging Face + Backup)
echo   - Heartbeat: 5s interval
echo   - HTTP Poll: 10s interval
echo.

REM Start the server
echo [STEP 3] Starting Diotec360 API Server (HTTP-Only Mode)...
echo [INFO] System will use HTTP Sync for all synchronization
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ========================================
echo SERVER OUTPUT:
echo ========================================
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

echo.
echo ========================================
echo [INFO] Server stopped
echo ========================================
pause
