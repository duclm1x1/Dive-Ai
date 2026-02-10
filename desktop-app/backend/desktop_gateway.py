"""
Dive AI V29.4 Desktop - Enhanced Gateway Server
Now with V98 + AICoding Claude 4.6 Opus support
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
import base64
from datetime import datetime

# Import LLM system
from llm import (
    LLMConnectionManager, 
    TaskRouter, 
    Task, 
    TaskType,
    create_manager
)

# Desktop automation imports
try:
    import pyautogui
    import pytesseract
    from PIL import ImageGrab
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    print("⚠️ Desktop automation dependencies not available")

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Dive AI V29.4 Desktop Gateway",
    description="Gateway with V98 + AICoding Claude 4.6 Opus",
    version="29.4.0"
)

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM
llm_manager = create_manager()
task_router = TaskRouter()

# ============================================================
# Request Models
# ============================================================

class ChatRequest(BaseModel):
    message: str
    user_id: str = "desktop-user"
    channel: str = "desktop"
    session_id: str = "default"
    context: Optional[str] = None
    prefer_provider: str = "v98"
    max_tokens: int = 8192
    temperature: float = 0.7
    stream: bool = False

class TaskRequest(BaseModel):
    prompt: str
    task_type: str = "chat"  # chat, code, reasoning, vision, automation
    context: Optional[str] = None
    priority: int = 5
    prefer_provider: str = "v98"

class AutomationRequest(BaseModel):
    action: str
    params: Optional[Dict[str, Any]] = {}

# ============================================================
# LLM Endpoints
# ============================================================

@app.get("/health")
async def health():
    """Health check with LLM status"""
    llm_health = await llm_manager.health_check()
    return {
        "status": "healthy",
        "version": "29.4.0",
        "timestamp": datetime.now().isoformat(),
        "llm": {
            "v98": llm_health.get("v98", False),
            "aicoding": llm_health.get("aicoding", False)
        },
        "automation": AUTOMATION_AVAILABLE
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat with Claude 4.6 via V98 or AICoding"""
    try:
        messages = [{"role": "user", "content": request.message}]
        
        if request.context:
            messages.insert(0, {
                "role": "system",
                "content": f"Context: {request.context}"
            })
        
        response = await llm_manager.chat(
            messages,
            prefer=request.prefer_provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "response": response.content,
            "provider": response.provider,
            "model": response.model,
            "tokens_used": response.tokens_used,
            "latency_ms": response.latency_ms,
            "thinking": response.thinking
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response"""
    async def generate():
        messages = [{"role": "user", "content": request.message}]
        async for chunk in llm_manager.stream(messages, prefer=request.prefer_provider):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/task")
async def process_task(request: TaskRequest):
    """Process a task with routing"""
    try:
        task_type_map = {
            "chat": TaskType.CHAT,
            "code": TaskType.CODE,
            "reasoning": TaskType.REASONING,
            "vision": TaskType.VISION,
            "automation": TaskType.AUTOMATION
        }
        
        task = Task(
            id=f"task_{datetime.now().timestamp()}",
            type=task_type_map.get(request.task_type, TaskType.CHAT),
            prompt=request.prompt,
            context=request.context,
            priority=request.priority,
            prefer_provider=request.prefer_provider
        )
        
        result = await task_router.process(task)
        
        if result.success:
            return {
                "success": True,
                "response": result.response.content,
                "provider": result.response.provider,
                "latency_ms": result.response.latency_ms
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/llm/stats")
async def llm_stats():
    """Get LLM usage statistics"""
    return {
        "manager": llm_manager.get_stats(),
        "router": task_router.get_stats()
    }

@app.get("/llm/providers")
async def llm_providers():
    """List available LLM providers"""
    return {
        "providers": [
            {
                "id": "v98",
                "name": "V98 API",
                "model": "Claude 4.6 Opus",
                "is_primary": True,
                "is_healthy": llm_manager.v98.is_healthy
            },
            {
                "id": "aicoding",
                "name": "AICoding API",
                "model": "Claude 4.6 Opus",
                "is_primary": False,
                "is_healthy": llm_manager.aicoding.is_healthy
            }
        ]
    }

# ============================================================
# Automation Endpoints
# ============================================================

@app.get("/automation/screenshot")
async def capture_screenshot():
    """Capture desktop screenshot"""
    if not AUTOMATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Automation not available")
    
    try:
        screenshot = ImageGrab.grab()
        import io
        buffer = io.BytesIO()
        screenshot.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "screenshot": img_str,
            "timestamp": datetime.now().isoformat(),
            "size": {"width": screenshot.width, "height": screenshot.height}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation/execute")
async def execute_automation(request: AutomationRequest):
    """Execute automation action"""
    if not AUTOMATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="Automation not available")
    
    try:
        action = request.action
        params = request.params or {}
        
        if action == 'click':
            x, y = params.get('x', 100), params.get('y', 100)
            pyautogui.click(x, y)
            return {"status": "success", "action": "click", "position": [x, y]}
        
        elif action == 'type':
            text = params.get('text', '')
            pyautogui.write(text, interval=0.05)
            return {"status": "success", "action": "type", "text": text}
        
        elif action == 'keypress':
            key = params.get('key', 'enter')
            pyautogui.press(key)
            return {"status": "success", "action": "keypress", "key": key}
        
        elif action == 'screenshot':
            return await capture_screenshot()
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/automation/ocr")
async def perform_ocr():
    """Perform OCR on screenshot"""
    if not AUTOMATION_AVAILABLE:
        raise HTTPException(status_code=503, detail="OCR not available")
    
    try:
        screenshot = ImageGrab.grab()
        text = pytesseract.image_to_string(screenshot)
        return {"text": text, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Terminal & File System
# ============================================================

@app.post("/terminal/execute")
async def terminal_execute(command: str, cwd: str = "."):
    """Execute terminal command"""
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "output": result.stdout,
            "error": result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out", "code": -1}
    except Exception as e:
        return {"error": str(e), "code": -1}

@app.post("/fs/read")
async def fs_read(path: str):
    """Read file content"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return {"content": f.read(), "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fs/write")
async def fs_write(path: str, content: str):
    """Write file content"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"success": True, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🦞 Dive AI V29.4 Desktop Gateway")
    print("=" * 60)
    print(f"   LLM Providers:")
    print(f"     - V98 (Claude 4.6 Opus) - Primary")
    print(f"     - AICoding (Claude 4.6 Opus) - Backup")
    print(f"   Automation: {'✅ Available' if AUTOMATION_AVAILABLE else '❌ Unavailable'}")
    print(f"   Starting on http://127.0.0.1:1879")
    print("=" * 60)
    
    uvicorn.run(app, host="127.0.0.1", port=1879)
