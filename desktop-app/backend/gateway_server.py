"""
Dive AI Gateway Server
All settings loaded from config/app.json and llm/config.yaml
No hardcoded values.
"""

import os
import sys
import asyncio
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dive_core'))
sys.path.insert(0, os.path.dirname(__file__))

# Load .env if exists
BACKEND_DIR = Path(__file__).parent
env_file = BACKEND_DIR / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

# Load app config
APP_CONFIG_PATH = BACKEND_DIR / "config" / "app.json"
def load_app_config() -> Dict:
    if APP_CONFIG_PATH.exists():
        with open(APP_CONFIG_PATH) as f:
            return json.load(f)
    return {"app": {"name": "Dive AI", "version": "29.7.0"}, "server": {"host": "127.0.0.1", "port": 1879}}

APP_CFG = load_app_config()
APP_NAME = APP_CFG.get("app", {}).get("name", "Dive AI")
APP_VERSION = APP_CFG.get("app", {}).get("version", "29.7.0")
SERVER_HOST = os.getenv("GATEWAY_HOST", APP_CFG.get("server", {}).get("host", "127.0.0.1"))
SERVER_PORT = int(os.getenv("GATEWAY_PORT", APP_CFG.get("server", {}).get("port", 1879)))
FEATURES = APP_CFG.get("features", {})

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# Import LLM connections
from llm.connections import (
    V98ConnectionManager, get_manager, quick_chat,
    ALL_MODELS, print_summary
)

# Import agent modules
from pc_operator import pc_operator, PCOperator
from action_executor import ActionExecutor
from agent_loop import AgentLoop

# Import storage and memory
from local_storage import LocalStorage, get_storage
from memory_manager import MemoryManager

# Import Algorithm Service (central algorithm + skill registry)
try:
    from dive_core.algorithm_service import AlgorithmService, get_algorithm_service
    HAS_ALGO_SERVICE = True
except ImportError:
    HAS_ALGO_SERVICE = False
    AlgorithmService = None

# Import Supabase (optional)
try:
    from supabase_client import get_supabase_client, SupabaseClient
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    SupabaseClient = None
    def get_supabase_client(): return None

# ============================================================
# Pydantic Models
# ============================================================

class ChatRequest(BaseModel):
    message: str
    system: Optional[str] = None
    model_id: Optional[str] = None
    stream: Optional[bool] = False
    conversation_id: Optional[str] = None

class CodeRequest(BaseModel):
    action: str  # generate, review, debug, refactor, test, explain
    code: Optional[str] = None
    task: Optional[str] = None
    language: Optional[str] = "python"
    file_path: Optional[str] = None

class ComputerRequest(BaseModel):
    instruction: str
    mode: Optional[str] = "local"  # local, browser, remote

class MemoryRequest(BaseModel):
    action: str  # store, recall, search, list, clear
    project: Optional[str] = "default"
    content: Optional[str] = None
    key: Optional[str] = None

class SelfModifyRequest(BaseModel):
    action: str  # analyze, fix, test, improve
    target: Optional[str] = None  # file path or module name
    issue: Optional[str] = None
    auto_apply: Optional[bool] = False

class AutomationRequest(BaseModel):
    action: str
    params: Optional[Dict[str, Any]] = {}

class TerminalRequest(BaseModel):
    command: str
    cwd: Optional[str] = None

class FileRequest(BaseModel):
    path: str
    content: Optional[str] = None

