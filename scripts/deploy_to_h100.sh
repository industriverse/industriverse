#!/bin/bash

# Configuration from Screenshot
HOST="213.181.105.235"
PORT="12803"
USER="root"
SSH_KEY="$HOME/.ssh/id_ed25519" # Key from screenshot
REMOTE_DIR="/workspace/industriverse"

# Check for B2 Credentials
if [ -z "$B2_KEY_ID" ] || [ -z "$B2_APP_KEY" ]; then
    echo "❌ Error: B2_KEY_ID and B2_APP_KEY environment variables are not set."
    echo "Please export them before running this script:"
    echo "  export B2_KEY_ID='your_key_id'"
    echo "  export B2_APP_KEY='your_app_key'"
    exit 1
fi

echo "🚀 Deploying to H100 Pod ($HOST:$PORT)..."
echo "🔑 Using Key: $SSH_KEY"
echo "🔑 You may be asked for your SSH key passphrase."

# 1. Sync Code (Excluding heavy/unnecessary folders)
# We use rsync to efficiently transfer only changed files
echo "📦 Syncing codebase..."
rsync -avz -e "ssh -p $PORT -i $SSH_KEY" \
    --exclude '.git' \
    --exclude 'data' \
    --exclude 'venv' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    . $USER@$HOST:$REMOTE_DIR

# 2. Execute Remote Setup & Run
echo "🔥 Executing Big Burn on Remote..."
ssh -p $PORT -i $SSH_KEY -t $USER@$HOST << EOF
    export B2_KEY_ID=$B2_KEY_ID
    export B2_APP_KEY=$B2_APP_KEY
    
    # Create directory if it doesn't exist
    mkdir -p $REMOTE_DIR
    cd $REMOTE_DIR
    
    echo "🛠️  Setting up Virtual Environment on H100..."
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    # Activate venv
    source venv/bin/activate
    
    echo "📦 Installing Dependencies..."
    pip install --upgrade pip
    pip install torch pyyaml b2sdk
    
    echo "🚀 Starting The Big Burn..."
    # Run the orchestrator with PYTHONPATH set to current directory
    PYTHONPATH=. python3 scripts/run_big_burn.py
    
    echo "✅ Remote Execution Complete."
EOF
