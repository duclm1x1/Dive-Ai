"""
Dive AI — Advanced Memory Architecture
5-file markdown memory + hybrid search + daily ephemeral logs.
Replaces basic MemoryManager with OpenClaw-parity memory system.
"""
import os, json, time, re, math, sqlite3, hashlib
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class DiveMemory:
    """
    Advanced memory system with 5 markdown identity files,
    daily ephemeral logs, and hybrid BM25+semantic search.
    """

    DEFAULT_DIR = os.path.expanduser("~/.dive-ai/memory")

    # Core identity files
    FILES = {
        "user": "USER.md",
        "identity": "IDENTITY.md",
        "soul": "SOUL.md",
        "heartbeat": "HEARTBEAT.md",
        "memory": "MEMORY.md",
    }

    DEFAULTS = {
        "user": """# User Profile
## Preferences
- Language: auto-detect
- Timezone: auto-detect
- Communication style: professional

## Work Patterns
- (Dive AI learns your patterns over time)

## Known Facts
- (Facts extracted from conversations appear here)
""",
        "identity": """# Dive AI Identity
## Name
Dive AI

## Role
Personal AI assistant with full system access

## Emoji
🤿

## Relationship
Trusted coding partner and productivity assistant

## Version
V29.7 — Antigravity Edition
""",
        "soul": """# Dive AI Soul
## Personality
- Helpful, concise, and technically precise
- Proactive but not intrusive
- Honest about limitations and uncertainties

## Communication Rules
- Default language: match user's language
- Humor: light, contextual
- Code style: clean, well-documented
- Error handling: explain root cause, not just fix

## Tone
Professional yet friendly. Like a senior engineer pair-programming.

## Core Values
- Accuracy over speed
- User privacy first
- Transparent reasoning
- Continuous improvement
""",
        "heartbeat": """# Heartbeat Checklist
## Periodic Monitors
- [ ] Check disk space (warn if < 10%)
- [ ] Check CPU usage (warn if > 90% sustained)
- [ ] Check memory usage (warn if > 85%)
- [ ] Review pending tasks
- [ ] Check for system updates

## Proactive Actions
- [ ] Summarize daily activity
- [ ] Remind about incomplete projects
- [ ] Suggest optimizations based on patterns
""",
        "memory": """# Long-Term Memory
## Key Decisions
- (Important decisions are recorded here)

## Project Context
- (Active project information appears here)

## Learned Preferences
- (User preferences discovered over time)
""",
    }

    def __init__(self, memory_dir: str = None):
        self.dir = memory_dir or self.DEFAULT_DIR
        os.makedirs(self.dir, exist_ok=True)
        os.makedirs(os.path.join(self.dir, "daily"), exist_ok=True)
        self._db_path = os.path.join(self.dir, "search_index.db")
        self._init_files()
        self._init_search_db()

    # ── File Management ─────────────────────────────────

    def _init_files(self):
        """Create default identity files if they don't exist."""
        for key, filename in self.FILES.items():
            path = os.path.join(self.dir, filename)
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.DEFAULTS.get(key, f"# {key.title()}\n"))

    def read(self, key: str) -> str:
        """Read an identity file."""
        filename = self.FILES.get(key)
        if not filename:
            return ""
        path = os.path.join(self.dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def write(self, key: str, content: str):
        """Write to an identity file."""
        filename = self.FILES.get(key)
        if not filename:
            return
        path = os.path.join(self.dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self._index_document(key, content)

    def append(self, key: str, text: str):
        """Append to an identity file."""
        current = self.read(key)
        self.write(key, current.rstrip() + "\n" + text + "\n")

    def update_section(self, key: str, section: str, content: str):
        """Update a specific section within an identity file."""
        full = self.read(key)
        pattern = rf"(## {re.escape(section)}\n)(.*?)(\n## |\Z)"
        replacement = rf"\g<1>{content}\n\g<3>"
        updated = re.sub(pattern, replacement, full, flags=re.DOTALL)
        if updated == full:
            # Section not found, append
            updated = full.rstrip() + f"\n\n## {section}\n{content}\n"
        self.write(key, updated)

    def get_all(self) -> Dict[str, str]:
        """Read all identity files."""
        return {key: self.read(key) for key in self.FILES}

    # ── Daily Ephemeral Logs ────────────────────────────

    def _daily_path(self, d: date = None) -> str:
        d = d or date.today()
        return os.path.join(self.dir, "daily", f"{d.isoformat()}.md")

    def log_daily(self, entry: str, category: str = "activity"):
        """Append an entry to today's daily log."""
        path = self._daily_path()
        now = datetime.now().strftime("%H:%M:%S")
        is_new = not os.path.exists(path)
        with open(path, "a", encoding="utf-8") as f:
            if is_new:
                f.write(f"# Daily Log — {date.today().isoformat()}\n\n")
            f.write(f"- **{now}** [{category}] {entry}\n")
        self._index_document(f"daily-{date.today().isoformat()}", entry)

    def read_daily(self, d: date = None) -> str:
        """Read a daily log."""
        path = self._daily_path(d)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def list_daily_logs(self, last_n: int = 30) -> List[str]:
        """List available daily log dates."""
        daily_dir = os.path.join(self.dir, "daily")
        if not os.path.exists(daily_dir):
            return []
        logs = sorted([f.replace(".md", "") for f in os.listdir(daily_dir)
                       if f.endswith(".md")], reverse=True)
        return logs[:last_n]

    # ── Fact Extraction & Learning ──────────────────────

    def add_fact(self, fact: str, category: str = "general"):
        """Add a learned fact to MEMORY.md."""
        existing = self.read("memory")
        if fact in existing:
            return  # No duplicates
        section = "Learned Preferences" if category == "preference" else \
                  "Key Decisions" if category == "decision" else \
                  "Project Context" if category == "project" else "Key Decisions"
        self.update_section("memory", section,
                            existing.split(f"## {section}")[-1].strip() + f"\n- {fact}")
        self.log_daily(f"Learned: {fact}", "learning")

    def add_user_fact(self, fact: str):
        """Add a fact about the user to USER.md."""
        self.update_section("user", "Known Facts",
                            self.read("user").split("## Known Facts")[-1].strip() + f"\n- {fact}")

    def set_preference(self, key: str, value: str):
        """Set a user preference."""
        user_content = self.read("user")
        # Check if preference line exists
        pattern = rf"- {re.escape(key)}: .+"
        if re.search(pattern, user_content):
            updated = re.sub(pattern, f"- {key}: {value}", user_content)
        else:
            updated = user_content.rstrip() + f"\n- {key}: {value}\n"
        self.write("user", updated)

    # ── Hybrid Search (BM25 + keyword) ──────────────────

    def _init_search_db(self):
        """Initialize SQLite FTS5 for hybrid search."""
        conn = sqlite3.connect(self._db_path)
        conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
                        USING fts5(doc_id, content, tokenize='porter')""")
        conn.execute("""CREATE TABLE IF NOT EXISTS memory_docs (
                        doc_id TEXT PRIMARY KEY, content TEXT, updated_at TEXT)""")
        conn.commit()
        conn.close()
        # Index existing files
        for key in self.FILES:
            content = self.read(key)
            if content:
                self._index_document(key, content)

    def _index_document(self, doc_id: str, content: str):
        """Index a document for search."""
        conn = sqlite3.connect(self._db_path)
        try:
            conn.execute("DELETE FROM memory_fts WHERE doc_id = ?", (doc_id,))
            conn.execute("INSERT INTO memory_fts (doc_id, content) VALUES (?, ?)",
                         (doc_id, content))
            conn.execute("""INSERT OR REPLACE INTO memory_docs (doc_id, content, updated_at)
                            VALUES (?, ?, ?)""", (doc_id, content, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Hybrid search across all memory files and daily logs."""
        results = []
        conn = sqlite3.connect(self._db_path)
        try:
            # FTS5 BM25 search
            cursor = conn.execute("""
                SELECT doc_id, snippet(memory_fts, 1, '>>>', '<<<', '...', 50),
                       rank FROM memory_fts
                WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?
            """, (query, limit))
            for row in cursor:
                results.append({
                    "doc_id": row[0], "snippet": row[1],
                    "score": -row[2],  # FTS5 rank is negative
                    "source": "bm25",
                })
        except Exception:
            pass
        finally:
            conn.close()

        # Keyword fallback search
        query_lower = query.lower()
        for key in self.FILES:
            content = self.read(key)
            if query_lower in content.lower():
                lines = content.split("\n")
                matching = [l for l in lines if query_lower in l.lower()]
                if matching and not any(r["doc_id"] == key for r in results):
                    results.append({
                        "doc_id": key, "snippet": matching[0][:200],
                        "score": 0.5, "source": "keyword",
                    })

        return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]

    # ── System Prompt Builder ───────────────────────────

    def build_system_context(self) -> str:
        """Build dynamic system prompt from all identity files."""
        parts = []
        soul = self.read("soul")
        if soul:
            parts.append(soul.strip())

        identity = self.read("identity")
        if identity:
            parts.append(identity.strip())

        user = self.read("user")
        if user:
            parts.append(user.strip())

        heartbeat = self.read("heartbeat")
        if heartbeat:
            parts.append(heartbeat.strip())

        return "\n\n---\n\n".join(parts)

    # ── Status & Stats ─────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Get memory system status."""
        files = {}
        for key, filename in self.FILES.items():
            path = os.path.join(self.dir, filename)
            if os.path.exists(path):
                stat = os.stat(path)
                files[key] = {
                    "file": filename, "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
        daily_logs = self.list_daily_logs()
        return {
            "memory_dir": self.dir,
            "identity_files": files,
            "daily_logs_count": len(daily_logs),
            "latest_daily": daily_logs[0] if daily_logs else None,
            "search_index": os.path.exists(self._db_path),
        }