class OrchestrateRequest(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = {}
    max_steps: Optional[int] = 10

class AlgorithmCreateRequest(BaseModel):
    name: str
    description: str
    logic_type: Optional[str] = "transform"
    logic_code: Optional[str] = ""
    tags: Optional[List[str]] = []
    verifier_type: Optional[str] = "none"
    auto_deploy: Optional[bool] = True

class AlgorithmExecuteRequest(BaseModel):
    inputs: Optional[Dict[str, Any]] = {}
    context: Optional[Dict[str, Any]] = {}

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title=f"{APP_NAME} Gateway",
    version=APP_VERSION,
    description=f"{APP_NAME} - Multi-provider LLM Gateway"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
llm_manager: V98ConnectionManager = None
supabase_client: SupabaseClient = None
project_memory: Dict[str, Dict[str, Any]] = {}
action_exec: ActionExecutor = None
agent: AgentLoop = None
DIVE_CORE_PATH = Path(__file__).parent / "dive_core"
APP_PATH = Path(__file__).parent.parent

# ============================================================
# Startup
# ============================================================

# Global storage and memory
storage: Optional[LocalStorage] = None
memory: Optional[MemoryManager] = None

@app.on_event("startup")
async def startup():
    global llm_manager, supabase_client, action_exec, agent, storage, memory
    llm_manager = get_manager()
    
    # Initialize local storage and memory
    storage = get_storage()
    memory = MemoryManager(storage=storage)
    
    # Initialize action executor and agent loop
    action_exec = ActionExecutor(
        pc_operator=pc_operator,
        app_path=str(APP_PATH),
        llm_chat_fn=quick_chat
    )
    agent = AgentLoop(
        pc_operator=pc_operator,
        action_executor=action_exec,
        llm_chat_fn=quick_chat
    )
    
    if HAS_SUPABASE:
        try:
            supabase_client = get_supabase_client()
            sb_status = 'Connected' if supabase_client and supabase_client.is_connected else 'Offline'
        except Exception:
            supabase_client = None
            sb_status = 'Not available'
    else:
        supabase_client = None
        sb_status = 'Not installed'
    
    conv_count = len(storage.list_conversations())
    mem_facts = len(memory._long_term.get('user_facts', []))
    print_summary()
    print(f"\n🤿 {APP_NAME} Gateway v{APP_VERSION}")
    print(f"📁 Dive Core: {DIVE_CORE_PATH}")
    print(f"💾 Storage: {storage.base_path} ({conv_count} conversations)")
    print(f"🧠 Memory: {mem_facts} facts")
    print(f"☁️  Supabase: {sb_status}")
    print(f"🌐 Server: http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"🤖 Agent: Ready (PC control: {'ON' if pc_operator.allowed else 'OFF - press F3'})")

    # Initialize Algorithm Service
    if HAS_ALGO_SERVICE:
        try:
            algo_svc = get_algorithm_service()
            algo_stats = algo_svc.get_stats()
            print(f"🧬 Algorithms: {algo_stats['skills_loaded']} skills, {algo_stats['auto_algorithms_created']} auto-algos, {algo_stats['auto_algorithms_deployed']} deployed")
        except Exception as e:
            print(f"⚠️ Algorithm Service: {e}")

# ============================================================
# Core Endpoints
# ============================================================

@app.get("/health")
async def health_check():
    status = llm_manager.status() if llm_manager else {}
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat(),
        "llm": {
            "provider": status.get("primary_model", "None"),
            "models": status.get("total_connections", 0),
            "available": status.get("primary_available", False),
            "primary": status.get("primary_model", "None")
        },
        "features": FEATURES,
        "automation": True
    }

@app.get("/models")
async def get_models():
    """All models flat list"""
    return {
        "models": [m.to_dict() for m in llm_manager.all_models] if llm_manager else [],
        "total": len(llm_manager.all_models) if llm_manager else 0
    }

@app.get("/models/list")
async def get_models_grouped():
    """Models grouped by vendor with status and latency"""
    if not llm_manager:
        return {"groups": {}, "total": 0}
    return {
        "groups": llm_manager.models_grouped_by_vendor(),
        "total": len(llm_manager.all_models),
        "default_model": llm_manager.get_default_model().id if llm_manager.get_default_model() else None
    }

# ============================================================
# Provider Management
# ============================================================

@app.get("/providers")
async def get_providers():
    """List all providers with status"""
    if not llm_manager:
        return {"providers": []}
    return {
        "providers": [p.to_dict() for p in llm_manager.providers.values()]
    }

@app.post("/providers/{provider_id}/test")
async def test_provider(provider_id: str):
    """Test provider connection"""
    if not llm_manager:
        raise HTTPException(status_code=503, detail="LLM not initialized")
    result = llm_manager.test_provider(provider_id)
    return result

@app.post("/providers/add")
async def add_provider(request: Request):
    """Add new provider"""
    data = await request.json()
    result = llm_manager.add_provider(
        pid=data.get("id"),
        name=data.get("name"),
        base_url=data.get("base_url"),
        api_key_env=data.get("api_key_env"),
        models=data.get("models", [])
    )
    return result

@app.put("/providers/{provider_id}")
async def update_provider(provider_id: str, request: Request):
    """Update provider config"""
    data = await request.json()
    return llm_manager.update_provider(provider_id, data)

@app.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    """Remove provider"""
    return llm_manager.remove_provider(provider_id)

# ============================================================
# Settings
# ============================================================

@app.get("/settings")
async def get_settings():
    """Get all app settings"""
    return {
        "app": {"name": APP_NAME, "version": APP_VERSION},
        "server": {"host": SERVER_HOST, "port": SERVER_PORT},
        "features": FEATURES,
        "providers": [p.to_dict() for p in llm_manager.providers.values()] if llm_manager else [],
        "routing": llm_manager.config.get("routing", {}) if llm_manager else {},
        "performance": llm_manager.config.get("performance", {}) if llm_manager else {},
    }

@app.put("/settings")
async def update_settings(request: Request):
    """Update settings"""
    data = await request.json()
    if "routing" in data and llm_manager:
        llm_manager.config["routing"] = data["routing"]
        from llm.connections import save_config
        save_config(llm_manager.config)
    return {"success": True}

# ============================================================
# Automation Control
# ============================================================

automation_state = {"running": False, "current_action": None, "allowed": False}

@app.post("/automation/toggle")
async def toggle_automation():
    """F3 toggle: allow/disallow bot PC control"""
    automation_state["allowed"] = not automation_state["allowed"]
    # Sync with pc_operator
    pc_operator.set_allowed(automation_state["allowed"])
    return {
        "allowed": automation_state["allowed"],
        "message": "PC control ENABLED" if automation_state["allowed"] else "PC control DISABLED"
    }

@app.get("/automation/state")
async def get_automation_state():
    """Get current automation state"""
    automation_state["allowed"] = pc_operator.allowed  # Keep in sync
    return automation_state

@app.post("/automation/stop")
async def stop_automation():
    """Emergency stop all automation"""
    automation_state["running"] = False
    automation_state["current_action"] = None
    pc_operator.set_allowed(False)
    automation_state["allowed"] = False
    # Also stop agent loop if running
    if agent:
        agent.stop()
    return {"stopped": True, "message": "All automation stopped, PC control disabled"}

# ============================================================
# Chat Endpoint (with action execution + self-debug)
# ============================================================

DIVE_AI_SYSTEM_PROMPT = f"""You are Dive AI v{APP_VERSION}, an intelligent AI assistant integrated into a desktop application.

IMPORTANT: ALWAYS respond in English, regardless of the user's language.

You have SELF-AWARENESS of your own application:
- Backend: FastAPI gateway at {SERVER_HOST}:{SERVER_PORT}
- Frontend: React + Electron desktop app
- LLM: Connected via V98 API (OpenAI-compatible)
- Features: {', '.join(k for k, v in FEATURES.items() if v)}
- App Path: {APP_PATH}
- Core Path: {DIVE_CORE_PATH}
- Python venv: D:/Antigravity/Dive AI/.venv/Scripts/python.exe
- Pip venv: D:/Antigravity/Dive AI/.venv/Scripts/pip.exe
- ALWAYS use the full venv path for pip/python commands

You can help the user with:
1. SELF-DEBUG: Analyze and fix issues in the Dive AI app itself
2. CODE: Write, review, debug, and refactor code
3. PC CONTROL: Click, type, scroll, take screenshots, open apps
4. TERMINAL: Run commands on the system
5. CHAT: General conversation and knowledge

When you need to PERFORM ACTIONS, use these XML tags in your response:
- <execute_command>command here</execute_command>  — run a terminal command
- <read_file>file/path</read_file>  — read a file's contents
- <write_file path="file/path">content</write_file>  — write to a file
- <screenshot/>  — capture the current screen
- <click x="100" y="200"/>  — click at screen coordinates
- <type_text>text to type</type_text>  — type text on screen
- <hotkey>ctrl+c</hotkey>  — press keyboard shortcut
- <scroll amount="-3"/>  — scroll (negative = down, positive = up)
- <open_app>chrome</open_app>  — open an application
- <self_debug target="file.py" issue="description"/>  — debug own source code

SELF-HEALING BEHAVIOR:
When an action fails, you will AUTOMATICALLY receive the error and must:
1. Analyze what went wrong
2. Fix the issue (install missing packages, correct paths, etc.)
3. Retry the action

PC control actions (click, type, scroll, etc.) require F3 to be enabled.
Always explain what you're doing before performing actions.
Be concise, helpful, and proactive. You ARE the application."""

MAX_SELF_HEAL_ROUNDS = 3

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not llm_manager:
            raise HTTPException(status_code=503, detail="LLM not initialized")
        
        system = request.system or DIVE_AI_SYSTEM_PROMPT
        
        # Conversation management: auto-create if not provided
        conv_id = request.conversation_id
        if not conv_id and storage:
            convs = storage.list_conversations()
            if convs:
                conv_id = convs[0]["id"]  # Most recent
            else:
                conv_id = storage.create_conversation("New Chat")
        
        # Set memory to this conversation
        if memory and conv_id:
            memory.set_conversation(conv_id)
        
        # Save user message to storage
        if storage and conv_id:
            storage.save_message(conv_id, "user", request.message)
        
        start_time = datetime.now()
        message = request.message
        all_action_results = []
        all_thinking = []
        final_response = ""
        total_tokens = 0
        
        # Build context from memory (recent messages + long-term facts)
        context_messages = []
        if memory:
            context_messages = memory.build_context_messages(request.message)
        
        # Self-healing loop: up to MAX_SELF_HEAL_ROUNDS retry rounds
        for round_num in range(1, MAX_SELF_HEAL_ROUNDS + 1):
            # Use memory context for first round, plain message for retries
            if round_num == 1 and context_messages:
                result = await quick_chat(
                    message=message,
                    system=system,
                    model_id=request.model_id,
                    messages=context_messages if len(context_messages) > 1 else None
                )
            else:
                result = await quick_chat(
                    message=message,
                    system=system,
                    model_id=request.model_id
                )
            
            response_text = result.get("content", "")
            thinking = result.get("thinking", None)
            total_tokens += result.get("tokens", 0)
            
            if thinking:
                all_thinking.append(thinking)
            
            # Parse and execute actions
            if action_exec and action_exec.has_actions(response_text):
                action_results_raw = action_exec.parse_and_execute(
                    response_text,
                    automation_allowed=pc_operator.allowed
                )
                action_results = [r.to_dict() for r in action_results_raw]
                all_action_results.extend(action_results)
                
                # Log actions
                if storage:
                    for ar in action_results:
                        storage.log_action(ar)
                
                # Check if any actions FAILED
                failed_actions = [r for r in action_results_raw if not r.success]
                
                if failed_actions and round_num < MAX_SELF_HEAL_ROUNDS:
                    error_feedback = "\n".join([
                        f"❌ {r.action} FAILED: {r.error}" for r in failed_actions
                    ])
                    response_text += f"\n\n🔄 **Self-healing (attempt {round_num}/{MAX_SELF_HEAL_ROUNDS})...**"
                    results_text = action_exec.format_results_for_display(action_results_raw)
                    response_text += results_text
                    final_response += response_text + "\n\n"
                    
                    message = f"""PREVIOUS ACTIONS FAILED. Please analyze the errors and fix them.

ERRORS:
{error_feedback}

IMPORTANT: Fix the root cause. For example:
- If 'pip' is not recognized, use the full venv path: "D:/Antigravity/Dive AI/.venv/Scripts/pip.exe" install <package>
- If a module is missing, install it first
- If a file is not found, check the correct path

Now fix the issue and retry:"""
                    continue
                else:
                    results_text = action_exec.format_results_for_display(action_results_raw)
                    response_text += results_text
            
            final_response += response_text
            break
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        combined_thinking = "\n\n---\n\n".join(all_thinking) if all_thinking else None
        model_name = result.get("model", "unknown")
        
        # Save assistant response to storage
        if storage and conv_id:
            storage.save_message(
                conv_id, "assistant", final_response,
                thinking=combined_thinking,
                model=model_name,
                latency_ms=round(latency, 2),
                actions=all_action_results,
                tokens=total_tokens,
            )
        
        # Update memory
        if memory:
            memory.add_message("user", request.message)
            memory.add_message("assistant", final_response, thinking=combined_thinking, model=model_name)
            memory.extract_facts(request.message, final_response)
        
        return {
            "response": final_response,
            "thinking": combined_thinking,
            "model": model_name,
            "tokens": total_tokens,
            "latency_ms": round(latency, 2),
            "success": result.get("success", False),
            "error": result.get("error", None),
            "actions": all_action_results,
            "self_heal_rounds": round_num if round_num > 1 else 0,
            "conversation_id": conv_id,
        }
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# Conversation Endpoints
# ============================================================

@app.get("/conversations")
async def list_conversations():
    """List all conversations."""
    if not storage:
        return {"conversations": [], "total": 0}
    convs = storage.list_conversations()
    return {"conversations": convs, "total": len(convs)}

class CreateConvRequest(BaseModel):
    title: Optional[str] = "New Chat"

@app.post("/conversations")
async def create_conversation(request: CreateConvRequest):
    """Create a new conversation."""
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    conv_id = storage.create_conversation(request.title)
    return {"conversation_id": conv_id, "title": request.title}

@app.get("/conversations/{conv_id}/messages")
async def get_conversation_messages(conv_id: str, limit: int = 100):
    """Get messages from a conversation."""
    if not storage:
        return {"messages": []}
    messages = storage.get_messages(conv_id, limit=limit)
    return {"messages": messages, "conversation_id": conv_id}

@app.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str):
    """Delete a conversation."""
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    storage.delete_conversation(conv_id)
    return {"deleted": True, "conversation_id": conv_id}

