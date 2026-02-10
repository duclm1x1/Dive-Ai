"""Autonomous Skill Generator — Writes and installs new skills on-the-fly.
OpenClaw key differentiator: agents can generate their own skills.
"""
import os, time, re
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

SKILL_TEMPLATE = '''"""{description}"""
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory

class {class_name}(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="{skill_name}", description="{description}",
            category=SkillCategory.{category}, version="1.0.0",
            input_schema={input_schema},
            output_schema={output_schema},
            tags={tags},
            combo_compatible=[], combo_position="any")

    def _execute(self, inputs, context=None):
        try:
{execute_body}
        except Exception as e:
            return AlgorithmResult("failure", None, {{"error": str(e)}})
'''

class SkillGeneratorSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="skill-generator", description="Autonomously generate and install new skills from specs",
            category=SkillCategory.AI, version="1.0.0",
            input_schema={"name": {"type": "string", "required": True},
                          "description": {"type": "string", "required": True},
                          "category": {"type": "string"},
                          "inputs": {"type": "dict"}, "outputs": {"type": "dict"},
                          "logic": {"type": "string"}, "tags": {"type": "list"}},
            output_schema={"file_path": "string", "class_name": "string", "installed": "boolean"},
            tags=["generate", "create", "skill", "autonomous", "meta", "self-modify"],
            trigger_patterns=[r"generate\s+skill", r"create\s+new\s+skill", r"build\s+skill\s+for"],
            combo_compatible=["self-improve", "code-review"],
            combo_position="any", cost_per_call=0.001)

    def _to_class_name(self, name):
        parts = re.sub(r'[^a-zA-Z0-9]', ' ', name).split()
        return ''.join(p.capitalize() for p in parts) + 'Skill'

    def _to_file_name(self, name):
        return re.sub(r'[^a-z0-9]', '_', name.lower()) + '_skill.py'

    def _execute(self, inputs, context=None):
        name = inputs.get("name", "")
        description = inputs.get("description", "")
        category = inputs.get("category", "CUSTOM").upper()
        input_schema = inputs.get("inputs", {"data": {"type": "string"}})
        output_schema = inputs.get("outputs", {"result": "string"})
        logic = inputs.get("logic", "")
        tags = inputs.get("tags", [name.lower()])

        if not name or not description:
            return AlgorithmResult("failure", None, {"error": "name and description required"})

        class_name = self._to_class_name(name)
        skill_name = re.sub(r'[^a-z0-9]', '-', name.lower())
        file_name = self._to_file_name(name)

        # Generate execute body
        if logic:
            # User provided custom logic
            execute_lines = []
            for line in logic.strip().split("\n"):
                execute_lines.append(f"            {line}")
            execute_body = "\n".join(execute_lines)
        else:
            # Default passthrough logic
            execute_body = f'''            result = {{}}
            for k, v in inputs.items():
                result[k] = v
            result["processed_by"] = "{skill_name}"
            return AlgorithmResult("success", result, {{"skill": "{skill_name}"}})'''

        # Generate the skill file
        code = SKILL_TEMPLATE.format(
            description=description, class_name=class_name, skill_name=skill_name,
            category=category, input_schema=repr(input_schema),
            output_schema=repr(output_schema), tags=repr(tags),
            execute_body=execute_body,
        )

        # Determine install location
        cat_dir = category.lower()
        skills_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skills_dir = os.path.join(skills_base, "skills", cat_dir)
        os.makedirs(skills_dir, exist_ok=True)

        # Ensure __init__.py exists
        init_file = os.path.join(skills_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")

        file_path = os.path.join(skills_dir, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Try to validate the generated code compiles
        try:
            compile(code, file_path, "exec")
            valid = True
        except SyntaxError as e:
            valid = False

        return AlgorithmResult("success", {
            "file_path": file_path, "class_name": class_name, "skill_name": skill_name,
            "category": cat_dir, "installed": True, "valid_syntax": valid,
            "lines": len(code.split("\n")),
        }, {"skill": "skill-generator"})
