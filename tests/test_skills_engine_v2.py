import unittest
import asyncio
from src.skills_engine_v2 import DiveSkillsEngine, SkillStatus, SkillCategory

class TestDiveSkillsEngineV2(unittest.TestCase):

    def setUp(self):
        self.engine = DiveSkillsEngine()

    def test_initialization(self):
        self.assertEqual(self.engine.version, "2.0.0")
        self.assertGreater(len(self.engine.skills), 0)

    def test_list_skills(self):
        skills = self.engine.list_skills()
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
        self.assertIn("name", skills[0])
        self.assertIn("category", skills[0])

    async def test_execute_code_generation_skill(self):
        result = await self.engine.execute_skill(
            "code_generation",
            prompt="Create a function",
            language="python"
        )
        self.assertEqual(result.skill_name, "code_generation")
        self.assertEqual(result.status, SkillStatus.SUCCESS)
        self.assertIn("code", result.result)

    async def test_execute_data_processing_skill(self):
        result = await self.engine.execute_skill(
            "data_processing",
            data={"key": "value"},
            operation="transform"
        )
        self.assertEqual(result.status, SkillStatus.SUCCESS)
        self.assertTrue(result.result["processed"])

    async def test_execute_automation_skill(self):
        result = await self.engine.execute_skill(
            "automation",
            workflow="my_workflow"
        )
        self.assertEqual(result.status, SkillStatus.SUCCESS)
        self.assertEqual(result.result["status"], "completed")

    async def test_execute_analysis_skill(self):
        result = await self.engine.execute_skill(
            "analysis",
            data=[1, 2, 3],
            analysis_type="statistical"
        )
        self.assertEqual(result.status, SkillStatus.SUCCESS)
        self.assertIn("insights", result.result)

    async def test_execute_skills_parallel(self):
        tasks = [
            {"skill": "code_generation", "params": {"prompt": "p1", "language": "python"}},
            {"skill": "data_processing", "params": {"data": {}, "operation": "op1"}}
        ]
        results = await self.engine.execute_skills_parallel(tasks)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].status, SkillStatus.SUCCESS)
        self.assertEqual(results[1].status, SkillStatus.SUCCESS)

    async def test_execute_workflow(self):
        workflow = [
            {"skill": "data_processing", "params": {"data": {}, "operation": "op1"}},
            {"parallel": True, "tasks": [
                {"skill": "code_generation", "params": {"prompt": "p1", "language": "python"}},
                {"skill": "analysis", "params": {"data": [], "analysis_type": "type1"}}
            ]}
        ]
        results = await self.engine.execute_workflow(workflow)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].status, SkillStatus.SUCCESS)
        self.assertEqual(results[1].status, SkillStatus.SUCCESS)
        self.assertEqual(results[2].status, SkillStatus.SUCCESS)

    def test_get_stats(self):
        stats = self.engine.get_stats()
        self.assertEqual(stats["version"], "2.0.0")
        self.assertGreaterEqual(stats["total_skills"], 4)

    def run_async_test(self, coro):
        return asyncio.run(coro)

    def test_async_tests(self):
        self.run_async_test(self.test_execute_code_generation_skill())
        self.run_async_test(self.test_execute_data_processing_skill())
        self.run_async_test(self.test_execute_automation_skill())
        self.run_async_test(self.test_execute_analysis_skill())
        self.run_async_test(self.test_execute_skills_parallel())
        self.run_async_test(self.test_execute_workflow())

if __name__ == '__main__':
    # This is a bit of a hack to run async tests in a sync test runner
    # A better solution would be to use a test runner that supports asyncio
    suite = unittest.TestSuite()
    suite.addTest(TestDiveSkillsEngineV2("test_initialization"))
    suite.addTest(TestDiveSkillsEngineV2("test_list_skills"))
    suite.addTest(TestDiveSkillsEngineV2("test_get_stats"))
    suite.addTest(TestDiveSkillsEngineV2("test_async_tests"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
