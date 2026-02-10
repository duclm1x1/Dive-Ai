"""
Dive AI Algorithm Service — Central integration layer.
Connects: AutoAlgorithmCreator + SkillRegistry + Hot Deploy + Agent Core + Gateway

This is the SINGLE entry point for all algorithm operations in Dive AI.
All systems (agent, gateway, AI skills) route through this service.
"""
import os, sys, json, time, importlib, importlib.util, inspect, traceback
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

# Ensure backend path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from dive_core.auto_algorithm_creator import AutoAlgorithmCreator, AlgorithmBlueprint
from dive_core.skills.skill_registry import SkillRegistry


@dataclass
class DeployedAlgorithm:
    """A hot-deployed algorithm instance ready for execution."""
    name: str
    class_name: str
    instance: Any
    file_path: str
    deployed_at: str
    call_count: int = 0
    total_cost: float = 0.0
    last_result: Optional[Dict] = None


class AlgorithmService:
    """
    Central Algorithm Service — the brain connecting everything.

    Usage:
        service = AlgorithmService.get_instance()
        service.create_algorithm(name, description, logic_type, logic_code)
        service.deploy("my-algo")
        result = service.execute("my-algo", {"input": "data"})
        service.list_all()  # both skills + auto-created algos
    """

    _instance = None  # Singleton

    @classmethod
    def get_instance(cls) -> 'AlgorithmService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Core components
        self.creator = AutoAlgorithmCreator()
        self.registry = SkillRegistry()
        self._deployed: Dict[str, DeployedAlgorithm] = {}
        self._execution_log: List[Dict] = []

        # Auto-load existing registered algorithms on startup
        self._auto_load_skills()
        self._auto_deploy_existing()

    # ══════════════════════════════════════════════════
    # SKILL REGISTRATION (load all built-in skills)
    # ══════════════════════════════════════════════════

    def _auto_load_skills(self):
        """Load all built-in skills into the registry."""
        skills_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills")
        categories = [
            "browser", "search", "communication", "devops",
            "ai", "productivity", "media", "finance",
            "smart_home", "coding",
        ]
        loaded = 0
        for cat in categories:
            cat_dir = os.path.join(skills_dir, cat)
            if not os.path.isdir(cat_dir):
                continue
            for fname in os.listdir(cat_dir):
                if fname.endswith("_skill.py") and not fname.startswith("__"):
                    try:
                        mod_name = fname[:-3]
                        mod_path = os.path.join(cat_dir, fname)
                        spec = importlib.util.spec_from_file_location(
                            f"skill_{cat}_{mod_name}", mod_path
                        )
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)

                        # Find skill classes
                        for attr_name, attr in inspect.getmembers(mod, inspect.isclass):
                            if (hasattr(attr, 'execute') and hasattr(attr, 'spec')
                                    and attr_name != 'BaseSkill'
                                    and 'Base' not in attr_name):
                                try:
                                    instance = attr()
                                    self.registry.register(instance)
                                    loaded += 1
                                except Exception:
                                    pass
                    except Exception:
                        pass

        self._skill_count = loaded

    def _auto_deploy_existing(self):
        """Deploy all previously-created auto algorithms."""
        deployed = 0
        for algo_info in self.creator.list_algorithms():
            try:
                result = self.creator.deploy(algo_info["name"])
                if result.get("success") and result.get("instance"):
                    self._deployed[algo_info["name"]] = DeployedAlgorithm(
                        name=algo_info["name"],
                        class_name=algo_info.get("class_name", ""),
                        instance=result["instance"],
                        file_path=algo_info.get("file_path", ""),
                        deployed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    deployed += 1
            except Exception:
                pass

        self._auto_deployed_count = deployed

    # ══════════════════════════════════════════════════
    # CREATE (from blueprint or quick params)
    # ══════════════════════════════════════════════════

    def create_algorithm(self, name: str, description: str,
                         logic_type: str = "transform",
                         logic_code: str = "",
                         tags: List[str] = None,
                         verifier_type: str = "none",
                         input_schema: Dict = None,
                         output_schema: Dict = None,
                         cost_per_call: float = 0.0,
                         auto_deploy: bool = True) -> Dict[str, Any]:
        """Create a new algorithm and optionally auto-deploy it."""
        blueprint = AlgorithmBlueprint(
            name=name,
            description=description,
            logic_type=logic_type,
            logic_code=logic_code,
            tags=tags or [name.lower()],
            verifier_type=verifier_type,
            input_schema=input_schema or {},
            output_schema=output_schema or {},
            cost_per_call=cost_per_call,
        )
        result = self.creator.create(blueprint)

        if result.get("success") and auto_deploy:
            deploy_result = self.deploy(name)
            result["deployed"] = deploy_result.get("success", False)
            result["deploy_status"] = deploy_result.get("test_status", "unknown")

        self._log("create", name, result)
        return result

    def create_from_blueprint(self, blueprint: AlgorithmBlueprint,
                              auto_deploy: bool = True) -> Dict:
        """Create from a full blueprint object."""
        result = self.creator.create(blueprint)
        if result.get("success") and auto_deploy:
            deploy_result = self.deploy(blueprint.name)
            result["deployed"] = deploy_result.get("success", False)
        self._log("create_blueprint", blueprint.name, result)
        return result

    # ══════════════════════════════════════════════════
    # DEPLOY (hot-load into runtime)
    # ══════════════════════════════════════════════════

    def deploy(self, name: str) -> Dict[str, Any]:
        """Deploy an algorithm into the running system."""
        result = self.creator.deploy(name)
        if result.get("success") and result.get("instance"):
            self._deployed[name] = DeployedAlgorithm(
                name=name,
                class_name=result.get("class", ""),
                instance=result["instance"],
                file_path=self.creator.get_algorithm(name).get("file_path", ""),
                deployed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        self._log("deploy", name, result)
        return {k: v for k, v in result.items() if k != "instance"}

    def undeploy(self, name: str) -> bool:
        """Remove an algorithm from the running system."""
        if name in self._deployed:
            del self._deployed[name]
            self._log("undeploy", name, {"success": True})
            return True
        return False

    # ══════════════════════════════════════════════════
    # EXECUTE (run algorithm or skill)
    # ══════════════════════════════════════════════════

    def execute(self, name: str, inputs: Dict = None,
                context: Dict = None) -> Dict[str, Any]:
        """
        Execute ANY algorithm or skill by name.
        Checks deployed auto-algos first, then skill registry.
        This is the unified execution gateway.
        """
        inputs = inputs or {}
        start_time = time.time()

        # 1. Check deployed auto-algorithms
        if name in self._deployed:
            algo = self._deployed[name]
            try:
                result = algo.instance.execute(inputs, context)
                algo.call_count += 1
                elapsed = round((time.time() - start_time) * 1000, 1)
                algo.last_result = {
                    "status": result.status,
                    "data": result.data,
                    "elapsed_ms": elapsed,
                }
                output = {
                    "success": result.status == "success",
                    "source": "auto_algorithm",
                    "name": name,
                    "status": result.status,
                    "data": result.data,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {},
                    "elapsed_ms": elapsed,
                    "call_count": algo.call_count,
                }
                self._log("execute", name, output)
                return output
            except Exception as e:
                return {
                    "success": False, "source": "auto_algorithm",
                    "name": name, "error": str(e),
                }

        # 2. Check skill registry
        skill = self.registry.get(name)
        if skill:
            try:
                result = skill.execute(inputs, context)
                elapsed = round((time.time() - start_time) * 1000, 1)
                output = {
                    "success": result.status == "success",
                    "source": "skill_registry",
                    "name": name,
                    "status": result.status,
                    "data": result.data,
                    "metadata": result.metadata if hasattr(result, 'metadata') else {},
                    "elapsed_ms": elapsed,
                }
                self._log("execute_skill", name, output)
                return output
            except Exception as e:
                return {
                    "success": False, "source": "skill_registry",
                    "name": name, "error": str(e),
                }

        # 3. Not found
        return {
            "success": False, "error": f"Algorithm/skill '{name}' not found",
            "available": self.list_names(),
        }

    # ══════════════════════════════════════════════════
    # QUERY (list, search, stats)
    # ══════════════════════════════════════════════════

    def list_all(self) -> Dict[str, Any]:
        """List everything: skills + auto algorithms + deployed."""
        skills = []
        for s in self.registry.list_all():
            if isinstance(s, dict):
                skills.append(s)
            else:
                skills.append({"name": str(s)})

        auto_algos = self.creator.list_algorithms()
        deployed = [
            {
                "name": d.name, "class": d.class_name,
                "calls": d.call_count, "deployed_at": d.deployed_at,
            }
            for d in self._deployed.values()
        ]

        return {
            "skills": skills,
            "auto_algorithms": auto_algos,
            "deployed": deployed,
            "counts": {
                "skills": len(skills),
                "auto_algorithms": len(auto_algos),
                "deployed": len(deployed),
                "total": len(skills) + len(auto_algos),
            }
        }

    def list_names(self) -> List[str]:
        """List all available names (skills + deployed algos)."""
        names = set()
        for s in self.registry.list_all():
            if isinstance(s, dict):
                names.add(s.get("name", ""))
            else:
                names.add(str(s))
        for d in self._deployed:
            names.add(d)
        return sorted(names)

    def get_info(self, name: str) -> Optional[Dict]:
        """Get info about a specific algorithm or skill."""
        # Check auto-algo registry
        algo_info = self.creator.get_algorithm(name)
        if algo_info:
            deployed_info = self._deployed.get(name)
            return {
                "type": "auto_algorithm",
                "info": algo_info,
                "deployed": deployed_info is not None,
                "call_count": deployed_info.call_count if deployed_info else 0,
                "last_result": deployed_info.last_result if deployed_info else None,
            }

        # Check skill registry
        skill = self.registry.get(name)
        if skill:
            return {
                "type": "skill",
                "name": name,
                "spec": {
                    "description": getattr(skill.spec, 'description', ''),
                    "version": getattr(skill.spec, 'version', '1.0.0'),
                    "category": str(getattr(skill.spec, 'category', 'custom')),
                    "tags": getattr(skill.spec, 'tags', []),
                } if hasattr(skill, 'spec') else {},
            }

        return None

    def get_stats(self) -> Dict:
        """Get comprehensive stats."""
        creator_stats = self.creator.get_stats()
        deployed_calls = sum(d.call_count for d in self._deployed.values())

        return {
            "skills_loaded": self._skill_count,
            "auto_algorithms_created": creator_stats["total_algorithms"],
            "auto_algorithms_deployed": len(self._deployed),
            "total_executions": deployed_calls,
            "execution_log_size": len(self._execution_log),
            "categories": creator_stats.get("categories", {}),
            "with_verifiers": creator_stats.get("with_verifiers", 0),
        }

    def search(self, query: str) -> List[Dict]:
        """Search for algorithms/skills by query."""
        results = []
        query_lower = query.lower()

        # Search skills
        for skill_info in self.registry.list_all():
            name = skill_info.get("name", "") if isinstance(skill_info, dict) else str(skill_info)
            if query_lower in name.lower():
                results.append({"name": name, "type": "skill", "match": "name"})

        # Search auto algorithms
        for algo in self.creator.list_algorithms():
            if (query_lower in algo.get("name", "").lower() or
                    query_lower in algo.get("description", "").lower() or
                    any(query_lower in t for t in algo.get("tags", []))):
                results.append({
                    "name": algo["name"], "type": "auto_algorithm",
                    "description": algo.get("description", ""),
                })

        return results

    # ══════════════════════════════════════════════════
    # DELETE
    # ══════════════════════════════════════════════════

    def delete_algorithm(self, name: str) -> Dict:
        """Delete an auto-created algorithm (undeploy + remove)."""
        self.undeploy(name)
        deleted = self.creator.delete_algorithm(name)
        return {"success": deleted, "name": name}

    # ══════════════════════════════════════════════════
    # INTERNAL
    # ══════════════════════════════════════════════════

    def _log(self, action: str, name: str, result: Dict):
        """Log an action."""
        self._execution_log.append({
            "action": action, "name": name,
            "success": result.get("success", False),
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        # Keep last 100
        if len(self._execution_log) > 100:
            self._execution_log = self._execution_log[-100:]

    def get_log(self, limit: int = 20) -> List[Dict]:
        """Get recent execution log."""
        return self._execution_log[-limit:]


# ══════════════════════════════════════════════════
# Module-level convenience (singleton access)
# ══════════════════════════════════════════════════

def get_algorithm_service() -> AlgorithmService:
    """Get the global AlgorithmService singleton."""
    return AlgorithmService.get_instance()
