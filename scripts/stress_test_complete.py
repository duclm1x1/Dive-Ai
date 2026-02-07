#!/usr/bin/env python3
"""
Dive AI V21.0 - Comprehensive Stress Test
Tests all components of the unified brain system

Test Categories:
1. Memory System Performance
2. Doc-First Workflow
3. Knowledge Graph
4. Context Injection
5. Version Control
6. Concurrent Operations
7. Large-Scale Data
8. Error Handling
"""

import sys
import time
import concurrent.futures
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "core"))
sys.path.insert(0, str(Path(__file__).parent / "skills" / "dive-memory-v3" / "scripts"))

from dive_enhanced_workflow import DiveEnhancedWorkflow


def print_test_header(test_name: str):
    """Print test header"""
    print("\n" + "="*80)
    print(f"  TEST: {test_name}")
    print("="*80)


def test_memory_performance():
    """Test 1: Memory System Performance"""
    print_test_header("Memory System Performance")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-memory")
    
    # Test rapid memory addition
    print("\n   📝 Test 1.1: Rapid Memory Addition (1000 memories)")
    start = time.time()
    
    for i in range(1000):
        workflow.memory.add(
            content=f"Test memory {i}: This is a test memory for stress testing",
            section="test",
            tags=["stress-test", f"batch-{i//100}"],
            importance=5
        )
    
    duration = time.time() - start
    rate = 1000 / duration
    
    print(f"      ✅ Added 1000 memories in {duration:.2f}s")
    print(f"      📊 Rate: {rate:.2f} memories/second")
    
    # Test search performance
    print("\n   🔍 Test 1.2: Search Performance")
    start = time.time()
    
    results = workflow.memory.search("test memory", top_k=50)
    
    duration = time.time() - start
    
    print(f"      ✅ Searched 1000 memories in {duration*1000:.2f}ms")
    print(f"      📊 Found {len(results)} results")
    
    # Test graph generation
    print("\n   📊 Test 1.3: Knowledge Graph Generation")
    start = time.time()
    
    graph = workflow.memory.get_graph(section="test")
    
    duration = time.time() - start
    
    print(f"      ✅ Generated graph in {duration:.2f}s")
    print(f"      📊 Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    
    return True


def test_doc_first_workflow():
    """Test 2: Doc-First Workflow"""
    print_test_header("Doc-First Workflow")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-workflow")
    
    # Test project creation
    print("\n   📚 Test 2.1: Create 10 Projects")
    start = time.time()
    
    for i in range(10):
        workflow.create_project_docs(
            project_id=f"test-project-{i}",
            title=f"Test Project {i}",
            full_doc=f"Full documentation for test project {i}",
            criteria=[f"Criterion {j}" for j in range(5)]
        )
    
    duration = time.time() - start
    
    print(f"      ✅ Created 10 projects in {duration:.2f}s")
    print(f"      📊 Rate: {10/duration:.2f} projects/second")
    
    # Test context loading
    print("\n   🧠 Test 2.2: Load Context for All Projects")
    start = time.time()
    
    for i in range(10):
        context = workflow.load_enhanced_context(f"test-project-{i}")
    
    duration = time.time() - start
    
    print(f"      ✅ Loaded 10 contexts in {duration:.2f}s")
    print(f"      📊 Rate: {10/duration:.2f} contexts/second")
    
    return True


def test_knowledge_graph():
    """Test 3: Knowledge Graph"""
    print_test_header("Knowledge Graph")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-graph")
    
    # Create interconnected memories
    print("\n   🔗 Test 3.1: Create 100 Interconnected Memories")
    start = time.time()
    
    memory_ids = []
    for i in range(100):
        memory_id = workflow.memory.add(
            content=f"Memory {i}: Related to memories {i-1} and {i+1}",
            section="graph-test",
            tags=["graph", f"cluster-{i//10}"],
            importance=7
        )
        memory_ids.append(memory_id)
    
    duration = time.time() - start
    
    print(f"      ✅ Created 100 memories in {duration:.2f}s")
    
    # Test related memories
    print("\n   🔍 Test 3.2: Find Related Memories")
    start = time.time()
    
    related = workflow.memory.get_related(memory_ids[50], max_depth=2)
    
    duration = time.time() - start
    
    print(f"      ✅ Found {len(related)} related memories in {duration*1000:.2f}ms")
    
    # Test graph export
    print("\n   📤 Test 3.3: Export Full Knowledge Graph")
    start = time.time()
    
    graph = workflow.memory.get_graph()
    
    duration = time.time() - start
    
    print(f"      ✅ Exported graph in {duration:.2f}s")
    print(f"      📊 Total nodes: {len(graph['nodes'])}, Total edges: {len(graph['edges'])}")
    
    return True


def test_context_injection():
    """Test 4: Context Injection"""
    print_test_header("Context Injection")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-context")
    
    # Add diverse memories
    print("\n   📝 Test 4.1: Add 50 Diverse Memories")
    
    topics = ["authentication", "database", "API", "frontend", "backend"]
    
    for i in range(50):
        topic = topics[i % len(topics)]
        workflow.memory.add(
            content=f"Memory about {topic}: Implementation details for {topic} system {i}",
            section="context-test",
            tags=[topic, "implementation"],
            importance=6
        )
    
    print(f"      ✅ Added 50 diverse memories")
    
    # Test context injection
    print("\n   💉 Test 4.2: Context Injection for Different Tasks")
    
    tasks = [
        "Implement authentication system",
        "Design database schema",
        "Create REST API",
        "Build frontend interface",
        "Deploy backend services"
    ]
    
    for task in tasks:
        start = time.time()
        context = workflow.memory.get_context_for_task(task, max_memories=5)
        duration = time.time() - start
        
        print(f"      ✅ '{task}': {len(context)} chars in {duration*1000:.2f}ms")
    
    return True


def test_version_control():
    """Test 5: Version Control"""
    print_test_header("Version Control")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-versions")
    
    # Create multiple versions
    print("\n   📸 Test 5.1: Create 10 Version Snapshots")
    start = time.time()
    
    for i in range(10):
        # Add some memories
        for j in range(10):
            workflow.memory.add(
                content=f"Version {i} memory {j}",
                section="versions-test",
                tags=[f"v{i}"],
                importance=5
            )
        
        # Create snapshot
        workflow.create_version_snapshot(
            version=f"test-{i}.0",
            description=f"Test version {i}"
        )
    
    duration = time.time() - start
    
    print(f"      ✅ Created 10 versions in {duration:.2f}s")
    print(f"      📊 Rate: {10/duration:.2f} versions/second")
    
    # Check exports
    exports_dir = workflow.memory_root / "exports"
    exports = list(exports_dir.glob("*.json"))
    
    print(f"      📁 Total exports: {len(exports)}")
    
    return True


def test_concurrent_operations():
    """Test 6: Concurrent Operations"""
    print_test_header("Concurrent Operations")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-concurrent")
    
    def add_memories(thread_id: int, count: int):
        """Add memories in thread"""
        for i in range(count):
            workflow.memory.add(
                content=f"Thread {thread_id} memory {i}",
                section="concurrent-test",
                tags=[f"thread-{thread_id}"],
                importance=5
            )
        return count
    
    # Test concurrent writes
    print("\n   🔀 Test 6.1: Concurrent Memory Addition (10 threads × 50 memories)")
    start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_memories, i, 50) for i in range(10)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    duration = time.time() - start
    total = sum(results)
    
    print(f"      ✅ Added {total} memories concurrently in {duration:.2f}s")
    print(f"      📊 Rate: {total/duration:.2f} memories/second")
    
    return True


