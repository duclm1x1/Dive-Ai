"""
Terminal API - Command execution

- POST /terminal/execute
- POST /terminal/spawn
- GET /terminal/processes
"""

import subprocess
import os
import asyncio
from typing import Optional, Dict, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/terminal", tags=["Terminal"])


class ExecuteRequest(BaseModel):
    command: str
    cwd: str = "."
    timeout: int = 60
    shell: bool = True


class ExecuteResponse(BaseModel):
    output: str
    error: str
    code: int
    duration_ms: float


# Active processes
_processes: Dict[str, subprocess.Popen] = {}


@router.post("/execute", response_model=ExecuteResponse)
async def execute_command(request: ExecuteRequest):
    """Execute command and wait for result"""
    start = datetime.now()
    
    try:
        result = subprocess.run(
            request.command,
            shell=request.shell,
            cwd=request.cwd,
            capture_output=True,
            text=True,
            timeout=request.timeout
        )
        
        duration = (datetime.now() - start).total_seconds() * 1000
        
        return ExecuteResponse(
            output=result.stdout,
            error=result.stderr,
            code=result.returncode,
            duration_ms=duration
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(408, f"Command timed out after {request.timeout}s")
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/spawn")
async def spawn_process(command: str, cwd: str = "."):
    """Spawn background process"""
    import uuid
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        pid = str(uuid.uuid4())[:8]
        _processes[pid] = process
        
        return {
            "pid": pid,
            "command": command,
            "status": "running"
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/processes")
async def list_processes():
    """List spawned processes"""
    result = []
    
    for pid, proc in list(_processes.items()):
        poll = proc.poll()
        
        if poll is None:
            status = "running"
        else:
            status = "completed"
            # Clean up completed processes
            del _processes[pid]
        
        result.append({
            "pid": pid,
            "status": status,
            "returncode": poll
        })
    
    return {"processes": result}


@router.post("/kill/{pid}")
async def kill_process(pid: str):
    """Kill spawned process"""
    if pid not in _processes:
        raise HTTPException(404, f"Process {pid} not found")
    
    try:
        _processes[pid].terminate()
        del _processes[pid]
        return {"killed": pid}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/cwd")
async def get_cwd():
    """Get current working directory"""
    return {"cwd": os.getcwd()}


@router.post("/cd")
async def change_directory(path: str):
    """Change working directory"""
    try:
        os.chdir(path)
        return {"cwd": os.getcwd()}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/env")
async def get_environment():
    """Get environment variables (safe subset)"""
    safe_vars = ["PATH", "HOME", "USER", "SHELL", "TERM", "PWD"]
    return {
        "env": {k: os.environ.get(k, "") for k in safe_vars if k in os.environ}
    }
