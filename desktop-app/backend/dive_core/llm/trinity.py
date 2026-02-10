"""
Dive AI v25 - Trinity Architecture

Unified System: Hear + Vision + Transformation

The Trinity combines three models into one seamless experience:
- HEAR: Listen, Understand, Speak (Voice Interface)
- VISION: See, Detect, Act (Desktop Automation)
- TRANSFORMATION: Think, Plan, Execute (Reasoning Engine)

This is the main entry point for Dive AI v25 Computer Assistant.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional, Callable, AsyncGenerator, Dict, Any, List
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)


class TrinityState(Enum):
    """State of the Trinity system"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    ACTING = "acting"
    SPEAKING = "speaking"


@dataclass
class TrinityConfig:
    """Configuration for Trinity system"""
    # Language
    language: str = "en"  # "en", "vi", "auto"
    
    # Models
    hear_enabled: bool = True
    vision_enabled: bool = True
    transformation_enabled: bool = True
    
    # Performance
    target_latency_ms: int = 500
    
    # Hardware
    device: str = "cuda"  # "cuda", "cpu"
    
    # Behavior
    speak_while_acting: bool = True  # Full-duplex: speak progress while executing
    learn_from_actions: bool = True  # Store successful actions in memory


@dataclass
class TrinityEvent:
    """Event from Trinity system"""
    type: str
    source: str  # "hear", "vision", "transformation"
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class DiveAIv25Trinity:
    """
    Dive AI v25 Trinity - Complete Computer Assistant
    
    Combines:
    - Hear Model: Voice interface (listen, understand, speak)
    - Vision Model: Desktop automation (see, detect, act)
    - Transformation Model: Reasoning engine (think, plan, execute)
    
    Usage:
        trinity = DiveAIv25Trinity()
        await trinity.initialize()
        
        # Voice command
        result = await trinity.process_voice(audio_data)
        
        # Text command
        result = await trinity.process_text("Open Chrome")
        
        # Streaming mode
        async for event in trinity.stream(audio_generator):
            print(event)
    """
    
    def __init__(self, config: Optional[TrinityConfig] = None):
        self.config = config or TrinityConfig()
        
        # Models
        self._hear = None
        self._vision = None
        self._transformation = None
        self._memory = None
        
        # State
        self._state = TrinityState.IDLE
        self._initialized = False
        
        # Event queue
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
        # Statistics
        self._stats = {
            "commands_processed": 0,
            "actions_executed": 0,
            "errors": 0,
            "total_latency_ms": 0
        }
        
    async def initialize(self):
        """Initialize all Trinity components"""
        if self._initialized:
            return
            
        logger.info("🔺 Initializing Dive AI v25 Trinity...")
        logger.info(f"   Language: {self.config.language}")
        logger.info(f"   Device: {self.config.device}")
        
        start_time = time.time()
        
        try:
            # Initialize Hear Model
            if self.config.hear_enabled:
                logger.info("   👂 Initializing Hear Model...")
                from hear.hear_model import HearModel, HearModelConfig
                
                hear_config = HearModelConfig(
                    language=self.config.language,
                    stt_device=self.config.device
                )
                self._hear = HearModel(hear_config)
                await self._hear.initialize()
                
                # Set callbacks
                self._hear.set_callbacks(
                    on_intent=self._on_intent,
                    on_action=self._on_action_request
                )
                
            # Initialize Vision Model (from v24)
            if self.config.vision_enabled:
                logger.info("   👁️ Initializing Vision Model...")
                # Import from v24 or create stub
                try:
                    import sys
                    sys.path.insert(0, '/home/ubuntu/dive-ai-v24')
                    from vision.models.vision_model import VisionModel
                    self._vision = VisionModel()
                    await self._vision.initialize()
                except ImportError:
                    logger.warning("   ⚠️ Vision Model not available, using stub")
                    self._vision = VisionModelStub()
                    
            # Initialize Transformation Model (from v24)
            if self.config.transformation_enabled:
                logger.info("   🧠 Initializing Transformation Model...")
                try:
                    from core.orchestrator.v24_orchestrator import DiveAIv24Orchestrator
                    self._transformation = DiveAIv24Orchestrator()
                    await self._transformation.initialize()
                except ImportError:
                    logger.warning("   ⚠️ Transformation Model not available, using stub")
                    self._transformation = TransformationModelStub()
                    
            # Initialize Memory V4
            logger.info("   💾 Initializing Memory V4...")
            try:
                from memory.storage.memory_v4 import MemoryV4
                self._memory = MemoryV4()
                await self._memory.initialize()
            except ImportError:
                logger.warning("   ⚠️ Memory V4 not available, using stub")
                self._memory = MemoryStub()
                
            elapsed = time.time() - start_time
            self._initialized = True
            
            logger.info(f"✅ Trinity initialized in {elapsed:.2f}s")
            logger.info(f"   Hear: {'✅' if self._hear else '❌'}")
            logger.info(f"   Vision: {'✅' if self._vision else '❌'}")
            logger.info(f"   Transformation: {'✅' if self._transformation else '❌'}")
            logger.info(f"   Memory: {'✅' if self._memory else '❌'}")
            
        except Exception as e:
            logger.error(f"❌ Trinity initialization failed: {e}")
            raise
            
    async def process_voice(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Process voice command through full Trinity pipeline
        
        Args:
            audio: Audio data (16kHz, mono, float32)
            
        Returns:
            Dict with results from all stages
        """
        if not self._initialized:
            await self.initialize()
            
        start_time = time.time()
        self._state = TrinityState.LISTENING
        
        result = {
            "success": False,
            "transcription": None,
            "intent": None,
            "plan": None,
            "actions": [],
            "response": None,
            "latency_ms": 0
        }
        
        try:
            # 1. HEAR: Listen and Understand
            await self._emit_event(TrinityEvent("listening", "hear"))
            
            hear_result = await self._hear.listen_and_respond(audio)
            result["transcription"] = hear_result["transcription"]
            result["intent"] = hear_result["intent"]
            
            await self._emit_event(TrinityEvent("understood", "hear", {
                "text": hear_result["transcription"],
                "intent": hear_result["intent"]
            }))
            
            # 2. TRANSFORMATION: Plan
            self._state = TrinityState.THINKING
            await self._emit_event(TrinityEvent("thinking", "transformation"))
            
            plan = await self._transformation.plan(hear_result["intent"])
            result["plan"] = plan
            
            await self._emit_event(TrinityEvent("planned", "transformation", {
                "steps": len(plan.get("steps", []))
            }))
            
            # 3. VISION: Execute (with voice feedback)
            self._state = TrinityState.ACTING
            
            for step in plan.get("steps", []):
                # Speak progress (if enabled)
                if self.config.speak_while_acting:
                    progress_text = f"Executing: {step.get('description', 'action')}..."
                    asyncio.create_task(self._speak_progress(progress_text))
                    
                # Execute action
                await self._emit_event(TrinityEvent("executing", "vision", step))
                
                action_result = await self._vision.execute(step)
                result["actions"].append(action_result)
                
                if not action_result.get("success", False):
                    await self._emit_event(TrinityEvent("error", "vision", {
                        "step": step,
                        "error": action_result.get("error")
                    }))
                    break
                    
            # 4. HEAR: Confirm completion
            self._state = TrinityState.SPEAKING
            
            if all(a.get("success", False) for a in result["actions"]):
                response = self._generate_completion_response(result)
                result["response"] = response
                result["success"] = True
                
                # Speak confirmation
                await self._hear.speak(response)
                
                # Learn from success
                if self.config.learn_from_actions:
                    await self._memory.store_learning(
                        result["intent"],
                        result["plan"],
                        result["actions"]
                    )
            else:
                response = self._generate_error_response(result)
                result["response"] = response
                await self._hear.speak(response)
                
            # Calculate latency
            result["latency_ms"] = int((time.time() - start_time) * 1000)
            
            # Update stats
            self._stats["commands_processed"] += 1
            self._stats["actions_executed"] += len(result["actions"])
            self._stats["total_latency_ms"] += result["latency_ms"]
            if not result["success"]:
                self._stats["errors"] += 1
                
        except Exception as e:
            logger.error(f"Trinity error: {e}")
            result["error"] = str(e)
            self._stats["errors"] += 1
            
        finally:
            self._state = TrinityState.IDLE
            
        return result
        
    async def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text command (skip STT)
        
        Args:
            text: Command text
            
        Returns:
            Dict with results
        """
        if not self._initialized:
            await self.initialize()
            
        # Understand intent
        intent = await self._hear.understand(text)
        
        # Create mock audio result
        mock_result = {
            "transcription": text,
            "intent": intent.to_dict(),
            "response": self._hear._generate_response(intent)
        }
        
        # Process through transformation and vision
        return await self._process_intent(intent, mock_result)
        
    async def _process_intent(self, intent, hear_result: Dict) -> Dict[str, Any]:
        """Process intent through transformation and vision"""
        result = {
            "success": False,
            "transcription": hear_result.get("transcription"),
            "intent": hear_result.get("intent"),
            "plan": None,
            "actions": [],
            "response": None
        }
        
        # Plan
        plan = await self._transformation.plan(intent)
        result["plan"] = plan
        
        # Execute
        for step in plan.get("steps", []):
            action_result = await self._vision.execute(step)
            result["actions"].append(action_result)
            
            if not action_result.get("success", False):
                break
                
        # Determine success
        result["success"] = all(a.get("success", False) for a in result["actions"])
        
        # Generate response
        if result["success"]:
            result["response"] = self._generate_completion_response(result)
        else:
            result["response"] = self._generate_error_response(result)
            
        return result
        
    async def stream(
        self,
        audio_stream: AsyncGenerator[np.ndarray, None],
        audio_output: Optional[Callable] = None
    ) -> AsyncGenerator[TrinityEvent, None]:
        """
        Full streaming mode
        
        Args:
            audio_stream: Async generator yielding audio chunks
            audio_output: Callable to play audio
            
        Yields:
            TrinityEvent for each stage
        """
        if not self._initialized:
            await self.initialize()
            
        yield TrinityEvent("started", "trinity")
        
        try:
            async for hear_event in self._hear.stream(audio_stream, audio_output):
                # Forward hear events
                yield TrinityEvent(
                    hear_event.type,
                    "hear",
                    hear_event.data
                )
                
                # Process actions
                if hear_event.type == "action":
                    intent_data = hear_event.data
                    
                    # Plan
                    yield TrinityEvent("thinking", "transformation")
                    plan = await self._transformation.plan(intent_data)
                    yield TrinityEvent("planned", "transformation", plan)
                    
                    # Execute
                    for step in plan.get("steps", []):
                        yield TrinityEvent("executing", "vision", step)
                        result = await self._vision.execute(step)
                        yield TrinityEvent("executed", "vision", result)
                        
        except asyncio.CancelledError:
            yield TrinityEvent("cancelled", "trinity")
            
        finally:
            yield TrinityEvent("stopped", "trinity")
            
    async def _speak_progress(self, text: str):
        """Speak progress (non-blocking)"""
        try:
            await self._hear.speak(text)
        except Exception as e:
            logger.debug(f"Progress speech failed: {e}")
            
    def _generate_completion_response(self, result: Dict) -> str:
        """Generate completion response"""
        lang = self.config.language if self.config.language != "auto" else "en"
        
        action_count = len(result.get("actions", []))
        
        if lang == "vi":
            if action_count == 1:
                return "Xong! Đã hoàn thành."
            return f"Xong! Đã thực hiện {action_count} bước."
        else:
            if action_count == 1:
                return "Done! Task completed."
            return f"Done! Completed {action_count} steps."
            
    def _generate_error_response(self, result: Dict) -> str:
        """Generate error response"""
        lang = self.config.language if self.config.language != "auto" else "en"
        
        # Find the failed action
        failed_action = None
        for action in result.get("actions", []):
            if not action.get("success", False):
                failed_action = action
                break
                
        error = failed_action.get("error", "Unknown error") if failed_action else "Unknown error"
        
        if lang == "vi":
            return f"Xin lỗi, có lỗi xảy ra: {error}"
        else:
            return f"Sorry, there was an error: {error}"
            
    def _on_intent(self, intent):
        """Callback when intent is detected"""
        logger.debug(f"Intent detected: {intent}")
        
    def _on_action_request(self, intent):
        """Callback when action is requested"""
        logger.debug(f"Action requested: {intent}")
        
    async def _emit_event(self, event: TrinityEvent):
        """Emit event to queue"""
        await self._event_queue.put(event)
        
    async def get_events(self) -> AsyncGenerator[TrinityEvent, None]:
        """Get events from queue"""
        while True:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=0.1
                )
                yield event
            except asyncio.TimeoutError:
                continue
                
    @property
    def state(self) -> TrinityState:
        """Current state"""
        return self._state
        
    @property
    def stats(self) -> Dict[str, Any]:
        """Get statistics"""
        stats = self._stats.copy()
        if stats["commands_processed"] > 0:
            stats["avg_latency_ms"] = stats["total_latency_ms"] / stats["commands_processed"]
        else:
            stats["avg_latency_ms"] = 0
        return stats


