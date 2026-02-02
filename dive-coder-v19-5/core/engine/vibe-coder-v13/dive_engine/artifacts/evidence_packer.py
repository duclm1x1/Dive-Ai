"""
Dive Engine V2 - Evidence Packer
=================================

This module implements the evidence packing system that automatically
collects and packages all E3 artifacts for a run.

Key Features:
- Auto-collect all run artifacts
- SHA256 hash verification
- Claims ledger generation
- Scorecard generation
- EvidencePack bundling

Artifacts:
- claims.jsonl (E3)
- evidencepack.json (E3)
- scorecard.json (E3)
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from dive_engine.core.models import (
    BudgetPlan,
    CognitivePhase,
    EffortPlan,
    EvidenceLevel,
    MonitorReport,
    MonitorVerdict,
    ProcessTraceSummary,
    RouterDecision,
    RunSpec,
    ThinkingPhase,
    utcnow_iso,
)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class Claim:
    """A single claim in the claims ledger."""
    claim_id: str
    run_id: str
    claim_type: str  # routing, effort, verification, output, etc.
    statement: str
    evidence_level: EvidenceLevel
    artifact_refs: List[Dict[str, str]]  # [{path, sha256}]
    created_at: str = field(default_factory=utcnow_iso)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "run_id": self.run_id,
            "claim_type": self.claim_type,
            "statement": self.statement,
            "evidence_level": self.evidence_level.value,
            "artifact_refs": self.artifact_refs,
            "created_at": self.created_at,
        }
    
    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class Scorecard:
    """Run scorecard summarizing outcomes."""
    run_id: str
    status: str  # completed, failed, partial
    
    # Routing summary
    routing_path: str
    thinking_strategy: str
    effort_level: str
    
    # Phase completion
    phases_planned: int
    phases_completed: int
    phases_failed: int
    
    # Evidence summary
    artifacts_collected: int
    evidence_level_achieved: EvidenceLevel
    
    # Monitor summary
    monitor_verdict: str
    monitor_scores: Dict[str, float]
    
    # Budget usage
    budget_used: Dict[str, Any]
    
    # Timing
    started_at: str
    completed_at: str
    duration_ms: int
    
    # Claims
    claims_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "routing": {
                "path": self.routing_path,
                "thinking_strategy": self.thinking_strategy,
                "effort_level": self.effort_level,
            },
            "phases": {
                "planned": self.phases_planned,
                "completed": self.phases_completed,
                "failed": self.phases_failed,
            },
            "evidence": {
                "artifacts_collected": self.artifacts_collected,
                "level_achieved": self.evidence_level_achieved.value,
            },
            "monitor": {
                "verdict": self.monitor_verdict,
                "scores": self.monitor_scores,
            },
            "budget_used": self.budget_used,
            "timing": {
                "started_at": self.started_at,
                "completed_at": self.completed_at,
                "duration_ms": self.duration_ms,
            },
            "claims_count": self.claims_count,
        }


@dataclass
class EvidencePackV2:
    """Enhanced evidence pack for Dive Engine V2."""
    pack_id: str
    run_id: str
    created_at: str = field(default_factory=utcnow_iso)
    
    # Git info
    git_sha: Optional[str] = None
    git_branch: Optional[str] = None
    
    # CI info
    ci_run_id: Optional[str] = None
    ci_job_name: Optional[str] = None
    
    # Run summary
    run_spec: Optional[Dict[str, Any]] = None
    router_decision: Optional[Dict[str, Any]] = None
    effort_plan: Optional[Dict[str, Any]] = None
    
    # Artifacts
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Claims
    claims: List[Dict[str, Any]] = field(default_factory=list)
    
    # Scorecard
    scorecard: Optional[Dict[str, Any]] = None
    
    # Monitor report
    monitor_report: Optional[Dict[str, Any]] = None
    
    # Verification
    hash_index: Dict[str, str] = field(default_factory=dict)  # path -> sha256
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "git": {
                "sha": self.git_sha,
                "branch": self.git_branch,
            },
            "ci": {
                "run_id": self.ci_run_id,
                "job_name": self.ci_job_name,
            },
            "run_summary": {
                "run_spec": self.run_spec,
                "router_decision": self.router_decision,
                "effort_plan": self.effort_plan,
            },
            "artifacts": self.artifacts,
            "claims": self.claims,
            "scorecard": self.scorecard,
            "monitor_report": self.monitor_report,
            "hash_index": self.hash_index,
        }


# =============================================================================
# EVIDENCE PACKER
# =============================================================================

class EvidencePackerV2:
    """
    Evidence packer for Dive Engine V2.
    
    This class automatically collects and packages all artifacts
    from a run into an E3 evidence pack.
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize the evidence packer.
        
        Args:
            repo_root: Repository root path
        """
        self.repo_root = repo_root or Path.cwd()
    
    def pack(
        self,
        run_id: str,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        budget_plan: BudgetPlan,
        phases: Dict[CognitivePhase, ThinkingPhase],
        process_trace: ProcessTraceSummary,
        monitor_report: MonitorReport,
        artifacts: Dict[str, Path],
        output_dir: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """
        Pack all evidence for a run.
        
        This is the main entry point that:
        1. Generates claims ledger
        2. Generates scorecard
        3. Collects all artifacts
        4. Creates evidence pack
        
        Args:
            run_id: The run ID
            run_spec: The run specification
            router_decision: The routing decision
            effort_plan: The effort plan
            budget_plan: The budget plan
            phases: Executed thinking phases
            process_trace: The process trace summary
            monitor_report: The monitor report
            artifacts: Dict of artifact name -> path
            output_dir: Output directory (uses default if None)
            
        Returns:
            Dict mapping artifact names to paths
        """
        output_dir = output_dir or self._get_output_dir(run_id)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result_artifacts = {}
        
        # Step 1: Generate claims
        claims = self._generate_claims(
            run_id, run_spec, router_decision, effort_plan,
            phases, process_trace, monitor_report, artifacts
        )
        claims_path = self._emit_claims(claims, output_dir)
        result_artifacts["claims"] = claims_path
        
        # Step 2: Generate scorecard
        scorecard = self._generate_scorecard(
            run_id, run_spec, router_decision, effort_plan,
            budget_plan, phases, monitor_report, claims
        )
        scorecard_path = self._emit_scorecard(scorecard, output_dir)
        result_artifacts["scorecard"] = scorecard_path
        
        # Step 3: Collect all artifacts with hashes
        all_artifacts = self._collect_artifacts(artifacts, output_dir)
        
        # Step 4: Create evidence pack
        pack = self._create_evidence_pack(
            run_id, run_spec, router_decision, effort_plan,
            all_artifacts, claims, scorecard, monitor_report
        )
        pack_path = self._emit_evidence_pack(pack, output_dir)
        result_artifacts["evidencepack"] = pack_path
        
        return result_artifacts
    
    def _get_output_dir(self, run_id: str) -> Path:
        """Get default output directory for run."""
        return self.repo_root / ".vibe" / "runs" / run_id
    
    def _generate_claims(
        self,
        run_id: str,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        phases: Dict[CognitivePhase, ThinkingPhase],
        process_trace: ProcessTraceSummary,
        monitor_report: MonitorReport,
        artifacts: Dict[str, Path],
    ) -> List[Claim]:
        """Generate claims ledger from run data."""
        claims = []
        claim_counter = 0
        
        def make_claim_id() -> str:
            nonlocal claim_counter
            claim_counter += 1
            return f"{run_id}-claim-{claim_counter:03d}"
        
        # Routing claim
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="routing",
            statement=f"Task routed to {router_decision.path.value} path with {router_decision.thinking_strategy.value} strategy",
            evidence_level=EvidenceLevel.E2,
            artifact_refs=[self._artifact_ref(artifacts.get("router_decision"))],
        ))
        
        # Effort claim
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="effort",
            statement=f"Effort level set to {effort_plan.effort_level.value} with {effort_plan.budget_tokens} thinking tokens",
            evidence_level=EvidenceLevel.E2,
            artifact_refs=[self._artifact_ref(artifacts.get("effort_plan"))],
        ))
        
        # Phase completion claims
        completed_phases = [p for p, ps in phases.items() if ps.status == "completed"]
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="execution",
            statement=f"Completed {len(completed_phases)}/{len(phases)} cognitive phases",
            evidence_level=EvidenceLevel.E2,
            artifact_refs=[self._artifact_ref(artifacts.get("mode_run"))],
        ))
        
        # Monitor claim
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="monitoring",
            statement=f"Process monitoring verdict: {monitor_report.verdict.value}",
            evidence_level=EvidenceLevel.E2,
            artifact_refs=[self._artifact_ref(artifacts.get("monitor_report"))],
        ))
        
        # Process trace claim
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="traceability",
            statement=f"Process trace generated with {len(process_trace.key_decisions)} key decisions documented",
            evidence_level=EvidenceLevel.E1,
            artifact_refs=[self._artifact_ref(artifacts.get("process_trace"))],
        ))
        
        # Evidence collection claim
        claims.append(Claim(
            claim_id=make_claim_id(),
            run_id=run_id,
            claim_type="evidence",
            statement=f"Collected {len(artifacts)} artifacts with SHA256 verification",
            evidence_level=EvidenceLevel.E3,
            artifact_refs=[self._artifact_ref(p) for p in artifacts.values() if p],
        ))
        
        return claims
    
    def _generate_scorecard(
        self,
        run_id: str,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        budget_plan: BudgetPlan,
        phases: Dict[CognitivePhase, ThinkingPhase],
        monitor_report: MonitorReport,
        claims: List[Claim],
    ) -> Scorecard:
        """Generate run scorecard."""
        completed = [p for p, ps in phases.items() if ps.status == "completed"]
        failed = [p for p, ps in phases.items() if ps.status == "failed"]
        
        # Determine achieved evidence level
        if monitor_report.verdict == MonitorVerdict.PASS:
            achieved_level = EvidenceLevel.E3
        elif monitor_report.verdict == MonitorVerdict.WARN:
            achieved_level = EvidenceLevel.E2
        else:
            achieved_level = EvidenceLevel.E1
        
        return Scorecard(
            run_id=run_id,
            status="completed" if not failed else "partial",
            routing_path=router_decision.path.value,
            thinking_strategy=router_decision.thinking_strategy.value,
            effort_level=effort_plan.effort_level.value,
            phases_planned=len(phases),
            phases_completed=len(completed),
            phases_failed=len(failed),
            artifacts_collected=len(claims),
            evidence_level_achieved=achieved_level,
            monitor_verdict=monitor_report.verdict.value,
            monitor_scores={
                "completeness": monitor_report.completeness_score,
                "coherence": monitor_report.logical_coherence_score,
                "evidence": monitor_report.evidence_coverage_score,
                "risk": monitor_report.risk_assessment_score,
            },
            budget_used={
                "llm_calls": budget_plan.llm_calls_used,
                "tool_calls": budget_plan.tool_calls_used,
                "tokens": budget_plan.tokens_used,
                "thinking_tokens": budget_plan.thinking_tokens_used,
                "cost_usd": budget_plan.actual_cost_usd,
            },
            started_at=run_spec.created_at,
            completed_at=utcnow_iso(),
            duration_ms=budget_plan.elapsed_ms,
            claims_count=len(claims),
        )
    
    def _collect_artifacts(
        self,
        artifacts: Dict[str, Path],
        output_dir: Path,
    ) -> List[Dict[str, Any]]:
        """Collect all artifacts with metadata."""
        collected = []
        
        for name, path in artifacts.items():
            if path and path.exists():
                collected.append({
                    "name": name,
                    "path": str(path),
                    "sha256": self._sha256_file(path),
                    "size_bytes": path.stat().st_size,
                    "evidence_level": self._infer_evidence_level(name),
                })
        
        # Also collect any additional files in output_dir
        for file_path in output_dir.glob("*.json"):
            if file_path.name not in [Path(p).name for p in artifacts.values() if p]:
                collected.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "sha256": self._sha256_file(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "evidence_level": "E2",
                })
        
        for file_path in output_dir.glob("*.md"):
            if file_path.name not in [Path(p).name for p in artifacts.values() if p]:
                collected.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "sha256": self._sha256_file(file_path),
                    "size_bytes": file_path.stat().st_size,
                    "evidence_level": "E1",
                })
        
        return collected
    
    def _create_evidence_pack(
        self,
        run_id: str,
        run_spec: RunSpec,
        router_decision: RouterDecision,
        effort_plan: EffortPlan,
        artifacts: List[Dict[str, Any]],
        claims: List[Claim],
        scorecard: Scorecard,
        monitor_report: MonitorReport,
    ) -> EvidencePackV2:
        """Create the evidence pack."""
        pack_id = f"ep-{run_id}-{os.getpid()}"
        
        # Build hash index
        hash_index = {a["path"]: a["sha256"] for a in artifacts}
        
        return EvidencePackV2(
            pack_id=pack_id,
            run_id=run_id,
            git_sha=self._get_git_sha(),
            git_branch=self._get_git_branch(),
            ci_run_id=os.environ.get("CI_RUN_ID"),
            ci_job_name=os.environ.get("CI_JOB_NAME"),
            run_spec=run_spec.to_dict(),
            router_decision=router_decision.to_dict(),
            effort_plan=effort_plan.to_dict(),
            artifacts=artifacts,
            claims=[c.to_dict() for c in claims],
            scorecard=scorecard.to_dict(),
            monitor_report=monitor_report.to_dict(),
            hash_index=hash_index,
        )
    
    def _emit_claims(self, claims: List[Claim], output_dir: Path) -> Path:
        """Emit claims.jsonl artifact."""
        claims_path = output_dir / "claims.jsonl"
        with claims_path.open("w", encoding="utf-8") as f:
            for claim in claims:
                f.write(claim.to_jsonl() + "\n")
        return claims_path
    
    def _emit_scorecard(self, scorecard: Scorecard, output_dir: Path) -> Path:
        """Emit scorecard.json artifact."""
        scorecard_path = output_dir / "scorecard.json"
        scorecard_path.write_text(
            json.dumps(scorecard.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return scorecard_path
    
    def _emit_evidence_pack(self, pack: EvidencePackV2, output_dir: Path) -> Path:
        """Emit evidencepack.json artifact."""
        pack_path = output_dir / "evidencepack.json"
        pack_path.write_text(
            json.dumps(pack.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return pack_path
    
    def _artifact_ref(self, path: Optional[Path]) -> Dict[str, str]:
        """Create artifact reference with hash."""
        if not path or not path.exists():
            return {"path": "N/A", "sha256": "N/A"}
        return {
            "path": str(path),
            "sha256": self._sha256_file(path),
        }
    
    def _sha256_file(self, path: Path) -> str:
        """Calculate SHA256 hash of file."""
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    
    def _infer_evidence_level(self, name: str) -> str:
        """Infer evidence level from artifact name."""
        e3_artifacts = {"claims", "evidencepack", "scorecard", "sarif", "baseline"}
        e2_artifacts = {"router_decision", "effort_plan", "budget_plan", "monitor_report", "mode_run"}
        
        if any(e3 in name.lower() for e3 in e3_artifacts):
            return "E3"
        elif any(e2 in name.lower() for e2 in e2_artifacts):
            return "E2"
        else:
            return "E1"
    
    def _get_git_sha(self) -> Optional[str]:
        """Get current git SHA."""
        head = self.repo_root / ".git" / "HEAD"
        if not head.exists():
            return None
        
        ref = head.read_text(encoding="utf-8", errors="ignore").strip()
        if ref.startswith("ref:"):
            ref_path = ref.split(" ", 1)[-1].strip()
            p = self.repo_root / ".git" / ref_path
            if p.exists():
                return p.read_text(encoding="utf-8", errors="ignore").strip()[:40]
        return ref[:40] if ref else None
    
    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch."""
        head = self.repo_root / ".git" / "HEAD"
        if not head.exists():
            return None
        
        ref = head.read_text(encoding="utf-8", errors="ignore").strip()
        if ref.startswith("ref:"):
            ref_path = ref.split(" ", 1)[-1].strip()
            if ref_path.startswith("refs/heads/"):
                return ref_path.replace("refs/heads/", "")
        return None


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def pack_evidence(run_id: str, run_dir: Path) -> Path:
    """
    Convenience function to pack evidence from a completed run.
    
    This loads all artifacts from the run directory and creates
    an evidence pack.
    
    Args:
        run_id: The run ID
        run_dir: Directory containing run artifacts
        
    Returns:
        Path to the evidence pack
    """
    packer = EvidencePackerV2(run_dir.parent.parent.parent)  # repo_root
    
    # Load artifacts from run directory
    artifacts = {}
    for json_file in run_dir.glob("*.json"):
        artifacts[json_file.stem] = json_file
    for md_file in run_dir.glob("*.md"):
        artifacts[md_file.stem] = md_file
    
    # Create minimal pack (for standalone use)
    pack = EvidencePackV2(
        pack_id=f"ep-{run_id}-standalone",
        run_id=run_id,
        artifacts=[
            {
                "name": name,
                "path": str(path),
                "sha256": packer._sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
            for name, path in artifacts.items()
        ],
    )
    
    pack_path = run_dir / "evidencepack.json"
    pack_path.write_text(
        json.dumps(pack.to_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    return pack_path
