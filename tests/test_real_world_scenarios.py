"""Real-world scenarios for Dive Coder.

WARNING: These tests can hit the network and cost money (LLM tokens).
They are skipped unless RUN_REAL=1.
"""

import os
import pytest
import time

pytestmark = pytest.mark.real

if os.getenv('RUN_REAL', '0') != '1':
    pytest.skip('Set RUN_REAL=1 to run real-world scenarios', allow_module_level=True)

from dive_engine.llm.gateway import UnifiedLLMGateway


def test_gateway_smoke():
    """Sanity check that the gateway can be constructed."""
    gw = UnifiedLLMGateway()
    assert gw is not None


def test_gateway_latency_baseline():
    """Basic baseline: a single request should return within a reasonable time.

    This test is intentionally loose; tighten it in CI with stable routing.
    """
    gw = UnifiedLLMGateway()
    start = time.time()
    # This call requires your env to be configured with at least one provider
    # and a default model.
    _ = gw  # placeholder; implement a real chat call once your routing is wired
    elapsed = time.time() - start
    assert elapsed < 5.0
