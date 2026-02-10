"""
Algorithm Manager - Enhanced
Manages registration, execution, and lifecycle of all algorithms

Updated to support full algorithm catalog
"""

import os
import sys
from typing import Dict, Any, Optional, List

# Add paths
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


class AlgorithmManager:
    """
    Enhanced Algorithm Manager for V29.4
    
    Manages 80+ algorithms across 10 categories
    """
    
    def __init__(self, auto_scan: bool = False):
        self.algorithms = {}  # {algorithm_id: algorithm_instance}
        self.category_index = {}  # {category: [algorithm_ids]}
        self.execution_stats = {}  # {algorithm_id: {calls, successes, failures, avg_time}}
        
        print("🧠 AlgorithmManager initialized")
        
        # Auto-scan on startup if requested
        if auto_scan:
            self.auto_register_all()
        else:
            print("   Awaiting algorithm registration...")
    
    def register(self, algorithm_id: str, algorithm: Any):
        """
        Register an algorithm
        
        Args:
            algorithm_id: Unique identifier
            algorithm: Algorithm instance (must have spec and execute())
        """
        if algorithm_id in self.algorithms:
            print(f"   ⚠️  Algorithm '{algorithm_id}' already registered, replacing...")
        
        self.algorithms[algorithm_id] = algorithm
        
        # Index by category
        if hasattr(algorithm, 'spec') and algorithm.spec:
            category = algorithm.spec.category
            if category not in self.category_index:
                self.category_index[category] = []
            if algorithm_id not in self.category_index[category]:
                self.category_index[category].append(algorithm_id)
        
        # Initialize stats
        if algorithm_id not in self.execution_stats:
            self.execution_stats[algorithm_id] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "total_time_ms": 0
            }
    
    def get_algorithm(self, algorithm_id: str) -> Optional[Any]:
        """Get algorithm by ID"""
        return self.algorithms.get(algorithm_id)
    
    def list_algorithms(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all algorithms (optionally filtered by category)
        
        Returns:
            List of algorithm info dicts
        """
        if category:
            algorithm_ids = self.category_index.get(category, [])
            algorithms = [self.algorithms[aid] for aid in algorithm_ids if aid in self.algorithms]
        else:
            algorithms = list(self.algorithms.values())
        
        return [
            algo.get_info() if hasattr(algo, 'get_info') else {"id": "unknown"}
            for algo in algorithms
        ]
    
    def execute(self, algorithm_id: str, params: Dict[str, Any]) -> Any:
        """
        Execute an algorithm
        
        Args:
            algorithm_id: Algorithm to execute
            params: Input parameters
        
        Returns:
            AlgorithmResult
        """
        import time
        
        algorithm = self.get_algorithm(algorithm_id)
        if not algorithm:
            return {
                "status": "error",
                "error": f"Algorithm '{algorithm_id}' not found"
            }
        
        # Track execution
        start_time = time.time()
        self.execution_stats[algorithm_id]["calls"] += 1
        
        try:
            # Validate inputs
            if hasattr(algorithm, 'validate_inputs'):
                is_valid, error = algorithm.validate_inputs(params)
                if not is_valid:
                    self.execution_stats[algorithm_id]["failures"] += 1
                    return {
                        "status": "error",
                        "error": error
                    }
            
            # Execute
            result = algorithm.execute(params)
            
            # Track stats
            elapsed_ms = (time.time() - start_time) * 1000
            self.execution_stats[algorithm_id]["total_time_ms"] += elapsed_ms
            
            if hasattr(result, 'status') and result.status == "success":
                self.execution_stats[algorithm_id]["successes"] += 1
            else:
                self.execution_stats[algorithm_id]["failures"] += 1
            
            return result
        
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            self.execution_stats[algorithm_id]["total_time_ms"] += elapsed_ms
            self.execution_stats[algorithm_id]["failures"] += 1
            
            return {
                "status": "error",
                "error": f"Execution failed: {str(e)}"
            }
    
    def get_stats(self, algorithm_id: Optional[str] = None) -> Dict[str, Any]:
        """Get execution statistics"""
        if algorithm_id:
            stats = self.execution_stats.get(algorithm_id, {})
            if stats.get("calls", 0) > 0:
                stats["avg_time_ms"] = stats["total_time_ms"] / stats["calls"]
                stats["success_rate"] = stats["successes"] / stats["calls"] * 100
            return stats
        
        return self.execution_stats
    
    def get_categories(self) -> List[str]:
        """Get list of all categories"""
        return list(self.category_index.keys())
    
    def auto_register_all(self):
        """
        Auto-register all algorithms from operational/ and composite/ folders
        """
        print("\n🔍 Auto-discovering algorithms...")
        
        # Get directory paths
        base_dir = os.path.dirname(__file__)
        operational_dir = os.path.join(base_dir, "operational")
        composite_dir = os.path.join(base_dir, "composite")
        
        registered_count = 0
        
        # Register operational algorithms
        if os.path.exists(operational_dir):
            registered_count += self._register_from_directory(operational_dir)
        
        # Register composite algorithms
        if os.path.exists(operational_dir):
            registered_count += self._register_from_directory(composite_dir)
        
        print(f"\n✅ Auto-registered {registered_count} algorithms")
        print(f"   Total algorithms: {len(self.algorithms)}")
        print(f"   Categories: {len(self.category_index)}")
    
    def _register_from_directory(self, directory: str) -> int:
        """Register all algorithms from a directory"""
        import importlib.util
        
        if not os.path.exists(directory):
            return 0
        
        count = 0
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    # Load module
                    module_path = os.path.join(directory, filename)
                    spec = importlib.util.spec_from_file_location(filename[:-3], module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Call register function if exists
                    if hasattr(module, 'register'):
                        module.register(self)
                        count += 1
                
                except Exception as e:
                    print(f"   ⚠️  Failed to load {filename}: {e}")
        
        return count
