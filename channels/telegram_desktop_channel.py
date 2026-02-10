"""
Dive AI V29.3 - Telegram Desktop Channel
Controls Telegram desktop app via UI automation

No API needed - directly controls Telegram app on PC
"""

import asyncio
import os
import subprocess
from typing import Dict, Any, Optional, List
from channels.desktop_channel_base import DesktopChannelBase


class TelegramDesktopChannel(DesktopChannelBase):
    """
    Telegram Desktop Channel
    
    Controls Telegram Desktop app via UI automation
    """
    
    def __init__(self, telegram_path: Optional[str] = None):
        """
        Initialize Telegram desktop channel
        
        Args:
            telegram_path: Path to Telegram.exe (auto-detected if None)
        """
        
        if not telegram_path:
            telegram_path = self._find_telegram_path()
        
        super().__init__("Telegram", telegram_path)
        
        self.gateway_chat_name = "Dive AI Bot"
        self.check_interval = 2.0
    
    def _find_telegram_path(self) -> Optional[str]:
        """Auto-detect Telegram installation"""
        
        possible_paths = [
            os.path.expanduser("~\\AppData\\Roaming\\Telegram Desktop\\Telegram.exe"),
            "C:\\Program Files\\Telegram Desktop\\Telegram.exe",
            "C:\\Program Files (x86)\\Telegram Desktop\\Telegram.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def launch_app(self) -> bool:
        """Launch Telegram desktop app"""
        
        if not self.app_path:
            print("❌ Telegram not found. Please install Telegram Desktop.")
            return False
        
        try:
            print(f"🚀 Launching Telegram from {self.app_path}")
            subprocess.Popen([self.app_path])
            
            await asyncio.sleep(3)
            
            self.is_running = True
            print("✅ Telegram launched")
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch Telegram: {e}")
            return False
    
    async def find_chat_window(self, chat_name: str) -> bool:
        """Find Telegram chat using search"""
        
        try:
            # Open search (Ctrl+F in Telegram)
            await self.press_key('ctrl')
            await asyncio.sleep(0.1)
            await self.press_key('f')
            await asyncio.sleep(0.5)
            
            # Type chat name
            await self.type_text(chat_name)
            await asyncio.sleep(0.5)
            
            # Select first result
            await self.press_key('down')
            await self.press_key('enter')
            await asyncio.sleep(0.5)
            
            print(f"✅ Opened chat: {chat_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to find chat: {e}")
            return False
    
    async def send_message(self, chat_name: str, message: str) -> bool:
        """Send message to Telegram chat"""
        
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
        """Read recent messages from Telegram chat"""
        
        try:
            await self.find_chat_window(chat_name)
            
            # Screenshot chat area
            screenshot_path = await self.screenshot()
            
            # TODO: OCR/Vision to extract messages
            messages = []
            
            return messages
            
        except Exception as e:
            print(f"❌ Failed to read messages: {e}")
            return []
    
    async def start_gateway_bot(self, gateway_server):
        """Start Telegram bot connected to Gateway"""
        
        print(f"\n{'='*60}")
        print(f"🤖 STARTING TELEGRAM DESKTOP BOT")
        print(f"{'='*60}")
        print(f"Chat: {self.gateway_chat_name}")
        print(f"{'='*60}\n")
        
        await self.launch_app()
        
        async def handle_message(message):
            """Forward to Gateway"""
            result = await gateway_server.process_request(
                message=message['content'],
                channel='telegram_desktop',
                user_id=message['author']
            )
            
            await self.send_message(
                chat_name=self.gateway_chat_name,
                message=result['response']
            )
        
        # Monitor loop (simplified)
        while self.is_running:
            await asyncio.sleep(self.check_interval)
