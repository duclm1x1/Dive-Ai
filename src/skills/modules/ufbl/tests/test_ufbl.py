_# UFBL Engine - Tests

import unittest
from ..src.main import UFBLEngine

class TestUFBLEngine(unittest.TestCase):

    def setUp(self):
        self.engine = UFBLEngine()

    def test_process_feedback(self):
        feedback = {"rating": 5, "comment": "Great work!"}
        result = self.engine.process_feedback(feedback)
        self.assertEqual(result["status"], "processed")

if __name__ == '__main__':
    unittest.main()
_
