"""
Offline TTS Layer for Dive AI v25
Uses XTTS-v2 for local text-to-speech with voice cloning
"""

from typing import Optional
from dataclasses import dataclass
import os


@dataclass
class TTSResult:
    """TTS result"""
    audio: bytes
    format: str  # mp3, wav, pcm
    sample_rate: int
    duration: float


class OfflineTTS:
    """
    Offline Text-to-Speech using XTTS-v2
    
    Features:
    - Human-like voice quality
    - Voice cloning from 3-second sample
    - 17 languages including Vietnamese
    - Works 100% offline
    - GPU optimized (AMD ROCm compatible)
    """
    
    def __init__(self, device: str = "cuda"):
        """
        Initialize offline TTS
        
        Args:
            device: Device to use (cuda, cpu)
        """
        self.device = device
        self.model = None
        self.speaker_wav = None
        
        print(f"🔊 Initializing Offline TTS (XTTS-v2)...")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize XTTS-v2 model"""
        try:
            from TTS.api import TTS
            
            print(f"  📥 Loading XTTS-v2 model...")
            self.model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                device=self.device,
                progress_bar=True,
                gpu=self.device == "cuda"
            )
            print(f"  ✅ TTS model loaded successfully")
        
        except ImportError:
            print("  ❌ TTS not installed")
            print("  Install with: pip install TTS")
            raise
        except Exception as e:
            print(f"  ❌ Error loading model: {e}")
            # Try CPU fallback
            try:
                from TTS.api import TTS
                self.device = "cpu"
                self.model = TTS(
                    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                    device="cpu",
                    progress_bar=True,
                    gpu=False
                )
                print(f"  ✅ TTS model loaded on CPU (slower)")
            except Exception as cpu_error:
                print(f"  ❌ CPU fallback failed: {cpu_error}")
                raise
    
    async def speak(
        self,
        text: str,
        language: str = "en",
        speaker_wav: Optional[str] = None,
        speed: float = 1.0
    ) -> TTSResult:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            language: Language code (en, vi, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko)
            speaker_wav: Path to speaker WAV file for voice cloning (3+ seconds)
            speed: Speech speed (0.5 - 2.0)
        
        Returns:
            TTSResult with audio bytes
        """
        try:
            import io
            import soundfile as sf
            import numpy as np
            
            # Use provided speaker or default
            if speaker_wav is None:
                speaker_wav = self.speaker_wav
            
            # Generate speech
            print(f"  🎙️  Generating speech ({language})...")
            wav = self.model.tts(
                text=text,
                speaker_wav=speaker_wav,
                language=language,
                speed=speed
            )
            
            # Convert to bytes
            buffer = io.BytesIO()
            sf.write(buffer, wav, self.model.synthesizer.output_sample_rate, format='WAV')
            audio_bytes = buffer.getvalue()
            
            # Calculate duration
            duration = len(wav) / self.model.synthesizer.output_sample_rate
            
            return TTSResult(
                audio=audio_bytes,
                format="wav",
                sample_rate=self.model.synthesizer.output_sample_rate,
                duration=duration
            )
        
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            return TTSResult(
                audio=b"",
                format="wav",
                sample_rate=24000,
                duration=0.0
            )
    
    async def clone_voice(self, speaker_wav_path: str) -> bool:
        """
        Load speaker voice for cloning
        
        Args:
            speaker_wav_path: Path to WAV file (3+ seconds recommended)
        
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(speaker_wav_path):
                print(f"❌ Speaker file not found: {speaker_wav_path}")
                return False
            
            self.speaker_wav = speaker_wav_path
            print(f"✅ Voice cloning loaded: {speaker_wav_path}")
            return True
        
        except Exception as e:
            print(f"❌ Voice cloning error: {e}")
            return False


class OfflineTTSStreaming:
    """
    Streaming TTS for real-time speech generation
    """
    
    def __init__(self, device: str = "cuda"):
        self.tts = OfflineTTS(device)
    
    async def speak_streaming(
        self,
        text: str,
        language: str = "en",
        speaker_wav: Optional[str] = None
    ):
        """
        Stream text-to-speech by splitting into sentences
        
        Args:
            text: Text to convert
            language: Language code
            speaker_wav: Speaker WAV file for voice cloning
        
        Yields:
            TTSResult chunks
        """
        # Split into sentences
        sentences = text.split(". ")
        
        for sentence in sentences:
            if sentence.strip():
                result = await self.tts.speak(
                    sentence + ".",
                    language=language,
                    speaker_wav=speaker_wav
                )
                yield result


class EdgeTTSFallback:
    """
    Edge TTS Fallback (Free Microsoft TTS)
    Used when XTTS-v2 fails or for quick responses
    """
    
    def __init__(self):
        self.client = None
        print(f"🔊 Initializing Edge TTS Fallback...")
        self._initialize()
    
    def _initialize(self):
        """Initialize Edge TTS"""
        try:
            import edge_tts
            print(f"  ✅ Edge TTS available (fallback)")
        except ImportError:
            print(f"  ⚠️  Edge TTS not installed (optional fallback)")
            print(f"  Install with: pip install edge-tts")
    
    async def speak(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> TTSResult:
        """
        Generate speech using Edge TTS
        
        Args:
            text: Text to convert
            language: Language code
            voice: Voice name (auto-selected if None)
        
        Returns:
            TTSResult
        """
        try:
            import edge_tts
            import io
            
            # Select voice based on language
            voices = {
                "en": "en-US-AriaNeural",
                "vi": "vi-VN-HoaiMyNeural",
                "es": "es-ES-AlvaroNeural",
                "fr": "fr-FR-HenriNeural",
                "de": "de-DE-ConradNeural",
                "it": "it-IT-DiegoNeural",
                "pt": "pt-BR-AntonioNeural",
                "zh": "zh-CN-YunxiNeural",
                "ja": "ja-JP-KeitaNeural",
                "ko": "ko-KR-InJoonNeural",
            }
            
            selected_voice = voice or voices.get(language, "en-US-AriaNeural")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, selected_voice)
            
            # Collect audio
            audio_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_buffer.write(chunk["data"])
            
            audio_bytes = audio_buffer.getvalue()
            
            return TTSResult(
                audio=audio_bytes,
                format="mp3",
                sample_rate=24000,
                duration=len(audio_bytes) / 24000 / 2  # Approximate
            )
        
        except Exception as e:
            print(f"❌ Edge TTS Error: {e}")
            return TTSResult(
                audio=b"",
                format="mp3",
                sample_rate=24000,
                duration=0.0
            )


# Example usage
async def main():
    """Test offline TTS"""
    
    tts = OfflineTTS(device="cuda")
    
    print("\n🔊 Testing Offline TTS...")
    
    # Test basic speech
    result = await tts.speak(
        "Hello, this is Dive AI v25 speaking to you offline.",
        language="en"
    )
    print(f"✅ Generated audio: {len(result.audio)} bytes")
    print(f"✅ Duration: {result.duration:.2f} seconds")
    
    # Test Vietnamese
    result_vi = await tts.speak(
        "Xin chào, đây là Dive AI v25 nói chuyện với bạn ngoại tuyến.",
        language="vi"
    )
    print(f"✅ Vietnamese audio: {len(result_vi.audio)} bytes")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
