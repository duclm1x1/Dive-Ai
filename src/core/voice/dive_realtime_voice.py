#!/usr/bin/env python3
"""
Dive AI V25.3 - OpenAI Realtime API Integration
Ultra-low latency voice interaction with GPT-4o
"""

import os
import json
import asyncio
import base64
import threading
import queue
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
import websockets
import pyaudio

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class RealtimeConfig:
    """Configuration for Realtime API"""
    model: str = "gpt-4o-realtime-preview-2024-10-01"
    voice: str = "alloy"  # alloy, echo, fable, onyx, nova, shimmer
    modalities: List[str] = None
    instructions: str = ""
    temperature: float = 0.8
    max_response_output_tokens: int = 4096
    
    def __post_init__(self):
        if self.modalities is None:
            self.modalities = ["text", "audio"]


class RealtimeVoiceProcessor:
    """
    OpenAI Realtime API voice processor
    Provides ultra-low latency voice-to-voice interaction
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[RealtimeConfig] = None,
        on_response: Optional[Callable[[str], None]] = None,
        on_audio: Optional[Callable[[bytes], None]] = None,
        on_function_call: Optional[Callable[[str, dict], Any]] = None
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.config = config or RealtimeConfig()
        
        # Callbacks
        self.on_response = on_response
        self.on_audio = on_audio
        self.on_function_call = on_function_call
        
        # WebSocket connection
        self.ws = None
        self.connected = False
        
        # Audio settings
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = 24000  # 24kHz required by Realtime API
        self.chunk_size = 1024
        
        # Queues
        self.audio_input_queue = queue.Queue()
        self.audio_output_queue = queue.Queue()
        
        # State
        self.is_speaking = False
        self.session_id = None
        self.conversation_active = False
        
        # PyAudio
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        
        print(f"✓ Realtime Voice Processor initialized")
        print(f"  Model: {self.config.model}")
        print(f"  Voice: {self.config.voice}")
    
    async def connect(self):
        """Connect to OpenAI Realtime API via WebSocket"""
        url = "wss://api.openai.com/v1/realtime"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.ws = await websockets.connect(
                url,
                extra_headers=headers,
                ping_interval=20,
                ping_timeout=10
            )
            
            self.connected = True
            print("✓ Connected to OpenAI Realtime API")
            
            # Configure session
            await self._configure_session()
            
            return True
        
        except Exception as e:
            print(f"⚠ Connection error: {e}")
            self.connected = False
            return False
    
    async def _configure_session(self):
        """Configure the Realtime API session"""
        config_message = {
            "type": "session.update",
            "session": {
                "modalities": self.config.modalities,
                "instructions": self.config.instructions or "You are Dive AI, a helpful voice assistant.",
                "voice": self.config.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500
                },
                "temperature": self.config.temperature,
                "max_response_output_tokens": self.config.max_response_output_tokens
            }
        }
        
        await self.ws.send(json.dumps(config_message))
        print("✓ Session configured")
    
    async def disconnect(self):
        """Disconnect from Realtime API"""
        if self.ws and self.connected:
            await self.ws.close()
            self.connected = False
            print("🛑 Disconnected from Realtime API")
    
    def start_audio_streams(self):
        """Start audio input/output streams"""
        try:
            # Input stream (microphone)
            self.input_stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_input_callback
            )
            
            # Output stream (speakers)
            self.output_stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                output=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_output_callback
            )
            
            self.input_stream.start_stream()
            self.output_stream.start_stream()
            
            print("✓ Audio streams started")
        
        except Exception as e:
            print(f"⚠ Audio stream error: {e}")
    
    def stop_audio_streams(self):
        """Stop audio streams"""
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        
        self.audio.terminate()
        print("🛑 Audio streams stopped")
    
    def _audio_input_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio input"""
        self.audio_input_queue.put(in_data)
        return (None, pyaudio.paContinue)
    
    def _audio_output_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio output"""
        try:
            data = self.audio_output_queue.get_nowait()
            return (data, pyaudio.paContinue)
        except queue.Empty:
            # Return silence if no audio available
            return (b'\x00' * frame_count * 2, pyaudio.paContinue)
    
    async def send_audio(self, audio_data: bytes):
        """Send audio data to Realtime API"""
        if not self.connected:
            return
        
        # Encode audio as base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        }
        
        await self.ws.send(json.dumps(message))
    
    async def commit_audio(self):
        """Commit audio buffer and request response"""
        if not self.connected:
            return
        
        message = {
            "type": "input_audio_buffer.commit"
        }
        
        await self.ws.send(json.dumps(message))
        
        # Create response
        response_message = {
            "type": "response.create",
            "response": {
                "modalities": self.config.modalities,
                "instructions": self.config.instructions
            }
        }
        
        await self.ws.send(json.dumps(response_message))
    
    async def send_text(self, text: str):
        """Send text message to Realtime API"""
        if not self.connected:
            return
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        
        await self.ws.send(json.dumps(message))
        await self.commit_audio()
    
    async def handle_events(self):
        """Handle incoming events from Realtime API"""
        if not self.connected:
            return
        
        try:
            async for message in self.ws:
                event = json.loads(message)
                event_type = event.get("type")
                
                # Handle different event types
                if event_type == "session.created":
                    self.session_id = event.get("session", {}).get("id")
                    print(f"✓ Session created: {self.session_id}")
                
                elif event_type == "session.updated":
                    print("✓ Session updated")
                
                elif event_type == "input_audio_buffer.speech_started":
                    print("🎤 Speech started")
                    self.is_speaking = True
                
                elif event_type == "input_audio_buffer.speech_stopped":
                    print("🎤 Speech stopped")
                    self.is_speaking = False
                    # Automatically commit audio when speech stops
                    await self.commit_audio()
                
                elif event_type == "input_audio_buffer.committed":
                    print("✓ Audio committed")
                
                elif event_type == "response.created":
                    print("🤖 Response created")
                
                elif event_type == "response.output_item.added":
                    print("📝 Output item added")
                
                elif event_type == "response.content_part.added":
                    print("📝 Content part added")
                
                elif event_type == "response.audio.delta":
                    # Receive audio response
                    audio_base64 = event.get("delta")
                    if audio_base64:
                        audio_data = base64.b64decode(audio_base64)
                        self.audio_output_queue.put(audio_data)
                        
                        if self.on_audio:
                            self.on_audio(audio_data)
                
                elif event_type == "response.audio.done":
                    print("🔊 Audio response complete")
                
                elif event_type == "response.text.delta":
                    # Receive text response
                    text_delta = event.get("delta")
                    if text_delta and self.on_response:
                        self.on_response(text_delta)
                
                elif event_type == "response.text.done":
                    text = event.get("text")
                    print(f"💬 Text response: {text}")
                
                elif event_type == "response.function_call_arguments.delta":
                    print("🔧 Function call arguments delta")
                
                elif event_type == "response.function_call_arguments.done":
                    # Function call completed
                    call_id = event.get("call_id")
                    name = event.get("name")
                    arguments = json.loads(event.get("arguments", "{}"))
                    
                    print(f"🔧 Function call: {name}({arguments})")
                    
                    if self.on_function_call:
                        result = self.on_function_call(name, arguments)
                        await self._send_function_result(call_id, result)
                
                elif event_type == "response.done":
                    print("✓ Response complete")
                
                elif event_type == "error":
                    error = event.get("error", {})
                    print(f"⚠ Error: {error.get('message')}")
        
        except websockets.exceptions.ConnectionClosed:
            print("🛑 Connection closed")
            self.connected = False
        except Exception as e:
            print(f"⚠ Event handling error: {e}")
    
    async def _send_function_result(self, call_id: str, result: Any):
        """Send function call result back to Realtime API"""
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            }
        }
        
        await self.ws.send(json.dumps(message))
        await self.commit_audio()
    
    async def audio_streaming_loop(self):
        """Continuously stream audio from microphone to API"""
        while self.connected and self.conversation_active:
            try:
                audio_data = self.audio_input_queue.get(timeout=0.1)
                await self.send_audio(audio_data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠ Audio streaming error: {e}")
                await asyncio.sleep(0.1)
    
    async def run(self):
        """Main run loop"""
        # Connect
        if not await self.connect():
            return
        
        # Start audio streams
        self.start_audio_streams()
        
        # Set conversation active
        self.conversation_active = True
        
        # Run event handler and audio streaming concurrently
        try:
            await asyncio.gather(
                self.handle_events(),
                self.audio_streaming_loop()
            )
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
        finally:
            self.conversation_active = False
            self.stop_audio_streams()
            await self.disconnect()


# Example usage
if __name__ == "__main__":
    def handle_response(text: str):
        print(f"📝 Response: {text}")
    
    def handle_audio(audio_data: bytes):
        pass  # Audio is automatically played via output stream
    
    def handle_function_call(name: str, args: dict) -> dict:
        print(f"🔧 Function called: {name}({args})")
        
        # Example function implementations
        if name == "open_application":
            app_name = args.get("app_name")
            # Execute command to open application
            return {"success": True, "message": f"Opened {app_name}"}
        
        return {"success": False, "message": "Function not implemented"}
    
    # Create processor
    processor = RealtimeVoiceProcessor(
        on_response=handle_response,
        on_audio=handle_audio,
        on_function_call=handle_function_call
    )
    
    # Run
    print("🎤 Starting Realtime Voice Processor...")
    print("Speak into your microphone. Press Ctrl+C to stop.")
    
    asyncio.run(processor.run())
