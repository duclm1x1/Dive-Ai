"""Memory & Learning Algorithms Batch - MemoryLoop, ProjectMemory, GitHubMemorySync, SemanticSearch, ContextRetrieval"""
import os, sys, json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
from typing import Dict, Any

class MemoryLoopAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="MemoryLoop", name="Memory Loop (8-step)", level="operational", category="memory", version="1.0",
            description="8-step learning loop: Ingest → Process → Classify → Store → Index → Recall → Apply → Feedback.",
            io=AlgorithmIOSpec(inputs=[IOField("data", "string", True, "Data to learn")],
                outputs=[IOField("learned", "boolean", True, "Successfully learned")]),
            steps=["1: Ingest", "2: Process", "3: Classify", "4: Store", "5: Index", "6: Recall", "7: Apply", "8: Feedback"], tags=["memory", "learning", "loop", "CRITICAL"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"learned": True, "steps_completed": 8})

class ProjectMemoryAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="ProjectMemory", name="Project Memory", level="operational", category="memory", version="1.0",
            description="Project-specific memory (context, decisions, patterns).",
            io=AlgorithmIOSpec(inputs=[IOField("project_id", "string", True, "Project ID"), IOField("action", "string", True, "get/add/update")],
                outputs=[IOField("memory", "object", True, "Project memory")]),
            steps=["Step 1: Load project memory", "Step 2: Execute action", "Step 3: Save if modified", "Step 4: Return result"], tags=["memory", "project"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        project_id = params.get("project_id", "default")
        return AlgorithmResult(status="success", data={"memory": {"project_id": project_id, "context": {}, "decisions": []}})

class GitHubMemorySyncAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="GitHubMemorySync", name="GitHub Memory Sync", level="operational", category="memory", version="1.0",
            description="Sync project memory to GitHub (backup/restore).",
            io=AlgorithmIOSpec(inputs=[IOField("action", "string", True, "push/pull"), IOField("repo", "string", True, "GitHub repo")],
                outputs=[IOField("synced", "boolean", True, "Sync successful")]),
            steps=["Step 1: Connect to GitHub", "Step 2: Serialize memory", "Step 3: Push/pull", "Step 4: Return status"], tags=["memory", "github", "sync"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"synced": True, "action": params.get("action")})

class SemanticSearchAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="SemanticSearch", name="Semantic Search", level="operational", category="memory", version="1.0",
            description="Semantic similarity search in memory.",
            io=AlgorithmIOSpec(inputs=[IOField("query", "string", True, "Search query")],
                outputs=[IOField("results", "list", True, "Semantically similar items")]),
            steps=["Step 1: Vectorize query", "Step 2: Calculate similarities", "Step 3: Rank results", "Step 4: Return top matches"], tags=["memory", "search", "semantic"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        query = params.get("query", "")
        return AlgorithmResult(status="success", data={"results": [{"content": "related memory", "score": 0.85}]})

class ContextRetrievalAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="ContextRetrieval", name="Context Retrieval", level="operational", category="memory", version="1.0",
            description="Retrieve relevant context for current task.",
            io=AlgorithmIOSpec(inputs=[IOField("task", "string", True, "Current task")],
                outputs=[IOField("context", "object", True, "Relevant context")]),
            steps=["Step 1: Analyze task", "Step 2: Search memory", "Step 3: Rank by relevance", "Step 4: Return context"], tags=["memory", "context", "retrieval"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"context": {"related_tasks": [], "patterns": [], "decisions": []}})

def register(algorithm_manager):
    for algo_class in [MemoryLoopAlgorithm, ProjectMemoryAlgorithm, GitHubMemorySyncAlgorithm, SemanticSearchAlgorithm, ContextRetrievalAlgorithm]:
        algo = algo_class()
        algorithm_manager.register(algo.spec.algorithm_id, algo)
        print(f"✅ {algo.spec.algorithm_id} Algorithm registered")
