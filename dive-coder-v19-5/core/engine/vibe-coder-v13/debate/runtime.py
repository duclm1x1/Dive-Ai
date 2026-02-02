from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from core.models import Report


@dataclass
class Argument:
    side: str  # 'pro' or 'con'
    title: str
    body: str
    evidence: List[str]


@dataclass
class DebateSummary:
    question: str
    args: List[Argument]
    recommendation: str
    guardrails: List[str]


def generate_debate(question: str, report: Optional[Report] = None) -> DebateSummary:
    """Generate a structured debate frame.

    This runtime is intentionally deterministic/offline: it does not call an LLM.
    It produces a debate script that an agent (Antigravity) can run to challenge fixes.
    """
    q = (question or '').strip() or 'Proposed change'
    evidence: List[str] = []
    if report is not None:
        evidence.append(f"repo:{report.repo_root}")
        for f in (report.findings or [])[:8]:
            evidence.append(f"finding:{f.rule_id}:{f.file}:{f.line}")

    pros = [
        Argument(
            side='pro',
            title='Improves reliability/maintainability',
            body='Applies best-practice fixes and verification gates; reduces regressions.',
            evidence=evidence[:4],
        ),
        Argument(
            side='pro',
            title='Enterprise traceability',
            body='Produces SARIF/markdown reports and keeps an audit trail for compliance.',
            evidence=evidence[:4],
        ),
    ]

    cons = [
        Argument(
            side='con',
            title='Risk of over-automation',
            body='Auto-patches can change semantics; must be constrained to safe transforms and gated by tests.',
            evidence=evidence[-4:] if evidence else [],
        ),
        Argument(
            side='con',
            title='Tooling availability variance',
            body='Gates like semgrep/ruff may not exist in all environments; requires policy-aware fallbacks.',
            evidence=[],
        ),
    ]

    guardrails = [
        'Only apply patches that are idempotent and reversible (unified diff).',
        'Require passing gates (typecheck/tests/build) before merge.',
        'For security findings, prefer fail-closed defaults (mask secrets, disable dangerous calls).',
        'Record skills.selected[] triggers so reviewers can verify decisioning.',
    ]

    rec = 'Proceed if gates pass; otherwise narrow scope to the highest-confidence findings and re-run verification.'

    return DebateSummary(question=q, args=pros + cons, recommendation=rec, guardrails=guardrails)


def to_dict(d: DebateSummary) -> Dict[str, Any]:
    return {
        'question': d.question,
        'arguments': [asdict(a) for a in d.args],
        'recommendation': d.recommendation,
        'guardrails': d.guardrails,
    }


def to_markdown(d: DebateSummary) -> str:
    lines: List[str] = []
    lines.append(f"# Debate\n\n**Question:** {d.question}\n")
    lines.append('## Arguments\n')
    for a in d.args:
        lines.append(f"### {a.side.upper()}: {a.title}\n")
        lines.append(a.body + '\n')
        if a.evidence:
            lines.append('Evidence:')
            for e in a.evidence:
                lines.append(f"- {e}")
            lines.append('')
    lines.append('## Guardrails\n')
    for g in d.guardrails:
        lines.append(f"- {g}")
    lines.append('\n## Recommendation\n')
    lines.append(d.recommendation)
    lines.append('')
    return '\n'.join(lines)
