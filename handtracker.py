import cv2
import mediapipe as mp
from utils.config import Config

class HandTracker:
    def __init__(self, cfg: Config, camera_index: int = 0, model_complexity: int = 0):
        """
        Initialize hand tracker
        
        Args:
            cfg: Configuration object
            camera_index: Camera device index (default: 0)
            model_complexity: MediaPipe model complexity (0=Lite, 1=Full)
        """
        self.cfg = cfg
        self.camera_index = camera_index
        self.model_complexity = model_complexity
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {camera_index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.CAP_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.CAP_HEIGHT)
        
        # Initialize MediaPipe Hands
        self.mp = mp.solutions.hands
        self.hands = self.mp.Hands(
            max_num_hands=2,
            model_complexity=model_complexity,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.draw = mp.solutions.drawing_utils
        
        # State
        self.latest = None
        self.latest_frame = None
        
        print(f"[HandTracker] Initialized with camera {camera_index}, "
              f"model complexity {model_complexity}")
    
    def step(self):
        """
        Process one frame and return hand landmarks
        
        Returns:
            tuple: (hands_data, frame) where hands_data is list of (landmarks, label)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        
        # Convert to RGB for MediaPipe
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(img)
        
        out = []
        
        if res.multi_hand_landmarks and res.multi_handedness:
            for lm, hinfo in zip(res.multi_hand_landmarks, res.multi_handedness):
                # Extract landmarks as list of [x, y] coordinates
                pts = [[p.x, p.y] for p in lm.landmark]
                
                # Get hand label (left/right)
                label = hinfo.classification[0].label.lower()
                
                out.append((pts, label))
                
                # Draw landmarks on frame if debug overlay enabled
                if self.cfg.DEBUG_OVERLAY:
                    self.draw.draw_landmarks(
                        frame, 
                        lm, 
                        self.mp.HAND_CONNECTIONS
                    )
        
        self.latest = out if out else None
        self.latest_frame = frame
        
        return self.latest, self.latest_frame
    
    def get_camera_info(self):
        """Get camera properties"""
        if not self.cap.isOpened():
            return None
        
        return {
            'index': self.camera_index,
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'backend': self.cap.getBackendName()
        }
    
    def shutdown(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'cap') and self.cap is not None:
                self.cap.release()
        except Exception as e:
            print(f"[HandTracker] Error releasing camera: {e}")
        
        try:
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"[HandTracker] Error destroying windows: {e}")
        
        print("[HandTracker] Shutdown complete")