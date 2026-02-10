"""
Dive AI - LLM Connections
Multi-provider, multi-model support with latency tracking.
All config from config.yaml — no hardcoded values.
"""

import os
import time
import yaml
import asyncio
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


# ============================================================
# Data Classes
# ============================================================

@dataclass
class LLMModel:
    id: str
    name: str
    model: str
    vendor: str
    provider_id: str
    provider_name: str
    thinking: bool = False
    priority: int = 5
    context_length: int = 200000
    max_output: int = 8192
    supports_vision: bool = False
    supports_streaming: bool = True
    latency_ms: float = -1  # -1 = not tested
    status: str = "unknown"  # connected / failed / unknown

    def to_dict(self):
        return asdict(self)


@dataclass
class LLMProvider:
    id: str
    name: str
    base_url: str
    api_key_env: str
    api_key: str = ""
    rate_limit: int = 100
    is_primary: bool = False
    models: List[LLMModel] = field(default_factory=list)
    connected: bool = False
    latency_ms: float = -1

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "base_url": self.base_url,
            "api_key_env": self.api_key_env,
            "has_key": bool(self.api_key),
            "rate_limit": self.rate_limit,
            "is_primary": self.is_primary,
            "connected": self.connected,
            "latency_ms": self.latency_ms,
            "model_count": len(self.models),
        }


@dataclass 
class LLMResponse:
    success: bool
    content: str = ""
    thinking: str = ""
    model: str = ""
    provider: str = ""
    tokens: int = 0
    latency_ms: float = 0
    error: str = ""

    def to_dict(self):
        return asdict(self)


# ============================================================
# Config Loader
# ============================================================

CONFIG_PATH = Path(__file__).parent / "config.yaml"

def load_config() -> Dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    return {"providers": {}}

def save_config(config: Dict):
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


# ============================================================
# LLM Client
# ============================================================

class LLMClient:
    """OpenAI-compatible API client"""

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, messages: List[Dict], model: str, 
             temperature: float = 0.7, max_tokens: int = 4096,
             stream: bool = False) -> LLMResponse:
        """Send chat completion"""
        start = time.time()

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            resp = requests.post(
                f"{self.provider.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=120
            )
            latency = (time.time() - start) * 1000
            resp.raise_for_status()
            data = resp.json()

            choice = data.get("choices", [{}])[0]
            message = choice.get("message", {})
            usage = data.get("usage", {})

            return LLMResponse(
                success=True,
                content=message.get("content", ""),
                thinking=message.get("thinking", ""),
                model=data.get("model", model),
                provider=self.provider.name,
                tokens=usage.get("total_tokens", 0),
                latency_ms=round(latency, 2),
            )
        except requests.exceptions.Timeout:
            return LLMResponse(success=False, error="Request timed out", provider=self.provider.name)
        except requests.exceptions.ConnectionError:
            return LLMResponse(success=False, error="Connection failed", provider=self.provider.name)
        except Exception as e:
            return LLMResponse(success=False, error=str(e), provider=self.provider.name)

    def stream_chat(self, messages: List[Dict], model: str,
                    temperature: float = 0.7, max_tokens: int = 4096):
        """Stream chat completion — yields (event_type, data) tuples.
        Event types: 'token', 'thinking', 'done', 'error'
        """
        import json as _json

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        try:
            resp = requests.post(
                f"{self.provider.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=180,
                stream=True,
            )
            resp.raise_for_status()

            full_content = ""
            full_thinking = ""
            model_name = model

            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = _json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        model_name = chunk.get("model", model)

                        # Content token
                        if "content" in delta and delta["content"]:
                            token = delta["content"]
                            full_content += token
                            yield ("token", token)

                        # Thinking token (Claude-style)
                        if "thinking" in delta and delta["thinking"]:
                            thinking_token = delta["thinking"]
                            full_thinking += thinking_token
                            yield ("thinking", thinking_token)

                        # Role-only chunks (skip)
                        if "role" in delta and "content" not in delta:
                            continue

                    except _json.JSONDecodeError:
                        continue

            yield ("done", {
                "content": full_content,
                "thinking": full_thinking,
                "model": model_name,
                "provider": self.provider.name,
            })

        except Exception as e:
            yield ("error", str(e))

    def test_connection(self) -> tuple:
        """Quick ping test, returns (success, latency_ms)"""
        start = time.time()
        try:
            resp = requests.post(
                f"{self.provider.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.provider.models[0].model if self.provider.models else "test",
                    "messages": [{"role": "user", "content": "Reply OK"}],
                    "max_tokens": 5,
                },
                timeout=30
            )
            latency = (time.time() - start) * 1000
            if resp.status_code == 200:
                return True, round(latency, 2)
            return False, round(latency, 2)
        except Exception:
            latency = (time.time() - start) * 1000
            return False, round(latency, 2)


# ============================================================
# Connection Manager
# ============================================================

