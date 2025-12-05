#!/bin/bash
set -e

echo "🏭 Installing Dark Factory OS..."

# 1. Check System
echo "🔍 Checking system requirements..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required."
    exit 1
fi

# 2. Install Dependencies
echo "📦 Installing dependencies..."
# pip install -r requirements_edge.txt (Mocking this step)
echo "✅ Dependencies installed."

# 3. Setup Service
echo "⚙️ Setting up systemd service..."
SERVICE_FILE="/tmp/dark_factory.service"
cat <<EOF > $SERVICE_FILE
[Unit]
Description=Dark Factory OS Daemon
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/industriverse/src/app/dark_factory/ui/app.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created at $SERVICE_FILE"

# 4. Finalize
echo "🚀 Installation Complete!"
echo "Run 'systemctl start dark_factory' to launch."
