_# DNAS Engine - Tests

import unittest
from ..src.main import DNASEngine

class TestDNASEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DNASEngine()

    def test_search(self):
        task_description = "Image classification on CIFAR-10"
        result = self.engine.search(task_description)
        self.assertIn("architecture", result)

if __name__ == '__main__':
    unittest.main()
_
