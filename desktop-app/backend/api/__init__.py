"""Backend API Package"""

from fastapi import APIRouter

from .chat import router as chat_router
from .models import router as models_router
from .automation import router as automation_router
from .filesystem import router as filesystem_router
from .terminal import router as terminal_router


# Main router that includes all sub-routers
api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(models_router)
api_router.include_router(automation_router)
api_router.include_router(filesystem_router)
api_router.include_router(terminal_router)


__all__ = ["api_router"]
