_# CLLT Engine - Tests

import unittest
from ..src.main import CLLTEngine

class TestCLLTEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CLLTEngine()

    def test_remember_and_recall(self):
        self.engine.remember("test_key", "test_value")
        value = self.engine.recall("test_key")
        self.assertEqual(value, "Recalled information")

if __name__ == '__main__':
    unittest.main()
_
