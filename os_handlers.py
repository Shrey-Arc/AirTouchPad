import platform
import subprocess
import sys
import ctypes
import shutil
import os

OS = platform.system().lower()

def _run_cmd(cmd):
    """Execute system command safely"""
    try:
        subprocess.run(cmd, shell=isinstance(cmd, str), check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

# Permission detection helpers
def check_macos_accessibility():
    """Check if app has macOS Accessibility permissions"""
    if 'darwin' not in OS:
        return None
    
    try:
        # Try a harmless synthetic input test
        import pyautogui
        pyautogui.position()  # This will fail without permissions
        return True
    except Exception:
        return False

def check_windows_input_permissions():
    """Check if Windows allows synthetic input"""
    if 'windows' not in OS:
        return None
    
    try:
        import pyautogui
        # Windows typically allows this, but UAC can block
        return True
    except Exception:
        return False

def check_linux_input_method():
    """Detect Linux display server and available input methods"""
    if 'linux' not in OS:
        return None
    
    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    
    if session_type == 'wayland':
        # Check for Wayland input helpers
        if shutil.which('ydotool'):
            return 'wayland-ydotool'
        elif shutil.which('wtype'):
            return 'wayland-wtype'
        else:
            return 'wayland-no-helper'
    else:
        # X11 - check for xdotool
        if shutil.which('xdotool'):
            return 'x11-xdotool'
        else:
            return 'x11-pyautogui'

def get_permission_instructions():
    """Get user-friendly instructions for enabling permissions"""
    if 'darwin' in OS:
        if not check_macos_accessibility():
            return (
                "macOS Accessibility Required:\n"
                "1. Open System Settings → Privacy & Security → Accessibility\n"
                "2. Add Terminal or Python to allowed apps\n"
                "3. Restart AirTouchPad"
            )
    
    elif 'windows' in OS:
        return (
            "Windows Permissions:\n"
            "1. Ensure Focus Assist is not blocking input\n"
            "2. Run as normal user (not administrator)\n"
            "3. Check Windows Defender isn't blocking"
        )
    
    elif 'linux' in OS:
        method = check_linux_input_method()
        if method == 'wayland-no-helper':
            return (
                "Linux/Wayland Input Helper Required:\n"
                "Install one of:\n"
                "  sudo apt install ydotool\n"
                "OR:\n"
                "  sudo apt install wtype\n"
                "OR switch to X11 session"
            )
        elif method and 'wayland' in method:
            return "Linux/Wayland: Input helper detected ✓"
        elif method == 'x11-pyautogui':
            return (
                "Linux/X11: Using PyAutoGUI\n"
                "Optional: sudo apt install xdotool for better compatibility"
            )
    
    return "Permissions OK"

# PyAutoGUI setup
try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

# Volume Controls
def volume_up():
    """Increase system volume"""
    if pyautogui:
        try:
            pyautogui.press('volumeup')
            return True
        except:
            pass
    
    if 'windows' in OS:
        # Use nircmd if available
        if shutil.which('nircmd.exe'):
            return _run_cmd('nircmd.exe changesysvolume 5000')
    
    elif 'linux' in OS:
        if shutil.which('pactl'):
            return _run_cmd('pactl set-sink-volume @DEFAULT_SINK@ +5%')
        elif shutil.which('amixer'):
            return _run_cmd('amixer set Master 5%+')
    
    return False

def volume_down():
    """Decrease system volume"""
    if pyautogui:
        try:
            pyautogui.press('volumedown')
            return True
        except:
            pass
    
    if 'windows' in OS:
        if shutil.which('nircmd.exe'):
            return _run_cmd('nircmd.exe changesysvolume -5000')
    
    elif 'linux' in OS:
        if shutil.which('pactl'):
            return _run_cmd('pactl set-sink-volume @DEFAULT_SINK@ -5%')
        elif shutil.which('amixer'):
            return _run_cmd('amixer set Master 5%-')
    
    return False

def mute_toggle():
    """Toggle mute"""
    if pyautogui:
        try:
            pyautogui.press('volumemute')
            return True
        except:
            pass
    
    if 'linux' in OS:
        if shutil.which('pactl'):
            return _run_cmd('pactl set-sink-mute @DEFAULT_SINK@ toggle')
        elif shutil.which('amixer'):
            return _run_cmd('amixer set Master toggle')
    
    return False

# Media Controls
def media_play_pause():
    """Toggle media playback"""
    if pyautogui:
        try:
            pyautogui.press('playpause')
            return True
        except:
            pass
    
    if 'linux' in OS and shutil.which('playerctl'):
        return _run_cmd('playerctl play-pause')
    
    return False

def media_next():
    """Next track"""
    if pyautogui:
        try:
            pyautogui.press('nexttrack')
            return True
        except:
            pass
    
    if 'linux' in OS and shutil.which('playerctl'):
        return _run_cmd('playerctl next')
    
    return False

def media_prev():
    """Previous track"""
    if pyautogui:
        try:
            pyautogui.press('prevtrack')
            return True
        except:
            pass
    
    if 'linux' in OS and shutil.which('playerctl'):
        return _run_cmd('playerctl previous')
    
    return False

# Lock Screen
def lock_screen():
    """Lock the workstation"""
    if 'windows' in OS:
        try:
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception:
            return _run_cmd('rundll32.exe user32.dll,LockWorkStation')
    
    elif 'darwin' in OS:
        # macOS lock screen
        return _run_cmd('/usr/bin/osascript -e \'tell application "System Events" to keystroke "q" using {control down, command down}\'')
    
    elif 'linux' in OS:
        # Try multiple methods
        if shutil.which('loginctl'):
            return _run_cmd('loginctl lock-session')
        elif shutil.which('gnome-screensaver-command'):
            return _run_cmd('gnome-screensaver-command -l')
        elif shutil.which('xdg-screensaver'):
            return _run_cmd('xdg-screensaver lock')
        elif shutil.which('dm-tool'):
            return _run_cmd('dm-tool lock')
    
    print('[OS_HANDLERS] Lock screen: No method available for this system')
    return False

# Brightness Control
def set_brightness(percent: int):
    """Set screen brightness (best-effort)"""
    percent = int(max(0, min(100, percent)))
    
    if 'windows' in OS:
        # PowerShell WMI method (requires admin on some systems)
        cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness({percent},0)"'
        success = _run_cmd(cmd)
        if not success:
            print(f'[OS_HANDLERS] Brightness control failed - may require admin privileges')
        return success
    
    elif 'darwin' in OS:
        # macOS: requires 'brightness' CLI tool (not default)
        if shutil.which('brightness'):
            return _run_cmd(f'brightness {percent/100.0}')
        else:
            print('[OS_HANDLERS] Install brightness CLI: brew install brightness')
            return False
    
    elif 'linux' in OS:
        # Try brightnessctl first (most reliable)
        if shutil.which('brightnessctl'):
            return _run_cmd(f'brightnessctl set {percent}%')
        
        # Try xbacklight
        elif shutil.which('xbacklight'):
            return _run_cmd(f'xbacklight -set {percent}')
        
        # Try direct sysfs write (requires permissions)
        else:
            try:
                brightness_path = '/sys/class/backlight/intel_backlight/brightness'
                max_brightness_path = '/sys/class/backlight/intel_backlight/max_brightness'
                
                if os.path.exists(brightness_path) and os.access(brightness_path, os.W_OK):
                    with open(max_brightness_path, 'r') as f:
                        max_bright = int(f.read().strip())
                    
                    target = int(max_bright * percent / 100)
                    with open(brightness_path, 'w') as f:
                        f.write(str(target))
                    return True
            except Exception:
                pass
            
            print('[OS_HANDLERS] Brightness control requires brightnessctl or proper permissions')
            return False
    
    return False

# Notifications and Quick Settings
def open_notifications():
    """Open notification center"""
    if pyautogui:
        try:
            if 'windows' in OS:
                pyautogui.hotkey('win', 'n')
            elif 'darwin' in OS:
                # macOS notification center
                pyautogui.hotkey('command', 'shift', 'n')
            return True
        except:
            pass
    return False

def open_quick_settings():
    """Open quick settings panel"""
    if pyautogui:
        try:
            if 'windows' in OS:
                pyautogui.hotkey('win', 'a')
            elif 'darwin' in OS:
                # macOS Control Center
                pyautogui.hotkey('fn', 'c')
            return True
        except:
            pass
    return False

# Diagnostic function
def diagnose_system():
    """Print system capabilities and permission status"""
    print("\n=== AirTouchPad System Diagnostics ===")
    print(f"OS: {platform.system()} {platform.release()}")
    
    if 'darwin' in OS:
        perm = check_macos_accessibility()
        print(f"macOS Accessibility: {'✓ Enabled' if perm else '✗ Disabled'}")
    
    elif 'linux' in OS:
        method = check_linux_input_method()
        print(f"Linux Input Method: {method}")
    
    print(f"\nPyAutoGUI: {'✓ Available' if pyautogui else '✗ Not installed'}")
    
    print("\nPermission Instructions:")
    print(get_permission_instructions())
    print("=====================================\n")

if __name__ == '__main__':
    # Run diagnostics
    diagnose_system()