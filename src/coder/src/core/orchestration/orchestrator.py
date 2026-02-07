"""
Legacy Orchestrator Shim
Redirects to canonical implementation in v20/coder/orchestrator/orchestrator.py
"""
import sys
import os
from pathlib import Path

# Calculate path to v20
current_file = Path(__file__)
v20_path = current_file.parents[6] / 'v20'
sys.path.insert(0, str(v20_path))

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
