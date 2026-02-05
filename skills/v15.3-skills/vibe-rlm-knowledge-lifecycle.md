# vibe- RLM + Knowledge lifecycle

> **BASE SKILL (always-on)** — dùng cho cả **Vibe Coder** và **Cruel System**.
>
> Mục tiêu: thay vì “nhét dữ liệu vào context”, luôn ưu tiên **query dữ liệu nằm ngoài model** bằng **code execution + recursion**,
> đồng thời quản trị vòng đời tri thức (knowledge lifecycle) để **nhanh, đúng, có bằng chứng, và có giới hạn chi phí**.

---

## 0) Mental model

- LLM **không phải bộ nhớ**. LLM là **planner + coordinator**.
- “Memory” thực chất là: **khả năng truy vấn đúng** (exactness-first) với **chi phí chấp nhận được**.
- RLM = **đệ quy + code execution**:
  - Root call: lập kế hoạch + viết code để *peek* vào kho dữ liệu.
  - Sub-calls: thu hẹp scope theo manh mối, giải từng lớp, dừng đúng lúc.

> Nguyên tắc: **Always reduce scope**. Không scan tất cả nếu chưa ước lượng chi phí.

---

## 1) Khi nào bắt buộc dùng skill này

### Always-on (baseline)
- Repo lớn, log dài, workflow JSON lớn, hoặc user hỏi “tìm chi tiết rất nhỏ”.
- Khi cần **exact match** (ID, key, edge-case, schema rule, line-level evidence).
- Khi cần **triage nhanh**: ước lượng cost trước khi đào sâu.

### Typical triggers
- `knowledge`, `rag`, `rlm`, `recursive`, `retrieval`, `index`, `cache`, `vector`, `bm25`, `regex`, `scan`, `log`, `workflow`, `n8n`.

---

## 2) Execution environment contract (sandbox)

**Environment must provide:**
- `store`: file-backed corpus (codebase/logs/workflows) — không nằm trong prompt.
- `tools` (no network by default):
  - `fs`: list/read files (bounded)
  - `search`: lexical (regex/string), BM25/FTS, optional vector
  - `index`: build/update incremental index
  - `cache`: query cache by hash(scope+query+code)
  - `cost`: estimate scan cost (bytes, IO, recursion fanout)
  - `trace`: record code executed + evidence

**Hard limits (enterprise defaults):**
- `max_depth` (recursion): 3–6
- `max_bytes_scanned`: configurable per task
- `max_cpu_ms` / `max_wall_ms`
- `max_subcalls`
- `no_network = true` (unless policy enables KB update)

---

## 3) Query protocol (RLM loop)

### Step A — Plan
1) Define **question** → convert thành **query spec**:
   - exact keys/IDs/regex patterns
   - file scopes (folders, extensions)
   - schema/constraints
2) Run **cost estimation**:
   - predicted bytes scanned
   - predicted candidate set size
   - index availability (hit/miss)
3) Choose strategy:
   - if cost high → build index first / narrow scope
   - if exact match needed → lexical first, vector only for recall

### Step B — Execute (code)
- Execute minimal code that returns **small observation**:
  - list of candidate files/spans
  - snippet hashes + line ranges
  - structured rows (JSONL/CSV)
- Never return whole documents to model.

### Step C — Recurse (narrow)
- For each candidate span:
  - subcall with **smaller scope + clearer target**
  - verify hypotheses, reject false positives
- Stop when:
  - evidence satisfies constraints, hoặc
  - budget hit (then return best-effort + next actions)

### Step D — Synthesize (evidence-first)
Output must include:
- What was executed (high-level)
- Evidence references: file paths + line ranges + matched tokens/ids
- Confidence + stop reason + remaining uncertainty

---

## 4) Knowledge lifecycle (the “K” in RLM+K)

## 4A) Governance: IKO / EvidencePack / Gatekeeper (production workflow)

### Key axioms
- **IKO is the Single Source of Truth** for each issue.
  - Path: `.vibe/iko/<IKO_ID>.json`
  - Contains: `state`, evidence packs, investigations, and audit trail.
- **EvidencePack pipeline** is automatic from **CI/CD and/or Canary**.
  - Path: `.vibe/evidence/<EVIDENCEPACK_ID>.evidencepack.json`
  - EvidencePack is *pointers + checksums*, not a data dump.
- **Gatekeeper is the only component allowed to transition state.**
  - Gatekeeper validates allowed transitions and requires EvidencePack for “serious” transitions.
- **RLM is the investigator + verifier** (đội điều tra + verify).
  - RLM attaches investigations and evidence pointers.
  - RLM does **not** decide “done”.

### Folder baseline
- `.vibe/iko/` (IKOs)
- `.vibe/iko/investigations/` (RLM outputs)
- `.vibe/evidence/` (EvidencePacks)

### Minimal commands
```bash
# Create IKO
python3 .shared/vibe-coder-v13/vibe.py iko-new --repo . --id IKO-123 --title "..." --description "..."

# Investigate (RLM attaches investigation; no state change)
python3 .shared/vibe-coder-v13/vibe.py investigate --repo . --issue-id IKO-123 --question "..."

# CI evidencepack
python3 .shared/vibe-coder-v13/vibe.py evidencepack --repo . --issue-id IKO-123 --outdir .vibe/evidence

# Gatekeeper transition (only place that changes state)
python3 .shared/vibe-coder-v13/vibe.py gatekeeper --repo . --issue-id IKO-123 --to EVIDENCE_READY --actor gatekeeper --evidencepack .vibe/evidence/<pack>.evidencepack.json
```


### States
1) **Ingest**: (optional) pull external knowledge (GitHub/Reddit/docs) → policy gated  
2) **Normalize**: strip secrets/PII, canonicalize formats, chunking
3) **Index**:
   - FTS/BM25 for exactness
   - Trigram/suffix/prefix accelerators
   - Optional vector for semantic recall
4) **Cache**:
   - query cache (hash(query+scope+version))
   - hot-path cache (top files/spans)
5) **Validate / Drift**:
   - schema validation
   - regression baseline: only diffs/regressions
6) **Evict**:
   - TTL / LRU
   - invalidate on repo change (git hash) or KB version bump
7) **Provenance**:
   - each fact must have source pointer (file/url + commit + timestamp)

### Enterprise rules
- Default **no network**. KB update requires explicit policy allow.
- Always sanitize credentials (workflow JSON / env files) before storing.

---

## 5) Engineering retrieval recipes

### Codebase
- Prefer:
  - `ripgrep`-style lexical scan → then AST/structured parse for precision.
- Use index if:
  - repeated queries, or repo > N files.

### Logs
- Use:
  - regex prefilter + time-window narrowing
  - histogram sample before full scan (cost control)

### n8n workflows
- Validate JSON schema first, then run best-practice rules:
  - missing retries/error branch
  - credential misuse
  - concurrency / idempotency
  - timeouts / rate-limit
- Always sanitize credential names → placeholders.

---

## 6) Failure modes & mitigations

- **False recall from vectors** → always confirm with lexical/evidence.
- **Over-scanning** → enforce budget + cost estimation gates.
- **Recursive explosion** → cap fanout + choose “top-k candidates”.
- **Tool drift** → pin external skills/KB via lock (repo+commit+checksum).
- **Security** → never execute untrusted code; sandbox strictly.

---

## 7) Minimal output checklist (must pass)

- [ ] Có query plan + cost estimate (even rough).
- [ ] Có code-execution trace (what tools ran).
- [ ] Có evidence pointers (paths/lines/ids).
- [ ] Có stop reason + next actions.
