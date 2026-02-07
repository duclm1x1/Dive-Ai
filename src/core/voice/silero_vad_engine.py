"""
Silero VAD Engine - Technique #1 (10/10 Priority)

Enterprise-grade Voice Activity Detection with <1ms latency per 30ms audio chunk.
Supports 6000+ languages with high accuracy.

Features:
- <1ms processing time per chunk
- 8kHz and 16kHz sampling rates
- Configurable sensitivity
- Real-time speech probability
- Low memory footprint (~2MB model)
"""

import torch
import numpy as np
from typing import Optional, List, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VADConfig:
    """Configuration for Silero VAD"""
    sampling_rate: int = 16000  # 8000 or 16000
    threshold: float = 0.5  # Speech probability threshold (0.0-1.0)
    min_speech_duration_ms: int = 250  # Minimum speech duration
    min_silence_duration_ms: int = 100  # Minimum silence duration
    window_size_samples: int = 512  # Processing window size
    speech_pad_ms: int = 30  # Padding around speech segments


class SileroVADEngine:
    """
    Silero VAD Engine for real-time voice activity detection.
    
    Performance:
    - Latency: <1ms per 30ms chunk (single CPU thread)
    - Accuracy: >95% on speech detection
    - Memory: ~2MB model size
    - Languages: 6000+ supported
    """
    
    def __init__(self, config: Optional[VADConfig] = None):
        """
        Initialize Silero VAD engine.
        
        Args:
            config: VAD configuration (uses defaults if None)
        """
        self.config = config or VADConfig()
        self.model = None
        self.utils = None
        self._is_initialized = False
        
        # State tracking
        self.is_speech = False
        self.speech_start_time = None
        self.silence_start_time = None
        self.current_speech_duration = 0
        self.current_silence_duration = 0
        
        # Statistics
        self.total_chunks_processed = 0
        self.total_speech_detected = 0
        self.total_processing_time = 0
        
        logger.info(f"Silero VAD Engine initialized with config: {self.config}")
    
    def initialize(self) -> bool:
        """
        Load Silero VAD model.
        
        Returns:
            True if initialization successful
        """
        try:
            import time
            start_time = time.time()
            
            # Load model from torch.hub
            self.model, self.utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False,
                onnx=False
            )
            
            # Set to evaluation mode
            self.model.eval()
            
            # Extract utils
            (self.get_speech_timestamps,
             self.save_audio,
             self.read_audio,
             self.VADIterator,
             self.collect_chunks) = self.utils
            
            self._is_initialized = True
            
            load_time = time.time() - start_time
            logger.info(f"Silero VAD model loaded successfully in {load_time:.3f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Silero VAD: {e}")
            return False
    
    def process_chunk(self, audio_chunk: np.ndarray) -> Tuple[bool, float]:
        """
        Process single audio chunk and detect voice activity.
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            Tuple of (is_speech: bool, probability: float)
        """
        if not self._is_initialized:
            logger.warning("VAD not initialized, initializing now...")
            if not self.initialize():
                return False, 0.0
        
        try:
            import time
            start_time = time.time()
            
            # Convert to torch tensor
            if isinstance(audio_chunk, np.ndarray):
                audio_tensor = torch.from_numpy(audio_chunk).float()
            else:
                audio_tensor = audio_chunk
            
            # Ensure correct shape
            if audio_tensor.dim() == 1:
                audio_tensor = audio_tensor.unsqueeze(0)
            
            # Get speech probability
            with torch.no_grad():
                speech_prob = self.model(audio_tensor, self.config.sampling_rate).item()
            
            # Determine if speech based on threshold
            is_speech = speech_prob >= self.config.threshold
            
            # Update statistics
            self.total_chunks_processed += 1
            if is_speech:
                self.total_speech_detected += 1
            
            processing_time = time.time() - start_time
            self.total_processing_time += processing_time
            
            # Log performance every 1000 chunks
            if self.total_chunks_processed % 1000 == 0:
                avg_time = self.total_processing_time / self.total_chunks_processed
                speech_ratio = self.total_speech_detected / self.total_chunks_processed
                logger.debug(
                    f"VAD Stats: {self.total_chunks_processed} chunks, "
                    f"avg time: {avg_time*1000:.3f}ms, "
                    f"speech ratio: {speech_ratio:.2%}"
                )
            
            return is_speech, speech_prob
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            return False, 0.0
    
    def get_speech_timestamps_from_audio(
        self,
        audio: np.ndarray,
        return_seconds: bool = True
    ) -> List[dict]:
        """
        Get speech timestamps from full audio.
        
        Args:
            audio: Full audio as numpy array
            return_seconds: Return timestamps in seconds (vs samples)
            
        Returns:
            List of speech segments with start/end timestamps
        """
        if not self._is_initialized:
            if not self.initialize():
                return []
        
        try:
            # Convert to torch tensor
            if isinstance(audio, np.ndarray):
                audio_tensor = torch.from_numpy(audio).float()
            else:
                audio_tensor = audio
            
            # Get speech timestamps
            speech_timestamps = self.get_speech_timestamps(
                audio_tensor,
                self.model,
                sampling_rate=self.config.sampling_rate,
                threshold=self.config.threshold,
                min_speech_duration_ms=self.config.min_speech_duration_ms,
                min_silence_duration_ms=self.config.min_silence_duration_ms,
                window_size_samples=self.config.window_size_samples,
                speech_pad_ms=self.config.speech_pad_ms,
                return_seconds=return_seconds
            )
            
            return speech_timestamps
            
        except Exception as e:
            logger.error(f"Error getting speech timestamps: {e}")
            return []
    
    def detect_speech_start(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if speech is starting in this chunk.
        
        Args:
            audio_chunk: Audio data
            
        Returns:
            True if speech is starting
        """
        is_speech, prob = self.process_chunk(audio_chunk)
        
        if is_speech and not self.is_speech:
            # Speech starting
            self.is_speech = True
            self.speech_start_time = self.total_chunks_processed
            self.silence_start_time = None
            logger.debug(f"Speech started (prob: {prob:.3f})")
            return True
        
        return False
    
    def detect_speech_end(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if speech is ending in this chunk.
        
        Args:
            audio_chunk: Audio data
            
        Returns:
            True if speech is ending
        """
        is_speech, prob = self.process_chunk(audio_chunk)
        
        if not is_speech and self.is_speech:
            # Potential speech ending
            if self.silence_start_time is None:
                self.silence_start_time = self.total_chunks_processed
            
            # Calculate silence duration
            silence_chunks = self.total_chunks_processed - self.silence_start_time
            silence_ms = (silence_chunks * self.config.window_size_samples / 
                         self.config.sampling_rate * 1000)
            
            if silence_ms >= self.config.min_silence_duration_ms:
                # Speech ended
                self.is_speech = False
                speech_chunks = self.silence_start_time - self.speech_start_time
                speech_ms = (speech_chunks * self.config.window_size_samples / 
                           self.config.sampling_rate * 1000)
                logger.debug(f"Speech ended (duration: {speech_ms:.0f}ms, prob: {prob:.3f})")
                return True
        
        elif is_speech:
            # Reset silence tracking
            self.silence_start_time = None
        
        return False
    
    def is_speaking(self) -> bool:
        """
        Check if currently in speech state.
        
        Returns:
            True if currently speaking
        """
        return self.is_speech
    
    def reset(self):
        """Reset VAD state."""
        self.is_speech = False
        self.speech_start_time = None
        self.silence_start_time = None
        self.current_speech_duration = 0
        self.current_silence_duration = 0
        logger.debug("VAD state reset")
    
    def get_statistics(self) -> dict:
        """
        Get VAD statistics.
        
        Returns:
            Dictionary with statistics
        """
        if self.total_chunks_processed == 0:
            return {
                'total_chunks': 0,
                'speech_chunks': 0,
                'speech_ratio': 0.0,
                'avg_processing_time_ms': 0.0
            }
        
        return {
            'total_chunks': self.total_chunks_processed,
            'speech_chunks': self.total_speech_detected,
            'speech_ratio': self.total_speech_detected / self.total_chunks_processed,
            'avg_processing_time_ms': (self.total_processing_time / 
                                      self.total_chunks_processed * 1000),
            'is_speaking': self.is_speech
        }
    
    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (f"SileroVADEngine(initialized={self._is_initialized}, "
                f"chunks={stats['total_chunks']}, "
                f"speech_ratio={stats['speech_ratio']:.2%}, "
                f"avg_time={stats['avg_processing_time_ms']:.3f}ms)")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create VAD engine
    config = VADConfig(
        sampling_rate=16000,
        threshold=0.5,
        min_speech_duration_ms=250,
        min_silence_duration_ms=100
    )
    
    vad = SileroVADEngine(config)
    vad.initialize()
    
    # Simulate audio chunks
    import time
    for i in range(10):
        # Generate random audio (replace with real audio in production)
        audio_chunk = np.random.randn(512).astype(np.float32)
        
        is_speech, prob = vad.process_chunk(audio_chunk)
        print(f"Chunk {i}: Speech={is_speech}, Probability={prob:.3f}")
        
        time.sleep(0.03)  # 30ms
    
    # Print statistics
    print(f"\nStatistics: {vad.get_statistics()}")
    print(f"\nVAD: {vad}")
