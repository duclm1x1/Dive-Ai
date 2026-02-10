"""
Zalo Desktop Channel - Monitor and respond to Zalo messages

Uses pyautogui to interact with Zalo desktop window.
"""

import time
import re
from typing import Optional, Dict, List
from dataclasses import dataclass

try:
    import pyautogui
    from PIL import ImageGrab
    AVAILABLE = True
except ImportError:
    AVAILABLE = False

from ..llm.connections import get_manager


@dataclass
class ZaloMessage:
    """Incoming Zalo message"""
    sender: str
    content: str
    timestamp: float


class ZaloDesktopChannel:
    """
    Monitor Zalo Desktop and respond using Claude
    
    Flow:
    1. Find Zalo window
    2. Monitor for new messages
    3. Extract text using OCR
    4. Send to Claude for response
    5. Type response back
    """
    
    WINDOW_TITLE = "Zalo"
    
    def __init__(self):
        self.manager = get_manager()
        self.running = False
        self.message_history: List[ZaloMessage] = []
    
    def is_available(self) -> bool:
        """Check if Zalo automation is available"""
        return AVAILABLE
    
    def find_window(self) -> bool:
        """Find Zalo window (placeholder)"""
        # Would use win32gui on Windows
        return True
    
    def focus_window(self):
        """Focus Zalo window"""
        # Placeholder
        pass
    
    def get_new_messages(self) -> List[ZaloMessage]:
        """Get new messages from screen (using OCR)"""
        # Placeholder - would use OCR to extract messages
        return []
    
    def send_message(self, text: str):
        """Send message to current chat"""
        if not AVAILABLE:
            return
        
        # Type message
        pyautogui.write(text, interval=0.02)
        time.sleep(0.1)
        
        # Press Enter to send
        pyautogui.press('enter')
    
    def generate_response(self, message: str, context: str = None) -> str:
        """Generate response using Claude"""
        system = """You are a helpful assistant responding to Zalo messages.
Keep responses concise and friendly.
Use Vietnamese if the user writes in Vietnamese."""
        
        response = self.manager.chat(message, system=system)
        return response.content if response.success else "Sorry, I couldn't process that."
    
    def process_message(self, message: ZaloMessage) -> str:
        """Process message and return response"""
        response = self.generate_response(message.content)
        self.send_message(response)
        return response
    
    def start_monitoring(self, interval: float = 1.0):
        """Start monitoring loop"""
        self.running = True
        
        while self.running:
            messages = self.get_new_messages()
            for msg in messages:
                self.process_message(msg)
            time.sleep(interval)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False


# Singleton
_channel = None

def get_zalo_channel() -> ZaloDesktopChannel:
    """Get Zalo channel"""
    global _channel
    if _channel is None:
        _channel = ZaloDesktopChannel()
    return _channel
