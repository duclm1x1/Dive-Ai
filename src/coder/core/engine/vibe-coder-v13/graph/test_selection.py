from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .import_graph import build_import_graph


_TEST_PATTERNS = (
    '*.spec.js', '*.spec.jsx', '*.spec.ts', '*.spec.tsx',
    '*.test.js', '*.test.jsx', '*.test.ts', '*.test.tsx',
)


def _discover_tests(repo_root: Path) -> List[str]:
    tests: Set[str] = set()
    # Python
    for p in repo_root.rglob('*.py'):
        rp = str(p.relative_to(repo_root))
        if rp.startswith('.vibe/') or '/.vibe/' in rp:
            continue
        if rp.startswith('tests/') or '/tests/' in rp or rp.endswith('_test.py'):
            tests.add(rp)
    # JS/TS
    for pat in _TEST_PATTERNS:
        for p in repo_root.rglob(pat):
            rp = str(p.relative_to(repo_root))
            if rp.startswith('.vibe/') or '/.vibe/' in rp or 'node_modules/' in rp:
                continue
            tests.add(rp)
    # __tests__ folders
    for p in repo_root.rglob('__tests__'):
        if not p.is_dir():
            continue
        for f in p.rglob('*'):
            if f.is_file():
                rp = str(f.relative_to(repo_root))
                if 'node_modules/' not in rp and '.vibe/' not in rp:
                    tests.add(rp)
    return sorted(tests)


def _top_dir(path: str) -> str:
    parts = Path(path).parts
    return parts[0] if parts else ''


def _score_test(test_path: str, impacted: Set[str]) -> float:
    td = _top_dir(test_path)
    score = 0.0
    for f in impacted:
        if _top_dir(f) == td and td:
            score += 2.0
        if Path(f).parent == Path(test_path).parent:
            score += 3.0
        # same basename token
        if Path(f).stem in Path(test_path).stem:
            score += 1.0
    # prefer unit-like tests over e2e by name
    name = Path(test_path).name.lower()
    if 'e2e' in name or 'playwright' in name or 'cypress' in name:
        score -= 1.0
    return score


@dataclass
class TestSelection:
    changed_files: List[str]
    impacted_files: List[str]
    selected_tests: List[str]
    all_tests_count: int


def select_tests(repo_root: str, changed_files: List[str], max_tests: int = 40) -> TestSelection:
    """Select a focused set of tests to run based on import-graph impact.

    Heuristic approach (fast, offline):
      - Build best-effort import graph
      - Compute impacted files = reverse reachability from changed files
      - Score tests by directory proximity and name affinity
      - Fallback to 'tests smoke set' if nothing matches
    """
    rr = Path(repo_root).resolve()
    changed_rel = [str(Path(f)) for f in (changed_files or [])]
    g = build_import_graph(str(rr), files=changed_rel)
    impacted = set(changed_rel) | g.impacted_by(changed_rel, depth=6)

    tests = _discover_tests(rr)
    if not tests:
        return TestSelection(
            changed_files=changed_rel,
            impacted_files=sorted(impacted),
            selected_tests=[],
            all_tests_count=0,
        )

    scored: List[Tuple[float, str]] = []
    for t in tests:
        s = _score_test(t, impacted)
        if s > 0:
            scored.append((s, t))
    scored.sort(key=lambda x: x[0], reverse=True)

    selected = [t for _, t in scored[: int(max_tests)]]

    # Fallback: choose a small representative subset
    if not selected:
        selected = tests[: min(len(tests), int(max_tests), 10)]

    return TestSelection(
        changed_files=changed_rel,
        impacted_files=sorted(impacted),
        selected_tests=selected,
        all_tests_count=len(tests),
    )
