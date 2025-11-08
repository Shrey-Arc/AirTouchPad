# ============================================================================
# FILE 1: launcher.py (MAIN ENTRY POINT)
# ============================================================================

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Check for first run
    first_run_marker = Path(__file__).parent / '.first_run'
    
    if not first_run_marker.exists():
        # Run installation wizard
        print("First run detected. Starting installation wizard...")
        try:
            subprocess.run([sys.executable, 'installer_wizard.py'], check=True)
            # Create marker file after successful installation
            first_run_marker.touch()
        except subprocess.CalledProcessError:
            print("Installation wizard failed or was cancelled.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nInstallation cancelled by user.")
            sys.exit(1)
    
    # Launch main GUI
    from main_gui import MainGUI
    app = MainGUI()
    app.run()

if __name__ == '__main__':
    main()

