import unittest
from src.coder_v17 import DiveCoderV17, CodeContext, CodeLanguage, CodeQuality, GeneratedCode

class TestDiveCoderV17(unittest.TestCase):

    def setUp(self):
        self.coder = DiveCoderV17()

    def test_initialization(self):
        self.assertEqual(self.coder.version, "17.0.0")
        self.assertIn("python", self.coder.supported_languages)
        self.assertIn("javascript", self.coder.supported_languages)

    def test_generate_python_code(self):
        context = CodeContext(
            language=CodeLanguage.PYTHON,
            framework="FastAPI",
            quality_level=CodeQuality.PRODUCTION
        )
        prompt = "Create a REST API endpoint"
        result = self.coder.generate_code(prompt, context)

        self.assertIsInstance(result, GeneratedCode)
        self.assertEqual(result.language, CodeLanguage.PYTHON)
        self.assertIn("Create a REST API endpoint", result.code)
        self.assertIn("FastAPI", result.explanation)
        self.assertGreater(result.quality_score, 0.8)
        self.assertIsNotNone(result.tests)
        self.assertIsNotNone(result.documentation)
        self.assertIsNotNone(result.error_handling)

    def test_generate_javascript_code(self):
        context = CodeContext(
            language=CodeLanguage.JAVASCRIPT,
            framework="React",
            quality_level=CodeQuality.STANDARD
        )
        prompt = "Create a new component"
        result = self.coder.generate_code(prompt, context)

        self.assertIsInstance(result, GeneratedCode)
        self.assertEqual(result.language, CodeLanguage.JAVASCRIPT)
        self.assertIn("Create a new component", result.code)
        self.assertIn("React", result.explanation)
        self.assertGreater(result.quality_score, 0.7)
        self.assertIsNotNone(result.tests)

    def test_code_analysis(self):
        code = '''
# Simple python code
def hello():
    print("Hello")
'''
        context = CodeContext(language=CodeLanguage.PYTHON)
        analysis = self.coder.analyze_code(code, context)

        self.assertIn("quality_score", analysis)
        self.assertIn("complexity", analysis)
        self.assertEqual(analysis["complexity"], "Low")
        self.assertIn("Consider using logging instead of print()", analysis["issues"])
        self.assertIn("Add docstrings/documentation", analysis["suggestions"])

    def test_refactor_code(self):
        code = "def my_func(): pass"
        context = CodeContext(language=CodeLanguage.PYTHON)
        result = self.coder.refactor_code(code, context, optimization_type="readability")

        self.assertIsInstance(result, GeneratedCode)
        self.assertEqual(result.language, CodeLanguage.PYTHON)
        self.assertIn("readability", result.explanation)

if __name__ == '__main__':
    unittest.main()
