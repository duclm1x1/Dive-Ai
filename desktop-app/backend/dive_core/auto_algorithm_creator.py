"""
Dive AI Auto Algorithm Creator -- Autonomously generate, verify, and deploy algorithms.
This is the core auto-creation engine that generates algorithm code from natural language specs,
validates them, and hot-deploys them into the running system.
"""
import os, re, time, json, importlib, importlib.util, inspect, traceback
from string import Template
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class AlgorithmBlueprint:
    """Blueprint for a new algorithm to be created."""
    name: str
    description: str
    category: str = "custom"
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    logic_type: str = "transform"      # transform, compute, api, pipeline, validator
    logic_code: str = ""               # Custom execute body
    tags: List[str] = field(default_factory=list)
    cost_per_call: float = 0.0
    verifier_type: str = "none"        # none, schema, range, custom
    verifier_code: str = ""
    combo_compatible: List[str] = field(default_factory=list)


# ── Algorithm Templates (using $-substitution to avoid {} conflicts) ────

TEMPLATES = {
    "transform": Template('''
        # Transform input data
        result = {}
        for k, v in inputs.items():
            result[k] = v
        $custom_logic
        return AlgorithmResult("success", result, {"algorithm": "$name", "type": "transform"})
'''),
    "compute": Template('''
        # Compute result from inputs
        data = inputs.get("data", {})
        $custom_logic
        return AlgorithmResult("success", {"result": result, "computed": True},
            {"algorithm": "$name", "type": "compute"})
'''),
    "api": Template('''
        import urllib.request, json as _json
        url = inputs.get("url", "$api_url")
        headers = inputs.get("headers", {})
        headers["User-Agent"] = "DiveAI-AutoAlgo/1.0"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = _json.loads(resp.read())
        $custom_logic
        return AlgorithmResult("success", {"data": data}, {"algorithm": "$name", "type": "api"})
'''),
    "pipeline": Template('''
        # Multi-step pipeline
        steps_done = []
        data = inputs.get("data", {})
        $custom_logic
        return AlgorithmResult("success", {"steps": steps_done, "result": data},
            {"algorithm": "$name", "type": "pipeline"})
'''),
    "validator": Template('''
        # Validate input data
        errors = []
        data = inputs.get("data", {})
        $custom_logic
        valid = len(errors) == 0
        return AlgorithmResult("success" if valid else "failure",
            {"valid": valid, "errors": errors},
            {"algorithm": "$name", "type": "validator"})
'''),
}

VERIFIER_TEMPLATES = {
    "schema": Template('''
class ${name}Verifier:
    def verify(self, result, context=None):
        from dive_core.specs import VerificationResult
        if result is None:
            return VerificationResult(False, 0.0, "Result is None", {})
        if not isinstance(result.data, dict):
            return VerificationResult(False, 0.0, "Result data is not dict", {})
        required = $required_fields
        missing = [k for k in required if k not in result.data]
        if missing:
            return VerificationResult(False, 0.5, f"Missing fields: {missing}", {"missing": missing})
        return VerificationResult(True, 1.0, "Schema valid", {})
'''),
    "range": Template('''
class ${name}Verifier:
    def verify(self, result, context=None):
        from dive_core.specs import VerificationResult
        if result is None:
            return VerificationResult(False, 0.0, "Result is None", {})
        value = result.data.get("$check_field", 0)
        in_range = $min_val <= value <= $max_val
        score = 1.0 if in_range else 0.0
        return VerificationResult(in_range, score,
            f"Value {value} {'in' if in_range else 'out of'} range [$min_val, $max_val]",
            {"value": value, "min": $min_val, "max": $max_val})
'''),
}

ALGORITHM_FILE_TEMPLATE = Template('''"""Auto-generated algorithm: $description."""
from dive_core.algorithms.base import BaseAlgorithm, AlgorithmResult
from dive_core.specs import AlgorithmSpec, VerificationResult

$verifier_code

class $class_name(BaseAlgorithm):
    """Auto-generated: $description"""

    def __init__(self):
        super().__init__()
        self.spec = AlgorithmSpec(
            name="$name",
            description="$description",
            version="1.0.0",
            input_schema=$input_schema,
            output_schema=$output_schema,
            verifier=$verifier_ref,
            cost_per_call=$cost,
            tags=$tags,
        )

    def execute(self, inputs, context=None):
        try:
$execute_body
        except Exception as e:
            return AlgorithmResult("failure", None, {"error": str(e), "algorithm": "$name"})

    def can_handle(self, task):
        keywords = $keywords
        task_lower = task.lower()
        return sum(1 for k in keywords if k in task_lower) / max(len(keywords), 1)
''')


