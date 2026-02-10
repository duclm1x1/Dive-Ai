"""Trace the exact import chain that causes failures."""
import sys, os, io, traceback, importlib

old_stdout = sys.stdout
old_stderr = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Restore
sys.stdout = old_stdout  
sys.stderr = old_stderr

# Try loading each failing module and capture full traceback
failures = [
    ("adaptive_rag", "dive_core.engine.dive_adaptive_rag"),
    ("impact_analyzer", "dive_core.engine.dive_impact_analyzer"),
    ("llm_optimizer", "dive_core.llm_optimizer"),
    ("memory_brain", "dive_core.memory.dive_memory_brain"),
    ("search_engine", "dive_core.search.dive_search_engine"),
    ("self_improve", "dive_core.dive_ai_self_improve"),
]

lines = []
for name, mod_path in failures:
    lines.append(f"\n=== {name} ({mod_path}) ===")
    try:
        # Remove if already partially loaded
        if mod_path in sys.modules:
            del sys.modules[mod_path]
        importlib.import_module(mod_path)
        lines.append("  OK - loaded successfully")
    except Exception as e:
        tb = traceback.format_exc()
        # Show last 10 lines of traceback
        tb_lines = tb.strip().split('\n')[-10:]
        for line in tb_lines:
            lines.append(f"  {line}")

with open("_trace_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Trace written to _trace_report.txt")
