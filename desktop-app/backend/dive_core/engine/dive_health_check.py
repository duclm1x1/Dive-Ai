"""
Dive AI — Health Check & Auto-Connectivity Scanner
=====================================================
Runs every 1 hour to find disconnected modules, features, and skills.

This is the IMMUNE SYSTEM of Dive AI:
  1. Scans entire dive_core/ for Python modules
  2. Checks which ones are imported by the runtime
  3. Checks which ones are registered in lifecycle_bridge/DiveBrain
  4. Reports disconnected modules
  5. Optionally auto-connects simple cases

Also integrates with DiveUpdateSystemComplete to trigger updates
when new modules are detected or existing ones change.

Usage:
    checker = DiveHealthCheck.get_instance()
    report = checker.run_full_check()  # immediate check
    checker.start_periodic(interval_hours=1)  # auto-run every 1 hour
"""

import os
import sys
import time
import json
import re
import ast
import importlib
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from pathlib import Path

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@dataclass
class ModuleInfo:
    """Information about a discovered module."""
    name: str
    path: str
    relative_path: str
    has_classes: bool = False
    has_functions: bool = False
    class_names: List[str] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    size_bytes: int = 0
    is_connected: bool = False
    connected_by: str = ""          # Who imports it
    category: str = "unknown"       # engine, skills, search, etc.
    importance: str = "normal"      # low, normal, high, critical


@dataclass
class HealthReport:
    """Result of a health check scan."""
    scan_id: str = ""
    timestamp: float = field(default_factory=time.time)
    total_modules: int = 0
    connected_modules: int = 0
    disconnected_modules: int = 0
    disconnected_list: List[Dict] = field(default_factory=list)
    connected_list: List[str] = field(default_factory=list)
    category_stats: Dict[str, Dict] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    scan_duration_ms: float = 0.0
    dive_update_status: Dict = field(default_factory=dict)


