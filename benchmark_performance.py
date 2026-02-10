"""
⚡ PERFORMANCE BENCHMARK SUITE
Comprehensive performance testing for V98/AICoding algorithms

Benchmarks:
1. Connection speed
2. Model discovery time
3. Chat completion latency
4. Memory usage profiling
5. API call patterns
"""

import os
import sys
import time
import psutil
import gc
from typing import Dict, List

sys.path.append(os.path.dirname(__file__))

from core.algorithms.algorithm_manager import AlgorithmManager


class PerformanceBenchmark:
    """Benchmark harness for algorithm performance testing"""
    
    def __init__(self):
        self.results = []
        self.process = psutil.Process()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def benchmark(self, name: str, func, *args, **kwargs):
        """Run a benchmark and record results"""
        print(f"\n⚡ Benchmark: {name}")
        
        # Force garbage collection before test
        gc.collect()
        mem_before = self.get_memory_usage()
        
        # Time execution
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        # Memory after
        mem_after = self.get_memory_usage()
        mem_delta = mem_after - mem_before
        
        benchmark_result = {
            "name": name,
            "time_ms": elapsed * 1000,
            "memory_mb": mem_delta,
            "success": result is not None
        }
        
        self.results.append(benchmark_result)
        
        print(f"   ⏱️  Time: {elapsed*1000:.0f}ms")
        print(f"   💾 Memory: {mem_delta:+.2f}MB")
        print(f"   {'✅' if result else '❌'} Result: {'Success' if result else 'Failed'}")
        
        return result


def benchmark_v98_connection():
    """Benchmark V98 connection performance"""
    print("\n" + "=" * 70)
    print("V98 CONNECTION BENCHMARKS")
    print("=" * 70)
    
    bench = PerformanceBenchmark()
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    v98 = manager.get_algorithm("V98Connection")
    
    if not v98:
        print("❌ V98Connection not found")
        return bench.results
    
    # Benchmark 1: Initial connection
    def test_connect():
        result = v98.execute({"action": "connect"})
        return result.status == "success"
    
    bench.benchmark("V98 - Initial Connection", test_connect)
    
    # Benchmark 2: Model listing
    def test_list_models():
        result = v98.execute({"action": "list_models"})
        return result.status == "success"
    
    bench.benchmark("V98 - List All Models", test_list_models)
    
    # Benchmark 3: Filtered model search
    def test_filter_models():
        result = v98.execute({"action": "list_models", "filter_by": "claude"})
        return result.status == "success"
    
    bench.benchmark("V98 - Filter Models (Claude)", test_filter_models)
    
    # Benchmark 4: Health check
    def test_health():
        result = v98.execute({"action": "health"})
        return result.status == "success"
    
    bench.benchmark("V98 - Health Check", test_health)
    
    # Benchmark 5: Chat completion (small)
    def test_chat_small():
        result = v98.execute({
            "action": "chat",
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        })
        return result.status == "success"
    
    bench.benchmark("V98 - Chat (Small, 10 tokens)", test_chat_small)
    
    return bench.results


def benchmark_aicoding_connection():
    """Benchmark AICoding connection performance"""
    print("\n" + "=" * 70)
    print("AICODING CONNECTION BENCHMARKS")
    print("=" * 70)
    
    bench = PerformanceBenchmark()
    manager = AlgorithmManager(auto_scan=False)
    manager._register_from_directory("D:\\Antigravity\\Dive AI\\core\\algorithms\\operational")
    aicoding = manager.get_algorithm("AICodingConnection")
    
    if not aicoding:
        print("❌ AICodingConnection not found")
        return bench.results
    
    # Benchmark 1: Connection
    def test_connect():
        result = aicoding.execute({"action": "connect"})
        return result.status == "success"
    
    bench.benchmark("AICoding - Connection", test_connect)
    
    # Benchmark 2: Health check
    def test_health():
        result = aicoding.execute({"action": "health"})
        return result.status == "success"
    
    bench.benchmark("AICoding - Health Check", test_health)
    
    # Benchmark 3: Anthropic messages (small)
    def test_messages_small():
        result = aicoding.execute({
            "action": "messages",
            "model": "claude-sonnet-4-5-20250929",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        })
        return result.status == "success"
    
    bench.benchmark("AICoding - Anthropic Messages (10 tokens)", test_messages_small)
    
    return bench.results


