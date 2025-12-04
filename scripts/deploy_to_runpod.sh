#!/usr/bin/env bash
set -euo pipefail

# Configuration
REMOTE_HOST="213.181.105.213"
REMOTE_PORT="18473"
REMOTE_USER="root"
SSH_KEY="$HOME/.ssh/id_ed25519"
REMOTE_DIR="/workspace/industriverse"

# Local Data Path (from our local bypass)
LOCAL_DATA="$HOME/industriverse_data"

echo "🚀 Deploying to RunPod H100 ($REMOTE_HOST)..."

# 1. Sync Codebase
echo "   Syncing Code..."
rsync -avz -e "ssh -p $REMOTE_PORT -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --exclude '.git' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.venv' \
    --exclude '*_env' \
    --exclude 'venv' \
    --exclude 'node_modules' \
    --exclude 'data' \
    ./ "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR"

# 2. Sync Data (Fossils)
echo "   Syncing Data..."
# We sync the local fossil vault to the remote workspace
rsync -avz -e "ssh -p $REMOTE_PORT -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "$LOCAL_DATA/fossil_vault" \
    "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

# 3. Remote Setup & Launch
echo "   Configuring Remote Environment..."
ssh -p $REMOTE_PORT -i $SSH_KEY -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" << EOF
    set -e
    cd $REMOTE_DIR
    
    # Install Dependencies
    echo "   Installing Dependencies..."
    pip install --break-system-packages -r requirements.txt
    
    # Ensure Directories
    mkdir -p data/model_zoo data/logs
    
    # Set Environment
    export EXTERNAL_DRIVE="$REMOTE_DIR"
    export PYTHONPATH="$REMOTE_DIR"
    
    # Check GPU
    echo "   Checking GPU..."
    python3 -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()} ({torch.cuda.get_device_name(0)})')"
    
    # Start Worker (Background)
    # We use nohup to keep it running after disconnect
    echo "   Starting GPU Worker..."
    nohup python3 src/scf/daemon/gpu_worker.py \
        data/fossil_vault/fossil-test-001.json \
        --job "cloud-run-001" \
        > data/logs/cloud-worker.log 2>&1 &
        
    echo "✅ Worker Started! PID: \$!"
EOF

echo "🎉 Deployment Complete."
