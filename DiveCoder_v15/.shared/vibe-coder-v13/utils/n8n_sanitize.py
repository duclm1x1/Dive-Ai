from __future__ import annotations

import json
from typing import Any, Dict, Tuple

from core.n8n import is_n8n_workflow


SECRET_KEYS = ('token', 'password', 'apikey', 'api_key', 'secret', 'authorization', 'bearer')


def _is_secret_key(key: str) -> bool:
    kl = (key or '').lower()
    return any(sk in kl for sk in SECRET_KEYS)


def _is_placeholder(val: str) -> bool:
    v = (val or '').strip()
    return v.startswith('{{') or v.startswith('<') or v.startswith('$') or v.startswith('{{$env.')


def sanitize_n8n_text(text: str) -> Tuple[str, bool, Dict[str, Any]]:
    """Strip credential names/ids and replace likely secret literals with placeholders."""
    try:
        obj = json.loads(text)
    except Exception:
        return text, False, {'reason': 'not_json'}

    if not is_n8n_workflow(obj):
        return text, False, {'reason': 'not_n8n'}

    changed = False
    notes: Dict[str, Any] = {'credentials_stripped': 0, 'secrets_replaced': 0}

    nodes = obj.get('nodes') if isinstance(obj, dict) else None
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            creds = node.get('credentials')
            if isinstance(creds, dict):
                for k, v in list(creds.items()):
                    if isinstance(v, dict):
                        if 'id' in v:
                            v.pop('id', None)
                            notes['credentials_stripped'] += 1
                            changed = True
                        if 'name' in v:
                            v.pop('name', None)
                            notes['credentials_stripped'] += 1
                            changed = True

            params = node.get('parameters')
            if isinstance(params, dict):
                for pk, pv in list(params.items()):
                    if isinstance(pv, str) and _is_secret_key(pk) and not _is_placeholder(pv) and len(pv.strip()) >= 8:
                        placeholder = f"{{$env.{pk.upper()}}}"
                        params[pk] = placeholder
                        notes['secrets_replaced'] += 1
                        changed = True

    if changed:
        return json.dumps(obj, indent=2, ensure_ascii=False), True, notes
    return text, False, notes
