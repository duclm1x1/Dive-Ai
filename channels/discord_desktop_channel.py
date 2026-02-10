"""
Dive AI V29.3 - Discord Desktop Channel
Controls Discord desktop app via UI automation

No API needed - directly controls Discord app on PC
Full access to all Discord features
"""

import asyncio
import os
import subprocess
from typing import Dict, Any, Optional, List
from channels.desktop_channel_base import DesktopChannelBase


class DiscordDesktopChannel(DesktopChannelBase):
    """
    Discord Desktop Channel
    
    Controls Discord app installed on PC via UI automation
    """
    
    def __init__(self, discord_path: Optional[str] = None):
        """
        Initialize Discord desktop channel
        
        Args:
            discord_path: Path to Discord.exe (auto-detected if None)
        """
        
        # Auto-detect Discord path if not provided
        if not discord_path:
            discord_path = self._find_discord_path()
        
        super().__init__("Discord", discord_path)
        
        # Discord-specific settings
        self.gateway_channel_name = "Dive-AI"  # Default channel to monitor
        self.check_interval = 2.0  # seconds
    
    def _find_discord_path(self) -> Optional[str]:
        """Auto-detect Discord installation path"""
        
        possible_paths = [
            os.path.expanduser("~\\AppData\\Local\\Discord\\Update.exe"),
            os.path.expanduser("~\\AppData\\Roaming\\Discord\\Discord.exe"),
            "C:\\Program Files\\Discord\\Discord.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    async def launch_app(self) -> bool:
        """Launch Discord desktop app"""
        
        if not self.app_path:
            print("❌ Discord not found. Please install Discord desktop app.")
            return False
        
        try:
            print(f"🚀 Launching Discord from {self.app_path}")
            
            # Launch Discord
            if self.app_path.endswith("Update.exe"):
                # Discord portable version
                subprocess.Popen([self.app_path, "--processStart", "Discord.exe"])
            else:
                subprocess.Popen([self.app_path])
            
            # Wait for Discord to start
            await asyncio.sleep(5)
            
            self.is_running = True
            print("✅ Discord launched successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to launch Discord: {e}")
            return False
    
    async def find_chat_window(self, chat_name: str) -> bool:
        """
        Find and focus Discord chat/channel
        
        Uses Ctrl+K to open quick switcher, then types channel name
        """
        
        try:
            # Open quick switcher
            await self.press_key('ctrl')
            await asyncio.sleep(0.1)
            await self.press_key('k')
            await asyncio.sleep(0.5)
            
            # Type channel name
            await self.type_text(chat_name)
            await asyncio.sleep(0.5)
            
            # Press Enter to select
            await self.press_key('enter')
            await asyncio.sleep(0.5)
            
            print(f"✅ Switched to #{chat_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to find chat: {e}")
            return False
    
    async def send_message(self, chat_name: str, message: str) -> bool:
        """Send message to Discord channel"""
        
        try:
            # Switch to channel
            await self.find_chat_window(chat_name)
            
            # Type message
            await self.type_text(message)
            await asyncio.sleep(0.2)
            
            # Send (Enter)
            await self.press_key('enter')
            
            print(f"✅ Sent message to #{chat_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    async def read_messages(self, chat_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """
        Read recent messages from Discord channel
        
        Uses OCR or screenshot analysis
        """
        
        try:
            # Switch to channel
            await self.find_chat_window(chat_name)
            
            # Take screenshot of chat area
            screenshot_path = await self.screenshot()
            
            # TODO: Use OCR or vision model to extract messages
            # For now, return placeholder
            messages = [
                {
                    'author': 'User',
                    'content': 'Message extracted from screenshot',
                    'timestamp': 'now'
                }
            ]
            
            return messages
            
        except Exception as e:
            print(f"❌ Failed to read messages: {e}")
            return []
    
    async def monitor_channel(self, chat_name: str, callback):
        """
        Monitor Discord channel for new messages
        
        Args:
            chat_name: Channel name to monitor  
            callback: async function(message) to call for each new message
        """
        
        print(f"👀 Monitoring Discord #{chat_name}...")
        
        last_messages = []
        
        while self.is_running:
            try:
                # Read current messages
                current_messages = await self.read_messages(chat_name, count=5)
                
                # Find new messages
                for msg in current_messages:
                    if msg not in last_messages:
                        # New message detected
                        await callback(msg)
                
                last_messages = current_messages
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def start_gateway_bot(self, gateway_server):
        """
        Start Discord bot connected to Gateway
        
        Monitors Discord channel and forwards messages to Gateway
        """
        
        print(f"\n{'='*60}")
        print(f"🤖 STARTING DISCORD DESKTOP BOT")
        print(f"{'='*60}")
        print(f"Channel: #{self.gateway_channel_name}")
        print(f"Gateway: Connected")
        print(f"{'='*60}\n")
        
        # Launch Discord
        await self.launch_app()
        
        # Define message handler
        async def handle_message(message):
            """Forward Discord message to Gateway"""
            
            print(f"\n📩 New Discord message from {message['author']}")
            print(f"   Content: {message['content']}")
            
            # Send to Gateway
            result = await gateway_server.process_request(
                message=message['content'],
                channel='discord_desktop',
                user_id=message['author']
            )
            
            # Send response back to Discord
            await self.send_message(
                chat_name=self.gateway_channel_name,
                message=result['response']
            )
        
        # Start monitoring
        await self.monitor_channel(self.gateway_channel_name, handle_message)


# Test function
async def test_discord_channel():
    """Test Discord desktop channel"""
    
    print("\n🧪 Testing Discord Desktop Channel\n")
    
    # Create channel
    discord = DiscordDesktopChannel()
    
    # Launch Discord
    if await discord.launch_app():
        # Test sending message
        await discord.send_message("general", "Hello from Dive AI!")
        
        # Test reading messages
        messages = await discord.read_messages("general")
        print(f"Read {len(messages)} messages")


if __name__ == "__main__":
    asyncio.run(test_discord_channel())