class V98ConnectionManager:
    """Multi-provider LLM connection manager"""

    def __init__(self):
        self.config = load_config()
        self.providers: Dict[str, LLMProvider] = {}
        self.clients: Dict[str, LLMClient] = {}
        self.all_models: List[LLMModel] = []
        self._load_providers()

    def _load_providers(self):
        """Load providers and models from config"""
        self.providers.clear()
        self.clients.clear()
        self.all_models.clear()

        for pid, pconf in self.config.get("providers", {}).items():
            api_key = os.getenv(pconf.get("api_key_env", ""), "")

            provider = LLMProvider(
                id=pid,
                name=pconf.get("name", pid),
                base_url=pconf.get("base_url", ""),
                api_key_env=pconf.get("api_key_env", ""),
                api_key=api_key,
                rate_limit=pconf.get("rate_limit", 100),
                is_primary=pconf.get("is_primary", False),
                connected=bool(api_key),
            )

            # Load models
            for mconf in pconf.get("models", []):
                model = LLMModel(
                    id=mconf.get("id", ""),
                    name=mconf.get("name", ""),
                    model=mconf.get("model", ""),
                    vendor=mconf.get("vendor", "Unknown"),
                    provider_id=pid,
                    provider_name=provider.name,
                    thinking=mconf.get("thinking", False),
                    priority=mconf.get("priority", 5),
                    context_length=mconf.get("context_length", 200000),
                    max_output=mconf.get("max_output", 8192),
                    supports_vision=mconf.get("supports_vision", False),
                    supports_streaming=mconf.get("supports_streaming", True),
                    status="ready" if api_key else "no_key",
                )
                provider.models.append(model)
                self.all_models.append(model)

            self.providers[pid] = provider
            if api_key:
                self.clients[pid] = LLMClient(provider)

    def reload(self):
        """Reload config from disk"""
        self.config = load_config()
        self._load_providers()

    def get_model(self, model_id: str) -> Optional[LLMModel]:
        """Find model by ID across all providers"""
        for m in self.all_models:
            if m.id == model_id:
                return m
        return None

    def get_default_model(self) -> Optional[LLMModel]:
        """Get default model from routing config"""
        default_id = self.config.get("routing", {}).get("default_model", "")
        model = self.get_model(default_id)
        if model:
            return model
        # Fallback: first available model from primary provider
        for p in self.providers.values():
            if p.is_primary and p.connected and p.models:
                return p.models[0]
        # Fallback: any available model
        for m in self.all_models:
            if m.status != "no_key":
                return m
        return self.all_models[0] if self.all_models else None

    def get_client(self, provider_id: str) -> Optional[LLMClient]:
        """Get client for provider"""
        return self.clients.get(provider_id)

    def chat(self, message: str, system: str = "", 
             model_id: str = None, messages: list = None) -> LLMResponse:
        """Send chat with failover"""
        # Find model
        model = self.get_model(model_id) if model_id else self.get_default_model()
        if not model:
            return LLMResponse(success=False, error="No models available")

        # Build messages (use provided messages or build from scratch)
        if messages:
            chat_messages = list(messages)
            if system and (not chat_messages or chat_messages[0].get('role') != 'system'):
                chat_messages.insert(0, {"role": "system", "content": system})
        else:
            chat_messages = []
            if system:
                chat_messages.append({"role": "system", "content": system})
            chat_messages.append({"role": "user", "content": message})

        # Try the model's provider first
        client = self.get_client(model.provider_id)
        if client:
            result = client.chat(chat_messages, model.model)
            if result.success:
                model.latency_ms = result.latency_ms
                model.status = "connected"
                return result

        # Failover chain
        chain = self.config.get("failover", {}).get("chain", [])
        for pid in chain:
            if pid == model.provider_id:
                continue  # Already tried
            alt_client = self.get_client(pid)
            if alt_client:
                # Find equivalent model in fallback provider
                alt_model = None
                alt_provider = self.providers.get(pid)
                if alt_provider:
                    for m in alt_provider.models:
                        if m.vendor == model.vendor:
                            alt_model = m
                            break
                    if not alt_model and alt_provider.models:
                        alt_model = alt_provider.models[0]

                if alt_model:
                    result = alt_client.chat(chat_messages, alt_model.model)
                    if result.success:
                        alt_model.latency_ms = result.latency_ms
                        alt_model.status = "connected"
                        return result

        return LLMResponse(success=False, error="All providers failed")

    def stream_chat(self, message: str, system: str = "",
                    model_id: str = None, messages: list = None):
        """Stream chat with model resolution — yields (event_type, data) tuples."""
        model = self.get_model(model_id) if model_id else self.get_default_model()
        if not model:
            yield ("error", "No models available")
            return

        if messages:
            chat_messages = list(messages)
            if system and (not chat_messages or chat_messages[0].get('role') != 'system'):
                chat_messages.insert(0, {"role": "system", "content": system})
        else:
            chat_messages = []
            if system:
                chat_messages.append({"role": "system", "content": system})
            chat_messages.append({"role": "user", "content": message})

        client = self.get_client(model.provider_id)
        if client:
            yield from client.stream_chat(chat_messages, model.model)

    def test_provider(self, provider_id: str) -> Dict:
        """Test a provider connection"""
        client = self.get_client(provider_id)
        if not client:
            provider = self.providers.get(provider_id)
            if provider and not provider.api_key:
                return {"connected": False, "latency_ms": -1, "error": f"{provider.api_key_env} not set"}
            return {"connected": False, "latency_ms": -1, "error": "Provider not found"}

        success, latency = client.test_connection()
        provider = self.providers[provider_id]
        provider.connected = success
        provider.latency_ms = latency

        # Update model statuses
        for m in provider.models:
            m.status = "connected" if success else "failed"
            m.latency_ms = latency

        return {"connected": success, "latency_ms": latency}

    def models_grouped_by_vendor(self) -> Dict:
        """Return models grouped by vendor with status"""
        groups = {}
        for m in sorted(self.all_models, key=lambda x: x.priority):
            vendor = m.vendor
            if vendor not in groups:
                groups[vendor] = []
            groups[vendor].append(m.to_dict())
        return groups

    def status(self) -> Dict:
        """Overall status"""
        available = sum(1 for p in self.providers.values() if p.connected)
        primary = None
        for p in self.providers.values():
            if p.is_primary:
                primary = p
                break

        return {
            "total_providers": len(self.providers),
            "available_providers": available,
            "total_models": len(self.all_models),
            "primary_provider": primary.name if primary else "None",
            "primary_available": primary.connected if primary else False,
            "primary_model": primary.models[0].name if primary and primary.models else "None",
        }

    # Provider CRUD
    def add_provider(self, pid: str, name: str, base_url: str, 
                     api_key_env: str, models: List[Dict] = None) -> Dict:
        """Add new provider to config"""
        self.config.setdefault("providers", {})[pid] = {
            "name": name,
            "base_url": base_url,
            "api_key_env": api_key_env,
            "rate_limit": 60,
            "is_primary": False,
            "models": models or [],
        }
        save_config(self.config)
        self._load_providers()
        return {"success": True, "provider_id": pid}

    def update_provider(self, pid: str, updates: Dict) -> Dict:
        """Update provider config"""
        if pid not in self.config.get("providers", {}):
            return {"success": False, "error": "Provider not found"}
        self.config["providers"][pid].update(updates)
        save_config(self.config)
        self._load_providers()
        return {"success": True}

    def remove_provider(self, pid: str) -> Dict:
        """Remove provider"""
        if pid in self.config.get("providers", {}):
            del self.config["providers"][pid]
            save_config(self.config)
            self._load_providers()
            return {"success": True}
        return {"success": False, "error": "Provider not found"}


