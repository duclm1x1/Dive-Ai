_# ITS Engine - Tests

import unittest
from ..src.main import ITSEngine

class TestITSEngine(unittest.TestCase):

    def setUp(self):
        self.engine = ITSEngine()

    def test_infer(self):
        prompt = "Generate a Python function"
        priority = "high"
        result = self.engine.infer(prompt, priority)
        self.assertEqual(result, "Inference result")

if __name__ == '__main__':
    unittest.main()
_
