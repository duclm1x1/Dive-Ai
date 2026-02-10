"""
Comprehensive test for all 30 Dive AI skills + combos + messaging + agent protocol.
Tests Phase 1-5 of the OpenClaw parity plan.
"""
import sys, os, time, json, traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

results = {"passed": 0, "failed": 0, "errors": [], "details": []}

def test(name, fn):
    try:
        r = fn()
        if r:
            results["passed"] += 1
            results["details"].append(f"  ✅ {name}")
        else:
            results["failed"] += 1
            results["details"].append(f"  ❌ {name}: returned False")
            results["errors"].append(name)
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"  ❌ {name}: {e}")
        results["errors"].append(f"{name}: {e}")

# ══════════════════════════════════════════════════════════
# PHASE 1: Foundation
# ══════════════════════════════════════════════════════════
print("═" * 60)
print("PHASE 1: Skill System Foundation")
print("═" * 60)

from dive_core.skills.skill_spec import SkillSpec, SkillCategory
from dive_core.skills.base_skill import BaseSkill
from dive_core.skills.skill_registry import SkillRegistry, get_registry
from dive_core.skills.skill_combo_engine import SkillComboEngine, ComboChain, ComboStep

test("SkillSpec creation", lambda: SkillSpec(name="test", description="Test", version="1.0").name == "test")
test("SkillCategory enum", lambda: len(SkillCategory) == 10)
test("Registry singleton", lambda: get_registry() is get_registry())
test("Registry empty", lambda: len(get_registry().list_names()) == 0)
test("ComboEngine init", lambda: SkillComboEngine() is not None)

# ══════════════════════════════════════════════════════════
# PHASE 2: Load All 30 Skills
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 2: Loading All 30 Skills")
print("═" * 60)

registry = SkillRegistry()

# Browser skills
from dive_core.skills.browser.browser_skill import BrowserSkill
from dive_core.skills.browser.scraper_skill import ScraperSkill
from dive_core.skills.browser.form_fill_skill import FormFillSkill
from dive_core.skills.browser.web_screenshot_skill import WebScreenshotSkill
from dive_core.skills.browser.pdf_skill import PdfSkill

test("BrowserSkill import", lambda: registry.register(BrowserSkill()))
test("ScraperSkill import", lambda: registry.register(ScraperSkill()))
test("FormFillSkill import", lambda: registry.register(FormFillSkill()))
test("WebScreenshotSkill import", lambda: registry.register(WebScreenshotSkill()))
test("PdfSkill import", lambda: registry.register(PdfSkill()))

# Search skills
from dive_core.skills.search.web_search_skill import WebSearchSkill
from dive_core.skills.search.academic_skill import AcademicSkill
from dive_core.skills.search.youtube_skill import YoutubeSkill
from dive_core.skills.search.deep_research_skill import DeepResearchSkill
from dive_core.skills.search.news_skill import NewsSkill

test("WebSearchSkill import", lambda: registry.register(WebSearchSkill()))
test("AcademicSkill import", lambda: registry.register(AcademicSkill()))
test("YoutubeSkill import", lambda: registry.register(YoutubeSkill()))
test("DeepResearchSkill import", lambda: registry.register(DeepResearchSkill()))
test("NewsSkill import", lambda: registry.register(NewsSkill()))

# Communication skills
from dive_core.skills.communication.email_skill import EmailSkill
from dive_core.skills.communication.email_reader_skill import EmailReaderSkill
from dive_core.skills.communication.telegram_skill import TelegramSkill
from dive_core.skills.communication.discord_skill import DiscordSkill
from dive_core.skills.communication.webhook_skill import WebhookSkill

test("EmailSkill import", lambda: registry.register(EmailSkill()))
test("EmailReaderSkill import", lambda: registry.register(EmailReaderSkill()))
test("TelegramSkill import", lambda: registry.register(TelegramSkill()))
test("DiscordSkill import", lambda: registry.register(DiscordSkill()))
test("WebhookSkill import", lambda: registry.register(WebhookSkill()))

# DevOps skills
from dive_core.skills.devops.git_skill import GitSkill
from dive_core.skills.devops.docker_skill import DockerSkill
from dive_core.skills.devops.file_skill import FileSkill
from dive_core.skills.devops.process_skill import ProcessSkill
from dive_core.skills.devops.system_info_skill import SystemInfoSkill

