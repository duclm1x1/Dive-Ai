#!/usr/bin/env python3
"""
Dive Smart Orchestrator - Intelligent Prompt Processing System

Inspired by:
- Manus AI: Explicit agent loop (Analyze → Plan → Execute → Observe)
- Claude Opus 4.5: Intent detection, ambiguity handling, creative problem solving
- Codex: Think first, batch everything, bias to action

Architecture:
1. ANALYZE - Intent detection, complexity assessment, memory context
2. THINK FIRST - Identify all resources, plan parallel operations
3. PLAN - Task decomposition (if complex)
4. ROUTE - Multi-model selection
5. EXECUTE - Batch operations, parallel execution
6. OBSERVE - Update plan, store in memory
7. REPEAT/FINISH - Continue or complete

Author: Dive AI Team
Version: V21.1 - Smart Processing
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Import Dive Memory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dive_memory_3file_complete import DiveMemory3FileComplete
from dive_interrupt_handler import InterruptHandler, Interrupt


class TaskType(Enum):
    """Task classification types"""
    SIMPLE = "simple"  # Single-step, straightforward
    MODERATE = "moderate"  # Multi-step, clear path
    COMPLEX = "complex"  # Multi-step, requires planning
    CREATIVE = "creative"  # Requires creative problem solving
    RESEARCH = "research"  # Information gathering
    CODING = "coding"  # Code generation/modification
    ANALYSIS = "analysis"  # Data analysis
    DEPLOYMENT = "deployment"  # System deployment


class ModelType(Enum):
    """Available models for routing"""
    CLAUDE_OPUS = "claude-opus-4-5"
    CLAUDE_SONNET = "claude-sonnet-4-5-20250929"
    GPT_CODEX = "gpt-5-2-codex"
    GEMINI = "gemini-3-pro-preview"


@dataclass
class Intent:
    """User intent detection result"""
    type: TaskType
    goals: List[str]
    entities: List[str]
    ambiguities: List[str]
    tradeoffs: List[Dict[str, Any]]
    confidence: float
    raw_prompt: str


@dataclass
class Step:
    """Single step in a plan"""
    id: int
    description: str
    dependencies: List[int] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, done, failed
    model: Optional[ModelType] = None
    result: Optional[Any] = None
    parallel_group: int = 0


@dataclass
class Plan:
    """Task execution plan"""
    steps: List[Step]
    parallel_groups: List[List[Step]]
    status: str = "in_progress"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Event:
    """Event in the event stream"""
    type: str  # user_message, plan, action, observation, result
    data: Any
    timestamp: datetime = field(default_factory=datetime.now)


class IntentDetector:
    """Detects user intent from prompt"""
    
    def __init__(self, memory: DiveMemory3FileComplete):
        self.memory = memory
    
    def detect(self, prompt: str, context: Dict[str, Any]) -> Intent:
        """Detect intent from prompt"""
        
        # Classify task type
        task_type = self._classify_task(prompt)
        
        # Extract goals
        goals = self._extract_goals(prompt)
        
        # Extract entities (files, projects, tools, etc.)
        entities = self._extract_entities(prompt)
        
        # Detect ambiguities
        ambiguities = self._detect_ambiguity(prompt)
        
        # Reason about tradeoffs
        tradeoffs = self._reason_tradeoffs(goals, ambiguities)
        
        # Calculate confidence
        confidence = self._calculate_confidence(task_type, goals, ambiguities)
        
        return Intent(
            type=task_type,
            goals=goals,
            entities=entities,
            ambiguities=ambiguities,
            tradeoffs=tradeoffs,
            confidence=confidence,
            raw_prompt=prompt
        )
    
    def _classify_task(self, prompt: str) -> TaskType:
        """Classify task complexity and type"""
        prompt_lower = prompt.lower()
        
        # Keywords for each type
        if any(kw in prompt_lower for kw in ["install", "setup", "deploy", "configure"]):
            return TaskType.DEPLOYMENT
        elif any(kw in prompt_lower for kw in ["code", "implement", "write", "develop", "build"]):
            return TaskType.CODING
        elif any(kw in prompt_lower for kw in ["research", "find", "search", "investigate"]):
            return TaskType.RESEARCH
        elif any(kw in prompt_lower for kw in ["analyze", "compare", "evaluate"]):
            return TaskType.ANALYSIS
        elif any(kw in prompt_lower for kw in ["create", "design", "generate"]):
            return TaskType.CREATIVE
        
        # Assess complexity by counting sub-tasks
        subtask_indicators = ["+", "and", "then", ",", ";"]
        subtask_count = sum(prompt.count(indicator) for indicator in subtask_indicators)
        
        if subtask_count >= 5:
            return TaskType.COMPLEX
        elif subtask_count >= 2:
            return TaskType.MODERATE
        else:
            return TaskType.SIMPLE
    
    def _extract_goals(self, prompt: str) -> List[str]:
        """Extract goals from prompt"""
        goals = []
        
        # Split by common delimiters
        parts = prompt.replace(" and ", "|").replace(", ", "|").replace(" + ", "|").split("|")
        
        for part in parts:
            part = part.strip()
            if part and len(part) > 10:  # Filter out noise
                goals.append(part)
        
        return goals if goals else [prompt]
    
    def _extract_entities(self, prompt: str) -> List[str]:
        """Extract entities (files, projects, tools)"""
        entities = []
        
        # Look for file paths
        import re
        file_patterns = [
            r'["\']([^"\']+\.(py|js|md|json|txt|yaml|yml))["\']',
            r'`([^`]+\.(py|js|md|json|txt|yaml|yml))`',
            r'(\w+\.(py|js|md|json|txt|yaml|yml))'
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, prompt)
            entities.extend([m[0] if isinstance(m, tuple) else m for m in matches])
        
        # Look for project names (capitalized words)
        project_pattern = r'\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b'
        projects = re.findall(project_pattern, prompt)
        entities.extend(projects)
        
        return list(set(entities))
    
    def _detect_ambiguity(self, prompt: str) -> List[str]:
        """Detect ambiguities in prompt"""
        ambiguities = []
        
        # Vague terms
        vague_terms = ["something", "anything", "somehow", "maybe", "probably", "might"]
        for term in vague_terms:
            if term in prompt.lower():
                ambiguities.append(f"Vague term: '{term}'")
        
        # Missing details
        if "?" in prompt:
            ambiguities.append("Contains questions - may need clarification")
        
        # Multiple interpretations
        if " or " in prompt.lower():
            ambiguities.append("Multiple options mentioned - need to choose")
        
        return ambiguities
    
    def _reason_tradeoffs(self, goals: List[str], ambiguities: List[str]) -> List[Dict[str, Any]]:
        """Reason about tradeoffs"""
        tradeoffs = []
        
        # If multiple goals, there might be tradeoffs
        if len(goals) > 1:
            tradeoffs.append({
                "type": "multiple_goals",
                "description": "Multiple goals may require prioritization",
                "options": ["sequential", "parallel", "prioritized"]
            })
        
        # If ambiguities exist, there are interpretation tradeoffs
        if ambiguities:
            tradeoffs.append({
                "type": "ambiguity",
                "description": "Ambiguous prompt - make reasonable assumptions",
                "strategy": "bias_to_action"
            })
        
        return tradeoffs
    
    def _calculate_confidence(self, task_type: TaskType, goals: List[str], ambiguities: List[str]) -> float:
        """Calculate confidence in intent detection"""
        confidence = 1.0
        
        # Reduce confidence for ambiguities
        confidence -= len(ambiguities) * 0.1
        
        # Reduce confidence for complex tasks
        if task_type == TaskType.COMPLEX:
            confidence -= 0.1
        
        # Reduce confidence for multiple goals
        if len(goals) > 3:
            confidence -= 0.1
        
        return max(0.1, min(1.0, confidence))


class Planner:
    """Task decomposition and planning"""
    
    def __init__(self, memory: DiveMemory3FileComplete):
        self.memory = memory
    
    def create_plan(self, intent: Intent, context: Dict[str, Any]) -> Plan:
        """Create execution plan from intent"""
        
        # Check memory for similar tasks
        similar_tasks = self._find_similar_tasks(intent)
        
        # Generate steps
        if intent.type == TaskType.SIMPLE:
            steps = self._create_simple_plan(intent)
        else:
            steps = self._create_complex_plan(intent, similar_tasks)
        
        # Identify dependencies
        self._identify_dependencies(steps)
        
        # Optimize for parallelism
        parallel_groups = self._optimize_parallelism(steps)
        
        # Assign models
        self._assign_models(steps, intent)
        
        return Plan(
            steps=steps,
            parallel_groups=parallel_groups
        )
    
    def _find_similar_tasks(self, intent: Intent) -> List[Dict[str, Any]]:
        """Find similar tasks in memory"""
        # Search memory for similar intents
        # This would use semantic search in production
        return []
    
    def _create_simple_plan(self, intent: Intent) -> List[Step]:
        """Create simple single-step plan"""
        return [Step(
            id=1,
            description=intent.goals[0] if intent.goals else intent.raw_prompt,
            status="pending"
        )]
    
    def _create_complex_plan(self, intent: Intent, similar_tasks: List[Dict[str, Any]]) -> List[Step]:
        """Create complex multi-step plan"""
        steps = []
        
        for i, goal in enumerate(intent.goals, 1):
            step = Step(
                id=i,
                description=goal,
                status="pending"
            )
            steps.append(step)
        
        return steps
    
    def _identify_dependencies(self, steps: List[Step]):
        """Identify dependencies between steps"""
        # Simple heuristic: each step depends on previous
        for i, step in enumerate(steps):
            if i > 0:
                step.dependencies = [steps[i-1].id]
    
    def _optimize_parallelism(self, steps: List[Step]) -> List[List[Step]]:
        """Optimize steps for parallel execution"""
        parallel_groups = []
        current_group = []
        
        for step in steps:
            if not step.dependencies:
                # No dependencies - can run in parallel
                current_group.append(step)
                step.parallel_group = len(parallel_groups)
            else:
                # Has dependencies - start new group
                if current_group:
                    parallel_groups.append(current_group)
                current_group = [step]
                step.parallel_group = len(parallel_groups)
        
        if current_group:
            parallel_groups.append(current_group)
        
        return parallel_groups
    
    def _assign_models(self, steps: List[Step], intent: Intent):
        """Assign best model to each step"""
        for step in steps:
            step.model = self._select_model(step, intent)
    
    def _select_model(self, step: Step, intent: Intent) -> ModelType:
        """Select best model for step"""
        desc_lower = step.description.lower()
        
        if any(kw in desc_lower for kw in ["code", "implement", "write code", "develop"]):
            return ModelType.GPT_CODEX
        elif any(kw in desc_lower for kw in ["reason", "analyze", "complex", "tradeoff"]):
            return ModelType.CLAUDE_OPUS
        elif any(kw in desc_lower for kw in ["knowledge", "research", "find information"]):
            return ModelType.GEMINI
        else:
            return ModelType.CLAUDE_SONNET  # Default


class EventStreamManager:
    """Manages event stream for context"""
    
    def __init__(self, max_events: int = 100):
        self.events: List[Event] = []
        self.max_events = max_events
    
    def add_event(self, event_type: str, data: Any):
        """Add event to stream"""
        event = Event(type=event_type, data=data)
        self.events.append(event)
        
        # Compact if too long
        if len(self.events) > self.max_events:
            self.compact()
    
    def compact(self):
        """Compact old events"""
        # Keep recent events
        self.events = self.events[-self.max_events//2:]
    
    def get_context(self) -> str:
        """Get context from recent events"""
        context_lines = []
        for event in self.events[-20:]:  # Last 20 events
            context_lines.append(f"[{event.type}] {event.data}")
        return "\n".join(context_lines)


class DiveSmartOrchestrator:
    """
    Smart Orchestrator with intelligent prompt processing
    
    Implements:
    - Intent detection
    - Task decomposition
    - Multi-model routing
    - Parallel execution
    - Memory integration
    """
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory = DiveMemory3FileComplete(memory_dir)
        self.intent_detector = IntentDetector(self.memory)
        self.planner = Planner(self.memory)
        self.event_stream = EventStreamManager()
        self.interrupt_handler = InterruptHandler()
        
        # Set interrupt callback
        self.interrupt_handler.set_interrupt_callback(self._handle_interrupt_callback)
        
        print("🧠 Dive Smart Orchestrator initialized (with interrupt handling)")
    
    def process_prompt(self, prompt: str, project_id: str = "default") -> Dict[str, Any]:
        """
        Process user prompt with intelligent analysis
        
        Flow:
        1. ANALYZE - Intent detection, complexity assessment
        2. THINK FIRST - Identify resources, plan operations
        3. PLAN - Task decomposition
        4. ROUTE - Model selection
        5. EXECUTE - Batch operations
        6. OBSERVE - Update and store
        7. REPEAT/FINISH - Continue or complete
        """
        
        print(f"\n{'='*60}")
        print(f"🎯 Processing Prompt: {prompt[:80]}...")
        print(f"{'='*60}\n")
        
        # Add user message to event stream
        self.event_stream.add_event("user_message", prompt)
        
        # Phase 1: ANALYZE
        print("📊 Phase 1: ANALYZE")
        context = self._load_context(project_id)
        intent = self.intent_detector.detect(prompt, context)
        print(f"   Intent Type: {intent.type.value}")
        print(f"   Goals: {len(intent.goals)}")
        print(f"   Confidence: {intent.confidence:.2f}")
        
        # Phase 2: THINK FIRST
        print("\n🤔 Phase 2: THINK FIRST")
        resources = self._identify_resources(intent, context)
        print(f"   Resources Identified: {len(resources)}")
        
        # Phase 3: PLAN
        print("\n📋 Phase 3: PLAN")
        plan = self.planner.create_plan(intent, context)
        print(f"   Steps: {len(plan.steps)}")
        print(f"   Parallel Groups: {len(plan.parallel_groups)}")
        self.event_stream.add_event("plan", plan)
        
        # Phase 4: ROUTE
        print("\n🔀 Phase 4: ROUTE")
        for step in plan.steps:
            print(f"   Step {step.id}: {step.model.value if step.model else 'default'}")
        
        # Phase 5: EXECUTE
        print("\n⚡ Phase 5: EXECUTE")
        self.interrupt_handler.set_current_plan(plan)
        self.interrupt_handler.start_execution()
        results = self._execute_plan(plan, project_id)
        self.interrupt_handler.stop_execution()
        
        # Phase 6: OBSERVE
        print("\n👁️ Phase 6: OBSERVE")
        self._update_plan(plan, results)
        self._store_in_memory(project_id, intent, plan, results)
        
        # Phase 7: FINISH
        print("\n✅ Phase 7: FINISH")
        final_result = self._format_result(plan, results)
        self.event_stream.add_event("result", final_result)
        
        return final_result
    
    def _load_context(self, project_id: str) -> Dict[str, Any]:
        """Load context from memory"""
        context = self.memory.load_project(project_id)
        return context
    
    def _identify_resources(self, intent: Intent, context: Dict[str, Any]) -> List[str]:
        """Identify all needed resources"""
        resources = []
        
        # Files mentioned in entities
        resources.extend([e for e in intent.entities if '.' in e])
        
        # Tools needed based on task type
        if intent.type == TaskType.CODING:
            resources.extend(["code_editor", "git", "test_runner"])
        elif intent.type == TaskType.RESEARCH:
            resources.extend(["web_browser", "search_engine"])
        elif intent.type == TaskType.DEPLOYMENT:
            resources.extend(["shell", "package_manager", "git"])
        
        return resources
    
    def _execute_plan(self, plan: Plan, project_id: str) -> List[Dict[str, Any]]:
        """Execute plan with batching"""
        results = []
        
        for group in plan.parallel_groups:
            print(f"   Executing parallel group with {len(group)} steps...")
            
            # In production, this would use actual parallel execution
            for step in group:
                step.status = "in_progress"
                result = self._execute_step(step, project_id)
                step.status = "done"
                step.result = result
                results.append(result)
                
                self.event_stream.add_event("observation", {
                    "step_id": step.id,
                    "result": result
                })
        
        return results
    
    def _execute_step(self, step: Step, project_id: str) -> Dict[str, Any]:
        """Execute single step"""
        # Placeholder - in production, this would call actual tools/models
        return {
            "step_id": step.id,
            "description": step.description,
            "model": step.model.value if step.model else "default",
            "status": "success",
            "output": f"Executed: {step.description}"
        }
    
    def _update_plan(self, plan: Plan, results: List[Dict[str, Any]]):
        """Update plan based on results"""
        plan.status = "completed"
        plan.updated_at = datetime.now()
    
    def _store_in_memory(self, project_id: str, intent: Intent, plan: Plan, results: List[Dict[str, Any]]):
        """Store execution in memory"""
        # Store in CHANGELOG
        change_type = "Added" if "add" in intent.raw_prompt.lower() else "Changed"
        self.memory.log_change(
            project_id,
            change_type,
            f"Processed: {intent.raw_prompt[:100]}"
        )
        
        # Store in FULL doc
        execution_summary = f"\n## Execution: {datetime.now().isoformat()}\n"
        execution_summary += f"Intent: {intent.type.value}\n"
        execution_summary += f"Steps: {len(plan.steps)}\n"
        execution_summary += f"Results: {len(results)} completed\n"
        
        self.memory.save_full_knowledge(project_id, execution_summary, append=True)
    
    def _format_result(self, plan: Plan, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format final result"""
        return {
            "status": "success",
            "plan": {
                "steps": len(plan.steps),
                "completed": sum(1 for s in plan.steps if s.status == "done")
            },
            "results": results,
            "summary": f"Completed {len(results)} steps successfully"
        }
    
    def _handle_interrupt_callback(self, interrupt: Interrupt):
        """Handle interrupt callback"""
        print(f"   ⚠️ Interrupt callback: {interrupt.intent}")
        # In production, this would handle the interrupt appropriately
    
    def handle_user_interrupt(self, message: str) -> Interrupt:
        """Handle user interrupt during execution"""
        return self.interrupt_handler.handle_user_input(message)


# Test function
def test_smart_orchestrator():
    """Test smart orchestrator"""
    print("🧪 Testing Dive Smart Orchestrator\n")
    
    orchestrator = DiveSmartOrchestrator()
    
    # Test 1: Simple prompt
    print("\n" + "="*60)
    print("TEST 1: Simple Prompt")
    print("="*60)
    result1 = orchestrator.process_prompt(
        "Install Dive AI from GitHub",
        project_id="dive-ai"
    )
    print(f"\nResult: {result1['summary']}")
    
    # Test 2: Complex prompt
    print("\n" + "="*60)
    print("TEST 2: Complex Prompt")
    print("="*60)
    result2 = orchestrator.process_prompt(
        "Install Dive AI, configure LLM client, setup first run, test environment, and update documentation",
        project_id="dive-ai"
    )
    print(f"\nResult: {result2['summary']}")
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_smart_orchestrator()
