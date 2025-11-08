import platform
import os
import shutil

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

from os_handlers import (
    volume_up, volume_down, mute_toggle, 
    media_play_pause, media_next, media_prev, 
    lock_screen, set_brightness, 
    open_notifications, open_quick_settings
)

def _is_wayland():
    """Detect if running under Wayland"""
    return (os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland' or 
            os.environ.get('WAYLAND_DISPLAY') is not None)

def _has_wayland_helpers():
    """Check if Wayland input helpers are available"""
    return (shutil.which('ydotool') is not None or 
            shutil.which('wtype') is not None or
            shutil.which('swaymsg') is not None)

class EventMapper:
    def __init__(self, cfg):
        self.os = platform.system().lower()
        self.is_wayland = _is_wayland()
        self.has_wayland_helpers = _has_wayland_helpers()
        self.wayland_warning_shown = False
        
        # Log backend information
        if self.is_wayland:
            if self.has_wayland_helpers:
                print('[EventMapper] Running on Wayland with input helpers available')
            else:
                print('[EventMapper] WARNING: Running on Wayland without input helpers')
                print('[EventMapper] Install ydotool or wtype for full functionality:')
                print('[EventMapper]   sudo apt install ydotool')
                print('[EventMapper]   OR: sudo apt install wtype')
                self.wayland_warning_shown = True
        else:
            print(f'[EventMapper] Running on {self.os} (X11 or native)')
    
    def _check_wayland_availability(self, action_type):
        """Check if action is available on Wayland"""
        if self.is_wayland and not self.has_wayland_helpers:
            if not self.wayland_warning_shown:
                print(f'[EventMapper] Cannot perform {action_type}: Wayland input injection requires helpers')
                print('[EventMapper] Install: sudo apt install ydotool')
                self.wayland_warning_shown = True
            return False
        return True
    
    def handle(self, g):
        t = g.get('type')
        confidence = g.get('confidence', 1.0)
        print(f'[EVENT] {t} (confidence: {confidence:.2f})', g)
        
        try:
            # Basic mouse operations
            if t == 'left_click':
                if self._check_wayland_availability('click') and pyautogui:
                    pyautogui.click()
                    
            elif t == 'right_click':
                if self._check_wayland_availability('click') and pyautogui:
                    pyautogui.click(button='right')
                    
            elif t == 'middle_click':
                if self._check_wayland_availability('click') and pyautogui:
                    pyautogui.click(button='middle')
                    
            elif t == 'drag':
                if self._check_wayland_availability('drag') and pyautogui:
                    pyautogui.mouseDown()
                    
            # Scrolling
            elif t == 'scroll_up':
                if self._check_wayland_availability('scroll') and pyautogui:
                    pyautogui.scroll(120)
                    
            elif t == 'scroll_down':
                if self._check_wayland_availability('scroll') and pyautogui:
                    pyautogui.scroll(-120)
                    
            elif t == 'hscroll_right':
                if self._check_wayland_availability('hscroll') and pyautogui and hasattr(pyautogui, 'hscroll'):
                    pyautogui.hscroll(100)
                    
            elif t == 'hscroll_left':
                if self._check_wayland_availability('hscroll') and pyautogui and hasattr(pyautogui, 'hscroll'):
                    pyautogui.hscroll(-100)
                    
            # Window management
            elif t == 'app_switch':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    pyautogui.hotkey('alt', 'tab')
                    
            elif t == 'task_view':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    if 'windows' in self.os:
                        pyautogui.hotkey('win', 'tab')
                    elif 'darwin' in self.os:
                        pyautogui.hotkey('ctrl', 'up')
                        
            elif t == 'show_desktop':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    if 'windows' in self.os:
                        pyautogui.hotkey('win', 'd')
                    elif 'darwin' in self.os:
                        pyautogui.hotkey('f11')
                        
            elif t == 'screenshot':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    if 'windows' in self.os:
                        pyautogui.hotkey('win', 'printscreen')
                    elif 'darwin' in self.os:
                        pyautogui.hotkey('command', 'shift', '3')
                    elif 'linux' in self.os:
                        pyautogui.hotkey('printscreen')
                        
            elif t == 'snap_left':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    if 'windows' in self.os:
                        pyautogui.hotkey('win', 'left')
                    elif 'darwin' in self.os:
                        print('[EVENT] Snap left requires third-party app on macOS')
                        
            elif t == 'snap_right':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    if 'windows' in self.os:
                        pyautogui.hotkey('win', 'right')
                    elif 'darwin' in self.os:
                        print('[EVENT] Snap right requires third-party app on macOS')
                        
            # Volume controls (OS handlers)
            elif t == 'volume_up':
                volume_up()
                
            elif t == 'volume_down':
                volume_down()
                
            elif t == 'mute_unmute':
                mute_toggle()
                
            # Brightness controls
            elif t == 'brightness_up':
                set_brightness(70)  # Increase to 70%
                
            elif t == 'brightness_down':
                set_brightness(30)  # Decrease to 30%
                
            # Media controls
            elif t == 'media_toggle':
                media_play_pause()
                
            elif t == 'next_track':
                media_next()
                
            elif t == 'prev_track':
                media_prev()
                
            # Modifier and special keys
            elif t == 'modifier_hold':
                print('[EVENT] Modifier hold detected')
                
            elif t == 'enter':
                if self._check_wayland_availability('press') and pyautogui:
                    pyautogui.press('enter')
                    
            # Zoom
            elif t == 'zoom_in':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    pyautogui.hotkey('ctrl', '+')
                    
            elif t == 'zoom_out':
                if self._check_wayland_availability('hotkey') and pyautogui:
                    pyautogui.hotkey('ctrl', '-')
                    
            # Rotation
            elif t == 'rotate':
                angle = g.get('angle', 0)
                print(f'[EVENT] Rotate gesture detected: {angle:.2f} radians')
                
            # System
            elif t == 'lock_screen':
                lock_screen()
                
            elif t == 'notifications':
                open_notifications()
                
            elif t == 'quick_settings':
                open_quick_settings()
                
            else:
                print(f'[EVENT] Unhandled gesture type: {t}')
                
        except Exception as e:
            print(f'[EVENT] Error handling {t}: {e}')