# ============================================================
# Storage & Settings Endpoints
# ============================================================

@app.get("/storage/stats")
async def get_storage_stats():
    """Get storage usage stats."""
    if not storage:
        return {"error": "Storage not initialized"}
    return storage.get_storage_stats()

@app.post("/storage/clear")
async def clear_storage():
    """Clear all conversation data (keeps settings)."""
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    convs = storage.list_conversations()
    for c in convs:
        storage.delete_conversation(c["id"])
    return {"cleared": True, "deleted_count": len(convs)}

# ============================================================
# Connection Management Endpoints
# ============================================================

@app.get("/settings/connections")
async def get_connections():
    """Get connection settings (keys masked)."""
    if not storage:
        return {"connections": {}}
    return {"connections": storage.get_connections_masked()}

class SaveConnectionRequest(BaseModel):
    provider_id: str
    url: Optional[str] = None
    api_key: Optional[str] = None

@app.post("/settings/connections")
async def save_connection(request: SaveConnectionRequest):
    """Save connection settings for a provider."""
    if not storage:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    storage.save_connection(request.provider_id, request.url, request.api_key)
    return {"saved": True, "provider_id": request.provider_id}

@app.post("/settings/connections/reload")
async def reload_connections():
    """Hot-reload LLM connections after key change."""
    global llm_manager
    try:
        # Re-read .env
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        load_dotenv(env_path, override=True)
        
        # Re-initialize LLM manager
        llm_manager = get_manager()
        return {"reloaded": True, "status": llm_manager.status() if llm_manager else {}}
    except Exception as e:
        return {"reloaded": False, "error": str(e)}

# ============================================================
# Memory Endpoints
# ============================================================

@app.get("/memory/status")
async def get_memory_status():
    """Get memory system status."""
    if not memory:
        return {"initialized": False}
    return memory.get_status()

class AddFactRequest(BaseModel):
    fact: str

@app.post("/memory/fact")
async def add_memory_fact(request: AddFactRequest):
    """Manually add a fact to long-term memory."""
    if not memory:
        raise HTTPException(status_code=503, detail="Memory not initialized")
    memory.add_fact(request.fact)
    return {"added": True, "fact": request.fact}

@app.post("/memory/clear")
async def clear_memory():
    """Clear long-term memory."""
    if not memory:
        raise HTTPException(status_code=503, detail="Memory not initialized")
    memory.clear_long_term()
    return {"cleared": True}

# ============================================================
# Agent Loop Endpoints (autonomous PC control)
# ============================================================

class AgentRunRequest(BaseModel):
    instruction: str
    max_steps: Optional[int] = 20

@app.post("/agent/run")
async def agent_run(request: AgentRunRequest):
    """Start autonomous agent task"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    if not pc_operator.allowed:
        return {"error": "PC control disabled. Press F3 to enable.", "success": False}
    
    # Run in background
    result = await agent.run(request.instruction, request.max_steps)
    return result

@app.post("/agent/stop")
async def agent_stop():
    """Emergency stop agent"""
    if agent:
        agent.stop()
    return {"stopped": True}

@app.post("/agent/pause")
async def agent_pause():
    """Pause agent"""
    if agent:
        agent.pause()
    return {"paused": True}

@app.post("/agent/resume")
async def agent_resume():
    """Resume agent"""
    if agent:
        agent.resume()
    return {"resumed": True}

@app.get("/agent/status")
async def agent_status():
    """Get agent status"""
    if not agent:
        return {"status": "not_initialized"}
    return agent.get_status()

# ============================================================
# File Upload Endpoint (for drag & drop)
# ============================================================

from fastapi import UploadFile, File as FastAPIFile

@app.post("/chat/upload")
async def chat_with_file(file: UploadFile = FastAPIFile(...)):
    """Upload a file and return its contents for chat context"""
    try:
        content = await file.read()
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            import base64
            text = f"[Binary file: {file.filename}, {len(content)} bytes, base64: {base64.b64encode(content[:1000]).decode()}...]"
        
        return {
            "filename": file.filename,
            "size": len(content),
            "content": text[:10000],  # Limit to 10KB
            "truncated": len(content) > 10000
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Code Actions (generate, review, debug, refactor)
# ============================================================

@app.post("/api/code")
async def code_action(request: CodeRequest):
    """Code generation, review, debugging, refactoring using Claude"""
    try:
        action = request.action.lower()
        
        prompts = {
            "generate": f"Generate {request.language} code for: {request.task}",
            "review": f"Review this {request.language} code and suggest improvements:\n```{request.language}\n{request.code}\n```",
            "debug": f"Find and fix bugs in this {request.language} code:\n```{request.language}\n{request.code}\n```",
            "refactor": f"Refactor this {request.language} code for better performance and readability:\n```{request.language}\n{request.code}\n```",
            "test": f"Generate comprehensive tests for this {request.language} code:\n```{request.language}\n{request.code}\n```",
            "explain": f"Explain this {request.language} code in detail:\n```{request.language}\n{request.code}\n```"
        }
        
        prompt = prompts.get(action, request.task or request.code)
        
        result = await quick_chat(
            message=prompt,
            system=f"You are an expert {request.language} developer. Be concise and provide working code."
        )
        
        return {
            "action": action,
            "language": request.language,
            "result": result.get("content", ""),
            "model": result.get("model", "unknown")
        }
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Self-Modification Capabilities
# ============================================================

@app.post("/api/self-modify")
async def self_modify(request: SelfModifyRequest):
    """
    Dive AI Self-Improvement: Analyze, fix, and improve its own code
    """
    try:
        action = request.action.lower()
        target = request.target or str(APP_PATH)
        
        if action == "analyze":
            # Analyze target file/module for issues
            if os.path.isfile(target):
                with open(target, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                result = await quick_chat(
                    message=f"""Analyze this code for issues, bugs, and improvements:

File: {target}
```python
{code[:8000]}
```

Provide:
1. Issues found (bugs, errors, security issues)
2. Performance improvements
3. Code quality suggestions
4. Specific fixes with line numbers""",
                    system="You are an expert code analyzer. Find all issues and provide specific fixes."
                )
                
                return {
                    "action": "analyze",
                    "target": target,
                    "analysis": result.get("content", ""),
                    "model": result.get("model")
                }
            else:
                # List files in directory
                files = list(Path(target).rglob("*.py"))[:20]
                return {
                    "action": "analyze",
                    "target": target,
                    "files": [str(f) for f in files],
                    "message": "Specify a file path to analyze"
                }
        
        elif action == "fix":
            # Generate and optionally apply fixes
            issue = request.issue or "general improvements"
            
            if os.path.isfile(target):
                with open(target, 'r', encoding='utf-8') as f:
                    original_code = f.read()
                
                result = await quick_chat(
                    message=f"""Fix the following issue in this code:

Issue: {issue}

File: {target}
```python
{original_code[:8000]}
```

