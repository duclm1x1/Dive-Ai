"""
Dive AI — Central Connector (dive_connector.py)
=================================================
THE MASTER WIRING HUB that connects ALL Dive AI modules together.

This module lazy-loads and connects every subsystem:
  - Engine Layer: DiveEngine, ContextGuard, LaneQueue, AdaptiveRAG
  - Intelligence: IntentAnalyzer, ComplexityAnalyzer, ThinkingEngine, DualRouter
  - Skills: SkillIntelligence, SkillComboEngine, SkillRouter, 27 layer skills
  - Memory: MemoryBrain, AdvancedMemory, IdentitySystem
  - Search: SearchEngine, FileIndexer, QueryClassifier
  - Update: DiveUpdateSystem, UpdateIndexer, UpdateSuggester
  - Observability: DailyLogger, SessionReplay, Metrics
  - Security: SecurityHardening, ToolApproval
  - Orchestration: SmartOrchestrator, WorkflowEngine
  - Self-Improvement: SelfImprove, CruelSystem, ClaimsLedger

Usage:
    connector = DiveConnector.get_instance()
    status = connector.get_connectivity_status()
    engine = connector.get_engine()
    memory = connector.get_memory()
"""

import os
import sys
import time
import importlib
import traceback
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from pathlib import Path

# Ensure paths
BACKEND_DIR = Path(__file__).parent.parent.parent
CORE_DIR = BACKEND_DIR / "dive_core"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(CORE_DIR))


@dataclass
class ModuleStatus:
    """Status of a connected module."""
    name: str
    category: str  # engine, intelligence, skills, memory, search, update, observability, security, orchestrator, self_improve
    loaded: bool = False
    instance: Any = None
    error: str = ""
    load_time_ms: float = 0.0


