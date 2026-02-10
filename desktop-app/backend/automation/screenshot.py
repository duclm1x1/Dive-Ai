"""
Screenshot Service - Enhanced screen capture

- Full screen
- Region capture
- Screen recording (placeholder)
"""

import io
import base64
import time
from typing import Tuple, Optional
from datetime import datetime

try:
    from PIL import ImageGrab, Image
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


class ScreenshotService:
    """Screenshot capture service"""
    
    def __init__(self):
        self.last_capture: Optional[bytes] = None
        self.capture_count = 0
    
    def capture_full(self) -> dict:
        """Capture full screen"""
        if not AVAILABLE:
            return {"error": "PIL not available"}
        
        img = ImageGrab.grab()
        return self._process_image(img, "full")
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> dict:
        """Capture screen region"""
        if not AVAILABLE:
            return {"error": "PIL not available"}
        
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return self._process_image(img, "region")
    
    def capture_window(self, title: str) -> dict:
        """Capture specific window (Windows only)"""
        # Placeholder - requires win32gui
        return {"error": "Window capture not implemented"}
    
    def _process_image(self, img: Image.Image, type_: str) -> dict:
        """Process captured image"""
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        data = buffer.getvalue()
        self.last_capture = data
        self.capture_count += 1
        
        return {
            "type": type_,
            "base64": base64.b64encode(data).decode(),
            "size": {"width": img.width, "height": img.height},
            "bytes": len(data),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        if not AVAILABLE:
            return (0, 0)
        
        img = ImageGrab.grab()
        return (img.width, img.height)


# Singleton
_service = None

def get_screenshot_service() -> ScreenshotService:
    """Get screenshot service"""
    global _service
    if _service is None:
        _service = ScreenshotService()
    return _service


def capture() -> dict:
    """Quick capture"""
    return get_screenshot_service().capture_full()
