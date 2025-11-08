# ============================================================================
# FILE 4: utils/system_tray.py
# ============================================================================

import pystray
from PIL import Image, ImageDraw
import threading

class SystemTrayApp:
    def __init__(self, root_window, stop_callback):
        self.root = root_window
        self.stop_callback = stop_callback
        
        # Create icon image
        image = self.create_icon_image()
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem("Show Window", self.show_window),
            pystray.MenuItem("Stop AirTouchPad", self.stop_and_exit),
            pystray.MenuItem("Exit", self.exit_app)
        )
        
        # Create icon
        self.icon = pystray.Icon("AirTouchPad", image, "AirTouchPad Running", menu)
        
        # Run icon in separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
    
    def create_icon_image(self):
        # Create a simple hand icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color='#89b4fa')
        dc = ImageDraw.Draw(image)
        
        # Draw a simple hand shape
        dc.ellipse([16, 16, 48, 48], fill='white')
        
        return image
    
    def show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.icon.stop()
        self.icon = None
    
    def stop_and_exit(self):
        self.stop_callback()
        self.exit_app()
    
    def exit_app(self):
        self.icon.stop()
        self.root.quit()