def benchmark_algorithm_manager():
    """Benchmark AlgorithmManager performance"""
    print("\n" + "=" * 70)
    print("ALGORITHM MANAGER BENCHMARKS")
    print("=" * 70)
    
    bench = PerformanceBenchmark()
    
    # Benchmark 1: Initialization (no auto-scan)
    def test_init_no_scan():
        manager = AlgorithmManager(auto_scan=False)
        return manager is not None
    
    bench.benchmark("AlgorithmManager - Init (No Scan)", test_init_no_scan)
    
    # Benchmark 2: Initialization (with auto-scan)
    def test_init_with_scan():
        manager = AlgorithmManager(auto_scan=True)
        return manager is not None
    
    bench.benchmark("AlgorithmManager - Init (Auto-Scan)", test_init_with_scan)
    
    # Benchmark 3: Get algorithm (cached)
    manager = AlgorithmManager(auto_scan=True)
    def test_get_algorithm():
        algo = manager.get_algorithm("V98Connection")
        return algo is not None
    
    bench.benchmark("AlgorithmManager - Get Algorithm (Cached)", test_get_algorithm)
    
    return bench.results


def generate_performance_report(all_results: List[Dict]):
    """Generate comprehensive performance report"""
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE REPORT")
    print("=" * 70)
    
    # Summary statistics
    total_tests = len(all_results)
    successful = sum(1 for r in all_results if r['success'])
    avg_time = sum(r['time_ms'] for r in all_results) / total_tests if total_tests > 0 else 0
    total_memory = sum(r['memory_mb'] for r in all_results)
    
    print(f"\n✅ Summary:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful} ({(successful/total_tests)*100:.1f}%)")
    print(f"   Avg Time: {avg_time:.0f}ms")
    print(f"   Total Memory: {total_memory:+.2f}MB")
    
    # Performance by category
    print(f"\n⚡ Performance Breakdown:")
    print(f"   {'Benchmark':<50} {'Time':<12} {'Memory':<12} {'Status'}")
    print(f"   {'-'*50} {'-'*12} {'-'*12} {'-'*6}")
    
    for result in all_results:
        time_str = f"{result['time_ms']:.0f}ms"
        mem_str = f"{result['memory_mb']:+.2f}MB"
        status = "✅" if result['success'] else "❌"
        
        print(f"   {result['name']:<50} {time_str:<12} {mem_str:<12} {status}")
    
    # Optimization recommendations
    print(f"\n💡 Optimization Recommendations:")
    
    slow_tests = [r for r in all_results if r['time_ms'] > 1000]
    if slow_tests:
        print(f"\n   ⚠️  Slow Operations (>1s):")
        for test in slow_tests:
            print(f"      - {test['name']}: {test['time_ms']:.0f}ms")
            if "Connection" in test['name']:
                print(f"        → Cache connection results")
            if "Chat" in test['name']:
                print(f"        → Use smaller max_tokens for simple tasks")
            if "Auto-Scan" in test['name']:
                print(f"        → Use manual registration for faster startup")
    
    high_memory = [r for r in all_results if r['memory_mb'] > 10]
    if high_memory:
        print(f"\n   ⚠️  High Memory Usage (>10MB):")
        for test in high_memory:
            print(f"      - {test['name']}: {test['memory_mb']:.2f}MB")
            print(f"        → Implement model list caching")
            print(f"        → Use connection pooling")
    
    # Best performers
    fast_tests = sorted(all_results, key=lambda x: x['time_ms'])[:3]
    print(f"\n   ✅ Fastest Operations:")
    for i, test in enumerate(fast_tests, 1):
        print(f"      {i}. {test['name']}: {test['time_ms']:.0f}ms")
    
    return all_results


def run_all_benchmarks():
    """Run all performance benchmarks"""
    print("\n" + "=" * 70)
    print("⚡ DIVE AI PERFORMANCE BENCHMARK SUITE")
    print("=" * 70)
    print(f"\nSystem Info:")
    print(f"   CPU: {psutil.cpu_count()} cores")
    print(f"   Memory: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB")
    print(f"   Python: {sys.version.split()[0]}")
    
    all_results = []
    
    # Run benchmarks
    try:
        all_results.extend(benchmark_algorithm_manager())
    except Exception as e:
        print(f"\n❌ AlgorithmManager benchmark failed: {e}")
    
    try:
        all_results.extend(benchmark_v98_connection())
    except Exception as e:
        print(f"\n❌ V98 benchmark failed: {e}")
    
    try:
        all_results.extend(benchmark_aicoding_connection())
    except Exception as e:
        print(f"\n❌ AICoding benchmark failed: {e}")
    
    # Generate report
    generate_performance_report(all_results)
    
    print("\n" + "=" * 70)
    print("✅ Benchmark Complete!")
    print("=" * 70)
    
    return all_results


if __name__ == "__main__":
    results = run_all_benchmarks()
    sys.exit(0)
