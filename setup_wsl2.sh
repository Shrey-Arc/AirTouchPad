#!/bin/bash

echo "🔧 Setting up AirTouchPad for WSL2..."

# Update system
echo "📦 Updating packages..."
sudo apt update

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-tk \
    libcairo2-dev libgirepository1.0-dev \
    x11-apps v4l-utils

# Install Python packages
echo "📦 Installing Python packages..."
pip3 install opencv-python mediapipe pyautogui pillow

# Try to install pystray (may fail, that's ok)
echo "📦 Installing pystray (optional)..."
pip3 install pystray || echo "⚠️  pystray installation failed (expected on WSL2)"

# Setup display
echo "🖥️  Setting up display..."
if ! grep -q "DISPLAY" ~/.bashrc; then
    echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):0' >> ~/.bashrc
    echo "✅ DISPLAY variable added to ~/.bashrc"
fi

# Create marker
touch .first_run

echo ""
echo "✅ Setup complete!"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "1. WSL2 cannot access Windows camera directly"
echo "2. System tray may not work"
echo "3. For full functionality, run on Windows natively"
echo ""
echo "To start: source ~/.bashrc && python3 launcher_wsl.py"