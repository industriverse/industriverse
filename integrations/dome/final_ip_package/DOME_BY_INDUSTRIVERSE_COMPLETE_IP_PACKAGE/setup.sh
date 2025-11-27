#!/bin/bash
# Dome by Industriverse - Production Setup Script

echo "🚀 Setting up Dome by Industriverse Production Environment"
echo "=" * 80

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Set up CUDA environment (if available)
echo "⚡ Checking CUDA environment..."
if command -v nvcc &> /dev/null; then
    echo "   ✅ CUDA found: $(nvcc --version | grep release)"
    pip install cupy-cuda11x tensorrt
else
    echo "   ⚠️ CUDA not found - CPU mode only"
fi

# Set up industrial protocols
echo "🏭 Setting up industrial protocol support..."
pip install pymodbus opcua paho-mqtt

# Create configuration directories
echo "📁 Creating configuration directories..."
mkdir -p config/production
mkdir -p logs
mkdir -p data/csi_frames
mkdir -p data/compliance_reports

echo "✅ Dome by Industriverse setup complete!"
echo "🏭 Ready for production deployment"
