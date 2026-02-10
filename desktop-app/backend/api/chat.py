"""
Chat API - Streaming chat endpoints

Provides:
- POST /chat - Standard chat
- POST /chat/stream - SSE streaming
- POST /chat/with-model - Chat with specific model
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import json

from ..llm.connections import get_manager, V98Model, ALL_MODELS
from ..llm.router import get_router, TaskType
from ..llm.streaming import V98StreamClient, StreamBuffer
from ..llm.tokens import record_usage


router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    system: Optional[str] = None
    model_id: Optional[str] = None
    task_type: Optional[str] = None  # code_generation, analysis, etc.
    max_tokens: int = 4096
    temperature: float = 0.7


class ChatResponse(BaseModel):
    content: str
    model: str
    tokens: int
    latency_ms: float
    thinking: Optional[str] = None


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Standard chat completion"""
    manager = get_manager()
    
    if not manager.is_available():
        raise HTTPException(503, "V98 not available - check API key")
    
    # Route to optimal model
    model = None
    if request.model_id:
        model = manager.get_model_by_id(request.model_id)
    elif request.task_type:
        model_router = get_router()
        task_type = TaskType[request.task_type.upper()]
        decision = model_router.route("", task_type=task_type)
        model = decision.model
    
    # Call V98
    if model:
        response = manager.chat_with_model(
            request.message,
            model,
            system=request.system,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    else:
        response = manager.chat(
            request.message,
            system=request.system,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
    
    if not response.success:
        raise HTTPException(500, response.error)
    
    # Record usage
    record_usage(response.model, 0, response.tokens_used)
    
    return ChatResponse(
        content=response.content,
        model=response.model,
        tokens=response.tokens_used,
        latency_ms=response.latency_ms,
        thinking=response.thinking
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """SSE streaming chat"""
    
    client = V98StreamClient()
    
    # Get model
    model = None
    if request.model_id:
        manager = get_manager()
        model = manager.get_model_by_id(request.model_id)
    
    messages = []
    if request.system:
        messages.append({"role": "system", "content": request.system})
    messages.append({"role": "user", "content": request.message})
    
    async def generate():
        buffer = StreamBuffer()
        buffer.start()
        
        async for chunk in client.stream_chat(
            messages,
            model=model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        ):
            buffer.add(chunk)
            yield f"data: {json.dumps({'content': chunk})}\n\n"
        
        buffer.end()
        yield f"data: {json.dumps({'done': True, 'stats': buffer.stats})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.get("/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": m.id,
                "name": m.name,
                "model": m.model,
                "priority": m.priority,
                "thinking": m.supports_thinking,
                "max_tokens": m.max_tokens
            }
            for m in ALL_MODELS
        ]
    }


@router.get("/status")
async def chat_status():
    """Get chat service status"""
    manager = get_manager()
    return manager.status()
