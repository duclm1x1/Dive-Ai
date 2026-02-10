import unittest
import asyncio
from fastapi.testclient import TestClient
from src.main_v28_7 import app

class TestIntegrationV28_7(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["version"], "28.7.0")
        self.assertEqual(data["components"]["coder"], "17.0.0")
        self.assertEqual(data["components"]["memory"], "2.0.0")
        self.assertEqual(data["components"]["skills"], "2.0.0")
        self.assertEqual(data["components"]["orchestrator"], "2.0.0")

    def test_code_generation_endpoint(self):
        response = self.client.post(
            "/api/v1/code/generate",
            json={"prompt": "test", "language": "python"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("code", data)
        self.assertEqual(data["language"], "python")

    def test_memory_store_endpoint(self):
        response = self.client.post(
            "/api/v1/memory/store",
            json={"content": "test memory", "memory_type": "episodic"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})

    def test_skill_execution_endpoint(self):
        response = self.client.post(
            "/api/v1/skills/execute",
            json={"skill_name": "data_processing", "params": {"data": {}, "operation": "test"}}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")

    def test_orchestrator_task_submission(self):
        response = self.client.post(
            "/api/v1/orchestrator/task",
            json={"name": "integration test task"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("task_id", data)

    def test_orchestrator_status_endpoint(self):
        response = self.client.get("/api/v1/orchestrator/status")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_agents"], 512)

if __name__ == '__main__':
    unittest.main()