# Stub classes for when models are not available
class VisionModelStub:
    """Stub Vision Model for testing"""
    
    async def initialize(self):
        pass
        
    async def execute(self, step: Dict) -> Dict:
        return {
            "success": True,
            "step": step,
            "message": "[Vision Model Stub] Action simulated"
        }


class TransformationModelStub:
    """Stub Transformation Model for testing"""
    
    async def initialize(self):
        pass
        
    async def plan(self, intent) -> Dict:
        if isinstance(intent, dict):
            action = intent.get("action", "unknown")
            target = intent.get("target", "")
        else:
            action = intent.action.value if hasattr(intent, 'action') else "unknown"
            target = intent.target if hasattr(intent, 'target') else ""
            
        return {
            "steps": [
                {
                    "action": action,
                    "target": target,
                    "description": f"{action} {target}"
                }
            ]
        }


class MemoryStub:
    """Stub Memory for testing"""
    
    async def initialize(self):
        pass
        
    async def store_learning(self, intent, plan, actions):
        logger.debug(f"[Memory Stub] Stored learning: {intent}")


# Factory function
async def create_trinity(
    language: str = "en",
    device: str = "cuda"
) -> DiveAIv25Trinity:
    """
    Create and initialize Trinity
    
    Args:
        language: Language code
        device: "cuda" or "cpu"
        
    Returns:
        Initialized DiveAIv25Trinity
    """
    config = TrinityConfig(
        language=language,
        device=device
    )
    
    trinity = DiveAIv25Trinity(config)
    await trinity.initialize()
    return trinity


# Test function
async def test_trinity():
    """Test Trinity system"""
    print("🧪 Testing Dive AI v25 Trinity...")
    print("=" * 60)
    
    # Create Trinity with stubs
    config = TrinityConfig(
        language="en",
        device="cpu"
    )
    
    trinity = DiveAIv25Trinity(config)
    
    print("📝 Initializing Trinity...")
    await trinity.initialize()
    
    print("\n📝 Testing text commands...")
    
    test_commands = [
        "Open Chrome",
        "Click on the submit button",
        "Type hello world in the search box",
        "Search for weather forecast",
        "Take a screenshot"
    ]
    
    for cmd in test_commands:
        print(f"\n🎤 Command: \"{cmd}\"")
        result = await trinity.process_text(cmd)
        print(f"   Success: {result['success']}")
        print(f"   Intent: {result['intent'].get('action', 'unknown')}")
        print(f"   Response: {result['response']}")
        
    print("\n📊 Statistics:")
    stats = trinity.stats
    print(f"   Commands: {stats['commands_processed']}")
    print(f"   Actions: {stats['actions_executed']}")
    print(f"   Errors: {stats['errors']}")
    
    print("\n" + "=" * 60)
    print("✅ Trinity test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_trinity())
