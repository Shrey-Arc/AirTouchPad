import time, json, os
from utils.config import Config
from handtracker import HandTracker
# import the package's gesturelogic implementation
from gesturelogic import GestureEngine
from eventmapper import EventMapper
STATUS = os.path.join(os.path.dirname(__file__), 'status.json')

def write_status(d):
    try:
        with open(STATUS, 'w') as f: json.dump(d,f)
    except: pass

def main():
    cfg = Config()
    tracker = HandTracker(cfg)
    engine = GestureEngine(cfg)
    mapper = EventMapper(cfg)
    try:
        while True:
            hands, frame = tracker.step()
            gestures = engine.update(hands)
            if gestures:
                for g in gestures:
                    mapper.handle(g)
            write_status({'time':time.time(),'gestures':gestures})
            time.sleep(0.01)
    except KeyboardInterrupt:
        print('exiting')
    finally:
        tracker.shutdown()

if __name__ == '__main__':
    main()
