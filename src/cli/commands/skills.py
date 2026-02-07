#!/usr/bin/env python3
"""Dive AI CLI - Skills Command: List, run, and manage skills."""
import json
import os
import sys
import importlib.util
from datetime import datetime
from pathlib import Path

DIVE_ROOT = Path(__file__).parent.parent.parent.parent
SKILLS_DIR = DIVE_ROOT / "src" / "skills"


def discover_skills():
    """Discover all available skills from the skills directory."""
    skills = []

    if not SKILLS_DIR.exists():
        return skills

    # Internal skills (Python files)
    internal_dir = SKILLS_DIR / "internal"
    if internal_dir.exists():
        for f in sorted(internal_dir.glob("*.py")):
            if f.name.startswith("_"):
                continue
            skill_name = f.stem
            # Try to extract docstring
            desc = ""
            try:
                content = f.read_text()
                for line in content.split("\n"):
                    if '"""' in line or "'''" in line:
                        desc = line.strip().strip("\"'").strip()
                        break
            except Exception:
                pass

            skills.append({
                "name": skill_name,
                "type": "internal",
                "path": str(f.relative_to(DIVE_ROOT)),
                "description": desc,
            })

    # Module skills (directories with __init__.py or main.py)
    modules_dir = SKILLS_DIR / "modules"
    if modules_dir.exists():
        for d in sorted(modules_dir.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                main_file = d / "main.py"
                init_file = d / "__init__.py"
                if main_file.exists() or init_file.exists():
                    desc = ""
                    readme = d / "README.md"
                    if readme.exists():
                        desc = readme.read_text().split("\n")[0].strip("# ").strip()

                    skills.append({
                        "name": d.name,
                        "type": "module",
                        "path": str(d.relative_to(DIVE_ROOT)),
                        "description": desc,
                    })

    # Layer skills (from skills/ root)
    for f in sorted(SKILLS_DIR.glob("*.py")):
        if f.name.startswith("_"):
            continue
        skills.append({
            "name": f.stem,
            "type": "layer",
            "path": str(f.relative_to(DIVE_ROOT)),
            "description": "",
        })

    return skills


def run_skill(skill_name, input_data=None):
    """Attempt to run a skill by name."""
    skills = discover_skills()
    target = None

    for s in skills:
        if s["name"] == skill_name:
            target = s
            break

    if not target:
        return {"error": "Skill not found: " + skill_name, "available": [s["name"] for s in skills]}

    skill_path = DIVE_ROOT / target["path"]

    if target["type"] == "module":
        main_file = skill_path / "main.py"
        if main_file.exists():
            spec = importlib.util.spec_from_file_location(skill_name, str(main_file))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "run"):
                return mod.run(input_data)
            elif hasattr(mod, "main"):
                return mod.main(input_data)

    elif target["type"] in ("internal", "layer"):
        spec = importlib.util.spec_from_file_location(skill_name, str(skill_path))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "run"):
            return mod.run(input_data)
        elif hasattr(mod, "main"):
            return mod.main(input_data)

    return {"status": "loaded", "skill": skill_name, "note": "Skill loaded but no run/main function found"}


def execute(args):
    output = {
        "status": "success",
        "command": "skills",
        "timestamp": datetime.now().isoformat(),
    }

    if args.list:
        skills = discover_skills()
        output["skills"] = skills
        output["total"] = len(skills)

    elif args.run:
        try:
            result = run_skill(args.run, args.input)
            output["skill"] = args.run
            output["result"] = result
        except Exception as e:
            output["status"] = "error"
            output["error"] = str(e)
    else:
        output["message"] = "Use --list to see available skills or --run <name> to run one"

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
