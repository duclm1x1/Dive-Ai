#!/usr/bin/env python3
"""
Dive AI V28 - FastAPI Server
==============================
HTTP API server that exposes all Dive AI capabilities via REST endpoints.
Designed for Manus (or any AI agent) to call via HTTP, saving tokens.

All endpoints accept JSON and return JSON.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os
import sys
from pathlib import Path

# Ensure project root
DIVE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(DIVE_ROOT))


# === Request/Response Models ===

class AskRequest(BaseModel):
    question: str
    model: Optional[str] = None
    project: Optional[str] = None
    context: Optional[str] = None

class CodeRequest(BaseModel):
    action: str = "generate"  # generate, review, debug, refactor, test, explain
    task: Optional[str] = None
    code: Optional[str] = None  # Code content for review/debug/refactor
    language: str = "python"
    output_file: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    scope: str = "all"  # codebase, web, memory, all
    path: str = "."
    limit: int = 10

class MemoryRequest(BaseModel):
    action: str  # store, recall, search, list, changelog
    project: str
    content: Optional[str] = None
    query: Optional[str] = None
    category: str = "knowledge"

class ComputerRequest(BaseModel):
    task: str
    mode: str = "local"  # local, remote, browser
    screenshot: bool = False
    provider: str = "openai"
    model: str = "gpt-4o"

class SkillsRequest(BaseModel):
    action: str = "list"  # list, run
    skill_name: Optional[str] = None
    input_data: Optional[str] = None

class OrchestrateRequest(BaseModel):
    task: str
    project: Optional[str] = "default"
    max_steps: int = 10


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Dive AI V28 API",
        description="Fully Automatic Computer Assistant - REST API for AI Agent Integration",
        version="28.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Lazy-loaded singletons
    _state = {}

    def get_config():
        if "config" not in _state:
            from src.cli.config import DiveConfig
            _state["config"] = DiveConfig.load()
        return _state["config"]

    def get_llm():
        if "llm" not in _state:
            from src.cli.llm_adapter import DiveLLM
            _state["llm"] = DiveLLM(get_config())
        return _state["llm"]

    def get_memory():
        if "memory" not in _state:
            from src.cli.commands.memory import DiveMemoryCLI
            _state["memory"] = DiveMemoryCLI(get_config().memory.storage_dir)
        return _state["memory"]

    # === Health Check ===
    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "28.0.0", "timestamp": datetime.now().isoformat()}

    # === ASK ===
    @app.post("/api/ask")
    async def api_ask(req: AskRequest):
        llm = get_llm()
        config = get_config()

        memory_context = ""
        if req.project:
            try:
                mem = get_memory()
                recalled = mem.recall(req.project)
                if recalled:
                    parts = []
                    for cat, content in recalled.items():
                        parts.append(cat + ": " + content[:500])
                    memory_context = "\n\nProject Memory:\n" + "\n".join(parts)
            except Exception:
                pass

        file_context = ""
        if req.context:
            file_context = "\n\nAdditional Context:\n" + req.context[:3000]

        system = (
            "You are Dive AI, a fully automatic computer assistant. "
            "Answer questions accurately and concisely."
            + memory_context + file_context
        )

        result = llm.chat(req.question, system=system, model=req.model)

        return {
            "status": "success" if not result.get("error") else "error",
            "answer": result.get("content", ""),
            "model": result.get("model", ""),
            "usage": result.get("usage", {}),
            "tier": result.get("tier", ""),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat(),
        }

    # === CODE ===
    @app.post("/api/code")
    async def api_code(req: CodeRequest):
        llm = get_llm()

        task = req.task or ""
        context = req.code

        if not task and not context:
            raise HTTPException(400, "Either task or code is required")

        if context and not task:
            task = req.action + " this code"

        result = llm.code(task=task, language=req.language, context=context, action=req.action)

        response = {
            "status": "success" if not result.get("error") else "error",
            "action": req.action,
            "language": req.language,
            "code": result.get("content", ""),
            "model": result.get("model", ""),
            "usage": result.get("usage", {}),
            "error": result.get("error"),
            "timestamp": datetime.now().isoformat(),
        }

        if req.output_file and response["status"] == "success":
            try:
                Path(req.output_file).write_text(response["code"])
                response["saved_to"] = req.output_file
            except Exception as e:
                response["save_error"] = str(e)

        return response

    # === SEARCH ===
    @app.post("/api/search")
    async def api_search(req: SearchRequest):
        from src.cli.commands.search import search_codebase, search_memory, search_web

        config = get_config()
        results = {}

        if req.scope in ("codebase", "all"):
            results["codebase"] = search_codebase(req.query, req.path, req.limit)

        if req.scope in ("memory", "all"):
            results["memory"] = search_memory(req.query, config)

        if req.scope in ("web", "all"):
            try:
                llm = get_llm()
                results["web"] = search_web(req.query, llm)
            except Exception as e:
                results["web"] = {"error": str(e)}

        total = sum(len(v) if isinstance(v, list) else 1 for v in results.values())

        return {
            "status": "success",
            "query": req.query,
            "scope": req.scope,
            "results": results,
            "total_results": total,
            "timestamp": datetime.now().isoformat(),
        }

    # === MEMORY ===
    @app.post("/api/memory")
    async def api_memory(req: MemoryRequest):
        mem = get_memory()

        if req.action == "store":
            if not req.content:
                raise HTTPException(400, "content is required for store action")
            result = mem.store(req.project, req.content, req.category)
            return {"status": "success", "action": "store", "result": result}

        elif req.action == "recall":
            memories = mem.recall(req.project)
            return {"status": "success", "action": "recall", "project": req.project, "memories": memories}

        elif req.action == "search":
            if not req.query:
                raise HTTPException(400, "query is required for search action")
            results = mem.search(req.project, req.query)
            return {"status": "success", "action": "search", "results": results, "total": len(results)}

        elif req.action == "list":
            projects = mem.list_projects()
            return {"status": "success", "action": "list", "projects": projects}

        elif req.action == "changelog":
            if not req.content:
                raise HTTPException(400, "content is required for changelog action")
            result = mem.changelog(req.project, req.content)
            return {"status": "success", "action": "changelog", "result": result}

        raise HTTPException(400, "Unknown action: " + req.action)

    # === COMPUTER (UI-TARS) ===
    @app.post("/api/computer")
    async def api_computer(req: ComputerRequest):
        from src.cli.commands.computer import execute_task
        config = get_config()

        result = execute_task(
            task=req.task,
            mode=req.mode,
            screenshot=req.screenshot,
            provider=req.provider,
            model=req.model,
            config=config,
        )

        return {
            "status": "success" if not result.get("error") else "error",
            "task": req.task,
            "mode": req.mode,
            **result,
            "timestamp": datetime.now().isoformat(),
        }

    # === SKILLS ===
    @app.post("/api/skills")
    async def api_skills(req: SkillsRequest):
        from src.cli.commands.skills import discover_skills, run_skill

        if req.action == "list":
            skills = discover_skills()
            return {"status": "success", "skills": skills, "total": len(skills)}

        elif req.action == "run":
            if not req.skill_name:
                raise HTTPException(400, "skill_name is required for run action")
            result = run_skill(req.skill_name, req.input_data)
            return {"status": "success", "skill": req.skill_name, "result": result}

        raise HTTPException(400, "Unknown action: " + req.action)

    # === ORCHESTRATE ===
    @app.post("/api/orchestrate")
    async def api_orchestrate(req: OrchestrateRequest):
        llm = get_llm()

        plan_prompt = (
            "You are Dive AI Smart Orchestrator. Break down this complex task into "
            "a numbered list of concrete, executable steps. Each step should be "
            "actionable and specific. Output as JSON with keys: "
            '"steps" (array of {step_number, action, description, tool}).\n\n'
            "Task: " + req.task
        )

        plan_result = llm.chat(
            plan_prompt,
            system="You are a task planning AI. Output valid JSON only.",
            model=llm.models["power"],
            json_mode=True,
        )

        steps = []
        try:
            plan_data = json.loads(plan_result.get("content", "{}"))
            steps = plan_data.get("steps", [])
        except (json.JSONDecodeError, TypeError):
            steps = [{"step_number": 1, "action": "execute",
                      "description": plan_result.get("content", ""), "tool": "llm"}]

        if len(steps) > req.max_steps:
            steps = steps[:req.max_steps]

        # Store in memory
        try:
            mem = get_memory()
            mem.store(req.project, "Task: " + req.task + "\nPlan: " + json.dumps(steps), "orchestration")
        except Exception:
            pass

        return {
            "status": "success",
            "task": req.task,
            "plan": {"total_steps": len(steps), "steps": steps},
            "model": plan_result.get("model", ""),
            "usage": plan_result.get("usage", {}),
            "timestamp": datetime.now().isoformat(),
        }

    # === STATUS ===
    @app.get("/api/status")
    async def api_status():
        config = get_config()
        return {
            "status": "healthy",
            "version": config.version,
            "config": config.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }

    return app
