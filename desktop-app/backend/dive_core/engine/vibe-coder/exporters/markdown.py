from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from core.models import Finding, Report


def _md_escape(s: str) -> str:
    return (s or '').replace('|', '\\|').replace('\n', ' ').strip()


def write_report_markdown(path: str, report: Report) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = []
    lines.append(f"# Vibe Coder Report (v{report.version})")
    lines.append('')
    lines.append(f"- **Repo:** `{report.repo_root}`")
    lines.append(f"- **Mode:** `{report.mode}`")
    lines.append(f"- **Task:** {_md_escape(report.task) or 'N/A'}")
    lines.append(f"- **Detected stacks:** {', '.join(report.detected_stacks) if report.detected_stacks else 'N/A'}")
    lines.append(f"- **Score:** {report.scores.get('overall', 'N/A')} ({report.scores.get('grade', 'N/A')})")
    lines.append('')

    # Skills routing evidence (skills.selected[] + evidence ("triggers"))
    if isinstance(report.skills, dict) and report.skills:
        lines.append('## Skills')
        selected = report.skills.get('selected') or []
        triggers = report.skills.get('all_triggers') or []
        excluded = report.skills.get('excluded_external') or []
        enforced = report.skills.get('enforced_lock')

        lines.append('')
        lines.append(f"- **enforced_lock:** {str(bool(enforced)).lower()}")

        if selected:
            lines.append('')
            lines.append('**skills.selected**')
            lines.append('')
            for s in selected:
                if not isinstance(s, dict):
                    lines.append(f"- `{_md_escape(str(s))}`")
                    continue
                sid = _md_escape(str(s.get('skill_id') or s.get('id') or ''))
                title = _md_escape(str(s.get('title') or ''))
                score = str(s.get('score') or '')
                reason = _md_escape(str(s.get('reason') or ''))
                trig = s.get('triggers') or []
                trig_txt = ', '.join([_md_escape(str(t)) for t in trig]) if isinstance(trig, list) and trig else ''
                meta = ' '.join([x for x in [f"score:{score}" if score else '', f"reason:{reason}" if reason else ''] if x])
                if trig_txt:
                    meta = (meta + ' | ' if meta else '') + f"triggers: {trig_txt}"
                lines.append(f"- `{sid}` — {title}{(' — ' + meta) if meta else ''}")

        if triggers:
            lines.append('')
            lines.append('**evidence (triggers)**')
            lines.append('')
            for t in triggers:
                lines.append(f"- `{_md_escape(str(t))}`")

        if excluded:
            lines.append('')
            lines.append('**excluded (un-pinned external skills)**')
            lines.append('')
            for e in excluded:
                if isinstance(e, dict):
                    lines.append(f"- `{_md_escape(str(e.get('path') or ''))}` — {_md_escape(str(e.get('reason') or ''))}")
                else:
                    lines.append(f"- `{_md_escape(str(e))}`")

        lines.append('')

    # Action plan
    lines.append('## Action Plan')
    if not report.action_plan:
        lines.append('_No prioritized actions generated._')
    else:
        for i, a in enumerate(report.action_plan, 1):
            lines.append(f"{i}. **{a.get('priority','')}** [{a.get('category','')}] {_md_escape(a.get('title',''))}")
    lines.append('')

    # Findings table

    # Cruel system (always-on, Mode A)
    if isinstance(getattr(report, 'cruel', None), dict) and report.cruel:
        lines.append('')
        lines.append('## Cruel System')
        cruel = report.cruel
        lines.append(f"- **Enabled:** {bool(cruel.get('enabled'))}")
        lines.append(f"- **Mode:** `{_md_escape(str(cruel.get('mode') or 'A'))}`")
        lines.append(f"- **Files analyzed:** {cruel.get('files_analyzed', 0)}")
        if cruel.get('overall_score_avg') is not None:
            lines.append(f"- **Overall score (avg):** {cruel.get('overall_score_avg')}")
        dim = cruel.get('dimension_scores_avg') or {}
        if isinstance(dim, dict) and dim:
            top = sorted(dim.items(), key=lambda x: str(x[0]))
            lines.append('')
            lines.append('| Dimension | Avg Score |')
            lines.append('|---|---:|')
            for k, v in top:
                lines.append(f"| {_md_escape(str(k))} | {v} |")
        # top warnings
        file_reports = cruel.get('file_reports') or []
        warnings = []
        if isinstance(file_reports, list):
            for fr in file_reports:
                ws = (fr or {}).get('warnings') or []
                if isinstance(ws, list):
                    for w in ws:
                        if isinstance(w, dict):
                            warnings.append((fr.get('file'), w))
        if warnings:
            lines.append('')
            lines.append('### Top warnings (sample)')
            lines.append('')
            lines.append('| File | Severity | Dimension | Title |')
            lines.append('|---|---|---|---|')
            for (fn, w) in warnings[:20]:
                lines.append(f"| `{_md_escape(str(fn))}` | {_md_escape(str(w.get('severity') or ''))} | {_md_escape(str(w.get('dimension') or ''))} | {_md_escape(str(w.get('title') or ''))} |")

    lines.append('## Findings')
    lines.append('')
    lines.append('| Severity | Category | Confidence | Title | File:Line |')
    lines.append('|---|---|---:|---|---|')
    for f in report.findings:
        loc = ''
        if f.evidence is not None:
            loc = f"{f.evidence.file}:{f.evidence.start_line}"
        lines.append(
            f"| {f.severity} | {f.category} | {f.confidence} | {_md_escape(f.title)} | {_md_escape(loc)} |"
        )

    lines.append('')
    lines.append('## Gates')
    if not report.gates:
        lines.append('_No gates executed._')
    else:
        lines.append('')
        lines.append('| Gate | Allowed | Exit | Duration (ms) |')
        lines.append('|---|---|---:|---:|')
        for g in report.gates:
            lines.append(f"| {_md_escape(g.name)} | {str(bool(g.allowed)).lower()} | {g.exit_code if g.exit_code is not None else ''} | {g.duration_ms if g.duration_ms is not None else ''} |")

    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return str(p)


def write_findings_markdown(path: str, findings: List[Finding], title: str = 'Findings') -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append('')
    for f in findings:
        lines.append(f"## {f.id} - {f.title}")
        lines.append('')
        lines.append(f"- **Severity:** {f.severity}")
        lines.append(f"- **Category:** {f.category}")
        lines.append(f"- **Confidence:** {f.confidence}")
        if f.evidence is not None:
            lines.append(f"- **Location:** `{f.evidence.file}:{f.evidence.start_line}-{f.evidence.end_line}`")
        if f.cwe:
            lines.append(f"- **CWE:** {f.cwe}")
        lines.append('')
        lines.append(f"{f.description}")
        lines.append('')
        lines.append('**Recommendation**')
        lines.append('')
        lines.append(f"{f.recommendation}")
        lines.append('')
    p.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return str(p)
