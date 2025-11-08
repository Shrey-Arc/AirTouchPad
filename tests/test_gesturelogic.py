import unittest
import time
from gesturelogic import GestureEngine
from utils.config import Config

class TestGestureEngine(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.config.PINCH_THRESHOLD = 0.1
        self.config.CONFIDENCE_THRESHOLD = 0.5
        self.config.COOLDOWN = 0.1
        self.engine = GestureEngine(self.config)

    def test_left_click(self):
        # Simulate a left click gesture
        hands = [
            ([
                [0.5, 0.5], [0.5, 0.6], [0.5, 0.7], [0.5, 0.8], [0.4, 0.5], # Thumb
                [0.6, 0.5], [0.7, 0.5], [0.8, 0.5], [0.45, 0.55] # Index
            ], 'right')
        ]
        
        # Update the engine
        gestures = self.engine.update(hands)
        
        # Check if a left click gesture was detected
        self.assertEqual(len(gestures), 1)
        self.assertEqual(gestures[0]['type'], 'left_click')

    def test_no_gesture(self):
        # Simulate no gesture
        hands = [
            ([
                [0.5, 0.5], [0.5, 0.6], [0.5, 0.7], [0.5, 0.8], [0.2, 0.5], # Thumb
                [0.8, 0.5], [0.9, 0.5], [1.0, 0.5], [0.7, 0.5] # Index
            ], 'right')
        ]
        
        # Update the engine
        gestures = self.engine.update(hands)
        
        # Check that no gesture was detected
        self.assertEqual(len(gestures), 0)

if __name__ == '__main__':
    unittest.main()
