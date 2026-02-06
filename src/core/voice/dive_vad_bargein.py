#!/usr/bin/env python3
"""
Dive AI V25 - VAD-based Barge-in Module
Implements Voice Activity Detection for interrupting AI speech
"""

import os
import queue
import threading
import time
from typing import Optional, Callable
import numpy as np

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import webrtcvad
except ImportError:
    webrtcvad = None

try:
    import sounddevice as sd
except ImportError:
    sd = None


class VADBargeIn:
    """
    Voice Activity Detection for barge-in (interruption) capability
    Detects when user starts speaking and interrupts AI
    """
    
    def __init__(
        self,
        sensitivity: int = 2,  # 0-3, higher = more sensitive
        frame_duration: int = 30,  # ms per frame (10, 20, or 30)
        sample_rate: int = 16000,
        trigger_threshold: int = 3,  # Consecutive frames to trigger
        on_speech_detected: Optional[Callable] = None
    ):
        self.sensitivity = sensitivity
        self.frame_duration = frame_duration
        self.sample_rate = sample_rate
        self.trigger_threshold = trigger_threshold
        self.on_speech_detected = on_speech_detected
        
        # State
        self.is_monitoring = False
        self.speech_detected = False
        self.consecutive_speech_frames = 0
        
        # Initialize VAD
        if webrtcvad:
            try:
                self.vad = webrtcvad.Vad(sensitivity)
                print(f"✓ WebRTC VAD initialized (sensitivity: {sensitivity})")
            except Exception as e:
                print(f"⚠ WebRTC VAD init error: {e}")
                self.vad = None
        elif sr:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone(sample_rate=sample_rate)
                print("✓ SpeechRecognition VAD initialized")
            except (AttributeError, Exception) as e:
                print(f"⚠ SpeechRecognition VAD hardware not available: {e}")
                self.recognizer = None
                self.microphone = None
        else:
            print("⚠ VAD not available. Install: pip install webrtcvad pyaudio")
            self.vad = None
            self.microphone = None
        
        # Audio queue
        self.audio_queue = queue.Queue()
        
        # Monitoring thread
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start monitoring for voice activity"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.speech_detected = False
        self.consecutive_speech_frames = 0
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print("🎤 VAD monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("🛑 VAD monitoring stopped")
    
    def reset(self):
        """Reset speech detection state"""
        self.speech_detected = False
        self.consecutive_speech_frames = 0
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        if webrtcvad:
            self._monitor_with_webrtc()
        else:
            self._monitor_with_sr()
    
    def _monitor_with_webrtc(self):
        """Monitor using WebRTC VAD"""
        if not sd:
            print("⚠ VAD monitoring failed: sounddevice not installed")
            self.is_monitoring = False
            return
        
        # Audio parameters
        chunk_size = int(self.sample_rate * self.frame_duration / 1000)
        
        print(f"🎤 Listening for voice activity via sounddevice (chunk: {chunk_size}, rate: {self.sample_rate})")
        
        def callback(indata, frames, time, status):
            if not self.is_monitoring:
                return
            
            # indata is a numpy array, webrtcvad needs bytes
            frame = indata.tobytes()
            
            # Check for speech
            is_speech = self.vad.is_speech(frame, self.sample_rate)
            
            if is_speech:
                self.consecutive_speech_frames += 1
                
                # Trigger if threshold reached
                if self.consecutive_speech_frames >= self.trigger_threshold:
                    if not self.speech_detected:
                        self.speech_detected = True
                        print("🗣️ Speech detected! (barge-in)")
                        
                        if self.on_speech_detected:
                            self.on_speech_detected()
            else:
                # Reset counter if silence detected
                if self.consecutive_speech_frames > 0:
                    self.consecutive_speech_frames = max(0, self.consecutive_speech_frames - 1)

        try:
            with sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                blocksize=chunk_size,
                dtype='int16',
                callback=callback
            ):
                while self.is_monitoring:
                    time.sleep(0.1)
        
        except Exception as e:
            print(f"⚠ VAD monitoring error: {e}")
        
    def _monitor_with_sr(self):
        """Monitor using sounddevice for SpeechRecognition context"""
        if not self.microphone:
            print("⚠ VAD sr monitor failed: Microphone not initialized")
            return
            
        with self.microphone as source:
            # Note: adjust_for_ambient_noise might not be fully supported by our adapter yet
            # but we can try
            pass
        
        while self.is_monitoring:
            try:
                # We need to adapt sr.Recognizer.listen to use our sounddevice source
                # our SpeechRecognitionAdapter already handles this in its __enter__
                # but sr.Recognizer.listen calls source.stream.read
                audio = self.recognizer.listen(self.microphone, timeout=0.5, phrase_time_limit=1)
                
                if not self.speech_detected:
                    self.speech_detected = True
                    print("🗣️ Speech detected! (barge-in)")
                    if self.on_speech_detected:
                        self.on_speech_detected()
            except Exception as e:
                time.sleep(0.1)


