"""
Dive AI v25 - Streaming Speech-to-Text (STT)

Strategic Listen: Real-time speech recognition with streaming output

Models Supported:
- faster-whisper (recommended for local)
- Whisper V3 Large
- Deepgram Nova-3 (cloud)

Features:
- Streaming transcription (partial results)
- Voice Activity Detection (VAD)
- Multi-language support (EN/VI)
- Low latency (~200ms)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Optional, List, Callable
import numpy as np

logger = logging.getLogger(__name__)


class STTModel(Enum):
    """Available STT models"""
    FASTER_WHISPER_LARGE = "faster-whisper-large-v3"
    FASTER_WHISPER_MEDIUM = "faster-whisper-medium"
    FASTER_WHISPER_SMALL = "faster-whisper-small"
    WHISPER_LARGE = "whisper-large-v3"
    DEEPGRAM_NOVA = "deepgram-nova-3"


@dataclass
class TranscriptionEvent:
    """Event emitted during transcription"""
    text: str
    is_final: bool
    confidence: float
    language: str = "en"
    start_time: float = 0.0
    end_time: float = 0.0
    words: List[dict] = field(default_factory=list)
    
    def __str__(self):
        status = "✓" if self.is_final else "..."
        return f"[{status}] {self.text} ({self.confidence:.1%})"


@dataclass
class STTConfig:
    """Configuration for STT"""
    model: STTModel = STTModel.FASTER_WHISPER_LARGE
    language: str = "auto"  # "auto", "en", "vi"
    device: str = "cuda"    # "cuda", "cpu"
    compute_type: str = "float16"  # "float16", "int8", "float32"
    
    # Streaming settings
    chunk_duration: float = 0.5  # seconds
    min_silence_duration: float = 0.3  # seconds
    vad_threshold: float = 0.5
    
    # Performance
    beam_size: int = 5
    best_of: int = 5
    temperature: float = 0.0
    
    # Callbacks
    on_partial: Optional[Callable] = None
    on_final: Optional[Callable] = None


class AudioBuffer:
    """Buffer for accumulating audio chunks"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.buffer = np.array([], dtype=np.float32)
        self.start_time = time.time()
        
    def add(self, chunk: np.ndarray):
        """Add audio chunk to buffer"""
        self.buffer = np.concatenate([self.buffer, chunk])
        
    def get(self) -> np.ndarray:
        """Get current buffer content"""
        return self.buffer.copy()
    
    def clear(self):
        """Clear buffer"""
        self.buffer = np.array([], dtype=np.float32)
        self.start_time = time.time()
        
    @property
    def duration(self) -> float:
        """Duration of buffered audio in seconds"""
        return len(self.buffer) / self.sample_rate
    
    def trim(self, seconds: float):
        """Remove first N seconds from buffer"""
        samples_to_remove = int(seconds * self.sample_rate)
        self.buffer = self.buffer[samples_to_remove:]


