"""
Legacy Orchestrator Shim Module
Provides backward compatibility by redirecting to canonical implementation
"""

import sys
import os

# Add v20 to path for canonical imports
v20_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'v20')
if v20_path not in sys.path:
    sys.path.insert(0, v20_path)

# Import from canonical location
from v20.coder.orchestrator.orchestrator import (
    Orchestrator,
    OrchestratorConfig,
    OrchestratorState,
    TaskResult,
    create_orchestrator,
    get_default_orchestrator
)

__all__ = [
    'Orchestrator',
    'OrchestratorConfig',
    'OrchestratorState',
    'TaskResult',
    'create_orchestrator',
    'get_default_orchestrator'
]
