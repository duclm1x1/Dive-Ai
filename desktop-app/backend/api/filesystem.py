"""
File System API - File operations

- POST /fs/read
- POST /fs/write
- POST /fs/list
- POST /fs/mkdir
- POST /fs/delete
"""

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/fs", tags=["FileSystem"])


class ReadRequest(BaseModel):
    path: str
    encoding: str = "utf-8"


class WriteRequest(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"
    create_dirs: bool = True


class ListRequest(BaseModel):
    path: str
    recursive: bool = False
    pattern: str = "*"


class DeleteRequest(BaseModel):
    path: str
    force: bool = False


class FileInfo(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int
    modified: str


@router.post("/read")
async def read_file(request: ReadRequest):
    """Read file content"""
    try:
        path = Path(request.path)
        
        if not path.exists():
            raise HTTPException(404, f"File not found: {request.path}")
        
        if path.is_dir():
            raise HTTPException(400, "Cannot read directory")
        
        content = path.read_text(encoding=request.encoding)
        
        return {
            "path": str(path.absolute()),
            "content": content,
            "size": len(content),
            "encoding": request.encoding
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/write")
async def write_file(request: WriteRequest):
    """Write file content"""
    try:
        path = Path(request.path)
        
        if request.create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(request.content, encoding=request.encoding)
        
        return {
            "success": True,
            "path": str(path.absolute()),
            "size": len(request.content)
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/list")
async def list_directory(request: ListRequest):
    """List directory contents"""
    try:
        path = Path(request.path)
        
        if not path.exists():
            raise HTTPException(404, f"Path not found: {request.path}")
        
        if not path.is_dir():
            raise HTTPException(400, "Not a directory")
        
        items = []
        
        if request.recursive:
            for p in path.rglob(request.pattern):
                items.append(_file_info(p))
        else:
            for p in path.glob(request.pattern):
                items.append(_file_info(p))
        
        return {
            "path": str(path.absolute()),
            "items": items,
            "count": len(items)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/mkdir")
async def make_directory(path: str):
    """Create directory"""
    try:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(p.absolute())
        }
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/delete")
async def delete_file(request: DeleteRequest):
    """Delete file or directory"""
    try:
        path = Path(request.path)
        
        if not path.exists():
            raise HTTPException(404, f"Path not found: {request.path}")
        
        if path.is_dir():
            if request.force:
                import shutil
                shutil.rmtree(path)
            else:
                path.rmdir()
        else:
            path.unlink()
        
        return {
            "success": True,
            "deleted": str(path.absolute())
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/exists")
async def file_exists(path: str):
    """Check if file exists"""
    p = Path(path)
    return {
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else False,
        "is_dir": p.is_dir() if p.exists() else False
    }


@router.post("/info")
async def file_info(path: str):
    """Get file info"""
    try:
        p = Path(path)
        
        if not p.exists():
            raise HTTPException(404, f"Path not found: {path}")
        
        return _file_info(p)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


def _file_info(p: Path) -> dict:
    """Get file info dict"""
    stat = p.stat()
    return {
        "name": p.name,
        "path": str(p.absolute()),
        "is_dir": p.is_dir(),
        "size": stat.st_size if p.is_file() else 0,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }
