"""
Dive AI v25 - Streaming Text-to-Speech (TTS)

Natural Speak: Real-time speech synthesis with streaming output

Models Supported:
- XTTS-v2 (recommended, voice cloning)
- Coqui TTS
- Edge TTS (cloud, fastest)
- OpenAI TTS (cloud, best quality)

Features:
- Streaming audio output
- Voice cloning (6-second sample)
- Multi-language support (EN/VI)
- Low latency (~200ms to first byte)
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Optional, List, Union
from pathlib import Path
import numpy as np
import io

logger = logging.getLogger(__name__)


class TTSModel(Enum):
    """Available TTS models"""
    XTTS_V2 = "xtts-v2"
    COQUI_TTS = "coqui-tts"
    EDGE_TTS = "edge-tts"
    OPENAI_TTS = "openai-tts"


class TTSVoice(Enum):
    """Pre-defined voices"""
    # English voices
    EN_MALE_1 = "en_male_1"
    EN_FEMALE_1 = "en_female_1"
    EN_MALE_2 = "en_male_2"
    EN_FEMALE_2 = "en_female_2"
    
    # Vietnamese voices
    VI_MALE_1 = "vi_male_1"
    VI_FEMALE_1 = "vi_female_1"
    
    # Edge TTS voices
    EDGE_EN_JENNY = "en-US-JennyNeural"
    EDGE_EN_GUY = "en-US-GuyNeural"
    EDGE_VI_HOAI = "vi-VN-HoaiMyNeural"
    EDGE_VI_NAM = "vi-VN-NamMinhNeural"


@dataclass
class TTSConfig:
    """Configuration for TTS"""
    model: TTSModel = TTSModel.XTTS_V2
    voice: Union[TTSVoice, str] = TTSVoice.EN_FEMALE_1
    language: str = "en"  # "en", "vi"
    
    # Voice cloning
    voice_sample_path: Optional[str] = None
    
    # Audio settings
    sample_rate: int = 24000
    
    # Performance
    speed: float = 1.0
    pitch: float = 1.0
    
    # Streaming
    chunk_size: int = 4096
    
    # Device
    device: str = "cuda"


@dataclass
class TTSEvent:
    """Event emitted during TTS"""
    audio: np.ndarray
    sample_rate: int
    is_final: bool
    text_chunk: str = ""
    duration: float = 0.0
    
    def to_bytes(self) -> bytes:
        """Convert to WAV bytes"""
        import struct
        
        # Convert to 16-bit PCM
        audio_int16 = (self.audio * 32767).astype(np.int16)
        
        # Create WAV header
        num_channels = 1
        bits_per_sample = 16
        byte_rate = self.sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = len(audio_int16) * 2
        
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            36 + data_size,
            b'WAVE',
            b'fmt ',
            16,
            1,  # PCM
            num_channels,
            self.sample_rate,
            byte_rate,
            block_align,
            bits_per_sample,
            b'data',
            data_size
        )
        
        return header + audio_int16.tobytes()


class StreamingTTS:
    """
    Real-time Streaming Text-to-Speech
    
    Features:
    - Streaming audio generation
    - Voice cloning
    - Multi-language support
    - Low latency
    """
    
    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._model = None
        self._voice_embedding = None
        self._initialized = False
        
        # State
        self._is_speaking = False
        self._current_text = ""
        
    async def initialize(self):
        """Initialize TTS model"""
        if self._initialized:
            return
            
        logger.info(f"🔊 Initializing TTS: {self.config.model.value}")
        
        try:
            if self.config.model == TTSModel.XTTS_V2:
                await self._init_xtts()
            elif self.config.model == TTSModel.COQUI_TTS:
                await self._init_coqui()
            elif self.config.model == TTSModel.EDGE_TTS:
                await self._init_edge()
            elif self.config.model == TTSModel.OPENAI_TTS:
                await self._init_openai()
                
            # Load voice sample if provided
            if self.config.voice_sample_path:
                await self._load_voice_sample()
                
            self._initialized = True
            
            logger.info(f"✅ TTS initialized: {self.config.model.value}")
            logger.info(f"   Voice: {self.config.voice}")
            logger.info(f"   Language: {self.config.language}")
            
        except Exception as e:
            logger.error(f"❌ TTS initialization failed: {e}")
            raise
            
    async def _init_xtts(self):
        """Initialize XTTS-v2 model"""
        try:
            from TTS.api import TTS
            
            self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            if self.config.device == "cuda":
                self._model.to("cuda")
                
            self._model_type = "xtts"
            
        except ImportError:
            logger.warning("TTS (Coqui) not installed, using mock model")
            self._model_type = "mock"
            
    async def _init_coqui(self):
        """Initialize Coqui TTS model"""
        try:
            from TTS.api import TTS
            
            self._model = TTS("tts_models/en/ljspeech/tacotron2-DDC")
            self._model_type = "coqui"
            
        except ImportError:
            logger.warning("TTS (Coqui) not installed, using mock model")
            self._model_type = "mock"
            
    async def _init_edge(self):
        """Initialize Edge TTS (Microsoft)"""
        try:
            import edge_tts
            self._model_type = "edge"
            
        except ImportError:
            logger.warning("edge-tts not installed, using mock model")
            self._model_type = "mock"
            
    async def _init_openai(self):
        """Initialize OpenAI TTS"""
        try:
            import openai
            import os
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._model = openai.OpenAI(api_key=api_key)
                self._model_type = "openai"
            else:
                logger.warning("OPENAI_API_KEY not set, using mock model")
                self._model_type = "mock"
                
        except ImportError:
            logger.warning("openai not installed, using mock model")
            self._model_type = "mock"
            
    async def _load_voice_sample(self):
        """Load voice sample for cloning"""
        if not self.config.voice_sample_path:
            return
            
        path = Path(self.config.voice_sample_path)
        if not path.exists():
            logger.warning(f"Voice sample not found: {path}")
            return
            
        logger.info(f"🎤 Loading voice sample: {path}")
        
        if self._model_type == "xtts":
            # XTTS uses the sample path directly
            self._voice_embedding = str(path)
        else:
            # Other models may need different handling
            self._voice_embedding = str(path)
            
    async def clone_voice(self, audio_path: str) -> bool:
        """
        Clone voice from audio sample
        
        Args:
            audio_path: Path to 6-second audio sample
            
        Returns:
            True if successful
        """
        if not self._initialized:
            await self.initialize()
            
        self.config.voice_sample_path = audio_path
        await self._load_voice_sample()
        
        return self._voice_embedding is not None
        
    async def speak(self, text: str) -> np.ndarray:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio as numpy array
        """
        if not self._initialized:
            await self.initialize()
            
        start_time = time.time()
        self._current_text = text
        
        if self._model_type == "xtts":
            audio = await self._speak_xtts(text)
        elif self._model_type == "coqui":
            audio = await self._speak_coqui(text)
        elif self._model_type == "edge":
            audio = await self._speak_edge(text)
        elif self._model_type == "openai":
            audio = await self._speak_openai(text)
        else:
            audio = await self._speak_mock(text)
            
        elapsed = time.time() - start_time
        logger.debug(f"   TTS: {text[:30]}... ({elapsed:.2f}s)")
        
        return audio
        
    async def _speak_xtts(self, text: str) -> np.ndarray:
        """Synthesize with XTTS-v2"""
        if self._voice_embedding:
            wav = self._model.tts(
                text=text,
                speaker_wav=self._voice_embedding,
                language=self.config.language
            )
        else:
            wav = self._model.tts(
                text=text,
                language=self.config.language
            )
        return np.array(wav, dtype=np.float32)
        
    async def _speak_coqui(self, text: str) -> np.ndarray:
        """Synthesize with Coqui TTS"""
        wav = self._model.tts(text=text)
        return np.array(wav, dtype=np.float32)
        
    async def _speak_edge(self, text: str) -> np.ndarray:
        """Synthesize with Edge TTS"""
        import edge_tts
        
        # Select voice based on language
        if isinstance(self.config.voice, TTSVoice):
            voice = self.config.voice.value
        else:
            voice = self.config.voice
            
        if not voice.startswith("en-") and not voice.startswith("vi-"):
            # Use default Edge voice
            voice = "en-US-JennyNeural" if self.config.language == "en" else "vi-VN-HoaiMyNeural"
            
        communicate = edge_tts.Communicate(text, voice)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        # Convert MP3 to numpy array
        import io
        from pydub import AudioSegment
        
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
        samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        samples = samples / 32768.0  # Normalize
        
        return samples
        
    async def _speak_openai(self, text: str) -> np.ndarray:
        """Synthesize with OpenAI TTS"""
        response = self._model.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        # Convert to numpy array
        audio_data = response.content
        
        from pydub import AudioSegment
        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
        samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
        samples = samples / 32768.0
        
        return samples
        
    async def _speak_mock(self, text: str) -> np.ndarray:
        """Generate mock audio for testing"""
        # Generate silence with some noise
        duration = len(text) * 0.05  # ~50ms per character
        samples = int(duration * self.config.sample_rate)
        audio = np.random.randn(samples).astype(np.float32) * 0.001
        return audio
        
    async def speak_stream(self, text: str) -> AsyncGenerator[TTSEvent, None]:
        """
        Stream audio output as it's generated
        
        Args:
            text: Text to synthesize
            
        Yields:
            TTSEvent with audio chunks
        """
        if not self._initialized:
            await self.initialize()
            
        self._is_speaking = True
        self._current_text = text
        
        logger.info(f"🔊 Streaming TTS: {text[:50]}...")
        
        try:
            if self._model_type == "edge":
                # Edge TTS supports native streaming
                async for event in self._stream_edge(text):
                    if not self._is_speaking:
                        break
                    yield event
            else:
                # Other models: generate full audio then chunk
                audio = await self.speak(text)
                
                # Stream in chunks
                chunk_samples = self.config.chunk_size
                for i in range(0, len(audio), chunk_samples):
                    if not self._is_speaking:
                        break
                        
                    chunk = audio[i:i + chunk_samples]
                    is_final = (i + chunk_samples >= len(audio))
                    
                    yield TTSEvent(
                        audio=chunk,
                        sample_rate=self.config.sample_rate,
                        is_final=is_final,
                        duration=len(chunk) / self.config.sample_rate
                    )
                    
                    # Small delay to simulate streaming
                    await asyncio.sleep(0.01)
                    
        except asyncio.CancelledError:
            logger.info("🛑 TTS streaming cancelled")
            
        finally:
            self._is_speaking = False
            logger.info("🔊 TTS streaming stopped")
            
    async def _stream_edge(self, text: str) -> AsyncGenerator[TTSEvent, None]:
        """Native streaming with Edge TTS"""
        import edge_tts
        
        voice = "en-US-JennyNeural" if self.config.language == "en" else "vi-VN-HoaiMyNeural"
        communicate = edge_tts.Communicate(text, voice)
        
        audio_buffer = b""
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer += chunk["data"]
                
                # Yield when we have enough data
                if len(audio_buffer) >= 4096:
                    # Convert chunk to numpy
                    from pydub import AudioSegment
                    try:
                        audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_buffer))
                        samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                        samples = samples / 32768.0
                        
                        yield TTSEvent(
                            audio=samples,
                            sample_rate=24000,
                            is_final=False
                        )
                        
                        audio_buffer = b""
                    except:
                        pass  # Not enough data for valid MP3
                        
        # Yield remaining audio
        if audio_buffer:
            from pydub import AudioSegment
            try:
                audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_buffer))
                samples = np.array(audio_segment.get_array_of_samples(), dtype=np.float32)
                samples = samples / 32768.0
                
                yield TTSEvent(
                    audio=samples,
                    sample_rate=24000,
                    is_final=True
                )
            except:
                pass
                
    def stop(self):
        """Stop current speech"""
        self._is_speaking = False
        
    async def save_to_file(self, text: str, output_path: str):
        """
        Save synthesized speech to file
        
        Args:
            text: Text to synthesize
            output_path: Output file path (.wav)
        """
        audio = await self.speak(text)
        
        import soundfile as sf
        sf.write(output_path, audio, self.config.sample_rate)
        
        logger.info(f"💾 Saved audio to: {output_path}")


