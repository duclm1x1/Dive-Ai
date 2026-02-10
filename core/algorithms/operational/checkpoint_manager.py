"""
🔖 CHECKPOINT MANAGER
Manage checkpoints for state recovery

Based on V28's core_engine/checkpoint_manager.py
"""

import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class Checkpoint:
    """A state checkpoint"""
    id: str
    name: str
    state: Dict
    metadata: Dict = field(default_factory=dict)
    timestamp: float = 0.0


class CheckpointManagerAlgorithm(BaseAlgorithm):
    """
    🔖 Checkpoint Manager
    
    Manages state checkpoints:
    - State snapshots
    - Checkpoint storage
    - State restoration
    - Rollback capabilities
    
    From V28: core_engine/checkpoint_manager.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="CheckpointManager",
            name="Checkpoint Manager",
            level="operational",
            category="state",
            version="1.0",
            description="Manage checkpoints for state recovery",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "save/restore/list/delete"),
                    IOField("checkpoint_id", "string", False, "Checkpoint ID"),
                    IOField("state", "object", False, "State to save")
                ],
                outputs=[
                    IOField("result", "object", True, "Checkpoint operation result")
                ]
            ),
            steps=["Capture state", "Serialize", "Store checkpoint", "Index for retrieval"],
            tags=["checkpoint", "state", "recovery", "rollback"]
        )
        
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.checkpoint_dir = Path(".checkpoints")
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "list")
        
        print(f"\n🔖 Checkpoint Manager")
        
        if action == "save":
            return self._save_checkpoint(params.get("name", ""), params.get("state", {}))
        elif action == "restore":
            return self._restore_checkpoint(params.get("checkpoint_id", ""))
        elif action == "list":
            return self._list_checkpoints()
        elif action == "delete":
            return self._delete_checkpoint(params.get("checkpoint_id", ""))
        elif action == "rollback":
            return self._rollback(params.get("steps", 1))
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _save_checkpoint(self, name: str, state: Dict) -> AlgorithmResult:
        checkpoint = Checkpoint(
            id=f"cp_{len(self.checkpoints)}_{int(time.time())}",
            name=name or f"Checkpoint {len(self.checkpoints) + 1}",
            state=state,
            metadata={"created_at": time.strftime("%Y-%m-%d %H:%M:%S")},
            timestamp=time.time()
        )
        
        self.checkpoints[checkpoint.id] = checkpoint
        
        print(f"   Saved: {checkpoint.id} ({checkpoint.name})")
        
        return AlgorithmResult(
            status="success",
            data={
                "checkpoint_id": checkpoint.id,
                "name": checkpoint.name,
                "total_checkpoints": len(self.checkpoints)
            }
        )
    
    def _restore_checkpoint(self, checkpoint_id: str) -> AlgorithmResult:
        if not checkpoint_id:
            # Get latest
            if not self.checkpoints:
                return AlgorithmResult(status="error", error="No checkpoints available")
            checkpoint = max(self.checkpoints.values(), key=lambda c: c.timestamp)
        else:
            if checkpoint_id not in self.checkpoints:
                return AlgorithmResult(status="error", error="Checkpoint not found")
            checkpoint = self.checkpoints[checkpoint_id]
        
        print(f"   Restored: {checkpoint.id}")
        
        return AlgorithmResult(
            status="success",
            data={
                "checkpoint_id": checkpoint.id,
                "name": checkpoint.name,
                "state": checkpoint.state,
                "restored_from": checkpoint.metadata.get("created_at")
            }
        )
    
    def _list_checkpoints(self) -> AlgorithmResult:
        checkpoints = [
            {
                "id": cp.id,
                "name": cp.name,
                "created_at": cp.metadata.get("created_at"),
                "state_keys": list(cp.state.keys())
            }
            for cp in sorted(self.checkpoints.values(), key=lambda c: -c.timestamp)
        ]
        
        return AlgorithmResult(
            status="success",
            data={"checkpoints": checkpoints, "count": len(checkpoints)}
        )
    
    def _delete_checkpoint(self, checkpoint_id: str) -> AlgorithmResult:
        if checkpoint_id not in self.checkpoints:
            return AlgorithmResult(status="error", error="Checkpoint not found")
        
        del self.checkpoints[checkpoint_id]
        
        return AlgorithmResult(
            status="success",
            data={"deleted": checkpoint_id, "remaining": len(self.checkpoints)}
        )
    
    def _rollback(self, steps: int) -> AlgorithmResult:
        """Rollback N checkpoints"""
        sorted_checkpoints = sorted(self.checkpoints.values(), key=lambda c: -c.timestamp)
        
        if len(sorted_checkpoints) < steps + 1:
            return AlgorithmResult(status="error", error=f"Not enough checkpoints for {steps} rollback")
        
        target = sorted_checkpoints[steps]
        
        # Delete newer checkpoints
        for i in range(steps):
            del self.checkpoints[sorted_checkpoints[i].id]
        
        return AlgorithmResult(
            status="success",
            data={
                "rolled_back_to": target.id,
                "state": target.state,
                "deleted_count": steps
            }
        )


def register(algorithm_manager):
    algo = CheckpointManagerAlgorithm()
    algorithm_manager.register("CheckpointManager", algo)
    print("✅ CheckpointManager registered")


if __name__ == "__main__":
    algo = CheckpointManagerAlgorithm()
    algo.execute({"action": "save", "name": "Initial", "state": {"step": 1}})
    algo.execute({"action": "save", "name": "After Build", "state": {"step": 2}})
    result = algo.execute({"action": "list"})
    print(f"Checkpoints: {result.data['count']}")
