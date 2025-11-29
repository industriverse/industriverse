#!/bin/bash

# Kill any existing processes on ports 5001 (Backend) and 3000 (Frontend)
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "🚀 Starting Industriverse Demo Suite..."

# 1. Start Backend
echo "   [1/2] Launching Maestro Backend (Port 5001)..."
node backend/app.js > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for Backend to be ready
sleep 2

# 2. Start Frontend
echo "   [2/2] Launching Demo Dashboard (Port 3000)..."
# Use npx vite with our custom config and entry point
npx vite serve . --config demo_app/vite.config.js --open demo_app/index.html

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
