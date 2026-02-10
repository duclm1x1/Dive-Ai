# Test V29 Components
import sys
sys.path.insert(0, '.')

print("=" * 50)
print("Testing Dive AI V29 Components")
print("=" * 50)

# Test 1: Memory V5
print("\n1. Memory V5...")
try:
    from core.memory_v2.memory_v5 import get_memory_v5
    m = get_memory_v5("data/test_v29")
    print(f"   ✅ Memory V5 OK - {m.db_path}")
except Exception as e:
    print(f"   ❌ Memory V5 Failed: {e}")

# Test 2: GPA Scorer
print("\n2. GPA Scorer...")
try:
    from core.evaluation.gpa_scorer import GPAScorerAlgorithm, GPAScore
    scorer = GPAScorerAlgorithm()
    gpa = GPAScore.calculate(0.8, 0.7, 0.9)
    print(f"   ✅ GPA Scorer OK - Test GPA: {gpa.overall:.2f} ({gpa.level.value})")
except Exception as e:
    print(f"   ❌ GPA Scorer Failed: {e}")

# Test 3: Workflow Scorer
print("\n3. Workflow Scorer...")
try:
    from core.evaluation.workflow_scorer import get_workflow_scorer, ProcessKPIs
    ws = get_workflow_scorer()
    kpis = ProcessKPIs.calculate(10, 5, 1, 2, True)
    print(f"   ✅ Workflow Scorer OK - Test KPIs: {kpis.overall_score:.2f}")
except Exception as e:
    print(f"   ❌ Workflow Scorer Failed: {e}")

# Test 4: Algorithm Suggester
print("\n4. Algorithm Suggester...")
try:
    from core.reasoning.algorithm_suggester import get_algorithm_suggester
    suggester = get_algorithm_suggester("data/test_v29/suggester.db")
    suggestions = suggester.suggest("Build a web app", top_n=3)
    print(f"   ✅ Algorithm Suggester OK - Top suggestion: {suggestions[0].algorithm if suggestions else 'None'}")
except Exception as e:
    print(f"   ❌ Algorithm Suggester Failed: {e}")

# Test 5: Hierarchical Decomposition
print("\n5. Hierarchical Decomposition...")
try:
    from core.reasoning.hierarchical_decomposition import HierarchicalTaskDecomposition
    decomp = HierarchicalTaskDecomposition()
    result = decomp.execute({"request": "Create a Python web app"})
    if result.status == "success":
        print(f"   ✅ Hierarchical Decomposition OK - Tasks: {len(result.data['subtasks'])}")
    else:
        print(f"   ⚠️ Decomposition returned: {result.error}")
except Exception as e:
    print(f"   ❌ Hierarchical Decomposition Failed: {e}")

print("\n" + "=" * 50)
print("V29 Component Tests Complete!")
print("=" * 50)
