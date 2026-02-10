from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


REQUIRED_INPUTS: Dict[str, List[str]] = {
    'nextjs': [
        'project.name',
        'project.description',
        'product.users',
        'product.core_flows',
        'ui.style',
        'data.sources',
        'non_functional.slo',
        'non_functional.security',
    ],
    'nestjs': [
        'project.name',
        'project.description',
        'api.endpoints',
        'data.storage',
        'non_functional.security',
        'non_functional.observability',
    ],
    'tailwind': [
        'project.name',
        'project.description',
        'ui.style',
        'content.pages',
        'non_functional.seo',
    ],
    'website': [
        'project.name',
        'project.description',
        'content.pages',
        'ui.style',
        'non_functional.seo',
    ],
    'n8n': [
        'project.name',
        'workflow.trigger',
        'workflow.steps',
        'workflow.success_criteria',
        'workflow.error_handling',
        'secrets.placeholders',
    ],
}


def _get(spec: Dict[str, Any], path: str) -> Any:
    cur: Any = spec
    for part in path.split('.'):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def validate_spec(kind: str, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
    req = REQUIRED_INPUTS.get(kind, [])
    missing: List[str] = []
    for p in req:
        v = _get(spec, p)
        if v is None or v == '' or v == [] or v == {}:
            missing.append(p)
    return (len(missing) == 0), missing
