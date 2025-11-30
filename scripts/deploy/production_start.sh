#!/bin/bash

echo "🚀 INITIALIZING EMPEIRIA HAUS PRODUCTION STACK..."

# 1. Check Manifest
if [ ! -f "config/system_manifest.json" ]; then
    echo "❌ ERROR: System Manifest not found. Deployment aborted."
    exit 1
fi
echo "✅ Manifest Verified."

# 2. Start Daemon
echo "Starting Collector Daemon..."
python3 scripts/datahub/datahub_ctl.py start
sleep 2
python3 scripts/datahub/datahub_ctl.py research on
echo "✅ Daemon Running (Research Mode: ON)."

# 3. Start API Bridge
echo "Starting API Bridge..."
# Using nohup to run in background
nohup python3 src/api/bridge_server.py > logs/api.log 2>&1 &
API_PID=$!
echo "✅ API Bridge Running (PID: $API_PID) at http://localhost:8000"

# 4. Final Status
echo "---------------------------------------------------"
echo "✨ EMPEIRIA HAUS IS LIVE."
echo "---------------------------------------------------"
echo "Backend:  ACTIVE"
echo "Research: ACTIVE"
echo "API:      ACTIVE"
echo "Frontend: READY (Serve 'src/frontend' via your web server)"
echo "---------------------------------------------------"
echo "To stop: python3 scripts/datahub/datahub_ctl.py stop && kill $API_PID"
