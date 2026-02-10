"""
Dive AI — Session Replay System
JSONL event recording, session replay, export/import.
"""
import os, json, time, hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional


class SessionRecorder:
    """
    Records all agent actions as JSONL events for replay and debugging.
    Each session is a separate JSONL file.
    """

    SESSIONS_DIR = os.path.expanduser("~/.dive-ai/sessions")

    def __init__(self, session_id: str = None):
        os.makedirs(self.SESSIONS_DIR, exist_ok=True)
        self.session_id = session_id or f"session-{int(time.time())}"
        self._events: List[Dict] = []
        self._start_time = time.time()
        self._file = os.path.join(self.SESSIONS_DIR, f"{self.session_id}.jsonl")
        self._metadata = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "events": 0,
        }

    # ── Recording ───────────────────────────────────────

    def record(self, event_type: str, data: Dict = None,
               tool_name: str = None, status: str = "ok") -> Dict:
        """Record a single event."""
        event = {
            "ts": time.time(),
            "dt": datetime.now().isoformat(),
            "seq": len(self._events),
            "type": event_type,
            "tool": tool_name,
            "status": status,
            "data": data or {},
            "elapsed_ms": int((time.time() - self._start_time) * 1000),
        }
        self._events.append(event)
        self._metadata["events"] = len(self._events)

        # Append to file
        with open(self._file, "a") as f:
            f.write(json.dumps(event, default=str) + "\n")

        return event

    def record_tool_call(self, tool_name: str, inputs: Dict,
                         output: Any = None, duration_ms: float = 0) -> Dict:
        """Record a tool/skill execution."""
        return self.record("tool_call", {
            "inputs": inputs,
            "output": str(output)[:500] if output else None,
            "duration_ms": duration_ms,
        }, tool_name=tool_name)

    def record_llm_call(self, model: str, prompt_tokens: int = 0,
                        completion_tokens: int = 0, duration_ms: float = 0) -> Dict:
        """Record an LLM API call."""
        return self.record("llm_call", {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "duration_ms": duration_ms,
        })

    def record_user_message(self, message: str) -> Dict:
        """Record user input."""
        return self.record("user_message", {
            "message": message[:1000],
            "length": len(message),
        })

    def record_agent_response(self, response: str, model: str = None) -> Dict:
        """Record agent response."""
        return self.record("agent_response", {
            "response": response[:1000],
            "length": len(response),
            "model": model,
        })

    def record_error(self, error: str, context: Dict = None) -> Dict:
        """Record an error."""
        return self.record("error", {
            "error": error, "context": context or {},
        }, status="error")

    # ── Replay ──────────────────────────────────────────

    @staticmethod
    def load_session(session_id: str) -> List[Dict]:
        """Load all events from a session file."""
        path = os.path.join(SessionRecorder.SESSIONS_DIR, f"{session_id}.jsonl")
        if not os.path.exists(path):
            return []
        events = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    try: events.append(json.loads(line))
                    except: pass
        return events

    @staticmethod
    def replay_summary(session_id: str) -> Dict:
        """Get a summary of a session for replay."""
        events = SessionRecorder.load_session(session_id)
        if not events:
            return {"error": "Session not found or empty"}

        tool_calls = [e for e in events if e["type"] == "tool_call"]
        llm_calls = [e for e in events if e["type"] == "llm_call"]
        errors = [e for e in events if e["status"] == "error"]
        messages = [e for e in events if e["type"] in ("user_message", "agent_response")]

        total_duration = events[-1]["elapsed_ms"] if events else 0
        tools_used = list(set(e.get("tool", "") for e in tool_calls if e.get("tool")))

        return {
            "session_id": session_id,
            "total_events": len(events),
            "duration_ms": total_duration,
            "duration_human": f"{total_duration / 1000:.1f}s",
            "tool_calls": len(tool_calls),
            "llm_calls": len(llm_calls),
            "messages": len(messages),
            "errors": len(errors),
            "tools_used": tools_used,
            "started_at": events[0]["dt"] if events else None,
            "ended_at": events[-1]["dt"] if events else None,
        }

    @staticmethod
    def list_sessions(last_n: int = 20) -> List[Dict]:
        """List available sessions."""
        sessions_dir = SessionRecorder.SESSIONS_DIR
        if not os.path.exists(sessions_dir):
            return []
        files = sorted([f for f in os.listdir(sessions_dir) if f.endswith(".jsonl")],
                       reverse=True)
        results = []
        for f in files[:last_n]:
            sid = f.replace(".jsonl", "")
            path = os.path.join(sessions_dir, f)
            stat = os.stat(path)
            results.append({
                "session_id": sid,
                "file": f,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        return results

    # ── Export/Import ───────────────────────────────────

    def export_session(self, output_path: str = None) -> str:
        """Export current session as a JSON file."""
        if not output_path:
            output_path = os.path.join(self.SESSIONS_DIR,
                                       f"{self.session_id}_export.json")
        export = {
            "metadata": self._metadata,
            "events": self._events,
            "summary": SessionRecorder.replay_summary(self.session_id),
        }
        with open(output_path, "w") as f:
            json.dump(export, f, indent=2, default=str)
        return output_path

    @staticmethod
    def import_session(json_path: str) -> Dict:
        """Import a session from a JSON export."""
        if not os.path.exists(json_path):
            return {"success": False, "error": "File not found"}
        with open(json_path) as f:
            data = json.load(f)
        session_id = data.get("metadata", {}).get("session_id", f"imported-{int(time.time())}")
        events = data.get("events", [])

        # Write as JSONL
        path = os.path.join(SessionRecorder.SESSIONS_DIR, f"{session_id}.jsonl")
        with open(path, "w") as f:
            for event in events:
                f.write(json.dumps(event, default=str) + "\n")

        return {"success": True, "session_id": session_id,
                "events": len(events), "path": path}

    # ── Finalize ────────────────────────────────────────

    def finalize(self) -> Dict:
        """Finalize the session and return summary."""
        self._metadata["ended_at"] = datetime.now().isoformat()
        self._metadata["duration_ms"] = int((time.time() - self._start_time) * 1000)
        # Write metadata
        meta_path = os.path.join(self.SESSIONS_DIR, f"{self.session_id}_meta.json")
        with open(meta_path, "w") as f:
            json.dump(self._metadata, f, indent=2)
        return self._metadata
