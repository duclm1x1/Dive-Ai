"""
Hybrid Mode: Graceful API Fallback System for Dive AI v25

Strategy:
- Primary: Offline (local models)
- Secondary: V98 API (when online)
- Automatic fallback based on connectivity
"""

import asyncio
import os
from typing import Optional
from enum import Enum
from dataclasses import dataclass
import socket


class Mode(Enum):
    """Operation modes"""
    OFFLINE = "offline"
    HYBRID = "hybrid"
    ONLINE = "online"


@dataclass
class HybridConfig:
    """Hybrid mode configuration"""
    mode: Mode = Mode.OFFLINE
    use_api_when_available: bool = True
    prefer_local_speed: bool = True  # Prioritize speed over quality
    fallback_on_error: bool = True
    v98_api_key: Optional[str] = None
    v98_api_url: Optional[str] = None


class ConnectivityMonitor:
    """Monitor internet connectivity"""
    
    @staticmethod
    async def is_online(timeout: int = 2) -> bool:
        """
        Check if internet is available
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            True if online, False otherwise
        """
        try:
            # Try to connect to Google DNS
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection("8.8.8.8", 53),
                timeout=timeout
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, OSError):
            return False
    
    @staticmethod
    async def check_api_availability(
        api_url: str,
        timeout: int = 2
    ) -> bool:
        """
        Check if specific API is available
        
        Args:
            api_url: API endpoint URL
            timeout: Timeout in seconds
        
        Returns:
            True if API is reachable
        """
        try:
            import httpx
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.head(api_url)
                return response.status_code < 500
        except Exception:
            return False


