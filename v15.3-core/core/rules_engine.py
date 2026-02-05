from __future__ import annotations

import json
import re
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .models import Evidence, Finding
from utils.hash_utils import sha256_text


@dataclass
class RegexRule:
    id: str
    title: str
    category: str
    severity: str
    confidence: int
    regex: str
    description: str
    recommendation: str
    file_globs: List[str]
    cwe: Optional[str] = None
    owasp: Optional[str] = None


def load_rule_files(rule_dirs: List[str]) -> List[RegexRule]:
    rules: List[RegexRule] = []
    for d in rule_dirs:
        p = Path(d)
        if not p.exists() or not p.is_dir():
            continue
        for f in sorted(p.glob('*.json')):
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
            except Exception:
                continue
            if isinstance(data, dict):
                data = [data]
            if not isinstance(data, list):
                continue
            for obj in data:
                if not isinstance(obj, dict):
                    continue
                try:
                    rules.append(RegexRule(
                        id=str(obj['id']),
                        title=str(obj.get('title', obj['id'])),
                        category=str(obj.get('category', 'style')),
                        severity=str(obj.get('severity', 'medium')),
                        confidence=int(obj.get('confidence', 80)),
                        regex=str(obj['regex']),
                        description=str(obj.get('description', '')),
                        recommendation=str(obj.get('recommendation', '')),
                        file_globs=list(obj.get('file_globs', ['**/*'])),
                        cwe=str(obj.get('cwe')) if obj.get('cwe') else None,
                        owasp=str(obj.get('owasp')) if obj.get('owasp') else None,
                    ))
                except Exception:
                    continue
    return rules


def _file_matches(path: str, globs: List[str]) -> bool:
    # Support both relative and absolute patterns. We'll match on POSIX-like path.
    p = path.replace('\\', '/')
    for g in globs:
        if fnmatch(p, g) or fnmatch(Path(p).name, g):
            return True
    return False


def run_regex_rules(
    rules: Iterable[RegexRule],
    file_path: str,
    text: str,
    tool: str = 'vibe-regex',
) -> List[Finding]:
    findings: List[Finding] = []
    if not rules:
        return findings

    for r in rules:
        if not _file_matches(file_path, r.file_globs):
            continue

        try:
            pattern = re.compile(r.regex, re.MULTILINE)
        except re.error:
            continue

        for m in pattern.finditer(text):
            # Determine 1-based line number range
            start = m.start()
            end = m.end()
            start_line = text.count('\n', 0, start) + 1
            end_line = text.count('\n', 0, end) + 1
            snippet = text.splitlines()[start_line - 1] if start_line - 1 < len(text.splitlines()) else ''
            evidence = Evidence(
                file=file_path,
                start_line=start_line,
                end_line=end_line,
                snippet_hash=sha256_text(snippet)[:16],
            )
            findings.append(Finding(
                id=r.id,
                category=r.category,
                severity=r.severity,
                title=r.title,
                description=r.description or f"Matched regex rule {r.id} at line {start_line}.",
                recommendation=r.recommendation or 'Review and fix the matched pattern.',
                confidence=r.confidence,
                rule_id=r.id,
                tool=tool,
                cwe=r.cwe,
                owasp=r.owasp,
                evidence=evidence,
                tags=['regex'],
            ))

    return findings
