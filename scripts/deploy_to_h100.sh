#!/bin/bash
set -e

# Sovereign Intelligence - H100 Deployment Script
# Usage: ./deploy_to_h100.sh

echo "🚀 Starting Deployment to H100 Instance..."

# 1. Update System
echo "   🔄 Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git curl python3-pip

# 2. Install Docker & NVIDIA Container Toolkit
if ! command -v docker &> /dev/null; then
    echo "   🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    
    # NVIDIA Toolkit
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    
    sudo apt-get update
    sudo apt-get install -y nvidia-container-toolkit
    sudo nvidia-ctk runtime configure --runtime=docker
    sudo systemctl restart docker
else
    echo "   ✅ Docker already installed."
fi

# 3. Clone Repository (if not present)
if [ ! -d "industriverse" ]; then
    echo "   📦 Cloning Repository..."
    # Using HTTPS for simplicity in this script, ideally use SSH keys or a PAT
    git clone https://github.com/industriverse/industriverse.git
else
    echo "   ✅ Repository already exists. Pulling latest..."
    cd industriverse && git pull && cd ..
fi

# 4. Build Docker Image
echo "   🔨 Building Sovereign Docker Image..."
cd industriverse
sudo docker build -t sovereign-stack .

echo "✅ Deployment Setup Complete."
echo "   Run 'python3 scripts/run_big_burn.py' to start the training."
