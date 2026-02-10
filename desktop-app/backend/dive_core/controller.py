"""
Dive AI v25 - Full-Duplex Controller

Coordinate simultaneous listening and speaking
Based on NVIDIA PersonaPlex and Kyutai Moshi architectures

Features:
- Listen while speaking
- Handle interruptions
- Natural backchanneling
- Turn-taking management
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, AsyncGenerator, List
try:
    import numpy as np
except ImportError:
    np = None


logger = logging.getLogger(__name__)


class DuplexState(Enum):
    """State of the duplex controller"""
    IDLE = "idle"
    LISTENING = "listening"
    SPEAKING = "speaking"
    DUPLEX = "duplex"  # Both listening and speaking


class TurnState(Enum):
    """Who has the conversational turn"""
    USER = "user"
    ASSISTANT = "assistant"
    OVERLAP = "overlap"


@dataclass
class DuplexEvent:
    """Event from duplex controller"""
    type: str  # "transcription", "response", "interruption", "backchannel"
    data: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class DuplexConfig:
    """Configuration for duplex controller"""
    # Timing
    interruption_threshold: float = 0.3  # seconds of user speech to trigger interruption
    backchannel_interval: float = 3.0    # seconds between backchannels
    silence_timeout: float = 1.5         # seconds of silence before turn ends
    
    # Behavior
    allow_interruptions: bool = True
    enable_backchannels: bool = True
    
    # Audio
    sample_rate: int = 16000
    
    # Language
    language: str = "en"


class FullDuplexController:
    """
    Full-Duplex Voice Controller
    
    Enables natural conversation by:
    1. Listening continuously (even while speaking)
    2. Detecting and handling interruptions
    3. Generating natural backchannels
    4. Managing turn-taking
    """
    
    def __init__(self, config: Optional[DuplexConfig] = None):
        self.config = config or DuplexConfig()
        
        # State
        self._state = DuplexState.IDLE
        self._turn = TurnState.USER
        
        # Components (injected)
        self._stt = None
        self._tts = None
        self._intent_analyzer = None
        
        # Queues for async communication
        self._transcription_queue: asyncio.Queue = asyncio.Queue()
        self._response_queue: asyncio.Queue = asyncio.Queue()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
        # Timing
        self._last_user_speech = 0
        self._last_assistant_speech = 0
        self._last_backchannel = 0
        
        # Callbacks
        self._on_transcription: Optional[Callable] = None
        self._on_response: Optional[Callable] = None
        self._on_intent: Optional[Callable] = None
        self._on_interruption: Optional[Callable] = None
        
        # Tasks
        self._tasks: List[asyncio.Task] = []
        self._running = False
        
    def set_components(self, stt, tts, intent_analyzer):
        """Set STT, TTS, and Intent components"""
        self._stt = stt
        self._tts = tts
        self._intent_analyzer = intent_analyzer
        
    def set_callbacks(
        self,
        on_transcription: Optional[Callable] = None,
        on_response: Optional[Callable] = None,
        on_intent: Optional[Callable] = None,
        on_interruption: Optional[Callable] = None
    ):
        """Set event callbacks"""
        self._on_transcription = on_transcription
        self._on_response = on_response
        self._on_intent = on_intent
        self._on_interruption = on_interruption
        
    async def start(self, audio_input: AsyncGenerator, audio_output: Callable):
        """
        Start full-duplex operation
        
        Args:
            audio_input: Async generator yielding audio chunks
            audio_output: Callable to play audio
        """
        logger.info("🎙️ Starting Full-Duplex Controller...")
        
        self._running = True
        self._state = DuplexState.LISTENING
        
        try:
            # Create concurrent tasks
            async with asyncio.TaskGroup() as tg:
                # Listen task - continuous STT
                self._tasks.append(
                    tg.create_task(self._listen_loop(audio_input))
                )
                
                # Process task - handle transcriptions
                self._tasks.append(
                    tg.create_task(self._process_loop())
                )
                
                # Speak task - handle responses
                self._tasks.append(
                    tg.create_task(self._speak_loop(audio_output))
                )
                
                # Monitor task - handle interruptions and backchannels
                self._tasks.append(
                    tg.create_task(self._monitor_loop())
                )
                
        except asyncio.CancelledError:
            logger.info("🛑 Full-Duplex Controller cancelled")
            
        finally:
            self._running = False
            self._state = DuplexState.IDLE
            logger.info("🎙️ Full-Duplex Controller stopped")
            
    async def stop(self):
        """Stop full-duplex operation"""
        self._running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
            
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        
    async def _listen_loop(self, audio_input: AsyncGenerator):
        """Continuous listening loop"""
        logger.info("👂 Listen loop started")
        
        try:
            async for transcription in self._stt.transcribe_stream(audio_input):
                if not self._running:
                    break
                    
                # Update timing
                self._last_user_speech = time.time()
                
                # Update state
                if self._state == DuplexState.SPEAKING:
                    self._state = DuplexState.DUPLEX
                else:
                    self._state = DuplexState.LISTENING
                    
                # Put transcription in queue
                await self._transcription_queue.put(transcription)
                
                # Emit event
                await self._emit_event(DuplexEvent(
                    type="transcription",
                    data={
                        "text": transcription.text,
                        "is_final": transcription.is_final,
                        "confidence": transcription.confidence
                    }
                ))
                
                # Callback
                if self._on_transcription:
                    self._on_transcription(transcription)
                    
        except asyncio.CancelledError:
            pass
            
        logger.info("👂 Listen loop stopped")
        
    async def _process_loop(self):
        """Process transcriptions and generate responses"""
        logger.info("🧠 Process loop started")
        
        try:
            while self._running:
                try:
                    # Get transcription with timeout
                    transcription = await asyncio.wait_for(
                        self._transcription_queue.get(),
                        timeout=0.1
                    )
                    
                    # Only process final transcriptions
                    if not transcription.is_final:
                        continue
                        
                    # Analyze intent
                    intent = await self._intent_analyzer.analyze(
                        transcription.text,
                        {"language": transcription.language}
                    )
                    
                    # Callback
                    if self._on_intent:
                        self._on_intent(intent)
                        
                    # Generate response
                    response = await self._generate_response(intent)
                    
                    # Put response in queue
                    await self._response_queue.put(response)
                    
                except asyncio.TimeoutError:
                    continue
                    
        except asyncio.CancelledError:
            pass
            
        logger.info("🧠 Process loop stopped")
        
    async def _speak_loop(self, audio_output: Callable):
        """Handle speaking responses"""
        logger.info("🔊 Speak loop started")
        
        try:
            while self._running:
                try:
                    # Get response with timeout
                    response = await asyncio.wait_for(
                        self._response_queue.get(),
                        timeout=0.1
                    )
                    
                    # Update state
                    self._state = DuplexState.SPEAKING
                    self._turn = TurnState.ASSISTANT
                    
                    # Speak response
                    async for audio_event in self._tts.speak_stream(response):
                        if not self._running:
                            break
                            
                        # Check for interruption
                        if await self._check_interruption():
                            await self._handle_interruption()
                            break
                            
                        # Output audio
                        audio_output(audio_event.audio)
                        
                        self._last_assistant_speech = time.time()
                        
                    # Update state
                    self._state = DuplexState.LISTENING
                    self._turn = TurnState.USER
                    
                    # Emit event
                    await self._emit_event(DuplexEvent(
                        type="response",
                        data={"text": response}
                    ))
                    
                    # Callback
                    if self._on_response:
                        self._on_response(response)
                        
                except asyncio.TimeoutError:
                    continue
                    
        except asyncio.CancelledError:
            pass
            
        logger.info("🔊 Speak loop stopped")
        
    async def _monitor_loop(self):
        """Monitor for interruptions and generate backchannels"""
        logger.info("👀 Monitor loop started")
        
        try:
            while self._running:
                await asyncio.sleep(0.1)
                
                # Check for backchannel opportunity
                if self.config.enable_backchannels:
                    await self._check_backchannel()
                    
        except asyncio.CancelledError:
            pass
            
        logger.info("👀 Monitor loop stopped")
        
    async def _check_interruption(self) -> bool:
        """Check if user is interrupting"""
        if not self.config.allow_interruptions:
            return False
            
        # Check if user has been speaking while we're speaking
        if self._state == DuplexState.DUPLEX:
            time_since_user_speech = time.time() - self._last_user_speech
            if time_since_user_speech < self.config.interruption_threshold:
                return True
                
        return False
        
    async def _handle_interruption(self):
        """Handle user interruption"""
        logger.info("⚡ Interruption detected!")
        
        # Stop speaking
        self._tts.stop()
        
        # Update state
        self._state = DuplexState.LISTENING
        self._turn = TurnState.USER
        
        # Emit event
        await self._emit_event(DuplexEvent(
            type="interruption",
            data={"timestamp": time.time()}
        ))
        
        # Callback
        if self._on_interruption:
            self._on_interruption()
            
    async def _check_backchannel(self):
        """Check if we should emit a backchannel"""
        now = time.time()
        
        # Only backchannel when user is speaking
        if self._turn != TurnState.USER:
            return
            
        # Check timing
        time_since_last = now - self._last_backchannel
        time_since_user = now - self._last_user_speech
        
        # Emit backchannel if user has been speaking for a while
        if (time_since_last > self.config.backchannel_interval and 
            time_since_user < 0.5):  # User recently spoke
            
            await self._emit_backchannel()
            self._last_backchannel = now
            
    async def _emit_backchannel(self):
        """Emit a backchannel response"""
        from ..tts.streaming_tts import ResponseTemplates
        
        backchannel = ResponseTemplates.get("backchannel", self.config.language)
        
        logger.debug(f"💬 Backchannel: {backchannel}")
        
        # Emit event
        await self._emit_event(DuplexEvent(
            type="backchannel",
            data={"text": backchannel}
        ))
        
        # Speak backchannel (non-blocking)
        asyncio.create_task(self._speak_backchannel(backchannel))
        
    async def _speak_backchannel(self, text: str):
        """Speak backchannel without blocking"""
        try:
            audio = await self._tts.speak(text)
            # Output would go here
        except Exception as e:
            logger.debug(f"Backchannel failed: {e}")
            
    async def _generate_response(self, intent) -> str:
        """Generate response based on intent"""
        from ..tts.streaming_tts import ResponseTemplates
        
        # Map intent to response template
        if intent.action.value in ["click", "type", "scroll", "open", "close"]:
            return ResponseTemplates.get(
                "acknowledge",
                self.config.language,
                action=intent.action.value,
                target=intent.target or "that"
            )
        elif intent.action.value == "question":
            return "Let me think about that..."
        else:
            return "I understand. Let me help you with that."
            
    async def _emit_event(self, event: DuplexEvent):
        """Emit event to queue"""
        await self._event_queue.put(event)
        
    async def get_events(self) -> AsyncGenerator[DuplexEvent, None]:
        """Get events from controller"""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=0.1
                )
                yield event
            except asyncio.TimeoutError:
                continue
                
    @property
    def state(self) -> DuplexState:
        """Current duplex state"""
        return self._state
        
    @property
    def turn(self) -> TurnState:
        """Current turn holder"""
        return self._turn
        
    @property
    def is_listening(self) -> bool:
        """Is currently listening"""
        return self._state in [DuplexState.LISTENING, DuplexState.DUPLEX]
        
    @property
    def is_speaking(self) -> bool:
        """Is currently speaking"""
        return self._state in [DuplexState.SPEAKING, DuplexState.DUPLEX]


# Simplified interface for common use cases
class SimpleVoiceAssistant:
    """
    Simplified voice assistant interface
    
    Example usage:
        assistant = SimpleVoiceAssistant()
        await assistant.start()
        
        # User speaks: "Open Chrome"
        # Assistant responds: "Opening Chrome now..."
        # Vision Model executes the action
    """
    
    def __init__(self, language: str = "en"):
        self.language = language
        self._controller = None
        self._stt = None
        self._tts = None
        self._intent_analyzer = None
        
    async def initialize(self):
        """Initialize all components"""
        from ..stt.streaming_stt import StreamingSTT, STTConfig
        from ..tts.streaming_tts import StreamingTTS, TTSConfig, TTSModel
        from ..understanding.intent_analyzer import IntentAnalyzer
        
        # Initialize STT
        self._stt = StreamingSTT(STTConfig(language=self.language))
        await self._stt.initialize()
        
        # Initialize TTS
        self._tts = StreamingTTS(TTSConfig(
            model=TTSModel.EDGE_TTS,
            language=self.language
        ))
        await self._tts.initialize()
        
        # Initialize Intent Analyzer
        self._intent_analyzer = IntentAnalyzer(self.language)
        
        # Initialize Controller
        self._controller = FullDuplexController(DuplexConfig(
            language=self.language
        ))
        self._controller.set_components(
            self._stt,
            self._tts,
            self._intent_analyzer
        )
        
        logger.info("✅ Voice Assistant initialized")
        
    async def process_audio(self, audio: np.ndarray) -> dict:
        """
        Process single audio input
        
        Args:
            audio: Audio data (16kHz, mono, float32)
            
        Returns:
            Dict with transcription, intent, and response
        """
        # Transcribe
        transcription = await self._stt.transcribe(audio)
        
        # Analyze intent
        intent = await self._intent_analyzer.analyze(transcription.text)
        
        # Generate response
        response = await self._generate_response(intent)
        
        # Speak response
        response_audio = await self._tts.speak(response)
        
        return {
            "transcription": transcription.text,
            "intent": intent.to_dict(),
            "response": response,
            "response_audio": response_audio
        }
        
    async def _generate_response(self, intent) -> str:
        """Generate response for intent"""
        from ..tts.streaming_tts import ResponseTemplates
        
        if intent.action.value in ["click", "type", "scroll", "open", "close", "navigate", "search"]:
            return ResponseTemplates.get(
                "acknowledge",
                self.language,
                action=intent.action.value,
                target=intent.target or "that"
            )
        elif intent.action.value == "question":
            return "Let me think about that..." if self.language == "en" else "Để tôi suy nghĩ..."
        elif intent.action.value == "confirm":
            return "Got it!" if self.language == "en" else "Được rồi!"
        elif intent.action.value == "cancel":
            return "Cancelled." if self.language == "en" else "Đã hủy."
        else:
            return "I understand." if self.language == "en" else "Tôi hiểu."


# Test function
async def test_duplex_controller():
    """Test duplex controller"""
    print("🧪 Testing Full-Duplex Controller...")
    print("=" * 50)
    
    # Create simple assistant
    assistant = SimpleVoiceAssistant(language="en")
    
    print("📝 Note: Full test requires audio input/output")
    print("   Testing intent analysis only...")
    
    # Test intent analysis
    from ..understanding.intent_analyzer import IntentAnalyzer
    
    analyzer = IntentAnalyzer()
    
    test_inputs = [
        "Click on the submit button",
        "Open Chrome and search for weather",
        "Type hello world",
        "Scroll down",
        "What's the weather today?"
    ]
    
    for text in test_inputs:
        intent = await analyzer.analyze(text)
        print(f"📝 \"{text}\"")
        print(f"   → {intent}")
        print()
        
    print("=" * 50)
    print("✅ Duplex controller test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_duplex_controller())
