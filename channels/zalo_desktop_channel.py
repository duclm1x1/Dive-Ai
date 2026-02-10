"""
Dive AI V29.3 - Zalo Desktop Channel
Controls Zalo PC app via UI automation

Vietnamese messaging platform support
"""

import asyncio
import os
import subprocess
from typing import Dict, Any, Optional, List
from channels.desktop_channel_base import DesktopChannelBase


class ZaloDesktopChannel(DesktopChannelBase):
    """
    Zalo Desktop Channel
    
    Controls Zalo PC app via UI automation
    Vietnamese messaging platform
    """
    
    def __init__(self, zalo_path: Optional[str] = None):
        """
        Initialize Zalo desktop channel
        
        Args:
            zalo_path: Path to Zalo.exe (auto-detected if None)
        """
        
        if not zalo_path:
            zalo_path = self._find_zalo_path()
        
        super().__init__("Zalo", zalo_path)
        
        self.gateway_chat_name = "Dive AI"
        self.check_interval = 2.0
    
    def _find_zalo_path(self) -> Optional[str]:
        """Auto-detect Zalo PC installation"""
        
        possible_paths = [
            os.path.expanduser("~\\AppData\\Local\\Programs\\Zalo\\Zalo.exe"),
            "C:\\Program Files\\Zalo\\Zalo.exe"),
            "C:\\Program Files (x86)\\Zalo\\Zalo.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def launch_app(self) -> bool:
        """Launch Zalo PC app"""
        
        if not self.app_path:
            print("❌ Zalo not found. Please install Zalo PC from zalo.me")
            return False
        
        try:
            print(f"🚀 Launching Zalo from {self.app_path}")
            subprocess.Popen([self.app_path])
            
            await asyncio.sleep(4)
            
            self.is_running = True
            print("✅ Zalo launched")
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch Zalo: {e}")
            return False
    
    async def find_chat_window(self, chat_name: str) -> bool:
        """Find Zalo chat"""
        
        try:
            # Click search box (top of Zalo)
            # Coordinates may need adjustment
            await self.click_at(200, 50)
            await asyncio.sleep(0.3)
            
            # Type chat name
            await self.type_text(chat_name)
            await asyncio.sleep(0.5)
            
            # Select chat (Down + Enter)
            await self.press_key('down')
            await self.press_key('enter')
            await asyncio.sleep(0.5)
            
            print(f"✅ Opened chat: {chat_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to find chat: {e}")
            return False
    
    async def send_message(self, chat_name: str, message: str) -> bool:
        """Send message to Zalo chat"""
        
        try:
            await self.find_chat_window(chat_name)
            
            # Type message
            await self.type_text(message)
            await asyncio.sleep(0.2)
            
            # Send (Enter)
            await self.press_key('enter')
            
            print(f"✅ Sent message to {chat_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    async def read_messages(self, chat_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """Read messages from Zalo chat"""
        
        try:
            await self.find_chat_window(chat_name)
            
            # Screenshot chat
            screenshot_path = await self.screenshot()
            
            # TODO: OCR with Vietnamese support
            messages = []
            
            return messages
            
        except Exception as e:
            print(f"❌ Failed to read messages: {e}")
            return []
    
    async def start_gateway_bot(self, gateway_server):
        """Start Zalo bot connected to Gateway"""
        
        print(f"\n{'='*60}")
        print(f"🤖 STARTING ZALO DESKTOP BOT")
        print(f"{'='*60}")
        print(f"Chat: {self.gateway_chat_name}")
        print(f"{'='*60}\n")
        
        await self.launch_app()
        
        async def handle_message(message):
            """Forward to Gateway"""
            result = await gateway_server.process_request(
                message=message['content'],
                channel='zalo_desktop',
                user_id=message['author']
            )
            
            await self.send_message(
                chat_name=self.gateway_chat_name,
                message=result['response']
            )
        
        # Monitor loop
        while self.is_running:
            await asyncio.sleep(self.check_interval)


# Test
async def test_zalo():
    """Test Zalo channel"""
    print("\n🧪 Testing Zalo Desktop Channel\n")
    
    zalo = ZaloDesktopChannel()
    
    if await zalo.launch_app():
        await zalo.send_message("Dive AI", "Xin chào từ Dive AI!")


if __name__ == "__main__":
    asyncio.run(test_zalo())
