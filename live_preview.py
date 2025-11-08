import cv2
import threading
import mediapipe as mp

class LivePreview:
    def __init__(self, camera_index=0):
        self.cam = cv2.VideoCapture(camera_index, cv2.CAP_MSMF)
        self.running = True

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=2, model_complexity=0)
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def draw_landmarks(self, frame, hand_landmarks):
        h, w, _ = frame.shape
        for id, lm in enumerate(hand_landmarks.landmark):
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 5, (0,255,255), -1)  # yellow

    def loop(self):
        while self.running:
            ret, frame = self.cam.read()
            if not ret: continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb)

            if results.multi_hand_landmarks:
                for lm in results.multi_hand_landmarks:
                    self.draw_landmarks(frame, lm)

            cv2.imshow("AirTouchPad Live Preview", frame)
            cv2.waitKey(1)

        self.cam.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False
