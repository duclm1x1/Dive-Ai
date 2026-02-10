"""
🔄 STATE MACHINE
Finite state machine implementation

Based on V28's core_engine/state_machine.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class StateTransition:
    """A state transition"""
    from_state: str
    to_state: str
    event: str
    condition: Optional[str] = None


@dataclass
class State:
    """A state definition"""
    name: str
    is_initial: bool = False
    is_final: bool = False
    on_enter: Optional[str] = None
    on_exit: Optional[str] = None


class StateMachineAlgorithm(BaseAlgorithm):
    """
    🔄 State Machine
    
    Finite state machine:
    - State definitions
    - Transition management  
    - Event-driven transitions
    - State history
    
    From V28: core_engine/state_machine.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="StateMachine",
            name="State Machine",
            level="operational",
            category="control",
            version="1.0",
            description="Finite state machine implementation",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "define/transition/status"),
                    IOField("states", "array", False, "State definitions"),
                    IOField("event", "string", False, "Trigger event")
                ],
                outputs=[
                    IOField("result", "object", True, "State machine result")
                ]
            ),
            steps=["Define states", "Set transitions", "Handle events", "Update state"],
            tags=["state-machine", "fsm", "control"]
        )
        
        self.states: Dict[str, State] = {}
        self.transitions: List[StateTransition] = []
        self.current_state: Optional[str] = None
        self.history: List[Dict] = []
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "status")
        
        print(f"\n🔄 State Machine")
        
        if action == "define":
            return self._define(params.get("states", []), params.get("transitions", []))
        elif action == "transition":
            return self._transition(params.get("event", ""))
        elif action == "status":
            return self._get_status()
        elif action == "reset":
            return self._reset()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _define(self, states_data: List[Dict], transitions_data: List[Dict]) -> AlgorithmResult:
        # Define states
        for state_data in states_data:
            state = State(
                name=state_data.get("name", ""),
                is_initial=state_data.get("initial", False),
                is_final=state_data.get("final", False),
                on_enter=state_data.get("on_enter"),
                on_exit=state_data.get("on_exit")
            )
            self.states[state.name] = state
            
            if state.is_initial and self.current_state is None:
                self.current_state = state.name
        
        # Define transitions
        for trans_data in transitions_data:
            trans = StateTransition(
                from_state=trans_data.get("from", ""),
                to_state=trans_data.get("to", ""),
                event=trans_data.get("event", ""),
                condition=trans_data.get("condition")
            )
            self.transitions.append(trans)
        
        print(f"   Defined: {len(self.states)} states, {len(self.transitions)} transitions")
        
        return AlgorithmResult(
            status="success",
            data={
                "states": len(self.states),
                "transitions": len(self.transitions),
                "current": self.current_state
            }
        )
    
    def _transition(self, event: str) -> AlgorithmResult:
        if not self.current_state:
            return AlgorithmResult(status="error", error="No current state")
        
        # Find matching transition
        for trans in self.transitions:
            if trans.from_state == self.current_state and trans.event == event:
                old_state = self.current_state
                self.current_state = trans.to_state
                
                self.history.append({
                    "from": old_state,
                    "to": trans.to_state,
                    "event": event,
                    "timestamp": time.time()
                })
                
                print(f"   Transition: {old_state} -> {trans.to_state}")
                
                return AlgorithmResult(
                    status="success",
                    data={
                        "from": old_state,
                        "to": trans.to_state,
                        "event": event
                    }
                )
        
        return AlgorithmResult(
            status="error",
            error=f"No transition for event '{event}' from state '{self.current_state}'"
        )
    
    def _get_status(self) -> AlgorithmResult:
        current = self.states.get(self.current_state)
        
        return AlgorithmResult(
            status="success",
            data={
                "current_state": self.current_state,
                "is_final": current.is_final if current else False,
                "available_transitions": [
                    {"event": t.event, "to": t.to_state}
                    for t in self.transitions if t.from_state == self.current_state
                ],
                "history_length": len(self.history)
            }
        )
    
    def _reset(self) -> AlgorithmResult:
        # Find initial state
        for state in self.states.values():
            if state.is_initial:
                self.current_state = state.name
                break
        
        self.history.clear()
        
        return AlgorithmResult(
            status="success",
            data={"reset_to": self.current_state}
        )


def register(algorithm_manager):
    algo = StateMachineAlgorithm()
    algorithm_manager.register("StateMachine", algo)
    print("✅ StateMachine registered")


if __name__ == "__main__":
    algo = StateMachineAlgorithm()
    algo.execute({
        "action": "define",
        "states": [
            {"name": "idle", "initial": True},
            {"name": "running"},
            {"name": "completed", "final": True}
        ],
        "transitions": [
            {"from": "idle", "to": "running", "event": "start"},
            {"from": "running", "to": "completed", "event": "finish"}
        ]
    })
    algo.execute({"action": "transition", "event": "start"})
    result = algo.execute({"action": "status"})
    print(f"Current: {result.data['current_state']}")
