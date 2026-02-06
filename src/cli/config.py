#!/usr/bin/env python3
"""
Dive AI CLI - Configuration Manager
=====================================
Manages all configuration for Dive AI, including:
- LLM API keys and endpoints
- UI-TARS connection settings
- Memory storage paths
- Model routing preferences
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

DIVE_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = DIVE_ROOT / ".dive"
CONFIG_FILE = CONFIG_DIR / "config.json"
MEMORY_DIR = DIVE_ROOT / "memory"


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7

    # Cost optimization: route simple tasks to cheaper models
    fast_model: str = "gpt-4.1-nano"       # For simple tasks
    standard_model: str = "gpt-4.1-mini"   # For medium tasks
    power_model: str = "gemini-2.5-flash"  # For complex tasks


@dataclass
class UITarsConfig:
    """UI-TARS Desktop integration configuration."""
    enabled: bool = False
    cli_path: str = "agent-tars"  # npx @agent-tars/cli or global install
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    mode: str = "local"  # local, remote, browser
    screenshot_dir: str = str(DIVE_ROOT / "screenshots")


@dataclass
class MemoryConfig:
    """Memory system configuration."""
    storage_dir: str = str(MEMORY_DIR)
    max_context_tokens: int = 8000
    auto_save: bool = True


@dataclass
class ServerConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class DiveConfig:
    """Master configuration for Dive AI."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    uitars: UITarsConfig = field(default_factory=UITarsConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    debug: bool = False
    version: str = "28.0.0"

    @classmethod
    def load(cls) -> "DiveConfig":
        """Load config from file and environment variables."""
        config = cls()

        # Load from config file if exists
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    data = json.load(f)
                if "llm" in data:
                    for k, v in data["llm"].items():
                        if hasattr(config.llm, k):
                            setattr(config.llm, k, v)
                if "uitars" in data:
                    for k, v in data["uitars"].items():
                        if hasattr(config.uitars, k):
                            setattr(config.uitars, k, v)
                if "memory" in data:
                    for k, v in data["memory"].items():
                        if hasattr(config.memory, k):
                            setattr(config.memory, k, v)
                if "server" in data:
                    for k, v in data["server"].items():
                        if hasattr(config.server, k):
                            setattr(config.server, k, v)
            except Exception:
                pass

        # Override with environment variables (highest priority)
        config.llm.api_key = os.getenv("OPENAI_API_KEY", config.llm.api_key)
        config.llm.base_url = os.getenv("OPENAI_BASE_URL", config.llm.base_url)
        config.llm.provider = os.getenv("DIVE_LLM_PROVIDER", config.llm.provider)
        config.llm.model = os.getenv("DIVE_LLM_MODEL", config.llm.model)

        config.uitars.enabled = os.getenv("DIVE_UITARS_ENABLED", "").lower() in ("1", "true", "yes")
        config.uitars.api_key = os.getenv("UITARS_API_KEY", config.llm.api_key)
        config.uitars.provider = os.getenv("UITARS_PROVIDER", config.uitars.provider)
        config.uitars.model = os.getenv("UITARS_MODEL", config.uitars.model)

        config.debug = os.getenv("DIVE_DEBUG", "").lower() in ("1", "true", "yes")

        return config

    def save(self):
        """Save current config to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "base_url": self.llm.base_url,
                "max_tokens": self.llm.max_tokens,
                "temperature": self.llm.temperature,
                "fast_model": self.llm.fast_model,
                "standard_model": self.llm.standard_model,
                "power_model": self.llm.power_model,
            },
            "uitars": {
                "enabled": self.uitars.enabled,
                "cli_path": self.uitars.cli_path,
                "provider": self.uitars.provider,
                "model": self.uitars.model,
                "mode": self.uitars.mode,
            },
            "memory": {
                "storage_dir": self.memory.storage_dir,
                "max_context_tokens": self.memory.max_context_tokens,
                "auto_save": self.memory.auto_save,
            },
            "server": {
                "host": self.server.host,
                "port": self.server.port,
                "workers": self.server.workers,
            },
            "version": self.version,
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "version": self.version,
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "has_api_key": bool(self.llm.api_key),
                "base_url": self.llm.base_url or "(default)",
                "fast_model": self.llm.fast_model,
                "standard_model": self.llm.standard_model,
                "power_model": self.llm.power_model,
            },
            "uitars": {
                "enabled": self.uitars.enabled,
                "mode": self.uitars.mode,
                "provider": self.uitars.provider,
                "model": self.uitars.model,
            },
            "memory": {
                "storage_dir": self.memory.storage_dir,
                "auto_save": self.memory.auto_save,
            },
            "debug": self.debug,
        }
