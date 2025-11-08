import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import sys
import threading
import os
from pathlib import Path

class InstallerWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AirTouchPad - Installation Wizard")
        self.root.geometry("750x650")
        self.root.resizable(False, False)
        
        # Modern color scheme
        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#89b4fa"
        self.success_color = "#a6e3a1"
        self.error_color = "#f38ba8"
        
        self.root.configure(bg=self.bg_color)
        
        self.current_page = 0
        self.pages = [
            self.create_welcome_page,
            self.create_license_page,
            self.create_dependencies_page,
            self.create_completion_page
        ]
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True)
        
        # FIX: Separate containers for pages and navigation
        # Page container - use pack with weight to prevent overlap
        self.page_container = tk.Frame(main_container, bg=self.bg_color, height=500)
        self.page_container.pack(fill="both", expand=True, padx=20, pady=(20, 0))
        self.page_container.pack_propagate(False)  # Prevent shrinking
        
        # Navigation container - fixed height at bottom
        self.nav_container = tk.Frame(main_container, bg=self.bg_color, height=60)
        self.nav_container.pack(fill="x", side="bottom", padx=20, pady=20)
        self.nav_container.pack_propagate(False)  # Keep fixed height
        
        self.show_page(0)
        
    def create_welcome_page(self):
        # Create frame WITHOUT parent - will be packed later
        frame = tk.Frame(self.page_container, bg=self.bg_color)
        
        title = tk.Label(frame, text="🎯 Welcome to AirTouchPad!", 
                        font=("Segoe UI", 28, "bold"),
                        fg=self.accent_color, bg=self.bg_color)
        title.pack(pady=(20, 10))
        
        subtitle = tk.Label(frame, text="Control Your Computer with Hand Gestures",
                           font=("Segoe UI", 14),
                           fg=self.fg_color, bg=self.bg_color)
        subtitle.pack(pady=(0, 30))
        
        features_text = '''
✨ 31 Unique Gesture Controls
🖱️ Replace Mouse & Keyboard
🎮 Gaming & Creative Workflows
🌐 Multi-OS Support (Windows, macOS, Linux)
📊 Real-time Hand Tracking
⚡ Low Latency Performance
🎨 Customizable Gestures
🔒 Privacy-First (Local Processing)
        '''
        
        features = tk.Label(frame, text=features_text,
                           font=("Segoe UI", 12),
                           fg=self.fg_color, bg=self.bg_color,
                           justify="left")
        features.pack(pady=20)
        
        info = tk.Label(frame, 
                        text="This wizard will guide you through the installation process.\n\n"
                            "Click 'Next' to continue.",
                        font=("Segoe UI", 11),
                        fg=self.fg_color, bg=self.bg_color,
                        justify="center")
        info.pack(pady=20)
        
        return frame
    
    def create_license_page(self):
        frame = tk.Frame(self.page_container, bg=self.bg_color)
        
        title = tk.Label(frame, text="📜 License Agreement",
                        font=("Segoe UI", 20, "bold"),
                        fg=self.accent_color, bg=self.bg_color)
        title.pack(pady=(10, 20))
        
        license_text = '''MIT License

Copyright (c) 2025 AirTouchPad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
        
        text_frame = tk.Frame(frame, bg=self.bg_color)
        text_frame.pack(fill="both", expand=True, padx=10)
        
        text_widget = scrolledtext.ScrolledText(text_frame, 
                                                font=("Consolas", 10),
                                                bg="#2e2e3e", fg=self.fg_color,
                                                height=15, wrap="word")
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", license_text)
        text_widget.config(state="disabled")
        
        self.accept_var = tk.BooleanVar()
        accept_cb = tk.Checkbutton(frame, 
                                   text="I accept the terms and conditions",
                                   variable=self.accept_var,
                                   font=("Segoe UI", 11, "bold"),
                                   fg=self.accent_color, bg=self.bg_color,
                                   selectcolor=self.bg_color,
                                   activebackground=self.bg_color,
                                   activeforeground=self.success_color)
        accept_cb.pack(pady=15)
        
        return frame
    
    def create_dependencies_page(self):
        frame = tk.Frame(self.page_container, bg=self.bg_color)
        
        title = tk.Label(frame, text="📦 Installing Dependencies",
                        font=("Segoe UI", 20, "bold"),
                        fg=self.accent_color, bg=self.bg_color)
        title.pack(pady=(10, 20))
        
        info = tk.Label(frame,
                       text="Installing required packages... This may take a few minutes.",
                       font=("Segoe UI", 12),
                       fg=self.fg_color, bg=self.bg_color)
        info.pack(pady=10)
        
        self.progress = ttk.Progressbar(frame, mode='indeterminate', length=400)
        self.progress.pack(pady=20)
        
        output_frame = tk.Frame(frame, bg=self.bg_color)
        output_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.output_text = scrolledtext.ScrolledText(output_frame,
                                                     font=("Consolas", 9),
                                                     bg="#2e2e3e", fg=self.fg_color,
                                                     height=12)
        self.output_text.pack(fill="both", expand=True)
        
        self.status_label = tk.Label(frame, text="",
                                    font=("Segoe UI", 11),
                                    fg=self.fg_color, bg=self.bg_color)
        self.status_label.pack(pady=10)
        
        return frame
    
    def create_completion_page(self):
        frame = tk.Frame(self.page_container, bg=self.bg_color)
        
        title = tk.Label(frame, text="🎉 Installation Complete!",
                        font=("Segoe UI", 24, "bold"),
                        fg=self.success_color, bg=self.bg_color)
        title.pack(pady=(30, 20))
        
        message = tk.Label(frame,
                          text="AirTouchPad has been successfully installed!\n\n"
                               "🎮 You're ready to control your computer with hand gestures.\n\n"
                               "Next steps:\n"
                               "1. Calibrate your camera for optimal performance\n"
                               "2. Learn the gesture controls in the tutorial\n"
                               "3. Start controlling your computer hands-free!\n\n"
                               "Click 'Finish' to launch AirTouchPad.",
                          font=("Segoe UI", 12),
                          fg=self.fg_color, bg=self.bg_color,
                          justify="center")
        message.pack(pady=20)
        
        return frame
    
    def show_page(self, page_num):
        self.current_page = page_num
        
        # Clear page container
        for widget in self.page_container.winfo_children():
            widget.destroy()
        
        # Build new page - MUST pack it!
        page_frame = self.pages[page_num]()
        page_frame.pack(fill="both", expand=True)
        
        # Clear navigation container
        for widget in self.nav_container.winfo_children():
            widget.destroy()
        
        # Create navigation buttons in nav_container
        # Back button
        if page_num > 0:
            tk.Button(self.nav_container, text="← Back",
                     command=lambda: self.show_page(page_num - 1),
                     font=("Segoe UI", 11),
                     bg="#3e3e4e", fg=self.fg_color,
                     padx=20, pady=8, relief="flat",
                     cursor="hand2").pack(side="left")
        
        # Next/Finish button
        if page_num < len(self.pages) - 1:
            if page_num == 1:  # License page
                cmd = lambda: self.proceed_from_license(page_num)
            elif page_num == 2:  # Dependencies page - auto-start
                threading.Thread(target=self.install_dependencies, daemon=True).start()
                return
            else:
                cmd = lambda: self.show_page(page_num + 1)
            
            tk.Button(self.nav_container, text="Next →",
                     command=cmd,
                     font=("Segoe UI", 11, "bold"),
                     bg=self.accent_color, fg="#000",
                     padx=20, pady=8, relief="flat",
                     cursor="hand2").pack(side="right")
        else:
            tk.Button(self.nav_container, text="Finish ✓",
                     command=self.finish,
                     font=("Segoe UI", 11, "bold"),
                     bg=self.success_color, fg="#000",
                     padx=30, pady=8, relief="flat",
                     cursor="hand2").pack(side="right")
    
    def proceed_from_license(self, page_num):
        if not self.accept_var.get():
            messagebox.showwarning("License Agreement",
                                 "You must accept the license agreement to continue.")
            return
        self.show_page(page_num + 1)
    
    def install_dependencies(self):
        self.progress.start()
        self.output_text.insert("end", "Starting installation...\n")
        
        # Define tags for colored text
        self.output_text.tag_config("success", foreground=self.success_color)
        self.output_text.tag_config("error", foreground=self.error_color)
        
        requirements = [
            'opencv-python',
            'mediapipe',
            'pyautogui',
            'pystray',
            'pillow'
        ]
        
        for i, package in enumerate(requirements):
            self.output_text.insert("end", f"\nInstalling {package}...\n")
            self.output_text.see("end")
            self.status_label.config(text=f"Installing {package}... ({i+1}/{len(requirements)})")
            
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True, text=True, timeout=300
                )
                self.output_text.insert("end", result.stdout)
                if result.returncode == 0:
                    self.output_text.insert("end", f"✓ {package} installed successfully\n", "success")
                else:
                    self.output_text.insert("end", f"⚠ Warning installing {package}\n", "error")
            except Exception as e:
                self.output_text.insert("end", f"Error: {str(e)}\n", "error")
            
            self.output_text.see("end")
        
        self.progress.stop()
        self.status_label.config(text="✓ Installation complete!",
                                fg=self.success_color)
        self.output_text.insert("end", "\n" + "="*50 + "\n")
        self.output_text.insert("end", "Installation completed successfully!\n", "success")
        
        # Auto-proceed after 2 seconds
        self.root.after(2000, lambda: self.show_page(3))
    
    def finish(self):
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    wizard = InstallerWizard()
    wizard.run()