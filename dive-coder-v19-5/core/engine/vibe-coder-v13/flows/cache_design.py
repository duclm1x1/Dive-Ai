from __future__ import annotations

import json
import time
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib


CACHE_ROOT_REL = Path(".cache") / "cache-design"


def _sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


@dataclass
class ValidatorResult:
    id: str
    ok: bool
    notes: List[str]


def init_cache_design(repo: Path, force: bool = False) -> Path:
    root = repo / CACHE_ROOT_REL
    artifacts = root / "artifacts"
    for p in [root, artifacts, root / "store", root / "index", root / "locks", root / "tmp"]:
        p.mkdir(parents=True, exist_ok=True)

    spec_path = root / "spec.yml"
    if force or not spec_path.exists():
        spec_path.write_text(
            """# cache-design spec (v13)
# Fill these fields, then run: vibe cache-design validate
surfaces:
  # - name: dashboard.summary
  #   kind: api|db|job|llm|vector
  #   scope: tenant|user|global
  #   inputs: ["..."]
  #   expected_qps: 0
  #   freshness:
  #     ttl_seconds: 300
  #     swr_seconds: 1800
  #     stale_if_error_seconds: 600
scope_model:
  tenant_id: required
  user_id: required
  permissions_fingerprint: optional
targets:
  api_call_reduction_pct: 90
expected_counts:
  ttl_only: 0
  swr: 0
  event_driven: 0
telemetry:
  required: true
""",
            encoding="utf-8",
        )

    templates: Dict[str, str] = {
        "A_cacheability_matrix.md": "# Artifact A — Cacheability Matrix\n\n| Surface | Cacheable | Scope | Freshness class | Strategy | Notes |\n|---|---:|---|---|---|---|\n",
        "B_freshness_contracts.md": "# Artifact B — Freshness Contracts\n\nDefine TTL/SWR/stale-if-error per surface.\n",
        "C_key_design_spec.md": "# Artifact C — Key Design Spec\n\nKeys MUST include tenant_id + user_id/principal_id + surface_name + version + request_fingerprint.\n",
        "D_invalidation_strategies.md": "# Artifact D — Invalidation Strategies\n\nClassify surfaces into TTL-only / SWR / event-driven.\n",
        "E_stampede_protection.md": "# Artifact E — Stampede Protection\n\nSingleflight/coalescing, lock TTL/lease, jitter, early refresh, negative caching.\n",
        "F_hot_key_mitigation.md": "# Artifact F — Hot-key Mitigation\n\nL1+L2, hot-key detection, rebuild throttling, admission control.\n",
        "G_failure_modes.md": "# Artifact G — Failure Modes\n\nCircuit breaker, stale-if-error policy, cold cache storm, poisoning defenses.\n",
        "H_single_host_integration.md": "# Artifact H — Single-host Integration\n\nBudgets, eviction policy, big-key detection, compression, quotas.\n",
    }

    for name, body in templates.items():
        p = artifacts / name
        if force or not p.exists():
            p.write_text(body, encoding="utf-8")

    ledger = artifacts / "ledger.jsonl"
    if force or not ledger.exists():
        ledger.write_text(
            """{"id":"S-001","statement":"Cache key includes tenant_id and user_id for all user-scoped surfaces","confidence":0.9,"status":"draft","owner":"","evidence":[]}
""",
            encoding="utf-8",
        )

    # placeholder indices
    (root / "index" / "tags.json").write_text("{}", encoding="utf-8")
    (root / "index" / "stats.json").write_text("{}", encoding="utf-8")

    return root



