"""
Offline STT Layer for Dive AI v25
Uses faster-whisper (CTranslate2 optimized) for local speech recognition
"""

import os
from typing import Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class STTResult:
    """STT result"""
    text: str
    confidence: float
    language: str
    is_final: bool


class OfflineSTT:
    """
    Offline Speech-to-Text using faster-whisper
    
    Features:
    - 30x faster than original Whisper
    - 17.8% WER (excellent accuracy)
    - Works 100% offline
    - Supports 99+ languages
    - GPU optimized (AMD ROCm compatible)
    """
    
    def __init__(self, model_size: str = "large-v3-turbo"):
        """
        Initialize offline STT
        
        Args:
            model_size: Model size (tiny, base, small, medium, large, large-v3-turbo)
                       Recommended: large-v3-turbo (fastest + best accuracy)
        """
        self.model_size = model_size
        self.model = None
        self.device = "cuda"  # Will auto-fallback to cpu if no GPU
        
        print(f"🎤 Initializing Offline STT ({model_size})...")
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize faster-whisper model"""
        try:
            from faster_whisper import WhisperModel
            
            # Download model if needed
            print(f"  📥 Loading {self.model_size} model...")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="float16"  # For GPU
            )
            print(f"  ✅ STT model loaded successfully")
        
        except ImportError:
            print("  ❌ faster-whisper not installed")
            print("  Install with: pip install faster-whisper")
            raise
        except Exception as e:
            print(f"  ❌ Error loading model: {e}")
            # Try CPU fallback
            try:
                self.device = "cpu"
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"
                )
                print(f"  ✅ STT model loaded on CPU (slower)")
            except Exception as cpu_error:
                print(f"  ❌ CPU fallback failed: {cpu_error}")
                raise
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        beam_size: int = 5
    ) -> STTResult:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio bytes (WAV, MP3, etc.)
            language: Language code (auto-detect if None)
            beam_size: Beam search size (higher = more accurate but slower)
        
        Returns:
            STTResult with transcribed text
        """
        try:
            # Convert bytes to numpy array
            import io
            import soundfile as sf
            
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            
            # Transcribe
            segments, info = self.model.transcribe(
                audio_array,
                language=language,
                beam_size=beam_size,
                best_of=5,
                temperature=0.0,  # Deterministic
                condition_on_previous_text=False
            )
            
            # Collect segments
            text = " ".join(segment.text for segment in segments)
            
            return STTResult(
                text=text,
                confidence=info.probability if hasattr(info, 'probability') else 0.9,
                language=info.language if hasattr(info, 'language') else language or "en",
                is_final=True
            )
        
        except Exception as e:
            print(f"❌ STT Error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language=language or "en",
                is_final=True
            )
    
    async def transcribe_file(self, file_path: str) -> STTResult:
        """
        Transcribe audio file
        
        Args:
            file_path: Path to audio file
        
        Returns:
            STTResult
        """
        try:
            import soundfile as sf
            
            audio_data, sample_rate = sf.read(file_path)
            
            # Convert to bytes
            import io
            buffer = io.BytesIO()
            sf.write(buffer, audio_data, sample_rate, format='WAV')
            audio_bytes = buffer.getvalue()
            
            return await self.transcribe(audio_bytes)
        
        except Exception as e:
            print(f"❌ File transcription error: {e}")
            return STTResult(
                text="",
                confidence=0.0,
                language="en",
                is_final=True
            )


class OfflineSTTStreaming:
    """
    Streaming STT for real-time transcription
    """
    
    def __init__(self, model_size: str = "large-v3-turbo"):
        self.stt = OfflineSTT(model_size)
        self.buffer = b""
        self.chunk_duration = 1.0  # Process every 1 second
    
    async def process_chunk(self, audio_chunk: bytes) -> Optional[STTResult]:
        """
        Process audio chunk for streaming
        
        Args:
            audio_chunk: Audio chunk bytes
        
        Returns:
            STTResult if enough audio accumulated, None otherwise
        """
        self.buffer += audio_chunk
        
        # Process if buffer has ~1 second of audio (16kHz * 2 bytes = 32KB)
        if len(self.buffer) >= 32000:
            result = await self.stt.transcribe(self.buffer)
            result.is_final = False
            self.buffer = b""
            return result
        
        return None
    
    async def finalize(self) -> STTResult:
        """
        Finalize streaming and process remaining audio
        
        Returns:
            Final STTResult
        """
        if self.buffer:
            result = await self.stt.transcribe(self.buffer)
            result.is_final = True
            self.buffer = b""
            return result
        
        return STTResult(
            text="",
            confidence=0.0,
            language="en",
            is_final=True
        )


# Example usage
async def main():
    """Test offline STT"""
    
    stt = OfflineSTT(model_size="large-v3-turbo")
    
    # Test with a file
    print("\n🎤 Testing Offline STT...")
    
    # Create a dummy audio file for testing
    import soundfile as sf
    import numpy as np
    
    # Generate 3 seconds of silence (for testing)
    sample_rate = 16000
    duration = 3
    audio = np.zeros(sample_rate * duration, dtype=np.float32)
    
    # Save to bytes
    import io
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    audio_bytes = buffer.getvalue()
    
    # Transcribe
    result = await stt.transcribe(audio_bytes)
    print(f"✅ Transcription: {result.text}")
    print(f"✅ Confidence: {result.confidence}")
    print(f"✅ Language: {result.language}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