class VoiceActivityDetector:
    """
    Voice Activity Detection (VAD)
    
    Detects when user is speaking vs silence
    """
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self._model = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize VAD model (Silero VAD)"""
        if self._initialized:
            return
            
        try:
            import torch
            
            # Load Silero VAD
            model, utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False
            )
            self._model = model
            self._get_speech_timestamps = utils[0]
            self._initialized = True
            logger.info("✅ VAD initialized (Silero)")
            
        except Exception as e:
            logger.warning(f"⚠️ Silero VAD not available, using energy-based VAD: {e}")
            self._initialized = True
            
    def is_speech(self, audio: np.ndarray, sample_rate: int = 16000) -> bool:
        """Check if audio contains speech"""
        if self._model is not None:
            import torch
            audio_tensor = torch.from_numpy(audio).float()
            speech_prob = self._model(audio_tensor, sample_rate).item()
            return speech_prob > self.threshold
        else:
            # Fallback: energy-based detection
            energy = np.sqrt(np.mean(audio ** 2))
            return energy > 0.01
            
    def get_speech_segments(self, audio: np.ndarray, sample_rate: int = 16000) -> List[dict]:
        """Get speech segments with timestamps"""
        if self._model is not None:
            import torch
            audio_tensor = torch.from_numpy(audio).float()
            return self._get_speech_timestamps(
                audio_tensor, 
                self._model, 
                sampling_rate=sample_rate
            )
        return [{"start": 0, "end": len(audio)}]


class StreamingSTT:
    """
    Real-time Streaming Speech-to-Text
    
    Features:
    - Continuous audio streaming
    - Partial transcription results
    - Voice Activity Detection
    - Multi-language support
    """
    
    def __init__(self, config: Optional[STTConfig] = None):
        self.config = config or STTConfig()
        self._model = None
        self._vad = VoiceActivityDetector(self.config.vad_threshold)
        self._buffer = AudioBuffer()
        self._initialized = False
        
        # State
        self._is_listening = False
        self._last_speech_time = 0
        self._accumulated_text = ""
        
    async def initialize(self):
        """Initialize STT model"""
        if self._initialized:
            return
            
        logger.info(f"🎤 Initializing STT: {self.config.model.value}")
        
        try:
            if self.config.model in [
                STTModel.FASTER_WHISPER_LARGE,
                STTModel.FASTER_WHISPER_MEDIUM,
                STTModel.FASTER_WHISPER_SMALL
            ]:
                await self._init_faster_whisper()
            elif self.config.model == STTModel.WHISPER_LARGE:
                await self._init_whisper()
            elif self.config.model == STTModel.DEEPGRAM_NOVA:
                await self._init_deepgram()
                
            await self._vad.initialize()
            self._initialized = True
            
            logger.info(f"✅ STT initialized: {self.config.model.value}")
            logger.info(f"   Device: {self.config.device}")
            logger.info(f"   Language: {self.config.language}")
            
        except Exception as e:
            logger.error(f"❌ STT initialization failed: {e}")
            raise
            
    async def _init_faster_whisper(self):
        """Initialize faster-whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            model_size = self.config.model.value.replace("faster-whisper-", "")
            
            self._model = WhisperModel(
                model_size,
                device=self.config.device,
                compute_type=self.config.compute_type
            )
            self._model_type = "faster_whisper"
            
        except ImportError:
            logger.warning("faster-whisper not installed, using mock model")
            self._model_type = "mock"
            
    async def _init_whisper(self):
        """Initialize OpenAI Whisper model"""
        try:
            import whisper
            
            self._model = whisper.load_model(
                "large-v3",
                device=self.config.device
            )
            self._model_type = "whisper"
            
        except ImportError:
            logger.warning("whisper not installed, using mock model")
            self._model_type = "mock"
            
    async def _init_deepgram(self):
        """Initialize Deepgram client"""
        try:
            from deepgram import Deepgram
            import os
            
            api_key = os.getenv("DEEPGRAM_API_KEY")
            if api_key:
                self._model = Deepgram(api_key)
                self._model_type = "deepgram"
            else:
                logger.warning("DEEPGRAM_API_KEY not set, using mock model")
                self._model_type = "mock"
                
        except ImportError:
            logger.warning("deepgram not installed, using mock model")
            self._model_type = "mock"
            
    async def transcribe(self, audio: np.ndarray) -> TranscriptionEvent:
        """
        Transcribe audio buffer
        
        Args:
            audio: Audio data as numpy array (16kHz, mono, float32)
            
        Returns:
            TranscriptionEvent with transcription result
        """
        if not self._initialized:
            await self.initialize()
            
        start_time = time.time()
        
        if self._model_type == "faster_whisper":
            segments, info = self._model.transcribe(
                audio,
                language=None if self.config.language == "auto" else self.config.language,
                beam_size=self.config.beam_size,
                best_of=self.config.best_of,
                temperature=self.config.temperature,
                vad_filter=True
            )
            
            text = " ".join([seg.text for seg in segments])
            confidence = info.language_probability if hasattr(info, 'language_probability') else 0.9
            language = info.language if hasattr(info, 'language') else "en"
            
        elif self._model_type == "whisper":
            result = self._model.transcribe(
                audio,
                language=None if self.config.language == "auto" else self.config.language
            )
            text = result["text"]
            confidence = 0.9
            language = result.get("language", "en")
            
        else:
            # Mock transcription for testing
            text = "[Mock transcription - install faster-whisper for real STT]"
            confidence = 0.5
            language = "en"
            
        elapsed = time.time() - start_time
        logger.debug(f"   Transcription: {text[:50]}... ({elapsed:.2f}s)")
        
        return TranscriptionEvent(
            text=text.strip(),
            is_final=True,
            confidence=confidence,
            language=language,
            start_time=0,
            end_time=len(audio) / 16000
        )
        
    async def transcribe_stream(
        self, 
        audio_stream: AsyncGenerator[np.ndarray, None]
    ) -> AsyncGenerator[TranscriptionEvent, None]:
        """
        Stream transcription with partial results
        
        Args:
            audio_stream: Async generator yielding audio chunks
            
        Yields:
            TranscriptionEvent for each transcription (partial and final)
        """
        if not self._initialized:
            await self.initialize()
            
        self._is_listening = True
        self._buffer.clear()
        self._accumulated_text = ""
        
        logger.info("🎤 Starting streaming transcription...")
        
        try:
            async for chunk in audio_stream:
                if not self._is_listening:
                    break
                    
                # Add chunk to buffer
                self._buffer.add(chunk)
                
                # Check for speech
                is_speech = self._vad.is_speech(chunk)
                
                if is_speech:
                    self._last_speech_time = time.time()
                    
                # Process buffer when enough audio accumulated
                if self._buffer.duration >= self.config.chunk_duration:
                    # Check if we should emit partial result
                    if is_speech or (time.time() - self._last_speech_time < self.config.min_silence_duration):
                        # Emit partial transcription
                        result = await self.transcribe(self._buffer.get())
                        result.is_final = False
                        
                        if result.text and result.text != self._accumulated_text:
                            yield result
                            
                            if self.config.on_partial:
                                self.config.on_partial(result)
                                
                    else:
                        # Silence detected - emit final result
                        if self._buffer.duration > 0.1:
                            result = await self.transcribe(self._buffer.get())
                            result.is_final = True
                            
                            if result.text:
                                self._accumulated_text = result.text
                                yield result
                                
                                if self.config.on_final:
                                    self.config.on_final(result)
                                    
                            self._buffer.clear()
                            
        except asyncio.CancelledError:
            logger.info("🛑 Streaming transcription cancelled")
            
        finally:
            # Emit final result for remaining buffer
            if self._buffer.duration > 0.1:
                result = await self.transcribe(self._buffer.get())
                result.is_final = True
                if result.text:
                    yield result
                    
            self._is_listening = False
            logger.info("🎤 Streaming transcription stopped")
            
    def stop(self):
        """Stop streaming transcription"""
        self._is_listening = False
        
    async def transcribe_file(self, file_path: str) -> TranscriptionEvent:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            TranscriptionEvent with full transcription
        """
        import soundfile as sf
        
        audio, sample_rate = sf.read(file_path)
        
        # Resample if needed
        if sample_rate != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)
            
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = audio.mean(axis=1)
            
        return await self.transcribe(audio.astype(np.float32))


# Convenience function
async def create_stt(
    model: str = "faster-whisper-large-v3",
    language: str = "auto",
    device: str = "cuda"
) -> StreamingSTT:
    """
    Create and initialize STT instance
    
    Args:
        model: Model name
        language: Language code or "auto"
        device: "cuda" or "cpu"
        
    Returns:
        Initialized StreamingSTT instance
    """
    config = STTConfig(
        model=STTModel(model) if model in [m.value for m in STTModel] else STTModel.FASTER_WHISPER_LARGE,
        language=language,
        device=device
    )
    
    stt = StreamingSTT(config)
    await stt.initialize()
    return stt


# Test function
async def test_stt():
    """Test STT functionality"""
    print("🧪 Testing Streaming STT...")
    print("=" * 50)
    
    stt = StreamingSTT(STTConfig(
        model=STTModel.FASTER_WHISPER_LARGE,
        device="cpu"  # Use CPU for testing
    ))
    
    await stt.initialize()
    
    # Create mock audio stream
    async def mock_audio_stream():
        for _ in range(5):
            # Generate 0.5s of random audio
            chunk = np.random.randn(8000).astype(np.float32) * 0.01
            yield chunk
            await asyncio.sleep(0.5)
            
    print("📝 Transcribing mock audio stream...")
    async for event in stt.transcribe_stream(mock_audio_stream()):
        print(f"   {event}")
        
    print("=" * 50)
    print("✅ STT test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_stt())
