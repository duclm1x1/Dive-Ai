_# FPV Engine - Tests

import unittest
from ..src.main import FPVEngine

class TestFPVEngine(unittest.TestCase):

    def setUp(self):
        self.engine = FPVEngine()

    def test_verification_success(self):
        code = "def add(a, b): return a + b"
        specification = "The function add(a, b) should return the sum of a and b."
        result, message = self.engine.verify(code, specification)
        self.assertTrue(result)
        self.assertEqual(message, "Verification successful")

if __name__ == '__main__':
    unittest.main()
_
