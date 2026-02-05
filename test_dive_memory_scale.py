#!/usr/bin/env python3
"""
Dive-Memory v3 - Scale Test
Test at 100, 1000, 2000 memories
"""

import sys
import time
import random
import json
import os
from pathlib import Path

# Add dive-memory path
sys.path.insert(0, str(Path(__file__).parent / "skills/dive-memory-v3/scripts"))

from dive_memory import DiveMemory

def generate_test_data(count):
    """Generate test memories"""
    sections = ["solutions", "decisions", "research", "executions", "capabilities"]
    tags_pool = ["python", "javascript", "react", "api", "database", "auth"]
    
    data = []
    for i in range(count):
        data.append({
            "content": f"Test memory {i}: Solution using {random.choice(tags_pool)}",
            "section": random.choice(sections),
            "tags": random.sample(tags_pool, random.randint(1, 3)),
            "importance": random.randint(1, 10)
        })
    return data

def test_scale(count):
    """Test at specific scale"""
    print(f"\n{'='*70}")
    print(f"TESTING: {count} MEMORIES")
    print(f"{'='*70}")
    
    db_path = f"/tmp/dive-memory-test-{count}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    memory = DiveMemory(db_path)
    results = {}
    
    # Test 1: Add memories
    print(f"\n1. Adding {count} memories...")
    test_data = generate_test_data(count)
    
    start = time.time()
    for i, data in enumerate(test_data):
        memory.add(**data)
        if (i + 1) % 100 == 0:
            print(f"   Added {i + 1}/{count}...")
    add_time = time.time() - start
    
    results['add'] = {
        'total_time': round(add_time, 2),
        'avg_time_ms': round((add_time / count) * 1000, 2),
        'per_second': round(count / add_time, 2)
    }
    print(f"   ✅ Added {count} in {add_time:.2f}s ({results['add']['per_second']:.2f}/sec)")
    
    # Test 2: Search
    print(f"\n2. Testing search (50 queries)...")
    queries = ["python solution", "javascript api", "react database", "auth security"]
    search_times = []
    
    for i in range(50):
        start = time.time()
        results_list = memory.search(random.choice(queries), top_k=10)
        search_times.append((time.time() - start) * 1000)
    
    results['search'] = {
        'avg_ms': round(sum(search_times) / len(search_times), 2),
        'min_ms': round(min(search_times), 2),
        'max_ms': round(max(search_times), 2)
    }
    print(f"   ✅ Search avg: {results['search']['avg_ms']:.2f}ms (min: {results['search']['min_ms']:.2f}ms, max: {results['search']['max_ms']:.2f}ms)")
    
    # Test 3: Stats
    print(f"\n3. Getting stats...")
    start = time.time()
    stats = memory.get_stats()
    stats_time = (time.time() - start) * 1000
    
    results['stats'] = {
        'time_ms': round(stats_time, 2),
        'total_memories': stats['total_memories'],
        'total_links': stats['total_links']
    }
    print(f"   ✅ Stats: {stats['total_memories']} memories, {stats['total_links']} links ({stats_time:.2f}ms)")
    
    # Test 4: Database size
    db_size = os.path.getsize(db_path) / (1024 * 1024)
    results['database'] = {
        'size_mb': round(db_size, 2),
        'avg_bytes': round((os.path.getsize(db_path) / count), 2)
    }
    print(f"   ✅ Database: {db_size:.2f}MB ({results['database']['avg_bytes']:.0f} bytes/memory)")
    
    # Test 5: Graph
    print(f"\n4. Building knowledge graph...")
    start = time.time()
    graph = memory.get_graph()
    graph_time = time.time() - start
    
    results['graph'] = {
        'time_s': round(graph_time, 2),
        'nodes': len(graph['nodes']),
        'edges': len(graph['edges'])
    }
    print(f"   ✅ Graph: {results['graph']['nodes']} nodes, {results['graph']['edges']} edges ({graph_time:.2f}s)")
    
    print(f"\n{'='*70}")
    print(f"COMPLETED: {count} MEMORIES TEST")
    print(f"{'='*70}\n")
    
    return results

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("DIVE-MEMORY V3 - SCALE TEST SUITE")
    print("="*70)
    
    all_results = {}
    
    for count in [100, 1000, 2000]:
        all_results[count] = test_scale(count)
    
    # Generate report
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    
    print("\n{:<15} {:<15} {:<15} {:<15}".format("Memories", "Add (sec)", "Search (ms)", "DB Size (MB)"))
    print("-" * 70)
    
    for count in [100, 1000, 2000]:
        r = all_results[count]
        print("{:<15} {:<15} {:<15} {:<15}".format(
            count,
            r['add']['total_time'],
            r['search']['avg_ms'],
            r['database']['size_mb']
        ))
    
    # Performance analysis
    print("\n" + "="*70)
    print("PERFORMANCE ANALYSIS")
    print("="*70)
    
    for count in [100, 1000, 2000]:
        r = all_results[count]
        print(f"\n{count} Memories:")
        print(f"  Add: {r['add']['per_second']:.2f} memories/sec")
        print(f"  Search: {r['search']['avg_ms']:.2f}ms average")
        print(f"  Database: {r['database']['size_mb']:.2f}MB ({r['database']['avg_bytes']:.0f} bytes/memory)")
        print(f"  Graph: {r['graph']['nodes']} nodes, {r['graph']['edges']} edges")
        
        # Performance rating
        if r['search']['avg_ms'] < 100:
            rating = "EXCELLENT"
        elif r['search']['avg_ms'] < 200:
            rating = "GOOD"
        elif r['search']['avg_ms'] < 500:
            rating = "ACCEPTABLE"
        else:
            rating = "SLOW"
        print(f"  Rating: {rating}")
    
    # Save results
    with open('/home/ubuntu/dive-memory-test-results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n✅ Results saved to: /home/ubuntu/dive-memory-test-results.json")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
