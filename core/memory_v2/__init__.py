"""
Dive AI V29 - Unified Memory Package

Memory V5: Consolidated from 11 memory files
- Project Layer (3-file system)
- Brain Layer (check before actions)
- Cache Layer (fast local with indexing)
- Cloud Layer (Supabase sync)
- SQLite (algorithms, executions, theses)
"""

# V5 - Unified Memory (recommended)
from .memory_v5 import (
    MemoryV5,
    get_memory_v5,
    GPAScore,
    ProcessKPIs,
    AlgorithmRecord,
    ExecutionRecord,
    ThesisRecord,
    MemoryEntry,
    MemoryType
)

# V2 - Legacy (for backward compatibility)
try:
    from .memory_v2 import MemoryV2, get_memory_v2
except ImportError:
    MemoryV2 = MemoryV5
    get_memory_v2 = get_memory_v5

__all__ = [
    # V5 - Primary
    'MemoryV5',
    'get_memory_v5',
    # Data classes
    'GPAScore',
    'ProcessKPIs',
    'AlgorithmRecord',
    'ExecutionRecord',
    'ThesisRecord',
    'MemoryEntry',
    'MemoryType',
    # Legacy
    'MemoryV2',
    'get_memory_v2',
]
