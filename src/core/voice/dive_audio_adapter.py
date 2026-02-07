import numpy as np
import sounddevice as sd
import queue
import io
import wave
import speech_recognition as sr

class DiveMicrophone:
    """
    A sounddevice-based replacement for speech_recognition.Microphone
    """
    def __init__(self, device=None, chunk_size=1024, sample_rate=16000):
        self.device = device
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.stream = None
        
        # Mimic sr.Microphone attributes
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_WIDTH = 2  # 16-bit
        self.CHUNK = chunk_size

    def __enter__(self):
        self.stream = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.sample_rate,
            callback=self._callback,
            blocksize=self.chunk_size,
            dtype='int16'
        )
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"Audio Status: {status}")
        self.audio_queue.put(indata.copy())

    def read(self, size):
        # This is a bit tricky as sr.Microphone doesn't have a read() method used directly by recognizer
        # instead recognizer uses the stream property.
        pass

class DiveAudioStream:
    def __init__(self, audio_queue):
        self.audio_queue = audio_queue
    
    def read(self, size):
        # Convert queue chunks to bytes
        try:
            data = self.audio_queue.get(timeout=2)
            return data.tobytes()
        except queue.Empty:
            return b""

# We need to wrap the sounddevice stream to look like what sr.Recognizer expects
class SpeechRecognitionAdapter(sr.AudioSource):
    def __init__(self, device=None, sample_rate=16000, chunk_size=1024):
        # We don't call super().__init__() because sr.AudioSource is abstract
        self.device = device
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Attributes required by sr.Recognizer
        self.SAMPLE_RATE = sample_rate
        self.SAMPLE_WIDTH = 2
        self.CHUNK = chunk_size
        self.audio_queue = queue.Queue()
        self.stream_handle = None
        self.stream = None

    def __enter__(self):
        self.stream_handle = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.sample_rate,
            callback=self._callback,
            blocksize=self.chunk_size,
            dtype='int16'
        )
        self.stream_handle.start()
        self.stream = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stream_handle:
            self.stream_handle.stop()
            self.stream_handle.close()
            self.stream_handle = None
        self.stream = None

    def _callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy().tobytes())

    def read(self, size):
        try:
            return self.audio_queue.get(timeout=2)
        except queue.Empty:
            return b""
