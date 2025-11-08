import subprocess

class WaylandInput:
    def __init__(self):
        pass

    def click(self, button='left'):
        if button == 'left':
            self._run_command(['ydotool', 'click', '0x80'])
        elif button == 'right':
            self._run_command(['ydotool', 'click', '0x81'])
        elif button == 'middle':
            self._run_command(['ydotool', 'click', '0x82'])

    def mouseDown(self, button='left'):
        if button == 'left':
            self._run_command(['ydotool', 'mousedown', '0x80'])
        elif button == 'right':
            self._run_command(['ydotool', 'mousedown', '0x81'])
        elif button == 'middle':
            self._run_command(['ydotool', 'mousedown', '0x82'])

    def mouseUp(self, button='left'):
        if button == 'left':
            self._run_command(['ydotool', 'mouseup', '0x80'])
        elif button == 'right':
            self._run_command(['ydotool', 'mouseup', '0x81'])
        elif button == 'middle':
            self._run_command(['ydotool', 'mouseup', '0x82'])

    def scroll(self, clicks):
        self._run_command(['ydotool', 'scroll', str(clicks)])

    def hscroll(self, clicks):
        # ydotool does not support horizontal scroll directly
        # This is a limitation of this implementation
        pass

    def hotkey(self, *args):
        command = ['ydotool', 'key']
        for arg in args:
            command.append(arg)
        self._run_command(command)

    def press(self, key):
        self._run_command(['ydotool', 'key', key])

    def _run_command(self, command):
        try:
            subprocess.run(command, check=True)
        except FileNotFoundError:
            print("ydotool not found. Please install ydotool for Wayland support.")
        except Exception as e:
            print(f"Error running ydotool command: {e}")
