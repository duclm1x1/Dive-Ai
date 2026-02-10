"""
Dive AI Combo Templates — Pre-built algorithm chains.
Each combo chains multiple skills with verification at every step.
"""
from .skill_combo_engine import ComboChain, ComboStep


# ── Research Combos ────────────────────────────────────────

RESEARCH_AND_WRITE = ComboChain(
    name="research-and-write",
    description="Search the web, aggregate research, and save notes",
    steps=[
        ComboStep(skill_name="web-search", params={}),
        ComboStep(skill_name="deep-research", use_prev_output=True),
        ComboStep(skill_name="note-taker", params={"action": "save"}, use_prev_output=True),
    ],
    tags=["research", "write", "content"],
)

ACADEMIC_DIVE = ComboChain(
    name="academic-dive",
    description="Search arXiv papers and create research notes",
    steps=[
        ComboStep(skill_name="academic-search", params={}),
        ComboStep(skill_name="deep-research", use_prev_output=True),
        ComboStep(skill_name="note-taker", params={"action": "save"}, use_prev_output=True),
    ],
    tags=["academic", "research", "paper"],
)

# ── DevOps Combos ──────────────────────────────────────────

CODE_REVIEW_DEPLOY = ComboChain(
    name="code-review-deploy",
    description="Review code quality, then commit and push via git",
    steps=[
        ComboStep(skill_name="code-review", params={}),
        ComboStep(skill_name="git-ops", params={"action": "commit"}, use_prev_output=True),
    ],
    tags=["code", "deploy", "git"],
)

SYSTEM_HEALTH_CHECK = ComboChain(
    name="system-health-check",
    description="Check system info and analyze for issues",
    steps=[
        ComboStep(skill_name="system-info", params={}),
        ComboStep(skill_name="data-analyzer", use_prev_output=True),
    ],
    tags=["system", "health", "monitor"],
)

# ── Communication Combos ───────────────────────────────────

NEWS_DIGEST = ComboChain(
    name="news-digest",
    description="Search news, summarize, and send via email/telegram",
    steps=[
        ComboStep(skill_name="news-search", params={}),
        ComboStep(skill_name="deep-research", use_prev_output=True),
        ComboStep(skill_name="note-taker", params={"action": "save"}, use_prev_output=True),
    ],
    tags=["news", "digest", "summary"],
)

SCRAPE_AND_ANALYZE = ComboChain(
    name="scrape-and-analyze",
    description="Browse a URL, scrape content, and analyze data",
    steps=[
        ComboStep(skill_name="web-browse", params={}),
        ComboStep(skill_name="web-scrape", use_prev_output=True),
        ComboStep(skill_name="data-analyzer", use_prev_output=True),
    ],
    tags=["scrape", "analyze", "data"],
)

# ── AI Combos ──────────────────────────────────────────────

SELF_DIAGNOSTIC = ComboChain(
    name="self-diagnostic",
    description="Run self-improvement analysis on all skills",
    steps=[
        ComboStep(skill_name="self-improve", params={"focus": "all"}),
        ComboStep(skill_name="note-taker", params={"action": "save", "title": "Self-Diagnostic Report"}, use_prev_output=True),
    ],
    tags=["self", "diagnostic", "improve"],
)

MEMORY_RESEARCH = ComboChain(
    name="memory-research",
    description="Query memory then supplement with web research",
    steps=[
        ComboStep(skill_name="memory-query", params={}),
        ComboStep(skill_name="web-search", use_prev_output=True),
        ComboStep(skill_name="deep-research", use_prev_output=True),
    ],
    tags=["memory", "research", "recall"],
)

# ── All Templates ──────────────────────────────────────────

ALL_COMBOS = [
    RESEARCH_AND_WRITE,
    ACADEMIC_DIVE,
    CODE_REVIEW_DEPLOY,
    SYSTEM_HEALTH_CHECK,
    NEWS_DIGEST,
    SCRAPE_AND_ANALYZE,
    SELF_DIAGNOSTIC,
    MEMORY_RESEARCH,
]
