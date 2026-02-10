"""
Algorithm Priority Manager
Inspired by V28.7 core skills priority system

Manages algorithm priorities and always-running background algorithms
Priority levels: CRITICAL (1) → HIGH (2) → NORMAL (3) → LOW (4)
"""

import time
import threading
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Algorithm priority levels (lower number = higher priority)"""
    CRITICAL = 1  # Always running, essential for system
    HIGH = 2      # Frequently executed, important
    NORMAL = 3    # Regular execution
    LOW = 4       # Background, occasional


@dataclass
class AlgorithmPriority:
    """Priority configuration for an algorithm"""
    algorithm_id: str
    priority: Priority
    always_running: bool = False
    execution_interval: Optional[int] = None  # seconds, for always-running
    auto_execute: bool = False
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class AlgorithmPriorityManager:
    """
    Manage algorithm priorities and background execution
    
    Inspired by V28.7 Core Skills Priority System:
    - CRITICAL algorithms run continuously (memory, monitoring, update detection)
    - HIGH priority algorithms execute frequently
    - Background threads for always-running algorithms
    """
    
    def __init__(self, algorithm_manager):
        self.algorithm_manager = algorithm_manager
        self.priorities: Dict[str, AlgorithmPriority] = {}
        self.background_threads: Dict[str, threading.Thread] = {}
        self.running = False
        
        self._initialize_priorities()
    
    def _initialize_priorities(self):
        """Initialize algorithm priorities (V28.7 inspired)"""
        
        # CRITICAL - Always Running (V28.7 Core Skills)
        self.priorities["HighPerformanceMemory"] = AlgorithmPriority(
            algorithm_id="HighPerformanceMemory",
            priority=Priority.CRITICAL,
            always_running=True,
            execution_interval=5,  # Every 5 seconds
            auto_execute=True
        )
        
        self.priorities["MemoryLoop"] = AlgorithmPriority(
            algorithm_id="MemoryLoop",
            priority=Priority.CRITICAL,
            always_running=True,
            execution_interval=60,  # Every minute
            auto_execute=True
        )
        
        self.priorities["UpdateDetection"] = AlgorithmPriority(
            algorithm_id="UpdateDetection",
            priority=Priority.CRITICAL,
            always_running=True,
            execution_interval=300,  # Every 5 minutes
            auto_execute=True
        )
        
        self.priorities["WorkflowMonitoring"] = AlgorithmPriority(
            algorithm_id="WorkflowMonitoring",
            priority=Priority.CRITICAL,
            always_running=True,
            execution_interval=10,  # Every 10 seconds
            auto_execute=True
        )
        
        self.priorities["AgentPerformanceTracking"] = AlgorithmPriority(
            algorithm_id="AgentPerformanceTracking",
            priority=Priority.CRITICAL,
            always_running=True,
            execution_interval=30,  # Every 30 seconds
            auto_execute=True
        )
        
        # HIGH Priority - Frequent Execution
        self.priorities["SmartModelRouter"] = AlgorithmPriority(
            algorithm_id="SmartModelRouter",
            priority=Priority.HIGH,
            auto_execute=True,
            dependencies=["ComplexityAnalyzer"]
        )
        
        self.priorities["SemanticRouting"] = AlgorithmPriority(
            algorithm_id="SemanticRouting",
            priority=Priority.HIGH,
            auto_execute=True
        )
        
        self.priorities["AgentSelector"] = AlgorithmPriority(
            algorithm_id="AgentSelector",
            priority=Priority.HIGH,
            auto_execute=True
        )
        
        self.priorities["ContextRetrieval"] = AlgorithmPriority(
            algorithm_id="ContextRetrieval",
            priority=Priority.HIGH,
            always_running=True,
            execution_interval=15,  # Every 15 seconds
            auto_execute=True
        )
        
        # NORMAL Priority - Regular Use
        self.priorities["HybridPrompting"] = AlgorithmPriority(
            algorithm_id="HybridPrompting",
            priority=Priority.NORMAL
        )
        
        self.priorities["CodeGenerator"] = AlgorithmPriority(
            algorithm_id="CodeGenerator",
            priority=Priority.NORMAL
        )
        
        self.priorities["SmartOrchestrator"] = AlgorithmPriority(
            algorithm_id="SmartOrchestrator",
            priority=Priority.NORMAL,
            dependencies=["TaskDecomposition", "AgentSelector"]
        )
        
        # LOW Priority - Background/Occasional
        self.priorities["AlgorithmOptimizer"] = AlgorithmPriority(
            algorithm_id="AlgorithmOptimizer",
            priority=Priority.LOW,
            always_running=True,
            execution_interval=3600,  # Every hour
            auto_execute=True
        )
        
        self.priorities["GitHubMemorySync"] = AlgorithmPriority(
            algorithm_id="GitHubMemorySync",
            priority=Priority.LOW,
            always_running=True,
            execution_interval=1800,  # Every 30 minutes
            auto_execute=True
        )
    
    def start_all_background_algorithms(self):
        """Start all always-running background algorithms"""
        
        print("\n" + "="*60)
        print("🔄 Starting Background Algorithms (V28.7 Priority System)")
        print("="*60)
        
        self.running = True
        
        for algo_id, priority_config in self.priorities.items():
            if priority_config.always_running and priority_config.auto_execute:
                self._start_background_algorithm(algo_id, priority_config)
        
        print(f"\n✅ Started {len(self.background_threads)} background algorithms")
        print("="*60)
    
    def _start_background_algorithm(self, algo_id: str, config: AlgorithmPriority):
        """Start a background thread for an algorithm"""
        
        def background_loop():
            print(f"   🔄 [{config.priority.name}] {algo_id} - Every {config.execution_interval}s")
            
            while self.running:
                try:
                    # Execute algorithm
                    result = self.algorithm_manager.execute(algo_id, {
                        "mode": "background",
                        "interval": config.execution_interval
                    })
                    
                    # Sleep until next execution
                    time.sleep(config.execution_interval)
                    
                except Exception as e:
                    print(f"   ⚠️  Background algorithm {algo_id} error: {e}")
                    time.sleep(config.execution_interval)
        
        # Create and start thread
        thread = threading.Thread(target=background_loop, daemon=True, name=f"BG_{algo_id}")
        thread.start()
        
        self.background_threads[algo_id] = thread
    
    def stop_all_background_algorithms(self):
        """Stop all background algorithms"""
        
        print("\n🛑 Stopping background algorithms...")
        self.running = False
        
        # Wait for threads to finish
        for algo_id, thread in self.background_threads.items():
            if thread.is_alive():
                print(f"   Stopping {algo_id}...")
                thread.join(timeout=2)
        
        self.background_threads.clear()
        print("✅ All background algorithms stopped")
    
    def get_priority(self, algo_id: str) -> Priority:
        """Get priority for an algorithm"""
        config = self.priorities.get(algo_id)
        return config.priority if config else Priority.NORMAL
    
    def get_sorted_algorithms(self) -> List[str]:
        """Get algorithms sorted by priority"""
        
        sorted_algos = sorted(
            self.priorities.items(),
            key=lambda x: x[1].priority.value
        )
        
        return [algo_id for algo_id, _ in sorted_algos]
    
    def should_auto_execute(self, algo_id: str) -> bool:
        """Check if algorithm should auto-execute"""
        config = self.priorities.get(algo_id)
        return config.auto_execute if config else False
    
    def get_dependencies(self, algo_id: str) -> List[str]:
        """Get algorithm dependencies"""
        config = self.priorities.get(algo_id)
        return config.dependencies if config else []
    
    def get_status(self) -> Dict[str, Any]:
        """Get priority system status"""
        
        return {
            "running": self.running,
            "background_algorithms": len(self.background_threads),
            "total_managed": len(self.priorities),
            "by_priority": {
                "CRITICAL": sum(1 for p in self.priorities.values() if p.priority == Priority.CRITICAL),
                "HIGH": sum(1 for p in self.priorities.values() if p.priority == Priority.HIGH),
                "NORMAL": sum(1 for p in self.priorities.values() if p.priority == Priority.NORMAL),
                "LOW": sum(1 for p in self.priorities.values() if p.priority == Priority.LOW)
            },
            "always_running": [
                algo_id for algo_id, p in self.priorities.items() 
                if p.always_running
            ]
        }


# Example usage
if __name__ == "__main__":
    from core.algorithms import get_algorithm_manager
    
    manager = get_algorithm_manager()
    priority_manager = AlgorithmPriorityManager(manager)
    
    # Show status
    status = priority_manager.get_status()
    print("\n📊 Priority System Status:")
    print(f"   Total Managed: {status['total_managed']}")
    print(f"   By Priority: {status['by_priority']}")
    print(f"   Always Running: {len(status['always_running'])}")
    for algo in status['always_running']:
        print(f"      - {algo}")
    
    # Start background algorithms (commented out for testing)
    # priority_manager.start_all_background_algorithms()
    # time.sleep(30)  # Run for 30 seconds
    # priority_manager.stop_all_background_algorithms()
