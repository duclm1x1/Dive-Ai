from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class GateSpec:
    name: str
    cmd: List[str]


class StackPlugin(Protocol):
    """Stack plugin interface (enterprise v11.1).

    We pass repo_root into suggested_gates so plugins can inspect package manager + scripts safely.
    """

    name: str

    def detect(self, repo_root: str) -> bool: ...

    def suggested_gates(self, repo_root: str) -> List[GateSpec]: ...
