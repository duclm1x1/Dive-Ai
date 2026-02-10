"""
Automation API - Desktop automation endpoints

- POST /automation/click
- POST /automation/type
- POST /automation/keypress
- GET /automation/screenshot
- POST /automation/execute - Natural language instruction
"""

import io
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Desktop automation
try:
    import pyautogui
    from PIL import ImageGrab
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


router = APIRouter(prefix="/automation", tags=["Automation"])


class ClickRequest(BaseModel):
    x: int
    y: int
    button: str = "left"  # left, right, middle
    clicks: int = 1


class TypeRequest(BaseModel):
    text: str
    interval: float = 0.05


class KeyRequest(BaseModel):
    key: str  # enter, tab, escape, etc.
    modifiers: List[str] = []  # ctrl, alt, shift


class ExecuteRequest(BaseModel):
    instruction: str  # Natural language instruction
    screenshot: bool = True  # Include screenshot in response


@router.get("/status")
async def automation_status():
    """Check automation availability"""
    return {
        "available": AVAILABLE,
        "libraries": {
            "pyautogui": AVAILABLE,
            "pillow": AVAILABLE
        }
    }


@router.post("/click")
async def click(request: ClickRequest):
    """Click at position"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        pyautogui.click(
            x=request.x,
            y=request.y,
            button=request.button,
            clicks=request.clicks
        )
        return {
            "success": True,
            "action": "click",
            "position": [request.x, request.y],
            "button": request.button
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/type")
async def type_text(request: TypeRequest):
    """Type text"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        pyautogui.write(request.text, interval=request.interval)
        return {
            "success": True,
            "action": "type",
            "chars": len(request.text)
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/keypress")
async def keypress(request: KeyRequest):
    """Press key with optional modifiers"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        if request.modifiers:
            pyautogui.hotkey(*request.modifiers, request.key)
        else:
            pyautogui.press(request.key)
        
        return {
            "success": True,
            "action": "keypress",
            "key": request.key,
            "modifiers": request.modifiers
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/screenshot")
async def screenshot():
    """Capture screenshot"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        img = ImageGrab.grab()
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return {
            "screenshot": base64.b64encode(buffer.getvalue()).decode(),
            "size": {"width": img.width, "height": img.height},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/screenshot/region")
async def screenshot_region(x: int, y: int, width: int, height: int):
    """Capture screenshot of region"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return {
            "screenshot": base64.b64encode(buffer.getvalue()).decode(),
            "region": {"x": x, "y": y, "width": width, "height": height},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/position")
async def get_mouse_position():
    """Get current mouse position"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        pos = pyautogui.position()
        return {"x": pos.x, "y": pos.y}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/screen/size")
async def get_screen_size():
    """Get screen size"""
    if not AVAILABLE:
        raise HTTPException(503, "Automation not available")
    
    try:
        size = pyautogui.size()
        return {"width": size.width, "height": size.height}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/execute")
async def execute_instruction(request: ExecuteRequest):
    """
    Execute natural language instruction
    
    This is a placeholder for UI-TARS integration.
    In production, this would use the UI-TARS model.
    """
    return {
        "status": "pending",
        "instruction": request.instruction,
        "message": "UI-TARS integration pending. Manual execution required.",
        "timestamp": datetime.now().isoformat()
    }
