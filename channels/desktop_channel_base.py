"""
Dive AI V29.3 - Desktop Channel Base
Base class for desktop-based channels (Discord, Telegram, Zalo)

Uses UI automation to control desktop apps instead of APIs
This allows full access to all features without API limitations
"""

import asyncio
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import pyautogui
import time


class DesktopChannelBase(ABC):
    """
    Base class for desktop-based channels
    
    Uses UI-TARS or direct UI automation to control
    Discord/Telegram/Zalo desktop applications
    """
    
    def __init__(self, app_name: str, app_path: Optional[str] = None):
        """
        Initialize desktop channel
        
        Args:
            app_name: Application name (e.g., "Discord", "Telegram")
            app_path: Path to executable (optional)
        """
        self.app_name = app_name
        self.app_path = app_path
        self.is_running = False
        
        # UI automation settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.5
        
        print(f"🖥️ {app_name} Desktop Channel initialized")
    
    @abstractmethod
    async def launch_app(self) -> bool:
        """Launch the desktop application"""
        pass
    
    @abstractmethod
    async def find_chat_window(self, chat_name: str) -> bool:
        """Find and focus specific chat window"""
        pass
    
    @abstractmethod
    async def send_message(self, chat_name: str, message: str) -> bool:
        """Send message to specific chat"""
        pass
    
    @abstractmethod
    async def read_messages(self, chat_name: str, count: int = 10) -> List[Dict[str, Any]]:
        """Read recent messages from chat"""
        pass
    
    async def type_text(self, text: str):
        """Type text using keyboard automation"""
        pyautogui.write(text, interval=0.05)
    
    async def press_key(self, key: str):
        """Press a key"""
        pyautogui.press(key)
    
    async def click_at(self, x: int, y: int):
        """Click at specific coordinates"""
        pyautogui.click(x, y)
    
    async def find_image(self, image_path: str, confidence: float = 0.8) -> Optional[tuple]:
        """
        Find image on screen
        
        Returns:
            (x, y) coordinates or None
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            if location:
                return pyautogui.center(location)
        except Exception as e:
            print(f"⚠️ Image not found: {e}")
        return None
    
    async def screenshot(self, region: Optional[tuple] = None) -> str:
        """
        Take screenshot
        
        Args:
            region: (x, y, width, height) or None for full screen
        
        Returns:
            Path to screenshot file
        """
        timestamp = int(time.time())
        filename = f"screenshots/{self.app_name}_{timestamp}.png"
        
        if region:
            im = pyautogui.screenshot(region=region)
        else:
            im = pyautogui.screenshot()
        
        im.save(filename)
        return filename