test("GitSkill import", lambda: registry.register(GitSkill()))
test("DockerSkill import", lambda: registry.register(DockerSkill()))
test("FileSkill import", lambda: registry.register(FileSkill()))
test("ProcessSkill import", lambda: registry.register(ProcessSkill()))
test("SystemInfoSkill import", lambda: registry.register(SystemInfoSkill()))

# AI skills
from dive_core.skills.ai.model_switch_skill import ModelSwitchSkill
from dive_core.skills.ai.prompt_skill import PromptSkill
from dive_core.skills.ai.agent_spawn_skill import AgentSpawnSkill
from dive_core.skills.ai.memory_query_skill import MemoryQuerySkill
from dive_core.skills.ai.self_improve_skill import SelfImproveSkill

test("ModelSwitchSkill import", lambda: registry.register(ModelSwitchSkill()))
test("PromptSkill import", lambda: registry.register(PromptSkill()))
test("AgentSpawnSkill import", lambda: registry.register(AgentSpawnSkill()))
test("MemoryQuerySkill import", lambda: registry.register(MemoryQuerySkill()))
test("SelfImproveSkill import", lambda: registry.register(SelfImproveSkill()))

# Productivity skills
from dive_core.skills.productivity.task_skill import TaskSkill
from dive_core.skills.productivity.note_skill import NoteSkill
from dive_core.skills.productivity.data_skill import DataSkill
from dive_core.skills.productivity.code_review_skill import CodeReviewSkill
from dive_core.skills.productivity.scheduler_skill import SchedulerSkill

test("TaskSkill import", lambda: registry.register(TaskSkill()))
test("NoteSkill import", lambda: registry.register(NoteSkill()))
test("DataSkill import", lambda: registry.register(DataSkill()))
test("CodeReviewSkill import", lambda: registry.register(CodeReviewSkill()))
test("SchedulerSkill import", lambda: registry.register(SchedulerSkill()))

# Verify total
print(f"\n  📊 Total skills registered: {len(registry.list_names())}")
test("30 skills registered", lambda: len(registry.list_names()) == 30)

# ══════════════════════════════════════════════════════════
# PHASE 2B: Execute Skills
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 2B: Executing Skills")
print("═" * 60)

# System info (safe, no network)
r = registry.get("system-info").execute({})
test("system-info execute", lambda: r.status == "success")
test("system-info has OS", lambda: r.data.get("os") is not None)
print(f"    → OS: {r.data.get('os')}, CPU: {r.data.get('cpu_count')}")

# File manager
r = registry.get("file-manager").execute({"action": "list", "path": "."})
test("file-manager list", lambda: r.status == "success")
test("file-manager has files", lambda: len(r.data.get("files", [])) > 0)

# Process manager
r = registry.get("process-manager").execute({"action": "list"})
test("process-manager list", lambda: r.status == "success")

# Git ops
r = registry.get("git-ops").execute({"action": "status", "path": os.path.dirname(__file__)})
test("git-ops status", lambda: r.status in ("success", "failure"))

# Model switcher
r = registry.get("model-switcher").execute({"model_id": "gpt-4"})
test("model-switcher", lambda: r.status == "success" and r.data.get("switched"))

# Prompt optimizer
r = registry.get("prompt-optimizer").execute({"prompt": "explain AI", "task_type": "general"})
test("prompt-optimizer", lambda: r.status == "success" and len(r.data.get("improvements", [])) > 0)

# Scraper
html = "<html><head><title>Test</title></head><body><h1>Hello</h1><a href='https://test.com'>Link</a></body></html>"
r = registry.get("web-scrape").execute({"html": html})
test("web-scrape extract", lambda: r.status == "success" and "Hello" in r.data.get("text", ""))
test("web-scrape links", lambda: "https://test.com" in r.data.get("links", []))
test("web-scrape title", lambda: r.data.get("title") == "Test")

# Form fill
form_html = '<form action="/submit"><input name="email" type="text"><input name="pass" type="password"></form>'
r = registry.get("form-fill").execute({"html": form_html, "fields": {"email": "test@test.com"}})
test("form-fill detect", lambda: r.status == "success" and r.data.get("total_fields") >= 2)

