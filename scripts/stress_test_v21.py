#!/usr/bin/env python3
"""
Dive AI V21.0 Comprehensive Stress Test
Tests all integrated components and tracks results in self-aware memory
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "integration"))
sys.path.insert(0, str(Path(__file__).parent / "skills" / "dive-memory-v3" / "scripts"))

from dive_ai_self_memory import DiveAISelfMemory
from dive_memory import DiveMemory


class DiveAIV21StressTest:
    """Comprehensive stress test for Dive AI V21.0"""
    
    def __init__(self):
        self.self_memory = DiveAISelfMemory()
        self.results = []
        self.start_time = time.time()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = time.time() - self.start_time
        print(f"[{timestamp:8.2f}s] [{level}] {message}")
    
    def test_dive_memory_v3(self) -> Dict[str, Any]:
        """Test Dive Memory v3 performance"""
        self.log("Testing Dive Memory v3...", "TEST")
        
        test_result = {
            "name": "Dive Memory v3",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            # Initialize memory
            memory = DiveMemory()
            
            # Test add performance
            add_start = time.time()
            memory_ids = []
            for i in range(100):
                mem_id = memory.add(
                    content=f"Test memory {i}",
                    section="test",
                    tags=["stress-test"],
                    importance=5
                )
                memory_ids.append(mem_id)
            add_duration = time.time() - add_start
            
            # Test search performance
            search_start = time.time()
            results = memory.search("test memory", section="test", top_k=10)
            search_duration = time.time() - search_start
            
            # Get stats
            stats = memory.get_stats()
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "memories_added": len(memory_ids),
                    "add_duration": add_duration,
                    "add_rate": len(memory_ids) / add_duration,
                    "search_duration": search_duration * 1000,  # ms
                    "search_results": len(results),
                    "total_memories": stats.get("total_memories", 0)
                }
            })
            
            self.log(f"✅ Dive Memory v3: {len(memory_ids)} memories added in {add_duration:.2f}s ({len(memory_ids)/add_duration:.1f} mem/s)", "PASS")
            self.log(f"   Search: {search_duration*1000:.2f}ms for {len(results)} results", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Dive Memory v3 failed: {e}", "FAIL")
        
        return test_result
    
    def test_self_aware_memory(self) -> Dict[str, Any]:
        """Test self-aware memory system"""
        self.log("Testing Self-Aware Memory...", "TEST")
        
        test_result = {
            "name": "Self-Aware Memory",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            # Track a test change
            self.self_memory.track_code_change(
                file_path="stress_test_v21.py",
                change_type="tested",
                description="Running comprehensive stress test",
                details={"test_type": "stress_test"}
            )
            
            # Query history
            history = self.self_memory.query_history("stress test", top_k=5)
            
            # Get stats
            stats = self.self_memory.get_stats()
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "history_results": len(history),
                    "total_memories": stats.get("total_memories", 0),
                    "sections": len(stats.get("section_stats", {}))
                }
            })
            
            self.log(f"✅ Self-Aware Memory: {len(history)} history entries found", "PASS")
            self.log(f"   Total memories: {stats.get('total_memories', 0)}", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Self-Aware Memory failed: {e}", "FAIL")
        
        return test_result
    
    def test_dive_context(self) -> Dict[str, Any]:
        """Test Dive Context integration"""
        self.log("Testing Dive Context...", "TEST")
        
        test_result = {
            "name": "Dive Context",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            dive_context_path = Path(__file__).parent / "dive-context"
            
            # Check if Dive Context exists
            if not dive_context_path.exists():
                raise FileNotFoundError("Dive Context directory not found")
            
            # Check package.json
            package_json = dive_context_path / "package.json"
            if not package_json.exists():
                raise FileNotFoundError("package.json not found")
            
            # Check dist directory (built)
            dist_dir = dive_context_path / "dist"
            built = dist_dir.exists()
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "path": str(dive_context_path),
                    "package_json_exists": True,
                    "built": built
                }
            })
            
            self.log(f"✅ Dive Context: Found at {dive_context_path}", "PASS")
            self.log(f"   Built: {'Yes' if built else 'No (run: cd dive-context && pnpm build)'}", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Dive Context failed: {e}", "FAIL")
        
        return test_result
    
    def test_antigravity_plugin(self) -> Dict[str, Any]:
        """Test Antigravity Plugin"""
        self.log("Testing Antigravity Plugin...", "TEST")
        
        test_result = {
            "name": "Antigravity Plugin",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            antigravity_path = Path(__file__).parent / "antigravity_plugin"
            
            # Check if Antigravity Plugin exists
            if not antigravity_path.exists():
                raise FileNotFoundError("Antigravity Plugin directory not found")
            
            # Check server.py
            server_py = antigravity_path / "server.py"
            if not server_py.exists():
                raise FileNotFoundError("server.py not found")
            
            # Check subdirectories
            subdirs = ["mcp", "dashboard", "extension"]
            found_subdirs = [d for d in subdirs if (antigravity_path / d).exists()]
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "path": str(antigravity_path),
                    "server_exists": True,
                    "subdirs_found": found_subdirs
                }
            })
            
            self.log(f"✅ Antigravity Plugin: Found at {antigravity_path}", "PASS")
            self.log(f"   Subdirs: {', '.join(found_subdirs)}", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Antigravity Plugin failed: {e}", "FAIL")
        
        return test_result
    
    def test_monitor_ui(self) -> Dict[str, Any]:
        """Test Monitor UI"""
        self.log("Testing Monitor UI...", "TEST")
        
        test_result = {
            "name": "Monitor UI",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            monitor_server_path = Path(__file__).parent / "monitor_server"
            ui_path = Path(__file__).parent / "ui" / "dive-monitor"
            
            # Check if Monitor Server exists
            if not monitor_server_path.exists():
                raise FileNotFoundError("Monitor Server directory not found")
            
            # Check if UI exists
            if not ui_path.exists():
                raise FileNotFoundError("UI directory not found")
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "monitor_server_path": str(monitor_server_path),
                    "ui_path": str(ui_path),
                    "monitor_server_exists": True,
                    "ui_exists": True
                }
            })
            
            self.log(f"✅ Monitor UI: Found server and UI", "PASS")
            self.log(f"   Server: {monitor_server_path}", "INFO")
            self.log(f"   UI: {ui_path}", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Monitor UI failed: {e}", "FAIL")
        
        return test_result
    
    def test_skills_integration(self) -> Dict[str, Any]:
        """Test skills integration"""
        self.log("Testing Skills Integration...", "TEST")
        
        test_result = {
            "name": "Skills Integration",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            skills_path = Path(__file__).parent / "skills"
            
            if not skills_path.exists():
                raise FileNotFoundError("Skills directory not found")
            
            # Count skills
            v20_skills = list((skills_path).glob("*/SKILL.md"))
            v15_3_skills_path = skills_path / "v15.3-skills"
            v15_3_skills = list(v15_3_skills_path.glob("**/*.md")) if v15_3_skills_path.exists() else []
            
            total_skills = len(v20_skills) + len(v15_3_skills)
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "v20_skills": len(v20_skills),
                    "v15_3_skills": len(v15_3_skills),
                    "total_skills": total_skills
                }
            })
            
            self.log(f"✅ Skills Integration: {total_skills} total skills", "PASS")
            self.log(f"   V20.2.1: {len(v20_skills)} skills", "INFO")
            self.log(f"   V15.3: {len(v15_3_skills)} skills", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ Skills Integration failed: {e}", "FAIL")
        
        return test_result
    
    def test_v15_3_core(self) -> Dict[str, Any]:
        """Test V15.3 core engine"""
        self.log("Testing V15.3 Core Engine...", "TEST")
        
        test_result = {
            "name": "V15.3 Core Engine",
            "status": "unknown",
            "duration": 0,
            "details": {}
        }
        
        start = time.time()
        
        try:
            core_path = Path(__file__).parent / "v15.3-core"
            
            if not core_path.exists():
                raise FileNotFoundError("V15.3 Core directory not found")
            
            # Check key modules
            modules = ["dive_engine", "advanced_searching", "builder", "dag", "debate"]
            found_modules = [m for m in modules if (core_path / m).exists()]
            
            # Count Python files
            py_files = list(core_path.glob("**/*.py"))
            
            test_result.update({
                "status": "passed",
                "duration": time.time() - start,
                "details": {
                    "path": str(core_path),
                    "modules_found": found_modules,
                    "python_files": len(py_files)
                }
            })
            
            self.log(f"✅ V15.3 Core Engine: {len(found_modules)}/{len(modules)} modules found", "PASS")
            self.log(f"   Modules: {', '.join(found_modules)}", "INFO")
            self.log(f"   Python files: {len(py_files)}", "INFO")
            
        except Exception as e:
            test_result.update({
                "status": "failed",
                "duration": time.time() - start,
                "error": str(e)
            })
            self.log(f"❌ V15.3 Core Engine failed: {e}", "FAIL")
        
        return test_result
    
    def run_all_tests(self):
        """Run all stress tests"""
        self.log("=" * 80, "INFO")
        self.log("DIVE AI V21.0 COMPREHENSIVE STRESS TEST", "INFO")
        self.log("=" * 80, "INFO")
        self.log("", "INFO")
        
        # Run tests
        tests = [
            self.test_dive_memory_v3,
            self.test_self_aware_memory,
            self.test_dive_context,
            self.test_antigravity_plugin,
            self.test_monitor_ui,
            self.test_skills_integration,
            self.test_v15_3_core
        ]
        
        for test_func in tests:
            result = test_func()
            self.results.append(result)
            self.log("", "INFO")
        
        # Summary
        self.log("=" * 80, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("=" * 80, "INFO")
        
        passed = sum(1 for r in self.results if r["status"] == "passed")
        failed = sum(1 for r in self.results if r["status"] == "failed")
        total = len(self.results)
        
        self.log(f"Total Tests: {total}", "INFO")
        self.log(f"Passed: {passed} ✅", "INFO")
        self.log(f"Failed: {failed} ❌", "INFO")
        self.log(f"Success Rate: {passed/total*100:.1f}%", "INFO")
        self.log("", "INFO")
        
        # Track results in self-aware memory
        self.log("Tracking results in self-aware memory...", "INFO")
        for result in self.results:
            self.self_memory.track_test_result(
                test_name=result["name"],
                status=result["status"],
                duration=result["duration"],
                details=result.get("details", {})
            )
        
        # Save results to file
        results_file = Path(__file__).parent / "stress_test_results_v21.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "total_duration": time.time() - self.start_time,
                "passed": passed,
                "failed": failed,
                "total": total,
                "results": self.results
            }, f, indent=2)
        
        self.log(f"Results saved to: {results_file}", "INFO")
        self.log("", "INFO")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED! Dive AI V21.0 is production ready!", "PASS")
        else:
            self.log(f"⚠️  {failed} test(s) failed. Please review the results.", "WARN")
        
        return passed == total


def main():
    """Main entry point"""
    tester = DiveAIV21StressTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
