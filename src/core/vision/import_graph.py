from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from core.dependency_graph import DependencyAnalyzer
from advanced_searching.api import AdvancedSearch


_JS_IMPORT_RE = re.compile(r"\bimport\s+(?:[^;]+?)\s+from\s+['\"]([^'\"]+)['\"]|\brequire\(['\"]([^'\"]+)['\"]\)")
_TS_EXTS = {'.js', '.jsx', '.ts', '.tsx'}


def _is_local_spec(s: str) -> bool:
    return s.startswith('.') or s.startswith('/')


def _resolve_js_import(repo_root: Path, from_file: Path, spec: str) -> Optional[str]:
    """Resolve a local JS/TS import to a repo-relative file path (best-effort)."""
    if not _is_local_spec(spec):
        return None
    base = (from_file.parent / spec).resolve()
    candidates = []
    if base.suffix:
        candidates.append(base)
    else:
        for ext in _TS_EXTS:
            candidates.append(base.with_suffix(ext))
        for ext in _TS_EXTS:
            candidates.append(base / f'index{ext}')
    for c in candidates:
        try:
            if c.exists() and c.is_file():
                return str(c.relative_to(repo_root))
        except Exception:
            continue
    return None


@dataclass
class ImportGraph:
    graph: Dict[str, Set[str]]
    reverse: Dict[str, Set[str]]

    def impacted_by(self, changed: Iterable[str], depth: int = 6) -> Set[str]:
        """Reverse reachability: files that may be impacted by `changed`."""
        impacted: Set[str] = set()
        frontier: List[Tuple[str, int]] = [(c, 0) for c in changed]
        while frontier:
            node, d = frontier.pop()
            if d > depth:
                continue
            for parent in self.reverse.get(node, set()):
                if parent not in impacted:
                    impacted.add(parent)
                    frontier.append((parent, d + 1))
        return impacted


def build_import_graph(repo_root: str, files: Optional[List[str]] = None) -> ImportGraph:
    """Build a best-effort import graph for Python + JS/TS.

    Uses:
      - Python AST via DependencyAnalyzer
      - JS/TS regex import parsing (fast, partial)
      - AdvancedSearch facets as a supplemental signal (imports list)
    """
    rr = Path(repo_root).resolve()
    graph: Dict[str, Set[str]] = {}
    reverse: Dict[str, Set[str]] = {}

    # 1) Python
    try:
        py = DependencyAnalyzer(str(rr))
        if files:
            py.analyze([str(rr / f) if not str(f).startswith(str(rr)) else str(f) for f in files])
        else:
            # Fallback: analyze common python files only
            py_files = [str(p) for p in rr.rglob('*.py') if '.vibe' not in str(p)]
            py.analyze(py_files)
        for src, deps in py.graph.items():
            graph.setdefault(src, set()).update(deps)
        for dep, parents in py.reverse_graph.items():
            reverse.setdefault(dep, set()).update(parents)
    except Exception:
        pass

    # 2) JS/TS via regex scan (changed files only if provided)
    scan_paths: List[Path] = []
    if files:
        for f in files:
            p = (rr / f).resolve() if not str(f).startswith(str(rr)) else Path(f).resolve()
            if p.suffix.lower() in _TS_EXTS and p.exists():
                scan_paths.append(p)
    else:
        for ext in _TS_EXTS:
            scan_paths.extend([p for p in rr.rglob(f'*{ext}') if '.vibe' not in str(p) and 'node_modules' not in str(p)])

    for p in scan_paths:
        try:
            rel = str(p.relative_to(rr))
            txt = p.read_text(encoding='utf-8', errors='ignore')
            for m in _JS_IMPORT_RE.finditer(txt):
                spec = m.group(1) or m.group(2) or ''
                dep = _resolve_js_import(rr, p, spec)
                if not dep:
                    continue
                graph.setdefault(rel, set()).add(dep)
                reverse.setdefault(dep, set()).add(rel)
        except Exception:
            continue

    # 3) Supplemental: AdvancedSearch facets imports (fast)
    try:
        adv = AdvancedSearch(str(rr))
        data = adv._load()  # type: ignore[attr-defined]
        if not data:
            adv.index()
            data = adv._load()  # type: ignore[attr-defined]
        for f in data.get('files', []) if isinstance(data, dict) else []:
            rel = str(f.get('path') or '')
            facets = f.get('facets') or {}
            for imp in facets.get('imports') or []:
                # Only keep local-ish imports for enrichment (Python module names are handled above).
                if isinstance(imp, str) and (imp.startswith('.') or '/' in imp):
                    # Cannot resolve robustly; skip.
                    continue
            # no-op enrichment for now; reserved for future (module mapping)
    except Exception:
        pass

    return ImportGraph(graph=graph, reverse=reverse)
