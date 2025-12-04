#!/bin/bash
# deploy_to_runpod.sh
# Deploys the Industriverse codebase to the RunPod instance.

HOST="213.181.105.236"
PORT="10693"
USER="root"
KEY="~/.ssh/id_ed25519"

echo "🚀 Deploying to RunPod ($HOST)..."

# 0. Create Remote Directory
ssh -p $PORT -i $KEY -o StrictHostKeyChecking=no $USER@$HOST "mkdir -p ~/industriverse"

# 1. Sync Codebase
rsync -avz -e "ssh -p $PORT -i $KEY -o StrictHostKeyChecking=no" \
    --exclude '.git' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    . $USER@$HOST:~/industriverse/

# 2. Setup Remote Environment
ssh -p $PORT -i $KEY -o StrictHostKeyChecking=no $USER@$HOST << 'EOF'
    cd ~/industriverse
    echo "📦 Installing Dependencies..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    pip install b2sdk python-dotenv pandas numpy
    
    echo "📂 Creating Directories..."
    mkdir -p fossil_vault
    
    echo "✅ Deployment Complete."
EOF
