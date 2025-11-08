import platform
from os_handlers import volume_up, volume_down, mute_toggle, media_play_pause, media_next, media_prev, lock_screen, set_brightness, open_notifications, open_quick_settings, is_wayland
import time
import shutil

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

if is_wayland() and shutil.which('ydotool'):
    from wayland_input import WaylandInput
    input_backend = WaylandInput()
else:
    input_backend = pyautogui

class EventMapper:
    def __init__(self, cfg):
        self.os = platform.system().lower()
    def handle(self, g):
        t = g.get('type')
        print('[EVENT]', t, g)
        try:
            if t == 'left_click':
                if input_backend: input_backend.click()
            elif t == 'right_click':
                if input_backend: input_backend.click(button='right')
            elif t == 'middle_click':
                if input_backend: input_backend.click(button='middle')
            elif t == 'drag':
                if input_backend: input_backend.mouseDown()
            elif t == 'scroll_up':
                if input_backend: input_backend.scroll(120)
            elif t == 'scroll_down':
                if input_backend: input_backend.scroll(-120)
            elif t == 'hscroll_right':
                if input_backend and hasattr(input_backend,'hscroll'): input_backend.hscroll(100)
            elif t == 'hscroll_left':
                if input_backend and hasattr(input_backend,'hscroll'): input_backend.hscroll(-100)
            elif t == 'app_switch':
                if input_backend: input_backend.hotkey('alt','tab')
            elif t == 'task_view':
                if input_backend: input_backend.hotkey('win','tab')
            elif t == 'show_desktop':
                if input_backend: input_backend.hotkey('win','d')
            elif t == 'screenshot':
                if self.os=='windows' and input_backend: input_backend.hotkey('win','printscreen')
            elif t == 'snap_left':
                if input_backend: input_backend.hotkey('win','left')
            elif t == 'snap_right':
                if input_backend: input_backend.hotkey('win','right')
            elif t == 'volume_up':
                volume_up()
            elif t == 'volume_down':
                volume_down()
            elif t == 'mute_unmute':
                mute_toggle()
            elif t == 'brightness_up':
                # increase by 10% (best-effort)
                set_brightness(70)
            elif t == 'brightness_down':
                set_brightness(30)
            elif t == 'media_toggle':
                media_play_pause()
            elif t == 'next_track':
                media_next()
            elif t == 'prev_track':
                media_prev()
            elif t == 'modifier_hold':
                print('Modifier hold')
            elif t == 'enter':
                if input_backend: input_backend.press('enter')
            elif t == 'zoom_in':
                if input_backend: input_backend.hotkey('ctrl','+')
            elif t == 'zoom_out':
                if input_backend: input_backend.hotkey('ctrl','-')
            elif t == 'rotate':
                print('Rotate', g.get('angle'))
            elif t == 'lock_screen':
                lock_screen()
            elif t == 'notifications':
                open_notifications()
            elif t == 'quick_settings':
                open_quick_settings()
            else:
                print('Unhandled', t)
        except Exception as e:
            print('Error handling', t, e)
