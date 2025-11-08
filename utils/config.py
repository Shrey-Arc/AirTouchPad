import json, os
class Config:
    DEFAULTS = {
        'CAP_WIDTH': 640,
        'CAP_HEIGHT': 480,
        'PINCH_THRESHOLD': 0.04,
        'TWO_FINGER_THRESHOLD': 0.05,
        'HOLD_TIME': 0.35,
        'BUFFER_LEN': 8,
        'COOLDOWN': 0.25,
        'DEBUG_OVERLAY': True
    }
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), '..', 'config.json')
        self.path = os.path.abspath(self.path)
        self._data = {}
        self.load()
    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path,'r') as f: self._data = json.load(f)
            except Exception:
                self._data = dict(self.DEFAULTS)
        else:
            self._data = dict(self.DEFAULTS); self.save()
    def save(self):
        try:
            with open(self.path,'w') as f: json.dump(self._data,f,indent=2)
        except Exception as e:
            print('Failed to save config:', e)
    def __getattr__(self, name):
        if name in self._data: return self._data[name]
        raise AttributeError(name)
    def __setattr__(self, name, value):
        if name in ('path','_data','DEFAULTS'):
            return super().__setattr__(name, value)
        self._data[name] = value
        self.save()
