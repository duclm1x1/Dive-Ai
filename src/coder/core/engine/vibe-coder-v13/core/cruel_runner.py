from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cruel.cruel_system import CruelSystem


_DEFAULT_EXTS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".sh": "bash",
}


def _is_ignored(path: Path) -> bool:
    parts = set(path.parts)
    ignore = {
        ".git",
        "node_modules",
        "dist",
        "build",
        ".next",
        ".turbo",
        ".cache",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
    }
    return any(p in ignore for p in parts)


def select_cruel_files(repo_root: str, *, max_files: int = 40, max_bytes: int = 120_000) -> List[str]:
    """
    Select a stable subset of files for Cruel analysis to keep runtime predictable.
    """
    root = Path(repo_root)
    out: List[str] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if _is_ignored(p):
            continue
        ext = p.suffix.lower()
        if ext not in _DEFAULT_EXTS:
            continue
        try:
            st = p.stat()
        except OSError:
            continue
        if st.st_size <= 0 or st.st_size > max_bytes:
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        out.append(rel)
        if len(out) >= max_files:
            break
    return out


def run_cruel(repo_root: str, *, rel_files: Optional[List[str]] = None, max_warnings_per_file: int = 20) -> Dict[str, Any]:
    """
    Run CruelSystem against selected files and return a compact report suitable for attaching to Vibe report.
    """
    root = Path(repo_root)
    files = rel_files or select_cruel_files(repo_root)

    cs = CruelSystem()

    file_reports: List[Dict[str, Any]] = []
    warnings_total = 0

    for rel in files:
        p = root / rel
        ext = p.suffix.lower()
        lang = _DEFAULT_EXTS.get(ext, "text")
        try:
            code = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        rep = cs.analyze(code, language=lang, filename=rel)
        # keep only top warnings
        warnings = rep.get("warnings") or []
        if isinstance(warnings, list) and len(warnings) > max_warnings_per_file:
            warnings = warnings[:max_warnings_per_file]
        rep["warnings"] = warnings
        warnings_total += len(warnings) if isinstance(warnings, list) else 0
        file_reports.append(
            {
                "file": rel,
                "language": lang,
                "code_length": rep.get("code_length"),
                "overall_score": rep.get("overall_score"),
                "dimension_scores": rep.get("dimension_scores"),
                "warnings": warnings,
            }
        )

    # aggregate dimension averages
    dim_sums: Dict[str, float] = {}
    dim_counts: Dict[str, int] = {}
    overall_scores: List[float] = []
    for fr in file_reports:
        ds = fr.get("dimension_scores") or {}
        if isinstance(ds, dict):
            for k, v in ds.items():
                try:
                    fv = float(v)
                except Exception:
                    continue
                dim_sums[k] = dim_sums.get(k, 0.0) + fv
                dim_counts[k] = dim_counts.get(k, 0) + 1
        try:
            ov = float(fr.get("overall_score"))
            overall_scores.append(ov)
        except Exception:
            pass

    dim_avg = {k: (dim_sums[k] / max(1, dim_counts.get(k, 1))) for k in dim_sums}
    overall_avg = sum(overall_scores) / max(1, len(overall_scores)) if overall_scores else None

    return {
        "enabled": True,
        "mode": "A",
        "files_analyzed": len(file_reports),
        "files": [fr["file"] for fr in file_reports],
        "overall_score_avg": overall_avg,
        "dimension_scores_avg": dim_avg,
        "warnings_total": warnings_total,
        "file_reports": file_reports,
    }
