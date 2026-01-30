"""Integration tests for Unified LLM Gateway.

Notes
-----
- Some tests can hit the network and cost money. Those are marked with
  @pytest.mark.real and are skipped unless RUN_REAL=1 and at least one API key is set.

Run locally:
  pip install -r requirements-dev.txt
  pytest -q

Run real (requires keys):
  RUN_REAL=1 OPENAI_API_KEY=... pytest -q -m real
"""

import os
import json
import sys
import time
import pytest

# Add parent directory to path (V13 style)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.shared/vibe-coder-v13'))

from dive_engine.llm.performance_tracker import (
    PerformanceTracker,
    ProviderName,
    get_performance_tracker,
)
from dive_engine.llm.account_pool import (
    AccountPoolManager,
    AccountNode,
    ProviderType,
)
from dive_engine.llm.gateway import UnifiedLLMGateway


def _skip_if_no_creds():
    """Skip tests that can hit network / cost money unless explicitly enabled."""
    if os.getenv('RUN_REAL', '0') != '1':
        pytest.skip('Set RUN_REAL=1 and provide API keys to run real LLM gateway tests')
    if not any(os.getenv(k) for k in ['OPENAI_API_KEY','ANTHROPIC_API_KEY','AICODING_API_KEY','V98API_API_KEY']):
        pytest.skip('No API keys found in env; set at least one provider key')


def test_performance_tracker():
    tracker = PerformanceTracker()

    tracker.record_request(ProviderName.V98API, success=True, latency_ms=250.5, cost=0.002)
    tracker.record_request(ProviderName.V98API, success=True, latency_ms=300.2, cost=0.003)
    tracker.record_request(ProviderName.AICODING, success=True, latency_ms=180.0, cost=0.001)
    tracker.record_request(ProviderName.AICODING, success=False, latency_ms=0, cost=0)

    stats = tracker.get_stats_summary()
    assert 'best_provider' in stats
    assert 'provider_rankings' in stats


def test_account_pool_scoring(tmp_path):
    # Use an empty on-disk config so the manager doesn't auto-load real accounts
    cfg = tmp_path / "accounts.yaml"
    cfg.write_text(json.dumps({"providers": {"V98API": {"accounts": []}}}))

    pool = AccountPoolManager(config_path=cfg)

    fresh = AccountNode(account_id='fresh', provider=ProviderType.V98API, api_key='k1')
    stale = AccountNode(account_id='stale', provider=ProviderType.V98API, api_key='k2')

    # Simulate a less desirable account by applying a cooldown
    stale.last_error_ts = time.time()

    pool.add_account(fresh)
    pool.add_account(stale)

    selected = pool.select_account(ProviderType.V98API)
    assert selected is not None
    assert selected.account_id == 'fresh'




@pytest.mark.real
async def test_gateway_real_request():
    _skip_if_no_creds()

    gateway = UnifiedLLMGateway()
    response = await gateway.chat_completion(
        messages=[{'role': 'user', 'content': "Say 'Hello from Dive Engine!' and nothing else."}],
        model='gpt-4.1-mini',
        max_tokens=50,
    )
    content = response.choices[0].message.content
    assert 'Hello' in content


@pytest.mark.real
async def test_gateway_streaming():
    _skip_if_no_creds()

    gateway = UnifiedLLMGateway()
    got_any = False
    async for chunk in gateway.chat_completion_stream(
        messages=[{'role': 'user', 'content': 'Count from 1 to 3, one number per line.'}],
        model='gpt-4.1-mini',
        max_tokens=50,
    ):
        delta = chunk['choices'][0]['delta']
        if delta.get('content'):
            got_any = True
    assert got_any


@pytest.mark.real
async def test_failover_mark_unhealthy():
    _skip_if_no_creds()

    tracker = get_performance_tracker()
    tracker.mark_unhealthy(ProviderName.V98API)
    best = tracker.get_best_provider()
    assert best != ProviderName.V98API

    tracker.mark_healthy(ProviderName.V98API)
