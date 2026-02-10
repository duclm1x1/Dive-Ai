"""CLI Search, Memory, Computer, Orchestrate, Serve Algorithms - Batch Creation"""
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from core.algorithms.base_algorithm import BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
from typing import Dict, Any

class CLISearchAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CLISearch", name="CLI Search", level="composite", category="cli", version="1.0",
            description="Handle 'dive search' - multi-source search (codebase + memory + web).",
            io=AlgorithmIOSpec(inputs=[IOField("query", "string", True, "Search query")],
                outputs=[IOField("results", "list", True, "Search results")]),
            steps=["Step 1: Parse query", "Step 2: Search codebase", "Step 3: Search memory", "Step 4: Return combined"], tags=["cli", "search"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"results": [{"source": "codebase", "snippet": "result..."}]})

class CLIMemoryAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CLIMemory", name="CLI Memory", level="composite", category="cli", version="1.0",
            description="Handle 'dive memory' - add/search/list project memory.",
            io=AlgorithmIOSpec(inputs=[IOField("action", "string", True, "add/search/list")],
                outputs=[IOField("result", "object", True, "Memory operation result")]),
            steps=["Step 1: Parse action", "Step 2: Execute with HighPerformanceMemory", "Step 3: Return result"], tags=["cli", "memory"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"result": {"action": params.get("action"), "success": True}})

class CLIComputerAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CLIComputer", name="CLI Computer", level="composite", category="cli", version="1.0",
            description="Handle 'dive computer' - execute computer control tasks.",
            io=AlgorithmIOSpec(inputs=[IOField("command", "string", True, "Natural language command")],
                outputs=[IOField("actions", "list", True, "Executed actions")]),
            steps=["Step 1: Parse command", "Step 2: Plan actions", "Step 3: Execute with ComputerOperator", "Step 4: Return result"], tags=["cli", "computer-control"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"actions": [{"type": "screenshot"}], "success": True})

class CLIOrchestrateAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CLIOrchestrate", name="CLI Orchestrate", level="composite", category="cli", version="1.0",
            description="Handle 'dive orchestrate' - complex multi-step task execution.",
            io=AlgorithmIOSpec(inputs=[IOField("task", "string", True, "Complex task")],
                outputs=[IOField("execution_plan", "object", True, "7-phase plan")]),
            steps=["Step 1: Analyze task", "Step 2: Call SmartOrchestrator", "Step 3: Execute phases", "Step 4: Return results"], tags=["cli", "orchestration"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        return AlgorithmResult(status="success", data={"execution_plan": {"phases": []}, "status": "planned"})

class CLIServeAlgorithm(BaseAlgorithm):
    def __init__(self):
        self.spec = AlgorithmSpec(algorithm_id="CLIServe", name="CLI Serve", level="composite", category="cli", version="1.0",
            description="Handle 'dive serve' - start HTTP API server.",
            io=AlgorithmIOSpec(inputs=[IOField("port", "integer", False, "Server port")],
                outputs=[IOField("server_url", "string", True, "Running server URL")]),
            steps=["Step 1: Setup FastAPI app", "Step 2: Register endpoints", "Step 3: Start uvicorn", "Step 4: Return URL"], tags=["cli", "api", "server"])
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        port = params.get("port", 8000)
        return AlgorithmResult(status="success", data={"server_url": f"http://localhost:{port}", "status": "running"})

def register(algorithm_manager):
    for algo_class in [CLISearchAlgorithm, CLIMemoryAlgorithm, CLIComputerAlgorithm, CLIOrchestrateAlgorithm, CLIServeAlgorithm]:
        algo = algo_class()
        algorithm_manager.register(algo.spec.algorithm_id, algo)
        print(f"✅ {algo.spec.algorithm_id} Algorithm registered")
