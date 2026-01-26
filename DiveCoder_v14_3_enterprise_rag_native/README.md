# Vibe Coder v13.0.0 – Antigravity Enterprise Add-on (Breakthrough Edition)

Drop-in add-on để dùng Vibe Coder như **encapsulated logic OS** cho Antigravity.

## Install (copy-in)

1) Copy 2 thư mục này vào **root project** của bạn:

- `.agent/`
- `.shared/`

2) Append vào `.agent/rules/GEMINI.md`:

```md
@vibe-coder-v13.md
```

(Tham khảo `.agent/rules/GEMINI_PATCH.md`).

## Dive Coder packaging policy (folder naming)

- Folder phân phối **luôn** theo tên project + version: ví dụ `dive_coder_v14_state_of_the_art`.
- Mỗi lần update version (v14 → v15), **đổi luôn tên folder** tương ứng.

Lý do: giúp traceable artifacts (reports/claims/evidencepacks/KB) theo version, tránh lẫn lộn.

## Slash commands

- `/vibe-status`
- `/vibe-review`
- `/vibe-pr`
- `/vibe-baseline`
- `/vibe-sarif`
- `/vibe-autopatch`
- `/vibe-golden`
- `/vibe-docs`
- `/vibe-skills`
- `/vibe-build` (Project Builder)
- `/vibe-resolve` (verification loop + patch diff)

## CLI direct

```bash
# Repo-level review (confidence>=80 by default)
python3 .shared/vibe-coder-v13/vibe.py review --repo . --mode balanced --seed 42 \
  --out .vibe/reports/vibe-report.json \
  --md-out docs/vibe-report.md \
  --sarif-out .vibe/reports/vibe-report.sarif.json

# PR / diff review
python3 .shared/vibe-coder-v13/vibe.py review --repo . --diff-base origin/main --mode balanced

# Verification loop (review → resolve engine patch → gates)
python3 .shared/vibe-coder-v13/vibe.py resolve --repo . --run-gates \
  --patch-out .vibe/reports/vibe-resolve.patch \
  --out .vibe/reports/vibe-resolve.json

# Project Builder
python3 .shared/vibe-coder-v13/vibe.py build --kind nextjs --spec ./spec.yml --outdir ./out_app
```

## V13 bootstrap: init / preflight / self-review

Các lệnh này giúp bạn **khởi tạo templates**, **kiểm tra input bắt buộc**, và **tự đánh giá readiness** trước khi chạy pipeline nặng (review/build/resolve).

