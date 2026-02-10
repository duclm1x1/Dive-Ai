"""
Dive AI v25 - Hear Model

Strategic Listen-Understand-Speak Complete

The Hear Model is the voice interface for Dive AI v25.
It enables natural conversation with the computer assistant.

Components:
- STT (Speech-to-Text): Real-time speech recognition
- TTS (Text-to-Speech): Natural speech synthesis
- Intent Understanding: Extract actions from speech
- Full-Duplex Controller: Simultaneous listen/speak

Integration:
- Transformation Model: For reasoning and planning
- Vision Model: For desktop automation
- Memory V4: For learning from interactions
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, AsyncGenerator, Dict, Any
import numpy as np

from .stt.streaming_stt import StreamingSTT, STTConfig, STTModel, TranscriptionEvent
from .tts.streaming_tts import StreamingTTS, TTSConfig, TTSModel, TTSEvent, ResponseTemplates
from .understanding.intent_analyzer import IntentAnalyzer, Intent, ActionType
from .duplex.controller import FullDuplexController, DuplexConfig, DuplexState

logger = logging.getLogger(__name__)


@dataclass
class HearModelConfig:
    """Configuration for Hear Model"""
    # Language
    language: str = "en"  # "en", "vi", "auto"
    
    # STT settings
    stt_model: str = "faster-whisper-large-v3"
    stt_device: str = "cuda"
    
    # TTS settings
    tts_model: str = "edge-tts"
    tts_voice_sample: Optional[str] = None
    
    # Duplex settings
    enable_duplex: bool = True
    allow_interruptions: bool = True
    enable_backchannels: bool = True
    
    # Performance
    target_latency_ms: int = 500


@dataclass
class HearEvent:
    """Event from Hear Model"""
    type: str  # "listening", "transcription", "intent", "speaking", "response", "error"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self):
        return f"HearEvent({self.type}: {self.data})"


class HearModel:
    """
    Dive AI v25 Hear Model
    
    The voice interface that enables natural conversation.
    
    Usage:
        hear = HearModel()
        await hear.initialize()
        
        # Process voice command
        result = await hear.listen_and_respond(audio_data)
        
        # Or use streaming
        async for event in hear.stream(audio_generator):
            print(event)
    """
    
    def __init__(self, config: Optional[HearModelConfig] = None):
        self.config = config or HearModelConfig()
        
        # Components
        self._stt: Optional[StreamingSTT] = None
        self._tts: Optional[StreamingTTS] = None
        self._intent_analyzer: Optional[IntentAnalyzer] = None
        self._duplex: Optional[FullDuplexController] = None
        
        # State
        self._initialized = False
        self._is_listening = False
        self._is_speaking = False
        
        # Callbacks for integration
        self._on_intent: Optional[Callable] = None
        self._on_action: Optional[Callable] = None
        
        # Event queue
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
    async def initialize(self):
        """Initialize all Hear Model components"""
        if self._initialized:
            return
            
        logger.info("🎧 Initializing Hear Model...")
        logger.info(f"   Language: {self.config.language}")
        logger.info(f"   STT: {self.config.stt_model}")
        logger.info(f"   TTS: {self.config.tts_model}")
        
        try:
            # Initialize STT
            stt_config = STTConfig(
                model=STTModel(self.config.stt_model) if self.config.stt_model in [m.value for m in STTModel] else STTModel.FASTER_WHISPER_LARGE,
                language=self.config.language if self.config.language != "auto" else "auto",
                device=self.config.stt_device
            )
            self._stt = StreamingSTT(stt_config)
            await self._stt.initialize()
            
            # Initialize TTS
            tts_config = TTSConfig(
                model=TTSModel(self.config.tts_model) if self.config.tts_model in [m.value for m in TTSModel] else TTSModel.EDGE_TTS,
                language=self.config.language if self.config.language != "auto" else "en",
                voice_sample_path=self.config.tts_voice_sample
            )
            self._tts = StreamingTTS(tts_config)
            await self._tts.initialize()
            
            # Initialize Intent Analyzer
            self._intent_analyzer = IntentAnalyzer(self.config.language)
            
            # Initialize Duplex Controller
            if self.config.enable_duplex:
                duplex_config = DuplexConfig(
                    allow_interruptions=self.config.allow_interruptions,
                    enable_backchannels=self.config.enable_backchannels,
                    language=self.config.language if self.config.language != "auto" else "en"
                )
                self._duplex = FullDuplexController(duplex_config)
                self._duplex.set_components(self._stt, self._tts, self._intent_analyzer)
                
            self._initialized = True
            logger.info("✅ Hear Model initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Hear Model initialization failed: {e}")
            raise
            
    def set_callbacks(
        self,
        on_intent: Optional[Callable] = None,
        on_action: Optional[Callable] = None
    ):
        """
        Set callbacks for integration with other models
        
        Args:
            on_intent: Called when intent is detected (for Transformation Model)
            on_action: Called when action should be executed (for Vision Model)
        """
        self._on_intent = on_intent
        self._on_action = on_action
        
    async def listen(self, audio: np.ndarray) -> TranscriptionEvent:
        """
        Transcribe audio to text
        
        Args:
            audio: Audio data (16kHz, mono, float32)
            
        Returns:
            TranscriptionEvent with text and confidence
        """
        if not self._initialized:
            await self.initialize()
            
        return await self._stt.transcribe(audio)
        
    async def understand(self, text: str) -> Intent:
        """
        Analyze text to extract intent
        
        Args:
            text: Transcribed text
            
        Returns:
            Intent with action and entities
        """
        if not self._initialized:
            await self.initialize()
            
        intent = await self._intent_analyzer.analyze(text)
        
        # Callback
        if self._on_intent:
            self._on_intent(intent)
            
        return intent
        
    async def speak(self, text: str) -> np.ndarray:
        """
        Synthesize text to speech
        
        Args:
            text: Text to speak
            
        Returns:
            Audio data as numpy array
        """
        if not self._initialized:
            await self.initialize()
            
        return await self._tts.speak(text)
        
    async def speak_stream(self, text: str) -> AsyncGenerator[TTSEvent, None]:
        """
        Stream speech synthesis
        
        Args:
            text: Text to speak
            
        Yields:
            TTSEvent with audio chunks
        """
        if not self._initialized:
            await self.initialize()
            
        async for event in self._tts.speak_stream(text):
            yield event
            
    async def listen_and_respond(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Complete listen-understand-respond cycle
        
        Args:
            audio: Audio data (16kHz, mono, float32)
            
        Returns:
            Dict with transcription, intent, response, and response_audio
        """
        if not self._initialized:
            await self.initialize()
            
        # 1. Listen (STT)
        transcription = await self.listen(audio)
        await self._emit_event(HearEvent("transcription", {
            "text": transcription.text,
            "confidence": transcription.confidence,
            "language": transcription.language
        }))
        
        # 2. Understand (Intent)
        intent = await self.understand(transcription.text)
        await self._emit_event(HearEvent("intent", intent.to_dict()))
        
        # 3. Generate Response
        response = self._generate_response(intent)
        
        # 4. Speak (TTS)
        response_audio = await self.speak(response)
        await self._emit_event(HearEvent("response", {"text": response}))
        
        # 5. Trigger Action (if applicable)
        if intent.action not in [ActionType.QUESTION, ActionType.UNKNOWN]:
            if self._on_action:
                self._on_action(intent)
                
        return {
            "transcription": transcription.text,
            "transcription_confidence": transcription.confidence,
            "language": transcription.language,
            "intent": intent.to_dict(),
            "response": response,
            "response_audio": response_audio
        }
        
    async def stream(
        self, 
        audio_stream: AsyncGenerator[np.ndarray, None],
        audio_output: Optional[Callable] = None
    ) -> AsyncGenerator[HearEvent, None]:
        """
        Full streaming mode with duplex support
        
        Args:
            audio_stream: Async generator yielding audio chunks
            audio_output: Callable to play audio (optional)
            
        Yields:
            HearEvent for each stage of processing
        """
        if not self._initialized:
            await self.initialize()
            
        yield HearEvent("listening", {"status": "started"})
        
        try:
            # Stream transcription
            async for transcription in self._stt.transcribe_stream(audio_stream):
                # Emit transcription event
                yield HearEvent("transcription", {
                    "text": transcription.text,
                    "is_final": transcription.is_final,
                    "confidence": transcription.confidence
                })
                
                # Process final transcriptions
                if transcription.is_final and transcription.text.strip():
                    # Understand intent
                    intent = await self.understand(transcription.text)
                    yield HearEvent("intent", intent.to_dict())
                    
                    # Generate and speak response
                    response = self._generate_response(intent)
                    yield HearEvent("speaking", {"text": response})
                    
                    # Stream response audio
                    async for tts_event in self._tts.speak_stream(response):
                        if audio_output:
                            audio_output(tts_event.audio)
                            
                    yield HearEvent("response", {"text": response, "completed": True})
                    
                    # Trigger action
                    if intent.action not in [ActionType.QUESTION, ActionType.UNKNOWN]:
                        yield HearEvent("action", intent.to_dict())
                        if self._on_action:
                            self._on_action(intent)
                            
        except asyncio.CancelledError:
            yield HearEvent("listening", {"status": "cancelled"})
            
        finally:
            yield HearEvent("listening", {"status": "stopped"})
            
    def _generate_response(self, intent: Intent) -> str:
        """Generate appropriate response for intent"""
        lang = intent.language if intent.language else self.config.language
        if lang == "auto":
            lang = "en"
            
        # Action acknowledgment
        if intent.action in [
            ActionType.CLICK, ActionType.TYPE, ActionType.SCROLL,
            ActionType.OPEN, ActionType.CLOSE, ActionType.NAVIGATE,
            ActionType.SEARCH, ActionType.DRAG
        ]:
            return ResponseTemplates.get(
                "acknowledge",
                lang,
                action=intent.action.value,
                target=intent.target or "that"
            )
            
        # Screenshot
        elif intent.action == ActionType.SCREENSHOT:
            return "Taking a screenshot..." if lang == "en" else "Đang chụp màn hình..."
            
        # Confirmation
        elif intent.action == ActionType.CONFIRM:
            return "Got it!" if lang == "en" else "Được rồi!"
            
        # Cancellation
        elif intent.action == ActionType.CANCEL:
            return "Cancelled." if lang == "en" else "Đã hủy."
            
        # Question
        elif intent.action == ActionType.QUESTION:
            return "Let me think about that..." if lang == "en" else "Để tôi suy nghĩ..."
            
        # Unknown
        else:
            return "I understand. How can I help?" if lang == "en" else "Tôi hiểu. Tôi có thể giúp gì?"
            
    async def _emit_event(self, event: HearEvent):
        """Emit event to queue"""
        await self._event_queue.put(event)
        
    async def get_events(self) -> AsyncGenerator[HearEvent, None]:
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
    def is_listening(self) -> bool:
        """Is currently listening"""
        return self._is_listening
        
    @property
    def is_speaking(self) -> bool:
        """Is currently speaking"""
        return self._is_speaking
        
    @property
    def state(self) -> str:
        """Current state"""
        if self._duplex:
            return self._duplex.state.value
        elif self._is_speaking:
            return "speaking"
        elif self._is_listening:
            return "listening"
        return "idle"


