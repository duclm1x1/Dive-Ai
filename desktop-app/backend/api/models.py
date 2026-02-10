"""
Models API - Model management endpoints

- GET /models - List all models
- GET /models/{id} - Get model details
- GET /models/stats - Usage statistics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

from ..llm.connections import (
    get_manager, ALL_MODELS, V98Model,
    CLAUDE_OPUS_46_THINKING, CLAUDE_SONNET_45
)
from ..llm.router import get_router
from ..llm.tokens import get_tracker, get_usage_stats


router = APIRouter(prefix="/models", tags=["Models"])


class ModelInfo(BaseModel):
    id: str
    name: str
    model: str
    priority: int
    supports_thinking: bool
    max_tokens: int
    temperature: float


class ModelStats(BaseModel):
    requests: int
    tokens: int
    cost_usd: float


@router.get("", response_model=List[ModelInfo])
async def list_models():
    """List all available Claude models"""
    return [
        ModelInfo(
            id=m.id,
            name=m.name,
            model=m.model,
            priority=m.priority,
            supports_thinking=m.supports_thinking,
            max_tokens=m.max_tokens,
            temperature=m.temperature
        )
        for m in ALL_MODELS
    ]


@router.get("/primary")
async def get_primary_model():
    """Get primary model"""
    return ModelInfo(
        id=CLAUDE_OPUS_46_THINKING.id,
        name=CLAUDE_OPUS_46_THINKING.name,
        model=CLAUDE_OPUS_46_THINKING.model,
        priority=CLAUDE_OPUS_46_THINKING.priority,
        supports_thinking=CLAUDE_OPUS_46_THINKING.supports_thinking,
        max_tokens=CLAUDE_OPUS_46_THINKING.max_tokens,
        temperature=CLAUDE_OPUS_46_THINKING.temperature
    )


@router.get("/{model_id}")
async def get_model(model_id: str):
    """Get specific model by ID"""
    manager = get_manager()
    model = manager.get_model_by_id(model_id)
    
    if not model:
        raise HTTPException(404, f"Model {model_id} not found")
    
    return ModelInfo(
        id=model.id,
        name=model.name,
        model=model.model,
        priority=model.priority,
        supports_thinking=model.supports_thinking,
        max_tokens=model.max_tokens,
        temperature=model.temperature
    )


@router.get("/stats/usage")
async def get_model_stats():
    """Get token usage statistics"""
    return get_usage_stats()


@router.get("/stats/routing")
async def get_routing_stats():
    """Get routing statistics"""
    router_ = get_router()
    return router_.get_stats()


@router.post("/recommend")
async def recommend_model(prompt: str, task_type: str = None):
    """Recommend best model for task"""
    router_ = get_router()
    
    from ..llm.router import TaskType
    
    if task_type:
        try:
            tt = TaskType[task_type.upper()]
            decision = router_.route("", task_type=tt)
        except KeyError:
            decision = router_.route(prompt)
    else:
        decision = router_.route(prompt)
    
    return {
        "recommended": decision.model.id,
        "name": decision.model.name,
        "reason": decision.reason,
        "confidence": decision.confidence
    }
