"""LLM Connections Package - Multi-provider, multi-model"""

from .connections import (
    V98ConnectionManager,
    get_manager,
    quick_chat,
    print_summary,
    get_all_models,
    LLMResponse,
    LLMProvider,
    LLMModel,
    LLMClient,
    ALL_MODELS,
    ALL_PROVIDERS,
    load_config,
    save_config,
)

LLMConnectionManager = V98ConnectionManager

__all__ = [
    "V98ConnectionManager",
    "LLMConnectionManager",
    "get_manager",
    "quick_chat",
    "print_summary",
    "get_all_models",
    "LLMResponse",
    "LLMProvider",
    "LLMModel",
    "LLMClient",
    "ALL_MODELS",
    "ALL_PROVIDERS",
    "load_config",
    "save_config",
]
