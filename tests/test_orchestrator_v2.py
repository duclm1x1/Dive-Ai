import unittest
import asyncio
from src.orchestrator_v2 import DiveOrchestratorV2, Task, TaskStatus

class TestDiveOrchestratorV2(unittest.TestCase):

    def setUp(self):
        self.orchestrator = DiveOrchestratorV2(num_agents=16)

    def test_initialization(self):
        self.assertEqual(self.orchestrator.version, "2.0.0")
        self.assertEqual(len(self.orchestrator.agents), 16)
        self.assertEqual(self.orchestrator.num_agents, 16)

    async def test_submit_and_execute_task(self):
        task = Task(name="Test Task")
        task_id = await self.orchestrator.submit_task(task)
        self.assertIn(task, self.orchestrator.task_queue)
        
        # This is a simplified test; in a real scenario, a worker would pick this up
        # For now, we'll just check if an agent can execute it
        executed = await self.orchestrator.execute_task(task)
        self.assertTrue(executed)
        self.assertEqual(task.status, TaskStatus.COMPLETED)

    async def test_execute_tasks_parallel(self):
        tasks = [Task(name=f"Task {i}") for i in range(4)]
        results = await self.orchestrator.execute_tasks_parallel(tasks)
        self.assertEqual(len(results), 4)
        self.assertTrue(all(results))

    async def test_execution_plan(self):
        task1 = Task(name="Task 1")
        task2 = Task(name="Task 2", dependencies=[task1.id])
        plan = self.orchestrator.create_execution_plan("Test Plan", [task1, task2])
        
        success = await self.orchestrator.execute_execution_plan(plan)
        self.assertTrue(success)
        self.assertEqual(plan.status, TaskStatus.COMPLETED)

    def test_get_cluster_status(self):
        status = self.orchestrator.get_cluster_status()
        self.assertEqual(status["total_agents"], 16)
        self.assertIn("cluster_health", status)

    def test_get_agent_metrics(self):
        agent_id = "agent_0000"
        metrics = self.orchestrator.get_agent_metrics(agent_id)
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.agent_id, agent_id)

    def run_async_test(self, coro):
        return asyncio.run(coro)

    def test_async_tests(self):
        self.run_async_test(self.test_submit_and_execute_task())
        self.run_async_test(self.test_execute_tasks_parallel())
        self.run_async_test(self.test_execution_plan())

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestDiveOrchestratorV2("test_initialization"))
    suite.addTest(TestDiveOrchestratorV2("test_get_cluster_status"))
    suite.addTest(TestDiveOrchestratorV2("test_get_agent_metrics"))
    suite.addTest(TestDiveOrchestratorV2("test_async_tests"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