class DiveHealthCheck:
    """
    Auto-connectivity scanner — the immune system of Dive AI.
    
    Runs periodically to find and report disconnected modules.
    Integrates with DiveUpdateSystemComplete for version tracking.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> 'DiveHealthCheck':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._dive_core_dir = os.path.join(BACKEND_DIR, "dive_core")
        self._scan_history: List[HealthReport] = []
        self._periodic_thread: Optional[threading.Thread] = None
        self._running = False
        self._total_scans = 0

        # Known runtime entry points (files that are actually imported/used)
        self._runtime_files = {
            "gateway_server.py",
            "dive_core/agent/dive_agent_core.py",
            "dive_core/engine/lifecycle_bridge.py",
            "dive_core/engine/dive_brain.py",
            "dive_core/engine/dive_connector.py",
            "dive_core/engine/full_lifecycle.py",
            "dive_core/algorithm_service.py",
            "dive_core/engine/self_debugger.py",
            "dive_core/engine/deployment_rules.py",
            "dive_core/engine/dive_health_check.py",
        }

        # DiveConnector integration
        self._connector = None
        try:
            from dive_core.engine.dive_connector import get_connector
            self._connector = get_connector()
        except Exception:
            pass

        # DiveUpdate integration
        self._update_system = None
        try:
            from dive_core.search.dive_update_system_complete import DiveUpdateSystemComplete
            self._update_system = DiveUpdateSystemComplete(auto_update=False)
        except Exception:
            pass

    # ══════════════════════════════════════════════════════════
    # FULL SCAN — discover all modules, check connections
    # ══════════════════════════════════════════════════════════

    def run_full_check(self) -> Dict:
        """
        Run a complete health check:
          1. Discover all Python modules in dive_core/
          2. Parse imports to build connection graph
          3. Check which modules are reachable from runtime entry points
          4. Report disconnected modules with recommendations
          5. Check DiveUpdate status
        """
        start = time.time()
        self._total_scans += 1
        scan_id = f"scan_{self._total_scans}_{int(time.time())}"

        # Step 1: Discover all modules
        all_modules = self._discover_modules()

        # Step 2: Build import graph
        import_graph = self._build_import_graph(all_modules)

        # Step 3: Find connected modules (reachable from runtime)
        connected = self._find_connected(import_graph)

        # Step 4: Classify connected vs disconnected
        disconnected_list = []
        connected_list = []
        category_stats = {}

        for mod in all_modules:
            cat = mod.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "connected": 0, "disconnected": 0}
            category_stats[cat]["total"] += 1

            if mod.relative_path in connected or mod.name in connected:
                mod.is_connected = True
                connected_list.append(mod.relative_path)
                category_stats[cat]["connected"] += 1
            else:
                disconnected_list.append({
                    "name": mod.name,
                    "path": mod.relative_path,
                    "category": mod.category,
                    "classes": mod.class_names[:5],
                    "functions": mod.function_names[:5],
                    "size_bytes": mod.size_bytes,
                    "importance": mod.importance,
                })
                category_stats[cat]["disconnected"] += 1

        # Step 5: Generate recommendations
        recommendations = self._generate_recommendations(disconnected_list, category_stats)

        # Step 6: Check DiveUpdate status
        dive_update_status = {}
        if self._update_system:
            try:
                dive_update_status = self._update_system.get_system_status()
            except Exception:
                dive_update_status = {"error": "DiveUpdate check failed"}

        # Build report
        duration = round((time.time() - start) * 1000, 1)
        report = HealthReport(
            scan_id=scan_id,
            total_modules=len(all_modules),
            connected_modules=len(connected_list),
            disconnected_modules=len(disconnected_list),
            disconnected_list=disconnected_list,
            connected_list=connected_list,
            category_stats=category_stats,
            recommendations=recommendations,
            scan_duration_ms=duration,
            dive_update_status=dive_update_status,
        )

        self._scan_history.append(report)

        return {
            "scan_id": scan_id,
            "total_modules": report.total_modules,
            "connected": report.connected_modules,
            "disconnected": report.disconnected_modules,
            "connectivity_rate": round(
                report.connected_modules / max(report.total_modules, 1) * 100, 1
            ),
            "category_stats": category_stats,
            "disconnected_top": disconnected_list[:20],
            "recommendations": recommendations[:10],
            "dive_update": dive_update_status,
            "scan_duration_ms": duration,
        }

    def _discover_modules(self) -> List[ModuleInfo]:
        """Discover all Python modules in dive_core/."""
        modules = []
        # Key directories to scan (avoid vision/ which is huge)
        scan_dirs = [
            "",  # dive_core root
            "engine",
            "agent",
            "skills",
            "search",
            "memory",
            "orchestrator",
            "security",
            "marketplace",
            "workflow",
            "voice",
        ]

        for subdir in scan_dirs:
            dir_path = os.path.join(self._dive_core_dir, subdir) if subdir else self._dive_core_dir
            if not os.path.isdir(dir_path):
                continue

            for fname in os.listdir(dir_path):
                if not fname.endswith(".py") or fname.startswith("__"):
                    continue

                fpath = os.path.join(dir_path, fname)
                rel_path = os.path.relpath(fpath, BACKEND_DIR).replace("\\", "/")

                mod = ModuleInfo(
                    name=fname[:-3],  # Remove .py
                    path=fpath,
                    relative_path=rel_path,
                    size_bytes=os.path.getsize(fpath),
                    category=subdir if subdir else "core",
                )

                # Quick parse for classes and functions
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(5000)  # First 5KB only
                    
                    classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                    functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
                    
                    mod.class_names = classes[:10]
                    mod.function_names = functions[:10]
                    mod.has_classes = len(classes) > 0
                    mod.has_functions = len(functions) > 0

                    # Determine importance
                    if any(kw in fname.lower() for kw in ["engine", "brain", "core", "service"]):
                        mod.importance = "high"
                    elif any(kw in fname.lower() for kw in ["update", "bridge", "router"]):
                        mod.importance = "high"
                    elif any(kw in fname.lower() for kw in ["test", "example", "demo"]):
                        mod.importance = "low"

                except Exception:
                    pass

                modules.append(mod)

        return modules

    def _build_import_graph(self, modules: List[ModuleInfo]) -> Dict[str, Set[str]]:
        """Build import graph: module → set of modules it imports."""
        graph: Dict[str, Set[str]] = {}
        
        for mod in modules:
            graph[mod.relative_path] = set()
            try:
                with open(mod.path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(10000)
                
                # Find import statements
                imports = re.findall(
                    r'(?:from|import)\s+(dive_core[\w\.]*)',
                    content
                )
                for imp in imports:
                    # Convert module path to file path
                    parts = imp.replace(".", "/") + ".py"
                    graph[mod.relative_path].add(parts)

            except Exception:
                pass

        return graph

    def _find_connected(self, import_graph: Dict[str, Set[str]]) -> Set[str]:
        """Find all modules reachable from runtime entry points (BFS)."""
        connected = set()
        queue = list(self._runtime_files)
        connected.update(queue)

        while queue:
            current = queue.pop(0)
            for target in import_graph.get(current, set()):
                if target not in connected:
                    connected.add(target)
                    queue.append(target)

        # Also add reverse: if a module imports a runtime file, it's likely connected
        for mod_path, imports in import_graph.items():
            for imp in imports:
                if imp in connected:
                    connected.add(mod_path)

        return connected

    def _generate_recommendations(self, disconnected: List[Dict],
                                  category_stats: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recs = []

        # High-importance disconnected modules
        high_imp = [d for d in disconnected if d.get("importance") == "high"]
        if high_imp:
            names = ", ".join(d["name"] for d in high_imp[:5])
            recs.append(f"⚠️ {len(high_imp)} high-importance modules disconnected: {names}")

        # Categories with low connectivity
        for cat, stats in category_stats.items():
            if stats["total"] > 2:
                rate = stats["connected"] / stats["total"]
                if rate < 0.5:
                    recs.append(
                        f"📦 Category '{cat}': only {stats['connected']}/{stats['total']} "
                        f"({rate:.0%}) connected — consider integrating"
                    )

        # Modules with useful-looking classes
        for d in disconnected[:10]:
            if d.get("classes"):
                recs.append(
                    f"🔌 {d['name']} has classes {d['classes'][:3]} — "
                    f"may be worth connecting to DiveBrain"
                )

        return recs

    # ══════════════════════════════════════════════════════════
    # PERIODIC SCANNING — auto-run every N hours
    # ══════════════════════════════════════════════════════════

    def start_periodic(self, interval_hours: float = 1.0):
        """Start periodic health checks (runs in background thread)."""
        if self._running:
            return {"status": "already_running"}

        self._running = True
        interval_sec = interval_hours * 3600

        def _periodic_loop():
            while self._running:
                try:
                    self.run_full_check()
                except Exception:
                    pass
                # Sleep in small chunks so we can stop quickly
                for _ in range(int(interval_sec / 5)):
                    if not self._running:
                        break
                    time.sleep(5)

        self._periodic_thread = threading.Thread(
            target=_periodic_loop,
            daemon=True,
            name="DiveHealthCheck-Periodic",
        )
        self._periodic_thread.start()
        return {
            "status": "started",
            "interval_hours": interval_hours,
        }

    def stop_periodic(self):
        """Stop periodic health checks."""
        self._running = False
        return {"status": "stopped"}

    # ══════════════════════════════════════════════════════════
    # DIVE UPDATE INTEGRATION
    # ══════════════════════════════════════════════════════════

    def check_updates(self) -> Dict:
        """Check for Dive AI component updates via DiveUpdateSystem."""
        if not self._update_system:
            return {"available": False, "reason": "DiveUpdateSystem not loaded"}
        try:
            updates = self._update_system.check_updates()
            return {
                "available": bool(updates),
                "updates": updates,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def trigger_update(self, component: str = None) -> Dict:
        """Trigger a DiveUpdate for a specific component or all."""
        if not self._update_system:
            return {"success": False, "reason": "DiveUpdateSystem not loaded"}
        try:
            if component:
                from dive_core.search.dive_update_system_complete import ComponentType
                comp_type = ComponentType(component)
                result = self._update_system.update_component(comp_type)
                return {
                    "success": result.success if hasattr(result, 'success') else True,
                    "component": component,
                }
            else:
                results = self._update_system.update_all()
                return {
                    "success": True,
                    "updated": len(results) if results else 0,
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ══════════════════════════════════════════════════════════
    # STATS & HISTORY
    # ══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Get health check statistics (includes connector data)."""
        latest = self._scan_history[-1] if self._scan_history else None
        
        stats = {
            "total_scans": self._total_scans,
            "periodic_running": self._running,
            "latest_scan": {
                "id": latest.scan_id if latest else None,
                "total": latest.total_modules if latest else 0,
                "connected": latest.connected_modules if latest else 0,
                "disconnected": latest.disconnected_modules if latest else 0,
                "connectivity_rate": round(
                    latest.connected_modules / max(latest.total_modules, 1) * 100, 1
                ) if latest else 0,
                "timestamp": latest.timestamp if latest else 0,
            } if latest else None,
            "dive_update_loaded": self._update_system is not None,
            "dive_connector_loaded": self._connector is not None,
        }
        
        # Add connector stats if available
        if self._connector:
            try:
                stats["connector"] = self._connector.get_stats()
            except Exception:
                pass
        
        return stats

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get scan history."""
        return [
            {
                "scan_id": r.scan_id,
                "total": r.total_modules,
                "connected": r.connected_modules,
                "disconnected": r.disconnected_modules,
                "duration_ms": r.scan_duration_ms,
                "timestamp": r.timestamp,
            }
            for r in self._scan_history[-limit:]
        ]


def get_health_check() -> DiveHealthCheck:
    """Get the global DiveHealthCheck singleton."""
    return DiveHealthCheck.get_instance()
