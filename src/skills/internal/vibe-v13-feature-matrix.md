# Vibe Coder v13.0 Feature Matrix (Antigravity Enterprise)

> Thang điểm: **0–100** (càng cao càng “cần phải có” để dùng tốt trong Antigravity).
> Rule: **>=80** => coi như “bắt buộc có” trong mainline v13 (enterprise posture).
>
> Ghi chú quan trọng (truth-in-advertising):
> - `advanced_searching/api.py` trong v13 **đã nâng cấp** lên **pointer registry + facets + hints**, không còn chỉ “facet catalog + locate substring”.
> - `rag/engine.py` vẫn là **metadata ingestion + query placeholder** (embedding/vector retrieval chưa implement thực sự).

| # | Feature | Confidence | Included in v13 | Where / How to use |
|---:|---|---:|---|---|
| 1 | Repo-level review (scan nhiều file, aggregate report) | 95 | ✅ | `.shared/vibe-coder-v13/core/orchestrator.py` (`review`) |
| 2 | Diff/PR mode (review files changed bằng git diff) | 90 | ✅ | `review --diff-base`, workflows `/vibe-pr` |
| 3 | Stack detection (Next/Nest/Tailwind/Python) | 90 | ✅ | `.shared/vibe-coder-v13/core/stack_detector.py` |
| 4 | Plugin system (stack-specific gates defaults) | 88 | ✅ | `.shared/vibe-coder-v13/plugins/*` |
| 5 | Gates runner (lint/test/build) | 92 | ✅ | `.shared/vibe-coder-v13/gates/runner.py` + `review --run-gates` |
| 6 | Policy & permissions (shell/write/autofix allowlist) | 92 | ✅ | `.shared/vibe-coder-v13/utils/policy.py` |
| 7 | Cache v2 (content-hash cache per file) | 85 | ✅ | `.shared/vibe-coder-v13/core/cache.py` |
| 8 | Custom rule engine (regex rule packs, hot reload) | 85 | ✅ | `.shared/vibe-coder-v13/core/rules_engine.py` + `rules/custom/*.json` |
| 9 | Python AST analyzer (bug/security/docs/complexity heuristics) | 90 | ✅ | `.shared/vibe-coder-v13/core/python_ast.py` |
| 10 | Evidence anchors (file/line/snippet_hash) | 90 | ✅ | `core/models.py` (`Evidence`) |
| 11 | Confidence scoring (per finding) | 85 | ✅ | `Finding.confidence` + rule defs |
| 12 | Finding taxonomy (category + CWE mapping where possible) | 82 | ✅ | `Finding.category`, `Finding.cwe` |
| 13 | Action Plan (prioritize severity + confidence) | 85 | ✅ | `core/orchestrator.py::_action_plan` |
| 14 | Deterministic run manifest (hashes + tool versions) | 88 | ✅ | `core/models.py::RunManifest` |
| 15 | External tools integration (ruff/bandit/semgrep nếu có) | 90 | ✅ | `core/external_tools.py` |
| 16 | Baseline & regression (chỉ show new findings) | 88 | ✅ | `baseline set/compare` |
| 17 | SARIF export (CI/Security tooling) | 85 | ✅ | `exporters/sarif.py` + `vibe sarif` |
| 18 | Docs-as-code (markdown report) | 85 | ✅ | `exporters/markdown.py` |
| 19 | Autopatch (safe patches) | 82 | ✅ | `patch/autopatch.py` + `vibe autopatch` |
| 20 | Observability / traces (span durations) | 80 | ✅ | `utils/tracing.py` + `Report.traces` |
| 21 | Dependency graph / repo import mapping (impact reasoning) | 85 | ✅ | `.shared/vibe-coder-v13/dag/*` + orchestrator import scan |
| 22 | Advanced Searching v13 (pointer registry + facets + hints) | 90 | ✅ | `.shared/vibe-coder-v13/advanced_searching/api.py` + `vibe v13-search ...` |
| 23 | Advanced Searching v12 (SQLite FTS + hybrid search) | 92 | ✅ | `.shared/vibe-coder-v13/index/*` + `search/*` + `vibe search` |
| 24 | V13 Advanced RAG (ingest OK, query placeholder) | 70 | ⚠️ partial | `.shared/vibe-coder-v13/rag/engine.py` + `vibe v13-rag` |
| 25 | Init / Preflight pipeline + REQUIRED INPUT templates | 85 | ✅ | `.shared/vibe-coder-v13/builder/specs.py` + `builder/scaffold.py` |
| 26 | Hook / Commands system (minimal, enterprise-safe) | 82 | ✅ | `.shared/vibe-coder-v13/core/hooks.py` + `hooks-*` commands |
| 27 | IKO lifecycle (issue objects) | 85 | ✅ | `.shared/vibe-coder-v13/iko/*` + `iko-*` CLI |
| 28 | EvidencePack collector (audit bundle) | 85 | ✅ | `.shared/vibe-coder-v13/evidencepack/*` |
| 29 | Gatekeeper transitions (governance state) | 82 | ✅ | `.shared/vibe-coder-v13/gatekeeper/*` |
| 30 | Debate runtime (structured pros/cons synthesis) | 80 | ✅ | `.shared/vibe-coder-v13/debate/*` |
| 31 | Super-Coder Skills (SOLID/DRY/Clean Code contract) | 95 | ✅ | `.agent/skills/vibe-super-coder-skills.md` |
| 32 | Tech-stack specifics (Next/Nest/Tailwind defaults) | 90 | ✅ | `.agent/skills/vibe-tech-stack-modern-web.md` |
| 33 | QA & Debugging automation playbook | 88 | ✅ | `.agent/skills/vibe-qa-debugging.md` |
| 34 | Documentation Auto playbook | 85 | ✅ | `.agent/skills/vibe-documentation-auto.md` |
| 35 | Design Intelligence (UI + a11y checklist) | 82 | ✅ | `.agent/skills/vibe-design-intelligence.md` |
| 36 | AgentScope BaseSkill (multi-agent orchestration reference) | 85 | ✅ | `.agent/skills/vibe-agent-scope.md` |
| 37 | Cache-Design BaseSkill (freshness, stampede, hot-key, circuit breakers) | 90 | ✅ | .agent/skills/vibe-cache-design.md |
| 37 | cache-design (cache architecture: TTL/SWR/events, stampede, hot keys, CB) | 85 | ✅ | .agent/skills/vibe-cache-design.md |

