_# GAR Engine - Tests

import unittest
from ..src.main import GAREngine

class TestGAREngine(unittest.TestCase):

    def setUp(self):
        self.engine = GAREngine()

    def test_route(self):
        prompt = "Optimize this Python function"
        agent = self.engine.route(prompt)
        self.assertIn("agent", agent)

if __name__ == '__main__':
    unittest.main()
_
