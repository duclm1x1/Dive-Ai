# Barge-in Detector - Technique #3
import logging
logger = logging.getLogger(__name__)

class BargeInDetector:
    def __init__(self, vad_engine, sensitivity=0.7):
        self.vad = vad_engine
        self.sensitivity = sensitivity
        self.is_speaking = False
        
    def detect(self, audio_chunk):
        if not self.is_speaking:
            return False
        speech_prob = self.vad.process_chunk(audio_chunk)[1]
        return speech_prob > self.sensitivity
