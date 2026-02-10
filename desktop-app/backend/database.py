"""
Dive AI — SQLite Database Layer
Local-first database at D:\Antigravity\Dive_Ai_Database\dive_ai.db
Replaces JSON file storage with proper relational DB.
Background sync to Supabase for cloud backup.
"""

import os
import json
import sqlite3
import uuid
import asyncio
import traceback
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# ============================================================
# Configuration
# ============================================================

DB_DIR = Path(r"D:\Antigravity\Dive_Ai_Database")
DB_PATH = DB_DIR / "dive_ai.db"

# Fallback for non-Windows systems
if not DB_DIR.parent.exists():
    DB_DIR = Path.home() / ".dive-ai" / "database"

DB_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Schema
# ============================================================

SCHEMA_SQL = """
-- Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL DEFAULT 'New Chat',
    model TEXT DEFAULT '',
    message_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    cloud_id TEXT,
    synced_at TEXT
);

-- Messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    thinking TEXT,
    model TEXT,
    latency_ms REAL,
    tokens INTEGER DEFAULT 0,
    actions TEXT,
    attachments TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    cloud_synced INTEGER DEFAULT 0
);

-- Long-term memory
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT,
    value TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Action logs
CREATE TABLE IF NOT EXISTS action_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    action_data TEXT,
    success INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Algorithm execution results
CREATE TABLE IF NOT EXISTS algorithm_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    algorithm_name TEXT NOT NULL,
    inputs TEXT,
    output TEXT,
    gpa_score REAL,
    duration_ms INTEGER,
    status TEXT DEFAULT 'success',
    created_at TEXT DEFAULT (datetime('now')),
    cloud_synced INTEGER DEFAULT 0
);

-- Settings (local only)
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Connections (local only, API keys)
CREATE TABLE IF NOT EXISTS connections (
    provider_id TEXT PRIMARY KEY,
    url TEXT,
    api_key TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_unsynced ON messages(cloud_synced) WHERE cloud_synced = 0;
CREATE INDEX IF NOT EXISTS idx_memory_category ON memory(category);
CREATE INDEX IF NOT EXISTS idx_algo_runs_name ON algorithm_runs(algorithm_name);
CREATE INDEX IF NOT EXISTS idx_action_logs_created ON action_logs(created_at);
"""


# ============================================================
# DiveDatabase — Drop-in replacement for LocalStorage
# ============================================================

