from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.skills_lock import load_skills_lock, verify_skill_pinned


@dataclass
class SkillDoc:
    skill_id: str
    rel_path: str
    abs_path: str
    title: str
    is_external: bool


def _title_from_md(text: str, fallback: str) -> str:
    for line in text.splitlines():
        ln = line.strip()
        if ln.startswith('# '):
            return ln[2:].strip()
        if ln.startswith('## '):
            return ln[3:].strip()
    return fallback


def index_skills(repo_root: str, *, enforce_lock: bool = False) -> Tuple[List[SkillDoc], List[Dict[str, Any]]]:
    """Return (skills, excluded_external)."""
    root = Path(repo_root)
    internal_dir = root / '.agent' / 'skills'
    external_dir = root / '.agent' / 'skills_external'

    lock = load_skills_lock(repo_root)

    skills: List[SkillDoc] = []
    excluded_external: List[Dict[str, Any]] = []

    def ingest_dir(d: Path, is_external: bool) -> None:
        if not d.exists():
            return
        for p in sorted(d.rglob('*.md')):
            rel_path = str(p.relative_to(root))
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                text = ''
            title = _title_from_md(text, fallback=p.stem)

            if is_external and enforce_lock:
                ok, reason = verify_skill_pinned(rel_path=rel_path, abs_path=str(p), lock=lock)
                if not ok:
                    excluded_external.append({'path': rel_path, 'reason': reason})
                    continue

            skills.append(SkillDoc(
                skill_id=p.stem,
                rel_path=rel_path,
                abs_path=str(p),
                title=title,
                is_external=is_external,
            ))

    ingest_dir(internal_dir, is_external=False)
    ingest_dir(external_dir, is_external=True)

    return skills, excluded_external


def find_skill(skills: List[SkillDoc], *, contains: str) -> Optional[SkillDoc]:
    q = contains.lower().strip()
    for s in skills:
        if q in s.rel_path.lower() or q in s.skill_id.lower() or q in s.title.lower():
            return s
    return None
