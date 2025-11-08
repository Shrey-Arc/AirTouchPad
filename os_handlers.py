import platform, subprocess, sys, ctypes, shutil
OS = platform.system().lower()

def _run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=isinstance(cmd, str), check=True)
        return True
    except Exception as e:
        #print('cmd failed', cmd, e)
        return False

# Volume and media keys using pyautogui if available, else try platform-specific
try:
    import pyautogui
    pyautogui.FAILSAFE=False
except Exception:
    pyautogui=None

def volume_up():
    if pyautogui:
        try: pyautogui.press('volumeup'); return True
        except: pass
    if 'windows' in OS:
        return _run_cmd('nircmd.exe changesysvolume 5000')
    return False

def volume_down():
    if pyautogui:
        try: pyautogui.press('volumedown'); return True
        except: pass
    if 'windows' in OS:
        return _run_cmd('nircmd.exe changesysvolume -5000')
    return False

def mute_toggle():
    if pyautogui:
        try: pyautogui.press('volumemute'); return True
        except: pass
    return False

# Media
def media_play_pause():
    if pyautogui:
        try: pyautogui.press('playpause'); return True
        except: pass
    return False

def media_next():
    if pyautogui:
        try: pyautogui.press('nexttrack'); return True
        except: pass
    return False

def media_prev():
    if pyautogui:
        try: pyautogui.press('prevtrack'); return True
        except: pass
    return False

# Lock screen
def lock_screen():
    if 'windows' in OS:
        try:
            ctypes.windll.user32.LockWorkStation(); return True
        except Exception:
            return _run_cmd('rundll32.exe user32.dll,LockWorkStation')
    if 'darwin' in OS:
        # macOS: use AppleScript to lock screen (fast-user-switch menu)
        return _run_cmd("/usr/bin/osascript -e 'tell application \"System Events\" to keystroke \"q\" using {control down, command down}'")
    if 'linux' in OS:
        # try loginctl
        if shutil.which('loginctl'):
            return _run_cmd('loginctl lock-session')
        if shutil.which('gnome-screensaver-command'):
            return _run_cmd('gnome-screensaver-command -l')
        return False
    return False

# Brightness: attempt platform-specific commands. These often require privileges or helper tools.
def set_brightness(percent:int):
    percent = int(max(0, min(100, percent)))
    if 'windows' in OS:
        # Use PowerShell WMI call
        cmd = f'powershell -Command "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness({percent},0)"'
        return _run_cmd(cmd)
    if 'darwin' in OS:
        # macOS: try 'brightness' CLI (not installed by default)
        if shutil.which('brightness'):
            return _run_cmd(f'brightness {percent/100.0}')
        return False
    if 'linux' in OS:
        # try brightnessctl or xrandr as fallback
        if shutil.which('brightnessctl'):
            return _run_cmd(f'brightnessctl set {percent}%')
        if shutil.which('xrandr'):
            # xrandr cannot change backlight on most systems, fallback
            return False
        return False
    return False

# Notifications and quick settings
def open_notifications():
    if pyautogui:
        try: pyautogui.hotkey('win','n'); return True
        except: pass
    return False

def open_quick_settings():
    if pyautogui:
        try: pyautogui.hotkey('win','a'); return True
        except: pass
    return False
