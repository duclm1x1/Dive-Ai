"""
UI-TARS Desktop Proxy Endpoint
OpenAI-compatible API that routes to Dive AI V29.4 → v98store → Claude 4.6

This proxy allows UI-TARS Desktop to use your existing Dive AI infrastructure
with Claude 4.6 Opus Thinking via v98store.com.

Usage:
    uvicorn ui_tars_proxy:app --port 8765
    
Configure UI-TARS Desktop:
    VLM Base URL: http://localhost:8765/v1
    VLM API KEY: any-value (not validated)
    VLM Model Name: claude-opus-4-6-thinking
"""

import sys
import time
from pathlib import Path

# Add desktop-app backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "desktop-app" / "backend"))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

# Import Dive AI V29.4 LLM system
try:
    from llm.connections import (
        get_manager, 
        CLAUDE_OPUS_46_THINKING, 
        CLAUDE_SONNET_45,
        CLAUDE_SONNET_45_THINKING,
        CLAUDE_OPUS_45,
        CLAUDE_OPUS_45_THINKING,
        ALL_MODELS
    )
    from llm.v98_algorithm import V98Algorithm
except ImportError as e:
    print(f"Error importing Dive AI LLM modules: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)

# Initialize FastAPI
app = FastAPI(
    title="UI-TARS Dive AI Proxy",
    description="Connects UI-TARS Desktop to Dive AI V29.4 with Claude 4.6",
    version="1.0.0"
)

# Enable CORS for UI-TARS Desktop
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # UI-TARS runs locally
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ui-tars-proxy")


# ============================================================
# REQUEST/RESPONSE MODELS (OpenAI-compatible)
# ============================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "claude-opus-4-6-thinking"
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.3
    stream: Optional[bool] = False

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Usage


class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "dive-ai-v29"


# ============================================================
# MODEL MAPPING
# ============================================================

MODEL_MAP = {
    "claude-opus-4-6-thinking": CLAUDE_OPUS_46_THINKING,
    "claude-sonnet-4-5": CLAUDE_SONNET_45,
    "claude-sonnet-4-5-thinking": CLAUDE_SONNET_45_THINKING,
    "claude-opus-4-5": CLAUDE_OPUS_45,
    "claude-opus-4-5-thinking": CLAUDE_OPUS_45_THINKING,
    # Aliases for convenience
    "claude-4.6": CLAUDE_OPUS_46_THINKING,
    "claude-opus": CLAUDE_OPUS_46_THINKING,
    "default": CLAUDE_OPUS_46_THINKING,
}


# ============================================================
# SELF-MODIFICATION SYSTEM
# ============================================================

# Import self-modification modules
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from self_modification import (
        SelfAwareCodeAnalyzer,
        DiveCodeGenerator,
        SelfModificationEngine
    )
    SELF_MODIFICATION_ENABLED = True
except ImportError as e:
    logger.warning(f"Self-modification system not available: {e}")
    SELF_MODIFICATION_ENABLED = False


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "UI-TARS Dive AI Proxy",
        "version": "2.0.0",  # Upgraded with self-modification
        "status": "running",
        "backend": "Dive AI V29.4",
        "provider": "v98store.com",
        "models": list(MODEL_MAP.keys()),
        "features": {
            "chat": True,
            "self_modification": SELF_MODIFICATION_ENABLED
        },
        "endpoints": {
            "chat": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
            "self_mod": {
                "analyze": "/dive/analyze",
                "fix_bug": "/dive/fix-bug",
                "optimize": "/dive/optimize",
                "add_feature": "/dive/add-feature"
            }
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    manager = get_manager()
    
    return {
        "status": "healthy",
        "v98_connected": manager.client.is_available,
        "api_key_set": bool(manager.client.api_key),
        "timestamp": int(time.time())
    }


@app.get("/v1/models")
async def list_models():
    """List available models (OpenAI-compatible)"""
    created_time = int(time.time())
    
    models = [
        ModelInfo(
            id=model_id,
            created=created_time
        )
        for model_id in MODEL_MAP.keys()
    ]
    
    return {"object": "list", "data": models}


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """
    OpenAI-compatible chat completions endpoint
    
    Routes requests through Dive AI V29.4 algorithm system
    to v98store.com Claude 4.6
    """
    
    logger.info(f"Chat request: model={request.model}, messages={len(request.messages)}")
    
    try:
        # Select model
        v98_model = MODEL_MAP.get(request.model, CLAUDE_OPUS_46_THINKING)
        logger.info(f"Using Dive AI model: {v98_model.name}")
        
        # Convert messages to Dive AI format
        messages_dict = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Use V98Algorithm for execution with step tracking
        algorithm = V98Algorithm(name="UI-TARS-Proxy")
        
        # Extract user prompt (last user message)
        user_messages = [m for m in messages_dict if m["role"] == "user"]
        system_messages = [m for m in messages_dict if m["role"] == "system"]
        
        prompt = user_messages[-1]["content"] if user_messages else ""
        system = system_messages[0]["content"] if system_messages else None
        
        # Execute through algorithm
        result = algorithm.execute(
            prompt=prompt,
            system=system,
            model=v98_model,
            max_tokens=request.max_tokens
        )
        
        if result.status != "success":
            logger.error(f"Algorithm failed: {result.data.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.data.get("error", "Algorithm execution failed")
            )
        
        # Extract response content
        content = result.data.get("content", "")
        thinking = result.data.get("thinking", "")
        
        # If model supports thinking, prepend it
        if v98_model.supports_thinking and thinking:
            content = f"[Thinking]\n{thinking}\n\n[Response]\n{content}"
        
        # Build OpenAI-compatible response
        response_id = f"chatcmpl-{int(time.time() * 1000)}"
        
        response = ChatResponse(
            id=response_id,
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(
                        role="assistant",
                        content=content
                    ),
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=0,  # v98 doesn't return prompt tokens
                completion_tokens=result.tokens_used,
                total_tokens=result.tokens_used
            )
        )
        
        logger.info(f"Response: {len(content)} chars, {result.tokens_used} tokens, {result.total_time_ms:.0f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat_completions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/extensions/check")
async def check_model_availability(request: Request):
    """
    UI-TARS uses this endpoint to check if model is available
    """
    try:
        body = await request.json()
        model_name = body.get("model", "claude-opus-4-6-thinking")
        
        manager = get_manager()
        
        if not manager.client.is_available:
            return {
                "available": False,
                "error": "V98_API_KEY not set"
            }
        
        # Try a test call
        test_response = manager.client.chat(
            messages=[{"role": "user", "content": "test"}],
            model=MODEL_MAP.get(model_name, CLAUDE_OPUS_46_THINKING),
            max_tokens=10
        )
        
        return {
            "available": test_response.success,
            "model": model_name,
            "error": test_response.error if not test_response.success else None
        }
        
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }


