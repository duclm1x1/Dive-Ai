# Agent Scope (AgentScope)

**Repo:** https://github.com/agentscope-ai/agentscope

**Type:** `multi-agent-framework` (Python)

## What it is
AgentScope là framework Python để xây dựng **hệ thống AI đa tác tử** theo hướng *agent-oriented programming*: nhiều agent, mỗi agent có vai trò riêng, phối hợp qua workflow (conversation / debate / concurrent agents / routing / handoffs) trong một môi trường chung.

## Core capabilities (practical)
- **ReAct-style agent** (Reasoning–Acting) cho loop suy luận → gọi tool → phản hồi.
- **Tools + Agent Skills**: tách “capability” thành module có thể tái sử dụng.
- **Memory / Long-term memory** và quản lý context.
- **RAG / Plan / Pipeline**: các module phục vụ bài toán nhiều bước, nhiều nguồn.
- **Human-in-the-loop**: steering/approval khi cần.
- **MCP + A2A**: tích hợp tool servers và agent-to-agent protocols.
- **Tracing / Evaluation / Tuning**: phục vụ production & cải tiến chất lượng.

## Why this matters for Vibe Coder v13
Vibe Coder v13 mạnh nhất ở **repo intelligence** (advanced_searching + dependency reasoning + quality gates + self-review). AgentScope mạnh ở **multi-agent orchestration**. Kết hợp hai thứ tạo ra kiến trúc:

> AgentScope = “orchestrator runtime”
> 
> Vibe Coder = “repo brain + governance (review/gates/search)”

## Integration patterns (recommended)
### Pattern A — AgentScope orchestrates, Vibe is a specialist
Dựng 3–5 agent role trong AgentScope:
- **Planner/Manager**: chia task, giao việc, tổng hợp kết quả.
- **Locator**: gọi Vibe advanced_searching để index/locate/facets/pointers.
- **Reviewer/Governor**: gọi Vibe review + gates (semgrep/sarif/quality).
- **Patch Executor**: áp patch có kiểm soát (policy + diff discipline).
- (Optional) **Doc Agent**: xuất changelog, overview, release notes.

Khi đó Vibe chạy như một “service/tool” thay vì chỉ là CLI.

### Pattern B — Treat Vibe skills as an AgentScope skill pack
- Import/copy các file skill markdown của Vibe vào skill directory của AgentScope.
- Map skill names → AgentScope Agent Skills.
- Dùng “Vibe rules + QA” như guardrail cho các agent khác.

### Pattern C — MCP boundary for tool execution
Nếu bạn muốn separation rõ ràng:
- expose Vibe operations (search/review/self-review) qua MCP server endpoint
- AgentScope gọi MCP tools để dùng Vibe như một external tool provider

## Operational notes (enterprise)
- Nếu dùng AgentScope Runtime để deploy: ưu tiên chạy Vibe “search/review tools” trong sandbox/CI pipeline, xuất SARIF để integrate với code scanning.
- Tách rõ: **orchestration layer (AgentScope)** vs **governance layer (Vibe)** để dễ audit.

## Suggested “Agent Scope” BaseSkill contract for Vibe
Khi đưa AgentScope thành *base skill* trong Vibe stack, nên coi nó như:
- **Orchestration reference**: chuẩn hoá cách phân vai agent & giao tiếp.
- **Protocol reference**: MCP/A2A integration points.
- **Production posture**: tracing/eval/deploy mindset.


## Pattern mapping to Vibe CLI (practical)
- **Search/Locate**: `vibe v13-search index|locate|pointer|facets|hints`
- **Review + Gates**: `vibe review --run-gates` → `vibe sarif`
- **Regression**: `vibe baseline set` → `vibe baseline compare`
