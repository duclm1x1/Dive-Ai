"""
Dive AI — Local File Storage
JSON-based persistent storage for conversations, memory, settings, and connections.
Local-first: everything works without Supabase.
"""

import os
import json
import time
import shutil
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


class LocalStorage:
    """Central storage manager. All reads/writes go through this."""

    DEFAULT_BASE = os.path.join(os.path.expanduser("~"), ".dive-ai")

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or self.DEFAULT_BASE)
        self._init_directories()
        self._conversation_index: List[Dict] = []
        self._settings_cache: Dict = {}
        self._load_index()
        self._load_settings()
        print(f"💾 Local storage: {self.base_path}")

    # ── Directory Setup ─────────────────────────

    def _init_directories(self):
        """Create directory structure on first run."""
        dirs = [
            self.base_path / "config",
            self.base_path / "conversations",
            self.base_path / "memory",
            self.base_path / "logs",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    # ── Safe File I/O ────────────────────────────

    def _safe_read_json(self, path: Path, default=None):
        """Read JSON with corruption protection."""
        if default is None:
            default = {}
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️ Corrupted file {path}: {e}")
            # Backup corrupted file
            backup = path.with_suffix(".corrupted")
            try:
                shutil.copy2(path, backup)
            except:
                pass
        return default

    def _safe_write_json(self, path: Path, data: Any):
        """Atomic write: write to .tmp then rename to prevent corruption."""
        try:
            tmp_path = path.with_suffix(".tmp")
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            # Atomic rename (Windows: need to remove target first)
            if path.exists():
                path.unlink()
            tmp_path.rename(path)
            return True
        except OSError as e:
            print(f"❌ Write failed {path}: {e}")
            return False

    # ── Conversations ────────────────────────────

    def _index_path(self) -> Path:
        return self.base_path / "conversations" / "index.json"

    def _conv_path(self, conv_id: str) -> Path:
        return self.base_path / "conversations" / f"{conv_id}.json"

    def _load_index(self):
        """Load conversation index."""
        self._conversation_index = self._safe_read_json(
            self._index_path(), default=[]
        )

    def _save_index(self):
        """Save conversation index."""
        self._safe_write_json(self._index_path(), self._conversation_index)

    def list_conversations(self) -> List[Dict]:
        """Return conversation list (most recent first)."""
        return sorted(
            self._conversation_index,
            key=lambda c: c.get("updated_at", ""),
            reverse=True,
        )

    def create_conversation(self, title: str = "New Chat") -> str:
        """Create a new conversation. Returns conv_id."""
        conv_id = f"conv_{int(time.time() * 1000)}"
        now = datetime.now().isoformat()

        entry = {
            "id": conv_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "message_count": 0,
        }
        self._conversation_index.append(entry)
        self._save_index()

        # Create empty conversation file
        conv_data = {
            "id": conv_id,
            "title": title,
            "created_at": now,
            "messages": [],
        }
        self._safe_write_json(self._conv_path(conv_id), conv_data)
        return conv_id

    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """Load full conversation with messages."""
        path = self._conv_path(conv_id)
        if not path.exists():
            return None
        return self._safe_read_json(path)

    def get_messages(self, conv_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a conversation."""
        conv = self.get_conversation(conv_id)
        if not conv:
            return []
        messages = conv.get("messages", [])
        return messages[-limit:] if limit else messages

    def save_message(
        self,
        conv_id: str,
        role: str,
        content: str,
        thinking: str = None,
        model: str = None,
        latency_ms: float = None,
        actions: List[Dict] = None,
        attachments: List[Dict] = None,
        tokens: int = 0,
    ) -> Dict:
        """Append a message to a conversation."""
        conv = self.get_conversation(conv_id)
        if not conv:
            # Auto-create if doesn't exist
            self.create_conversation("Auto Chat")
            conv = self.get_conversation(conv_id) or {
                "id": conv_id,
                "messages": [],
            }

        now = datetime.now().isoformat()
        message = {
            "role": role,
            "content": content,
            "timestamp": now,
        }
        if thinking:
            message["thinking"] = thinking
        if model:
            message["model"] = model
        if latency_ms is not None:
            message["latency_ms"] = latency_ms
        if actions:
            message["actions"] = actions
        if attachments:
            message["attachments"] = attachments
        if tokens:
            message["tokens"] = tokens

        conv["messages"].append(message)
        conv["updated_at"] = now
        self._safe_write_json(self._conv_path(conv_id), conv)

        # Update index
        for entry in self._conversation_index:
            if entry["id"] == conv_id:
                entry["updated_at"] = now
                entry["message_count"] = len(conv["messages"])
                # Auto-title from first user message
                if entry["title"] == "New Chat" and role == "user":
                    entry["title"] = content[:60] + ("..." if len(content) > 60 else "")
                break
        self._save_index()
        return message

    def update_conversation_title(self, conv_id: str, title: str):
        """Update conversation title."""
        conv = self.get_conversation(conv_id)
        if conv:
            conv["title"] = title
            self._safe_write_json(self._conv_path(conv_id), conv)
        for entry in self._conversation_index:
            if entry["id"] == conv_id:
                entry["title"] = title
                break
        self._save_index()

    def delete_conversation(self, conv_id: str) -> bool:
        """Delete a conversation."""
        path = self._conv_path(conv_id)
        try:
            if path.exists():
                path.unlink()
        except OSError:
            pass
        self._conversation_index = [
            c for c in self._conversation_index if c["id"] != conv_id
        ]
        self._save_index()
        return True

    # ── Settings ─────────────────────────────────

    def _settings_path(self) -> Path:
        return self.base_path / "config" / "settings.json"

    def _load_settings(self):
        self._settings_cache = self._safe_read_json(self._settings_path())

    def get_setting(self, key: str, default=None):
        return self._settings_cache.get(key, default)

    def save_setting(self, key: str, value: Any):
        self._settings_cache[key] = value
        self._safe_write_json(self._settings_path(), self._settings_cache)

    def get_all_settings(self) -> Dict:
        return dict(self._settings_cache)

    # ── Connections (API keys, URLs) ─────────────

    def _connections_path(self) -> Path:
        return self.base_path / "config" / "connections.json"

    def get_connections(self) -> Dict:
        """Get connection settings (keys masked for frontend)."""
        conns = self._safe_read_json(self._connections_path())
        return conns

    def get_connections_raw(self) -> Dict:
        """Get raw connection settings (with full keys, for backend use)."""
        return self._safe_read_json(self._connections_path())

    def save_connection(self, provider_id: str, url: str = None, api_key: str = None):
        """Save connection details for a provider."""
        conns = self._safe_read_json(self._connections_path())
        if provider_id not in conns:
            conns[provider_id] = {}
        if url is not None:
            conns[provider_id]["url"] = url
        if api_key is not None:
            conns[provider_id]["api_key"] = api_key
        conns[provider_id]["updated_at"] = datetime.now().isoformat()
        self._safe_write_json(self._connections_path(), conns)

        # Also update .env file for the running backend
        self._sync_to_env(provider_id, url, api_key)

    def _sync_to_env(self, provider_id: str, url: str = None, api_key: str = None):
        """Sync connection changes to .env file."""
        env_path = Path(__file__).parent / ".env"
        lines = []
        if env_path.exists():
            with open(env_path, "r") as f:
                lines = f.readlines()

        # Map provider IDs to env var names
        key_map = {
            "v98": "V98_API_KEY",
            "aicoding": "AICODING_API_KEY",
        }

        env_key = key_map.get(provider_id)
        if env_key and api_key:
            # Update or add the key
            found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f"{env_key}="):
                    lines[i] = f"{env_key}={api_key}\n"
                    found = True
                    break
            if not found:
                lines.append(f"\n{env_key}={api_key}\n")

            with open(env_path, "w") as f:
                f.writelines(lines)

    def get_connections_masked(self) -> Dict:
        """Get connections with API keys masked for display."""
        conns = self.get_connections()
        masked = {}
        for pid, data in conns.items():
            masked[pid] = dict(data)
            if "api_key" in masked[pid] and masked[pid]["api_key"]:
                key = masked[pid]["api_key"]
                masked[pid]["api_key_masked"] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                masked[pid]["has_key"] = True
            else:
                masked[pid]["has_key"] = False
        return masked

    # ── Memory Files ─────────────────────────────

    def _memory_path(self, name: str) -> Path:
        return self.base_path / "memory" / f"{name}.json"

    def get_memory(self, name: str = "context") -> Dict:
        return self._safe_read_json(self._memory_path(name))

    def save_memory(self, name: str, data: Dict):
        self._safe_write_json(self._memory_path(name), data)

    # ── Action Logs ──────────────────────────────

    def _action_log_path(self) -> Path:
        return self.base_path / "logs" / "actions.json"

    def log_action(self, action: Dict):
        """Append action to log (keep last 500)."""
        logs = self._safe_read_json(self._action_log_path(), default=[])
        action["logged_at"] = datetime.now().isoformat()
        logs.append(action)
        logs = logs[-500:]  # Keep last 500
        self._safe_write_json(self._action_log_path(), logs)

    def get_action_logs(self, limit: int = 50) -> List[Dict]:
        logs = self._safe_read_json(self._action_log_path(), default=[])
        return logs[-limit:]

    # ── Storage Stats ────────────────────────────

    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics."""
        total_size = 0
        file_count = 0

        for root, dirs, files in os.walk(self.base_path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total_size += os.path.getsize(fp)
                    file_count += 1
                except OSError:
                    pass

        return {
            "path": str(self.base_path),
            "used_bytes": total_size,
            "used_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "conversation_count": len(self._conversation_index),
            "memory_initialized": (self.base_path / "memory" / "context.json").exists(),
        }


# ── Singleton ────────────────────────────────

_storage: Optional[LocalStorage] = None


def get_storage(base_path: str = None) -> LocalStorage:
    """Get or create storage singleton."""
    global _storage
    if _storage is None:
        _storage = LocalStorage(base_path)
    return _storage
