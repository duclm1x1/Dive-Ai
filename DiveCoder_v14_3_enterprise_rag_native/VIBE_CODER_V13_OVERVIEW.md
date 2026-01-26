# Vibe Coder v13.0 — Antigravity Enterprise

## Tổng quan
Vibe Coder v13.0 là phiên bản **mainline** cho Antigravity Enterprise, tập trung vào 3 trụ cột:
1) **Repo Intelligence** (advanced_searching + dependency reasoning)
2) **Governance** (quality gates + semgrep/SARIF + self-review)
3) **Extensibility** (skills, hooks, external integrations)

> Ghi chú: v12.12.3 là **legacy fallback**; v13.0 là nền chính. Nếu thiếu module nhỏ, mới backfill từ v12.12.3.

---

## 1. Thành phần chính

### 1.1 Advanced Searching
Module `advanced_searching/` hướng tới thay thế grep/regex bằng search dựa trên **cấu trúc repo**:
- indexing (files/symbols)
- locate (span chính xác)
- facets (lọc theo loại thực thể)
- hints (gợi ý truy vấn)
- pointer registry (symbol → location → context)

### 1.2 Advanced RAG
RAG dùng để lấy context đa nguồn (repo + docs + specs) nhằm hỗ trợ:
- refactor lớn
- kiến trúc
- review phức tạp

### 1.3 CLI & Pipeline
`vibe.py` là entrypoint cho workflow:
- init/preflight
- search/locate
- review + gates
- self-review artifacts

### 1.4 Hooks / Commands
Hook system (mức vừa đủ) để mở rộng workflow mà không phá Antigravity:
- pre-command
- post-command
- custom commands

### 1.5 Quality Gates & Semgrep
- phát hiện cấu hình semgrep mặc định
- `.semgrep/vibe.yml`
- SARIF output cho CI / code scanning

---

## 2. Base Skills (core stack)
Vibe v13.0 vận hành dựa trên hệ skill markdown trong `.agent/skills/`.

### Bổ sung: Agent Scope (AgentScope)
Thêm base-skill **Agent Scope** để chuẩn hoá “multi-agent thinking”:
- AgentScope là framework multi-agent (Python) hỗ trợ ReAct agents, memory, planning, RAG, MCP/A2A, hooks…
- Gợi ý dùng AgentScope làm **orchestrator runtime**, còn Vibe làm **repo brain + governance**.

File skill note: `.agent/skills/vibe-agent-scope.md`

---

## 3. Artifacts
- `vibe_coder_v13.0_antigravity_enterprise.zip`
- `vibe_coder_v13.0_self_review.json`
- `vibe_coder_v13.0_self_review.md`
- `vibe_coder_v13.0_self_review.sarif.json`
- `VIBE_CODER_V13_OVERVIEW.md` (tài liệu tổng quan)


---

## Strategic improvements (Speed + Accuracy + Governance)

### 1) Incremental indexing + hash cache (Speed x10)
Implemented:
- SQLite FTS index now **skips unchanged files** via `(mtime,size)` fast-path and stores `content_hash`.
- Vector index updates **only changed/new files** (instead of re-embedding everything).
- AdvancedSearch pointer registry reuses cached per-file facets + pointers when unchanged.

Where:
- `.shared/vibe-coder-v13/index/db.py`
- `.shared/vibe-coder-v13/index/indexer.py`
- `.shared/vibe-coder-v13/advanced_searching/api.py`

### 2) Hybrid retrieval + reranker + grounding (Accuracy)
Implemented:
- `vibe.py search --mode v13` merges:
  - pointer hits (symbol-aware)
  - FTS hits (keyword)
  - vector hits (offline hashing embeddings)
- Reranker boosts exact/near symbol matches + path proximity.
- Grounding always returns `{path, start_line, end_line, snippet}` when possible.

Where:
- `.shared/vibe-coder-v13/search/hybrid.py`
- `.shared/vibe-coder-v13/search/semantic.py` (mode `v13`)

### 3) Repo graph + test selection (Speed + Debug accuracy)
Implemented:
- Best-effort import graph for Python + JS/TS.
- Impact-based test selection: `vibe.py select-tests --diff-base <ref>` (or `--changed`).

Where:
- `.shared/vibe-coder-v13/graph/import_graph.py`
- `.shared/vibe-coder-v13/graph/test_selection.py`
- `vibe.py` command: `select-tests`

### 4) Claims ledger + CI artifact validator (Zero governance theater)
Implemented:
- Claims ledger records machine-verifiable claims with evidence levels and artifact hashes.
- CI validator checks EvidencePack artifacts exist and hashes match.

Where:
- `.shared/vibe-coder-v13/core/claims.py`
- `.shared/vibe-coder-v13/tools/ci/validate_evidencepack.py`

### 5) Learning loop + eval harness (Gets stronger with use)
Implemented:
- Append-only run telemetry: `.vibe/learning/events.jsonl`
- Minimal eval harness for retrieval correctness.

Where:
- `.shared/vibe-coder-v13/learning/store.py`
- `examples/v13_eval_harness/run_eval.py`


## A–Z Flows (New in this build)

- `doctor`: repo readiness (templates/spec/tools/index/baseline)
- `explain`: grounded answers (hybrid retrieval -> pointers/snippets)
- `fix`: bugfix investigation bundle + optional pytest verification + claims ledger (+ EvidencePack when --full)
- `graph-build`/`graph-impact`: incremental import-graph store + impact computation

