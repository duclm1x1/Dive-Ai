"""
V98 API Integration for Dive AI v25 Hear Model

Provides STT, TTS, and Understanding via V98 API
with local fallback support
"""

import asyncio
import os
from typing import Optional, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import httpx
import json

# V98 Configuration
V98_BASE_URL = os.getenv("V98_API_URL", "https://v98store.com/v1")
V98_API_KEY = os.getenv("V98_API_KEY", "YOUR_V98_API_KEY_HERE")

# Aicoding Configuration (Alternative)
AICODING_BASE_URL = os.getenv("AICODING_API_URL", "https://aicoding.io.vn/v1")
AICODING_API_KEY = os.getenv("AICODING_API_KEY", "YOUR_AICODING_API_KEY_HERECJCk")


class APIProvider(Enum):
    """Available API providers"""
    V98 = "v98"
    AICODING = "aicoding"
    LOCAL = "local"


@dataclass
class STTResult:
    """Speech-to-Text result"""
    text: str
    confidence: float
    language: str
    is_final: bool


@dataclass
class TTSResult:
    """Text-to-Speech result"""
    audio: bytes
    format: str  # mp3, wav, pcm
    sample_rate: int


class V98STTClient:
    """
    V98 Speech-to-Text Client
    Uses latest STT models via V98 API
    """
    
    def __init__(self, provider: APIProvider = APIProvider.V98):
        self.provider = provider
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if provider == APIProvider.V98:
            self.base_url = V98_BASE_URL
            self.api_key = V98_API_KEY
        elif provider == APIProvider.AICODING:
            self.base_url = AICODING_BASE_URL
            self.api_key = AICODING_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
        model: str = "whisper-1"
    ) -> STTResult:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio bytes
            language: Language code (en, vi, etc.)
            model: Model to use (whisper-1, latest-stt, etc.)
        
        Returns:
            STTResult with transcribed text
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Prepare request based on provider
        if self.provider == APIProvider.V98:
            payload = {
                "model": model,
                "audio": audio_data.hex(),  # Convert bytes to hex string
                "language": language,
                "response_format": "json"
            }
            endpoint = f"{self.base_url}/audio/transcriptions"
        else:  # AICODING
            payload = {
                "model": model,
                "audio": audio_data.hex(),
                "language": language
            }
            endpoint = f"{self.base_url}/audio/transcriptions"
        
        try:
            response = await self.client.post(
                endpoint,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            
            return STTResult(
                text=data.get("text", ""),
                confidence=data.get("confidence", 0.9),
                language=language,
                is_final=True
            )
        
        except httpx.HTTPError as e:
            print(f"STT API Error: {e}")
            raise
    
    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator,
        language: str = "en"
    ) -> AsyncGenerator[STTResult, None]:
        """
        Stream transcription for real-time STT
        
        Args:
            audio_stream: Async generator yielding audio chunks
            language: Language code
        
        Yields:
            STTResult objects as they become available
        """
        buffer = b""
        
        async for chunk in audio_stream:
            buffer += chunk
            
            # Process buffer every 1 second of audio (16kHz * 2 bytes * 1s = 32KB)
            if len(buffer) >= 32000:
                result = await self.transcribe(buffer, language)
                result.is_final = False
                yield result
                buffer = b""
        
        # Process remaining audio
        if buffer:
            result = await self.transcribe(buffer, language)
            result.is_final = True
            yield result
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class V98TTSClient:
    """
    V98 Text-to-Speech Client
    Uses latest TTS models via V98 API
    """
    
    def __init__(self, provider: APIProvider = APIProvider.V98):
        self.provider = provider
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if provider == APIProvider.V98:
            self.base_url = V98_BASE_URL
            self.api_key = V98_API_KEY
        elif provider == APIProvider.AICODING:
            self.base_url = AICODING_BASE_URL
            self.api_key = AICODING_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def speak(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
        language: str = "en"
    ) -> TTSResult:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: Model to use (tts-1, tts-1-hd)
            speed: Speech speed (0.25 - 4.0)
            language: Language code
        
        Returns:
            TTSResult with audio bytes
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "input": text,
            "voice": voice,
            "speed": speed,
            "language": language,
            "response_format": "mp3"
        }
        
        endpoint = f"{self.base_url}/audio/speech"
        
        try:
            response = await self.client.post(
                endpoint,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            return TTSResult(
                audio=response.content,
                format="mp3",
                sample_rate=24000
            )
        
        except httpx.HTTPError as e:
            print(f"TTS API Error: {e}")
            raise
    
    async def speak_stream(
        self,
        text: str,
        voice: str = "alloy",
        model: str = "tts-1",
        speed: float = 1.0,
        language: str = "en"
    ) -> AsyncGenerator[TTSResult, None]:
        """
        Stream text-to-speech for real-time audio
        
        Args:
            text: Text to convert
            voice: Voice to use
            model: Model to use
            speed: Speech speed
            language: Language code
        
        Yields:
            TTSResult chunks as they become available
        """
        # For streaming, we split text into sentences
        sentences = text.split(". ")
        
        for sentence in sentences:
            if sentence.strip():
                result = await self.speak(
                    sentence + ".",
                    voice=voice,
                    model=model,
                    speed=speed,
                    language=language
                )
                yield result
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class V98UnderstandingClient:
    """
    V98 Understanding Client
    Uses latest LLM models for intent extraction and context understanding
    """
    
    def __init__(self, provider: APIProvider = APIProvider.V98):
        self.provider = provider
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if provider == APIProvider.V98:
            self.base_url = V98_BASE_URL
            self.api_key = V98_API_KEY
        elif provider == APIProvider.AICODING:
            self.base_url = AICODING_BASE_URL
            self.api_key = AICODING_API_KEY
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def analyze_intent(
        self,
        text: str,
        context: Optional[str] = None,
        language: str = "en",
        model: str = "gpt-4o"
    ) -> dict:
        """
        Analyze user intent from text
        
        Args:
            text: User input text
            context: Previous conversation context
            language: Language code
            model: LLM model to use
        
        Returns:
            Dict with action, target, parameters, confidence
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        system_prompt = """You are an AI assistant that analyzes user voice commands.
Extract the following from the user's input:
1. action: The action to perform (click, type, open, close, scroll, navigate, search, screenshot, question)
2. target: The target element or application
3. parameters: Any additional parameters
4. confidence: Your confidence level (0.0 - 1.0)

Respond in JSON format:
{
    "action": "...",
    "target": "...",
    "parameters": {...},
    "confidence": 0.0,
    "explanation": "..."
}"""
        
        user_message = f"User input: {text}"
        if context:
            user_message += f"\n\nContext: {context}"
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        endpoint = f"{self.base_url}/chat/completions"
        
        try:
            response = await self.client.post(
                endpoint,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Parse JSON response
            result = json.loads(content)
            return result
        
        except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
            print(f"Understanding API Error: {e}")
            return {
                "action": "question",
                "target": text,
                "parameters": {},
                "confidence": 0.0,
                "explanation": f"Error: {str(e)}"
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class HearModelV98:
    """
    Complete Hear Model using V98 API
    Integrates STT, Understanding, and TTS
    """
    
    def __init__(
        self,
        provider: APIProvider = APIProvider.V98,
        fallback_provider: Optional[APIProvider] = None
    ):
        self.provider = provider
        self.fallback_provider = fallback_provider
        
        self.stt = V98STTClient(provider)
        self.tts = V98TTSClient(provider)
        self.understanding = V98UnderstandingClient(provider)
        
        if fallback_provider:
            self.fallback_stt = V98STTClient(fallback_provider)
            self.fallback_tts = V98TTSClient(fallback_provider)
            self.fallback_understanding = V98UnderstandingClient(fallback_provider)
        else:
            self.fallback_stt = None
            self.fallback_tts = None
            self.fallback_understanding = None
    
    async def process_voice(
        self,
        audio_data: bytes,
        context: Optional[str] = None,
        language: str = "en"
    ) -> dict:
        """
        Complete voice processing pipeline:
        1. Listen (STT)
        2. Understand (Intent analysis)
        3. Respond (TTS)
        
        Args:
            audio_data: Audio bytes
            context: Conversation context
            language: Language code
        
        Returns:
            Dict with action, response_audio, understanding
        """
        try:
            # 1. LISTEN
            transcription = await self.stt.transcribe(audio_data, language)
            print(f"[STT] {transcription.text}")
            
            # 2. UNDERSTAND
            understanding = await self.understanding.analyze_intent(
                transcription.text,
                context=context,
                language=language
            )
            print(f"[UNDERSTANDING] Action: {understanding.get('action')}")
            
            # 3. RESPOND
            response_text = f"Executing {understanding.get('action')} on {understanding.get('target')}"
            response_audio = await self.tts.speak(response_text, language=language)
            print(f"[TTS] Generated response audio")
            
            return {
                "transcription": transcription.text,
                "understanding": understanding,
                "response_audio": response_audio.audio,
                "success": True
            }
        
        except Exception as e:
            print(f"[ERROR] Voice processing failed: {e}")
            
            # Try fallback if available
            if self.fallback_stt:
                print("[FALLBACK] Trying fallback provider...")
                try:
                    transcription = await self.fallback_stt.transcribe(audio_data, language)
                    understanding = await self.fallback_understanding.analyze_intent(
                        transcription.text,
                        context=context,
                        language=language
                    )
                    response_text = f"Executing {understanding.get('action')}"
                    response_audio = await self.fallback_tts.speak(response_text, language=language)
                    
                    return {
                        "transcription": transcription.text,
                        "understanding": understanding,
                        "response_audio": response_audio.audio,
                        "success": True,
                        "provider": "fallback"
                    }
                except Exception as fallback_error:
                    print(f"[FALLBACK ERROR] {fallback_error}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close all clients"""
        await self.stt.close()
        await self.tts.close()
        await self.understanding.close()
        
        if self.fallback_stt:
            await self.fallback_stt.close()
            await self.fallback_tts.close()
            await self.fallback_understanding.close()


# Example usage
async def main():
    """Test V98 integration"""
    
    # Initialize with V98 primary, AICODING fallback
    hear_model = HearModelV98(
        provider=APIProvider.V98,
        fallback_provider=APIProvider.AICODING
    )
    
    # Simulate audio data (would be real audio in practice)
    # This is just a placeholder
    dummy_audio = b"audio_data_here"
    
    # Process voice command
    result = await hear_model.process_voice(
        dummy_audio,
        context="User was browsing Chrome",
        language="en"
    )
    
    print(f"\nResult: {json.dumps(result, indent=2, default=str)}")
    
    await hear_model.close()


if __name__ == "__main__":
    asyncio.run(main())