# Task manager
r = registry.get("task-manager").execute({"action": "add", "title": "Test Task", "priority": "high"})
test("task-manager add", lambda: r.status == "success")
r = registry.get("task-manager").execute({"action": "list"})
test("task-manager list", lambda: r.status == "success" and r.data.get("total", 0) > 0)

# Note taker
r = registry.get("note-taker").execute({"action": "save", "title": "Test Note", "content": "This is a test note", "tags": ["test"]})
test("note-taker save", lambda: r.status == "success")
r = registry.get("note-taker").execute({"action": "search", "query": "test note"})
test("note-taker search", lambda: r.status == "success")

# Data analyzer
r = registry.get("data-analyzer").execute({"data": [{"name": "A", "val": 10}, {"name": "B", "val": 20}]})
test("data-analyzer", lambda: r.status == "success" and r.data["analysis"]["count"] == 2)

# Code review
r = registry.get("code-review").execute({"code": "import *\ndef foo():\n    eval('x')\n    password = 'secret123'\n"})
test("code-review issues", lambda: r.status == "success" and len(r.data.get("issues", [])) >= 2)
test("code-review score", lambda: r.data.get("score", 10) < 8)

# Scheduler
r = registry.get("scheduler").execute({"action": "add", "skill_name": "system-info", "interval_seconds": 300})
test("scheduler add", lambda: r.status == "success")
r = registry.get("scheduler").execute({"action": "list"})
test("scheduler list", lambda: r.status == "success" and r.data.get("total", 0) > 0)

# Memory query (may find nothing, that's OK)
r = registry.get("memory-query").execute({"query": "test"})
test("memory-query", lambda: r.status == "success")

# Self improve
r = registry.get("self-improve").execute({"focus": "all"})
test("self-improve", lambda: r.status == "success" and len(r.data.get("recommendations", [])) > 0)

# Email (simulated)
r = registry.get("email-send").execute({"to": "test@test.com", "subject": "Test", "body": "Hello"})
test("email-send simulated", lambda: r.status == "success" and r.data.get("simulated"))

# Email reader (simulated)
r = registry.get("email-read").execute({"limit": 5})
test("email-read simulated", lambda: r.status == "success" and r.data.get("simulated"))

# Telegram (simulated)
r = registry.get("telegram-bot").execute({"action": "send", "message": "Hello"})
test("telegram simulated", lambda: r.status == "success" and r.data.get("simulated"))

# Discord (simulated)
r = registry.get("discord-bot").execute({"message": "Hello"})
test("discord simulated", lambda: r.status == "success" and r.data.get("simulated"))

# Agent spawn
r = registry.get("agent-spawn").execute({"tasks": ["task1", "task2"]})
test("agent-spawn", lambda: r.status == "success" and r.data.get("queued") == 2)

# Deep research (standalone)
r = registry.get("deep-research").execute({"topic": "AI trends 2026"})
test("deep-research standalone", lambda: r.status == "success")

# ══════════════════════════════════════════════════════════
# PHASE 2C: Registry Features
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 2C: Registry Discovery & Stats")
print("═" * 60)

test("discover 'search'", lambda: len(registry.discover("search for AI news")) > 0)
test("discover 'email'", lambda: len(registry.discover("send email to John")) > 0)
test("discover 'code'", lambda: len(registry.discover("review my code")) > 0)
test("by category browser", lambda: len(registry.list_by_category(SkillCategory.BROWSER)) == 5)
test("by category search", lambda: len(registry.list_by_category(SkillCategory.SEARCH)) == 5)
test("by category comm", lambda: len(registry.list_by_category(SkillCategory.COMMUNICATION)) == 5)
test("by category devops", lambda: len(registry.list_by_category(SkillCategory.DEVOPS)) == 5)
test("by category ai", lambda: len(registry.list_by_category(SkillCategory.AI)) == 5)
test("by category prod", lambda: len(registry.list_by_category(SkillCategory.PRODUCTIVITY)) == 5)

stats = registry.get_stats()
test("stats total=30", lambda: stats["total_skills"] == 30)
test("stats has executions", lambda: stats["total_executions"] > 0)
print(f"    → Executions: {stats['total_executions']}, Cost: ${stats['total_cost']:.6f}")