# ============================================================
# Module-level convenience
# ============================================================

_manager: Optional[V98ConnectionManager] = None

def get_manager() -> V98ConnectionManager:
    global _manager
    if _manager is None:
        _manager = V98ConnectionManager()
    return _manager

def get_all_models() -> List[Dict]:
    return [m.to_dict() for m in get_manager().all_models]

ALL_MODELS = []  # Populated on import
ALL_PROVIDERS = []

def _init_module():
    global ALL_MODELS, ALL_PROVIDERS
    mgr = get_manager()
    ALL_MODELS = get_all_models()
    ALL_PROVIDERS = [p.to_dict() for p in mgr.providers.values()]

_init_module()

async def quick_chat(message: str, system: str = "", model_id: str = None, messages: list = None) -> Dict:
    """Quick async-compatible chat"""
    mgr = get_manager()
    result = mgr.chat(message=message, system=system, model_id=model_id, messages=messages)
    return result.to_dict()

def stream_chat_generator(message: str, system: str = "", model_id: str = None, messages: list = None):
    """Generator that yields (event_type, data) from LLM streaming."""
    mgr = get_manager()
    yield from mgr.stream_chat(message=message, system=system, model_id=model_id, messages=messages)

def print_summary():
    """Print connection summary"""
    mgr = get_manager()
    print("\n" + "=" * 60)
    print(f"🤿 Dive AI - LLM Connections")
    print("=" * 60)

    for i, (pid, provider) in enumerate(mgr.providers.items(), 1):
        star = "⭐" if provider.is_primary else "  "
        status = "✅" if provider.connected else "❌"
        first_model = provider.models[0].name if provider.models else "No models"
        key_status = "set" if provider.api_key else "NOT SET"
        
        print(f"{i}. {star} {status} {provider.name:20s} → {first_model}")
        print(f"      URL: {provider.base_url}")
        print(f"      Key: {provider.api_key_env} = {key_status}")
        print(f"      Models: {len(provider.models)}")

    total = len(mgr.providers)
    available = sum(1 for p in mgr.providers.values() if p.connected)
    print("-" * 60)
    print(f"Available: {available}/{total} providers, {len(mgr.all_models)} models")
    print("=" * 60)