class DiveDatabase:
    """
    SQLite-based storage for Dive AI Desktop.
    Same API as LocalStorage for backward compatibility.
    """

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
        self.base_path = str(self.db_path.parent)  # backward compat with LocalStorage
        print(f"💾 Database initialized: {self.db_path}")

    def _init_db(self):
        """Create tables if they don't exist."""
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")  # Better concurrent access
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._init_db()
        return self._conn

    # ── Conversations ───────────────────────────────────

    def list_conversations(self) -> List[Dict]:
        """Return conversation list (most recent first)."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, title, model, message_count, created_at, updated_at "
            "FROM conversations ORDER BY updated_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def create_conversation(self, title: str = "New Chat") -> str:
        """Create a new conversation. Returns conv_id."""
        conv_id = str(uuid.uuid4())[:8] + "-" + datetime.now().strftime("%H%M%S")
        now = datetime.now().isoformat()
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (conv_id, title, now, now)
        )
        conn.commit()
        return conv_id

    def get_conversation(self, conv_id: str) -> Optional[Dict]:
        """Load full conversation with messages."""
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        if not row:
            return None
        conv = dict(row)
        conv["messages"] = self.get_messages(conv_id)
        return conv

    def get_messages(self, conv_id: str, limit: int = 100) -> List[Dict]:
        """Get messages from a conversation."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM messages WHERE conversation_id = ? "
            "ORDER BY created_at ASC LIMIT ?",
            (conv_id, limit)
        ).fetchall()
        result = []
        for r in rows:
            msg = dict(r)
            # Parse JSON fields
            if msg.get("actions"):
                try:
                    msg["actions"] = json.loads(msg["actions"])
                except:
                    pass
            if msg.get("attachments"):
                try:
                    msg["attachments"] = json.loads(msg["attachments"])
                except:
                    pass
            result.append(msg)
        return result

    def save_message(self, conv_id: str, role: str, content: str,
                     thinking: str = None, model: str = None,
                     latency_ms: float = None, actions: List[Dict] = None,
                     attachments: List[Dict] = None, tokens: int = 0) -> int:
        """Save a message to a conversation. Returns message id."""
        now = datetime.now().isoformat()
        conn = self._get_conn()

        # Auto-create conversation if it doesn't exist
        existing = conn.execute(
            "SELECT id FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (conv_id, "New Chat", now, now)
            )

        cursor = conn.execute(
            "INSERT INTO messages (conversation_id, role, content, thinking, model, "
            "latency_ms, tokens, actions, attachments, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                conv_id, role, content, thinking, model,
                latency_ms, tokens,
                json.dumps(actions) if actions else None,
                json.dumps(attachments) if attachments else None,
                now
            )
        )

        # Update conversation
        conn.execute(
            "UPDATE conversations SET message_count = message_count + 1, updated_at = ? WHERE id = ?",
            (now, conv_id)
        )

        # Auto-title from first user message
        if role == "user":
            conv = conn.execute(
                "SELECT message_count, title FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()
            if conv and conv["message_count"] <= 1 and conv["title"] == "New Chat":
                auto_title = content[:50].strip()
                if len(content) > 50:
                    auto_title += "..."
                conn.execute(
                    "UPDATE conversations SET title = ? WHERE id = ?",
                    (auto_title, conv_id)
                )

        conn.commit()
        return cursor.lastrowid

    def update_conversation_title(self, conv_id: str, title: str):
        """Update conversation title."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title, datetime.now().isoformat(), conv_id)
        )
        conn.commit()

    def delete_conversation(self, conv_id: str):
        """Delete a conversation and all its messages."""
        conn = self._get_conn()
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conv_id,))
        conn.execute("DELETE FROM conversations WHERE id = ?", (conv_id,))
        conn.commit()

    # ── Settings ────────────────────────────────────────

    def get_setting(self, key: str, default=None):
        conn = self._get_conn()
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except:
                return row["value"]
        return default

    def save_setting(self, key: str, value: Any):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(value) if not isinstance(value, str) else value,
             datetime.now().isoformat())
        )
        conn.commit()

    def get_all_settings(self) -> Dict:
        conn = self._get_conn()
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        result = {}
        for r in rows:
            try:
                result[r["key"]] = json.loads(r["value"])
            except:
                result[r["key"]] = r["value"]
        return result

    # ── Connections (API keys — local only) ─────────────

    def get_connections(self) -> Dict:
        """Get connection settings (keys masked for frontend)."""
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM connections").fetchall()
        result = {}
        for r in rows:
            d = dict(r)
            # Mask API key for display
            if d.get("api_key"):
                key = d["api_key"]
                d["api_key_masked"] = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
                d["has_key"] = True
            else:
                d["api_key_masked"] = ""
                d["has_key"] = False
            result[d["provider_id"]] = d
        return result

    def get_connections_raw(self) -> Dict:
        """Get raw connection settings (with full keys, for backend use)."""
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM connections").fetchall()
        return {r["provider_id"]: dict(r) for r in rows}

    def save_connection(self, provider_id: str, url: str = None, api_key: str = None):
        """Save connection details for a provider."""
        conn = self._get_conn()
        now = datetime.now().isoformat()

        existing = conn.execute(
            "SELECT * FROM connections WHERE provider_id = ?", (provider_id,)
        ).fetchone()

        if existing:
            updates = []
            params = []
            if url is not None:
                updates.append("url = ?")
                params.append(url)
            if api_key is not None:
                updates.append("api_key = ?")
                params.append(api_key)
            updates.append("updated_at = ?")
            params.append(now)
            params.append(provider_id)
            conn.execute(
                f"UPDATE connections SET {', '.join(updates)} WHERE provider_id = ?",
                params
            )
        else:
            conn.execute(
                "INSERT INTO connections (provider_id, url, api_key, updated_at) VALUES (?, ?, ?, ?)",
                (provider_id, url or "", api_key or "", now)
            )
        conn.commit()

        # Also sync to .env
        self._sync_to_env(provider_id, url, api_key)

    def get_connections_masked(self) -> Dict:
        """Get connections with API keys masked for display."""
        return self.get_connections()

    def _sync_to_env(self, provider_id: str, url: str = None, api_key: str = None):
        """Sync connection changes to .env file."""
        env_path = Path(__file__).parent / ".env"
        env_vars = {}

        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, _, v = line.partition("=")
                        env_vars[k.strip()] = v.strip()

        key_map = {
            "v98": "V98_API_KEY",
            "aicoding": "AICODING_API_KEY",
            "openai": "OPENAI_API_KEY",
        }

        env_key = key_map.get(provider_id.lower())
        if env_key and api_key:
            env_vars[env_key] = api_key
            os.environ[env_key] = api_key

        with open(env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")

    # ── Memory ──────────────────────────────────────────

    def get_memory(self, name: str = "context") -> Dict:
        """Get memory data (backward compatible with JSON format)."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT category, key, value FROM memory"
        ).fetchall()

        result = {
            "user_facts": [],
            "preferences": {},
            "key_topics": [],
        }

        for r in rows:
            cat = r["category"]
            if cat == "fact":
                result["user_facts"].append(r["value"])
            elif cat == "preference":
                result["preferences"][r["key"]] = r["value"]
            elif cat == "topic":
                result["key_topics"].append(r["value"])

        return result

    def save_memory(self, name: str, data: Dict):
        """Save memory data (backward compatible with JSON format)."""
        conn = self._get_conn()
        now = datetime.now().isoformat()

        # Clear and rebuild
        conn.execute("DELETE FROM memory")

        for fact in data.get("user_facts", []):
            conn.execute(
                "INSERT INTO memory (category, value, created_at) VALUES ('fact', ?, ?)",
                (fact, now)
            )

        for k, v in data.get("preferences", {}).items():
            conn.execute(
                "INSERT INTO memory (category, key, value, created_at) VALUES ('preference', ?, ?, ?)",
                (k, str(v), now)
            )

        for topic in data.get("key_topics", []):
            conn.execute(
                "INSERT INTO memory (category, value, created_at) VALUES ('topic', ?, ?)",
                (topic, now)
            )

        conn.commit()

    # ── Action Logs ─────────────────────────────────────

    def log_action(self, action: Dict):
        """Append action to log (keep last 500)."""
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO action_logs (action_type, action_data, success) VALUES (?, ?, ?)",
            (
                action.get("type", "unknown"),
                json.dumps(action),
                1 if action.get("success", True) else 0
            )
        )

        # Trim to last 500
        conn.execute(
            "DELETE FROM action_logs WHERE id NOT IN "
            "(SELECT id FROM action_logs ORDER BY id DESC LIMIT 500)"
        )
        conn.commit()

    def get_action_logs(self, limit: int = 50) -> List[Dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM action_logs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d.get("action_data"):
                try:
                    d["action_data"] = json.loads(d["action_data"])
                except:
                    pass
            result.append(d)
        return result

    # ── Algorithm Runs ──────────────────────────────────

    def log_algorithm_run(self, name: str, inputs: Dict = None, output: Dict = None,
                          gpa_score: float = None, duration_ms: int = None,
                          status: str = "success") -> int:
        conn = self._get_conn()
        cursor = conn.execute(
            "INSERT INTO algorithm_runs (algorithm_name, inputs, output, gpa_score, "
            "duration_ms, status) VALUES (?, ?, ?, ?, ?, ?)",
            (
                name,
                json.dumps(inputs) if inputs else None,
                json.dumps(output) if output else None,
                gpa_score, duration_ms, status
            )
        )
        conn.commit()
        return cursor.lastrowid

    def get_algorithm_runs(self, name: str = None, limit: int = 50) -> List[Dict]:
        conn = self._get_conn()
        if name:
            rows = conn.execute(
                "SELECT * FROM algorithm_runs WHERE algorithm_name = ? ORDER BY id DESC LIMIT ?",
                (name, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM algorithm_runs ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Storage Stats ───────────────────────────────────

    def get_storage_stats(self) -> Dict:
        """Get storage usage statistics."""
        conn = self._get_conn()
        conv_count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
        msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        memory_count = conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0]
        log_count = conn.execute("SELECT COUNT(*) FROM action_logs").fetchone()[0]
        algo_count = conn.execute("SELECT COUNT(*) FROM algorithm_runs").fetchone()[0]

        # DB file size
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

        return {
            "db_path": str(self.db_path),
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / 1024 / 1024, 2),
            "conversations": conv_count,
            "messages": msg_count,
            "memory_entries": memory_count,
            "action_logs": log_count,
            "algorithm_runs": algo_count,
        }

    # ── Cloud Sync ──────────────────────────────────────

    def get_unsynced_messages(self, limit: int = 50) -> List[Dict]:
        """Get messages not yet synced to Supabase."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT m.*, c.cloud_id as conv_cloud_id FROM messages m "
            "JOIN conversations c ON m.conversation_id = c.id "
            "WHERE m.cloud_synced = 0 ORDER BY m.id ASC LIMIT ?",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def mark_messages_synced(self, message_ids: List[int]):
        """Mark messages as synced to cloud."""
        if not message_ids:
            return
        conn = self._get_conn()
        placeholders = ",".join("?" * len(message_ids))
        conn.execute(
            f"UPDATE messages SET cloud_synced = 1 WHERE id IN ({placeholders})",
            message_ids
        )
        conn.commit()

    def set_cloud_id(self, conv_id: str, cloud_id: str):
        """Link local conversation to Supabase UUID."""
        conn = self._get_conn()
        conn.execute(
            "UPDATE conversations SET cloud_id = ?, synced_at = ? WHERE id = ?",
            (cloud_id, datetime.now().isoformat(), conv_id)
        )
        conn.commit()

    # ── Cleanup ─────────────────────────────────────────

    def clear_all(self):
        """Clear all data (keeps settings and connections)."""
        conn = self._get_conn()
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM conversations")
        conn.execute("DELETE FROM action_logs")
        conn.execute("DELETE FROM algorithm_runs")
        conn.execute("DELETE FROM memory")
        conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Migration from JSON ─────────────────────────────

    def migrate_from_json(self, json_storage):
        """
        Import data from old LocalStorage (JSON files).
        Call once during upgrade.
        """
        try:
            # Migrate conversations
            convs = json_storage.list_conversations()
            for conv in convs:
                self._get_conn().execute(
                    "INSERT OR IGNORE INTO conversations (id, title, message_count, created_at, updated_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (conv["id"], conv.get("title", "Chat"),
                     conv.get("message_count", 0),
                     conv.get("created_at", datetime.now().isoformat()),
                     conv.get("updated_at", datetime.now().isoformat()))
                )

                # Migrate messages
                messages = json_storage.get_messages(conv["id"], limit=9999)
                for msg in messages:
                    self._get_conn().execute(
                        "INSERT OR IGNORE INTO messages "
                        "(conversation_id, role, content, thinking, model, latency_ms, "
                        "tokens, actions, attachments, created_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            conv["id"], msg["role"], msg["content"],
                            msg.get("thinking"), msg.get("model"),
                            msg.get("latency_ms"), msg.get("tokens", 0),
                            json.dumps(msg.get("actions")) if msg.get("actions") else None,
                            json.dumps(msg.get("attachments")) if msg.get("attachments") else None,
                            msg.get("timestamp", datetime.now().isoformat())
                        )
                    )

            # Migrate memory
            memory = json_storage.get_memory("context")
            if memory:
                self.save_memory("context", memory)

            # Migrate settings
            settings = json_storage.get_all_settings()
            for k, v in settings.items():
                self.save_setting(k, v)

            # Migrate connections
            try:
                conns = json_storage.get_connections_raw()
                for pid, conn_data in conns.items():
                    self.save_connection(
                        pid,
                        url=conn_data.get("url"),
                        api_key=conn_data.get("api_key")
                    )
            except:
                pass

            self._get_conn().commit()
            print(f"✅ Migrated {len(convs)} conversations from JSON to SQLite")
            return True

        except Exception as e:
            print(f"❌ Migration error: {e}")
            traceback.print_exc()
            return False


# ============================================================
# Singleton
# ============================================================

_db_instance: Optional[DiveDatabase] = None


def get_database(db_path: str = None) -> DiveDatabase:
    """Get or create database singleton."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DiveDatabase(db_path)
    return _db_instance


def init_database(db_path: str = None) -> DiveDatabase:
    """Initialize database with custom path."""
    global _db_instance
    _db_instance = DiveDatabase(db_path)
    return _db_instance
