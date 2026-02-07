_# CAC Engine - Tests

import unittest
from ..src.main import CACEngine

class TestCACEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CACEngine()

    def test_compress(self):
        text = "This is a long piece of text that needs to be compressed."
        query = "compress text"
        result = self.engine.compress(text, query)
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
_