# ══════════════════════════════════════════════════════════
# PHASE 3: Combo Engine
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 3: Combo Engine")
print("═" * 60)

from dive_core.skills.combo_templates import ALL_COMBOS

engine = SkillComboEngine(registry)
for combo in ALL_COMBOS:
    engine.register_combo(combo)

test("8 combos registered", lambda: len(engine.list_combos()) == 8)

# Execute system-health-check combo
combo = engine.get_combo("system-health-check")
r = engine.execute_combo(combo)
test("system-health combo success", lambda: r.success)
test("system-health 2 steps", lambda: len(r.step_results) == 2)
serial = engine.to_dict(r)
test("combo serializable", lambda: serial["success"])
print(f"    → Duration: {serial['total_duration_ms']:.1f}ms, Steps: {len(serial['steps'])}")

# Execute self-diagnostic combo
combo = engine.get_combo("self-diagnostic")
r = engine.execute_combo(combo)
test("self-diagnostic combo", lambda: r.success)
print(f"    → Duration: {r.total_duration_ms:.1f}ms")

# Plan a combo automatically
planned = engine.plan_combo("search for AI trends and take notes")
test("auto-plan combo", lambda: planned is not None and len(planned.steps) > 0)
if planned:
    print(f"    → Auto-planned: {[s.skill_name for s in planned.steps]}")

# Combo stats
cstats = engine.get_stats()
test("combo stats", lambda: cstats["combos_executed"] >= 2)

# ══════════════════════════════════════════════════════════
# PHASE 4: Messaging Bridge
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 4: Messaging Bridge")
print("═" * 60)

from dive_core.communication.messaging_bridge import MessagingBridge, MessageHandler

bridge = MessagingBridge()
test("bridge init", lambda: bridge is not None)
test("bridge status", lambda: bridge.status()["total_messages"] == 0)
test("telegram not configured", lambda: not bridge.telegram.configured)
test("discord not configured", lambda: not bridge.discord.configured)

# Message handler
handler = MessageHandler()
reply = handler.process("Hello Dive AI")
test("handler process", lambda: "Hello" in reply)
test("handler log", lambda: len(handler.message_log) == 1)

# ══════════════════════════════════════════════════════════
# PHASE 5: Agent Protocol
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("PHASE 5: Agent Protocol")
print("═" * 60)

from dive_core.communication.agent_protocol import DiveAgentProtocol

protocol = DiveAgentProtocol()
test("protocol init", lambda: protocol.agent_id == "dive-ai-primary")

protocol.register_capability("web-search", "Search the web")
protocol.register_capability("code-review", "Review code quality")
test("capabilities registered", lambda: len(protocol._capabilities) == 2)

info = protocol.get_info()
test("agent info", lambda: info["status"] == "online" and len(info["capabilities"]) == 2)

protocol.register_peer("agent-2", "Dive AI Secondary", "http://localhost:1880")
test("peer registered", lambda: len(protocol.discover_peers()) == 1)

task_resp = protocol.receive_task({"skill_name": "web-search", "inputs": {"query": "test"}})
test("receive task", lambda: task_resp["queued"])

status = protocol.get_status()
test("protocol status", lambda: status["capabilities"] == 2 and status["peers"] == 1)

# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("FINAL RESULTS")
print("═" * 60)
total = results["passed"] + results["failed"]
print(f"\n  🎯 {results['passed']}/{total} tests passed")

if results["failed"] > 0:
    print(f"\n  ⚠️  {results['failed']} FAILURES:")
    for e in results["errors"]:
        print(f"    → {e}")

print(f"\n  📊 Skills: {len(registry.list_names())}")
print(f"  📊 Categories: {len(registry.list_all())}")
print(f"  📊 Combos: {len(engine.list_combos())}")
print(f"  📊 Total executions: {registry.get_stats()['total_executions']}")

print("\n" + "═" * 60)
if results["failed"] == 0:
    print("  🚀 ALL PHASES PASSED — OpenClaw Parity Achieved!")
else:
    print(f"  ⚠️  {results['failed']} issues need fixing")
print("═" * 60)
