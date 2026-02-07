from __future__ import annotations

import ast
import difflib
import hashlib
import json
import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


DEFAULT_EXCLUDES = {
    ".git", ".vibe", "__pycache__", "node_modules", "dist", "build", ".next",
    ".venv", "venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".cache",
}


@dataclass
class Pointer:
    id: str
    kind: str  # function|class|export|symbol
    name: str
    path: str
    start_line: int
    end_line: int
    signature: str = ""
    doc: str = ""
    tags: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["tags"] = d.get("tags") or []
        return d


def _safe_relpath(p: Path, root: Path) -> str:
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except Exception:
        return str(p.name)


def _hash_id(*parts: str) -> str:
    h = hashlib.sha1()
    for part in parts:
        h.update(part.encode("utf-8", errors="ignore"))
        h.update(b"\0")
    return h.hexdigest()[:16]


def _iter_repo_files(repo_root: Path, excludes: Optional[Iterable[str]] = None) -> Iterable[Path]:
    excludes = set(excludes or DEFAULT_EXCLUDES)
    for p in repo_root.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = set(p.relative_to(repo_root).parts)
        if rel_parts & excludes:
            continue
        yield p


def _read_lines(path: Path) -> List[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        try:
            return path.read_text(errors="ignore").splitlines()
        except Exception:
            return []


def _py_signature(node: ast.AST) -> str:
    # Best-effort signature rendering (no defaults pretty-printing to keep stable)
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    args = node.args
    parts: List[str] = []

    def _fmt_arg(a: ast.arg) -> str:
        return a.arg

    if getattr(args, "posonlyargs", None):
        parts.extend(_fmt_arg(a) for a in args.posonlyargs)
        parts.append("/")

    parts.extend(_fmt_arg(a) for a in args.args)

    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")

    parts.extend(_fmt_arg(a) for a in args.kwonlyargs)

    if args.kwarg:
        parts.append("**" + args.kwarg.arg)

    return f"{node.name}(" + ", ".join([p for p in parts if p != "/"] + (["/"] if "/" in parts else [])) + ")"


class AdvancedSearch:
    """
    V13 Advanced Searching (repo intelligence layer):
    - index: build file catalog + pointer registry (symbols with locations)
    - locate: query over pointers/files with facets + scoring
    - facets: summarize index distribution
    - hints: suggest next queries (symbol/path fuzzy)
    - pointer: resolve pointer id -> location + snippet
    """

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.index_dir = self.repo_root / ".vibe" / "index"
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.index_dir / "v13_search.json"

    # ---------- Index ----------
    def index(self, files: Optional[List[str]] = None, excludes: Optional[List[str]] = None) -> str:
        """Build/update the pointer registry incrementally.

        Speed model:
          - Reuse existing per-file facets + pointers when (mtime,size) unchanged.
          - Only re-parse changed/new files.

        Output: `.vibe/index/v13_search.json`
        """
        repo_root = self.repo_root
        excludes = list(set((excludes or []) + list(DEFAULT_EXCLUDES)))

        file_paths: List[Path]
        if files:
            file_paths = [Path(f) for f in files if Path(f).is_file()]
        else:
            file_paths = list(_iter_repo_files(repo_root, excludes=excludes))

        prev = self._load() or {}
        prev_files = {f.get('path'): f for f in (prev.get('files') or []) if isinstance(f, dict)}
        prev_pointers = prev.get('pointers') or {}
        prev_ptrs_by_path: Dict[str, List[Dict[str, Any]]] = {}
        if isinstance(prev_pointers, dict):
            for _, p in prev_pointers.items():
                if isinstance(p, dict) and p.get('path'):
                    prev_ptrs_by_path.setdefault(str(p['path']), []).append(p)

        pointers: Dict[str, Dict[str, Any]] = {}
        symbol_index: Dict[str, List[str]] = {}
        catalog_files: List[Dict[str, Any]] = []

        for fp in file_paths:
            rel = _safe_relpath(fp, repo_root)
            try:
                st = fp.stat()
            except Exception:
                continue

            ext = fp.suffix.lower()

            prev_meta = prev_files.get(rel)
            if isinstance(prev_meta, dict) and float(prev_meta.get('mtime') or 0.0) == float(st.st_mtime) and int(prev_meta.get('size') or 0) == int(st.st_size):
                # Reuse cached facets + pointers.
                facets = prev_meta.get('facets') or {}
                cached_ptrs = prev_ptrs_by_path.get(rel, [])
                for ptr in cached_ptrs:
                    pid = str(ptr.get('id') or '')
                    if not pid:
                        continue
                    pointers[pid] = dict(ptr)
                    key = (ptr.get('name') or '').lower()
                    if key:
                        symbol_index.setdefault(key, []).append(pid)

                catalog_files.append({
                    'path': rel,
                    'size': st.st_size,
                    'ext': ext,
                    'mtime': st.st_mtime,
                    'facets': facets,
                })
                continue

            # Changed/new -> parse
            file_facets, file_pointers = self._extract_file_facets_and_pointers(fp)
            for ptr in file_pointers:
                pointers[ptr.id] = ptr.to_dict()
                key = ptr.name.lower()
                symbol_index.setdefault(key, []).append(ptr.id)

            catalog_files.append({
                'path': rel,
                'size': st.st_size,
                'ext': ext,
                'mtime': st.st_mtime,
                'facets': file_facets,
            })

        data = {
            'version': '13.0',
            'created_at': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
            'repo_root': str(repo_root),
            'files': catalog_files,
            'pointers': pointers,
            'symbol_index': symbol_index,
        }

        self.index_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        return str(self.index_path)

    def _extract_file_facets_and_pointers(self, path: Path) -> Tuple[Dict[str, Any], List[Pointer]]:
        ext = path.suffix.lower()
        lines = _read_lines(path)
        text = "\n".join(lines)

        facets: Dict[str, Any] = {
            "lang": self._lang_from_ext(ext),
        }
        pointers: List[Pointer] = []

        rel_path = _safe_relpath(path, self.repo_root)

        if ext == ".py":
            try:
                tree = ast.parse(text)
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for n in node.names:
                            imports.append(n.name)
                    elif isinstance(node, ast.ImportFrom):
                        mod = node.module or ""
                        imports.append(mod)
                facets["imports"] = sorted(set([i for i in imports if i]))
                # pointers: functions/classes
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        kind = "class" if isinstance(node, ast.ClassDef) else "function"
                        start = getattr(node, "lineno", 1)
                        end = getattr(node, "end_lineno", start)
                        name = getattr(node, "name", "unknown")
                        sig = _py_signature(node) if kind == "function" else f"class {name}"
                        doc = ast.get_docstring(node) or ""
                        pid = _hash_id(rel_path, kind, name, str(start), str(end))
                        pointers.append(Pointer(
                            id=pid,
                            kind=kind,
                            name=name,
                            path=rel_path,
                            start_line=int(start),
                            end_line=int(end),
                            signature=sig,
                            doc=doc.strip()[:500],
                            tags=[],
                        ))
                facets["classes"] = [p.name for p in pointers if p.kind == "class"]
                facets["functions"] = [p.name for p in pointers if p.kind == "function"]
            except Exception:
                # fall back to cheap regex if parse fails
                facets["imports"] = [ln.strip() for ln in lines if ln.startswith(("import ", "from "))]
                facets["classes"] = [ln.strip() for ln in lines if ln.lstrip().startswith("class ")]
                facets["functions"] = [ln.strip() for ln in lines if ln.lstrip().startswith(("def ", "async def "))]
        elif ext in [".js", ".ts", ".tsx", ".jsx"]:
            exports = []
            # very light symbol discovery
            for i, ln in enumerate(lines, start=1):
                if "export " in ln:
                    exports.append(ln.strip())
                m = re.search(r'\bexport\s+(?:default\s+)?(?:function|class)\s+([A-Za-z0-9_]+)', ln)
                if m:
                    name = m.group(1)
                    pid = _hash_id(rel_path, "export", name, str(i))
                    pointers.append(Pointer(
                        id=pid, kind="export", name=name,
                        path=rel_path,
                        start_line=i, end_line=i,
                        signature=ln.strip()[:200],
                        doc="",
                        tags=[],
                    ))
                m2 = re.search(r'\b(?:function|class)\s+([A-Za-z0-9_]+)\b', ln)
                if m2 and not ln.strip().startswith("//"):
                    name = m2.group(1)
                    pid = _hash_id(rel_path, "symbol", name, str(i))
                    pointers.append(Pointer(
                        id=pid, kind="symbol", name=name,
                        path=rel_path,
                        start_line=i, end_line=i,
                        signature=ln.strip()[:200],
                        doc="",
                        tags=[],
                    ))
            facets["exports"] = exports[:200]
        else:
            # generic facets for other files
            if ext in [".yml", ".yaml", ".json", ".toml", ".ini", ".cfg"]:
                facets["config"] = True

        facets["symbols_count"] = len(pointers)
        return facets, pointers

    def _lang_from_ext(self, ext: str) -> str:
        return {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".json": "json",
            ".toml": "toml",
        }.get(ext, "unknown")

    # ---------- Query ----------
    def _load(self) -> Dict[str, Any]:
        if not self.index_path.exists():
            return {}
        return json.loads(self.index_path.read_text(encoding="utf-8", errors="ignore") or "{}")

    def locate(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Query DSL (space-separated):
          - kind:function|class|export|symbol
          - ext:.py|.ts|...
          - path:core/orchestrator
          - symbol:Orchestrator
          - import:requests
          - free tokens => fuzzy match over symbol name + path
        Returns best matches across pointer registry first; falls back to file paths.
        """
        data = self._load()
        if not data:
            return []

        tokens = [t.strip() for t in (query or "").split() if t.strip()]
        filters: Dict[str, str] = {}
        free: List[str] = []

        for t in tokens:
            if ":" in t:
                k, v = t.split(":", 1)
                filters[k.lower()] = v
            else:
                free.append(t)

        pointers = data.get("pointers", {})
        files = data.get("files", [])

        results: List[Tuple[float, Dict[str, Any]]] = []

        def score_ptr(ptr: Dict[str, Any]) -> float:
            s = 0.0
            name = (ptr.get("name") or "").lower()
            path = (ptr.get("path") or "").lower()
            sig = (ptr.get("signature") or "").lower()

            if "kind" in filters and ptr.get("kind") != filters["kind"]:
                return -1.0
            if "ext" in filters and not path.endswith(filters["ext"].lower()):
                return -1.0
            if "path" in filters and filters["path"].lower() not in path:
                return -1.0
            if "symbol" in filters and filters["symbol"].lower() not in name:
                return -1.0

            for tok in free:
                tl = tok.lower()
                if tl == name:
                    s += 10.0
                elif name.startswith(tl):
                    s += 6.0
                elif tl in name:
                    s += 4.0
                if tl in path:
                    s += 2.0
                if tl in sig:
                    s += 1.0
            if "symbol" in filters:
                s += 3.0
            return s

        for pid, ptr in pointers.items():
            sc = score_ptr(ptr)
            if sc <= 0:
                continue
            out = dict(ptr)
            out["score"] = round(sc, 3)
            results.append((sc, out))

        # fallback to files if no pointer match
        if not results:
            ql = (query or "").lower()
            for f in files:
                if ql and ql not in f.get("path", "").lower():
                    continue
                out = dict(f)
                out["kind"] = "file"
                out["score"] = 1.0
                results.append((1.0, out))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in results[: max(1, int(limit))]]

    def facets(self) -> Dict[str, Any]:
        data = self._load()
        if not data:
            return {}
        exts: Dict[str, int] = {}
        kinds: Dict[str, int] = {}
        langs: Dict[str, int] = {}
        for f in data.get("files", []):
            exts[f.get("ext", "")] = exts.get(f.get("ext", ""), 0) + 1
            lang = (f.get("facets") or {}).get("lang", "unknown")
            langs[lang] = langs.get(lang, 0) + 1
        for _, p in (data.get("pointers") or {}).items():
            k = p.get("kind", "unknown")
            kinds[k] = kinds.get(k, 0) + 1

        return {
            "version": data.get("version"),
            "files_total": len(data.get("files", [])),
            "pointers_total": len((data.get("pointers") or {})),
            "exts": dict(sorted(exts.items(), key=lambda kv: kv[1], reverse=True)),
            "langs": dict(sorted(langs.items(), key=lambda kv: kv[1], reverse=True)),
            "kinds": dict(sorted(kinds.items(), key=lambda kv: kv[1], reverse=True)),
        }

    def hints(self, query: str, max_items: int = 8) -> Dict[str, Any]:
        data = self._load()
        if not data:
            return {"hints": []}

        symbol_index = data.get("symbol_index", {}) or {}
        symbols = list(symbol_index.keys())
        files = [f.get("path", "") for f in data.get("files", [])]

        q = (query or "").strip()
        ql = q.lower()

        hint_symbols = []
        if ql:
            hint_symbols = difflib.get_close_matches(ql, symbols, n=max_items, cutoff=0.6)

        hint_paths = []
        if ql:
            hint_paths = [p for p in files if ql in p.lower()][:max_items]

        # Suggest structured query forms
        structured = []
        if hint_symbols:
            structured.extend([f"symbol:{s}" for s in hint_symbols[: max_items // 2]])
        if hint_paths:
            structured.extend([f"path:{p}" for p in hint_paths[: max_items // 2]])

        return {
            "query": query,
            "symbol_suggestions": hint_symbols,
            "path_suggestions": hint_paths,
            "structured_suggestions": structured[:max_items],
        }

    def pointer(self, pointer_id: str, context_lines: int = 18) -> Dict[str, Any]:
        data = self._load()
        ptr = (data.get("pointers") or {}).get(pointer_id)
        if not ptr:
            return {}

        abs_path = self.repo_root / ptr["path"]
        lines = _read_lines(abs_path)
        s = max(1, int(ptr.get("start_line", 1)))
        e = max(s, int(ptr.get("end_line", s)))
        # context
        cs = max(1, s - context_lines // 2)
        ce = min(len(lines), e + context_lines // 2)
        snippet = "\n".join(lines[cs-1:ce])

        out = dict(ptr)
        out["snippet"] = {
            "start_line": cs,
            "end_line": ce,
            "text": snippet,
        }
        return out
