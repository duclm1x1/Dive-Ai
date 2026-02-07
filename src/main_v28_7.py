"""
Dive AI V28.7 - Main Application
Integrates all V2 components: Coder, Memory, Skills, Orchestrator
"""

import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.coder_v17 import DiveCoderV17, CodeContext, CodeLanguage, CodeQuality
from src.memory_v2 import DiveMemorySystem, MemoryType
from src.skills_engine_v2 import DiveSkillsEngine
from src.orchestrator_v2 import DiveOrchestratorV2, Task

# Initialize FastAPI app
app = FastAPI(
    title="Dive AI V28.7 API",
    description="Comprehensive upgrade with V2 components",
    version="28.7.0"
)

# Initialize Dive AI components
coder = DiveCoderV17()
memory = DiveMemorySystem()
skills = DiveSkillsEngine()
orchestrator = DiveOrchestratorV2(num_agents=512)


# --- API Models ---

class CodeGenRequest(BaseModel):
    prompt: str
    language: str
    framework: str = None
    quality: str = "standard"

class MemoryStoreRequest(BaseModel):
    content: str
    memory_type: str
    tags: list = []

class SkillRequest(BaseModel):
    skill_name: str
    params: dict = {}

class TaskRequest(BaseModel):
    name: str
    description: str = ""


# --- API Endpoints ---

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "28.7.0",
        "components": {
            "coder": coder.version,
            "memory": memory.version,
            "skills": skills.version,
            "orchestrator": orchestrator.version
        }
    }

# Coder V17 Endpoints
@app.post("/api/v1/code/generate")
def generate_code(req: CodeGenRequest):
    try:
        context = CodeContext(
            language=CodeLanguage(req.language),
            framework=req.framework,
            quality_level=CodeQuality(req.quality)
        )
        result = coder.generate_code(req.prompt, context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Memory V2 Endpoints
@app.post("/api/v1/memory/store")
def store_memory(req: MemoryStoreRequest):
    try:
        mem_type = MemoryType(req.memory_type)
        if mem_type == MemoryType.EPISODIC:
            memory.store_episodic_memory(req.content, tags=req.tags)
        elif mem_type == MemoryType.SEMANTIC:
            memory.store_semantic_memory(req.content, tags=req.tags)
        elif mem_type == MemoryType.PROCEDURAL:
            memory.store_procedural_memory(req.content, tags=req.tags)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Skills V2 Endpoints
@app.post("/api/v1/skills/execute")
async def execute_skill(req: SkillRequest):
    try:
        result = await skills.execute_skill(req.skill_name, **req.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Orchestrator V2 Endpoints
@app.post("/api/v1/orchestrator/task")
async def submit_task(req: TaskRequest):
    try:
        task = Task(name=req.name, description=req.description)
        task_id = await orchestrator.submit_task(task)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/orchestrator/status")
def get_orchestrator_status():
    return orchestrator.get_cluster_status()


# --- Main Entry Point ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8286)
