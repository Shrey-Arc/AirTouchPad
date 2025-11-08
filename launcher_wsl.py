import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🚀 AirTouchPad for WSL2")
    print("⚠️  Note: System tray and camera may have limited functionality")
    
    # Check for first run
    first_run_marker = Path(__file__).parent / '.first_run'
    
    if not first_run_marker.exists():
        print("\nFirst run detected. Installing dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 
                          'opencv-python', 'mediapipe', 'pyautogui', 'pillow'],
                          check=True)
            first_run_marker.touch()
            print("✅ Dependencies installed!")
        except Exception as e:
            print(f"❌ Installation failed: {e}")
            sys.exit(1)
    
    # Launch beast_core directly (skip GUI for now)
    print("\n🎮 Starting AirTouchPad core...")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, 'beast_core.py'])
    except KeyboardInterrupt:
        print("\n👋 Stopping AirTouchPad...")

if __name__ == '__main__':
    main()