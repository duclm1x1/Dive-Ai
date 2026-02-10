"""
Dive AI Skill Installer — CLI for install/uninstall/list skills.
Bridges the gap: OpenClaw has CLI install, now Dive AI does too.
"""
import os, sys, json, shutil, importlib, inspect, time
from typing import Optional, Dict, List


class SkillInstaller:
    """Install, uninstall, and manage Dive AI skills."""
    
    def __init__(self, skills_dir: str = None):
        base = os.path.dirname(os.path.abspath(__file__))
        self.skills_dir = skills_dir or base
        self.manifest_path = os.path.join(self.skills_dir, "installed.json")
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, "r") as f:
                return json.load(f)
        return {"installed": {}, "version": "1.0.0"}

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2)

    def list_installed(self) -> List[Dict]:
        """List all installed skills."""
        result = []
        for cat_dir in os.listdir(self.skills_dir):
            cat_path = os.path.join(self.skills_dir, cat_dir)
            if os.path.isdir(cat_path) and not cat_dir.startswith(("_", ".")):
                for fname in os.listdir(cat_path):
                    if fname.endswith("_skill.py"):
                        result.append({
                            "category": cat_dir,
                            "file": fname,
                            "name": fname.replace("_skill.py", "").replace("_", "-"),
                            "path": os.path.join(cat_path, fname),
                        })
        return result

    def list_categories(self) -> List[str]:
        """List all skill categories."""
        cats = []
        for d in os.listdir(self.skills_dir):
            path = os.path.join(self.skills_dir, d)
            if os.path.isdir(path) and not d.startswith(("_", ".")):
                skill_count = sum(1 for f in os.listdir(path) if f.endswith("_skill.py"))
                if skill_count > 0:
                    cats.append({"category": d, "skills": skill_count})
        return cats

    def install_from_file(self, source_path: str, category: str = "custom") -> Dict:
        """Install a skill from a .py file into the registry."""
        if not os.path.exists(source_path):
            return {"error": f"File not found: {source_path}"}
        
        fname = os.path.basename(source_path)
        if not fname.endswith("_skill.py"):
            return {"error": "Skill files must end with _skill.py"}
        
        dest_dir = os.path.join(self.skills_dir, category)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Init file
        init_path = os.path.join(dest_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")
        
        dest = os.path.join(dest_dir, fname)
        shutil.copy2(source_path, dest)
        
        name = fname.replace("_skill.py", "").replace("_", "-")
        self._manifest["installed"][name] = {
            "category": category, "file": fname, "path": dest,
            "installed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        self._save_manifest()
        
        return {"installed": name, "category": category, "path": dest}

    def install_from_url(self, url: str, category: str = "custom") -> Dict:
        """Download and install a skill from a URL."""
        import urllib.request
        fname = url.split("/")[-1]
        if not fname.endswith("_skill.py"):
            fname += "_skill.py"
        
        tmp_path = os.path.join(self.skills_dir, f"_tmp_{fname}")
        try:
            urllib.request.urlretrieve(url, tmp_path)
            result = self.install_from_file(tmp_path, category)
            os.remove(tmp_path)
            return result
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return {"error": str(e)}

    def uninstall(self, name: str) -> Dict:
        """Uninstall a skill by name."""
        info = self._manifest["installed"].get(name)
        if info and os.path.exists(info["path"]):
            os.remove(info["path"])
            del self._manifest["installed"][name]
            self._save_manifest()
            return {"uninstalled": name, "path": info["path"]}
        
        # Try finding by filename
        for skill in self.list_installed():
            if skill["name"] == name:
                os.remove(skill["path"])
                return {"uninstalled": name, "path": skill["path"]}
        
        return {"error": f"Skill '{name}' not found"}

    def get_info(self, name: str) -> Optional[Dict]:
        """Get detailed info about a skill."""
        for skill in self.list_installed():
            if skill["name"] == name:
                try:
                    with open(skill["path"], "r") as f:
                        content = f.read()
                    # Extract docstring
                    import ast
                    tree = ast.parse(content)
                    docstring = ast.get_docstring(tree) or ""
                    lines = len(content.split("\n"))
                    skill["docstring"] = docstring
                    skill["lines"] = lines
                except:
                    pass
                return skill
        return None

    def get_stats(self) -> Dict:
        """Get installer statistics."""
        installed = self.list_installed()
        categories = self.list_categories()
        return {
            "total_skills": len(installed),
            "total_categories": len(categories),
            "categories": categories,
            "manifest_entries": len(self._manifest.get("installed", {})),
        }


# ── CLI Interface ──────────────────────────────────────────

def main():
    """CLI entry point for skill management."""
    import argparse
    parser = argparse.ArgumentParser(description="Dive AI Skill Installer")
    parser.add_argument("command", choices=["list", "categories", "install", "uninstall", "info", "stats"],
                       help="Command to execute")
    parser.add_argument("--name", "-n", help="Skill name")
    parser.add_argument("--file", "-f", help="Path to skill file to install")
    parser.add_argument("--url", "-u", help="URL to download skill from")
    parser.add_argument("--category", "-c", default="custom", help="Category for installation")
    
    args = parser.parse_args()
    installer = SkillInstaller()
    
    if args.command == "list":
        skills = installer.list_installed()
        print(f"\n📦 Installed Skills ({len(skills)}):\n")
        by_cat = {}
        for s in skills:
            by_cat.setdefault(s["category"], []).append(s["name"])
        for cat, names in sorted(by_cat.items()):
            print(f"  {cat}/ ({len(names)})")
            for n in names:
                print(f"    • {n}")
    
    elif args.command == "categories":
        cats = installer.list_categories()
        print(f"\n📂 Categories ({len(cats)}):\n")
        for c in cats:
            print(f"  {c['category']}/ — {c['skills']} skills")
    
    elif args.command == "install":
        if args.file:
            result = installer.install_from_file(args.file, args.category)
        elif args.url:
            result = installer.install_from_url(args.url, args.category)
        else:
            print("Error: --file or --url required")
            return
        print(json.dumps(result, indent=2))
    
    elif args.command == "uninstall":
        if not args.name:
            print("Error: --name required")
            return
        result = installer.uninstall(args.name)
        print(json.dumps(result, indent=2))
    
    elif args.command == "info":
        if not args.name:
            print("Error: --name required")
            return
        info = installer.get_info(args.name)
        print(json.dumps(info, indent=2) if info else f"Skill '{args.name}' not found")
    
    elif args.command == "stats":
        stats = installer.get_stats()
        print(f"\n📊 Skill System Stats:\n")
        print(f"  Total skills: {stats['total_skills']}")
        print(f"  Categories: {stats['total_categories']}")
        for c in stats["categories"]:
            print(f"    {c['category']}: {c['skills']} skills")


if __name__ == "__main__":
    main()
