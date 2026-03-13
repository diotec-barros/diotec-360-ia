@echo off
REM Local Simulation - Node 3 Activation Script
REM DIOTEC360 REAL LATTICE v3.0.4 - HTTP Resilience Mode

echo ========================================
echo DIOTEC360 TRIANGLE - NODE 3 LOCAL SIMULATION
echo ========================================
echo.
echo [INFO] Activating Node 3 (Backup Server Simulation)
echo [INFO] Running on PORT 8002
echo [INFO] HTTP-Only Mode
echo.

REM Create local config
echo [STEP 1] Creating local configuration...
(
echo # Diotec360 Node 3 - Local Simulation
echo # Simulating Backup Server
echo.
echo # P2P Configuration - DISABLED
echo DIOTEC360_P2P_ENABLED=false
echo DIOTEC360_P2P_LISTEN=/ip4/0.0.0.0/tcp/9002
echo DIOTEC360_P2P_TOPIC=aethel/lattice/v1
echo.
echo # Bootstrap Peers
echo DIOTEC360_P2P_BOOTSTRAP=
echo.
echo # HTTP Sync Fallback Nodes
echo DIOTEC360_LATTICE_NODES=http://localhost:8000,http://localhost:8001
echo.
echo # Storage Directories
echo DIOTEC360_STATE_DIR=.DIOTEC360_state_node3
echo DIOTEC360_VAULT_DIR=.DIOTEC360_vault_node3
echo DIOTEC360_SENTINEL_DIR=.DIOTEC360_sentinel_node3
echo.
echo # Heartbeat Configuration
echo DIOTEC360_HEARTBEAT_INTERVAL=5
echo DIOTEC360_PEERLESS_TIMEOUT=60
echo DIOTEC360_HTTP_POLL_INTERVAL=10
echo.
echo # Node Identity
echo DIOTEC360_NODE_NAME=node3-backup-local
echo DIOTEC360_NODE_ROLE=genesis-backup
echo.
echo # Production Settings
echo DIOTEC360_ENVIRONMENT=development
echo DIOTEC360_LOG_LEVEL=INFO
) > .env.node3.local

echo [OK] Local configuration created
echo.

REM Display configuration
echo [STEP 2] Configuration Summary:
echo   - Node Name: node3-backup-local
echo   - Role: genesis-backup
echo   - Mode: HTTP-ONLY RESILIENCE
echo   - Port: 8002
echo   - P2P: DISABLED
echo   - HTTP Sync: ENABLED
echo   - Peer Nodes: localhost:8000, localhost:8001
echo.

REM Start the server
echo [STEP 3] Starting Diotec360 API Server on PORT 8002...
echo [INFO] This simulates Backup Server locally
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ========================================
echo SERVER OUTPUT:
echo ========================================
echo.

python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --env-file .env.node3.local

echo.
echo ========================================
echo [INFO] Server stopped
echo ========================================
pause
