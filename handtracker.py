import cv2, mediapipe as mp
from utils.config import Config
class HandTracker:
    def __init__(self, cfg: Config, camera_index: int = 0):
        self.cfg = cfg
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.CAP_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.CAP_HEIGHT)
        self.mp = mp.solutions.hands
        self.hands = self.mp.Hands(max_num_hands=2, model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.draw = mp.solutions.drawing_utils
        self.latest = None
        self.latest_frame = None
    def step(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(img)
        out = []
        if res.multi_hand_landmarks and res.multi_handedness:
            for lm, hinfo in zip(res.multi_hand_landmarks, res.multi_handedness):
                pts = [[p.x, p.y] for p in lm.landmark]
                label = hinfo.classification[0].label.lower()
                out.append((pts, label))
                self.draw.draw_landmarks(frame, lm, self.mp.HAND_CONNECTIONS)
        self.latest = out if out else None
        self.latest_frame = frame
        return self.latest, self.latest_frame
    def shutdown(self):
        try: self.cap.release()
        except: pass
        try: cv2.destroyAllWindows()
        except: pass
