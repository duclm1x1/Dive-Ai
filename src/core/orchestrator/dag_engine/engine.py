from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from utils.policy import Policy
from utils.yaml_lite import load_yaml_file


@dataclass
class NodeResult:
    id: str
    ok: bool
    started_at: float
    ended_at: float
    stdout: str = ''
    stderr: str = ''
    exit_code: int = 0


@dataclass
class DAGResult:
    ok: bool
    nodes: List[NodeResult]


def _topo_sort(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id = {str(n.get('id')): n for n in nodes}
    deps = {nid: set(map(str, (by_id[nid].get('deps') or []))) for nid in by_id}
    out: List[Dict[str, Any]] = []
    ready = [nid for nid, ds in deps.items() if not ds]
    while ready:
        nid = ready.pop(0)
        out.append(by_id[nid])
        for other in list(deps.keys()):
            if nid in deps[other]:
                deps[other].remove(nid)
                if not deps[other]:
                    ready.append(other)
        deps.pop(nid, None)
    if deps:
        raise ValueError('DAG has cycles or missing nodes: ' + ','.join(sorted(deps.keys())))
    return out


def _run_shell(cmd: List[str], cwd: str, policy: Policy, timeout_s: int = 900) -> NodeResult:
    if not policy.check_command(cmd):
        now = time.time()
        return NodeResult(id='shell', ok=False, started_at=now, ended_at=now, stderr='command_not_allowed', exit_code=126)
    start = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s)
        end = time.time()
        return NodeResult(
            id='shell',
            ok=p.returncode == 0,
            started_at=start,
            ended_at=end,
            stdout=(p.stdout or '')[:20000],
            stderr=(p.stderr or '')[:20000],
            exit_code=int(p.returncode),
        )
    except Exception as e:
        end = time.time()
        return NodeResult(id='shell', ok=False, started_at=start, ended_at=end, stderr=str(e), exit_code=1)


def run_dag(spec_path: str, repo_root: str, policy: Policy) -> DAGResult:
    """Run a simple DAG spec.

    Spec supports YAML/JSON with top-level `nodes` list.
    Each node:
      - id: string
      - deps: [id]
      - type: 'shell'
      - cmd: ['npm','test']
      - cwd: optional relative cwd

    Output is deterministic and policy-gated.
    """
    sp = Path(spec_path)
    if not sp.exists():
        raise FileNotFoundError(spec_path)

    if sp.suffix.lower() == '.json':
        import json
        data = json.loads(sp.read_text(encoding='utf-8', errors='ignore'))
    else:
        data = load_yaml_file(str(sp))

    nodes = (data or {}).get('nodes') or []
    if not isinstance(nodes, list) or not nodes:
        return DAGResult(ok=False, nodes=[])

    ordered = _topo_sort(nodes)
    results: List[NodeResult] = []
    ok_all = True

    for node in ordered:
        nid = str(node.get('id'))
        ntype = str(node.get('type') or 'shell').lower()
        cwd = str(Path(repo_root) / str(node.get('cwd') or '.'))
        if ntype != 'shell':
            start = time.time()
            end = time.time()
            results.append(NodeResult(id=nid, ok=False, started_at=start, ended_at=end, stderr=f'unsupported_type:{ntype}', exit_code=2))
            ok_all = False
            continue
        cmd = node.get('cmd')
        if not isinstance(cmd, list) or not cmd:
            start = time.time(); end = time.time()
            results.append(NodeResult(id=nid, ok=False, started_at=start, ended_at=end, stderr='missing_cmd', exit_code=2))
            ok_all = False
            continue
        r = _run_shell([str(x) for x in cmd], cwd=cwd, policy=policy)
        r.id = nid
        results.append(r)
        if not r.ok:
            ok_all = False
            # stop-on-fail by default
            break

    return DAGResult(ok=ok_all, nodes=results)


def to_dict(res: DAGResult) -> Dict[str, Any]:
    return {'ok': res.ok, 'nodes': [asdict(n) for n in res.nodes]}
