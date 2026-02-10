"""
Full test: ALL skills including new Media, Finance, SmartHome, Coding, Git extras.
Tests all gap-closing additions for OpenClaw parity.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

results = {"passed": 0, "failed": 0, "errors": []}

def test(name, fn):
    try:
        r = fn()
        if r:
            results["passed"] += 1
            print(f"  ✅ {name}")
        else:
            results["failed"] += 1
            print(f"  ❌ {name}")
            results["errors"].append(name)
    except Exception as e:
        results["failed"] += 1
        print(f"  ❌ {name}: {e}")
        results["errors"].append(f"{name}: {e}")

from dive_core.skills.skill_registry import SkillRegistry
from dive_core.skills.skill_spec import SkillCategory

reg = SkillRegistry()

# ── ORIGINAL 30 ─────────────────────────────────────────
print("=" * 60)
print("ORIGINAL 30 SKILLS")
print("=" * 60)

from dive_core.skills.browser.browser_skill import BrowserSkill
from dive_core.skills.browser.scraper_skill import ScraperSkill
from dive_core.skills.browser.form_fill_skill import FormFillSkill
from dive_core.skills.browser.web_screenshot_skill import WebScreenshotSkill
from dive_core.skills.browser.pdf_skill import PdfSkill
from dive_core.skills.search.web_search_skill import WebSearchSkill
from dive_core.skills.search.academic_skill import AcademicSkill
from dive_core.skills.search.youtube_skill import YoutubeSkill
from dive_core.skills.search.deep_research_skill import DeepResearchSkill
from dive_core.skills.search.news_skill import NewsSkill
from dive_core.skills.communication.email_skill import EmailSkill
from dive_core.skills.communication.email_reader_skill import EmailReaderSkill
from dive_core.skills.communication.telegram_skill import TelegramSkill
from dive_core.skills.communication.discord_skill import DiscordSkill
from dive_core.skills.communication.webhook_skill import WebhookSkill
from dive_core.skills.devops.git_skill import GitSkill
from dive_core.skills.devops.docker_skill import DockerSkill
from dive_core.skills.devops.file_skill import FileSkill
from dive_core.skills.devops.process_skill import ProcessSkill
from dive_core.skills.devops.system_info_skill import SystemInfoSkill
from dive_core.skills.ai.model_switch_skill import ModelSwitchSkill
from dive_core.skills.ai.prompt_skill import PromptSkill
from dive_core.skills.ai.agent_spawn_skill import AgentSpawnSkill
from dive_core.skills.ai.memory_query_skill import MemoryQuerySkill
from dive_core.skills.ai.self_improve_skill import SelfImproveSkill
from dive_core.skills.productivity.task_skill import TaskSkill
from dive_core.skills.productivity.note_skill import NoteSkill
from dive_core.skills.productivity.data_skill import DataSkill
from dive_core.skills.productivity.code_review_skill import CodeReviewSkill
from dive_core.skills.productivity.scheduler_skill import SchedulerSkill

for cls in [BrowserSkill, ScraperSkill, FormFillSkill, WebScreenshotSkill, PdfSkill,
            WebSearchSkill, AcademicSkill, YoutubeSkill, DeepResearchSkill, NewsSkill,
            EmailSkill, EmailReaderSkill, TelegramSkill, DiscordSkill, WebhookSkill,
            GitSkill, DockerSkill, FileSkill, ProcessSkill, SystemInfoSkill,
            ModelSwitchSkill, PromptSkill, AgentSpawnSkill, MemoryQuerySkill, SelfImproveSkill,
            TaskSkill, NoteSkill, DataSkill, CodeReviewSkill, SchedulerSkill]:
    reg.register(cls())

test("30 original skills", lambda: len(reg.list_names()) == 30)

# ── NEW MEDIA (5) ───────────────────────────────────────
print("\n" + "=" * 60)
print("NEW: MEDIA SKILLS (5)")
print("=" * 60)

from dive_core.skills.media.image_gen_skill import ImageGenSkill
from dive_core.skills.media.image_analyze_skill import ImageAnalyzeSkill
from dive_core.skills.media.video_skill import VideoSkill
from dive_core.skills.media.audio_skill import AudioSkill
from dive_core.skills.media.spotify_skill import SpotifySkill

for cls in [ImageGenSkill, ImageAnalyzeSkill, VideoSkill, AudioSkill, SpotifySkill]:
    reg.register(cls())

test("image-gen load", lambda: reg.get("image-gen") is not None)
test("image-analyze load", lambda: reg.get("image-analyze") is not None)
test("video-process load", lambda: reg.get("video-process") is not None)
test("audio-process load", lambda: reg.get("audio-process") is not None)
test("spotify load", lambda: reg.get("spotify") is not None)

r = reg.get("image-gen").execute({"prompt": "test image"})
test("image-gen sim", lambda: r.status == "success" and r.data.get("simulated"))

r = reg.get("image-analyze").execute({"image_path": "nonexistent.png"})
test("image-analyze no-file", lambda: r.status == "failure")

r = reg.get("spotify").execute({"action": "search", "query": "test"})
test("spotify sim", lambda: r.status == "success" and r.data.get("simulated"))

# ── NEW FINANCE (5) ─────────────────────────────────────
print("\n" + "=" * 60)
print("NEW: FINANCE SKILLS (5)")
print("=" * 60)

from dive_core.skills.finance.stock_skill import StockSkill
from dive_core.skills.finance.crypto_skill import CryptoSkill
from dive_core.skills.finance.budget_skill import BudgetSkill
from dive_core.skills.finance.currency_skill import CurrencySkill
from dive_core.skills.finance.finance_news_skill import FinanceNewsSkill

for cls in [StockSkill, CryptoSkill, BudgetSkill, CurrencySkill, FinanceNewsSkill]:
    reg.register(cls())

test("stock-tracker load", lambda: reg.get("stock-tracker") is not None)
test("crypto-tracker load", lambda: reg.get("crypto-tracker") is not None)
test("budget-tracker load", lambda: reg.get("budget-tracker") is not None)
test("currency-converter load", lambda: reg.get("currency-converter") is not None)
test("finance-news load", lambda: reg.get("finance-news") is not None)

r = reg.get("budget-tracker").execute({"action": "add", "amount": -50, "category": "food", "description": "lunch"})
test("budget add", lambda: r.status == "success")
r = reg.get("budget-tracker").execute({"action": "summary"})
test("budget summary", lambda: r.status == "success" and r.data.get("expenses", 0) >= 50)

# ── NEW SMART HOME (3) ──────────────────────────────────
print("\n" + "=" * 60)
print("NEW: SMART HOME SKILLS (3)")
print("=" * 60)

from dive_core.skills.smart_home.smart_home_skill import SmartHomeSkill
from dive_core.skills.smart_home.device_control_skill import DeviceControlSkill
from dive_core.skills.smart_home.sensor_skill import SensorSkill

for cls in [SmartHomeSkill, DeviceControlSkill, SensorSkill]:
    reg.register(cls())

test("smart-home load", lambda: reg.get("smart-home") is not None)
test("device-control load", lambda: reg.get("device-control") is not None)
test("sensor-monitor load", lambda: reg.get("sensor-monitor") is not None)

r = reg.get("smart-home").execute({"action": "states"})
test("smart-home sim", lambda: r.status == "success" and r.data.get("simulated"))

r = reg.get("sensor-monitor").execute({"sensor": "all"})
test("sensor read", lambda: r.status == "success")

r = reg.get("device-control").execute({"action": "status"})
test("device status", lambda: r.status == "success")

# ── NEW CODING (2) ──────────────────────────────────────
print("\n" + "=" * 60)
print("NEW: CODING SKILLS (2)")
print("=" * 60)

from dive_core.skills.coding.project_scaffold_skill import ProjectScaffoldSkill
from dive_core.skills.coding.refactor_skill import RefactorSkill

for cls in [ProjectScaffoldSkill, RefactorSkill]:
    reg.register(cls())

test("project-scaffold load", lambda: reg.get("project-scaffold") is not None)
test("code-refactor load", lambda: reg.get("code-refactor") is not None)

r = reg.get("code-refactor").execute({"action": "stats", "path": os.path.join(os.path.dirname(__file__), "desktop-app", "backend", "dive_core", "skills")})
test("refactor stats", lambda: r.status == "success" and r.data.get("files", 0) > 30)
print(f"    → {r.data.get('files', 0)} files, {r.data.get('lines', 0)} lines in skills/")

# ── NEW GIT/DEVOPS EXTRAS (3) ───────────────────────────
print("\n" + "=" * 60)
print("NEW: GIT/DEVOPS EXTRAS (3)")
print("=" * 60)

from dive_core.skills.devops.pr_skill import PRSkill
from dive_core.skills.devops.issue_skill import IssueSkill
from dive_core.skills.devops.cicd_skill import CICDSkill

for cls in [PRSkill, IssueSkill, CICDSkill]:
    reg.register(cls())

test("pr-manager load", lambda: reg.get("pr-manager") is not None)
test("issue-tracker load", lambda: reg.get("issue-tracker") is not None)
test("ci-cd load", lambda: reg.get("ci-cd") is not None)

r = reg.get("pr-manager").execute({"action": "list", "repo": "test/repo"})
test("pr sim", lambda: r.status == "success" and r.data.get("simulated"))
r = reg.get("ci-cd").execute({"action": "list", "repo": "test/repo"})
test("ci-cd sim", lambda: r.status == "success" and r.data.get("simulated"))

# ── NEW COMMS EXTRAS (2) ────────────────────────────────
print("\n" + "=" * 60)
print("NEW: COMMUNICATION EXTRAS (2)")
print("=" * 60)

from dive_core.skills.communication.slack_skill import SlackSkill
from dive_core.skills.communication.whatsapp_skill import WhatsAppSkill

for cls in [SlackSkill, WhatsAppSkill]:
    reg.register(cls())

test("slack-bot load", lambda: reg.get("slack-bot") is not None)
test("whatsapp-bot load", lambda: reg.get("whatsapp-bot") is not None)

r = reg.get("slack-bot").execute({"message": "Hello"})
test("slack sim", lambda: r.status == "success" and r.data.get("simulated"))
r = reg.get("whatsapp-bot").execute({"to": "+1234567890", "message": "Hello"})
test("whatsapp sim", lambda: r.status == "success" and r.data.get("simulated"))

# ── NEW PRODUCTIVITY (1) ────────────────────────────────
print("\n" + "=" * 60)
print("NEW: CALENDAR SKILL (1)")
print("=" * 60)

from dive_core.skills.productivity.calendar_skill import CalendarSkill
reg.register(CalendarSkill())

test("calendar load", lambda: reg.get("calendar") is not None)
r = reg.get("calendar").execute({"action": "add", "title": "Test Event", "start": "2026-02-10 09:00"})
test("calendar add", lambda: r.status == "success")
r = reg.get("calendar").execute({"action": "list"})
test("calendar list", lambda: r.status == "success" and r.data.get("total", 0) > 0)

# ── SKILL INSTALLER ────────────────────────────────────
print("\n" + "=" * 60)
print("SKILL INSTALLER CLI")
print("=" * 60)

from dive_core.skills.skill_installer import SkillInstaller
installer = SkillInstaller()
stats = installer.get_stats()
test("installer stats", lambda: stats["total_skills"] > 40)
test("installer categories", lambda: stats["total_categories"] >= 10)
print(f"    → {stats['total_skills']} skills across {stats['total_categories']} categories")

cats = installer.list_categories()
for c in cats:
    print(f"    {c['category']}: {c['skills']} skills")

# ── FINAL SUMMARY ──────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL RESULTS")
print("=" * 60)

total = results["passed"] + results["failed"]
all_skills = reg.list_names()
all_cats = reg.list_all()

print(f"\n  🎯 {results['passed']}/{total} tests passed")
print(f"\n  📊 Total skills in registry: {len(all_skills)}")
print(f"  📊 Categories: {len(all_cats)}")
for cat, skills in sorted(all_cats.items()):
    names = [s["name"] if isinstance(s, dict) else str(s) for s in skills]
    print(f"    {cat}: {len(skills)} skills - {', '.join(names)}")

if results["failed"] > 0:
    print(f"\n  Failures:")
    for e in results["errors"]:
        print(f"    -> {e}")

print("\n" + "=" * 60)
if results["failed"] == 0:
    print(f"  ALL {total} TESTS PASSED - Full OpenClaw Parity! ({len(all_skills)} skills)")
else:
    print(f"  {results['failed']} issues")
print("=" * 60)
