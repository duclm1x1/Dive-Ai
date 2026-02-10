from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from core.models import GateResult
from utils.policy import Policy


def run_semgrep_sarif_gate(repo_root: str, policy: Policy, config: str = 'auto', out_path: Optional[str] = None) -> GateResult:
    """Run semgrep and emit SARIF artifact.

    - If semgrep is missing, returns allowed=False (exit_code None).
    - Obeys Policy (command allowlist).
    """

    if shutil.which('semgrep') is None:
        return GateResult(name='semgrep-sarif', command='semgrep', allowed=False, exit_code=None, artifacts=None)

    out_path = out_path or str(Path(repo_root) / '.vibe' / 'reports' / 'semgrep.sarif.json')
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = ['semgrep', '--config', config, '--sarif', '--output', out_path]
    if not policy.check_command(cmd):
        return GateResult(name='semgrep-sarif', command=' '.join(cmd), allowed=False, exit_code=None, artifacts=None)

    try:
        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, timeout=1800)
        artifacts = {'sarif': out_path} if Path(out_path).exists() else None
        return GateResult(
            name='semgrep-sarif',
            command=' '.join(cmd),
            allowed=True,
            exit_code=int(proc.returncode),
            stdout=proc.stdout or '',
            stderr=proc.stderr or '',
            duration_ms=None,
            artifacts=artifacts,
        )
    except subprocess.TimeoutExpired:
        return GateResult(
            name='semgrep-sarif',
            command=' '.join(cmd),
            allowed=True,
            exit_code=124,
            stdout='',
            stderr='semgrep gate timed out',
            duration_ms=None,
            artifacts=None,
        )
    except Exception as e:
        return GateResult(
            name='semgrep-sarif',
            command=' '.join(cmd),
            allowed=True,
            exit_code=1,
            stdout='',
            stderr=str(e),
            duration_ms=None,
            artifacts=None,
        )
