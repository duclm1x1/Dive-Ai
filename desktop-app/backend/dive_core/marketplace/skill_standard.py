"""
Dive AI — Agent Skills Open Standard (SKILL.md) Loader
Parse and load skills in the Agent Skills Open Standard format.
Cross-platform compatible with OpenClaw/Cursor/GitHub skills.
"""
import os, re, json, importlib.util
from typing import Dict, Any, List, Optional
from pathlib import Path


class SkillStandard:
    """
    Parser and loader for the Agent Skills Open Standard.
    Compatible with SKILL.md format used by OpenClaw, Cursor, GitHub, etc.
    """

    @staticmethod
    def parse_skill_md(path: str) -> Dict[str, Any]:
        """Parse a SKILL.md file into structured metadata + instructions."""
        if not os.path.exists(path):
            return {"error": "File not found"}

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse YAML frontmatter
        frontmatter = {}
        body = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()
                for line in fm_text.split("\n"):
                    if ":" in line:
                        key, val = line.split(":", 1)
                        key = key.strip()
                        val = val.strip()
                        # Parse JSON arrays/objects
                        if val.startswith("[") or val.startswith("{"):
                            try: val = json.loads(val)
                            except: pass
                        frontmatter[key] = val

        # Extract sections from markdown
        sections = {}
        current_section = "main"
        current_lines = []
        for line in body.split("\n"):
            if line.startswith("# ") and not line.startswith("## "):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line[2:].strip()
                current_lines = []
            elif line.startswith("## "):
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                current_section = line[3:].strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return {
            "frontmatter": frontmatter,
            "name": frontmatter.get("name", ""),
            "description": frontmatter.get("description", ""),
            "version": frontmatter.get("version", "1.0.0"),
            "author": frontmatter.get("author", "unknown"),
            "category": frontmatter.get("category", "custom"),
            "tags": frontmatter.get("tags", []),
            "sections": sections,
            "body": body,
            "path": path,
        }

    @staticmethod
    def discover_skills(directory: str) -> List[Dict]:
        """Discover all SKILL.md files in a directory tree."""
        skills = []
        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.upper() == "SKILL.MD":
                    path = os.path.join(root, f)
                    parsed = SkillStandard.parse_skill_md(path)
                    if "error" not in parsed:
                        parsed["directory"] = root
                        # Check for scripts
                        scripts_dir = os.path.join(root, "scripts")
                        if os.path.exists(scripts_dir):
                            parsed["scripts"] = os.listdir(scripts_dir)
                        skills.append(parsed)
        return skills

    @staticmethod
    def create_skill_md(name: str, description: str, instructions: str,
                        category: str = "custom", version: str = "1.0.0",
                        author: str = "dive-ai", tags: List[str] = None,
                        output_dir: str = None) -> str:
        """Create a SKILL.md file in the standard format."""
        tags = tags or []
        output_dir = output_dir or os.path.expanduser(f"~/.dive-ai/skills/{name}")
        os.makedirs(output_dir, exist_ok=True)

        content = f"""---
name: {name}
description: {description}
version: {version}
author: {author}
category: {category}
tags: {json.dumps(tags)}
---

# {name}

{description}

## Instructions

{instructions}
"""
        path = os.path.join(output_dir, "SKILL.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return path

    @staticmethod
    def convert_dive_skill_to_standard(skill_instance: Any,
                                       output_dir: str = None) -> str:
        """Convert a Dive AI BaseSkill to Agent Skills Open Standard format."""
        try:
            spec = skill_instance.skill_spec
            name = spec.name
            description = spec.description
            category = spec.category.value if hasattr(spec.category, 'value') else str(spec.category)
            tags = spec.tags
            version = spec.version

            instructions = f"""This skill provides: {description}

## Available Actions
Check the skill's input_schema for available actions and parameters.

## Input Schema
```json
{json.dumps(spec.input_schema, indent=2)}
```

## Output Schema
```json
{json.dumps(spec.output_schema, indent=2)}
```

## Combo Compatible
{', '.join(spec.combo_compatible) if spec.combo_compatible else 'Any'}
"""
            return SkillStandard.create_skill_md(
                name=name, description=description,
                instructions=instructions, category=category,
                version=version, author="dive-ai", tags=tags,
                output_dir=output_dir,
            )
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def import_external_skill(skill_dir: str, target_dir: str = None) -> Dict:
        """Import an external Agent Skills Open Standard skill into Dive AI."""
        skill_md = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md):
            return {"success": False, "error": "No SKILL.md found"}

        parsed = SkillStandard.parse_skill_md(skill_md)
        name = parsed.get("name", os.path.basename(skill_dir))

        if not target_dir:
            target_dir = os.path.expanduser(f"~/.dive-ai/divehub/imported/{name}")
        os.makedirs(target_dir, exist_ok=True)

        # Copy everything
        for item in os.listdir(skill_dir):
            src = os.path.join(skill_dir, item)
            dst = os.path.join(target_dir, item)
            if os.path.isdir(src):
                if os.path.exists(dst): shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

        return {
            "success": True, "name": name,
            "path": target_dir, "metadata": parsed.get("frontmatter", {}),
        }
