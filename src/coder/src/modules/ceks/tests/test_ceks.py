_# CEKS Engine - Tests

import unittest
from ..src.main import CEKSEngine

class TestCEKSEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CEKSEngine()

    def test_share_and_get_knowledge(self):
        self.engine.share("expert-1", "Knowledge snippet 1")
        knowledge = self.engine.get_knowledge("expert-1")
        self.assertIn("Knowledge snippet 1", knowledge)

if __name__ == '__main__':
    unittest.main()
_
