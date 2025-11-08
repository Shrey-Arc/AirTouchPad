import tkinter as tk
from tkinter import ttk, messagebox
import time, threading, json, os
from handtracker import HandTracker
from utils.config import Config

CFG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

class Calibrator:
    def __init__(self):
        self.cfg = Config()
        self.tracker = HandTracker(self.cfg)
        self.samples = {'r_pinch':[], 'l_pinch':[], 'two_finger':[]}
        self.root = tk.Tk(); self.root.title('Calibration')
        ttk.Label(self.root, text='Calibration: follow prompts').pack(pady=6)
        self.status = ttk.Label(self.root, text='Ready')
        self.status.pack()
        ttk.Button(self.root, text='Calibrate Right Pinch', command=lambda: threading.Thread(target=self.record, args=('r_pinch',), daemon=True).start()).pack(pady=4)
        ttk.Button(self.root, text='Calibrate Left Pinch', command=lambda: threading.Thread(target=self.record, args=('l_pinch',), daemon=True).start()).pack(pady=4)
        ttk.Button(self.root, text='Calibrate Two-Finger', command=lambda: threading.Thread(target=self.record, args=('two_finger',), daemon=True).start()).pack(pady=4)
        ttk.Button(self.root, text='Compute & Save', command=self.compute).pack(pady=8)
        ttk.Button(self.root, text='Exit', command=self.close).pack(pady=4)
        self.root.mainloop()
    def record(self, key):
        self.status.config(text=f'Recording {key} for 5 seconds...')
        t0 = time.time()
        while time.time() - t0 < 5:
            hands, frame = self.tracker.step()
            if hands:
                for lm,label in hands:
                    if key=='r_pinch' and label.startswith('r'):
                        d = ((lm[4][0]-lm[8][0])**2 + (lm[4][1]-lm[8][1])**2)**0.5
                        self.samples[key].append(d)
                    if key=='l_pinch' and label.startswith('l'):
                        d = ((lm[4][0]-lm[8][0])**2 + (lm[4][1]-lm[8][1])**2)**0.5
                        self.samples[key].append(d)
                    if key=='two_finger':
                        # measure index-middle on first hand
                        d = ((lm[8][0]-lm[12][0])**2 + (lm[8][1]-lm[12][1])**2)**0.5
                        self.samples[key].append(d)
        self.status.config(text=f'Recorded {len(self.samples[key])} samples for {key}')
    def compute(self):
        cfg = self.cfg
        # compute mean and set thresholds slightly above mean
        for k,v in self.samples.items():
            if not v: continue
            m = sum(v)/len(v)
            if k in ('r_pinch','l_pinch'):
                cfg.PINCH_THRESHOLD = max(0.02, m*1.2)
            if k=='two_finger':
                cfg.TWO_FINGER_THRESHOLD = max(0.03, m*1.2)
        cfg.save()
        messagebox.showinfo('Saved','Calibration saved to config.json')
    def close(self):
        try: self.tracker.shutdown()
        except: pass
        self.root.destroy()

if __name__=='__main__': Calibrator()
