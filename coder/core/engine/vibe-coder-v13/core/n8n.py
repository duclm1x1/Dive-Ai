from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.models import Evidence, Finding
from utils.hash_utils import sha256_text


def _ev(path: str, start: int = 1, end: int = 1, snippet: str = '') -> Evidence:
    return Evidence(file=path, start_line=int(start), end_line=int(end), snippet_hash=sha256_text(snippet or path)[:16])


def is_n8n_workflow(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if 'nodes' not in obj or 'connections' not in obj:
        return False
    return True


def _iter_nodes(obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes = obj.get('nodes')
    return nodes if isinstance(nodes, list) else []


def _node_types(nodes: List[Dict[str, Any]]) -> List[str]:
    out: List[str] = []
    for n in nodes:
        t = str(n.get('type') or '').strip()
        if t:
            out.append(t)
    return out


def _is_http_node(t: str) -> bool:
    tl = (t or '').lower()
    return 'httprequest' in tl or tl.endswith('.http') or 'http request' in tl


def _has_retry(node: Dict[str, Any]) -> bool:
    params = node.get('parameters') or {}
    if not isinstance(params, dict):
        return False
    opts = params.get('options')
    if isinstance(opts, dict):
        for k in ('retry', 'maxRetries', 'retries'):
            v = opts.get(k)
            if isinstance(v, int) and v > 0:
                return True
            if isinstance(v, dict) and any(int(v.get(x) or 0) > 0 for x in ('maxRetries', 'retries')):
                return True
    return False


def _has_timeout(node: Dict[str, Any]) -> bool:
    params = node.get('parameters') or {}
    if not isinstance(params, dict):
        return False
    opts = params.get('options')
    if isinstance(opts, dict):
        for k in ('timeout', 'requestTimeout'):
            v = opts.get(k)
            if isinstance(v, int) and v > 0:
                return True
    return False


def _contains_secret_literal(obj: Any) -> bool:
    secret_keys = {'token', 'password', 'apikey', 'api_key', 'secret', 'bearer', 'authorization'}
    def rec(x: Any) -> bool:
        if isinstance(x, dict):
            for k, v in x.items():
                kl = str(k).lower()
                if any(sk in kl for sk in secret_keys):
                    if isinstance(v, str):
                        vv = v.strip()
                        if vv and not vv.startswith('{{') and not vv.startswith('<') and not vv.startswith('$') and len(vv) >= 8:
                            return True
                if rec(v):
                    return True
        elif isinstance(x, list):
            for it in x:
                if rec(it):
                    return True
        return False
    return rec(obj)


def _credentials_exported(nodes: List[Dict[str, Any]]) -> bool:
    for n in nodes:
        creds = n.get('credentials')
        if isinstance(creds, dict):
            for _, v in creds.items():
                if isinstance(v, dict):
                    if 'id' in v or 'name' in v:
                        return True
    return False


def analyze_n8n_text(path: str, text: str) -> List[Finding]:
    try:
        obj = json.loads(text)
    except Exception:
        return []

    if not is_n8n_workflow(obj):
        return []

    findings: List[Finding] = []
    nodes = _iter_nodes(obj)
    types = _node_types(nodes)

    # Schema sanity
    if not isinstance(obj.get('connections'), dict) or not isinstance(obj.get('nodes'), list):
        findings.append(Finding(
            id='N8N.SCHEMA.INVALID',
            category='bug',
            severity='high',
            title='Invalid n8n workflow JSON schema',
            description='Workflow JSON is missing required keys or has unexpected types (nodes/connections).',
            recommendation='Ensure workflow export includes `nodes: []` and `connections: {}` and is valid JSON.',
            confidence=95,
            tool='vibe-n8n',
            evidence=_ev(path, snippet='schema'),
            tags=['n8n', 'schema'],
        ))
        return findings

    http_nodes = [n for n in nodes if _is_http_node(str(n.get('type') or ''))]
    has_webhook = any('webhook' in t.lower() for t in types)

    # Credentials / secrets
    if _credentials_exported(nodes):
        findings.append(Finding(
            id='N8N.CREDENTIALS.EXPORTED',
            category='security',
            severity='critical',
            title='n8n workflow export includes credential identifiers',
            description='Workflow JSON contains credential id/name. This risks leaking sensitive configuration.',
            recommendation='Strip credential id/name from the workflow before committing. Use placeholders and environment-managed credentials.',
            confidence=98,
            tool='vibe-n8n',
            evidence=_ev(path, snippet='credentials'),
            tags=['n8n', 'secrets'],
        ))

    if _contains_secret_literal(obj):
        findings.append(Finding(
            id='N8N.SECRETS.LITERAL',
            category='security',
            severity='critical',
            title='Potential secret literal found in n8n workflow JSON',
            description='Workflow appears to contain literal token/password/apiKey values.',
            recommendation='Replace secrets with placeholders (e.g., {{$env.SECRET}}) and keep secrets in credential store or env vars.',
            confidence=92,
            tool='vibe-n8n',
            evidence=_ev(path, snippet='secret'),
            tags=['n8n', 'secrets'],
        ))

    # Reliability best practices
    if http_nodes:
        if not any(_has_retry(n) for n in http_nodes):
            findings.append(Finding(
                id='N8N.RETRY.MISSING',
                category='reliability',
                severity='high',
                title='Missing retry configuration for HTTP calls',
                description='Workflow uses HTTP request nodes but does not appear to configure retries.',
                recommendation='Configure retry/backoff for transient failures (network/5xx). Prefer bounded retries + jitter.',
                confidence=88,
                tool='vibe-n8n',
                evidence=_ev(path, snippet='retry'),
                tags=['n8n', 'retry'],
            ))

        if not any(_has_timeout(n) for n in http_nodes):
            findings.append(Finding(
                id='N8N.TIMEOUT.MISSING',
                category='reliability',
                severity='medium',
                title='Missing timeout configuration for HTTP calls',
                description='Workflow uses HTTP request nodes without explicit request timeout.',
                recommendation='Set a request timeout to avoid stuck executions. Choose value based on SLO and upstream behavior.',
                confidence=80,
                tool='vibe-n8n',
                evidence=_ev(path, snippet='timeout'),
                tags=['n8n', 'timeout'],
            ))

        settings = obj.get('settings') or {}
        has_error_workflow = isinstance(settings, dict) and any(k in settings for k in ('errorWorkflow', 'errorWorkflowId'))
        has_error_node = any('errortrigger' in t.lower() for t in types)
        if not (has_error_workflow or has_error_node):
            findings.append(Finding(
                id='N8N.ERROR_HANDLING.MISSING',
                category='reliability',
                severity='high',
                title='Missing error handling branch / error workflow',
                description='Workflow makes external calls but does not define an error workflow or error trigger handling.',
                recommendation='Add an error branch: capture failures, notify, and optionally retry/compensate. Consider dedicated error workflow.',
                confidence=86,
                tool='vibe-n8n',
                evidence=_ev(path, snippet='error'),
                tags=['n8n', 'error-handling'],
            ))

        # Concurrency / rate-limit
        helper_nodes = ('splitinbatches', 'wait', 'interval', 'rate', 'queue', 'throttle')
        has_concurrency_control = any(any(h in t.lower() for h in helper_nodes) for t in types)
        if len(http_nodes) >= 5 and not has_concurrency_control:
            findings.append(Finding(
                id='N8N.CONCURRENCY.MISSING',
                category='reliability',
                severity='medium',
                title='Missing concurrency / rate-limit control for multiple HTTP calls',
                description='Workflow performs many external calls but lacks obvious batching/rate limiting.',
                recommendation='Add batching (SplitInBatches), throttle, or queueing to control concurrency and respect upstream rate limits.',
                confidence=78,
                tool='vibe-n8n',
                evidence=_ev(path, snippet='concurrency'),
                tags=['n8n', 'concurrency'],
            ))

    if has_webhook:
        # Heuristic idempotency: look for keywords
        has_idem = False
        for n in nodes:
            name = str(n.get('name') or '').lower()
            params = n.get('parameters')
            if 'idempot' in name or 'dedup' in name:
                has_idem = True
                break
            if isinstance(params, dict):
                blob = json.dumps(params).lower()
                if 'idempot' in blob or 'dedup' in blob:
                    has_idem = True
                    break
        if not has_idem and http_nodes:
            findings.append(Finding(
                id='N8N.IDEMPOTENCY.MISSING',
                category='reliability',
                severity='medium',
                title='Potential missing idempotency for webhook-triggered workflow',
                description='Webhook-triggered workflows may run more than once; without idempotency this can duplicate side-effects.',
                recommendation='Add idempotency key tracking (store last processed event id) before side-effecting calls.',
                confidence=76,
                tool='vibe-n8n',
                evidence=_ev(path, snippet='idempotency'),
                tags=['n8n', 'idempotency'],
            ))

    return findings
