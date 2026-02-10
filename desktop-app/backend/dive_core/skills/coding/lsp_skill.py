"""LSP Integration Skill -- Code intelligence via Language Server Protocol."""
import subprocess, json, os, time
from ..base_skill import BaseSkill
from ...algorithms.base import AlgorithmResult
from ..skill_spec import SkillSpec, SkillCategory


class LspSkill(BaseSkill):
    def _build_spec(self):
        return SkillSpec(name="lsp", description="LSP: completions, diagnostics, hover, goto-def",
            category=SkillCategory.CODING, version="1.0.0",
            input_schema={"action": {"type": "string", "required": True},
                          "file": {"type": "string"}, "symbol": {"type": "string"},
                          "line": {"type": "integer"}, "character": {"type": "integer"}},
            output_schema={"servers": "dict", "diagnostics": "list", "completions": "list"},
            tags=["lsp", "code", "completion", "diagnostics", "intellisense", "ide"],
            trigger_patterns=[r"lsp\s+", r"code\s+complete", r"diagnostics", r"hover\s+info"],
            combo_compatible=["code-review", "project-scaffold", "refactor"],
            combo_position="any")

    SERVERS = {
        "python": ["pyright-langserver", "pylsp"],
        "typescript": ["typescript-language-server"],
        "rust": ["rust-analyzer"],
        "go": ["gopls"],
        "c": ["clangd"],
    }

    def _execute(self, inputs, context=None):
        action = inputs.get("action", "status")

        if action == "status":
            return self._check_servers()
        elif action == "diagnose":
            return self._diagnose(inputs)
        elif action == "complete":
            return self._complete(inputs)
        elif action == "analyze":
            return self._analyze(inputs)
        elif action == "hover":
            symbol = inputs.get("symbol", "")
            info = {}
            try:
                obj = eval(symbol)
                info = {"type": type(obj).__name__, "doc": str(getattr(obj, '__doc__', ''))[:500]}
            except:
                info = {"symbol": symbol, "note": "Run LSP server for full hover info"}
            return AlgorithmResult("success", {"hover": info}, {"skill": "lsp"})

        return AlgorithmResult("failure", None, {"error": f"Unknown action: {action}"})

    def _check_servers(self):
        available = {}
        for lang, cmds in self.SERVERS.items():
            found = False
            for cmd in cmds:
                try:
                    r = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
                    if r.returncode == 0:
                        available[lang] = {"server": cmd, "available": True}
                        found = True
                        break
                except:
                    pass
            if not found:
                available[lang] = {"server": cmds[0], "available": False}
        return AlgorithmResult("success",
            {"servers": available, "total": len(available),
             "available": sum(1 for v in available.values() if v["available"])},
            {"skill": "lsp"})

    def _diagnose(self, inputs):
        file_path = inputs.get("file", "")
        if not file_path or not os.path.exists(file_path):
            return AlgorithmResult("failure", None, {"error": "File not found"})
        ext = os.path.splitext(file_path)[1].lower()
        diagnostics = []
        if ext == ".py":
            try:
                import py_compile
                py_compile.compile(file_path, doraise=True)
                diagnostics.append({"type": "syntax", "status": "ok"})
            except py_compile.PyCompileError as e:
                diagnostics.append({"type": "syntax", "status": "error", "message": str(e)})
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
            diagnostics.append({"type": "metrics", "lines": content.count("\n")+1,
                "imports": content.count("import "), "functions": content.count("def "),
                "classes": content.count("class ")})
        elif ext in [".ts", ".tsx", ".js", ".jsx"]:
            try:
                r = subprocess.run(["npx", "tsc", "--noEmit", file_path],
                                   capture_output=True, text=True, timeout=30)
                diagnostics.append({"type": "typescript",
                    "status": "ok" if r.returncode == 0 else "error"})
            except:
                diagnostics.append({"type": "typescript", "status": "not_available"})
        return AlgorithmResult("success", {"file": file_path, "diagnostics": diagnostics},
                               {"skill": "lsp"})

    def _complete(self, inputs):
        file_path = inputs.get("file", "")
        if not file_path or not os.path.exists(file_path):
            return AlgorithmResult("failure", None, {"error": "File not found"})
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        completions = set()
        for l in lines:
            l = l.strip()
            if l.startswith("def ") and "(" in l:
                completions.add(l[4:l.index("(")].strip())
            elif l.startswith("class ") and ("(" in l or ":" in l):
                end = l.index("(") if "(" in l else l.index(":")
                completions.add(l[6:end].strip())
        return AlgorithmResult("success",
            {"completions": sorted(completions), "count": len(completions)},
            {"skill": "lsp"})

    def _analyze(self, inputs):
        file_path = inputs.get("file", "")
        if not file_path or not os.path.exists(file_path):
            return AlgorithmResult("failure", None, {"error": "File not found"})
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.split("\n")
        return AlgorithmResult("success", {
            "file": file_path, "lines": len(lines),
            "blank_lines": sum(1 for l in lines if not l.strip()),
            "comment_lines": sum(1 for l in lines if l.strip().startswith("#")),
            "functions": content.count("def "),
            "classes": content.count("class "),
            "imports": content.count("import "),
            "size_bytes": len(content),
        }, {"skill": "lsp"})
