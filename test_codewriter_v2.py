"""
Test CodeWriterV2 with live V98 API
"""

import sys
import os
sys.path.insert(0, r'D:\Antigravity\Dive-AI-v29 structle\Dive-AI-v29\src')

os.environ["V98_API_KEY"] = "YOUR_V98_API_KEY_HERE"

print("="*70)
print("CodeWriterV2 Test - Enhanced Code Generation")
print("="*70)

from core.algorithms.tactical.code_writer_v2 import generate_code

# Test 1: Simple function
print("\n[Test 1] Generate simple function...")
result = generate_code(
    "Write a Python function to calculate fibonacci numbers recursively",
    language="python",
    include_docs=True
)

if result.status == "success":
    print(f"OK - Code generated!")
    print(f"   Model: {result.data['model_used']}")
    print(f"   Complexity: {result.data['complexity_detected']}")
    print(f"   Code length: {len(result.data['code'])} chars")
    print(f"\nGenerated Code:\n{'-'*70}")
    print(result.data['code'][:500])
    print("...")
    print(f"{'-'*70}\n")
else:
    print(f"FAILED: {result.data.get('error')}")
    sys.exit(1)

# Test 2: Complex class with tests
print("[Test 2] Generate complex class with tests...")
result2 = generate_code(
    "Implement a binary search tree class in Python with insert, search, and delete methods",
    language="python",
    include_tests=True,
    include_docs=True,
    max_lines=200
)

if result2.status == "success":
    print(f"OK - Complex code generated!")
    print(f"   Model: {result2.data['model_used']}")
    print(f"   Complexity: {result2.data['complexity_detected']}")
    print(f"   Generation time: {result2.meta.get('llm_generation_time_ms', 0):.0f}ms")
    print(f"   Has tests: {len(result2.data.get('tests', '')) > 0}")
    print("\nExplanation:")
    print(result2.data.get('explanation', '')[:300])
    print("...")
else:
    print(f"FAILED: {result2.data.get('error')}")

print("\n" + "="*70)
print("Test completed!")
print("="*70)