class DiveConnector:
    """
    Central connector that wires ALL Dive AI modules together.
    
    This is THE single source of truth for what's connected.
    Every module goes through here.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'DiveConnector':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self._modules: Dict[str, ModuleStatus] = {}
        self._load_start = time.time()
        self._connect_all()
        self._load_time = time.time() - self._load_start
    
    # ================================================================
    # SAFE LOADER — try to import and instantiate, never crash
    # ================================================================
    
    def _safe_load(self, name: str, category: str, import_fn) -> ModuleStatus:
        """Safely load a module — never crash, always track."""
        status = ModuleStatus(name=name, category=category)
        start = time.time()
        try:
            instance = import_fn()
            status.loaded = True
            status.instance = instance
        except Exception as e:
            status.error = f"{type(e).__name__}: {str(e)[:200]}"
        status.load_time_ms = (time.time() - start) * 1000
        self._modules[name] = status
        return status
    
    # ================================================================
    # CONNECT ALL — wave by wave
    # ================================================================
    
    def _connect_all(self):
        """Connect all modules in dependency order."""
        self._connect_wave1_engine()
        self._connect_wave2_intelligence()
        self._connect_wave3_skills()
        self._connect_wave4_memory()
        self._connect_wave5_search_rag()
        self._connect_wave6_update()
        self._connect_wave7_observability_security()
        self._connect_wave8_orchestration()
        self._connect_wave9_self_improvement()
    
    # ── Wave 1: Engine Layer ──────────────────────────────────────
    
    def _connect_wave1_engine(self):
        self._safe_load("dive_engine", "engine", lambda: (
            __import__("dive_core.engine.dive_engine", fromlist=["DiveEngine"]).DiveEngine()
        ))
        self._safe_load("context_guard", "engine", lambda: (
            __import__("dive_core.engine.context_guard", fromlist=["ContextWindowGuard"]).ContextWindowGuard()
        ))
        self._safe_load("lane_queue", "engine", lambda: (
            __import__("dive_core.engine.lane_queue", fromlist=["LaneQueue"]).LaneQueue()
        ))
        self._safe_load("lifecycle_bridge", "engine", lambda: (
            __import__("dive_core.engine.lifecycle_bridge", fromlist=["get_lifecycle_bridge"]).get_lifecycle_bridge()
        ))
        self._safe_load("full_lifecycle", "engine", lambda: (
            __import__("dive_core.engine.full_lifecycle", fromlist=["FullLifecycleEngine"]).FullLifecycleEngine
        ))
        self._safe_load("dive_brain", "engine", lambda: (
            __import__("dive_core.engine.dive_brain", fromlist=["get_dive_brain"]).get_dive_brain()
        ))
        self._safe_load("self_debugger", "engine", lambda: (
            __import__("dive_core.engine.self_debugger", fromlist=["SelfDebugger"]).SelfDebugger.get_instance()
        ))
        self._safe_load("deployment_rules", "engine", lambda: (
            __import__("dive_core.engine.deployment_rules", fromlist=["DeploymentRules"]).DeploymentRules.get_instance()
        ))
        self._safe_load("health_check", "engine", lambda: (
            __import__("dive_core.engine.dive_health_check", fromlist=["get_health_check"]).get_health_check()
        ))
        self._safe_load("adaptive_rag", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_adaptive_rag")
        ))
        self._safe_load("claims_ledger", "engine", lambda: (
            __import__("dive_core.engine.dive_claims_ledger", fromlist=["DiveClaimsLedger"]).DiveClaimsLedger()
        ))
        self._safe_load("complexity_analyzer", "engine", lambda: (
            __import__("dive_core.engine.dive_complexity_analyzer", fromlist=["DiveComplexityAnalyzer"]).DiveComplexityAnalyzer()
        ))
        self._safe_load("context_compressor", "engine", lambda: (
            __import__("dive_core.engine.dive_context_compressor", fromlist=["DiveContextCompressor"]).DiveContextCompressor()
        ))
        self._safe_load("dependency_graph", "engine", lambda: (
            __import__("dive_core.engine.dive_dependency_graph", fromlist=["DiveDependencyGraph"]).DiveDependencyGraph()
        ))
        self._safe_load("dependency_tracker", "engine", lambda: (
            __import__("dive_core.engine.dive_dependency_tracker", fromlist=["DiveDependencyTracker"]).DiveDependencyTracker()
        ))
        self._safe_load("dual_router", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_dual_router")
        ))
        self._safe_load("effort_controller", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_effort_controller")
        ))
        self._safe_load("evidence_pack", "engine", lambda: (
            __import__("dive_core.engine.dive_evidence_pack", fromlist=["DiveEvidencePacker"]).DiveEvidencePacker()
        ))
        self._safe_load("impact_analyzer", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_impact_analyzer")
        ))
        self._safe_load("multi_strategy_retriever", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_multi_strategy_retriever")
        ))
        self._safe_load("rag_router", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_rag_router")
        ))
        self._safe_load("reranker", "engine", lambda: (
            __import__("dive_core.engine.dive_reranker", fromlist=["DiveReranker"]).DiveReranker()
        ))
        self._safe_load("strategy_selector", "engine", lambda: (
            importlib.import_module("dive_core.engine.dive_strategy_selector")
        ))
        self._safe_load("semantic_snapshot", "engine", lambda: (
            __import__("dive_core.engine.semantic_snapshot", fromlist=["SemanticSnapshot"]).SemanticSnapshot()
        ))
    
    # ── Wave 2: Intelligence Layer ────────────────────────────────
    
    def _connect_wave2_intelligence(self):
        self._safe_load("intent_analyzer", "intelligence", lambda: (
            __import__("dive_core.intent_analyzer", fromlist=["IntentAnalyzer"]).IntentAnalyzer()
        ))
        self._safe_load("algorithm_service", "intelligence", lambda: (
            __import__("dive_core.algorithm_service", fromlist=["get_algorithm_service"]).get_algorithm_service()
        ))
        self._safe_load("auto_algorithm_creator", "intelligence", lambda: (
            __import__("dive_core.auto_algorithm_creator", fromlist=["AutoAlgorithmCreator"]).AutoAlgorithmCreator()
        ))
        self._safe_load("llm_optimizer", "intelligence", lambda: (
            importlib.import_module("dive_core.llm_optimizer")
        ))
        self._safe_load("controller", "intelligence", lambda: (
            importlib.import_module("dive_core.controller")
        ))
    
    # ── Wave 3: Skills Infrastructure ─────────────────────────────
    
    def _connect_wave3_skills(self):
        self._safe_load("skill_intelligence", "skills", lambda: (
            __import__("dive_core.skills.skill_intelligence", fromlist=["SkillRegistry"]).SkillRegistry()
        ))
        self._safe_load("skill_combo_engine", "skills", lambda: (
            __import__("dive_core.skills.skill_combo_engine", fromlist=["SkillComboEngine"]).SkillComboEngine()
        ))
        self._safe_load("skill_router", "skills", lambda: (
            importlib.import_module("dive_core.skills.skill_router")
        ))
        self._safe_load("skill_generator", "skills", lambda: (
            __import__("dive_core.skills.skill_generator", fromlist=["SkillGenerator"]).SkillGenerator()
        ))
        self._safe_load("skill_installer", "skills", lambda: (
            __import__("dive_core.skills.skill_installer", fromlist=["SkillInstaller"]).SkillInstaller()
        ))
        self._safe_load("skill_registry", "skills", lambda: (
            __import__("dive_core.skills.skill_registry", fromlist=["SkillRegistry"]).SkillRegistry()
        ))
        self._safe_load("agent_skills_standard", "skills", lambda: (
            __import__("dive_core.skills.agent_skills_standard", fromlist=["AgentSkillsStandard"]).AgentSkillsStandard()
        ))
        self._safe_load("proactive_heartbeat", "skills", lambda: (
            __import__("dive_core.skills.proactive_heartbeat", fromlist=["ProactiveHeartbeat"]).ProactiveHeartbeat()
        ))
        self._safe_load("sandbox_executor", "skills", lambda: (
            __import__("dive_core.skills.sandbox_executor", fromlist=["SandboxExecutor"]).SandboxExecutor()
        ))
        
        # Load Layer 1-6 skills (27 total)
        layer_skills = [
            # Layer 1: Strategic Routing
            ("layer1_goal_aware_routing", "dive_core.skills.layer1_goalawarerouting"),
            ("layer1_hierarchical_execution", "dive_core.skills.layer1_hierarchicalexecution"),
            ("layer1_parallel_task_decomposition", "dive_core.skills.layer1_paralleltaskdecomposition"),
            ("layer1_strategic_routing", "dive_core.skills.layer1_strategicrouting"),
            # Layer 2: Dynamic Compute
            ("layer2_dynamic_compute_allocation", "dive_core.skills.layer2_dynamiccomputeallocation"),
            ("layer2_dynamic_neural_arch_search", "dive_core.skills.layer2_dynamicneuralarchitecturesearch"),
            ("layer2_hierarchical_dependency_solver", "dive_core.skills.layer2_hierarchicaldependencysolver"),
            ("layer2_intelligent_token_scheduling", "dive_core.skills.layer2_intelligenttokenscheduling"),
            # Layer 3: Context Management
            ("layer3_chunk_preserving_context", "dive_core.skills.layer3_chunkpreservingcontext"),
            ("layer3_context_aware_caching", "dive_core.skills.layer3_contextawarecaching"),
            ("layer3_contextual_compression", "dive_core.skills.layer3_contextualcompression"),
            ("layer3_dynamic_retrieval_context", "dive_core.skills.layer3_dynamicretrievalcontext"),
            ("layer3_semantic_context_weaving", "dive_core.skills.layer3_semanticcontextweaving"),
            ("layer3_structured_hierarchical_context", "dive_core.skills.layer3_structuredhierarchicalcontext"),
            ("layer3_token_accounting", "dive_core.skills.layer3_tokenaccounting"),
            # Layer 4: Parallel Execution
            ("layer4_distributed_processing", "dive_core.skills.layer4_distributedprocessing"),
            ("layer4_fault_tolerance", "dive_core.skills.layer4_faulttolerance"),
            ("layer4_load_balancing", "dive_core.skills.layer4_loadbalancing"),
            ("layer4_multi_agent_coordination", "dive_core.skills.layer4_multiagentcoordination"),
            ("layer4_parallel_execution", "dive_core.skills.layer4_parallelexecution"),
            # Layer 5: Verification
            ("layer5_automated_error_handling", "dive_core.skills.layer5_automatederrorhandling"),
            ("layer5_exhaustive_verification", "dive_core.skills.layer5_exhaustiveverification"),
            ("layer5_formal_program_verification", "dive_core.skills.layer5_formalprogramverification"),
            ("layer5_multi_version_proofs", "dive_core.skills.layer5_multiversionproofs"),
            ("layer5_universal_formal_baseline", "dive_core.skills.layer5_universalformalbaseline"),
            # Layer 6: Learning
            ("layer6_adaptive_learning", "dive_core.skills.layer6_adaptivelearning"),
            ("layer6_cross_layer_learning", "dive_core.skills.layer6_crosslayerlearning"),
            ("layer6_federated_expert_learning", "dive_core.skills.layer6_federatedexpertlearning"),
            ("layer6_feedback_based_learning", "dive_core.skills.layer6_feedbackbasedlearning"),
            ("layer6_knowledge_sharing", "dive_core.skills.layer6_knowledgesharing"),
        ]
        for skill_name, module_path in layer_skills:
            self._safe_load(skill_name, "layer_skill", lambda mp=module_path: (
                __import__(mp)
            ))
    
    # ── Wave 4: Memory System ─────────────────────────────────────
    
    def _connect_wave4_memory(self):
        self._safe_load("memory_brain", "memory", lambda: (
            importlib.import_module("dive_core.memory.dive_memory_brain")
        ))
        self._safe_load("advanced_memory", "memory", lambda: (
            __import__("dive_core.memory.advanced_memory", fromlist=["AdvancedMemory"]).AdvancedMemory()
        ))
        self._safe_load("identity_system", "memory", lambda: (
            __import__("dive_core.memory.identity_system", fromlist=["IdentitySystem"]).IdentitySystem()
        ))
        self._safe_load("memory_change_tracker", "memory", lambda: (
            __import__("dive_core.memory.dive_memory_change_tracker", fromlist=["MemoryChangeTracker"]).MemoryChangeTracker()
        ))
        self._safe_load("memory_indexer", "memory", lambda: (
            __import__("dive_core.memory.dive_memory_indexer", fromlist=["DiveMemoryIndexer"]).DiveMemoryIndexer()
        ))
        self._safe_load("update_memory_integration", "memory", lambda: (
            importlib.import_module("dive_core.memory.dive_update_memory_integration")
        ))
    
    # ── Wave 5: Search + RAG ──────────────────────────────────────
    
    def _connect_wave5_search_rag(self):
        self._safe_load("search_engine", "search", lambda: (
            importlib.import_module("dive_core.search.dive_search_engine")
        ))
        self._safe_load("search_index", "search", lambda: (
            importlib.import_module("dive_core.search.dive_search_index")
        ))
        self._safe_load("search_processor", "search", lambda: (
            __import__("dive_core.search.dive_search_processor", fromlist=["DiveSearchProcessor"]).DiveSearchProcessor()
        ))
        self._safe_load("file_indexer", "search", lambda: (
            __import__("dive_core.search.dive_file_indexer", fromlist=["DiveFileIndexer"]).DiveFileIndexer()
        ))
        self._safe_load("query_classifier", "search", lambda: (
            __import__("dive_core.search.dive_query_classifier", fromlist=["DiveQueryClassifier"]).DiveQueryClassifier()
        ))
    
    # ── Wave 6: DiveUpdate System ─────────────────────────────────
    
    def _connect_wave6_update(self):
        self._safe_load("update_system", "update", lambda: (
            importlib.import_module("dive_core.search.dive_update_system")
        ))
        self._safe_load("update_indexer", "update", lambda: (
            importlib.import_module("dive_core.search.dive_update_indexer")
        ))
        self._safe_load("update_suggester", "update", lambda: (
            importlib.import_module("dive_core.search.dive_update_suggester")
        ))
        self._safe_load("update_project_aware", "update", lambda: (
            importlib.import_module("dive_core.search.dive_update_project_aware")
        ))
        self._safe_load("update_search_enhanced", "update", lambda: (
            importlib.import_module("dive_core.search.dive_update_search_enhanced")
        ))
        self._safe_load("update_system_complete", "update", lambda: (
            __import__("dive_core.search.dive_update_system_complete", fromlist=["DiveUpdateSystemComplete"]).DiveUpdateSystemComplete()
        ))
    
    # ── Wave 7: Observability + Security ──────────────────────────
    
    def _connect_wave7_observability_security(self):
        self._safe_load("observability", "observability", lambda: (
            __import__("dive_core.observability.observability", fromlist=["DailyLogger"]).DailyLogger()
        ))
        self._safe_load("metrics", "observability", lambda: (
            __import__("dive_core.monitoring.metrics", fromlist=["MetricsCollector"]).MetricsCollector()
        ))
        self._safe_load("security_hardening", "security", lambda: (
            __import__("dive_core.security.security_hardening", fromlist=["SecurityHardening"]).SecurityHardening()
        ))
        self._safe_load("security_layer", "security", lambda: (
            __import__("dive_core.security.security_layer", fromlist=["SecurityLayer"]).SecurityLayer()
        ))
        self._safe_load("tool_approval", "security", lambda: (
            __import__("dive_core.security.tool_approval", fromlist=["ToolApproval"]).ToolApproval()
        ))
        self._safe_load("advanced_features", "features", lambda: (
            importlib.import_module("dive_core.features.advanced_features")
        ))
    
    # ── Wave 8: Orchestration ─────────────────────────────────────
    
    def _connect_wave8_orchestration(self):
        self._safe_load("smart_orchestrator", "orchestrator", lambda: (
            __import__("dive_core.orchestrator.dive_smart_orchestrator", fromlist=["DiveSmartOrchestrator"]).DiveSmartOrchestrator()
        ))
        self._safe_load("master_orchestrator", "orchestrator", lambda: (
            __import__("dive_core.master_orchestrator", fromlist=["get_master_orchestrator"]).get_master_orchestrator()
        ))
        self._safe_load("orchestrator_resilient", "orchestrator", lambda: (
            __import__("dive_core.orchestrator.dive_orchestrator_resilient", fromlist=["ResilientOrchestrator"]).ResilientOrchestrator()
        ))
        self._safe_load("workflow_engine", "orchestrator", lambda: (
            __import__("dive_core.workflow.dive_workflow_engine", fromlist=["DiveWorkflowEngine"]).DiveWorkflowEngine()
        ))
        self._safe_load("thinking_engine", "orchestrator", lambda: (
            importlib.import_module("dive_core.workflow.dive_thinking_engine")
        ))
        self._safe_load("dag_parallel", "orchestrator", lambda: (
            __import__("dive_core.workflow.dive_dag_parallel", fromlist=["DiveDAGParallel"]).DiveDAGParallel()
        ))
        self._safe_load("reasoning_trace", "orchestrator", lambda: (
            __import__("dive_core.workflow.dive_reasoning_trace", fromlist=["DiveReasoningTrace"]).DiveReasoningTrace(task="system_init")
        ))
    
    # ── Wave 9: Self-Improvement ──────────────────────────────────
    
    def _connect_wave9_self_improvement(self):
        self._safe_load("self_improve", "self_improve", lambda: (
            importlib.import_module("dive_core.dive_ai_self_improve")
        ))
        self._safe_load("cruel_system", "self_improve", lambda: (
            __import__("dive_core.dive_cruel_system", fromlist=["DiveCRUELSystem"]).DiveCRUELSystem()
        ))
        self._safe_load("interrupt_handler", "self_improve", lambda: (
            __import__("dive_core.dive_interrupt_handler", fromlist=["InterruptHandler"]).InterruptHandler()
        ))
        self._safe_load("agent_fleet", "self_improve", lambda: (
            __import__("dive_core.dive_agent_fleet", fromlist=["DiveAgentFleet"]).DiveAgentFleet()
        ))
        self._safe_load("agent_monitor", "self_improve", lambda: (
            __import__("dive_core.dive_agent_monitor", fromlist=["DiveAgentMonitor"]).DiveAgentMonitor()
        ))
        self._safe_load("monitoring_dashboard", "self_improve", lambda: (
            __import__("dive_core.dive_monitoring_dashboard", fromlist=["DiveMonitoringDashboard"]).DiveMonitoringDashboard()
        ))
        self._safe_load("plugin_system", "self_improve", lambda: (
            __import__("dive_core.dive_plugin_system", fromlist=["PluginSystem"]).PluginSystem()
        ))
    
    # ================================================================
    # ACCESSORS — get specific modules
    # ================================================================
    
    def get(self, name: str) -> Any:
        """Get a loaded module instance by name."""
        status = self._modules.get(name)
        if status and status.loaded:
            return status.instance
        return None
    
    def get_engine(self):
        """Get DiveEngine instance."""
        return self.get("dive_engine")
    
    def get_brain(self):
        """Get DiveBrain instance."""
        return self.get("dive_brain")
    
    def get_memory(self):
        """Get DiveMemoryBrain instance."""
        return self.get("memory_brain")
    
    def get_search(self):
        """Get DiveSearchEngine instance."""
        return self.get("search_engine")
    
    def get_intent_analyzer(self):
        """Get IntentAnalyzer instance."""
        return self.get("intent_analyzer")
    
    def get_skill_intelligence(self):
        """Get SkillIntelligence instance."""
        return self.get("skill_intelligence")
    
    def get_skill_combo(self):
        """Get SkillComboEngine instance."""
        return self.get("skill_combo_engine")
    
    def get_skill_router(self):
        """Get SkillRouter instance."""
        return self.get("skill_router")
    
    def get_thinking_engine(self):
        """Get ThinkingEngine instance."""
        return self.get("thinking_engine")
    
    def get_orchestrator(self):
        """Get SmartOrchestrator instance."""
        return self.get("smart_orchestrator")
    
    def get_update_system(self):
        """Get DiveUpdateSystem instance."""
        return self.get("update_system")
    
    def get_security(self):
        """Get SecurityHardening instance."""
        return self.get("security_hardening")
    
    def get_observability(self):
        """Get DailyLogger instance."""
        return self.get("observability")
    
    # ================================================================
    # STATUS & STATS
    # ================================================================
    
    def get_connectivity_status(self) -> Dict[str, Any]:
        """Get full connectivity status of all modules."""
        categories = {}
        for name, status in self._modules.items():
            cat = status.category
            if cat not in categories:
                categories[cat] = {"loaded": 0, "failed": 0, "modules": {}}
            if status.loaded:
                categories[cat]["loaded"] += 1
            else:
                categories[cat]["failed"] += 1
            categories[cat]["modules"][name] = {
                "loaded": status.loaded,
                "error": status.error if not status.loaded else "",
                "load_time_ms": round(status.load_time_ms, 2),
            }
        
        total = len(self._modules)
        loaded = sum(1 for s in self._modules.values() if s.loaded)
        failed = total - loaded
        
        return {
            "total_modules": total,
            "connected": loaded,
            "disconnected": failed,
            "connectivity_rate": round((loaded / total * 100) if total > 0 else 0, 1),
            "total_load_time_ms": round(self._load_time * 1000, 1),
            "categories": categories,
        }
    
    def get_disconnected(self) -> List[Dict[str, str]]:
        """Get list of all disconnected modules with error details."""
        return [
            {"name": name, "category": s.category, "error": s.error}
            for name, s in self._modules.items()
            if not s.loaded
        ]
    
    def get_connected_names(self) -> List[str]:
        """Get names of all connected modules."""
        return [name for name, s in self._modules.items() if s.loaded]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connector statistics."""
        status = self.get_connectivity_status()
        return {
            "total_modules": status["total_modules"],
            "connected": status["connected"],
            "disconnected": status["disconnected"],
            "connectivity_rate": status["connectivity_rate"],
            "load_time_ms": status["total_load_time_ms"],
            "categories": {
                cat: {"loaded": info["loaded"], "failed": info["failed"]}
                for cat, info in status["categories"].items()
            },
        }
    
    def print_status(self):
        """Print formatted connectivity status."""
        status = self.get_connectivity_status()
        print(f"\n{'='*60}")
        print(f"🔌 Dive AI Connector — {status['connected']}/{status['total_modules']} modules connected ({status['connectivity_rate']}%)")
        print(f"{'='*60}")
        for cat, info in status["categories"].items():
            icon = "✅" if info["failed"] == 0 else "⚠️"
            print(f"  {icon} {cat}: {info['loaded']}/{info['loaded']+info['failed']} connected")
            for mod_name, mod_info in info["modules"].items():
                if not mod_info["loaded"]:
                    print(f"      ❌ {mod_name}: {mod_info['error'][:80]}")
        print(f"{'='*60}\n")


# ── Singleton access ──────────────────────────────────────
_connector_instance = None

def get_connector() -> DiveConnector:
    """Get or create the global DiveConnector instance."""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = DiveConnector()
    return _connector_instance
