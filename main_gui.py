# ============================================================================
# FILE 3: main_gui.py
# ============================================================================

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import threading
import os
from pathlib import Path
from utils.system_tray import SystemTrayApp

class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AirTouchPad - Hand Gesture Control")
        self.root.geometry("900x600")
        
        # Modern dark theme
        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.success_color = "#a6e3a1"
        self.error_color = "#f38ba8"
        self.card_bg = "#2e2e3e"
        
        self.root.configure(bg=self.bg_color)
        
        self.core_process = None
        self.system_tray = None
        
        # Setup UI
        self.create_ui()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.accent_color, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_label = tk.Label(header, text="✋ AirTouchPad",
                              font=("Segoe UI", 32, "bold"),
                              bg=self.accent_color, fg="#000")
        title_label.pack(side="left", padx=30, pady=10)
        
        subtitle = tk.Label(header, text="Control Your Computer with Hand Gestures",
                          font=("Segoe UI", 12),
                          bg=self.accent_color, fg="#000")
        subtitle.pack(side="left", padx=(0, 30))
        
        # Status indicator
        self.status_frame = tk.Frame(header, bg=self.accent_color)
        self.status_frame.pack(side="right", padx=30)
        
        self.status_indicator = tk.Canvas(self.status_frame, width=15, height=15,
                                         bg=self.accent_color, highlightthickness=0)
        self.status_indicator.pack(side="left", padx=(0, 10))
        self.status_circle = self.status_indicator.create_oval(2, 2, 13, 13,
                                                               fill=self.error_color,
                                                               outline="")
        
        self.status_label = tk.Label(self.status_frame, text="Inactive",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.accent_color, fg="#000")
        self.status_label.pack(side="left")
        
        # Main content area
        content = tk.Frame(self.root, bg=self.bg_color)
        content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Left panel - Control buttons
        left_panel = tk.Frame(content, bg=self.bg_color)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Start/Stop button
        self.toggle_btn = tk.Button(left_panel, text="🚀 Start AirTouchPad",
                                    command=self.toggle_core,
                                    font=("Segoe UI", 16, "bold"),
                                    bg=self.success_color, fg="#000",
                                    padx=30, pady=20, relief="flat",
                                    cursor="hand2")
        self.toggle_btn.pack(fill="x", pady=(0, 20))
        
        # Feature cards
        features = [
            ("🎯 Calibration", "Calibrate camera for best accuracy", self.open_calibration),
            ("📚 Tutorial", "Learn 31 gesture controls", self.open_tutorial),
            ("🎮 Debug Overlay", "Visualize hand tracking", self.open_debug),
            ("⚙️ Settings", "Customize thresholds & behavior", self.open_settings),
        ]
        
        for title, desc, command in features:
            self.create_card(left_panel, title, desc, command)
        
        # Right panel - Info
        right_panel = tk.Frame(content, bg=self.bg_color, width=300)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Info card
        info_card = tk.Frame(right_panel, bg=self.card_bg, relief="flat")
        info_card.pack(fill="both", expand=True)
        
        info_title = tk.Label(info_card, text="ℹ️ Quick Info",
                             font=("Segoe UI", 16, "bold"),
                             bg=self.card_bg, fg=self.accent_color)
        info_title.pack(anchor="w", padx=20, pady=(20, 10))
        
        info_text = '''
📊 31 Gesture Controls
🖱️ Left & Right Click
📜 Scroll & Zoom
🎵 Media Controls
🔊 Volume & Brightness
🪟 Window Management
🖥️ Multi-Display Support
⚡ Real-time Processing

💡 Tip: Run calibration first
for optimal performance!

🎮 Works even when window
is minimized to tray.
        '''
        
        info_label = tk.Label(info_card, text=info_text,
                             font=("Segoe UI", 10),
                             bg=self.card_bg, fg=self.fg_color,
                             justify="left")
        info_label.pack(anchor="w", padx=20, pady=10)
        
        # About button
        about_btn = tk.Button(info_card, text="📝 About & Credits",
                            command=self.show_about,
                            font=("Segoe UI", 11),
                            bg=self.bg_color, fg=self.fg_color,
                            padx=20, pady=10, relief="flat",
                            cursor="hand2")
        about_btn.pack(side="bottom", fill="x", padx=20, pady=20)
    
    def create_card(self, parent, title, description, command):
        card = tk.Frame(parent, bg=self.card_bg, relief="flat")
        card.pack(fill="x", pady=(0, 15))
        
        btn = tk.Button(card, text=title,
                       command=command,
                       font=("Segoe UI", 14, "bold"),
                       bg=self.card_bg, fg=self.fg_color,
                       padx=20, pady=15, relief="flat",
                       cursor="hand2", anchor="w")
        btn.pack(fill="x")
        
        desc_label = tk.Label(card, text=description,
                             font=("Segoe UI", 10),
                             bg=self.card_bg, fg=self.fg_color,
                             padx=20, pady=(0, 15), anchor="w")
        desc_label.pack(fill="x")
    
    def toggle_core(self):
        if self.core_process is None:
            self.start_core()
        else:
            self.stop_core()
    
    def start_core(self):
        try:
            self.core_process = subprocess.Popen([sys.executable, 'beast_core.py'],
                                                stdout=subprocess.PIPE,
                                                stderr=subprocess.PIPE)
            self.toggle_btn.config(text="⏹️ Stop AirTouchPad",
                                  bg=self.error_color)
            self.status_indicator.itemconfig(self.status_circle, fill=self.success_color)
            self.status_label.config(text="Active")
            messagebox.showinfo("Started", "AirTouchPad is now active!\n\n"
                                          "You can minimize this window to system tray.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {str(e)}")
    
    def stop_core(self):
        if self.core_process:
            self.core_process.terminate()
            self.core_process.wait()
            self.core_process = None
            self.toggle_btn.config(text="🚀 Start AirTouchPad",
                                  bg=self.success_color)
            self.status_indicator.itemconfig(self.status_circle, fill=self.error_color)
            self.status_label.config(text="Inactive")
    
    def open_calibration(self):
        subprocess.Popen([sys.executable, 'calibration.py'])
    
    def open_tutorial(self):
        # Create tutorial window
        tutorial_win = tk.Toplevel(self.root)
        tutorial_win.title("Gesture Tutorial")
        tutorial_win.geometry("800x600")
        tutorial_win.configure(bg=self.bg_color)
        
        # Add tutorial content here
        tk.Label(tutorial_win, text="🎓 Gesture Controls Tutorial",
                font=("Segoe UI", 20, "bold"),
                bg=self.bg_color, fg=self.accent_color).pack(pady=20)
        
        tutorial_text = '''
RIGHT HAND GESTURES:
👆 Index-Thumb Pinch: Left Click
✌️ Index-Middle Pinch: Right Click  
👌 Thumb-Middle Pinch: Middle Click
✊ Hold Pinch: Drag
📜 Two-Finger + Move Up/Down: Scroll
↔️ Two-Finger + Move Left/Right: Horizontal Scroll
🔄 Three-Finger Swipe: App Switch
⬆️ Three-Finger Up: Task View
⬇️ Three-Finger Down: Show Desktop
📷 Three-Finger Tap: Screenshot

LEFT HAND GESTURES:
🔊 Index-Thumb Pinch: Volume Up
🔉 Thumb-Middle Pinch: Volume Down
🔇 Three-Finger Tap: Mute/Unmute
💡 Index-Middle Spread: Brightness Up
🌙 Index-Middle Pinch: Brightness Down
⏯️ Swipe Right: Next Track
⏪ Swipe Left: Previous Track
⏸️ Hold Pinch: Modifier Hold

BOTH HANDS:
🔍 Pinch Both + Spread: Zoom In
🔎 Pinch Both + Contract: Zoom Out
🔄 Rotate Hands: Rotate
🔒 Hands Together: Lock Screen
        '''
        
        text_widget = tk.Text(tutorial_win, font=("Consolas", 11),
                             bg=self.card_bg, fg=self.fg_color,
                             padx=30, pady=20, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", tutorial_text)
        text_widget.config(state="disabled")
    
    def open_debug(self):
        subprocess.Popen([sys.executable, 'debug_display.py'])
    
    def open_settings(self):
        messagebox.showinfo("Settings", "Edit config.json to customize settings.\n\n"
                                       "Run calibration to auto-tune thresholds.")
    
    def show_about(self):
        about_text = '''
AirTouchPad v1.0
━━━━━━━━━━━━━━━━━━━━━

Control your computer with hand gestures using AI-powered computer vision.

🎯 Features:
• 31 unique gesture controls
• Real-time hand tracking
• Multi-OS support
• Low latency (<50ms)
• Privacy-first (local processing)

🛠️ Technology:
• MediaPipe for hand tracking
• OpenCV for image processing
• PyAutoGUI for system control

📝 License: MIT
🌐 GitHub: github.com/yourusername/AirTouchPad

Made with ❤️ for hands-free computing
        '''
        messagebox.showinfo("About AirTouchPad", about_text)
    
    def on_closing(self):
        if self.core_process:
            # Ask user what to do
            result = messagebox.askyesnocancel(
                "Close Window",
                "AirTouchPad is currently running.\n\n"
                "• Yes: Minimize to system tray (keep running)\n"
                "• No: Stop AirTouchPad and exit\n"
                "• Cancel: Return to application"
            )
            
            if result is True:  # Minimize to tray
                self.minimize_to_tray()
            elif result is False:  # Stop and exit
                self.stop_core()
                self.root.quit()
        else:
            self.root.quit()
    
    def minimize_to_tray(self):
        self.root.withdraw()
        if not self.system_tray:
            self.system_tray = SystemTrayApp(self.root, self.stop_core)
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MainGUI()
    app.run()