class HybridHearModel:
    """
    Hybrid Hear Model: Offline-first with optional API enhancement
    """
    
    def __init__(self, config: HybridConfig = None):
        self.config = config or HybridConfig()
        self.offline_stt = None
        self.offline_tts = None
        self.offline_understanding = None
        self.api_client = None
        self.current_mode = self.config.mode
        self.connectivity_monitor = ConnectivityMonitor()
        
        print(f"🎧 Initializing Hybrid Hear Model ({self.config.mode.value})...")
        self._initialize()
    
    def _initialize(self):
        """Initialize components based on mode"""
        # Always initialize offline components
        self._initialize_offline()
        
        # Initialize API client if configured
        if self.config.use_api_when_available:
            self._initialize_api()
    
    def _initialize_offline(self):
        """Initialize offline components"""
        try:
            from hear.offline_stt import OfflineSTT
            from hear.offline_tts import OfflineTTS
            from hear.offline_understanding import OfflineUnderstanding
            
            print("  📡 Initializing offline components...")
            self.offline_stt = OfflineSTT(model_size="large-v3-turbo")
            self.offline_tts = OfflineTTS(device="cuda")
            self.offline_understanding = OfflineUnderstanding(device="cuda")
            print("  ✅ Offline components ready")
        
        except Exception as e:
            print(f"  ⚠️  Offline initialization warning: {e}")
    
    def _initialize_api(self):
        """Initialize API client"""
        try:
            from hear.v98_integration import HearModelV98, APIProvider
            
            api_key = self.config.v98_api_key or os.getenv("V98_API_KEY")
            api_url = self.config.v98_api_url or os.getenv("V98_API_URL")
            
            if not api_key:
                print("  ⚠️  V98 API key not configured (optional)")
                return
            
            print("  🌐 Initializing V98 API client...")
            self.api_client = HearModelV98(
                provider=APIProvider.V98
            )
            print("  ✅ API client ready")
        
        except Exception as e:
            print(f"  ⚠️  API initialization warning: {e}")
    
    async def process_voice(
        self,
        audio_data: bytes,
        context: Optional[str] = None,
        language: str = "en",
        force_mode: Optional[Mode] = None
    ) -> dict:
        """
        Process voice with intelligent fallback
        
        Args:
            audio_data: Audio bytes
            context: Conversation context
            language: Language code
            force_mode: Force specific mode (offline/hybrid/online)
        
        Returns:
            Result dict with transcription, understanding, response
        """
        # Determine mode
        mode = force_mode or await self._determine_mode()
        
        print(f"\n🎤 Processing voice ({mode.value} mode)...")
        
        if mode == Mode.OFFLINE:
            return await self._process_offline(audio_data, context, language)
        
        elif mode == Mode.ONLINE:
            result = await self._process_online(audio_data, context, language)
            if result.get("success"):
                return result
            # Fallback to offline
            print("  ⚠️  API failed, falling back to offline...")
            return await self._process_offline(audio_data, context, language)
        
        else:  # HYBRID
            # Try online first for better quality
            result = await self._process_online(audio_data, context, language)
            if result.get("success"):
                return result
            
            # Fallback to offline
            print("  ⚠️  API unavailable, using offline mode...")
            return await self._process_offline(audio_data, context, language)
    
    async def _determine_mode(self) -> Mode:
        """Determine best mode based on connectivity"""
        if self.config.mode != Mode.OFFLINE:
            is_online = await self.connectivity_monitor.is_online()
            
            if is_online and self.api_client:
                return Mode.HYBRID if self.config.mode == Mode.HYBRID else Mode.ONLINE
        
        return Mode.OFFLINE
    
    async def _process_offline(
        self,
        audio_data: bytes,
        context: Optional[str],
        language: str
    ) -> dict:
        """Process using offline models"""
        try:
            # 1. STT
            print("  🎤 Transcribing (offline)...")
            stt_result = await self.offline_stt.transcribe(audio_data, language)
            
            if not stt_result.text:
                return {"success": False, "error": "STT failed"}
            
            print(f"  ✅ Transcribed: {stt_result.text}")
            
            # 2. Understanding
            print("  🧠 Analyzing intent (offline)...")
            understanding = await self.offline_understanding.analyze_intent(
                stt_result.text,
                context=context,
                language=language
            )
            
            print(f"  ✅ Intent: {understanding.action}")
            
            # 3. TTS
            print("  🔊 Generating response (offline)...")
            response_text = f"Executing {understanding.action} on {understanding.target}"
            tts_result = await self.offline_tts.speak(
                response_text,
                language=language
            )
            
            print(f"  ✅ Response generated")
            
            return {
                "success": True,
                "mode": "offline",
                "transcription": stt_result.text,
                "understanding": {
                    "action": understanding.action,
                    "target": understanding.target,
                    "parameters": understanding.parameters,
                    "confidence": understanding.confidence
                },
                "response_audio": tts_result.audio,
                "response_text": response_text
            }
        
        except Exception as e:
            print(f"  ❌ Offline processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_online(
        self,
        audio_data: bytes,
        context: Optional[str],
        language: str
    ) -> dict:
        """Process using V98 API"""
        if not self.api_client:
            return {"success": False, "error": "API not configured"}
        
        try:
            print("  🌐 Processing via V98 API...")
            
            result = await self.api_client.process_voice(
                audio_data,
                context=context,
                language=language
            )
            
            if result.get("success"):
                print(f"  ✅ API processing successful")
                return {
                    "success": True,
                    "mode": "online",
                    "transcription": result.get("transcription", ""),
                    "understanding": result.get("understanding", {}),
                    "response_audio": result.get("response_audio", b""),
                    "response_text": ""
                }
            else:
                return {"success": False, "error": result.get("error", "Unknown error")}
        
        except Exception as e:
            print(f"  ❌ API processing error: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_mode(self, mode: Mode):
        """Change operation mode"""
        self.config.mode = mode
        self.current_mode = mode
        print(f"✅ Mode changed to: {mode.value}")
    
    async def get_status(self) -> dict:
        """Get system status"""
        is_online = await self.connectivity_monitor.is_online()
        
        return {
            "current_mode": self.current_mode.value,
            "is_online": is_online,
            "offline_ready": self.offline_stt is not None,
            "api_ready": self.api_client is not None,
            "preferred_mode": self.config.mode.value
        }
    
    async def close(self):
        """Cleanup"""
        if self.api_client:
            await self.api_client.close()


# Example usage
async def main():
    """Test hybrid mode"""
    
    # Create config
    config = HybridConfig(
        mode=Mode.HYBRID,
        use_api_when_available=True,
        fallback_on_error=True
    )
    
    # Initialize
    hear_model = HybridHearModel(config)
    
    # Check status
    status = await hear_model.get_status()
    print(f"\n📊 System Status:")
    print(f"  Current Mode: {status['current_mode']}")
    print(f"  Online: {status['is_online']}")
    print(f"  Offline Ready: {status['offline_ready']}")
    print(f"  API Ready: {status['api_ready']}")
    
    # Test offline mode
    print(f"\n🧪 Testing Offline Mode...")
    await hear_model.set_mode(Mode.OFFLINE)
    
    # Simulate audio (would be real audio in practice)
    dummy_audio = b"audio_data"
    
    # This would process the audio
    # result = await hear_model.process_voice(dummy_audio)
    
    await hear_model.close()


if __name__ == "__main__":
    asyncio.run(main())
