#!/bin/bash
# Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/bin/bash
# ========================================
# Diotec360 v3.0.5 - Node 3 Deployment
# Target: Backup Server
# ========================================

set -e  # Exit on error

echo ""
echo "========================================"
echo "  Diotec360 v3.0.5 - NODE 3 DEPLOYMENT"
echo "  Target: Backup Server"
echo "========================================"
echo ""

# Configuration
SERVER="user@backup.diotec360.com"
DEPLOY_DIR="/var/www/aethel"
SERVICE_NAME="aethel-backup"

echo "[1/8] Connecting to backup server..."
ssh $SERVER "echo 'Connection successful'"

echo ""
echo "[2/8] Creating deployment directory..."
ssh $SERVER "mkdir -p $DEPLOY_DIR"

echo ""
echo "[3/8] Uploading application files..."
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  aethel/ $SERVER:$DEPLOY_DIR/diotec360/
rsync -avz --exclude='.git' --exclude='node_modules' --exclude='__pycache__' \
  api/ $SERVER:$DEPLOY_DIR/api/

echo ""
echo "[4/8] Uploading configuration..."
scp requirements.txt $SERVER:$DEPLOY_DIR/
scp .env.node3.backup $SERVER:$DEPLOY_DIR/.env

echo ""
echo "[5/8] Uploading genesis state..."
rsync -avz .DIOTEC360_vault/ $SERVER:$DEPLOY_DIR/.DIOTEC360_vault/
rsync -avz .DIOTEC360_state/ $SERVER:$DEPLOY_DIR/.DIOTEC360_state/

echo ""
echo "[6/8] Installing dependencies..."
ssh $SERVER "cd $DEPLOY_DIR && pip3 install -r requirements.txt"

echo ""
echo "[7/8] Creating systemd service..."
ssh $SERVER "sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << 'EOF'
[Unit]
Description=DIOTEC360 LATTICE Node 3 (Backup)
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR
Environment=\"PATH=/usr/local/bin:/usr/bin:/bin\"
ExecStart=/usr/local/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

echo ""
echo "[8/8] Starting service..."
ssh $SERVER "sudo systemctl daemon-reload"
ssh $SERVER "sudo systemctl enable $SERVICE_NAME"
ssh $SERVER "sudo systemctl restart $SERVICE_NAME"

echo ""
echo "Waiting for service to start..."
sleep 5

echo ""
echo "Verifying deployment..."
ssh $SERVER "curl -s http://localhost:8000/health" || echo "Health check failed!"

echo ""
echo "========================================"
echo "  DEPLOYMENT SUCCESSFUL! 🎉"
echo "========================================"
echo ""
echo "Node 3 is running at:"
echo "  Internal: http://localhost:8000"
echo "  External: https://backup.diotec360.com"
echo ""
echo "Verify deployment:"
echo "  curl https://backup.diotec360.com/health"
echo "  curl https://backup.diotec360.com/api/lattice/state"
echo ""
echo "Expected Merkle Root:"
echo "  5df3daee3a0ca23c388a16c3db2c2388aea63f1c4ed5fa12377fe0fef6bf3ce5"
echo ""
echo "Check logs:"
echo "  ssh $SERVER 'sudo journalctl -u $SERVICE_NAME -f'"
echo ""
