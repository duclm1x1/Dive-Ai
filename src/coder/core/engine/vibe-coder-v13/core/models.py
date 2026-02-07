from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Literal


EvidenceLevel = Literal['E0', 'E1', 'E2', 'E3']


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


@dataclass
class Evidence:
    file: str
    start_line: int
    end_line: int
    snippet_hash: str

    @staticmethod
    def from_dict(d: Dict[str, Any] | None) -> Optional['Evidence']:
        if not isinstance(d, dict):
            return None
        return Evidence(
            file=str(d.get('file') or ''),
            start_line=int(d.get('start_line') or 1),
            end_line=int(d.get('end_line') or (d.get('start_line') or 1)),
            snippet_hash=str(d.get('snippet_hash') or ''),
        )


@dataclass
class Finding:
    """Canonical, tool-agnostic finding schema (v11).

    Notes:
      - `confidence` is 0..100.
      - `severity` is one of: critical|high|medium|low|info
      - `category` uses Vibe taxonomy (security, bug, performance, style, docs, architecture, dependency, test)
    """

    id: str
    category: str
    severity: str
    title: str
    description: str
    recommendation: str
    confidence: int

    rule_id: Optional[str] = None
    tool: Optional[str] = None
    cwe: Optional[str] = None
    owasp: Optional[str] = None

    evidence: Optional[Evidence] = None
    tags: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Finding':
        if not isinstance(d, dict):
            raise TypeError('Finding.from_dict expects dict')
        ev = Evidence.from_dict(d.get('evidence'))
        tags = d.get('tags')
        return Finding(
            id=str(d.get('id') or 'VIBE'),
            category=str(d.get('category') or 'style'),
            severity=str(d.get('severity') or 'low'),
            title=str(d.get('title') or ''),
            description=str(d.get('description') or ''),
            recommendation=str(d.get('recommendation') or ''),
            confidence=int(d.get('confidence') or 80),
            rule_id=str(d.get('rule_id')) if d.get('rule_id') else None,
            tool=str(d.get('tool')) if d.get('tool') else None,
            cwe=str(d.get('cwe')) if d.get('cwe') else None,
            owasp=str(d.get('owasp')) if d.get('owasp') else None,
            evidence=ev,
            tags=list(tags) if isinstance(tags, list) else None,
        )


@dataclass
class GateResult:
    name: str
    command: str
    allowed: bool
    # Evidence level for claims about this gate execution.
    # - E0: not executed / reasoning only
    # - E2: executed (stdout/stderr captured)
    # - E3: executed and produced reproducible artifacts (hashable files)
    evidence_level: EvidenceLevel = 'E0'
    exit_code: Optional[int] = None
    stdout: str = ''
    stderr: str = ''
    duration_ms: Optional[int] = None
    # Optional artifacts produced by the gate (e.g., SARIF paths).
    artifacts: Optional[Dict[str, str]] = None


@dataclass
class TraceSpan:
    name: str
    started_at: str
    finished_at: str
    duration_ms: int
    meta: Dict[str, Any]


@dataclass
class RunManifest:
    version: str
    started_at: str
    finished_at: str
    seed: int
    repo_root: str
    mode: str
    diff_base: Optional[str]
    file_count: int
    file_hashes: Dict[str, str]
    config_hash: str
    tool_versions: Dict[str, str]

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'RunManifest':
        if not isinstance(d, dict):
            raise TypeError('RunManifest.from_dict expects dict')
        return RunManifest(
            version=str(d.get('version') or ''),
            started_at=str(d.get('started_at') or ''),
            finished_at=str(d.get('finished_at') or ''),
            seed=int(d.get('seed') or 0),
            repo_root=str(d.get('repo_root') or ''),
            mode=str(d.get('mode') or ''),
            diff_base=d.get('diff_base'),
            file_count=int(d.get('file_count') or 0),
            file_hashes=dict(d.get('file_hashes') or {}),
            config_hash=str(d.get('config_hash') or ''),
            tool_versions=dict(d.get('tool_versions') or {}),
        )


