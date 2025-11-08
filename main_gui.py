import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import threading
import os
from pathlib import Path

# Camera debug preview (new)
try:
    from live_preview import LivePreview
except:
    LivePreview = None

try:
    import cv2
    CV2_AVAILABLE = True
except:
    CV2_AVAILABLE = False

try:
    from utils.system_tray import SystemTrayApp
except:
    SystemTrayApp = None


class MainGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AirTouchPad - Hand Gesture Control")
        self.root.geometry("900x700")

        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.success_color = "#a6e3a1"
        self.error_color = "#f38ba8"
        self.card_bg = "#2e2e3e"

        self.root.configure(bg=self.bg_color)

        self.core_process = None
        self.preview = None
        self.system_tray = None

        self.create_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def get_available_cameras(self):
        if not CV2_AVAILABLE:
            return ["Camera 0"]

        cams = []
        for i in range(3):
            try:
                cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
                if cap.isOpened():
                    cams.append(f"Camera {i}")
                    cap.release()
            except:
                pass

        if not cams:
            cams = ["Camera 0"]

        return cams

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

        self.status_frame = tk.Frame(header, bg=self.accent_color)
        self.status_frame.pack(side="right", padx=30)

        self.status_indicator = tk.Canvas(self.status_frame, width=15, height=15,
                                          bg=self.accent_color, highlightthickness=0)
        self.status_indicator.pack(side="left", padx=(0, 10))
        self.status_circle = self.status_indicator.create_oval(
            2, 2, 13, 13, fill=self.error_color, outline="")

        self.status_label = tk.Label(self.status_frame, text="Inactive",
                                     font=("Segoe UI", 11, "bold"),
                                     bg=self.accent_color, fg="#000")
        self.status_label.pack(side="left")

        # Main content
        content = tk.Frame(self.root, bg=self.bg_color)
        content.pack(fill="both", expand=True, padx=30, pady=30)

        left_panel = tk.Frame(content, bg=self.bg_color)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # Performance options
        perf_frame = tk.LabelFrame(left_panel, text="Performance Settings",
                                   bg=self.card_bg, fg=self.fg_color,
                                   font=("Segoe UI", 12, "bold"))
        perf_frame.pack(fill="x", pady=(0, 20))

        tk.Label(perf_frame, text="Camera:",
                 bg=self.card_bg, fg=self.fg_color).grid(row=0, column=0,
                                                         sticky="w", padx=10, pady=5)

        self.available_cameras = self.get_available_cameras()
        self.camera_var = tk.StringVar(self.root)
        self.camera_var.set(self.available_cameras[0])

        cam_menu = ttk.Combobox(perf_frame, textvariable=self.camera_var,
                                values=self.available_cameras,
                                state="readonly", width=15)
        cam_menu.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(perf_frame, text="Model Complexity:",
                 bg=self.card_bg, fg=self.fg_color).grid(row=1, column=0,
                                                         sticky="w", padx=10, pady=5)

        self.model_complexity_var = tk.StringVar(self.root, "0 (Lite)")

        model_menu = ttk.Combobox(perf_frame, textvariable=self.model_complexity_var,
                                  values=["0 (Lite)", "1 (Full)"],
                                  state="readonly", width=15)
        model_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Start/Stop button
        self.toggle_btn = tk.Button(left_panel, text="🚀 Start AirTouchPad",
                                    command=self.toggle_core,
                                    font=("Segoe UI", 16, "bold"),
                                    bg=self.success_color, fg="#000",
                                    padx=30, pady=20, relief="flat",
                                    cursor="hand2")
        self.toggle_btn.pack(fill="x", pady=(20, 20))

        # Feature Cards
        features = [
            ("🎯 Calibration", "Calibrate camera for best accuracy", self.open_calibration),
            ("📚 Tutorial", "Learn 31 gesture controls", self.open_tutorial),
            ("🎮 Debug Overlay", "Visualize hand tracking", self.open_debug),
            ("⚙️ Settings", "Customize thresholds & behavior", self.open_settings),
        ]

        for title, desc, command in features:
            self.create_card(left_panel, title, desc, command)

        # Right info section
        right_panel = tk.Frame(content, bg=self.bg_color, width=300)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)

        info_card = tk.Frame(right_panel, bg=self.card_bg)
        info_card.pack(fill="both", expand=True)

        info_title = tk.Label(info_card, text="ℹ️ Quick Info",
                              font=("Segoe UI", 16, "bold"),
                              bg=self.card_bg, fg=self.accent_color)
        info_title.pack(anchor="w", padx=20, pady=(20, 10))

        info_text = """
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
"""
        info_label = tk.Label(info_card, text=info_text,
                              font=("Segoe UI", 10),
                              bg=self.card_bg, fg=self.fg_color,
                              justify="left")
        info_label.pack(anchor="w", padx=20, pady=10)

    def create_card(self, parent, title, description, command):
        card = tk.Frame(parent, bg=self.card_bg)
        card.pack(fill="x", pady=(0, 15))

        btn = tk.Button(card, text=title, command=command,
                        font=("Segoe UI", 14, "bold"),
                        bg=self.card_bg, fg=self.fg_color,
                        padx=20, pady=15, anchor="w",
                        relief="flat", cursor="hand2")
        btn.pack(fill="x")

        # FIX: padding on Label must NOT be tuple
        desc_label = tk.Label(card, text=description,
                              font=("Segoe UI", 10),
                              bg=self.card_bg, fg=self.fg_color,
                              padx=20, anchor="w")
        desc_label.pack(fill="x", pady=(0, 15))

    def toggle_core(self):
        if self.core_process:
            self.stop_core()
        else:
            self.start_core()

    def start_core(self):
        try:
            cam_idx = self.camera_var.get().split()[-1]
            model_complexity = self.model_complexity_var.get().split()[0]

            self.core_process = subprocess.Popen(
                [sys.executable, "beast_core.py", cam_idx, model_complexity]
            )

            # Live preview window
            if LivePreview:
                self.preview = LivePreview(int(cam_idx))

            self.status_indicator.itemconfig(self.status_circle, fill=self.success_color)
            self.status_label.config(text="Active")
            self.toggle_btn.config(text="⏹️ Stop AirTouchPad", bg=self.error_color)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_core(self):
        if self.preview:
            self.preview.stop()
            self.preview = None

        if self.core_process:
            self.core_process.terminate()
            try:
                self.core_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.core_process.kill()
            self.core_process = None

        self.status_indicator.itemconfig(self.status_circle, fill=self.error_color)
        self.status_label.config(text="Inactive")
        self.toggle_btn.config(text="🚀 Start AirTouchPad", bg=self.success_color)

    def open_calibration(self):
        subprocess.Popen([sys.executable, "calibration.py"])

    def open_debug(self):
        subprocess.Popen([sys.executable, "debug_display.py"])

    def open_settings(self):
        messagebox.showinfo("Settings",
                            "Edit config.json to customize thresholds.\n"
                            "Run calibration for auto-tuning.")

    def open_tutorial(self):
        messagebox.showinfo("Tutorial", "Full tutorial coming soon.")

    def on_closing(self):
        if self.core_process:
            if messagebox.askyesno("Minimize", "Minimize to system tray?"):
                self.root.withdraw()
                if SystemTrayApp:
                    self.system_tray = SystemTrayApp(self.root, self.stop_core)
                return

            self.stop_core()
        self.root.quit()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    MainGUI().run()
