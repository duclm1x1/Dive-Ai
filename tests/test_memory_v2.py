import unittest
import os
from src.memory_v2 import DiveMemorySystem, MemoryType, KnowledgeNode, KnowledgeEdge

class TestDiveMemorySystemV2(unittest.TestCase):

    def setUp(self):
        self.db_paths = [
            "episodic_memory.db",
            "semantic_memory.db",
            "procedural_memory.db",
            "knowledge_graph.db"
        ]
        self.memory = DiveMemorySystem()

    def tearDown(self):
        self.memory.cleanup()
        for db_path in self.db_paths:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_initialization(self):
        self.assertEqual(self.memory.version, "2.0.0")
        self.assertIsNotNone(self.memory.episodic_store)
        self.assertIsNotNone(self.memory.semantic_store)
        self.assertIsNotNone(self.memory.procedural_store)
        self.assertIsNotNone(self.memory.knowledge_graph)

    def test_store_and_recall_episodic_memory(self):
        content = "User logged in successfully"
        self.memory.store_episodic_memory(content, tags=["login", "user"])
        results = self.memory.recall_memory("logged in", memory_type=MemoryType.EPISODIC)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, content)
        self.assertEqual(results[0].memory_type, MemoryType.EPISODIC)

    def test_store_and_recall_semantic_memory(self):
        content = "Dive AI is an autonomous agent framework"
        self.memory.store_semantic_memory(content, tags=["definition", "dive-ai"])
        results = self.memory.recall_memory("Dive AI", memory_type=MemoryType.SEMANTIC)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, content)

    def test_store_and_recall_procedural_memory(self):
        content = "How to build the project: run build.bat"
        self.memory.store_procedural_memory(content, tags=["build", "instructions"])
        results = self.memory.recall_memory("build the project", memory_type=MemoryType.PROCEDURAL)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, content)

    def test_add_and_query_knowledge_graph(self):
        self.memory.add_knowledge("Dive AI", "is_a", "Framework")
        self.memory.add_knowledge("Dive AI", "has_component", "Dive Coder")

        related_nodes = self.memory.query_knowledge("Dive AI")
        self.assertGreater(len(related_nodes), 0)
        
        labels = [node.label for node in related_nodes]
        self.assertIn("Framework", labels)
        self.assertIn("Dive Coder", labels)

    def test_working_memory(self):
        self.memory.store_working_memory("current_task", "task-123")
        current_task = self.memory.retrieve_working_memory("current_task")
        self.assertEqual(current_task, "task-123")
        self.memory.clear_working_memory()
        self.assertIsNone(self.memory.retrieve_working_memory("current_task"))

    def test_memory_stats(self):
        stats = self.memory.get_memory_stats()
        self.assertEqual(stats["version"], "2.0.0")
        self.assertEqual(stats["working_memory_size"], 0)
        self.assertEqual(stats["episodic_store"], "Active")

if __name__ == '__main__':
    unittest.main()
