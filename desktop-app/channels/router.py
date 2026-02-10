"""
Channel Router - Manage multiple channels

Centralizes channel management and routing.
"""

from typing import Dict, List, Optional
from enum import Enum


class ChannelType(Enum):
    ZALO_DESKTOP = "zalo_desktop"
    TELEGRAM = "telegram"
    DISCORD = "discord"


class ChannelRouter:
    """
    Manages multiple communication channels
    
    Usage:
        router = ChannelRouter()
        router.register("telegram", get_telegram_channel())
        router.start("telegram")
    """
    
    def __init__(self):
        self.channels: Dict[str, object] = {}
        self.active: List[str] = []
    
    def register(self, name: str, channel: object):
        """Register channel"""
        self.channels[name] = channel
    
    def unregister(self, name: str):
        """Unregister channel"""
        if name in self.channels:
            self.stop(name)
            del self.channels[name]
    
    def start(self, name: str):
        """Start channel"""
        if name not in self.channels:
            raise ValueError(f"Channel {name} not registered")
        
        channel = self.channels[name]
        
        if hasattr(channel, 'is_available') and not channel.is_available():
            raise RuntimeError(f"Channel {name} not available")
        
        if hasattr(channel, 'start'):
            channel.start()
            self.active.append(name)
    
    def stop(self, name: str):
        """Stop channel"""
        if name in self.channels and hasattr(self.channels[name], 'stop'):
            self.channels[name].stop()
            if name in self.active:
                self.active.remove(name)
    
    def stop_all(self):
        """Stop all channels"""
        for name in list(self.active):
            self.stop(name)
    
    def list_channels(self) -> List[Dict]:
        """List all channels"""
        result = []
        for name, channel in self.channels.items():
            available = True
            if hasattr(channel, 'is_available'):
                available = channel.is_available()
            
            result.append({
                "name": name,
                "available": available,
                "active": name in self.active
            })
        return result
    
    def get_status(self) -> Dict:
        """Get router status"""
        return {
            "total": len(self.channels),
            "active": len(self.active),
            "channels": self.list_channels()
        }


# Singleton
_router = None

def get_router() -> ChannelRouter:
    """Get channel router"""
    global _router
    if _router is None:
        _router = ChannelRouter()
        
        # Auto-register channels
        try:
            from .zalo_desktop import get_zalo_channel
            _router.register("zalo_desktop", get_zalo_channel())
        except:
            pass
        
        try:
            from .telegram import get_telegram_channel
            _router.register("telegram", get_telegram_channel())
        except:
            pass
        
        try:
            from .discord import get_discord_channel
            _router.register("discord", get_discord_channel())
        except:
            pass
    
    return _router