---

## AgentScope ↔ Vibe Coder: 3 integration patterns (recommended)

### Pattern 1 — AgentScope orchestrates, Vibe là specialist tool
**Khi dùng:** bạn muốn AgentScope điều phối nhiều agent role (Planner/Reviewer/Executor), còn Vibe cung cấp “repo brain” (search/review/gates).  
**Cách làm nhanh:** expose Vibe qua CLI wrapper hoặc Python module, AgentScope agents gọi:
- `vibe v13-search index` / `locate` / `pointer`
- `vibe review --run-gates`
- `vibe sarif` / `baseline compare`

### Pattern 2 — Treat Vibe skills như AgentScope skill pack
**Khi dùng:** bạn muốn “Vibe rules/skills” trở thành **skill library** cho AgentScope.  
**Cách làm:** import/copy `.agent/skills/*.md` và map vào AgentScope skill registry (skill_name → trigger → tool calls).  
**Benefit:** AgentScope agents có “guardrails” và playbooks chuẩn enterprise.

### Pattern 3 — MCP boundary: expose Vibe operations thành MCP tools để AgentScope gọi
**Khi dùng:** bạn cần tách layer rõ ràng (security/audit) và muốn AgentScope gọi tools theo chuẩn MCP.  
**Cách làm:** dựng MCP server “Vibe Tools” cung cấp:
- `vibe.search.locate`
- `vibe.search.pointer`
- `vibe.review.run`
- `vibe.report.export_sarif`
- `vibe.baseline.compare`

---

## Query cookbook (v13-search)

- Tìm symbol:
  - `vibe v13-search locate --query "symbol:Orchestrator"`
- Filter theo kind:
  - `vibe v13-search locate --query "kind:function path:core"`
- Xem facets:
  - `vibe v13-search facets`
- Gợi ý query:
  - `vibe v13-search hints --query "orchestratr"`
- Resolve pointer:
  - `vibe v13-search pointer --id <pointer_id>`