@dataclass
class Report:
    version: str
    started_at: str
    finished_at: str

    repo_root: str
    mode: str
    task: str

    detected_stacks: List[str]
    analyzed_files: List[str]

    findings: List[Finding]
    scores: Dict[str, Any]
    action_plan: List[Dict[str, Any]]

    gates: List[GateResult]
    traces: List[TraceSpan]

    manifest: RunManifest

    # Governance: evidence level for the overall report.
    # - E0: analysis only (no executed tools)
    # - E2: tools/gates executed with captured output
    # - E3: reproducible artifacts produced (e.g., SARIF / EvidencePack)
    evidence_level: EvidenceLevel = 'E0'

    # Optional path to a machine-verifiable EvidencePack for this run.
    evidencepack_path: Optional[str] = None

    # v12: skill routing evidence (optional)
    skills: Optional[Dict[str, Any]] = None

    # v12: Cruel System report (optional)
    cruel: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'repo_root': self.repo_root,
            'mode': self.mode,
            'task': self.task,
            'detected_stacks': self.detected_stacks,
            'analyzed_files': self.analyzed_files,
            'findings': [f.to_dict() for f in self.findings],
            'scores': self.scores,
            'action_plan': self.action_plan,
            'gates': [asdict(g) for g in self.gates],
            'traces': [asdict(t) for t in self.traces],
            'manifest': asdict(self.manifest),
            'evidence_level': self.evidence_level,
            'evidencepack_path': self.evidencepack_path,
            'skills': self.skills,
            'cruel': self.cruel,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Report':
        if not isinstance(d, dict):
            raise TypeError('Report.from_dict expects dict')

        findings = [Finding.from_dict(x) for x in (d.get('findings') or []) if isinstance(x, dict)]
        manifest = RunManifest.from_dict(d.get('manifest') or {})

        # Gates/traces are optional for docs/sarif conversion.
        gates = []
        for g in d.get('gates') or []:
            if not isinstance(g, dict):
                continue
            gates.append(GateResult(
                name=str(g.get('name') or ''),
                command=str(g.get('command') or ''),
                allowed=bool(g.get('allowed')),
                evidence_level=str(g.get('evidence_level') or 'E0'),
                exit_code=int(g.get('exit_code')) if g.get('exit_code') is not None else None,
                stdout=str(g.get('stdout') or ''),
                stderr=str(g.get('stderr') or ''),
                duration_ms=int(g.get('duration_ms')) if g.get('duration_ms') is not None else None,
                artifacts=dict(g.get('artifacts') or {}) if isinstance(g.get('artifacts'), dict) else None,
            ))

        traces = []
        for t in d.get('traces') or []:
            if not isinstance(t, dict):
                continue
            traces.append(TraceSpan(
                name=str(t.get('name') or ''),
                started_at=str(t.get('started_at') or ''),
                finished_at=str(t.get('finished_at') or ''),
                duration_ms=int(t.get('duration_ms') or 0),
                meta=dict(t.get('meta') or {}),
            ))

        return Report(
            version=str(d.get('version') or ''),
            started_at=str(d.get('started_at') or ''),
            finished_at=str(d.get('finished_at') or ''),
            repo_root=str(d.get('repo_root') or ''),
            mode=str(d.get('mode') or ''),
            task=str(d.get('task') or ''),
            detected_stacks=list(d.get('detected_stacks') or []),
            analyzed_files=list(d.get('analyzed_files') or []),
            findings=findings,
            scores=dict(d.get('scores') or {}),
            action_plan=list(d.get('action_plan') or []),
            gates=gates,
            traces=traces,
            manifest=manifest,
            evidence_level=str(d.get('evidence_level') or 'E0'),
            evidencepack_path=str(d.get('evidencepack_path')) if d.get('evidencepack_path') else None,
            skills=dict(d.get('skills') or {}) if isinstance(d.get('skills'), dict) else None,
            cruel=dict(d.get('cruel') or {}) if isinstance(d.get('cruel'), dict) else None,
        )