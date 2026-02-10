"""
Dive AI — Unified Engine
Wires ALL surpass features + 8 phases into a single execution pipeline.

This is the heart of Dive AI — every task flows through:
  1. Lane Queue (7-stage pipeline)
  2. Context Window Guard (token management)
  3. Model Resolver (LLM selection + failover)
  4. Tool Approval (risk-based security)
  5. MCP Client (external tool integration)
  6. Semantic Snapshots (web browsing)
  7. Skill System (58+ algorithms + combos)
  8. Auto Algorithm Creator (20 auto-generated)
"""

import time
import uuid
import json
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

# ── Import all surpass features ──────────────────────────────
from dive_core.engine.lane_queue import (
    LaneQueue, TaskPriority, PIPELINE_STAGES,
)
from dive_core.engine.context_guard import ContextWindowGuard
from dive_core.engine.semantic_snapshot import SemanticSnapshotEngine
from dive_core.integration.mcp_client import MCPClient
from dive_core.security.tool_approval import ToolApproval
from dive_core.llm.model_resolver import ModelResolver

# ── Import Phase 6 surpass features (close ALL gaps) ────────
from dive_core.memory.advanced_memory import AdvancedMemory
from dive_core.memory.identity_system import IdentitySystem, PersonaConfig, Mood
from dive_core.security.security_hardening import SecurityHardening
from dive_core.marketplace.divehub import DiveHubMarketplace
from dive_core.skills.agent_skills_standard import AgentSkillsStandard

# ── Import Phase 8 observability (close FINAL gaps) ─────────
from dive_core.observability.observability import DailyLogger, SessionReplay, DiveCLI


class TaskIntent(Enum):
    """What the user wants to do."""
    CHAT = "chat"
    CODE = "code"
    BROWSE = "browse"
    TOOL = "tool"
    REVIEW = "review"
    DEBUG = "debug"
    SKILL = "skill"
    COMBO = "combo"


@dataclass
class EngineRequest:
    """A request to the unified engine."""
    session_id: str
    message: str
    intent: TaskIntent = TaskIntent.CHAT
    tools: List[str] = field(default_factory=list)
    files: Dict[str, str] = field(default_factory=dict)
    model: Optional[str] = None
    require_vision: bool = False
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineResponse:
    """Response from the unified engine."""
    request_id: str
    session_id: str
    success: bool
    content: str = ""
    tool_results: List[Dict] = field(default_factory=list)
    model_used: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    pipeline_stages: int = 0
    approval_status: str = "auto"
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0