class BargeInController:
    """
    Controls barge-in behavior for full-duplex conversation
    Manages TTS interruption and task abortion
    """
    
    def __init__(
        self,
        vad: VADBargeIn,
        tts_controller,
        task_controller=None,
        abort_tasks_on_interrupt: bool = False
    ):
        self.vad = vad
        self.tts_controller = tts_controller
        self.task_controller = task_controller
        self.abort_tasks_on_interrupt = abort_tasks_on_interrupt
        
        # Set callback
        self.vad.on_speech_detected = self.on_interrupt
        
        # State
        self.interrupt_count = 0
        self.last_interrupt_time = 0
        
        print("✓ Barge-in controller initialized")
    
    def on_interrupt(self):
        """Handle voice interrupt"""
        current_time = time.time()
        
        # Debounce (ignore if too soon after last interrupt)
        if current_time - self.last_interrupt_time < 1.0:
            return
        
        self.last_interrupt_time = current_time
        self.interrupt_count += 1
        
        print(f"⚡ Interrupt #{self.interrupt_count}: Pausing TTS")
        
        # Stop TTS immediately
        if self.tts_controller:
            self.tts_controller.stop()
        
        # Optionally abort current task
        if self.abort_tasks_on_interrupt and self.task_controller:
            print("⚡ Aborting current task")
            self.task_controller.abort_current_task()
        
        # Reset VAD state
        self.vad.reset()
    
    def start(self):
        """Start barge-in monitoring"""
        self.vad.start_monitoring()
    
    def stop(self):
        """Stop barge-in monitoring"""
        self.vad.stop_monitoring()
    
    def get_stats(self) -> dict:
        """Get interrupt statistics"""
        return {
            "interrupt_count": self.interrupt_count,
            "last_interrupt": self.last_interrupt_time,
            "is_monitoring": self.vad.is_monitoring
        }


class AdaptiveVAD(VADBargeIn):
    """
    Adaptive VAD that adjusts sensitivity based on environment
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ambient_noise_level = 0
        self.adaptation_enabled = True
    
    def calibrate(self, duration: float = 2.0):
        """
        Calibrate VAD to ambient noise
        
        Args:
            duration: Calibration duration in seconds
        """
        print(f"🎤 Calibrating VAD (please remain silent for {duration}s)...")
        
        if sr and hasattr(self, 'recognizer') and hasattr(self, 'microphone'):
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.ambient_noise_level = self.recognizer.energy_threshold
                print(f"✓ Calibrated (threshold: {self.ambient_noise_level:.2f})")
        else:
            print("⚠ Calibration not available for WebRTC VAD")
    
    def adapt_sensitivity(self, noise_level: float):
        """Dynamically adjust sensitivity based on noise level"""
        if not self.adaptation_enabled:
            return
        
        # Adjust sensitivity (0-3)
        if noise_level < 100:
            new_sensitivity = 3  # Very sensitive
        elif noise_level < 300:
            new_sensitivity = 2  # Moderate
        elif noise_level < 500:
            new_sensitivity = 1  # Less sensitive
        else:
            new_sensitivity = 0  # Least sensitive
        
        if new_sensitivity != self.sensitivity and webrtcvad:
            self.sensitivity = new_sensitivity
            self.vad = webrtcvad.Vad(new_sensitivity)
            print(f"🔧 VAD sensitivity adjusted to {new_sensitivity}")


# Example usage
if __name__ == "__main__":
    # Mock TTS controller
    class MockTTS:
        def stop(self):
            print("🛑 TTS stopped")
    
    # Mock task controller
    class MockTaskController:
        def abort_current_task(self):
            print("⚡ Task aborted")
    
    # Test VAD
    def on_speech():
        print("✅ Speech detected callback triggered!")
    
    try:
        vad = VADBargeIn(
            sensitivity=2,
            trigger_threshold=3,
            on_speech_detected=on_speech
        )
        
        # Test with controller
        tts = MockTTS()
        task_ctrl = MockTaskController()
        
        controller = BargeInController(
            vad=vad,
            tts_controller=tts,
            task_controller=task_ctrl,
            abort_tasks_on_interrupt=True
        )
        
        print("\n🎤 Starting VAD test...")
        print("Speak to trigger barge-in (Ctrl+C to stop)\n")
        
        controller.start()
        
        # Keep running
        try:
            while True:
                time.sleep(1)
                if vad.speech_detected:
                    print(f"📊 Stats: {controller.get_stats()}")
                    vad.reset()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping...")
            controller.stop()
    
    except ImportError as e:
        print(f"⚠ Missing dependency: {e}")
        print("Install with: pip install webrtcvad pyaudio")
