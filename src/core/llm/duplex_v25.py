"""
Full-Duplex Voice Controller for Dive AI v25
Enables simultaneous listening and speaking
"""

import asyncio
from typing import AsyncGenerator, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class DuplexState(Enum):
    """Duplex controller states"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    DUPLEX = "duplex"  # Simultaneous listen/speak


@dataclass
class DuplexEvent:
    """Duplex event"""
    state: DuplexState
    timestamp: float
    data: Optional[dict] = None


class FullDuplexController:
    """
    Full-Duplex Voice Controller
    Manages simultaneous listening and speaking
    """
    
    def __init__(self, stt_client, tts_client, understanding_client):
        self.stt = stt_client
        self.tts = tts_client
        self.understanding = understanding_client
        
        self.state = DuplexState.IDLE
        self.is_listening = False
        self.is_speaking = False
        self.event_callbacks = []
        self.conversation_history = []
    
    async def emit_event(self, event: DuplexEvent):
        """Emit duplex event"""
        for callback in self.event_callbacks:
            try:
                await callback(event)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def on_state_change(self, callback: Callable):
        """Register state change callback"""
        self.event_callbacks.append(callback)
    
    async def start_duplex_conversation(
        self,
        audio_stream: AsyncGenerator,
        context: Optional[str] = None,
        language: str = "en"
    ):
        """
        Start full-duplex conversation
        Simultaneously listen and respond
        
        Args:
            audio_stream: Async generator yielding audio chunks
            context: Conversation context
            language: Language code
        """
        self.state = DuplexState.DUPLEX
        await self.emit_event(DuplexEvent(
            state=self.state,
            timestamp=asyncio.get_event_loop().time(),
            data={"message": "Starting duplex conversation"}
        ))
        
        # Create concurrent tasks for listening and responding
        listen_task = asyncio.create_task(
            self._listen_loop(audio_stream, context, language)
        )
        
        speak_task = asyncio.create_task(
            self._speak_loop()
        )
        
        try:
            await asyncio.gather(listen_task, speak_task)
        except asyncio.CancelledError:
            print("Duplex conversation cancelled")
        finally:
            self.state = DuplexState.IDLE
            await self.emit_event(DuplexEvent(
                state=self.state,
                timestamp=asyncio.get_event_loop().time(),
                data={"message": "Duplex conversation ended"}
            ))
    
    async def _listen_loop(
        self,
        audio_stream: AsyncGenerator,
        context: Optional[str],
        language: str
    ):
        """Listen loop - process incoming audio"""
        self.is_listening = True
        
        async for audio_chunk in audio_stream:
            if not self.is_listening:
                break
            
            try:
                # Transcribe audio
                self.state = DuplexState.LISTENING
                transcription = await self.stt.transcribe(
                    audio_chunk,
                    language=language
                )
                
                # Analyze intent
                self.state = DuplexState.PROCESSING
                understanding = await self.understanding.analyze_intent(
                    transcription.text,
                    context=context,
                    language=language
                )
                
                # Add to conversation history
                self.conversation_history.append({
                    "type": "user",
                    "text": transcription.text,
                    "understanding": understanding
                })
                
                # Emit event
                await self.emit_event(DuplexEvent(
                    state=self.state,
                    timestamp=asyncio.get_event_loop().time(),
                    data={
                        "transcription": transcription.text,
                        "understanding": understanding
                    }
                ))
                
                # Queue response
                await self._queue_response(understanding, language)
            
            except Exception as e:
                print(f"Listen loop error: {e}")
        
        self.is_listening = False
    
    async def _speak_loop(self):
        """Speak loop - generate and play responses"""
        self.is_speaking = True
        response_queue = asyncio.Queue()
        
        while self.is_speaking:
            try:
                # Get response from queue (with timeout)
                response = await asyncio.wait_for(
                    response_queue.get(),
                    timeout=1.0
                )
                
                if response is None:
                    break
                
                # Generate speech
                self.state = DuplexState.SPEAKING
                tts_result = await self.tts.speak(
                    response["text"],
                    language=response.get("language", "en")
                )
                
                # Add to history
                self.conversation_history.append({
                    "type": "assistant",
                    "text": response["text"],
                    "audio": tts_result.audio
                })
                
                # Emit event
                await self.emit_event(DuplexEvent(
                    state=self.state,
                    timestamp=asyncio.get_event_loop().time(),
                    data={
                        "response_text": response["text"],
                        "audio_duration": len(tts_result.audio) / 24000  # Approx duration
                    }
                ))
            
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Speak loop error: {e}")
        
        self.is_speaking = False
    
    async def _queue_response(self, understanding: dict, language: str):
        """Queue a response for speaking"""
        response_text = f"Executing {understanding.get('action')} on {understanding.get('target')}"
        
        # This would be queued in real implementation
        print(f"[QUEUED] {response_text}")
    
    async def stop_conversation(self):
        """Stop duplex conversation"""
        self.is_listening = False
        self.is_speaking = False
    
    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []


class InterruptibleSpeech:
    """
    Interruptible Speech
    Allows user to interrupt AI while it's speaking
    """
    
    def __init__(self, tts_client, stt_client):
        self.tts = tts_client
        self.stt = stt_client
        self.is_speaking = False
        self.speech_task = None
    
    async def speak_interruptible(
        self,
        text: str,
        language: str = "en",
        on_interrupt: Optional[Callable] = None
    ):
        """
        Speak text but allow interruption
        
        Args:
            text: Text to speak
            language: Language code
            on_interrupt: Callback when interrupted
        """
        self.is_speaking = True
        
        try:
            # Generate speech
            tts_result = await self.tts.speak(text, language=language)
            
            # Play audio (would be actual playback in real implementation)
            duration = len(tts_result.audio) / 24000
            
            # Check for interruption during playback
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < duration:
                if not self.is_speaking:
                    if on_interrupt:
                        await on_interrupt()
                    break
                
                await asyncio.sleep(0.1)
        
        finally:
            self.is_speaking = False
    
    async def interrupt(self):
        """Interrupt current speech"""
        self.is_speaking = False


# Example usage
async def example_duplex():
    """Example full-duplex conversation"""
    from hear.v98_integration import HearModelV98, APIProvider
    
    # Initialize
    hear_model = HearModelV98(provider=APIProvider.V98)
    
    # Create controller
    controller = FullDuplexController(
        hear_model.stt,
        hear_model.tts,
        hear_model.understanding
    )
    
    # Register event handler
    async def on_state_change(event: DuplexEvent):
        print(f"[{event.state.value.upper()}] {event.data}")
    
    controller.on_state_change(on_state_change)
    
    # Simulate audio stream
    async def audio_stream():
        # In real implementation, would read from microphone
        yield b"audio_chunk_1"
        yield b"audio_chunk_2"
        yield b"audio_chunk_3"
    
    # Start conversation
    try:
        await controller.start_duplex_conversation(
            audio_stream(),
            context="User is working on desktop",
            language="en"
        )
    finally:
        await hear_model.close()


if __name__ == "__main__":
    asyncio.run(example_duplex())