# ============================================================
# STARTUP
# ============================================================

# ============================================================
# SELF-MODIFICATION ENDPOINTS
# ============================================================

class AnalyzeRequest(BaseModel):
    module_path: str

class FixBugRequest(BaseModel):
    module_path: str
    bug_description: str
    apply_fix: bool = False  # If True, applies the fix immediately

class OptimizeRequest(BaseModel):
    module_path: str
    optimization_goal: str
    apply_changes: bool = False

class AddFeatureRequest(BaseModel):
    module_path: str
    feature_description: str
    apply_changes: bool = False


@app.post("/dive/analyze")
async def analyze_code(request: AnalyzeRequest):
    """
    Analyze Dive AI code module
    
    UI-TARS command: "Analyze desktop-app/backend/llm/connections.py"
    """
    if not SELF_MODIFICATION_ENABLED:
        raise HTTPException(status_code=503, detail="Self-modification not available")
    
    try:
        analyzer = SelfAwareCodeAnalyzer()
        result = analyzer.analyze_module(request.module_path)
        
        return {
            "success": True,
            "module": request.module_path,
            "purpose": result.purpose,
            "complexity": result.complexity_score,
            "dependencies": result.dependencies,
            "issues": result.issues,
            "suggestions": result.suggestions,
            "understanding": result.understanding
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dive/fix-bug")
async def fix_bug(request: FixBugRequest):
    """
    Generate and optionally apply bug fix
    
    UI-TARS command: "Fix bug in connections.py: slow synchronous requests"
    """
    if not SELF_MODIFICATION_ENABLED:
        raise HTTPException(status_code=503, detail="Self-modification not available")
    
    try:
        if request.apply_fix:
            # Apply fix with safety checks
            engine = SelfModificationEngine()
            result = engine.fix_bug(request.module_path, request.bug_description)
            
            return {
                "success": result.success,
                "module": request.module_path,
                "bug": request.bug_description,
                "applied": True,
                "backup_path": result.backup_path,
                "diff": result.change.diff if result.success else None,
                "error": result.error
            }
        else:
            # Just generate the fix, don't apply
            generator = DiveCodeGenerator()
            change = generator.generate_fix(request.module_path, request.bug_description)
            
            return {
                "success": True,
                "module": request.module_path,
                "bug": request.bug_description,
                "applied": False,
                "diff": change.diff,
                "preview": "Fix generated. Set apply_fix=true to apply."
            }
    except Exception as e:
        logger.error(f"Bug fix failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dive/optimize")
async def optimize_code(request: OptimizeRequest):
    """
    Optimize Dive AI code
    
    UI-TARS command: "Optimize v98_algorithm.py for speed"
    """
    if not SELF_MODIFICATION_ENABLED:
        raise HTTPException(status_code=503, detail="Self-modification not available")
    
    try:
        if request.apply_changes:
            engine = SelfModificationEngine()
            result = engine.optimize_module(request.module_path, request.optimization_goal)
            
            return {
                "success": result.success,
                "module": request.module_path,
                "optimization": request.optimization_goal,
                "applied": True,
                "backup_path": result.backup_path,
                "error": result.error
            }
        else:
            generator = DiveCodeGenerator()
            change = generator.optimize_code(request.module_path, request.optimization_goal)
            
            return {
                "success": True,
                "module": request.module_path,
                "optimization": request.optimization_goal,
                "applied": False,
                "diff": change.diff,
                "preview": "Optimization generated. Set apply_changes=true to apply."
            }
    except Exception as e:
        logger.error(f"Optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dive/add-feature")
async def add_feature(request: AddFeatureRequest):
    """
    Add new feature to Dive AI
    
    UI-TARS command: "Add caching to algorithm system"
    """
    if not SELF_MODIFICATION_ENABLED:
        raise HTTPException(status_code=503, detail="Self-modification not available")
    
    try:
        if request.apply_changes:
            engine = SelfModificationEngine()
            result = engine.add_feature(request.module_path, request.feature_description)
            
            return {
                "success": result.success,
                "module": request.module_path,
                "feature": request.feature_description,
                "applied": True,
                "backup_path": result.backup_path,
                "error": result.error
            }
        else:
            generator = DiveCodeGenerator()
            change = generator.add_feature(request.module_path, request.feature_description)
            
            return {
                "success": True,
                "module": request.module_path,
                "feature": request.feature_description,
                "applied": False,
                "diff": change.diff,
                "preview": "Feature generated. Set apply_changes=true to apply."
            }
    except Exception as e:
        logger.error(f"Feature addition failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 60)
    logger.info("UI-TARS Dive AI Proxy v2.0.0")
    logger.info("=" * 60)
    logger.info("Backend: Dive AI V29.4")
    logger.info("Provider: v98store.com")
    logger.info("Primary Model: Claude 4.6 Opus Thinking")
    logger.info("")
    
    # Test connection
    manager = get_manager()
    if manager.client.is_available:
        logger.info("✅ V98 API Key: Set")
        logger.info(f"✅ Base URL: {manager.client.BASE_URL}")
        logger.info(f"✅ Available Models: {len(ALL_MODELS)}")
    else:
        logger.warning("⚠️  V98_API_KEY not set!")
        logger.warning("Set environment variable to enable API access")
    
    logger.info("")
    
    # Self-modification status
    if SELF_MODIFICATION_ENABLED:
        logger.info("🧠 Self-Modification: ENABLED")
        logger.info("   Dive AI can analyze and modify its own code!")
    else:
        logger.warning("⚠️  Self-Modification: DISABLED")
    
    logger.info("")
    logger.info("Configure UI-TARS Desktop:")
    logger.info("  VLM Base URL: http://localhost:8765/v1")
    logger.info("  VLM API KEY: any-value")
    logger.info("  VLM Model: claude-opus-4-6-thinking")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    
    print("\nStarting UI-TARS Dive AI Proxy...")
    print("Access at: http://localhost:8765")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8765,
        log_level="info"
    )
