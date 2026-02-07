_# HE Engine - Tests

import unittest
from ..src.main import HEngine

class TestHEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HEngine()

    def test_decompose_and_route(self):
        task = "Build a complete e-commerce website"
        result = self.engine.decompose_and_route(task)
        self.assertIn("subtask-1", result)

if __name__ == '__main__':
    unittest.main()
_
