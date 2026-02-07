from __future__ import annotations

import subprocess
from dataclasses import dataclass
from time import perf_counter
from typing import List, Optional

from core.models import GateResult
from utils.policy import Policy


def run_gate(name: str, cmd: List[str], cwd: str, policy: Policy, timeout_s: int = 900) -> GateResult:
    allowed = policy.check_command(cmd)
    if not allowed:
        return GateResult(name=name, command=' '.join(cmd), allowed=False, evidence_level='E0')

    t0 = perf_counter()
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)
        t1 = perf_counter()
        return GateResult(
            name=name,
            command=' '.join(cmd),
            allowed=True,
            evidence_level='E2',
            exit_code=int(proc.returncode),
            stdout=proc.stdout or '',
            stderr=proc.stderr or '',
            duration_ms=int((t1 - t0) * 1000),
        )
    except subprocess.TimeoutExpired as e:
        t1 = perf_counter()
        return GateResult(
            name=name,
            command=' '.join(cmd),
            allowed=True,
            evidence_level='E2',
            exit_code=124,
            stdout=(e.stdout or '') if isinstance(e.stdout, str) else '',
            stderr=(e.stderr or '') if isinstance(e.stderr, str) else 'Gate timed out',
            duration_ms=int((t1 - t0) * 1000),
        )
    except Exception as e:
        t1 = perf_counter()
        return GateResult(
            name=name,
            command=' '.join(cmd),
            allowed=True,
            evidence_level='E2',
            exit_code=1,
            stdout='',
            stderr=str(e),
            duration_ms=int((t1 - t0) * 1000),
        )