# Factory function
async def create_hear_model(
    language: str = "en",
    stt_model: str = "faster-whisper-large-v3",
    tts_model: str = "edge-tts",
    enable_duplex: bool = True
) -> HearModel:
    """
    Create and initialize Hear Model
    
    Args:
        language: Language code ("en", "vi", "auto")
        stt_model: STT model name
        tts_model: TTS model name
        enable_duplex: Enable full-duplex mode
        
    Returns:
        Initialized HearModel instance
    """
    config = HearModelConfig(
        language=language,
        stt_model=stt_model,
        tts_model=tts_model,
        enable_duplex=enable_duplex
    )
    
    model = HearModel(config)
    await model.initialize()
    return model


# Test function
async def test_hear_model():
    """Test Hear Model"""
    print("🧪 Testing Hear Model...")
    print("=" * 60)
    
    # Create model with mock settings (no GPU required)
    config = HearModelConfig(
        language="en",
        stt_model="faster-whisper-large-v3",
        tts_model="edge-tts",
        stt_device="cpu",
        enable_duplex=False
    )
    
    model = HearModel(config)
    
    print("📝 Initializing Hear Model...")
    await model.initialize()
    
    print("\n📝 Testing Intent Understanding...")
    
    test_commands = [
        "Click on the submit button",
        "Open Chrome",
        "Type hello world in the search box",
        "Scroll down",
        "Search for weather forecast",
        "Take a screenshot",
        "What time is it?",
        # Vietnamese
        "Mở Chrome",
        "Bấm vào nút gửi",
        "Tìm kiếm thời tiết",
    ]
    
    for cmd in test_commands:
        intent = await model.understand(cmd)
        response = model._generate_response(intent)
        print(f"\n🎤 \"{cmd}\"")
        print(f"   Intent: {intent.action.value}")
        print(f"   Target: {intent.target}")
        print(f"   Response: {response}")
        
    print("\n" + "=" * 60)
    print("✅ Hear Model test complete!")
    print("\n📋 Summary:")
    print("   - STT: Ready (requires audio input)")
    print("   - TTS: Ready (requires audio output)")
    print("   - Intent: ✅ Working")
    print("   - Duplex: Ready (requires full audio setup)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_hear_model())