def _load_spec(spec_path: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    notes: List[str] = []
    if not spec_path.exists():
        notes.append("Missing spec.yml (run: vibe cache-design init)")
        return None, notes
    try:
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8", errors="replace")) or {}
        if not isinstance(data, dict):
            notes.append("spec.yml root must be a mapping/object")
            return None, notes
        return data, notes
    except Exception as e:
        notes.append(f"Failed to parse spec.yml: {e}")
        return None, notes


def _norm_strategy(v: Any) -> str:
    s = str(v or "").strip().lower()
    if s in {"ttl", "ttl-only", "ttl_only", "ttlonly"}:
        return "ttl-only"
    if s in {"swr", "stale-while-revalidate", "stale_while_revalidate"}:
        return "swr"
    if s in {"event", "event-driven", "event_driven", "cdc", "webhook"}:
        return "event-driven"
    return s or "unknown"


def _freshness_class(surface: Dict[str, Any]) -> str:
    f = surface.get("freshness") or {}
    if not isinstance(f, dict):
        return "unknown"
    ttl = f.get("ttl_seconds")
    swr = f.get("swr_seconds")
    try:
        ttl_i = int(ttl) if ttl is not None else None
        swr_i = int(swr) if swr is not None else None
    except Exception:
        return "unknown"
    if ttl_i is None:
        return "unknown"
    if swr_i and swr_i > 0:
        return f"TTL+SWR (ttl={ttl_i}s, swr={swr_i}s)"
    return f"TTL-only (ttl={ttl_i}s)"


def _render_cacheability_matrix(spec: Dict[str, Any]) -> str:
    surfaces = spec.get("surfaces") or []
    if not isinstance(surfaces, list):
        surfaces = []
    lines = [
        "# Artifact A — Cacheability Matrix",
        "",
        "| Surface | Cacheable | Scope | Freshness class | Strategy | Notes |",
        "|---|---:|---|---|---|---|",
    ]
    for s in surfaces:
        if not isinstance(s, dict):
            continue
        name = str(s.get("name") or "UNKNOWN")
        cacheable = bool(s.get("cacheable", True))
        scope = str(s.get("scope") or "unknown")
        strategy = _norm_strategy(s.get("strategy") or s.get("invalidation") or s.get("mode"))
        fresh = _freshness_class(s)
        notes = str(s.get("notes") or s.get("reason") or "")
        lines.append(f"| {name} | {'true' if cacheable else 'false'} | {scope} | {fresh} | {strategy} | {notes} |")
    lines.append("")
    lines.append("Generated by `vibe cache-design validate` from `spec.yml` (edit spec.yml to change).")
    lines.append("")
    return "\n".join(lines)


def _render_invalidation_summary(spec: Dict[str, Any]) -> str:
    surfaces = spec.get("surfaces") or []
    if not isinstance(surfaces, list):
        surfaces = []
    buckets = {"ttl-only": [], "swr": [], "event-driven": [], "unknown": []}
    for s in surfaces:
        if not isinstance(s, dict):
            continue
        name = str(s.get("name") or "UNKNOWN")
        strategy = _norm_strategy(s.get("strategy") or s.get("invalidation") or s.get("mode"))
        buckets.setdefault(strategy, []).append(name)
        if strategy not in buckets:
            buckets["unknown"].append(name)
    lines = ["# Artifact D — Invalidation Strategies", ""]
    for k in ["ttl-only", "swr", "event-driven", "unknown"]:
        items = buckets.get(k, [])
        lines.append(f"## {k} ({len(items)})")
        for n in items:
            lines.append(f"- {n}")
        lines.append("")
    lines.append("Generated by `vibe cache-design validate` from `spec.yml`.")
    lines.append("")
    return "\n".join(lines)

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def validate_cache_design(repo: Path) -> Tuple[Path, Dict[str, Any]]:
    root = repo / CACHE_ROOT_REL
    artifacts = root / "artifacts"
    report_path = artifacts / "validators_report.json"

    notes: List[str] = []
    spec_path = root / "spec.yml"
    spec, spec_notes = _load_spec(spec_path)
    notes.extend(spec_notes)

    # Auto-generate/refresh skeleton artifacts from spec.yml (deterministic, editable via spec)
    if spec:
        try:
            (artifacts / "A_cacheability_matrix.md").write_text(_render_cacheability_matrix(spec), encoding="utf-8")
            (artifacts / "D_invalidation_strategies.md").write_text(_render_invalidation_summary(spec), encoding="utf-8")
        except Exception as e:
            notes.append(f"Failed to generate skeleton artifacts from spec.yml: {e}")

    required = [
        "A_cacheability_matrix.md",
        "B_freshness_contracts.md",
        "C_key_design_spec.md",
        "D_invalidation_strategies.md",
        "E_stampede_protection.md",
        "F_hot_key_mitigation.md",
        "G_failure_modes.md",
        "H_single_host_integration.md",
        "ledger.jsonl",
    ]

    missing = [f for f in required if not (artifacts / f).exists()]
    if missing:
        notes.append(f"Missing artifacts: {missing}")

    # Enforce expected invalidation strategy counts (Enterprise requirement)
    counts_ok = True
    counts_detail: Dict[str, Any] = {"actual": {}, "expected": {}}

    if spec and isinstance(spec.get("surfaces"), list):
        actual = {"ttl_only": 0, "swr": 0, "event_driven": 0, "unknown": 0}
        for s in spec.get("surfaces", []):
            if not isinstance(s, dict):
                continue
            strat = _norm_strategy(s.get("strategy") or s.get("invalidation") or s.get("mode"))
            if strat == "ttl-only":
                actual["ttl_only"] += 1
            elif strat == "swr":
                actual["swr"] += 1
            elif strat == "event-driven":
                actual["event_driven"] += 1
            else:
                actual["unknown"] += 1

        counts_detail["actual"] = actual
        expected = spec.get("expected_counts") or {}

        if isinstance(expected, dict):
            def _coerce(v: Any, default: int) -> int:
                try:
                    if v is None:
                        return default
                    if isinstance(v, str) and v.strip().upper() in {"TODO", ""}:
                        return default
                    return int(v)
                except Exception:
                    return default

            exp = {
                "ttl_only": _coerce(expected.get("ttl_only"), actual["ttl_only"]),
                "swr": _coerce(expected.get("swr"), actual["swr"]),
                "event_driven": _coerce(expected.get("event_driven"), actual["event_driven"]),
            }

            # Enforce only if user explicitly set values OR enforce_counts=true
            enforce_counts = bool(spec.get("enforce_counts", False))
            user_set = any(
                (k in expected) and not (expected.get(k) in (None, 0, "0", "TODO", ""))
                for k in ["ttl_only", "swr", "event_driven"]
            )

            counts_detail["expected"] = exp
            if not (enforce_counts or user_set):
                notes.append(f"expected_counts not set; fill spec.yml expected_counts or set enforce_counts=true. Actual={actual}")
            else:
                if (actual["ttl_only"], actual["swr"], actual["event_driven"]) != (exp["ttl_only"], exp["swr"], exp["event_driven"]):
                    counts_ok = False
                    notes.append(f"Expected_counts mismatch: actual={actual} expected={exp}")

    c_key = _read_text(artifacts / "C_key_design_spec.md")
    b_fresh = _read_text(artifacts / "B_freshness_contracts.md")
    e_stampede = _read_text(artifacts / "E_stampede_protection.md")
    g_fail = _read_text(artifacts / "G_failure_modes.md")

    v131 = ValidatorResult(
        id="13.1",
        ok=("tenant" in c_key.lower() and "user" in c_key.lower()),
        notes=[
            "Key spec should explicitly require tenant_id + user_id/principal_id.",
            "Ensure no secrets/tokens/raw PII are cached.",
        ],
    )
    v132 = ValidatorResult(
        id="13.2",
        ok=("ttl" in b_fresh.lower()) and counts_ok,
        notes=[
            "Freshness contracts should define ttl_seconds (and optionally swr/stale-if-error).",
            "Confirm contracts match cacheability matrix classes.",
            "If you set expected_counts in spec.yml, the counts must match.",
        ],
    )
    v133 = ValidatorResult(
        id="13.3",
        ok=("singleflight" in e_stampede.lower() or "coalesc" in e_stampede.lower())
        and ("circuit" in g_fail.lower() or "breaker" in g_fail.lower()),
        notes=[
            "Stampede protection should include singleflight/coalescing and lock TTL/lease.",
            "Failure modes should include circuit breaker + admission control behaviors.",
        ],
    )

    results = [v131, v132, v133]
    ok = all(r.ok for r in results) and not missing

    # Build hash inventory for reproducibility (E3-friendly)
    artifact_hashes: Dict[str, str] = {}
    for f in required:
        p = artifacts / f
        if p.exists():
            artifact_hashes[str(p.relative_to(repo))] = _sha256_file(p)
    if spec_path.exists():
        artifact_hashes[str(spec_path.relative_to(repo))] = _sha256_file(spec_path)

    report = {
        "ok": ok,
        "generated_at_unix": int(time.time()),
        "cache_root": str(root.relative_to(repo)),
        "spec_path": str(spec_path.relative_to(repo)) if spec_path.exists() else None,
        "missing": missing,
        "strategy_counts": counts_detail,
        "validators": [{"id": r.id, "ok": r.ok, "notes": r.notes} for r in results],
        "notes": notes,
        "artifact_hashes": artifact_hashes,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path, report


def report_cache_design(repo: Path, out_path: Optional[Path] = None) -> Tuple[Path, Path]:
    """Emit an E3 EvidencePack + claims ledger for cache-design skill outputs.

    Returns (evidencepack_path, claims_path).
    """
    root = repo / CACHE_ROOT_REL
    artifacts = root / "artifacts"
    validators_path = artifacts / "validators_report.json"
    if not validators_path.exists():
        # ensure validators exist
        validate_cache_design(repo)

    # Collect artifacts
    to_include: List[Path] = []
    for p in artifacts.glob("*"):
        if p.is_file():
            to_include.append(p)

    # Build evidencepack
    entries: List[Dict[str, Any]] = []
    for p in sorted(to_include, key=lambda x: str(x)):
        rel = str(p.relative_to(repo))
        b = p.read_bytes()
        entries.append({"path": rel, "sha256": _sha256_bytes(b), "bytes": len(b)})

    evidencepack = {
        "schema": "vibe.cache_design.evidencepack.v1",
        "evidence_level": "E3",
        "tool": "vibe-coder-v13 cache-design",
        "generated_at_unix": int(time.time()),
        "cache_root": str(root.relative_to(repo)),
        "artifacts": entries,
    }

    out_path = out_path or (artifacts / "cache_design.evidencepack.json")
    out_path.write_text(json.dumps(evidencepack, indent=2), encoding="utf-8")

    # Claims ledger (skill-scoped)
    claims_path = artifacts / "cache_design.claims.json"
    ok = False
    try:
        vr = json.loads(validators_path.read_text(encoding="utf-8"))
        ok = bool(vr.get("ok"))
    except Exception:
        ok = False

    claims = [
        {
            "id": "CD-001",
            "claim": "cache-design artifacts A–H exist and validators 13.1–13.3 pass",
            "evidence_level": "E3",
            "artifact": str(validators_path.relative_to(repo)) if validators_path.exists() else None,
            "artifact_sha256": _sha256_file(validators_path) if validators_path.exists() else None,
            "ok": ok,
        },
        {
            "id": "CD-002",
            "claim": "cacheability matrix and invalidation strategies skeletons are generated from spec.yml",
            "evidence_level": "E3",
            "artifact": str((artifacts / "A_cacheability_matrix.md").relative_to(repo)) if (artifacts / "A_cacheability_matrix.md").exists() else None,
            "artifact_sha256": _sha256_file(artifacts / "A_cacheability_matrix.md") if (artifacts / "A_cacheability_matrix.md").exists() else None,
            "ok": (artifacts / "A_cacheability_matrix.md").exists(),
        },
    ]
    claims_path.write_text(json.dumps({"schema":"vibe.cache_design.claims.v1","generated_at_unix": int(time.time()),"claims": claims}, indent=2), encoding="utf-8")

    return out_path, claims_path
