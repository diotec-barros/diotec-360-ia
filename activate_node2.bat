@echo off
REM Activation Script for Node 2 (Primary Genesis Node)
REM DIOTEC360 REAL LATTICE v3.0.4

echo ========================================
echo DIOTEC360 REAL LATTICE - NODE 2 ACTIVATION
echo ========================================
echo.
echo [INFO] Activating Primary Genesis Node
echo [INFO] This will start Node 2 with production configuration
echo.

REM Copy production config
echo [STEP 1] Loading production configuration...
copy /Y .env.node2.diotec360 .env
if errorlevel 1 (
    echo [ERROR] Failed to copy configuration file
    pause
    exit /b 1
)
echo [OK] Configuration loaded: .env.node2.diotec360
echo.

REM Display configuration
echo [STEP 2] Configuration Summary:
echo   - Node Name: node2-diotec360
echo   - Role: genesis-primary
echo   - P2P Port: 9000
echo   - API Port: 8000
echo   - Heartbeat: 5s interval, 60s timeout
echo.

REM Start the server
echo [STEP 3] Starting Diotec360 API Server...
echo [INFO] Watch for Peer ID in the output below
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