# Convenience function
async def create_tts(
    model: str = "edge-tts",
    language: str = "en",
    voice_sample: Optional[str] = None
) -> StreamingTTS:
    """
    Create and initialize TTS instance
    
    Args:
        model: Model name
        language: Language code
        voice_sample: Path to voice sample for cloning
        
    Returns:
        Initialized StreamingTTS instance
    """
    config = TTSConfig(
        model=TTSModel(model) if model in [m.value for m in TTSModel] else TTSModel.EDGE_TTS,
        language=language,
        voice_sample_path=voice_sample
    )
    
    tts = StreamingTTS(config)
    await tts.initialize()
    return tts


# Response templates for Hear Model
class ResponseTemplates:
    """Pre-defined response templates in multiple languages"""
    
    TEMPLATES = {
        "en": {
            "acknowledge": [
                "I'll {action} {target} now...",
                "Working on {action}ing {target}...",
                "Let me {action} {target} for you...",
                "On it! {action}ing {target}..."
            ],
            "progress": [
                "{action}ing {target}...",
                "Almost there...",
                "Processing...",
                "Just a moment..."
            ],
            "confirm": [
                "Done! {result}",
                "All set! {result}",
                "Completed! {result}",
                "There you go! {result}"
            ],
            "error": [
                "Sorry, I couldn't {action}. {reason}",
                "I ran into an issue: {reason}",
                "Something went wrong: {reason}"
            ],
            "clarify": [
                "Did you mean {options}?",
                "I found multiple options: {options}. Which one?",
                "Could you clarify? I see {options}."
            ],
            "backchannel": [
                "uh-huh",
                "okay",
                "got it",
                "I see",
                "right"
            ]
        },
        "vi": {
            "acknowledge": [
                "Tôi sẽ {action} {target} ngay...",
                "Đang {action} {target}...",
                "Để tôi {action} {target} cho bạn...",
                "Được rồi! Đang {action} {target}..."
            ],
            "progress": [
                "Đang {action} {target}...",
                "Sắp xong rồi...",
                "Đang xử lý...",
                "Chờ một chút..."
            ],
            "confirm": [
                "Xong! {result}",
                "Hoàn thành! {result}",
                "Đã xong! {result}",
                "Đây rồi! {result}"
            ],
            "error": [
                "Xin lỗi, tôi không thể {action}. {reason}",
                "Có lỗi xảy ra: {reason}",
                "Có vấn đề: {reason}"
            ],
            "clarify": [
                "Bạn có ý là {options}?",
                "Tôi thấy nhiều lựa chọn: {options}. Bạn chọn cái nào?",
                "Bạn có thể nói rõ hơn? Tôi thấy {options}."
            ],
            "backchannel": [
                "ừ",
                "được",
                "hiểu rồi",
                "à",
                "vâng"
            ]
        }
    }
    
    @classmethod
    def get(cls, category: str, language: str = "en", **kwargs) -> str:
        """Get a response from template"""
        import random
        
        templates = cls.TEMPLATES.get(language, cls.TEMPLATES["en"])
        options = templates.get(category, ["..."])
        
        template = random.choice(options)
        
        try:
            return template.format(**kwargs)
        except KeyError:
            return template


# Test function
async def test_tts():
    """Test TTS functionality"""
    print("🧪 Testing Streaming TTS...")
    print("=" * 50)
    
    tts = StreamingTTS(TTSConfig(
        model=TTSModel.EDGE_TTS,
        language="en"
    ))
    
    await tts.initialize()
    
    # Test basic synthesis
    text = "Hello! I am Dive AI version 25. How can I help you today?"
    print(f"📝 Synthesizing: {text}")
    
    audio = await tts.speak(text)
    print(f"   Generated {len(audio)} samples ({len(audio)/24000:.2f}s)")
    
    # Test streaming
    print("\n📝 Testing streaming...")
    async for event in tts.speak_stream("This is a streaming test."):
        print(f"   Chunk: {len(event.audio)} samples, final={event.is_final}")
        
    # Test response templates
    print("\n📝 Testing response templates...")
    print(f"   EN: {ResponseTemplates.get('acknowledge', 'en', action='open', target='Chrome')}")
    print(f"   VI: {ResponseTemplates.get('acknowledge', 'vi', action='mở', target='Chrome')}")
    
    print("=" * 50)
    print("✅ TTS test complete!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_tts())