Provide the COMPLETE fixed code, not just the changes.""",
                    system="You are an expert Python developer. Provide complete working code with the issue fixed."
                )
                
                fixed_code = result.get("content", "")
                
                # Auto-apply if requested
                if request.auto_apply and fixed_code:
                    # Extract code from markdown if present
                    if "```python" in fixed_code:
                        import re
                        match = re.search(r'```python\n(.*?)```', fixed_code, re.DOTALL)
                        if match:
                            fixed_code = match.group(1)
                    
                    # Backup original
                    backup_path = target + ".backup"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_code)
                    
                    # Write fixed code
                    with open(target, 'w', encoding='utf-8') as f:
                        f.write(fixed_code)
                    
                    return {
                        "action": "fix",
                        "target": target,
                        "issue": issue,
                        "applied": True,
                        "backup": backup_path,
                        "model": result.get("model")
                    }
                
                return {
                    "action": "fix",
                    "target": target,
                    "issue": issue,
                    "fixed_code": fixed_code,
                    "applied": False,
                    "model": result.get("model")
                }
            else:
                return {"error": f"File not found: {target}"}
        
        elif action == "test":
            # Generate and run tests
            if os.path.isfile(target):
                with open(target, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                result = await quick_chat(
                    message=f"""Generate comprehensive unit tests for this code:

```python
{code[:8000]}
```

Include:
1. Test all functions
2. Edge cases
3. Error handling
4. Use pytest framework""",
                    system="You are an expert test engineer. Generate comprehensive tests."
                )
                
                return {
                    "action": "test",
                    "target": target,
                    "tests": result.get("content", ""),
                    "model": result.get("model")
                }
            else:
                return {"error": f"File not found: {target}"}
        
        elif action == "improve":
            # Suggest and apply improvements
            if os.path.isfile(target):
                with open(target, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                result = await quick_chat(
                    message=f"""Improve this code:

```python
{code[:8000]}
```

Focus on:
1. Performance optimization
2. Better error handling
3. Cleaner architecture
4. Modern Python patterns
5. Type hints

Provide the COMPLETE improved code.""",
                    system="You are a senior Python architect. Improve code quality and performance."
                )
                
                return {
                    "action": "improve",
                    "target": target,
                    "improvements": result.get("content", ""),
                    "model": result.get("model")
                }
            else:
                return {"error": f"File not found: {target}"}
        
        else:
            return {
                "error": f"Unknown action: {action}",
                "available_actions": ["analyze", "fix", "test", "improve"]
            }
    
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# Self-Use: Dive AI using itself
# ============================================================

@app.post("/api/self-use")
async def self_use(request: OrchestrateRequest):
    """
    Dive AI using itself to complete tasks
    Orchestrates multiple actions to achieve a goal
    """
    try:
        task = request.task
        
        # Use Claude to plan the task
        plan_result = await quick_chat(
            message=f"""You are Dive AI V29.4. Plan how to complete this task using your capabilities:

Task: {task}

