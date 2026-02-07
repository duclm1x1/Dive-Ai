#!/usr/bin/env python3
"""Dive AI CLI - Memory Command: Store, recall, search, and manage project memory."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


class DiveMemoryCLI:
    """Lightweight memory system for CLI - file-based, project-scoped."""

    def __init__(self, storage_dir):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _project_dir(self, project):
        d = self.storage_dir / project
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _memory_file(self, project, category="knowledge"):
        return self._project_dir(project) / (category + ".md")

    def store(self, project, content, category="knowledge"):
        """Store a memory entry."""
        fpath = self._memory_file(project, category)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = "\n## [" + timestamp + "]\n" + content + "\n"

        with open(fpath, "a") as f:
            f.write(entry)

        return {"stored": True, "file": str(fpath), "category": category}

    def recall(self, project, category=None):
        """Recall all memories for a project."""
        pdir = self._project_dir(project)
        memories = {}

        if category:
            fpath = self._memory_file(project, category)
            if fpath.exists():
                memories[category] = fpath.read_text()
        else:
            for f in pdir.glob("*.md"):
                memories[f.stem] = f.read_text()

        return memories

    def search(self, project, query):
        """Search memories for a project."""
        results = []
        pdir = self._project_dir(project)

        for f in pdir.glob("*.md"):
            content = f.read_text()
            for i, line in enumerate(content.split("\n"), 1):
                if query.lower() in line.lower():
                    results.append({
                        "category": f.stem,
                        "line": i,
                        "content": line.strip()[:200],
                    })

        return results

    def list_projects(self):
        """List all projects with memory."""
        projects = []
        if self.storage_dir.exists():
            for d in self.storage_dir.iterdir():
                if d.is_dir():
                    files = list(d.glob("*.md"))
                    total_size = sum(f.stat().st_size for f in files)
                    projects.append({
                        "project": d.name,
                        "categories": [f.stem for f in files],
                        "total_entries": sum(
                            f.read_text().count("## [") for f in files
                        ),
                        "size_bytes": total_size,
                    })
        return projects

    def changelog(self, project, entry):
        """Add entry to project changelog."""
        fpath = self._project_dir(project) / "CHANGELOG.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not fpath.exists():
            header = "# " + project + " - Changelog\n\n"
            fpath.write_text(header)

        with open(fpath, "a") as f:
            f.write("\n## [" + timestamp + "]\n" + entry + "\n")

        return {"stored": True, "file": str(fpath)}


def execute(args):
    from src.cli.config import DiveConfig
    config = DiveConfig.load()

    mem = DiveMemoryCLI(config.memory.storage_dir)
    action = args.action
    project = args.project

    output = {
        "status": "success",
        "command": "memory",
        "action": action,
        "project": project,
        "timestamp": datetime.now().isoformat(),
    }

    if action == "store":
        if not args.content:
            output["status"] = "error"
            output["message"] = "--content is required for store action"
        else:
            result = mem.store(project, args.content, args.category)
            output["result"] = result

    elif action == "recall":
        output["memories"] = mem.recall(project, args.category if hasattr(args, "category") else None)

    elif action == "search":
        if not args.query:
            output["status"] = "error"
            output["message"] = "--query is required for search action"
        else:
            output["results"] = mem.search(project, args.query)
            output["total"] = len(output["results"])

    elif action == "list":
        output["projects"] = mem.list_projects()

    elif action == "changelog":
        if not args.content:
            output["status"] = "error"
            output["message"] = "--content is required for changelog action"
        else:
            result = mem.changelog(project, args.content)
            output["result"] = result

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
