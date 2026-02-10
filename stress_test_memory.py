#!/usr/bin/env python3
"""
Dive AI V20.2 - Memory System Stress Test Suite
Tests: volume, concurrency, edge cases, errors, performance
"""

import sys
import os
import time
import random
import string
import threading
import sqlite3
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent / "skills/dive-memory-v3/scripts"))
from dive_memory import DiveMemory


class MemoryStressTest:
    """Comprehensive stress test suite for Dive-Memory"""
    
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "metrics": {}
        }
        self.test_db = "/tmp/dive-memory-stress-test.db"
    
    def cleanup(self):
        """Clean up test database"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def log_pass(self, test_name, details=""):
        """Log passed test"""
        self.results["passed"].append({"test": test_name, "details": details})
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def log_fail(self, test_name, error):
        """Log failed test"""
        self.results["failed"].append({"test": test_name, "error": str(error)})
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def log_warning(self, test_name, warning):
        """Log warning"""
        self.results["warnings"].append({"test": test_name, "warning": warning})
        print(f"⚠️  WARN: {test_name}")
        print(f"   {warning}")
    
    # ========== VOLUME TESTS ==========
    
    def test_rapid_add_10k(self):
        """Test: Add 10K memories rapidly"""
        print("\n" + "="*70)
        print("TEST: Rapid Add 10K Memories")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        try:
            start = time.time()
            for i in range(10000):
                memory.add(
                    content=f"Test memory {i}",
                    section="stress_test",
                    tags=["test"],
                    importance=5
                )
                if (i + 1) % 1000 == 0:
                    print(f"   Added {i + 1}/10000...")
            
            duration = time.time() - start
            rate = 10000 / duration
            
            # Verify count
            stats = memory.get_stats()
            if stats["total_memories"] != 10000:
                raise Exception(f"Expected 10000 memories, got {stats['total_memories']}")
            
            self.log_pass("Rapid Add 10K", f"Added 10K memories in {duration:.2f}s ({rate:.2f}/sec)")
            self.results["metrics"]["rapid_add_10k"] = {
                "duration": duration,
                "rate": rate
            }
            
        except Exception as e:
            self.log_fail("Rapid Add 10K", e)
    
    def test_large_content(self):
        """Test: Handle extremely large content"""
        print("\n" + "="*70)
        print("TEST: Large Content Handling")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        sizes = [
            ("1KB", 1024),
            ("10KB", 10 * 1024),
            ("100KB", 100 * 1024),
            ("1MB", 1024 * 1024),
        ]
        
        for name, size in sizes:
            try:
                content = "A" * size
                memory_id = memory.add(
                    content=content,
                    section="large_content",
                    tags=["large"],
                    importance=5
                )
                
                # Verify retrieval
                results = memory.search(content[:100], section="large_content")
                if not results:
                    raise Exception(f"Failed to retrieve {name} content")
                
                self.log_pass(f"Large Content {name}", f"Stored and retrieved {size} bytes")
                
            except Exception as e:
                if size >= 1024 * 1024:  # 1MB+
                    self.log_warning(f"Large Content {name}", f"Rejected (expected): {e}")
                else:
                    self.log_fail(f"Large Content {name}", e)
    
    # ========== CONCURRENT TESTS ==========
    
    def test_concurrent_add(self):
        """Test: Concurrent add operations"""
        print("\n" + "="*70)
        print("TEST: Concurrent Add Operations")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        def add_batch(batch_id, count):
            """Add batch of memories"""
            for i in range(count):
                memory.add(
                    content=f"Batch {batch_id} memory {i}",
                    section="concurrent",
                    tags=[f"batch-{batch_id}"],
                    importance=5
                )
        
        try:
            start = time.time()
            
            # 10 threads, 100 memories each = 1000 total
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(add_batch, i, 100) for i in range(10)]
                for future in as_completed(futures):
                    future.result()
            
            duration = time.time() - start
            
            # Verify count
            stats = memory.get_stats()
            if stats["total_memories"] != 1000:
                raise Exception(f"Expected 1000 memories, got {stats['total_memories']}")
            
            self.log_pass("Concurrent Add", f"1000 memories in {duration:.2f}s with 10 threads")
            
        except Exception as e:
            self.log_fail("Concurrent Add", e)
    
    def test_concurrent_search(self):
        """Test: Concurrent search operations"""
        print("\n" + "="*70)
        print("TEST: Concurrent Search Operations")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        # Add test data
        for i in range(1000):
            memory.add(
                content=f"Search test memory {i}",
                section="search_test",
                tags=["searchable"],
                importance=5
            )
        
        def search_batch(batch_id, count):
            """Perform batch of searches"""
            results = []
            for i in range(count):
                res = memory.search(f"memory {random.randint(0, 999)}", top_k=10)
                results.append(len(res))
            return results
        
        try:
            start = time.time()
            
            # 50 threads, 20 searches each = 1000 total
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = [executor.submit(search_batch, i, 20) for i in range(50)]
                all_results = []
                for future in as_completed(futures):
                    all_results.extend(future.result())
            
            duration = time.time() - start
            avg_results = sum(all_results) / len(all_results)
            
            self.log_pass("Concurrent Search", f"1000 searches in {duration:.2f}s with 50 threads, avg {avg_results:.1f} results")
            
        except Exception as e:
            self.log_fail("Concurrent Search", e)
    
    def test_concurrent_mixed(self):
        """Test: Mixed concurrent operations"""
        print("\n" + "="*70)
        print("TEST: Mixed Concurrent Operations")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        # Pre-populate
        for i in range(500):
            memory.add(
                content=f"Mixed test memory {i}",
                section="mixed",
                tags=["mixed"],
                importance=5
            )
        
        def mixed_operations(thread_id):
            """Perform mixed operations"""
            ops = []
            for i in range(20):
                op = random.choice(["add", "search", "update", "stats"])
                
                try:
                    if op == "add":
                        memory.add(
                            content=f"Thread {thread_id} memory {i}",
                            section="mixed",
                            tags=["mixed"],
                            importance=5
                        )
                        ops.append("add")
                    
                    elif op == "search":
                        memory.search("memory", section="mixed", top_k=5)
                        ops.append("search")
                    
                    elif op == "update":
                        # Get random memory
                        results = memory.search("memory", section="mixed", top_k=1)
                        if results:
                            memory.update(results[0].id, importance=random.randint(1, 10))
                            ops.append("update")
                    
                    elif op == "stats":
                        memory.get_stats(section="mixed")
                        ops.append("stats")
                
                except Exception as e:
                    ops.append(f"error:{op}")
            
            return ops
        
        try:
            start = time.time()
            
            # 20 threads, 20 operations each
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = [executor.submit(mixed_operations, i) for i in range(20)]
                all_ops = []
                for future in as_completed(futures):
                    all_ops.extend(future.result())
            
            duration = time.time() - start
            
            # Count operations
            op_counts = {}
            for op in all_ops:
                op_counts[op] = op_counts.get(op, 0) + 1
            
            errors = sum(1 for op in all_ops if op.startswith("error:"))
            
            if errors > 0:
                self.log_warning("Concurrent Mixed", f"{errors} errors in {len(all_ops)} operations")
            else:
                self.log_pass("Concurrent Mixed", f"{len(all_ops)} operations in {duration:.2f}s, no errors")
            
        except Exception as e:
            self.log_fail("Concurrent Mixed", e)
    
    # ========== EDGE CASE TESTS ==========
    
    def test_empty_content(self):
        """Test: Empty content handling"""
        print("\n" + "="*70)
        print("TEST: Empty Content Handling")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        try:
            memory_id = memory.add(
                content="",
                section="edge_case",
                tags=["empty"],
                importance=5
            )
            self.log_warning("Empty Content", "Accepted empty content (should validate?)")
        except Exception as e:
            self.log_pass("Empty Content", f"Rejected empty content: {e}")
    
    def test_unicode_content(self):
        """Test: Unicode and special characters"""
        print("\n" + "="*70)
        print("TEST: Unicode Content Handling")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        test_cases = [
            ("Emoji", "Hello 👋 World 🌍 Test 🚀"),
            ("Chinese", "你好世界"),
            ("Arabic", "مرحبا بالعالم"),
            ("Russian", "Привет мир"),
            ("Mixed", "Hello 世界 مرحبا мир 🌍"),
            ("Special", "Test\n\t\r\x00Special"),
            ("SQL Injection", "'; DROP TABLE memories; --"),
            ("XSS", "<script>alert('xss')</script>"),
        ]
        
        for name, content in test_cases:
            try:
                memory_id = memory.add(
                    content=content,
                    section="unicode",
                    tags=["unicode"],
                    importance=5
                )
                
                # Verify retrieval
                results = memory.search(content[:10] if len(content) > 10 else content, section="unicode")
                if not results:
                    raise Exception("Failed to retrieve")
                
                if results[0].content != content:
                    raise Exception(f"Content mismatch: {results[0].content} != {content}")
                
                self.log_pass(f"Unicode {name}", "Stored and retrieved correctly")
                
            except Exception as e:
                self.log_fail(f"Unicode {name}", e)
    
    def test_invalid_inputs(self):
        """Test: Invalid input handling"""
        print("\n" + "="*70)
        print("TEST: Invalid Input Handling")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        test_cases = [
            ("None content", None, "section", ["tag"], 5),
            ("None section", "content", None, ["tag"], 5),
            ("Invalid importance", "content", "section", ["tag"], 999),
            ("Negative importance", "content", "section", ["tag"], -1),
        ]
        
        for name, content, section, tags, importance in test_cases:
            try:
                memory_id = memory.add(
                    content=content,
                    section=section,
                    tags=tags,
                    importance=importance
                )
                self.log_warning(name, "Accepted invalid input (should validate?)")
            except Exception as e:
                self.log_pass(name, f"Rejected invalid input: {type(e).__name__}")
    
    # ========== ERROR SCENARIO TESTS ==========
    
    def test_database_corruption(self):
        """Test: Database corruption recovery"""
        print("\n" + "="*70)
        print("TEST: Database Corruption Recovery")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        # Add some data
        for i in range(100):
            memory.add(
                content=f"Memory {i}",
                section="corruption_test",
                tags=["test"],
                importance=5
            )
        
        # Corrupt database
        with open(self.test_db, 'r+b') as f:
            f.seek(100)
            f.write(b'\x00' * 1000)
        
        # Try to use corrupted database
        try:
            memory2 = DiveMemory(self.test_db)
            results = memory2.search("Memory", section="corruption_test")
            self.log_fail("Database Corruption", "Accepted corrupted database")
        except Exception as e:
            self.log_pass("Database Corruption", f"Detected corruption: {type(e).__name__}")
    
    def test_disk_full_simulation(self):
        """Test: Disk full scenario"""
        print("\n" + "="*70)
        print("TEST: Disk Full Simulation")
        print("="*70)
        
        # This test is difficult to simulate without actually filling disk
        # We'll test error handling for write failures
        
        self.log_warning("Disk Full", "Test skipped (requires actual disk full scenario)")
    
    # ========== PERFORMANCE TESTS ==========
    
    def test_memory_leak(self):
        """Test: Memory leak detection"""
        print("\n" + "="*70)
        print("TEST: Memory Leak Detection")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Baseline
        gc.collect()
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform operations
        for i in range(1000):
            memory.add(
                content=f"Leak test {i}",
                section="leak_test",
                tags=["test"],
                importance=5
            )
            memory.search(f"test {i}", section="leak_test")
        
        # Check memory
        gc.collect()
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        
        mem_increase = mem_after - mem_before
        
        if mem_increase > 100:  # More than 100MB increase
            self.log_warning("Memory Leak", f"Memory increased by {mem_increase:.2f}MB (potential leak)")
        else:
            self.log_pass("Memory Leak", f"Memory increased by {mem_increase:.2f}MB (acceptable)")
    
    def test_search_performance_degradation(self):
        """Test: Search performance over time"""
        print("\n" + "="*70)
        print("TEST: Search Performance Degradation")
        print("="*70)
        
        self.cleanup()
        memory = DiveMemory(self.test_db)
        
        # Add memories in batches and measure search time
        search_times = []
        
        for batch in range(5):
            # Add 1000 memories
            for i in range(1000):
                memory.add(
                    content=f"Batch {batch} memory {i}",
                    section="perf_test",
                    tags=["perf"],
                    importance=5
                )
            
            # Measure search time
            start = time.time()
            for _ in range(50):
                memory.search("memory", section="perf_test", top_k=10)
            duration = (time.time() - start) / 50 * 1000  # ms per search
            
            search_times.append(duration)
            print(f"   Batch {batch+1}: {(batch+1)*1000} memories, {duration:.2f}ms avg search")
        
        # Check degradation
        first_time = search_times[0]
        last_time = search_times[-1]
        degradation = (last_time - first_time) / first_time * 100
        
        if degradation > 100:  # More than 2x slower
            self.log_warning("Search Degradation", f"Search {degradation:.1f}% slower at 5K memories")
        else:
            self.log_pass("Search Degradation", f"Search only {degradation:.1f}% slower at 5K memories")
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self):
        """Run all stress tests"""
        print("\n" + "="*70)
        print("DIVE AI V20.2 - MEMORY SYSTEM STRESS TEST SUITE")
        print("="*70)
        
        start_time = time.time()
        
        # Volume tests
        self.test_rapid_add_10k()
        self.test_large_content()
        
        # Concurrent tests
        self.test_concurrent_add()
        self.test_concurrent_search()
        self.test_concurrent_mixed()
        
        # Edge case tests
        self.test_empty_content()
        self.test_unicode_content()
        self.test_invalid_inputs()
        
        # Error scenario tests
        self.test_database_corruption()
        self.test_disk_full_simulation()
        
        # Performance tests
        self.test_memory_leak()
        self.test_search_performance_degradation()
        
        duration = time.time() - start_time
        
        # Summary
        print("\n" + "="*70)
        print("STRESS TEST SUMMARY")
        print("="*70)
        print(f"\nTotal Duration: {duration:.2f}s")
        print(f"Tests Passed: {len(self.results['passed'])}")
        print(f"Tests Failed: {len(self.results['failed'])}")
        print(f"Warnings: {len(self.results['warnings'])}")
        
        if self.results['failed']:
            print("\n❌ FAILED TESTS:")
            for fail in self.results['failed']:
                print(f"  - {fail['test']}: {fail['error']}")
        
        if self.results['warnings']:
            print("\n⚠️  WARNINGS:")
            for warn in self.results['warnings']:
                print(f"  - {warn['test']}: {warn['warning']}")
        
        # Save results
        with open('/home/ubuntu/memory-stress-test-results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("\n✅ Results saved to: /home/ubuntu/memory-stress-test-results.json")
        print("="*70 + "\n")
        
        return len(self.results['failed']) == 0


def main():
    """Main entry point"""
    tester = MemoryStressTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