class AutoAlgorithmCreator:
    """
    Creates, validates, and deploys new algorithms automatically.
    Core engine for autonomous algorithm generation.
    """

    def __init__(self, algorithms_dir: Optional[str] = None):
        self.algorithms_dir = algorithms_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "algorithms", "auto_generated"
        )
        os.makedirs(self.algorithms_dir, exist_ok=True)

        # Ensure __init__.py
        init = os.path.join(self.algorithms_dir, "__init__.py")
        if not os.path.exists(init):
            with open(init, "w") as f:
                f.write("# Auto-generated algorithms\n")

        self._registry: Dict[str, Dict] = {}
        self._creation_log: List[Dict] = []
        self._load_registry()

    def _load_registry(self):
        """Load registry of created algorithms."""
        reg_file = os.path.join(self.algorithms_dir, "_registry.json")
        if os.path.exists(reg_file):
            with open(reg_file) as f:
                self._registry = json.load(f)

    def _save_registry(self):
        """Save registry to disk."""
        reg_file = os.path.join(self.algorithms_dir, "_registry.json")
        with open(reg_file, "w") as f:
            json.dump(self._registry, f, indent=2)

    def _to_class_name(self, name: str) -> str:
        parts = re.sub(r'[^a-zA-Z0-9]', ' ', name).split()
        return ''.join(p.capitalize() for p in parts) + 'Algorithm'

    def _to_file_name(self, name: str) -> str:
        return re.sub(r'[^a-z0-9]', '_', name.lower()) + '_algo.py'

    # ── Core Creation ──────────────────────────────

    def create(self, blueprint: AlgorithmBlueprint) -> Dict[str, Any]:
        """Create a new algorithm from a blueprint."""
        class_name = self._to_class_name(blueprint.name)
        file_name = self._to_file_name(blueprint.name)
        file_path = os.path.join(self.algorithms_dir, file_name)

        # Select and customize execute template (safe $-substitution)
        template = TEMPLATES.get(blueprint.logic_type, TEMPLATES["transform"])
        custom_logic = blueprint.logic_code or "pass"
        # Pre-indent subsequent lines of custom_logic to match template indent
        cl_lines = custom_logic.split("\n")
        custom_logic = "\n".join(
            cl_lines[0:1] + [("        " + ln if ln.strip() else ln) for ln in cl_lines[1:]]
        )
        execute_body = template.safe_substitute(
            name=blueprint.name, custom_logic=custom_logic,
            api_url=blueprint.input_schema.get("default_url", ""),
        )
        # Indent execute body for class method
        indented = "\n".join(f"            {line}" for line in execute_body.strip().split("\n"))

        # Generate verifier if needed
        verifier_code = ""
        verifier_ref = "None"
        if blueprint.verifier_type == "schema":
            verifier_code = VERIFIER_TEMPLATES["schema"].safe_substitute(
                name=class_name,
                required_fields=repr(list(blueprint.output_schema.keys())),
            )
            verifier_ref = f"{class_name}Verifier"
        elif blueprint.verifier_type == "range":
            verifier_code = VERIFIER_TEMPLATES["range"].safe_substitute(
                name=class_name,
                check_field=blueprint.verifier_code or "result",
                min_val=0, max_val=100,
            )
            verifier_ref = f"{class_name}Verifier"
        elif blueprint.verifier_type == "custom" and blueprint.verifier_code:
            verifier_code = blueprint.verifier_code
            verifier_ref = f"{class_name}Verifier"

        # Generate keywords for can_handle
        keywords = blueprint.tags + blueprint.name.lower().replace("-", " ").split()

        # Build full file (safe $-substitution)
        code = ALGORITHM_FILE_TEMPLATE.safe_substitute(
            description=blueprint.description, class_name=class_name,
            name=blueprint.name, input_schema=repr(blueprint.input_schema),
            output_schema=repr(blueprint.output_schema),
            verifier_code=verifier_code, verifier_ref=verifier_ref,
            cost=blueprint.cost_per_call, tags=repr(blueprint.tags),
            execute_body=indented, keywords=repr(keywords),
        )

        # Validate syntax
        try:
            compile(code, file_path, "exec")
            valid_syntax = True
        except SyntaxError as e:
            valid_syntax = False
            return {
                "success": False, "error": f"Syntax error: {e}",
                "file_path": file_path, "code_preview": code[:500],
            }

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Register
        entry = {
            "name": blueprint.name, "class_name": class_name,
            "file": file_name, "file_path": file_path,
            "category": blueprint.category, "logic_type": blueprint.logic_type,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "description": blueprint.description,
            "has_verifier": blueprint.verifier_type != "none",
            "tags": blueprint.tags,
        }
        self._registry[blueprint.name] = entry
        self._save_registry()

        self._creation_log.append({"action": "create", **entry})

        return {
            "success": True, "name": blueprint.name, "class_name": class_name,
            "file_path": file_path, "valid_syntax": valid_syntax,
            "has_verifier": blueprint.verifier_type != "none",
            "lines": len(code.split("\n")),
        }

    # ── Hot Deploy ─────────────────────────────────

    def deploy(self, name: str) -> Dict[str, Any]:
        """Hot-deploy an algorithm into the running system."""
        if name not in self._registry:
            return {"success": False, "error": f"Algorithm '{name}' not found"}

        entry = self._registry[name]
        file_path = entry["file_path"]

        try:
            # Ensure dive_core is importable from the generated file
            import sys as _sys
            backend_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), ".."
            )
            backend_dir = os.path.normpath(backend_dir)
            if backend_dir not in _sys.path:
                _sys.path.insert(0, backend_dir)

            # Dynamic import
            spec = importlib.util.spec_from_file_location(
                f"auto_algo_{name}", file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find the algorithm class
            algo_class = None
            for attr_name, attr in inspect.getmembers(module, inspect.isclass):
                if hasattr(attr, 'execute') and attr_name != 'BaseAlgorithm':
                    algo_class = attr
                    break

            if not algo_class:
                return {"success": False, "error": "No algorithm class found"}

            # Instantiate and verify
            instance = algo_class()
            test_result = instance.execute({"test": True})

            return {
                "success": True, "name": name, "class": algo_class.__name__,
                "instance": instance, "test_status": test_result.status,
                "deployed": True,
            }
        except Exception as e:
            return {
                "success": False, "error": str(e),
                "traceback": traceback.format_exc()[-1000:],
            }

    # ── Batch Create ──────────────────────────────

    def create_many(self, blueprints: List[AlgorithmBlueprint]) -> Dict[str, Any]:
        """Create multiple algorithms at once."""
        results = []
        for bp in blueprints:
            r = self.create(bp)
            results.append(r)
        created = sum(1 for r in results if r.get("success"))
        return {
            "total": len(blueprints), "created": created,
            "failed": len(blueprints) - created,
            "results": results,
        }

    # ── Query ─────────────────────────────────────

    def list_algorithms(self) -> List[Dict]:
        """List all auto-created algorithms."""
        return list(self._registry.values())

    def get_algorithm(self, name: str) -> Optional[Dict]:
        """Get details of a specific algorithm."""
        return self._registry.get(name)

    def delete_algorithm(self, name: str) -> bool:
        """Delete an auto-created algorithm."""
        if name not in self._registry:
            return False
        entry = self._registry.pop(name)
        fp = entry.get("file_path", "")
        if fp and os.path.exists(fp):
            os.unlink(fp)
        self._save_registry()
        return True

    def get_stats(self) -> Dict:
        """Get creation stats."""
        algos = list(self._registry.values())
        categories = {}
        for a in algos:
            cat = a.get("category", "custom")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_algorithms": len(algos),
            "categories": categories,
            "with_verifiers": sum(1 for a in algos if a.get("has_verifier")),
            "creation_log_entries": len(self._creation_log),
            "algorithms_dir": self.algorithms_dir,
        }

    def get_creation_log(self) -> List[Dict]:
        """Get the creation log."""
        return self._creation_log[-20:]

    # ── Quick Create Helpers ──────────────────────

    def quick_transform(self, name: str, description: str, logic: str = "",
                        tags: List[str] = None) -> Dict:
        """Quick-create a transform algorithm."""
        return self.create(AlgorithmBlueprint(
            name=name, description=description, logic_type="transform",
            logic_code=logic, tags=tags or [name.lower()],
        ))

    def quick_compute(self, name: str, description: str, logic: str = "",
                      tags: List[str] = None) -> Dict:
        """Quick-create a compute algorithm."""
        return self.create(AlgorithmBlueprint(
            name=name, description=description, logic_type="compute",
            logic_code=logic, tags=tags or [name.lower()],
        ))

    def quick_api(self, name: str, description: str, url: str = "",
                  tags: List[str] = None) -> Dict:
        """Quick-create an API algorithm."""
        return self.create(AlgorithmBlueprint(
            name=name, description=description, logic_type="api",
            input_schema={"url": {"type": "string"}, "default_url": url},
            tags=tags or [name.lower()],
        ))

    def quick_validator(self, name: str, description: str, logic: str = "",
                        tags: List[str] = None) -> Dict:
        """Quick-create a validator algorithm."""
        return self.create(AlgorithmBlueprint(
            name=name, description=description, logic_type="validator",
            logic_code=logic, tags=tags or [name.lower()],
        ))
