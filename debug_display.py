import cv2, time
from handtracker import HandTracker
from gesturelogic import GestureEngine
from utils.config import Config

def run_overlay():
    cfg = Config(); tracker = HandTracker(cfg); engine = GestureEngine(cfg)
    win = 'Debug'; cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    try:
        while True:
            hands, frame = tracker.step()
            if frame is None:
                time.sleep(0.02); continue
            gestures = engine.update(hands)
            if gestures:
                for i,g in enumerate(gestures):
                    cv2.putText(frame, str(g.get('type')), (10,30+i*30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            cv2.imshow(win, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
    except KeyboardInterrupt:
        pass
    finally:
        try: cv2.destroyAllWindows()
        except: pass

if __name__=='__main__': run_overlay()