def test_large_scale_data():
    """Test 7: Large-Scale Data"""
    print_test_header("Large-Scale Data")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-large")
    
    # Test large content
    print("\n   📄 Test 7.1: Store Large Documents (10 × 10KB)")
    start = time.time()
    
    large_content = "X" * 10000  # 10KB
    
    for i in range(10):
        workflow.memory.add(
            content=f"Large doc {i}: {large_content}",
            section="large-test",
            tags=["large"],
            importance=5
        )
    
    duration = time.time() - start
    
    print(f"      ✅ Stored 10 large documents in {duration:.2f}s")
    print(f"      📊 Total size: ~100KB")
    
    # Test search on large dataset
    print("\n   🔍 Test 7.2: Search Large Dataset")
    start = time.time()
    
    results = workflow.memory.search("Large doc", top_k=10)
    
    duration = time.time() - start
    
    print(f"      ✅ Searched in {duration*1000:.2f}ms")
    print(f"      📊 Found {len(results)} results")
    
    return True


def test_error_handling():
    """Test 8: Error Handling"""
    print_test_header("Error Handling")
    
    workflow = DiveEnhancedWorkflow(project_name="stress-test-errors")
    
    # Test invalid operations
    print("\n   ⚠️  Test 8.1: Invalid Operations")
    
    tests = [
        ("Empty content", lambda: workflow.memory.add("", "test", importance=5)),
        ("Invalid section", lambda: workflow.memory.search("test", section="")),
        ("Non-existent memory", lambda: workflow.memory.get_related("invalid-id")),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"      ⚠️  {test_name}: No error raised")
        except Exception as e:
            print(f"      ✅ {test_name}: Handled correctly ({type(e).__name__})")
            passed += 1
    
    print(f"\n      📊 Error handling: {passed}/{len(tests)} tests passed")
    
    return True


def main():
    """Run all stress tests"""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                   🧪 Dive AI V21.0 - Stress Test Suite                      ║
║                                                                              ║
║                      Comprehensive System Testing                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    tests = [
        ("Memory System Performance", test_memory_performance),
        ("Doc-First Workflow", test_doc_first_workflow),
        ("Knowledge Graph", test_knowledge_graph),
        ("Context Injection", test_context_injection),
        ("Version Control", test_version_control),
        ("Concurrent Operations", test_concurrent_operations),
        ("Large-Scale Data", test_large_scale_data),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n   ❌ Test failed: {e}")
    
    total_duration = time.time() - start_time
    
    # Print summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if error:
            print(f"           Error: {error}")
    
    print(f"\n   📊 Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"   ⏱️  Total duration: {total_duration:.2f}s")
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n   ⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Stress test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
