_# TA Engine - Tests

import unittest
from ..src.main import TAEngine

class TestTAEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TAEngine()

    def test_process(self):
        sequence = [1, 2, 3, 4, 5]
        result = self.engine.process(sequence)
        self.assertEqual(result, "Processed sequence")

if __name__ == '__main__':
    unittest.main()
_
