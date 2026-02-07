#!/usr/bin/env python3
"""
Dive Reasoning Trace - V22 Thinking Engine Component

Records complete reasoning trace for transparency and debugging.
Part of the Thinking Engine transformation (Week 3).
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class TraceEventType(Enum):
    """Types of trace events"""
    TASK_START = "task_start"
    TASK_END = "task_end"
    STEP_START = "step_start"
    STEP_END = "step_end"
    DECISION = "decision"
    OBSERVATION = "observation"
    ACTION = "action"
    ERROR = "error"
    MILESTONE = "milestone"


@dataclass
class TraceEvent:
    """A single event in the reasoning trace"""
    event_id: int
    event_type: TraceEventType
    timestamp: datetime
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'data': self.data,
            'parent_id': self.parent_id
        }


@dataclass
class ReasoningPath:
    """A path through the reasoning process"""
    path_id: int
    description: str
    events: List[TraceEvent] = field(default_factory=list)
    success: bool = False
    error: Optional[str] = None


class DiveReasoningTrace:
    """
    Records complete reasoning trace for a task.
    
    This provides full transparency into how Dive AI thinks,
    enabling debugging, explanation, and continuous improvement.
    """
    
    def __init__(self, task: str, task_id: Optional[str] = None):
        self.task = task
        self.task_id = task_id or f"task_{datetime.now().timestamp()}"
        self.events: List[TraceEvent] = []
        self.paths: List[ReasoningPath] = []
        self.current_path: Optional[ReasoningPath] = None
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
        
    def start_task(self, metadata: Optional[Dict] = None):
        """Record task start"""
        self.metadata.update(metadata or {})
        self.add_event(
            TraceEventType.TASK_START,
            f"Starting task: {self.task}",
            {'metadata': self.metadata}
        )
    
    def end_task(self, success: bool = True, result: Optional[Any] = None):
        """Record task end"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.add_event(
            TraceEventType.TASK_END,
            f"Task {'completed' if success else 'failed'} in {duration:.2f}s",
            {
                'success': success,
                'result': str(result) if result else None,
                'duration': duration
            }
        )
    
    def start_step(self, description: str, step_data: Optional[Dict] = None) -> int:
        """Record step start and return event ID"""
        return self.add_event(
            TraceEventType.STEP_START,
            description,
            step_data or {}
        )
    
    def end_step(self, step_id: int, result: Optional[Any] = None):
        """Record step end"""
        self.add_event(
            TraceEventType.STEP_END,
            f"Step {step_id} completed",
            {'result': str(result) if result else None},
            parent_id=step_id
        )
    
    def record_decision(
        self,
        description: str,
        options: List[str],
        chosen: str,
        reasoning: str
    ):
        """Record a decision point"""
        self.add_event(
            TraceEventType.DECISION,
            description,
            {
                'options': options,
                'chosen': chosen,
                'reasoning': reasoning
            }
        )
    
    def record_observation(self, description: str, data: Optional[Dict] = None):
        """Record an observation"""
        self.add_event(
            TraceEventType.OBSERVATION,
            description,
            data or {}
        )
    
    def record_action(self, description: str, action_data: Optional[Dict] = None):
        """Record an action"""
        self.add_event(
            TraceEventType.ACTION,
            description,
            action_data or {}
        )
    
    def record_error(self, description: str, error: Exception):
        """Record an error"""
        self.add_event(
            TraceEventType.ERROR,
            description,
            {
                'error_type': type(error).__name__,
                'error_message': str(error)
            }
        )
    
    def record_milestone(self, description: str, data: Optional[Dict] = None):
        """Record a milestone"""
        self.add_event(
            TraceEventType.MILESTONE,
            description,
            data or {}
        )
    
    def add_event(
        self,
        event_type: TraceEventType,
        description: str,
        data: Optional[Dict] = None,
        parent_id: Optional[int] = None
    ) -> int:
        """Add an event to the trace"""
        event = TraceEvent(
            event_id=len(self.events) + 1,
            event_type=event_type,
            timestamp=datetime.now(),
            description=description,
            data=data or {},
            parent_id=parent_id
        )
        
        self.events.append(event)
        
        # Add to current path if exists
        if self.current_path:
            self.current_path.events.append(event)
        
        return event.event_id
    
    def start_path(self, description: str) -> int:
        """Start a new reasoning path"""
        path = ReasoningPath(
            path_id=len(self.paths) + 1,
            description=description
        )
        self.paths.append(path)
        self.current_path = path
        return path.path_id
    
    def end_path(self, success: bool = True, error: Optional[str] = None):
        """End current reasoning path"""
        if self.current_path:
            self.current_path.success = success
            self.current_path.error = error
            self.current_path = None
    
    def get_events_by_type(self, event_type: TraceEventType) -> List[TraceEvent]:
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
    
    def get_decisions(self) -> List[TraceEvent]:
        """Get all decision events"""
        return self.get_events_by_type(TraceEventType.DECISION)
    
    def get_errors(self) -> List[TraceEvent]:
        """Get all error events"""
        return self.get_events_by_type(TraceEventType.ERROR)
    
    def get_milestones(self) -> List[TraceEvent]:
        """Get all milestone events"""
        return self.get_events_by_type(TraceEventType.MILESTONE)
    
    def to_dict(self) -> Dict:
        """Convert trace to dictionary"""
        return {
            'task': self.task,
            'task_id': self.task_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'metadata': self.metadata,
            'events': [e.to_dict() for e in self.events],
            'paths': [
                {
                    'path_id': p.path_id,
                    'description': p.description,
                    'success': p.success,
                    'error': p.error,
                    'event_count': len(p.events)
                }
                for p in self.paths
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert trace to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: str):
        """Save trace to file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load(cls, filepath: str) -> 'DiveReasoningTrace':
        """Load trace from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        trace = cls(data['task'], data['task_id'])
        trace.start_time = datetime.fromisoformat(data['start_time'])
        if data['end_time']:
            trace.end_time = datetime.fromisoformat(data['end_time'])
        trace.metadata = data['metadata']
        
        # Reconstruct events
        for event_data in data['events']:
            event = TraceEvent(
                event_id=event_data['event_id'],
                event_type=TraceEventType(event_data['event_type']),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                description=event_data['description'],
                data=event_data['data'],
                parent_id=event_data['parent_id']
            )
            trace.events.append(event)
        
        return trace
    
    def print_summary(self):
        """Print a human-readable summary"""
        print(f"=== Reasoning Trace: {self.task} ===")
        print(f"Task ID: {self.task_id}")
        print(f"Start: {self.start_time}")
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            print(f"End: {self.end_time} (duration: {duration:.2f}s)")
        print(f"Total events: {len(self.events)}")
        print(f"Paths: {len(self.paths)}")
        
        # Print decisions
        decisions = self.get_decisions()
        if decisions:
            print(f"\nDecisions ({len(decisions)}):")
            for d in decisions:
                print(f"  - {d.description}")
                print(f"    Chosen: {d.data.get('chosen')}")
        
        # Print milestones
        milestones = self.get_milestones()
        if milestones:
            print(f"\nMilestones ({len(milestones)}):")
            for m in milestones:
                print(f"  - {m.description}")
        
        # Print errors
        errors = self.get_errors()
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for e in errors:
                print(f"  - {e.description}: {e.data.get('error_message')}")


def main():
    """Test reasoning trace"""
    print("=== Dive Reasoning Trace Test ===\n")
    
    # Create trace
    trace = DiveReasoningTrace("Design and implement REST API")
    
    # Start task
    trace.start_task({'complexity': 'high', 'estimated_time': 60})
    
    # Record some steps
    step1 = trace.start_step("Analyze requirements")
    trace.record_observation("Requirements are clear", {'requirement_count': 5})
    trace.end_step(step1, "Requirements analyzed")
    
    # Record a decision
    trace.record_decision(
        "Choose framework",
        options=["Flask", "FastAPI", "Django"],
        chosen="FastAPI",
        reasoning="Best for async operations and automatic API docs"
    )
    
    # Record a milestone
    trace.record_milestone("Design complete", {'design_time': 15})
    
    # Start a path
    path1 = trace.start_path("Implementation path")
    trace.record_action("Create project structure")
    trace.record_action("Implement endpoints")
    trace.end_path(success=True)
    
    # End task
    trace.end_task(success=True, result="REST API implemented successfully")
    
    # Print summary
    trace.print_summary()
    
    # Test serialization
    print("\n=== Testing Serialization ===")
    json_str = trace.to_json()
    print(f"JSON length: {len(json_str)} characters")
    
    # Test save/load
    print("\n=== Testing Save/Load ===")
    trace.save("/tmp/test_trace.json")
    loaded_trace = DiveReasoningTrace.load("/tmp/test_trace.json")
    print(f"Loaded trace: {loaded_trace.task}")
    print(f"Events: {len(loaded_trace.events)}")


if __name__ == "__main__":
    main()
