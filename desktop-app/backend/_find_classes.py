"""Find correct class names for modules that failed to load."""
import ast, os

files = {
    'context_guard': 'dive_core/engine/context_guard.py',
    'dive_evidence_pack': 'dive_core/engine/dive_evidence_pack.py',
    'skill_intelligence': 'dive_core/skills/skill_intelligence.py',
    'dive_memory_change_tracker': 'dive_core/memory/dive_memory_change_tracker.py',
    'metrics': 'dive_core/monitoring/metrics.py',
    'dive_orchestrator_resilient': 'dive_core/orchestrator/dive_orchestrator_resilient.py',
    'dive_cruel_system': 'dive_core/dive_cruel_system.py',
    'dive_plugin_system': 'dive_core/dive_plugin_system.py',
    'dive_reasoning_trace': 'dive_core/workflow/dive_reasoning_trace.py',
}

lines = []
for key, fpath in files.items():
    if os.path.exists(fpath):
        try:
            tree = ast.parse(open(fpath, encoding='utf-8').read())
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('get_')]
            lines.append(f"{key}: classes={classes[:5]}, get_funcs={funcs[:3]}")
        except Exception as e:
            lines.append(f"{key}: ERROR {e}")
    else:
        lines.append(f"{key}: FILE NOT FOUND")

with open("_class_report.txt", "w") as f:
    f.write("\n".join(lines))
print("Done")
