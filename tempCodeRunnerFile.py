import sys
import os
import subprocess
from pathlib import Path

def check_permissions():
    """Check and display permission requirements"""
    print("\n" + "="*60)
    print("Checking system permissions...")
    print("="*60)
    
    try:
        from os_handlers import (
            get_permission_instructions,
            check_macos_accessibility,
            check_linux_input_method
        )
        
        instructions = get_permission_instructions()
        print(instructions)
        
        # Detailed checks
        import platform
        os_type = platform.system().lower()
        
        if 'darwin' in os_type:
            has_access = check_macos_accessibility()
            if has_access is False:
                print("\n⚠️  WARNING: macOS Accessibility not granted!")
                print("Some features will not work until you enable it.")
                response = input("\nContinue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Please enable Accessibility and run again.")
                    return False
        
        elif 'linux' in os_type:
            method = check_linux_input_method()
            if method == 'wayland-no-helper':
                print("\n⚠️  WARNING: Wayland detected but no input helper found!")
                print("Install ydotool or wtype for full functionality:")
                print("  sudo apt install ydotool")
                response = input("\nContinue with limited functionality? (y/n): ")
                if response.lower() != 'y':
                    print("Please install required tools and run again.")
                    return False
        
        print("\n✓ Permission check complete\n")
        return True
        
    except ImportError:
        print("⚠️  Could not import os_handlers for permission checks")
        return True
    except Exception as e:
        print(f"Error checking permissions: {e}")
        return True

def main():
    """Main launcher entry point"""
    print("\n✋ AirTouchPad Launcher")
    print("Version 1.0\n")
    
    # Check for first run
    first_run_marker = Path(__file__).parent / '.first_run'
    
    if not first_run_marker.exists():
        print("First run detected. Starting installation wizard...\n")
        try:
            result = subprocess.run(
                [sys.executable, 'installer_wizard.py'],
                check=True
            )
            
            # Create marker file after successful installation
            first_run_marker.touch()
            print("\n✓ Installation completed successfully!")
            
        except subprocess.CalledProcessError:
            print("\n❌ Installation wizard failed or was cancelled.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Installation cancelled by user.")
            sys.exit(1)
        except FileNotFoundError:
            print("\n❌ installer_wizard.py not found!")
            sys.exit(1)
    
    # Check permissions before launching
    if not check_permissions():
        sys.exit(1)
    
    # Launch main GUI
    try:
        print("Launching AirTouchPad main interface...\n")
        from main_gui import MainGUI
        app = MainGUI()
        app.run()
        
    except ImportError as e:
        print(f"\n❌ Failed to import main_gui: {e}")
        print("\nMissing dependencies. Please run:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed to launch: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Launcher interrupted by user")
        sys.exit(0)