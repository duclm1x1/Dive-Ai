# Add Skill & Develop (Skill Authoring + Integration Playbook)

> **Keywords for routing/index**: add skill, develop skill, skill authoring, skill integration, skill router, skill index, skills_reindex, automap, triggers, tags, kind, registry, discovery, dedup, group_id, skills.lock.json, external skills, audit, governance

## Mục tiêu
Chuẩn hoá vòng đời Skill trong **Dive Coder v14** để thêm skill *thông minh – bài bản – có kiểm soát*, tránh:
- trùng lặp/skill spam
- skill không được router chọn (routing dead)
- skill external thay đổi không kiểm soát (lack of pin/lock)
- skill không có chuẩn đầu ra (khó dùng, khó test)

## Khi nào dùng skill này
Dùng khi bạn muốn:
- thêm 1 skill mới vào `.agent/skills` hoặc `.agent/skills_external`
- audit/merge các skill hiện có
- chuẩn hoá template nội dung skill
- tạo phương án triển khai (manual/CLI/workflow/registry-first)

Không dùng nếu:
- chỉ cần 1 mẹo ngắn (hãy bổ sung vào skill liên quan)
- task là one-off và không lặp lại

## Sự thật kiến trúc (Dive Coder v14)
- Skill = file Markdown trong `.agent/skills/*.md` (internal) hoặc `.agent/skills/*.md` (external dạng `ext-*`)
- Skill được **index** và **route** thông qua core skill index/router; automap được sinh bởi `tools/skills_reindex.py`.
- Router thường chọn dựa trên: keywords, tags/kind inferred, và ngữ cảnh task.

## Input contract (bạn cần cung cấp)
Khi tạo skill mới, bạn phải cung cấp tối thiểu:
1) **Tên skill** (skill_id = tên file) theo convention
2) **Mục tiêu** và **use-cases** (khi nào dùng/không dùng)
3) **Input required** (user cần đưa gì)
4) **Output rules** (format output bắt buộc)
5) **Process** (các bước triển khai)
6) **Quality gates** (test/lint/security/docs)
7) **Examples** (2–3 prompt mẫu)

## Quy trình thêm skill thông minh (Smart + Systematic)

### Step 0 — Naming (đặt tên đúng để router hiểu)
**Internal**: `vibe-<domain>-<capability>.md`
- Ví dụ: `vibe-add-skill-develop.md`, `vibe-playwright-e2e.md`

**External**: `ext-<source>-<topic>.md`
- Ví dụ: `ext-vercel-add-skill.md`

Tránh tên chung chung: `helper.md`, `misc.md`.

### Step 1 — Anti-duplicate check (check đã có chưa)
Checklist bắt buộc:
- [ ] Search theo **file name** trong `.agent/skills`
- [ ] Search theo **Title** (`# ...`) và keyword chính
- [ ] Search theo **domain keywords** (react/testing/security/docs/ci/devtools/spec/...)
- [ ] Nếu có link repo: kiểm tra có skill nào cùng repo (dedup theo `group_id`)

Quy tắc quyết định:
- Trùng 60–80% → **merge/update skill cũ**
- Khác trigger hoặc khác output contract → **tạo skill mới**

### Step 2 — Design skill theo chuẩn (để “dùng được”)
Một skill tốt phải có:
- Why/Value: tại sao đáng tồn tại
- When to use / When NOT to use
- Inputs required (ask user nếu thiếu)
- Output rules (format + constraints)
- Procedure (step-by-step)
- Quality gates
- Examples

### Step 3 — Tối ưu để router tự chọn (routing correctness)
Trong nội dung skill, hãy cố tình include keyword để automap infer đúng:
- `testing`, `playwright`, `unit test`, `integration test` → **category: testing**
- `docs`, `readme`, `ADR` → **category: docs**
- `security`, `semgrep`, `secret scan` → **category: security**
- `spec`, `api`, `sdk` → **category: spec**
- `cli`, `npx`, `command` → **kind: cli**
- `registry`, `discovery` → **kind: registry** (chỉ auto khi discovery)

### Step 4 — External skill pin/lock (khi dùng enforce_lock)
Nếu skill nằm trong external pack và bạn bật enforce lock:
- Add entry vào `skills.lock.json` (hoặc `.vibe/skills.lock.json` tuỳ project)
- Mỗi entry nên có:
  - `path` (đường dẫn file skill)
  - `source_repo`
  - `source_commit` (pin theo commit)
  - `sha256` (hash content)

### Step 5 — Reindex (bắt buộc sau khi add/merge)
Chạy `tools/skills_reindex.py` để regen:
- automap (routing map)
- rule-skill map (nếu có)
- audit report

### Step 6 — Verify (Regression-safe)
Definition of Done (DoD):
- [ ] skill được index
- [ ] router chọn skill trong đúng scenario
- [ ] skill không gây spam (dedup/group)
- [ ] external lock không bị vi phạm (nếu bật)

## Output rules (khi skill này được gọi)
Khi user yêu cầu “thêm skill”, output phải luôn có 5 phần:
1) **Existing-skill check**: liệt kê skill gần giống nhất + kết luận merge vs new
2) **Skill spec**: name, purpose, triggers/tags/kind dự kiến
3) **Implementation plan**: file path + nội dung khung + checklists
4) **Index/Lock steps**: reindex + (nếu external) update lock
5) **Verification**: cách test routing + smoke check

## Template skill (copy/paste)
Dùng khung này cho mọi skill mới:

### Why this is useful
### When to use / When NOT to use
### Inputs required
### Output rules
### Procedure
### Quality gates
### Examples

## Examples
- “Thêm skill để tạo Playwright E2E tests cho Next.js app (CI ready)”
- “Audit tất cả skill hiện có, merge skill trùng, regen automap”
- “Tạo skill cho security secret scanning + pre-commit hooks”