### 1) v13-init — tạo templates + folders trong `.vibe/`

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-init --repo .
# (optional) chỉ generate vài kind
python3 .shared/vibe-coder-v13/vibe.py v13-init --repo . --kinds '["nextjs","nestjs"]'
```

Output mặc định:
- `.vibe/inputs/v13/*.yml` (templates spec)
- `.vibe/reports/v13_init.json`

### 2) v13-preflight — validate spec trước khi build/agent

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-preflight --repo . --kind nextjs --spec ./spec.yml
```

- Exit code `0` nếu OK, `2` nếu thiếu keys / invalid.
- Output: `.vibe/reports/v13_preflight.json`

### 3) v13-self-review — kiểm tra “repo readiness” (skills/search/templates/gates)

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-self-review --repo . --kind nextjs --spec ./spec.yml   --md-out docs/v13_self_review.md   --sarif-out .vibe/reports/v13_self_review.sarif.json
```

Output mặc định:
- `.vibe/reports/v13_self_review.json`
- (optional) `docs/v13_self_review.md`
- (optional) `.vibe/reports/v13_self_review.sarif.json`

---

## Baseline compare gate (E3) trong build pipeline

`build` đã tích hợp **baseline-init / baseline-compare** như một gate **E3**:

- Nếu baseline **chưa tồn tại**:
  - mặc định sẽ **auto-init** baseline tại: `.vibe/baseline.json` (E3 artifact)
- Nếu baseline **đã tồn tại**:
  - sẽ tạo `.vibe/reports/baseline-compare.json` (E3 artifact)
  - nếu có **new findings** so với baseline ⇒ build **fail** (exit code `3`) trừ khi bạn cho phép.

### Build với baseline mặc định

```bash
python3 .shared/vibe-coder-v13/vibe.py build --kind nextjs --spec ./spec.yml --outdir ./out_app --run-gates
```

### Flags baseline quan trọng

- `--baseline <path>`: đổi baseline path (default: `<outdir>/.vibe/baseline.json`)
- `--require-baseline`: nếu baseline thiếu ⇒ fail (không auto-init)
- `--allow-baseline-regressions`: không fail dù có new findings (vẫn emit compare artifact)

> Lưu ý: build sẽ emit Claims Ledger + EvidencePack (E3) để CI verify.

---

## V13 Advanced Search (`v13-search`) — hybrid, pointer-first

`v13-search` hỗ trợ **locate theo pointer registry** và trả về output có thể copy vào report/PR.

### Actions

- `index`: build search index (khi cần)
- `locate`: tìm theo query
- `facets`: liệt kê facets/symbol kinds
- `hints`: gợi ý query
- `pointer`: lấy detail theo pointer id

### Examples

```bash
# locate symbols/paths
python3 .shared/vibe-coder-v13/vibe.py v13-search --repo . locate --query "AuthService login" --limit 10

# list facets
python3 .shared/vibe-coder-v13/vibe.py v13-search --repo . facets

# pointer detail (accepts --id or --symbol-id)
python3 .shared/vibe-coder-v13/vibe.py v13-search --repo . pointer --id "<POINTER_ID>"
python3 .shared/vibe-coder-v13/vibe.py v13-search --repo . pointer --symbol-id "<POINTER_ID>"
```

Grounding rule:
- Khi trích dẫn code trong review/debug, luôn kèm **file path + start_line–end_line** (pointer output đã có đủ).

---

## V13 Advanced RAG (`v13-rag`) — offline-first retrieval

Dùng để ingest context từ các “sources” do bạn chỉ định (offline), sau đó query.

### Ingest

`sources` là JSON list. Mỗi item có thể là:
- `{ "path": "docs/...", "type": "file" }`
- `{ "path": "src/...", "type": "file" }`

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag --repo . ingest   --sources '[{"type":"file","path":"docs/architecture.md"},{"type":"file","path":"src/auth/service.ts"}]'
```

### Query

```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag --repo . query --prompt "How does auth token refresh work?"
```

Guidelines:
- RAG chỉ là **context amplifier**, không thay thế “search → locate → pointer”.
- Với claim quan trọng (security/behavior), ưu tiên output grounded bằng pointers (E1/E2/E3 tùy nguồn).


## Config

- `vibe.config.yml` (hoặc `.vibe/vibe.config.yml`) để bật/tắt P0/P1 gates.
- `skills.lock.json` để pin external skills (repo + commit + sha256) khi import vào `.agent/skills_external/`.


---

## RLM + Knowledge lifecycle (IKO / EvidencePack / Gatekeeper)

This pack includes a base skill and supporting tooling for **RLM-style engineering retrieval** plus a production governance loop:

- **IKO** (single source of truth per issue): `.vibe/iko/`
- **EvidencePack** (auto from CI/CD/Canary): `.vibe/evidence/`
- **Gatekeeper** (only state transition authority): `vibe gatekeeper`
- **RLM** is investigator/verifier only: `vibe investigate`

See: `docs/RLM_KNOWLEDGE_LIFECYCLE_PIPELINE.md`


## A–Z Flows (V13)

### `vibe doctor`
Checks environment + repo readiness.

```bash
python3 .shared/vibe-coder-v13/vibe.py doctor --repo . --kind nextjs --spec spec.yml
```

### `vibe explain`
Grounded repo explanation using hybrid retrieval (pointers + snippets).

```bash
python3 .shared/vibe-coder-v13/vibe.py explain --repo . --query "How auth refresh works?" --topk 8 --md-out .vibe/reports/explain.md
```

### `vibe fix`
Bugfix flow scaffold + optional verification (pytest only by default). Produces a grounded investigation bundle.

```bash
python3 .shared/vibe-coder-v13/vibe.py fix --repo . --failing-test "tests/test_auth.py::test_login" --stacktrace stack.txt --verify --full
```

### Graph utilities

```bash
python3 .shared/vibe-coder-v13/vibe.py graph-build --repo .
python3 .shared/vibe-coder-v13/vibe.py graph-impact --repo . --changed src/auth.py
```


## Cache-Design base skill (Enterprise)

Run the cache-design skill scaffold + validators:

```bash
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . init
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . validate
```

Artifacts are generated under `.cache/cache-design/` (A–H + ledger + validators report).


## LLM Adapters (Claude / Antigravity / Any LLM)

See `.agent/workflows/vibe-llm-adapters.md` for provider-ready prompt + structured-output guidance.


## Cache-Design (Enterprise Base Skill)

Scaffold artifacts A–H + spec, validate contracts/counts, and emit an E3 bundle.

```bash
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . init
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . validate
python3 .shared/vibe-coder-v13/vibe.py cache-design --repo . report
```

- `validate` loads `.cache/cache-design/spec.yml`, enforces expected TTL/SWR/event-driven counts (if provided), and regenerates Artifact A & D skeletons.
- `report` emits `.cache/cache-design/artifacts/cache_design.evidencepack.json` and `cache_design.claims.json` (E3).


## Template Modes (Prompt → Production-ready)

Ready-to-run mode templates live in `.vibe/templates/modes/`.

- `build-app` — application build/release
- `build-n8n` — n8n workflow A–Z production runbook
- `build` — generic build governance
- `debug` — bug triage → fix → verify
- `website` — marketing website production checklist

Each mode includes:
- `PROMPT.md` (system/first-message template)
- `CHECKLIST.md` (A–Z steps)
- `VERIFY_PLAN.md`
- `SCORECARD.md`



## Mode templates (Prompt → Production bundles)

V13 ships mode templates under `.vibe/templates/modes/<mode>/`.

### List modes
```bash
python3 .shared/vibe-coder-v13/vibe.py mode list --repo .
```

### Apply a mode (create run workspace)
```bash
python3 .shared/vibe-coder-v13/vibe.py mode apply --repo . build-n8n --run-id build-n8n-demo
```

### Run a mode (auto-run preflight + cache-design validators + pack E3)
```bash
python3 .shared/vibe-coder-v13/vibe.py mode run --repo . build-n8n --run-id build-n8n-demo --full \
  --query "What does this workflow do end-to-end?"
```

Outputs (inside `.vibe/runs/<run-id>/`):
- `PROMPT_RENDERED.md` (ready to paste to Claude/Antigravity/any LLM)
- `doctor.json`, `preflight.json` (if kind inferred/provided)
- `mode_run.json`, `mode.claims.json`, `mode.evidencepack.json` (E3 bundle)



## Production Adapters (dense embeddings / rerank) — skeleton (offline-first)

This bundle includes a **provider-based adapter layer** so you can later plug in:
- Dense embeddings (OpenAI / local / other)
- Cross-encoder rerankers
- LLM-judge rerankers

Offline-first behavior:
- Default `dense.provider=stub_hash` and `rerank.provider=stub` (no external calls).
- Core RAG v2 remains dependency-light and works without adapters.

### Files added
- `.shared/vibe-coder-v13/rag/adapters/embedding.py`
- `.shared/vibe-coder-v13/rag/adapters/rerank.py`
- `.shared/vibe-coder-v13/rag/retrieval/dense_index.py`
- `.shared/vibe-coder-v13/rag/retrieval/fusion.py`

### CLI usage
Build KB (+ optional dense index):
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag ingest --repo . --spec .vibe/inputs/v13/rag_spec.yml --dense
```

Query with dense + fusion:
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --dense --fusion rrf --dense-topk 24
```

Rerank (stub by default):
```bash
python3 .shared/vibe-coder-v13/vibe.py v13-rag query --repo . --spec .vibe/inputs/v13/rag_spec.yml \
  --prompt "..." --rerank --rerank-provider stub
```

### Folder naming policy
Whenever you bump a significant version/feature set, **rename the project root folder**.
This bundle root is:
`dive_coder_v14_graphrag_raptor_crag_offline_preset1_adapters`
