_# SR Engine - Tests

import unittest
from ..src.main import SREngine

class TestSREngine(unittest.TestCase):

    def setUp(self):
        self.engine = SREngine()

    def test_routing(self):
        prompt = "Create a new React component"
        agent = self.engine.route(prompt)
        self.assertIn("agent", agent)

if __name__ == '__main__':
    unittest.main()
_
