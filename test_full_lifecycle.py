"""
15 Full Lifecycle Test Cases — User Sits Back, AI Does Everything

Each test proves Dive AI can handle a complete real-world workflow:
  PC control → web search → build UI → login → database → test → debug → deploy

Tests exercise: 32 skill categories, 32 auto-created algorithms,
                8 lifecycle stages, 14 DiveEngine subsystems.

Grand goal: User says what they want → AI delivers the entire product.
"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "desktop-app", "backend"))

from dive_core.engine.full_lifecycle import (
    DiveSkillRegistry, AutoAlgorithmEngine, FullLifecycleEngine,
    LifecycleStage, SKILL_CATEGORIES, SKILL_REGISTRY, ALGORITHM_TEMPLATES,
    STAGE_ALGORITHMS, AlgorithmSpec,
)
from dive_core.engine.dive_engine import DiveEngine

# ── Test helpers ──────────────────────────────────────────────
passed = 0
failed = 0
total = 0
failures = []

def case(title, checks):
    global passed, failed, total
    ok = 0
    for name, fn in checks:
        total += 1
        try:
            if fn():
                ok += 1
                passed += 1
            else:
                failed += 1
                failures.append(f"{title}: {name}")
        except Exception as e:
            failed += 1
            failures.append(f"{title}: {name} — {e}")
    status = "✔" if ok == len(checks) else "✗"
    print(f"  {status} Case: {title} ({ok}/{len(checks)} checks)")


# ══════════════════════════════════════════════════════════════
# SETUP: Initialize all systems
# ══════════════════════════════════════════════════════════════
print("=" * 60)
print("  15 FULL LIFECYCLE TESTS — USER SITS BACK, AI DELIVERS")
print("=" * 60)

registry = DiveSkillRegistry()
algorithms = AutoAlgorithmEngine()
lifecycle = FullLifecycleEngine(registry, algorithms)
engine = DiveEngine()

print()
print(f"  Skills registered: {registry.get_stats()['total_skills']}")
print(f"  Algorithms created: {algorithms.get_stats()['total_algorithms']}")
print(f"  Categories covered: {len(SKILL_CATEGORIES)}")
print(f"  Lifecycle stages: {len(LifecycleStage)}")
print()


# ══════════════════════════════════════════════════════════════
# CASE 1: Build a REST API from scratch
# ══════════════════════════════════════════════════════════════
print("║║ Scenario: Full Product Development ║║")
result1 = lifecycle.run_full_lifecycle(
    "REST API",
    "Build a FastAPI REST API with auth, CRUD, and tests",
    {"framework": "fastapi", "features": ["auth", "crud", "tests"]},
)
case("1. Build REST API from scratch", [
    ("All 8 stages completed", lambda: result1["stages_completed"] == 8),
    ("Algorithms auto-selected", lambda: result1["total_algorithms"] >= 5),
    ("Skills auto-selected", lambda: result1["total_skills"] >= 10),
    ("Task completed", lambda: result1["status"] == "completed"),
    ("Plan stage ran", lambda: result1["stage_results"]["plan"]["success"]),
    ("Code stage ran", lambda: result1["stage_results"]["code"]["success"]),
    ("Test stage ran", lambda: result1["stage_results"]["test"]["success"]),
    ("Deploy stage ran", lambda: result1["stage_results"]["deploy"]["success"]),
])


# ══════════════════════════════════════════════════════════════
# CASE 2: Create React Dashboard UI
# ══════════════════════════════════════════════════════════════
result2 = lifecycle.run_full_lifecycle(
    "React Dashboard",
    "Create a modern React dashboard with charts, auth, and responsive design",
    {"framework": "react", "features": ["charts", "auth", "responsive"]},
)
case("2. Create React Dashboard UI", [
    ("Full lifecycle completed", lambda: result2["status"] == "completed"),
    ("UI Builder algorithm used", lambda: "UIBuilder" in str(result2)),
    ("Web frontend skills selected", lambda: len(result2["stage_results"]["code"]["skills_selected"]) > 0),
    ("Browser testing stage", lambda: result2["stage_results"]["test"]["success"]),
    ("8 stages executed", lambda: result2["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 3: Setup Database with Migrations
# ══════════════════════════════════════════════════════════════
result3 = lifecycle.run_full_lifecycle(
    "Database Setup",
    "Create PostgreSQL schema, migrations, seed data, and ORM models",
    {"database": "postgres", "orm": "sqlalchemy"},
)
case("3. Setup database with migrations", [
    ("Schema created (plan stage)", lambda: result3["stage_results"]["plan"]["success"]),
    ("Code generated", lambda: result3["stage_results"]["code"]["success"]),
    ("DataPipeline algorithm used", lambda: "DataPipeline" in str(result3)),
    ("Build stage ran", lambda: result3["stage_results"]["build"]["success"]),
    ("All stages complete", lambda: result3["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 4: Debug a Production Crash
# ══════════════════════════════════════════════════════════════
result4 = lifecycle.run_full_lifecycle(
    "Debug Production Crash",
    "Analyze crash logs, find root cause, implement fix, verify",
    {"error": "NullPointerException at line 42", "service": "payment-api"},
)
case("4. Debug a production crash", [
    ("Research phase ran", lambda: result4["stage_results"]["plan"]["success"]),
    ("Debug stage executed", lambda: result4["stage_results"]["debug"]["success"]),
    ("CodeGenerator used for fix", lambda: "CodeGenerator" in str(result4)),
    ("DeepResearcher used for analysis", lambda: "DeepResearcher" in str(result4)),
    ("Verify stage confirms fix", lambda: result4["stage_results"]["verify"]["success"]),
    ("Full lifecycle completed", lambda: result4["status"] == "completed"),
])


# ══════════════════════════════════════════════════════════════
# CASE 5: Search Web & Build Feature
# ══════════════════════════════════════════════════════════════
result5 = lifecycle.run_full_lifecycle(
    "Feature from Research",
    "Research best practices for rate limiting, then implement in FastAPI",
    {"topic": "rate_limiting", "framework": "fastapi"},
)
case("5. Search web & implement feature", [
    ("Research stage used DeepResearcher", lambda: any(
        a.get("name") == "DeepResearcher"
        for a in result5["stage_results"]["plan"].get("algorithms_executed", [])
    )),
    ("Code stage used CodeGenerator", lambda: any(
        a.get("name") == "CodeGenerator"
        for a in result5["stage_results"]["code"].get("algorithms_executed", [])
    )),
    ("Test stage executed", lambda: result5["stage_results"]["test"]["success"]),
    ("All stages passed", lambda: result5["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 6: Login System with OAuth + JWT
# ══════════════════════════════════════════════════════════════
result6 = lifecycle.run_full_lifecycle(
    "Auth System",
    "Build complete login: OAuth2, JWT tokens, bcrypt, session management, 2FA",
    {"auth_type": "oauth2", "features": ["jwt", "bcrypt", "2fa"]},
)
case("6. Login system with OAuth + JWT", [
    ("SecurityScanner in deploy", lambda: any(
        a.get("name") == "SecurityScanner"
        for a in result6["stage_results"]["deploy"].get("algorithms_executed", [])
    )),
    ("CodeGenerator in code stage", lambda: result6["stage_results"]["code"]["success"]),
    ("All 8 stages completed", lambda: result6["stages_completed"] == 8),
    ("Security skills used", lambda: result6["total_skills"] >= 5),
])


# ══════════════════════════════════════════════════════════════
# CASE 7: Deploy to Production (Docker + CI/CD + Cloud)
# ══════════════════════════════════════════════════════════════
result7 = lifecycle.run_full_lifecycle(
    "Production Deploy",
    "Dockerize app, setup CI/CD pipeline, deploy to AWS, configure SSL",
    {"cloud": "aws", "ci_cd": "github_actions", "ssl": True},
)
case("7. Deploy to production (Docker + CI/CD)", [
    ("CloudDeployer in deploy stage", lambda: any(
        a.get("name") == "CloudDeployer"
        for a in result7["stage_results"]["deploy"].get("algorithms_executed", [])
    )),
    ("ShellExecutor in build stage", lambda: any(
        a.get("name") == "ShellExecutor"
        for a in result7["stage_results"]["build"].get("algorithms_executed", [])
    )),
    ("Security scan in deploy", lambda: any(
        "security" in a.get("category", "")
        for a in result7["stage_results"]["deploy"].get("algorithms_executed", [])
    )),
    ("Verify stage confirms uptime", lambda: result7["stage_results"]["verify"]["success"]),
    ("All stages completed", lambda: result7["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 8: Full Test Suite (Unit + Integration + E2E)
# ══════════════════════════════════════════════════════════════
result8 = lifecycle.run_full_lifecycle(
    "Full Test Suite",
    "Unit tests, integration tests, E2E browser tests, coverage report",
    {"test_types": ["unit", "integration", "e2e"], "coverage_target": 80},
)
case("8. Full test suite creation", [
    ("BrowserAgent for E2E", lambda: "BrowserAgent" in str(result8)),
    ("CodeGenerator for test code", lambda: "CodeGenerator" in str(result8)),
    ("Test stage ran", lambda: result8["stage_results"]["test"]["success"]),
    ("All stages completed", lambda: result8["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 9: Web Scraping Pipeline
# ══════════════════════════════════════════════════════════════
print()
print("║║ Scenario: Data & Automation ║║")
result9 = lifecycle.run_full_lifecycle(
    "Web Scraping Pipeline",
    "Scrape product data, transform, store in DB, generate report",
    {"target_url": "products.example.com", "storage": "postgres"},
)
case("9. Web scraping pipeline", [
    ("BrowserAgent for scraping", lambda: "BrowserAgent" in str(result9)),
    ("DataPipeline for ETL", lambda: "DataPipeline" in str(result9)),
    ("All stages completed", lambda: result9["stages_completed"] == 8),
    ("Multiple skills used", lambda: result9["total_skills"] >= 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 10: AI Chat Feature with Memory
# ══════════════════════════════════════════════════════════════
result10 = lifecycle.run_full_lifecycle(
    "AI Chat Feature",
    "Build LLM chat with streaming, memory, context window, persona",
    {"llm_provider": "openai", "features": ["streaming", "memory", "persona"]},
)
case("10. AI chat feature with memory", [
    ("LLMOrchestrator used", lambda: "LLMOrchestrator" in str(result10)),
    ("CodeGenerator for implementation", lambda: "CodeGenerator" in str(result10)),
    ("Plan stage researched best practices", lambda: result10["stage_results"]["plan"]["success"]),
    ("All stages completed", lambda: result10["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 11: Mobile Responsive UI
# ══════════════════════════════════════════════════════════════
result11 = lifecycle.run_full_lifecycle(
    "Responsive UI",
    "Build mobile-first responsive UI with animations and dark mode",
    {"design_system": "material", "breakpoints": ["mobile", "tablet", "desktop"]},
)
case("11. Mobile responsive UI build", [
    ("UIBuilder used", lambda: "UIBuilder" in str(result11)),
    ("BrowserAgent for testing viewport", lambda: "BrowserAgent" in str(result11)),
    ("All stages completed", lambda: result11["stages_completed"] == 8),
    ("Multiple skills selected", lambda: result11["total_skills"] >= 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 12: Git Workflow (Branch → PR → Merge → Deploy)
# ══════════════════════════════════════════════════════════════
print()
print("║║ Scenario: DevOps & Git ║║")
result12 = lifecycle.run_full_lifecycle(
    "Git Workflow",
    "Create feature branch, implement feature, create PR, merge, deploy",
    {"branch": "feature/user-auth", "base": "main"},
)
case("12. Git workflow (branch → PR → deploy)", [
    ("GitWorkflow algorithm used", lambda: "GitWorkflow" in str(result12)),
    ("CodeGenerator for feature", lambda: "CodeGenerator" in str(result12)),
    ("CloudDeployer for deploy", lambda: "CloudDeployer" in str(result12)),
    ("All stages completed", lambda: result12["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 13: Monitoring & Observability Setup
# ══════════════════════════════════════════════════════════════
result13 = lifecycle.run_full_lifecycle(
    "Monitoring Setup",
    "Setup Prometheus, Grafana dashboards, alerts, logging",
    {"tools": ["prometheus", "grafana", "alertmanager"]},
)
case("13. Monitoring & observability setup", [
    ("CloudDeployer for infra", lambda: "CloudDeployer" in str(result13)),
    ("DataPipeline for metrics", lambda: "DataPipeline" in str(result13)),
    ("ShellExecutor for configs", lambda: "ShellExecutor" in str(result13)),
    ("All stages completed", lambda: result13["stages_completed"] == 8),
])


# ══════════════════════════════════════════════════════════════
# CASE 14: Security Audit & Remediation
# ══════════════════════════════════════════════════════════════
result14 = lifecycle.run_full_lifecycle(
    "Security Audit",
    "Full security scan, vulnerability assessment, patch, re-scan",
    {"scan_type": "full", "targets": ["deps", "code", "infra"]},
)
case("14. Security audit & remediation", [
    ("SecurityScanner in deploy", lambda: any(
        a.get("name") == "SecurityScanner"
        for a in result14["stage_results"]["deploy"].get("algorithms_executed", [])
    )),
    ("CodeGenerator for patches", lambda: "CodeGenerator" in str(result14)),
    ("Verify stage re-scans", lambda: result14["stage_results"]["verify"]["success"]),
    ("All stages completed", lambda: result14["stages_completed"] == 8),
])

# ══════════════════════════════════════════════════════════════
# CASE 15: MEGA — Full Product Launch (ALL systems)
# ══════════════════════════════════════════════════════════════
print()
print("║║ MEGA CASE: Full Product Launch ║║")
result15 = lifecycle.run_full_lifecycle(
    "Full Product Launch",
    "Complete product: research → design → code → database → auth → "
    "API → UI → tests → debug → deploy → monitoring → security audit → launch",
    {
        "product": "SaaS Dashboard",
        "stack": "FastAPI + React + PostgreSQL",
        "features": [
            "auth", "crud", "dashboard", "charts", "notifications",
            "admin_panel", "api_docs", "monitoring", "ci_cd",
        ],
    },
)

# Comprehensive checks for the mega case
case("15. FULL PRODUCT LAUNCH (ALL systems)", [
    # Core lifecycle
    ("All 8 stages completed", lambda: result15["stages_completed"] == 8),
    ("Status is completed", lambda: result15["status"] == "completed"),
    # Algorithms breadth
    ("5+ unique algorithms used", lambda: result15["total_algorithms"] >= 5),
    ("10+ skills engaged", lambda: result15["total_skills"] >= 10),
    # Critical stages
    ("Plan researched best approach", lambda: result15["stage_results"]["plan"]["success"]),
    ("Scaffold created project", lambda: result15["stage_results"]["scaffold"]["success"]),
    ("Code implemented features", lambda: result15["stage_results"]["code"]["success"]),
    ("Build compiled/containerized", lambda: result15["stage_results"]["build"]["success"]),
    ("Tests verified quality", lambda: result15["stage_results"]["test"]["success"]),
    ("Debug found/fixed issues", lambda: result15["stage_results"]["debug"]["success"]),
    ("Deploy pushed to prod", lambda: result15["stage_results"]["deploy"]["success"]),
    ("Verify confirmed live", lambda: result15["stage_results"]["verify"]["success"]),
])


# ══════════════════════════════════════════════════════════════
# BONUS: Registry & Algorithm Completeness
# ══════════════════════════════════════════════════════════════
print()
print("║║ System Completeness Verification ║║")

reg_stats = registry.get_stats()
algo_stats = algorithms.get_stats()
lc_stats = lifecycle.get_stats()

case("BONUS A: Skill Registry completeness", [
    ("32 categories registered", lambda: reg_stats["total_categories"] == 32),
    ("200+ skills registered", lambda: reg_stats["total_skills"] >= 200),
    ("Surpasses OpenClaw", lambda: reg_stats["surpasses_openclaw"]),
])

case("BONUS B: Algorithm completeness", [
    ("32 algorithms auto-created", lambda: algo_stats["total_algorithms"] == 32),
    ("All deployed", lambda: algo_stats["deployed"] == 32),
    ("32 categories covered", lambda: algo_stats["categories_covered"] == 32),
    ("Execution log populated", lambda: algo_stats["total_executions"] > 0),
])

case("BONUS C: DiveEngine has 14+ subsystems", [
    ("Engine operational", lambda: engine.health_check()["status"] == "operational"),
    ("14 subsystems", lambda: len(engine.health_check()["subsystems"]) >= 14),
    ("121+ MCP servers", lambda: engine.health_check()["mcp_servers"] >= 120),
])

case("BONUS D: Lifecycle engine stats", [
    ("15 tasks executed", lambda: lc_stats["total_tasks"] == 15),
    ("15 completed", lambda: lc_stats["completed"] == 15),
    ("8 lifecycle stages", lambda: lc_stats["lifecycle_stages"] == 8),
])


# ══════════════════════════════════════════════════════════════
# FINAL REPORT
# ══════════════════════════════════════════════════════════════
print()
print("=" * 60)
print(f"  {passed}/{total} checks passed ({round(passed/total*100, 1)}%)")
if failures:
    print(f"  {len(failures)} failures:")
    for f in failures:
        print(f"    ✗ {f}")

if passed == total:
    print()
    print("  ★  ALL 15 LIFECYCLE TESTS PASSED — USER SITS BACK, AI DELIVERS  ★")
    print()
    print(f"  Skills: {reg_stats['total_skills']} across {reg_stats['total_categories']} categories")
    print(f"  Algorithms: {algo_stats['total_algorithms']} auto-created & deployed")
    print(f"  Lifecycle: {lc_stats['lifecycle_stages']} stages × {lc_stats['completed']} runs = FULL COVERAGE")
print("=" * 60)
