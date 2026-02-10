"""
Dive AI Agent Protocol — Inter-agent communication.
Dive-to-Dive, Dive-to-OpenClaw, or any HTTP-based agent.
"""
import json
import time
import urllib.request
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AgentCapability:
    skill_name: str
    description: str
    input_schema: Dict = field(default_factory=dict)


@dataclass
class AgentInfo:
    agent_id: str
    name: str
    url: str  # Base URL for the agent's API
    capabilities: List[AgentCapability] = field(default_factory=list)
    last_seen: float = 0.0
    status: str = "unknown"


@dataclass
class AgentTask:
    task_id: str
    from_agent: str
    skill_name: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"


@dataclass
class AgentResult:
    task_id: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class DiveAgentProtocol:
    """
    Inter-agent communication protocol.
    Register this Dive AI instance, discover peers, delegate tasks.
    """

    def __init__(self, agent_id: str = "dive-ai-primary", name: str = "Dive AI", port: int = 1879):
        self.agent_id = agent_id
        self.name = name
        self.port = port
        self._peers: Dict[str, AgentInfo] = {}
        self._capabilities: List[AgentCapability] = []
        self._task_queue: List[AgentTask] = []
        self._results: Dict[str, AgentResult] = {}

    # ── Self-Registration ──────────────────────────────────

    def register_capability(self, skill_name: str, description: str, input_schema: Dict = None):
        self._capabilities.append(AgentCapability(skill_name, description, input_schema or {}))

    def get_info(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": [{"skill": c.skill_name, "description": c.description} for c in self._capabilities],
            "status": "online",
            "last_seen": time.time(),
        }

    # ── Peer Discovery ─────────────────────────────────────

    def register_peer(self, agent_id: str, name: str, url: str, capabilities: List[Dict] = None):
        caps = [AgentCapability(c.get("skill", ""), c.get("description", "")) for c in (capabilities or [])]
        self._peers[agent_id] = AgentInfo(agent_id, name, url, caps, time.time(), "online")

    def discover_peers(self) -> List[Dict]:
        return [{"agent_id": p.agent_id, "name": p.name, "url": p.url,
                 "capabilities": len(p.capabilities), "status": p.status}
                for p in self._peers.values()]

    def ping_peer(self, agent_id: str) -> Dict:
        peer = self._peers.get(agent_id)
        if not peer:
            return {"error": f"Unknown peer: {agent_id}"}
        try:
            url = f"{peer.url}/debug/ping"
            req = urllib.request.Request(url, headers={"User-Agent": "DiveAI-Agent"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
            peer.last_seen = time.time()
            peer.status = "online"
            return {"agent_id": agent_id, "status": "online", "response": data}
        except Exception as e:
            peer.status = "offline"
            return {"agent_id": agent_id, "status": "offline", "error": str(e)}

    # ── Task Delegation ────────────────────────────────────

    def delegate_task(self, agent_id: str, skill_name: str, inputs: Dict) -> AgentResult:
        peer = self._peers.get(agent_id)
        if not peer:
            return AgentResult("", False, error=f"Unknown peer: {agent_id}")
        
        task_id = f"task-{int(time.time())}"
        try:
            url = f"{peer.url}/skills/{skill_name}/execute"
            data = json.dumps(inputs).encode()
            req = urllib.request.Request(url, data=data,
                                         headers={"Content-Type": "application/json", "X-Agent-ID": self.agent_id})
            start = time.time()
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            duration = (time.time() - start) * 1000
            
            agent_result = AgentResult(task_id, result.get("success", True), result, duration_ms=duration)
            self._results[task_id] = agent_result
            return agent_result
        except Exception as e:
            return AgentResult(task_id, False, error=str(e))

    # ── Receive Tasks ──────────────────────────────────────

    def receive_task(self, task_data: Dict) -> Dict:
        task = AgentTask(
            task_id=task_data.get("task_id", f"recv-{int(time.time())}"),
            from_agent=task_data.get("from_agent", "unknown"),
            skill_name=task_data.get("skill_name", ""),
            inputs=task_data.get("inputs", {}),
        )
        self._task_queue.append(task)
        return {"queued": True, "task_id": task.task_id, "position": len(self._task_queue)}

    def get_status(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": len(self._capabilities),
            "peers": len(self._peers),
            "queued_tasks": len(self._task_queue),
            "completed_tasks": len(self._results),
        }
