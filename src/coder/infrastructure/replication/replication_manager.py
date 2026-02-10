"""
Legacy Replication Manager Shim
Redirects to canonical implementation in v20/coder/replication/replication_manager.py
"""
import sys
import os
from pathlib import Path

# Calculate path to v20
current_file = Path(__file__)
v20_path = current_file.parents[6] / 'v20'
sys.path.insert(0, str(v20_path))

# Import from canonical location
from v20.coder.replication.replication_manager import (
    ReplicationManager,
    ReplicationConfig,
    ReplicationState,
    ReplicationTask,
    ReplicationStrategy,
    DirectReplicationStrategy,
    IncrementalReplicationStrategy,
    create_replication_manager,
    get_default_replication_manager
)

__all__ = [
    'ReplicationManager',
    'ReplicationConfig',
    'ReplicationState',
    'ReplicationTask',
    'ReplicationStrategy',
    'DirectReplicationStrategy',
    'IncrementalReplicationStrategy',
    'create_replication_manager',
    'get_default_replication_manager'
]