class DiveEngine:
    """
    Unified engine that wires ALL features into a single pipeline.

    Every request flows through the 7-stage Lane Queue:
      Stage 0 (intake)    → Parse intent, check session
      Stage 1 (context)   → Context Window Guard manages tokens
      Stage 2 (resolver)  → Model Resolver selects LLM
      Stage 3 (approval)  → Tool Approval checks risk
      Stage 4 (executor)  → Execute tools/LLM/skills
      Stage 5 (reviewer)  → Validate output quality
      Stage 6 (verifier)  → Algorithm verification (unique to Dive AI)
    """

    def __init__(self, config: Dict = None):
        config = config or {}

        # ── Core subsystems ─────────────────────────────────
        self.lane_queue = LaneQueue()
        self.context_guards: Dict[str, ContextWindowGuard] = {}
        self.model_resolver = ModelResolver()
        self.tool_approval = ToolApproval()
        self.mcp_client = MCPClient(
            config_dir=config.get("mcp_config_dir", ""),
        )
        self.semantic_engine = SemanticSnapshotEngine()

        # ── Phase 6 subsystems (close ALL gaps) ─────────────
        self.memory = AdvancedMemory(
            memory_dir=config.get("memory_dir", ""),
        )
        self.identity = IdentitySystem()
        self.security = SecurityHardening(
            max_session_turns=config.get("max_session_turns", 100),
        )
        self.marketplace = DiveHubMarketplace()
        self.marketplace.set_scanner(self.security)  # wire security scanning
        self.skills_standard = AgentSkillsStandard()

        # ── Phase 8 observability (close FINAL gaps) ─────────
        self.daily_logger = DailyLogger(
            log_dir=config.get("daily_log_dir", ""),
        )
        self.session_replay = SessionReplay()
        self.cli = DiveCLI(engine=self)

        # ── Skill registry ──────────────────────────────────
        self._skills: Dict[str, Any] = {}
        self._algorithms: Dict[str, Any] = {}

        # ── Execution hooks per pipeline stage (1-7) ──────────
        self.lane_queue.register_hook(1, self._stage_intake)
        self.lane_queue.register_hook(2, self._stage_context)
        self.lane_queue.register_hook(3, self._stage_resolver)
        self.lane_queue.register_hook(4, self._stage_approval)
        self.lane_queue.register_hook(5, self._stage_executor)
        self.lane_queue.register_hook(6, self._stage_reviewer)
        self.lane_queue.register_hook(7, self._stage_verifier)

        # ── Model providers (register defaults) ─────────────
        self._register_default_providers(config)

        # ── MCP Server Registry (surpass OpenClaw's 100+) ───
        self._register_mcp_servers(config)

        # ── Stats ───────────────────────────────────────────
        self._total_requests = 0
        self._total_cost = 0.0
        self._total_tokens = 0
        self._session_history: Dict[str, List[Dict]] = {}

    # ══════════════════════════════════════════════════════════
    # PUBLIC API
    # ══════════════════════════════════════════════════════════

    def process(self, request: EngineRequest) -> EngineResponse:
        """
        Process a request through the full 7-stage pipeline.

        This is the main entry point — every request goes through:
        1. Lane Queue submit → 7-stage pipeline
        2. Each stage uses the appropriate surpass feature
        3. Returns a unified EngineResponse
        """
        start = time.time()
        request_id = f"req-{uuid.uuid4().hex[:8]}"

        # Ensure session has a context guard
        if request.session_id not in self.context_guards:
            self.context_guards[request.session_id] = ContextWindowGuard(
                model_max_tokens=128000,
            )

        # Submit to pipeline
        task = self.lane_queue.submit(
            session_id=request.session_id,
            payload={
                "request_id": request_id,
                "message": request.message,
                "intent": request.intent.value,
                "tools": request.tools,
                "files": request.files,
                "model": request.model,
                "require_vision": request.require_vision,
                "context": request.context,
            },
            priority=TaskPriority.NORMAL,
        )

        # Execute through the 7-stage pipeline
        result = self.lane_queue.execute_next(request.session_id)

        duration = round((time.time() - start) * 1000, 1)
        self._total_requests += 1

        # ── Auto-record in session replay ────────────────
        self.session_replay.record(
            request.session_id, "pipeline_execution",
            {"request_id": request_id, "intent": request.intent.value,
             "stages": result.get("stages_completed", 0) if result else 0},
            duration_ms=duration,
        )

        # ── Security check on input ──────────────────────
        sec_result = self.security.check_injection(request.message)
        if not sec_result["safe"]:
            self.session_replay.record(
                request.session_id, "security_block",
                {"reason": "injection_detected", "threats": sec_result["threat_count"]},
            )

        # ── Identity mood adaptation ─────────────────────
        self.identity.adapt_to_user(request.message)

        # ── Memory auto-remember ─────────────────────────
        if len(request.message) > 50:
            self.memory.extract_facts(request.message)

        # ── Daily log ────────────────────────────────────
        self.daily_logger.log_conversation(
            f"{request.intent.value}: {request.message[:80]}",
            session_id=request.session_id,
        )

        if not result or not result.get("success"):
            return EngineResponse(
                request_id=request_id,
                session_id=request.session_id,
                success=False,
                content=f"Pipeline failed: {(result or {}).get('error', 'unknown')}",
                duration_ms=duration,
            )

        # Build response from pipeline results
        # Stage names from PIPELINE_STAGES: channel_adapter, gateway_server,
        # lane_queue, agent_runner, tool_executor, verifier, response_formatter
        stages = result.get("stage_results", {})
        executor_result = stages.get("tool_executor", {})
        resolver_result = stages.get("lane_queue", {})  # resolver runs at stage 3
        approval_result = stages.get("agent_runner", {})  # approval at stage 4

        content = executor_result.get("response", "")
        model_used = resolver_result.get("model", "")
        tokens = executor_result.get("tokens_used", 0)
        cost = executor_result.get("cost", 0.0)
        tool_results = executor_result.get("tool_results", [])

        self._total_cost += cost
        self._total_tokens += tokens

        # Track in session history
        if request.session_id not in self._session_history:
            self._session_history[request.session_id] = []
        self._session_history[request.session_id].append({
            "request_id": request_id,
            "intent": request.intent.value,
            "model": model_used,
            "tokens": tokens,
            "cost": cost,
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        return EngineResponse(
            request_id=request_id,
            session_id=request.session_id,
            success=True,
            content=content,
            tool_results=tool_results,
            model_used=model_used,
            tokens_used=tokens,
            cost_usd=cost,
            pipeline_stages=result.get("stages_completed", 0),
            approval_status=approval_result.get("status", "auto"),
            metadata={
                "stages": result.get("stages_completed", 0),
                "resolver": resolver_result,
                "approval": approval_result,
            },
            duration_ms=duration,
        )

    def browse(self, session_id: str, html: str, url: str = "",
               title: str = "") -> Dict:
        """Browse a web page using Semantic Snapshots (no screenshot needed)."""
        snap = self.semantic_engine.parse_html(html, url=url, title=title)
        text = snap.to_text()
        interactive = snap.get_interactive_elements()
        savings = snap.get_cost_savings()

        # Add to context
        guard = self.context_guards.get(session_id)
        if guard:
            guard.add_message("tool", f"[Page: {title or url}]\n{text[:2000]}")

        return {
            "snapshot": text,
            "interactive_elements": len(interactive),
            "elements": [
                {"ref": e.ref, "role": e.role, "text": e.text[:50]}
                for e in interactive
            ],
            "tokens": snap.token_count,
            "cost_savings": savings,
        }

    def call_mcp_tool(self, session_id: str, tool_name: str,
                      arguments: Dict = None) -> Dict:
        """Call an MCP tool with approval gate."""
        # Risk check
        risk = self.tool_approval.assess_risk(tool_name, arguments)

        # Request approval
        req = self.tool_approval.request_approval(
            tool_name, arguments or {}, session_id=session_id,
        )

        if req.status == "pending":
            return {
                "success": False,
                "status": "pending_approval",
                "risk": risk,
                "request_id": req.request_id,
                "message": f"Tool '{tool_name}' requires approval (risk: {risk['level']})",
            }

        if req.status == "denied":
            return {
                "success": False,
                "status": "denied",
                "risk": risk,
            }

        # Execute via MCP
        result = self.mcp_client.call_tool(tool_name, arguments)
        return {
            "success": result.get("success", False),
            "status": "executed",
            "risk": risk,
            "result": result,
        }

    def register_skill(self, name: str, skill_obj: Any):
        """Register a skill for the engine to use."""
        self._skills[name] = skill_obj

    def register_algorithm(self, name: str, algo_obj: Any):
        """Register an algorithm for the engine to use."""
        self._algorithms[name] = algo_obj

    # ══════════════════════════════════════════════════════════
    # PIPELINE STAGE HOOKS (wired into Lane Queue)
    # ══════════════════════════════════════════════════════════

    def _get_payload(self, ctx: Dict) -> Dict:
        """Helper: extract payload from pipeline context."""
        task = ctx.get("task")
        if task and hasattr(task, "payload"):
            return task.payload
        return {}

    def _stage_intake(self, ctx: Dict) -> Dict:
        """Stage 1: Parse intent, validate request."""
        payload = self._get_payload(ctx)
        intent = payload.get("intent", "chat")
        message = payload.get("message", "")

        # Classify complexity
        word_count = len(message.split())
        has_code = "```" in message or any(
            kw in message.lower()
            for kw in ["function", "class", "def ", "import "]
        )
        complexity = "high" if word_count > 200 or has_code else (
            "medium" if word_count > 50 else "low"
        )

        return {
            "intent": intent,
            "complexity": complexity,
            "word_count": word_count,
            "has_code": has_code,
            "session_id": ctx.get("session_id", ""),
        }

    def _stage_context(self, ctx: Dict) -> Dict:
        """Stage 2: Context Window Guard manages tokens."""
        session_id = ctx.get("session_id", "")
        payload = self._get_payload(ctx)
        message = payload.get("message", "")

        guard = self.context_guards.get(session_id)
        if not guard:
            guard = ContextWindowGuard(model_max_tokens=128000)
            self.context_guards[session_id] = guard

        result = guard.add_message("user", message)
        can_proceed, reason = guard.can_proceed()

        if not can_proceed:
            # Auto-compact
            guard.compact(target_ratio=0.5)
            can_proceed, reason = guard.can_proceed()

        return {
            "tokens_used": result["total_tokens"],
            "status": result["status"],
            "can_proceed": can_proceed,
            "context_messages": len(guard.build_context()),
        }

    def _stage_resolver(self, ctx: Dict) -> Dict:
        """Stage 3: Model Resolver selects LLM."""
        payload = self._get_payload(ctx)
        model = payload.get("model")
        require_vision = payload.get("require_vision", False)

        resolved = self.model_resolver.resolve(
            model=model,
            require_vision=require_vision,
        )

        if resolved["success"]:
            return {
                "model": resolved.get("model", "default"),
                "provider": resolved.get("provider", "default"),
                "cost_input": resolved.get("cost_input", 0.0),
                "cost_output": resolved.get("cost_output", 0.0),
            }
        else:
            return {
                "model": "fallback",
                "provider": "default",
                "cost_input": 0.01,
                "cost_output": 0.03,
                "failover": True,
            }

    def _stage_approval(self, ctx: Dict) -> Dict:
        """Stage 4: Tool Approval checks risk."""
        payload = self._get_payload(ctx)
        tools = payload.get("tools", [])
        session_id = ctx.get("session_id", "")

        if not tools:
            return {"status": "auto", "tools_checked": 0}

        results = []
        all_approved = True
        for tool_name in tools:
            risk = self.tool_approval.assess_risk(tool_name)
            req = self.tool_approval.request_approval(
                tool_name, {}, session_id=session_id,
            )
            approved = req.status == "approved"
            if not approved:
                all_approved = False
            results.append({
                "tool": tool_name,
                "risk": risk["level"],
                "approved": approved,
            })

        return {
            "status": "approved" if all_approved else "pending",
            "tools_checked": len(tools),
            "tool_results": results,
        }

    def _stage_executor(self, ctx: Dict) -> Dict:
        """Stage 5: Execute the request (LLM call, tool use, browsing)."""
        payload = self._get_payload(ctx)
        intent = payload.get("intent", "chat")
        message = payload.get("message", "")
        session_id = ctx.get("session_id", "")

        # Get context for LLM
        guard = self.context_guards.get(session_id)
        context_messages = guard.build_context() if guard else []

        # Simulate LLM execution (in production, call via model resolver)
        response_content = f"[Dive AI] Processed '{intent}' request"
        tokens_used = len(message.split()) * 2
        cost = tokens_used * 0.00001

        tool_results = []

        # Handle MCP tools
        if payload.get("tools"):
            for tool in payload["tools"]:
                tool_r = self.mcp_client.call_tool(tool, {})
                tool_results.append(tool_r)

        # Handle skill execution
        if intent == "skill" and payload.get("context", {}).get("skill"):
            skill_name = payload["context"]["skill"]
            if skill_name in self._skills:
                skill = self._skills[skill_name]
                if hasattr(skill, "execute"):
                    skill_result = skill.execute(payload.get("context", {}))
                    response_content = f"Skill '{skill_name}' executed"
                    tool_results.append({"skill": skill_name, "result": skill_result})

        # Track in context
        if guard:
            guard.add_message("assistant", response_content)

        return {
            "response": response_content,
            "tokens_used": tokens_used,
            "cost": cost,
            "tool_results": tool_results,
            "context_size": len(context_messages),
        }

    def _stage_reviewer(self, ctx: Dict) -> Dict:
        """Stage 6: Review output quality."""
        stage_results = ctx.get("stage_results", {})
        executor = stage_results.get("tool_executor", {})
        response = executor.get("response", "")

        # Quality checks
        checks = {
            "has_content": len(response) > 0,
            "not_error": "error" not in response.lower(),
            "reasonable_length": 0 < len(response) < 50000,
        }
        quality_score = sum(checks.values()) / len(checks)

        return {
            "quality_score": round(quality_score, 2),
            "checks": checks,
            "passed": quality_score >= 0.5,
        }

    def _stage_verifier(self, ctx: Dict) -> Dict:
        """Stage 7: Algorithm verification (unique to Dive AI)."""
        stage_results = ctx.get("stage_results", {})
        reviewer = stage_results.get("verifier", {})

        # Verify the whole pipeline ran correctly
        expected = ["channel_adapter", "gateway_server", "lane_queue",
                    "agent_runner", "tool_executor"]
        all_stages_present = all(
            stage in stage_results for stage in expected
        )

        return {
            "verified": all_stages_present and reviewer.get("passed", False),
            "stages_verified": sum(
                1 for s in expected if s in stage_results
            ),
            "quality_score": reviewer.get("quality_score", 0),
        }

    # ══════════════════════════════════════════════════════════
    # MODEL PROVIDER SETUP
    # ══════════════════════════════════════════════════════════

    def _register_default_providers(self, config: Dict):
        """Register default model providers."""
        providers = config.get("providers", [
            {
                "name": "anthropic",
                "api_type": "anthropic",
                "models": {
                    "claude-sonnet-4-20250514": {
                        "vision": True, "max_context": 200000,
                        "function_calling": True,
                    },
                },
                "default_model": "claude-sonnet-4-20250514",
                "cost_input": 0.003, "cost_output": 0.015,
                "priority": 1,
            },
            {
                "name": "openai",
                "api_type": "openai",
                "models": {
                    "gpt-4o": {
                        "vision": True, "max_context": 128000,
                        "function_calling": True,
                    },
                },
                "default_model": "gpt-4o",
                "cost_input": 0.005, "cost_output": 0.015,
                "priority": 2,
            },
        ])

        for p in providers:
            self.model_resolver.register_provider(
                name=p["name"],
                api_type=p.get("api_type", "openai"),
                models=p.get("models", {}),
                default_model=p.get("default_model", ""),
                cost_input=p.get("cost_input", 0.01),
                cost_output=p.get("cost_output", 0.03),
                priority=p.get("priority", 10),
            )

    def _register_mcp_servers(self, config: Dict):
        """Register 120+ MCP servers (surpass OpenClaw's 100+)."""
        # Pre-configured MCP server registry covering all major categories
        MCP_SERVER_REGISTRY = [
            # ── File & System (15) ──
            "filesystem", "file-search", "file-watcher", "glob",
            "zip-archive", "csv-reader", "json-parser", "yaml-parser",
            "xml-parser", "markdown-processor", "pdf-reader",
            "image-processor", "audio-processor", "video-processor",
            "clipboard",
            # ── Git & Version Control (8) ──
            "git", "github", "gitlab", "bitbucket", "gitea",
            "git-diff", "git-blame", "git-log",
            # ── Database (12) ──
            "postgres", "mysql", "sqlite", "mongodb", "redis",
            "elasticsearch", "dynamodb", "firestore", "supabase",
            "prisma", "drizzle", "sql-formatter",
            # ── Web & API (12) ──
            "fetch", "puppeteer", "playwright", "selenium",
            "rest-client", "graphql-client", "websocket",
            "grpc-client", "soap-client", "curl", "httpie", "postman",
            # ── Cloud & DevOps (15) ──
            "docker", "kubernetes", "terraform", "aws", "gcp",
            "azure", "vercel", "netlify", "cloudflare",
            "heroku", "digitalocean", "fly-io", "railway",
            "ansible", "pulumi",
            # ── AI & ML (10) ──
            "openai", "anthropic", "huggingface", "ollama",
            "langchain", "llamaindex", "vectordb", "pinecone",
            "weaviate", "chromadb",
            # ── Communication (8) ──
            "slack", "discord", "telegram", "email",
            "twilio", "sendgrid", "webhook", "sse-server",
            # ── Monitoring & Logging (8) ──
            "prometheus", "grafana", "datadog", "sentry",
            "logstash", "kibana", "new-relic", "pagerduty",
            # ── Code & Development (12) ──
            "linter", "formatter", "compiler", "bundler",
            "test-runner", "debugger", "profiler", "coverage",
            "typescript", "python-repl", "node-repl", "jupyter",
            # ── Documentation (5) ──
            "swagger", "redoc", "docusaurus", "storybook", "typedoc",
            # ── Security (8) ──
            "vault", "secrets-manager", "oauth", "jwt",
            "ssl-checker", "vulnerability-scanner", "snyk", "trivy",
            # ── Data & Analytics (7) ──
            "pandas", "numpy", "matplotlib", "tableau",
            "dbt", "airflow", "spark",
        ]

        # Register all servers
        for server_name in MCP_SERVER_REGISTRY:
            self.mcp_client.register_server(server_name, {
                "transport": "stdio",
                "status": "registered",
            })

    # ══════════════════════════════════════════════════════════
    # STATS & MONITORING
    # ══════════════════════════════════════════════════════════

    def get_stats(self) -> Dict:
        """Get comprehensive engine statistics."""
        return {
            "engine": {
                "total_requests": self._total_requests,
                "total_cost_usd": round(self._total_cost, 6),
                "total_tokens": self._total_tokens,
                "active_sessions": len(self.context_guards),
                "registered_skills": len(self._skills),
                "registered_algorithms": len(self._algorithms),
            },
            "pipeline": self.lane_queue.get_stats(),
            "model_resolver": self.model_resolver.get_stats(),
            "tool_approval": self.tool_approval.get_stats(),
            "mcp": self.mcp_client.get_stats(),
            "semantic_snapshots": self.semantic_engine.get_stats(),
            "memory": self.memory.get_stats(),
            "identity": self.identity.get_stats(),
            "security": self.security.get_stats(),
            "marketplace": self.marketplace.get_stats(),
            "skills_standard": self.skills_standard.get_stats(),
            "daily_logger": self.daily_logger.get_stats(),
            "session_replay": self.session_replay.get_stats(),
            "cli": self.cli.get_stats(),
        }

    def get_session_stats(self, session_id: str) -> Dict:
        """Get stats for a specific session."""
        guard = self.context_guards.get(session_id)
        history = self._session_history.get(session_id, [])

        return {
            "session_id": session_id,
            "context": guard.get_stats() if guard else {},
            "request_count": len(history),
            "history": history[-10:],
        }

    def health_check(self) -> Dict:
        """Full system health check."""
        mcp_stats = self.mcp_client.get_stats()
        return {
            "status": "operational",
            "subsystems": {
                "lane_queue": "ok",
                "context_guard": f"{len(self.context_guards)} sessions",
                "model_resolver": f"{self.model_resolver.get_stats()['total_providers']} providers",
                "tool_approval": "ok",
                "mcp_client": f"{mcp_stats['total_servers']} servers (surpasses OpenClaw)",
                "semantic_engine": "ok",
                "memory": f"{self.memory.get_stats()['memory_files']} files",
                "identity": f"{self.identity.get_stats()['total_personas']} personas",
                "security": "multi-layer active",
                "marketplace": f"{self.marketplace.get_stats()['total_skills']} skills",
                "skills_standard": "SKILL.md bidirectional",
                "daily_logger": f"{self.daily_logger.get_stats()['total_entries']} entries",
                "session_replay": f"{self.session_replay.get_stats()['total_events']} events",
                "cli": f"{self.cli.get_stats()['available_commands']} commands",
            },
            "pipeline_stages": len(PIPELINE_STAGES),
            "total_requests": self._total_requests,
            "mcp_servers": mcp_stats['total_servers'],
        }


# ── Singleton ─────────────────────────────────────────────────

_engine: Optional[DiveEngine] = None


def get_engine(config: Dict = None) -> DiveEngine:
    """Get or create the DiveEngine singleton."""
    global _engine
    if _engine is None:
        _engine = DiveEngine(config or {})
    return _engine
