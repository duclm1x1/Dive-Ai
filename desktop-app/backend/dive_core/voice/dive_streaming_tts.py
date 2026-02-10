#!/usr/bin/env python3
"""
Dive AI V25 - Streaming TTS Module
Implements chunk-based text-to-speech for full-duplex conversation
"""

import os
import queue
import threading
import time
from typing import Optional, Generator, Callable
import tempfile

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import pygame
    pygame.mixer.init()
except ImportError:
    pygame = None


class StreamingTTS:
    """
    Streaming Text-to-Speech with chunk-based output
    Speaks responses as they're generated, not after completion
    """
    
    def __init__(
        self,
        provider: str = "pyttsx3",  # pyttsx3, openai
        api_key: Optional[str] = None,
        chunk_size: int = 50,  # Characters per chunk
        voice: str = "alloy"
    ):
        self.provider = provider
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.chunk_size = chunk_size
        self.voice = voice
        
        # Audio queue for streaming
        self.audio_queue = queue.Queue()
        self.is_speaking = False
        self.should_stop = False
        
        # Initialize TTS engine
        self._init_engine()
        
        # Start audio playback thread
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
        
        print(f"✓ Streaming TTS initialized (provider: {provider})")
    
    def _init_engine(self):
        """Initialize TTS engine"""
        if self.provider == "pyttsx3" and pyttsx3:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 175)
            self.engine.setProperty('volume', 0.9)
        elif self.provider == "openai" and OpenAI:
            self.client = OpenAI(api_key=self.api_key)
        else:
            raise ValueError(f"TTS provider '{self.provider}' not available")
    
    def speak_stream(self, text_generator: Generator[str, None, None], callback: Optional[Callable] = None):
        """
        Speak text as it's being generated
        
        Args:
            text_generator: Generator yielding text chunks
            callback: Optional callback for each chunk spoken
        """
        buffer = ""
        
        for chunk in text_generator:
            if self.should_stop:
                break
            
            buffer += chunk
            
            # Speak when buffer reaches chunk size or ends with punctuation
            if len(buffer) >= self.chunk_size or self._ends_with_punctuation(buffer):
                self._queue_audio(buffer.strip())
                if callback:
                    callback(buffer.strip())
                buffer = ""
        
        # Speak remaining buffer
        if buffer.strip() and not self.should_stop:
            self._queue_audio(buffer.strip())
            if callback:
                callback(buffer.strip())
    
    def speak(self, text: str, priority: bool = False):
        """
        Speak text immediately (non-streaming)
        
        Args:
            text: Text to speak
            priority: If True, clear queue and speak immediately
        """
        if priority:
            self.stop()
            time.sleep(0.1)  # Allow stop to take effect
        
        # Split into sentences for better pacing
        sentences = self._split_sentences(text)
        for sentence in sentences:
            if sentence.strip():
                self._queue_audio(sentence.strip())
    
    def _queue_audio(self, text: str):
        """Queue text for audio synthesis"""
        self.audio_queue.put(text)
    
    def _playback_loop(self):
        """Audio playback loop (runs in separate thread)"""
        while True:
            try:
                text = self.audio_queue.get(timeout=0.1)
                
                if self.should_stop:
                    self.should_stop = False
                    continue
                
                self.is_speaking = True
                self._synthesize_and_play(text)
                self.is_speaking = False
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Playback error: {e}")
                self.is_speaking = False
    
    def _synthesize_and_play(self, text: str):
        """Synthesize and play audio"""
        try:
            if self.provider == "pyttsx3":
                self.engine.say(text)
                self.engine.runAndWait()
            
            elif self.provider == "openai":
                # Generate audio
                response = self.client.audio.speech.create(
                    model="tts-1",
                    voice=self.voice,
                    input=text,
                    speed=1.0
                )
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    f.write(response.content)
                    temp_path = f.name
                
                # Play audio
                if pygame:
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()
                    
                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy() and not self.should_stop:
                        time.sleep(0.1)
                    
                    pygame.mixer.music.stop()
                
                # Clean up
                try:
                    os.unlink(temp_path)
                except:
                    pass
        
        except Exception as e:
            print(f"⚠ Synthesis error: {e}")
    
    def stop(self):
        """Stop current speech and clear queue"""
        self.should_stop = True
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Stop pygame if playing
        if pygame and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        
        # Stop pyttsx3 if speaking
        if self.provider == "pyttsx3" and self.engine:
            try:
                self.engine.stop()
            except:
                pass
    
    def is_active(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking or not self.audio_queue.empty()
    
    def _ends_with_punctuation(self, text: str) -> bool:
        """Check if text ends with punctuation"""
        return text.rstrip().endswith(('.', '!', '?', ',', ';', ':'))
    
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences"""
        import re
        sentences = re.split(r'([.!?]+\s+)', text)
        result = []
        for i in range(0, len(sentences)-1, 2):
            result.append(sentences[i] + sentences[i+1])
        if len(sentences) % 2 == 1:
            result.append(sentences[-1])
        return result


class LLMStreamingTTS:
    """
    Combines LLM streaming with TTS
    Speaks LLM responses as they're generated
    """
    
    def __init__(
        self,
        llm_client,
        tts: StreamingTTS,
        model: str = "gpt-4"
    ):
        self.llm_client = llm_client
        self.tts = tts
        self.model = model
    
    def generate_and_speak(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        on_chunk: Optional[Callable] = None
    ) -> str:
        """
        Generate LLM response and speak it in real-time
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            on_chunk: Callback for each text chunk
        
        Returns:
            Full generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Stream LLM response
        full_text = ""
        
        def text_generator():
            nonlocal full_text
            stream = self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_text += text
                    if on_chunk:
                        on_chunk(text)
                    yield text
        
        # Speak as text is generated
        self.tts.speak_stream(text_generator())
        
        return full_text


# Example usage
if __name__ == "__main__":
    # Test streaming TTS
    tts = StreamingTTS(provider="pyttsx3")
    
    # Test 1: Regular speak
    print("Test 1: Regular speak")
    tts.speak("Hello! This is a test of the streaming text to speech system.")
    time.sleep(3)
    
    # Test 2: Streaming speak
    print("\nTest 2: Streaming speak")
    def text_generator():
        words = "This is a streaming test where words appear one by one and are spoken as they arrive".split()
        for word in words:
            yield word + " "
            time.sleep(0.2)
    
    tts.speak_stream(text_generator(), callback=lambda x: print(f"Speaking: {x}"))
    
    # Wait for completion
    while tts.is_active():
        time.sleep(0.1)
    
    print("\n✓ Tests complete")
