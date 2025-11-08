import time, math, collections
from utils.config import Config

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

class GestureEngine:
    def __init__(self, config=Config()):
        self.cfg = config
        self.history = collections.deque(maxlen=self.cfg.BUFFER_LEN)
        self.hand_hist = {}
        self.last_emitted = {}
        self.smoothed_coords = {}

    def _smooth_coords(self, key, new_coords):
        """Apply exponential moving average to smoothen coordinates."""
        if key not in self.smoothed_coords:
            self.smoothed_coords[key] = new_coords
        else:
            alpha = self.cfg.SMOOTHING_FACTOR
            self.smoothed_coords[key] = (
                alpha * new_coords[0] + (1 - alpha) * self.smoothed_coords[key][0],
                alpha * new_coords[1] + (1 - alpha) * self.smoothed_coords[key][1]
            )
        return self.smoothed_coords[key]

    def _get_velocity(self, key, new_coords, prev_coords):
        """Calculate velocity based on smoothed coordinates."""
        smoothed_new = self._smooth_coords(key, new_coords)
        smoothed_prev = self._smooth_coords(key + "_prev", prev_coords) # Store previous smoothed value
        self.smoothed_coords[key + "_prev"] = smoothed_new # Update for next frame
        
        vx = smoothed_new[0] - smoothed_prev[0]
        vy = smoothed_new[1] - smoothed_prev[1]
        return vx, vy

    def _calculate_confidence(self, *factors):
        """Calculate a combined confidence score from multiple factors."""
        score = sum(f for f in factors if f is not None) / len(factors)
        return min(1.0, max(0.0, score))

    def _summarize(self, hands):
        s = []
        if not hands: return s
        for idx, (lm, label) in enumerate(hands):
            s.append({
                'label': label, 'idx': idx,
                'thumb': lm[4], 'index': lm[8], 'middle': lm[12], 'ring': lm[16], 'pinky': lm[20], 'wrist': lm[0]
            })
        return s

    def update(self, hands):
        now = time.time()
        summary = self._summarize(hands)
        self.history.append((now, summary))
        events = []
        
        prev_summary = self.history[-2][1] if len(self.history) >= 2 else []
        cur_map = {f"{h['label']}_{h['idx']}": h for h in summary}
        prev_map = {f"{h['label']}_{h['idx']}": h for h in prev_summary}

        for key, ch in cur_map.items():
            prev_h = prev_map.get(key)
            if not prev_h: continue

            vx, vy = self._get_velocity(key, ch['wrist'], prev_h['wrist'])
            
            d_ti = dist(ch['thumb'], ch['index'])
            d_im = dist(ch['index'], ch['middle'])
            d_tm = dist(ch['thumb'], ch['middle'])

            pinch_ti = d_ti < self.cfg.PINCH_THRESHOLD
            pinch_im = d_im < self.cfg.TWO_FINGER_THRESHOLD
            pinch_tm = d_tm < self.cfg.PINCH_THRESHOLD
            
            last = self.hand_hist.get(key, {})
            
            # Gesture logic with improved confidence
            if ch['label'].startswith('r'): # Right Hand
                if pinch_ti and not last.get('pinch_ti'):
                    conf = self._calculate_confidence(1.0 - d_ti / self.cfg.PINCH_THRESHOLD, 1 if abs(vx) < 0.01 else 0.5)
                    events.append({'type': 'left_click', 'confidence': conf})
                
                if pinch_im and not last.get('pinch_im'):
                    conf = self._calculate_confidence(1.0 - d_im / self.cfg.TWO_FINGER_THRESHOLD)
                    events.append({'type': 'right_click', 'confidence': conf})

                if pinch_tm and not last.get('pinch_tm'):
                    conf = self._calculate_confidence(1.0 - d_tm / self.cfg.PINCH_THRESHOLD)
                    events.append({'type': 'middle_click', 'confidence': conf})

                # Differentiate swipes from taps
                is_stable = abs(vx) < 0.02 and abs(vy) < 0.02
                is_swipe_x = abs(vx) > 0.05 and abs(vy) < 0.03
                is_swipe_y = abs(vy) > 0.05 and abs(vx) < 0.03

                tap3 = pinch_ti and pinch_im
                if tap3 and not last.get('tap3', False) and is_stable:
                     events.append({'type': 'screenshot', 'confidence': 1.0})

                if tap3 and is_swipe_x:
                    events.append({'type': 'app_switch', 'confidence': self._calculate_confidence(abs(vx) / 0.1)})
                
                if tap3 and is_swipe_y:
                    direction = 'task_view' if vy < 0 else 'show_desktop'
                    events.append({'type': direction, 'confidence': self._calculate_confidence(abs(vy) / 0.1)})

            # Update history for the hand
            self.hand_hist[key] = {'pinch_ti': pinch_ti, 'pinch_im': pinch_im, 'pinch_tm': pinch_tm, 'tap3': tap3}

        # Filter events by confidence and apply cooldown
        final_events = []
        for e in events:
            if e.get('confidence', 0) >= self.cfg.CONFIDENCE_THRESHOLD:
                key = e['type']
                if (now - self.last_emitted.get(key, 0)) > self.cfg.COOLDOWN:
                    final_events.append(e)
                    self.last_emitted[key] = now
        
        return final_events