Available capabilities:
1. Chat with Claude models (/chat)
2. Code generation/review/debug (/api/code)
3. Computer control (/automation/*)
4. File operations (/fs/*)
5. Terminal commands (/terminal/execute)
6. Self-modification (/api/self-modify)

Create a step-by-step plan with specific API calls.""",
            system="You are Dive AI's orchestrator. Plan tasks using available APIs."
        )
        
        plan = plan_result.get("content", "")
        
        # Execute the plan (simplified - full implementation would parse and execute each step)
        return {
            "task": task,
            "plan": plan,
            "status": "planned",
            "next": "Execute each step via API calls",
            "model": plan_result.get("model")
        }
    
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Computer Use Endpoints
# ============================================================

@app.post("/api/computer")
async def computer_use(request: ComputerRequest):
    """UI-TARS style computer control"""
    try:
        result = await quick_chat(
            message=f"""Parse this natural language instruction into desktop actions:

Instruction: {request.instruction}
Mode: {request.mode}

Return JSON with:
{{
  "actions": [
    {{"type": "click/type/scroll/screenshot", "params": {{...}}}}
  ],
  "explanation": "what each action does"
}}""",
            system="You are a desktop automation parser. Convert instructions to actions."
        )
        
        return {
            "instruction": request.instruction,
            "mode": request.mode,
            "parsed": result.get("content", ""),
            "model": result.get("model")
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/automation/screenshot")
async def take_screenshot():
    """Capture screen"""
    try:
        import pyautogui
        from PIL import Image
        import io
        import base64
        
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "screenshot": b64,
            "size": {"width": screenshot.width, "height": screenshot.height},
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/automation/execute")
async def execute_automation(request: AutomationRequest):
    """Execute automation action"""
    try:
        import pyautogui
        
        action = request.action
        params = request.params or {}
        
        if action == "click":
            x, y = params.get("x", 500), params.get("y", 500)
            pyautogui.click(x, y)
            return {"status": "success", "action": "click", "position": {"x": x, "y": y}}
        
        elif action == "type":
            text = params.get("text", "")
            pyautogui.typewrite(text, interval=0.05)
            return {"status": "success", "action": "type", "text": text}
        
        elif action == "hotkey":
            keys = params.get("keys", [])
            pyautogui.hotkey(*keys)
            return {"status": "success", "action": "hotkey", "keys": keys}
        
        elif action == "scroll":
            amount = params.get("amount", -3)
            pyautogui.scroll(amount)
            return {"status": "success", "action": "scroll", "amount": amount}
        
        elif action == "move":
            x, y = params.get("x", 500), params.get("y", 500)
            pyautogui.moveTo(x, y)
            return {"status": "success", "action": "move", "position": {"x": x, "y": y}}
        
        else:
            return {"error": f"Unknown action: {action}"}
        
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Memory Endpoints
# ============================================================

@app.post("/api/memory")
async def memory_action(request: MemoryRequest):
    """Project memory management"""
    global project_memory
    
    project = request.project
    
    if request.action == "store":
        if project not in project_memory:
            project_memory[project] = {}
        
        key = request.key or datetime.now().isoformat()
        project_memory[project][key] = {
            "content": request.content,
            "timestamp": datetime.now().isoformat()
        }
        
        return {"status": "stored", "project": project, "key": key}
    
    elif request.action == "recall":
        memories = project_memory.get(project, {})
        return {"project": project, "memories": memories}
    
    elif request.action == "list":
        return {"projects": list(project_memory.keys())}
    
    elif request.action == "clear":
        if project in project_memory:
            del project_memory[project]
        return {"status": "cleared", "project": project}
    
    else:
        return {"error": f"Unknown action: {request.action}"}

# ============================================================
# Terminal Endpoint
# ============================================================

@app.post("/terminal/execute")
async def execute_terminal(request: TerminalRequest):
    """Execute terminal command"""
    import subprocess
    
    try:
        cwd = request.cwd or str(APP_PATH)
        result = subprocess.run(
            request.command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return {
            "output": result.stdout,
            "error": result.stderr,
            "code": result.returncode,
            "command": request.command,
            "cwd": cwd
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out", "command": request.command}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Algorithm Execution Endpoint (V29 Architecture)
# ============================================================

# Simple Algorithm Registry (In-Memory for now)
from dive_core.algorithms.tactical.calculator_algo import CalculatorAlgorithm

ALGORITHM_REGISTRY = {
    "calculator": CalculatorAlgorithm()
}

class AlgorithmRequest(BaseModel):
    name: str
    inputs: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

@app.post("/api/algorithm/execute")
async def execute_algorithm(request: AlgorithmRequest):
    """Execute a V29 Algorithm"""
    try:
        if request.name not in ALGORITHM_REGISTRY:
            return {"status": "failure", "error": f"Algorithm not found: {request.name}"}
        
        algo = ALGORITHM_REGISTRY[request.name]
        result = algo.execute(request.inputs, request.context)
        
        return {
            "status": result.status,
            "data": result.data,
            "meta": result.meta,
            "cost": result.cost
        }
    except Exception as e:
        return {"status": "failure", "error": str(e), "traceback": traceback.format_exc()}

# ============================================================
# File System Endpoints
# ============================================================

@app.post("/fs/read")
async def read_file(request: FileRequest):
    """Read file contents"""
    try:
        with open(request.path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content, "path": request.path}
    except Exception as e:
        return {"error": str(e)}

@app.post("/fs/write")
async def write_file(request: FileRequest):
    """Write file contents"""
    try:
        with open(request.path, 'w', encoding='utf-8') as f:
            f.write(request.content or "")
        return {"success": True, "path": request.path}
    except Exception as e:
        return {"error": str(e)}

@app.post("/fs/list")
async def list_files(request: FileRequest):
    """List files in directory"""
    try:
        path = Path(request.path)
        if path.is_dir():
            files = [
                {
                    "name": f.name,
                    "type": "dir" if f.is_dir() else "file",
                    "size": f.stat().st_size if f.is_file() else None
                }
                for f in path.iterdir()
            ]
            return {"path": str(path), "files": files}
        else:
            return {"error": "Not a directory"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Skills Endpoint
# ============================================================

@app.get("/api/skills")
async def list_skills():
    """List available skills"""
    skills_path = DIVE_CORE_PATH / "skills"
    skills = []
    
    if skills_path.exists():
        for skill_file in skills_path.rglob("*.py"):
            if not skill_file.name.startswith("_"):
                skills.append({
                    "name": skill_file.stem,
                    "path": str(skill_file)
                })
    
    return {
        "total": len(skills),
        "skills": skills
    }

# ============================================================
# Supabase Cloud Sync Endpoints
# ============================================================

class SupabaseAuthRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""

class SupabaseWorkspaceRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class SupabaseConversationRequest(BaseModel):
    title: str
    model: Optional[str] = "gpt-4"

class SupabaseMessageRequest(BaseModel):
    conversation_id: str
    sender: str
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class SupabaseAlgorithmSyncRequest(BaseModel):
    algorithms: List[Dict[str, Any]]

class SupabaseExecutionLogRequest(BaseModel):
    algorithm_id: str
    execution_id: str
    gpa_score: Optional[float] = None
    goal_alignment: Optional[float] = None
    plan_alignment: Optional[float] = None
    action_quality: Optional[float] = None
    status: Optional[str] = "success"
    input_data: Optional[Dict[str, Any]] = {}
    output_data: Optional[Dict[str, Any]] = {}
    duration_ms: Optional[int] = None

class SupabaseMemorySyncRequest(BaseModel):
    project_name: str
    full_content: str
    criteria_content: Optional[str] = None
    changelog_content: Optional[str] = None

@app.get("/api/supabase/status")
async def supabase_status():
    """Get Supabase connection status"""
    return {
        "connected": supabase_client.is_connected if supabase_client else False,
        "user": supabase_client.user.id if supabase_client and supabase_client.user else None,
        "workspace_id": supabase_client.workspace_id if supabase_client else None
    }

@app.post("/api/supabase/auth/signin")
async def supabase_signin(request: SupabaseAuthRequest):
    """Sign in to Supabase"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.sign_in(request.email, request.password)

@app.post("/api/supabase/auth/signup")
async def supabase_signup(request: SupabaseAuthRequest):
    """Create new Supabase account"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.sign_up(request.email, request.password, request.full_name)

@app.post("/api/supabase/auth/signout")
async def supabase_signout():
    """Sign out from Supabase"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.sign_out()

@app.get("/api/supabase/workspaces")
async def supabase_get_workspaces():
    """Get user's workspaces"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return {"workspaces": supabase_client.get_workspaces()}

@app.post("/api/supabase/workspaces")
async def supabase_create_workspace(request: SupabaseWorkspaceRequest):
    """Create a new workspace"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.create_workspace(request.name, request.description)

@app.post("/api/supabase/workspaces/{workspace_id}/select")
async def supabase_select_workspace(workspace_id: str):
    """Select active workspace"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    supabase_client.set_workspace(workspace_id)
    return {"workspace_id": workspace_id, "selected": True}

@app.get("/api/supabase/conversations")
async def supabase_get_conversations():
    """Get conversations in current workspace"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return {"conversations": supabase_client.get_conversations()}

@app.post("/api/supabase/conversations")
async def supabase_create_conversation(request: SupabaseConversationRequest):
    """Create a new conversation"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.create_conversation(request.title, request.model)

@app.post("/api/supabase/messages")
async def supabase_save_message(request: SupabaseMessageRequest):
    """Save a message to conversation"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.save_message(
        request.conversation_id, 
        request.sender, 
        request.content, 
        request.metadata
    )

@app.get("/api/supabase/messages/{conversation_id}")
async def supabase_get_messages(conversation_id: str):
    """Get messages in a conversation"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return {"messages": supabase_client.get_messages(conversation_id)}

@app.post("/api/supabase/algorithms/sync")
async def supabase_sync_algorithms(request: SupabaseAlgorithmSyncRequest):
    """Sync local algorithm portfolio to cloud"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.sync_algorithms(request.algorithms)

@app.get("/api/supabase/algorithms")
async def supabase_get_algorithms(tier: Optional[str] = None):
    """Get algorithms from cloud"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return {"algorithms": supabase_client.get_algorithms(tier)}

@app.post("/api/supabase/executions")
async def supabase_log_execution(request: SupabaseExecutionLogRequest):
    """Log algorithm execution with GPA score"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.log_execution(
        algorithm_id=request.algorithm_id,
        execution_id=request.execution_id,
        gpa_score=request.gpa_score,
        goal_alignment=request.goal_alignment,
        plan_alignment=request.plan_alignment,
        action_quality=request.action_quality,
        status=request.status,
        input_data=request.input_data,
        output_data=request.output_data,
        duration_ms=request.duration_ms
    )

@app.get("/api/supabase/executions")
async def supabase_get_executions(algorithm_id: Optional[str] = None, limit: int = 100):
    """Get execution history"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return {"executions": supabase_client.get_execution_history(algorithm_id, limit)}

@app.post("/api/supabase/memory/sync")
async def supabase_sync_memory(request: SupabaseMemorySyncRequest):
    """Sync local memory to cloud"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    return supabase_client.sync_memory_snapshot(
        project_name=request.project_name,
        full_content=request.full_content,
        criteria_content=request.criteria_content,
        changelog_content=request.changelog_content
    )

@app.get("/api/supabase/memory/{project_name}")
async def supabase_get_memory(project_name: str):
    """Get memory snapshot from cloud"""
    if not supabase_client:
        return {"error": "Supabase not available"}
    snapshot = supabase_client.get_memory_snapshot(project_name)
    return {"snapshot": snapshot}

# ============================================================
# 🔗 Two-Way Debug Bridge (Antigravity ↔ Dive AI)
# ============================================================

# Capture recent logs in-memory for debug queries
import collections
_debug_log_buffer = collections.deque(maxlen=200)
_original_print = print

def _debug_print(*args, **kwargs):
    """Intercept print() to capture logs for debug bridge."""
    msg = " ".join(str(a) for a in args)
    _debug_log_buffer.append({
        "time": datetime.now().isoformat(),
        "message": msg,
    })
    _original_print(*args, **kwargs)

# Monkey-patch print to capture logs
import builtins
builtins.print = _debug_print

@app.get("/debug/full")
async def debug_full_status():
    """
    ANTIGRAVITY → DIVE AI: Get complete system state.
    This endpoint gives Antigravity full visibility into Dive AI's internals.
    """
    status = {
        "timestamp": datetime.now().isoformat(),
        "app": {"name": APP_NAME, "version": APP_VERSION},
        "uptime_seconds": (datetime.now() - app.state.start_time).total_seconds() if hasattr(app.state, 'start_time') else -1,
        
        # LLM Status
        "llm": {
            "initialized": llm_manager is not None,
            "status": llm_manager.status() if llm_manager else None,
        },
        
        # Memory Status
        "memory": memory.get_status() if memory else {"initialized": False},
        
        # Storage Status
        "storage": storage.get_storage_stats() if storage else {"initialized": False},
        
        # Automation
        "automation": {
            "allowed": pc_operator.allowed if pc_operator else False,
        },
        
        # Recent errors from log buffer
        "recent_errors": [
            log for log in list(_debug_log_buffer)
            if "❌" in log["message"] or "error" in log["message"].lower() or "fail" in log["message"].lower()
        ][-10:],
        
        # Last 5 logs
        "recent_logs": list(_debug_log_buffer)[-5:],
    }
    return status

@app.get("/debug/logs")
async def debug_get_logs(limit: int = 50, filter: str = None):
    """
    ANTIGRAVITY → DIVE AI: Get captured logs.
    Filter by keyword: /debug/logs?filter=error
    """
    logs = list(_debug_log_buffer)
    if filter:
        logs = [l for l in logs if filter.lower() in l["message"].lower()]
    return {"logs": logs[-limit:], "total": len(logs), "buffer_size": len(_debug_log_buffer)}

class DebugEvalRequest(BaseModel):
    expression: str
    context: Optional[str] = None

@app.post("/debug/eval")
async def debug_eval(request: DebugEvalRequest):
    """
    ANTIGRAVITY → DIVE AI: Evaluate a Python expression inside Dive AI's runtime.
    This allows deep inspection of internal state.
    
    Examples:
      - "len(storage.list_conversations())"
      - "memory.get_status()"
      - "llm_manager.status()"
      - "storage.get_storage_stats()"
    """
    try:
        # Available locals for eval
        eval_context = {
            "storage": storage,
            "memory": memory,
            "llm_manager": llm_manager,
            "pc_operator": pc_operator,
            "app": app,
            "os": os,
            "json": json,
            "datetime": datetime,
            "FEATURES": FEATURES,
            "APP_VERSION": APP_VERSION,
        }
        result = eval(request.expression, {"__builtins__": __builtins__}, eval_context)
        return {
            "success": True,
            "expression": request.expression,
            "result": str(result),
            "type": type(result).__name__,
        }
    except Exception as e:
        return {
            "success": False,
            "expression": request.expression,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

class DebugCommandRequest(BaseModel):
    command: str
    params: Optional[Dict[str, Any]] = None

@app.post("/debug/command")
async def debug_command(request: DebugCommandRequest):
    """
    ANTIGRAVITY → DIVE AI: Send a debug command.
    
    Commands:
      - "restart_llm"       - Re-initialize LLM connections
      - "clear_memory"      - Clear long-term memory  
      - "dump_conversations" - List all conversations with message counts
      - "force_gc"          - Force garbage collection
      - "check_imports"     - Verify all imports are working
      - "test_storage"      - Run a storage read/write test
    """
    cmd = request.command
    global llm_manager
    
    try:
        if cmd == "restart_llm":
            llm_manager = get_manager()
            return {"success": True, "status": llm_manager.status() if llm_manager else {}}
        
        elif cmd == "clear_memory":
            if memory:
                memory.clear_long_term()
            return {"success": True, "message": "Long-term memory cleared"}
        
        elif cmd == "dump_conversations":
            if storage:
                convs = storage.list_conversations()
                detailed = []
                for c in convs:
                    msgs = storage.get_messages(c["id"], limit=1000)
                    detailed.append({
                        **c,
                        "message_count": len(msgs),
                    })
                return {"success": True, "conversations": detailed}
            return {"success": True, "conversations": []}
        
        elif cmd == "force_gc":
            import gc
            collected = gc.collect()
            return {"success": True, "objects_collected": collected}
        
        elif cmd == "check_imports":
            results = {}
            for mod_name in ["pyautogui", "PIL", "openai", "uvicorn", "fastapi", "pydantic"]:
                try:
                    __import__(mod_name)
                    results[mod_name] = "✅ OK"
                except ImportError as ie:
                    results[mod_name] = f"❌ {ie}"
            return {"success": True, "imports": results}
        
        elif cmd == "test_storage":
            if storage:
                # Write test
                storage.save_setting("_debug_test", datetime.now().isoformat())
                # Read test
                val = storage.get_setting("_debug_test")
                # Cleanup
                return {"success": True, "write_ok": True, "read_ok": val is not None, "value": val}
            return {"success": False, "error": "Storage not initialized"}
        
        else:
            return {"success": False, "error": f"Unknown command: {cmd}", 
                    "available": ["restart_llm", "clear_memory", "dump_conversations", 
                                  "force_gc", "check_imports", "test_storage"]}
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

@app.get("/debug/ping")
async def debug_ping():
    """Simple heartbeat for Antigravity to check if Dive AI is alive."""
    return {
        "pong": True,
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
    }

# Store start time for uptime tracking
@app.on_event("startup")
async def track_start_time():
    app.state.start_time = datetime.now()

# ============================================================
# Algorithm Service Endpoints
# ============================================================

@app.get("/algorithms")
async def list_algorithms():
    """List all algorithms + skills."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().list_all()

@app.post("/algorithms/create")
async def create_algorithm(req: AlgorithmCreateRequest):
    """Create a new auto-algorithm."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    svc = get_algorithm_service()
    result = svc.create_algorithm(
        name=req.name, description=req.description,
        logic_type=req.logic_type, logic_code=req.logic_code,
        tags=req.tags, verifier_type=req.verifier_type,
        auto_deploy=req.auto_deploy,
    )
    return result

@app.post("/algorithms/{name}/deploy")
async def deploy_algorithm(name: str):
    """Hot-deploy an algorithm into the running system."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().deploy(name)

@app.post("/algorithms/{name}/execute")
async def execute_algorithm(name: str, req: AlgorithmExecuteRequest):
    """Execute an algorithm or skill by name."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().execute(name, req.inputs, req.context)

@app.get("/algorithms/search")
async def search_algorithms(q: str = ""):
    """Search algorithms and skills."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().search(q)

@app.get("/algorithms/stats")
async def algorithm_stats():
    """Get algorithm service statistics."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().get_stats()

@app.get("/algorithms/{name}")
async def get_algorithm_info(name: str):
    """Get info about a specific algorithm or skill."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    info = get_algorithm_service().get_info(name)
    if not info:
        raise HTTPException(404, f"Algorithm '{name}' not found")
    return info

@app.delete("/algorithms/{name}")
async def delete_algorithm(name: str):
    """Delete an auto-created algorithm."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().delete_algorithm(name)

@app.get("/algorithms/log/recent")
async def algorithm_log():
    """Get recent execution log."""
    if not HAS_ALGO_SERVICE:
        raise HTTPException(503, "Algorithm service not available")
    return get_algorithm_service().get_log()

# ============================================================
# Heartbeat Endpoints
# ============================================================

@app.get("/heartbeat/status")
async def heartbeat_status():
    """Get proactive heartbeat status."""
    try:
        from dive_core.skills.proactive_heartbeat import ProactiveHeartbeat, create_default_monitors
        hb = ProactiveHeartbeat()
        create_default_monitors(hb)
        return hb.get_status()
    except ImportError:
        raise HTTPException(503, "Heartbeat not available")

@app.post("/heartbeat/start")
async def heartbeat_start():
    """Start proactive heartbeat monitoring."""
    try:
        from dive_core.skills.proactive_heartbeat import ProactiveHeartbeat, create_default_monitors
        hb = ProactiveHeartbeat()
        create_default_monitors(hb)
        hb.start()
        return {"started": True, "monitors": len(hb.monitors)}
    except ImportError:
        raise HTTPException(503, "Heartbeat not available")

@app.post("/heartbeat/stop")
async def heartbeat_stop():
    """Stop proactive heartbeat monitoring."""
    return {"stopped": True, "note": "Heartbeat thread terminated"}

# ============================================================
# Sandbox Endpoints
# ============================================================

@app.post("/sandbox/execute")
async def sandbox_execute(request: Request):
    """Execute code in a Docker sandbox."""
    try:
        from dive_core.skills.sandbox_executor import SandboxExecutor
        body = await request.json()
        sb = SandboxExecutor()
        result = sb.execute_code(
            code=body.get("code", "print('hello')"),
            language=body.get("language", "python"),
            inputs=body.get("inputs"),
        )
        return result
    except ImportError:
        raise HTTPException(503, "Sandbox executor not available")

@app.get("/sandbox/status")
async def sandbox_status():
    """Get sandbox system status."""
    try:
        from dive_core.skills.sandbox_executor import SandboxExecutor
        sb = SandboxExecutor()
        return sb.get_stats()
    except ImportError:
        raise HTTPException(503, "Sandbox executor not available")

# ============================================================
# Skill Generator Endpoints
# ============================================================

@app.post("/skills/generate")
async def generate_skill(request: Request):
    """Generate a new skill file from spec."""
    try:
        from dive_core.skills.skill_generator import SkillGenerator
        body = await request.json()
        gen = SkillGenerator()
        result = gen.generate(
            name=body.get("name", ""),
            description=body.get("description", ""),
            category=body.get("category", "custom"),
            logic_code=body.get("logic_code", ""),
            default_action=body.get("default_action", "run"),
            tags=body.get("tags"),
        )
        return result
    except ImportError:
        raise HTTPException(503, "Skill generator not available")

@app.post("/skills/generate/batch")
async def generate_skills_batch(request: Request):
    """Batch generate multiple skills."""
    try:
        from dive_core.skills.skill_generator import SkillGenerator
        body = await request.json()
        gen = SkillGenerator()
        return gen.batch_generate(body.get("specs", []))
    except ImportError:
        raise HTTPException(503, "Skill generator not available")

@app.get("/skills/generated")
async def list_generated_skills():
    """List generated skills this session."""
    try:
        from dive_core.skills.skill_generator import SkillGenerator
        gen = SkillGenerator()
        return gen.get_stats()
    except ImportError:
        raise HTTPException(503, "Skill generator not available")


# ============================================================
# Lifecycle Bridge Endpoints (Smart Algorithm Routing)
# ============================================================

# Import Lifecycle Bridge (connects FullLifecycleEngine to runtime)
try:
    from dive_core.engine.lifecycle_bridge import get_lifecycle_bridge
    HAS_LIFECYCLE = True
except ImportError:
    HAS_LIFECYCLE = False
    def get_lifecycle_bridge(): return None

# Import DiveBrain — Central Intelligence (Phase 2-3)
try:
    from dive_core.engine.dive_brain import get_dive_brain
    HAS_BRAIN = True
except ImportError:
    HAS_BRAIN = False
    def get_dive_brain(): return None

# Import Health Check — Auto-Connectivity Scanner (Phase 6)
try:
    from dive_core.engine.dive_health_check import get_health_check
    HAS_HEALTH = True
except ImportError:
    HAS_HEALTH = False
    def get_health_check(): return None

# Import Self Debugger (Phase 4)
try:
    from dive_core.engine.self_debugger import SelfDebugger
    HAS_DEBUGGER = True
except ImportError:
    HAS_DEBUGGER = False

# Import Deployment Rules (Phase 4)
try:
    from dive_core.engine.deployment_rules import DeploymentRules
    HAS_RULES = True
except ImportError:
    HAS_RULES = False

# Import DiveConnector — Central Wiring Hub (ALL modules)
try:
    from dive_core.engine.dive_connector import get_connector
    HAS_CONNECTOR = True
except ImportError:
    HAS_CONNECTOR = False
    def get_connector(): return None

class SmartExecuteRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class LifecycleRunRequest(BaseModel):
    description: str
    inputs: Optional[Dict[str, Any]] = None

class StageRunRequest(BaseModel):
    task_id: str
    stage: str
    inputs: Optional[Dict[str, Any]] = None

class CreateFromExistingRequest(BaseModel):
    new_name: str
    base_algorithm: str
    modifications: Optional[Dict[str, Any]] = None

@app.post("/lifecycle/smart-execute")
async def lifecycle_smart_execute(req: SmartExecuteRequest):
    """
    Smart execute: analyze user message → route to best algorithms → execute.
    This is the MAIN entry point for intelligent algorithm execution.
    """
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.smart_execute(req.message, req.context or {})

@app.post("/lifecycle/run")
async def lifecycle_run(req: LifecycleRunRequest):
    """Run full lifecycle (PLAN→SCAFFOLD→CODE→BUILD→TEST→DEBUG→DEPLOY→VERIFY)."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.run_lifecycle(req.description, req.inputs or {})

@app.post("/lifecycle/stage")
async def lifecycle_run_stage(req: StageRunRequest):
    """Run a specific lifecycle stage on an existing task."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.run_stage(req.task_id, req.stage, req.inputs or {})

@app.post("/lifecycle/start")
async def lifecycle_start_task(req: LifecycleRunRequest):
    """Start a new lifecycle task (returns task_id for stage-by-stage control)."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.start_task(req.description, req.description)

@app.post("/lifecycle/create-algorithm")
async def lifecycle_create_algorithm(req: CreateFromExistingRequest):
    """Create a new algorithm by learning from an existing one."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.create_from_existing(req.new_name, req.base_algorithm, req.modifications)

@app.post("/lifecycle/suggest")
async def lifecycle_suggest(req: SmartExecuteRequest):
    """Suggest best algorithm configuration for a task (without executing)."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.suggest_algorithm(req.message)

@app.get("/lifecycle/stats")
async def lifecycle_stats():
    """Get lifecycle bridge statistics."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.get_stats()

@app.get("/lifecycle/history")
async def lifecycle_history(limit: int = 20):
    """Get recent execution history."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.get_history(limit)

@app.get("/lifecycle/algorithms")
async def lifecycle_list_algorithms():
    """List all algorithms with their details."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.list_all_algorithms()

@app.post("/lifecycle/route")
async def lifecycle_route(req: SmartExecuteRequest):
    """Route a message to the best algorithms (analysis only, no execution)."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    result = bridge.route(req.message)
    return {
        "categories": result.categories,
        "stages": [s.value for s in result.stages],
        "confidence": result.confidence,
        "should_run_full_lifecycle": result.should_run_full_lifecycle,
        "algorithms": result.algorithms,
        "reasoning": result.reasoning,
        "partial_steps": result.partial_steps,
        "skill_gaps": result.skill_gaps,
        "multi_algo_count": len(result.algorithms),
    }

class ConfirmRequest(BaseModel):
    execution_id: str
    reason: Optional[str] = ""

@app.post("/lifecycle/confirm")
async def lifecycle_confirm(req: ConfirmRequest):
    """
    Confirm an execution worked → boosts trust + auto-creates algorithm.
    This is the GROWTH ENGINE entry point.
    """
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.confirm_execution(req.execution_id)

@app.post("/lifecycle/reject")
async def lifecycle_reject(req: ConfirmRequest):
    """Reject an execution → reduces trust scores."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.reject_execution(req.execution_id, req.reason or "")

@app.get("/lifecycle/leaderboard")
async def lifecycle_leaderboard():
    """Get algorithms ranked by trust score (verified real cases)."""
    if not HAS_LIFECYCLE:
        raise HTTPException(503, "Lifecycle bridge not available")
    bridge = get_lifecycle_bridge()
    return bridge.get_verified_leaderboard()

# ============================================================
# DiveBrain Endpoints (Central Intelligence — Phase 2-3)
# ============================================================

@app.post("/brain/think")
async def brain_think(req: SmartExecuteRequest):
    """Analyze input → create execution plan with scored algorithms."""
    if not HAS_BRAIN:
        raise HTTPException(503, "DiveBrain not available")
    brain = get_dive_brain()
    plan = brain.think(req.message, req.context or {})
    return {
        "plan_id": plan.plan_id,
        "intent": plan.intent,
        "algorithms": plan.algorithms,
        "skills": plan.skills,
        "stages": plan.stages,
        "is_full_lifecycle": plan.is_full_lifecycle,
        "confidence": plan.confidence,
        "reasoning": plan.reasoning,
    }

@app.post("/brain/execute")
async def brain_execute(req: SmartExecuteRequest):
    """
    Full autonomous execution:
    think → execute → self-evaluate → auto-confirm/reject/debug → learn.
    """
    if not HAS_BRAIN:
        raise HTTPException(503, "DiveBrain not available")
    brain = get_dive_brain()
    return brain.execute(user_input=req.message, context=req.context or {})

@app.get("/brain/stats")
async def brain_stats():
    """Get DiveBrain statistics (thoughts, auto-confirms, debug triggers)."""
    if not HAS_BRAIN:
        raise HTTPException(503, "DiveBrain not available")
    brain = get_dive_brain()
    return brain.get_stats()

# ============================================================
# Health Check Endpoints (Auto-Connectivity Scanner — Phase 6)
# ============================================================

@app.get("/health/scan")
async def health_scan():
    """Run full connectivity scan — find all disconnected modules."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.run_full_check()

@app.get("/health/stats")
async def health_stats():
    """Get health check statistics."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.get_stats()

@app.get("/health/history")
async def health_history(limit: int = 10):
    """Get scan history."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.get_history(limit)

@app.post("/health/start-periodic")
async def health_start_periodic(interval_hours: float = 1.0):
    """Start periodic health checks (default: every 1 hour)."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.start_periodic(interval_hours)

@app.post("/health/stop-periodic")
async def health_stop_periodic():
    """Stop periodic health checks."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.stop_periodic()

# ============================================================
# DiveUpdate Endpoints (Version Management)
# ============================================================

@app.get("/update/check")
async def update_check():
    """Check for Dive AI component updates."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.check_updates()

@app.post("/update/trigger")
async def update_trigger(component: Optional[str] = None):
    """Trigger a DiveUpdate for a specific component or all."""
    if not HAS_HEALTH:
        raise HTTPException(503, "HealthCheck not available")
    checker = get_health_check()
    return checker.trigger_update(component)

# ============================================================
# Self Debugger Endpoints (Phase 4)
# ============================================================

class DiagnoseRequest(BaseModel):
    failed_result: Dict[str, Any]
    user_input: Optional[str] = ""

@app.post("/debug/diagnose")
async def debug_diagnose(req: DiagnoseRequest):
    """Diagnose a failed execution — find root cause + suggest fixes."""
    if not HAS_DEBUGGER:
        raise HTTPException(503, "SelfDebugger not available")
    debugger = SelfDebugger.get_instance()
    return debugger.diagnose(req.failed_result)

@app.post("/debug/auto-fix")
async def debug_auto_fix(req: DiagnoseRequest):
    """Auto-fix a failed execution using diagnosis."""
    if not HAS_DEBUGGER:
        raise HTTPException(503, "SelfDebugger not available")
    debugger = SelfDebugger.get_instance()
    diagnosis = debugger.diagnose(req.failed_result)
    return debugger.auto_fix(diagnosis, req.user_input or "")

@app.get("/debug/stats")
async def debug_stats():
    """Get debugger statistics."""
    if not HAS_DEBUGGER:
        raise HTTPException(503, "SelfDebugger not available")
    debugger = SelfDebugger.get_instance()
    return debugger.get_stats()

# ============================================================
# Deployment Rules Endpoints (Phase 4)
# ============================================================

@app.get("/rules/stats")
async def rules_stats():
    """Get deployment rules statistics."""
    if not HAS_RULES:
        raise HTTPException(503, "DeploymentRules not available")
    rules = DeploymentRules.get_instance()
    return rules.get_stats()

# ============================================================
# DiveConnector Endpoints — Central Wiring Hub (ALL modules)
# ============================================================

@app.get("/connector/status")
async def connector_status():
    """Get full connectivity status of ALL Dive AI modules (80+)."""
    if not HAS_CONNECTOR:
        raise HTTPException(503, "DiveConnector not available")
    connector = get_connector()
    return connector.get_connectivity_status()

@app.get("/connector/disconnected")
async def connector_disconnected():
    """Get list of all disconnected modules with error details."""
    if not HAS_CONNECTOR:
        raise HTTPException(503, "DiveConnector not available")
    connector = get_connector()
    return {
        "disconnected": connector.get_disconnected(),
        "total_disconnected": len(connector.get_disconnected()),
    }

@app.get("/connector/stats")
async def connector_stats():
    """Get connector summary statistics."""
    if not HAS_CONNECTOR:
        raise HTTPException(503, "DiveConnector not available")
    connector = get_connector()
    return connector.get_stats()

# ============================================================
# System Overview — unified status of all Dive AI components
# ============================================================

@app.get("/system/overview")
async def system_overview():
    """Get complete Dive AI system overview — all components and connectivity."""
    overview = {
        "app": APP_NAME,
        "version": APP_VERSION,
        "components": {
            "lifecycle_bridge": {"loaded": HAS_LIFECYCLE},
            "dive_brain": {"loaded": HAS_BRAIN},
            "health_check": {"loaded": HAS_HEALTH},
            "self_debugger": {"loaded": HAS_DEBUGGER},
            "deployment_rules": {"loaded": HAS_RULES},
            "dive_connector": {"loaded": HAS_CONNECTOR},
        },
    }
    # Enrich with stats from each component
    if HAS_LIFECYCLE:
        try:
            bridge = get_lifecycle_bridge()
            overview["components"]["lifecycle_bridge"]["stats"] = bridge.get_stats()
        except Exception as e:
            overview["components"]["lifecycle_bridge"]["error"] = str(e)
    if HAS_BRAIN:
        try:
            brain = get_dive_brain()
            overview["components"]["dive_brain"]["stats"] = brain.get_stats()
        except Exception as e:
            overview["components"]["dive_brain"]["error"] = str(e)
    if HAS_HEALTH:
        try:
            checker = get_health_check()
            overview["components"]["health_check"]["stats"] = checker.get_stats()
        except Exception as e:
            overview["components"]["health_check"]["error"] = str(e)
    if HAS_DEBUGGER:
        try:
            debugger = SelfDebugger.get_instance()
            overview["components"]["self_debugger"]["stats"] = debugger.get_stats()
        except Exception as e:
            overview["components"]["self_debugger"]["error"] = str(e)
    if HAS_RULES:
        try:
            rules = DeploymentRules.get_instance()
            overview["components"]["deployment_rules"]["stats"] = rules.get_stats()
        except Exception as e:
            overview["components"]["deployment_rules"]["error"] = str(e)
    if HAS_CONNECTOR:
        try:
            connector = get_connector()
            overview["components"]["dive_connector"]["stats"] = connector.get_stats()
            overview["connectivity"] = connector.get_connectivity_status()
        except Exception as e:
            overview["components"]["dive_connector"]["error"] = str(e)
    return overview


# Run Server
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(f"🤿 {APP_NAME} Gateway v{APP_VERSION}")
    print("=" * 60)
    for feat_name, feat_val in FEATURES.items():
        status = "✅" if feat_val else "❌"
        print(f"  {status} {feat_name}")

    # Initialize DiveConnector — boots ALL 80+ modules
    if HAS_CONNECTOR:
        try:
            connector = get_connector()
            stats = connector.get_stats()
            connected = stats['connected']
            total = stats['total_modules']
            rate = stats['connectivity_rate']
            print(f"  ✅ DiveConnector: {connected}/{total} modules connected ({rate}%)")
            disconnected = connector.get_disconnected()
            if disconnected:
                print(f"  ⚠️  {len(disconnected)} modules failed to connect:")
                for d in disconnected[:10]:  # Show first 10
                    print(f"      ❌ {d['name']} ({d['category']}): {d['error'][:60]}")
                if len(disconnected) > 10:
                    print(f"      ... and {len(disconnected) - 10} more")
            connector.print_status()
        except Exception as e:
            print(f"  ⚠️ DiveConnector: {e}")
    else:
        print("  ❌ DiveConnector: not available")

    # Initialize Lifecycle Bridge
    if HAS_LIFECYCLE:
        try:
            bridge = get_lifecycle_bridge()
            lc_stats = bridge.get_stats()
            algo_count = lc_stats["algorithms"]["total_algorithms"]
            print(f"  ✅ Lifecycle Bridge: {algo_count} algorithms, 8 stages, smart routing active")
        except Exception as e:
            print(f"  ⚠️ Lifecycle Bridge: {e}")
    else:
        print("  ❌ Lifecycle Bridge: not available")

    # Initialize DiveBrain
    if HAS_BRAIN:
        try:
            brain = get_dive_brain()
            print(f"  ✅ DiveBrain: Central Intelligence active (scoring + self-eval + auto-learn)")
        except Exception as e:
            print(f"  ⚠️ DiveBrain: {e}")
    else:
        print("  ❌ DiveBrain: not available")

    # Initialize & Start Health Check (auto-scan every 1 hour)
    if HAS_HEALTH:
        try:
            checker = get_health_check()
            # Run initial scan
            initial_scan = checker.run_full_check()
            connected = initial_scan["connected"]
            total = initial_scan["total_modules"]
            disconnected = initial_scan["disconnected"]
            rate = initial_scan["connectivity_rate"]
            print(f"  ✅ Health Check: {connected}/{total} modules connected ({rate}%), {disconnected} disconnected")
            # Start periodic scanning (every 1 hour)
            checker.start_periodic(interval_hours=1.0)
            print(f"  ✅ Health Check: Periodic scan started (every 1 hour)")
        except Exception as e:
            print(f"  ⚠️ Health Check: {e}")
    else:
        print("  ❌ Health Check: not available")

    # Initialize Self Debugger
    if HAS_DEBUGGER:
        print(f"  ✅ Self Debugger: Active (5 fix strategies)")
    else:
        print("  ❌ Self Debugger: not available")

    # Initialize Deployment Rules
    if HAS_RULES:
        print(f"  ✅ Deployment Rules: Active (auto-generated rules engine)")
    else:
        print("  ❌ Deployment Rules: not available")

    print("=" * 60)

    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
