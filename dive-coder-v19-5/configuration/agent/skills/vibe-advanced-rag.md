# Vibe Advanced RAG 2025 (SOTA Playbook)

Mục tiêu: Nâng cấp năng lực **Retrieval-Augmented Generation (RAG)** của Dive Coder theo các kỹ thuật thực chiến mạnh nhất (đến 2025), giúp **tăng độ đúng**, **giảm hallucination**, **tối ưu latency/cost**, và **minh bạch hoá nguồn**.

---

## Khi nào dùng
Dùng skill này khi bạn cần:
- Xây/upgrade pipeline RAG (Q&A nội bộ, assistant cho repo/docs, search+answer).
- Tăng **faithfulness** (có trích dẫn, bám nguồn), giảm trả lời bừa.
- Truy vấn phức tạp: multi-hop, multi-doc, có filter metadata, có data có cấu trúc.
- Cần chiến lược **adaptive retrieval** (tuỳ câu hỏi chọn phương pháp).

Không dùng skill này khi:
- Nhiệm vụ chỉ cần LLM reasoning *không phụ thuộc kiến thức ngoài*.
- Corpus rất nhỏ (<= vài trang) → nhét thẳng vào context hoặc summary.

---

## Input cần có (contract)
1) **Use-case**: chatbot Q&A, code assistant, compliance/legal, customer support, analytics, …
2) **Corpus & nguồn**: file types (pdf/md/html), repo/docs, DB (SQL), graph, images.
3) **Ràng buộc**: latency (p95), cost, offline/online, quyền truy cập, PII.
4) **Kết quả mong muốn**: format câu trả lời (có citation? có JSON?), tone.
5) **Bộ test/eval** (tối thiểu 30–100 queries): ground truth hoặc rubric.

Nếu thiếu (5), phải tạo **evaluation set** trước khi tối ưu.

---

## Output rules (bắt buộc)
Khi áp dụng skill này, phải xuất ra:
1) **RAG Blueprint** (kiến trúc + luồng dữ liệu) theo các khối: Query → Routing → Indexing → Retrieval → Rerank/Refine → Generation → Eval/Monitor.
2) **Implementation plan** dạng checklist + task A–Z (có ưu tiên P0/P1/P2).
3) **Ablation matrix**: ít nhất 6 thí nghiệm so sánh (baseline vs upgrade).
4) **Evaluation plan**: metric + cách chấm + logging.
5) **Failure modes & mitigations**: sai retrieval, thiếu coverage, spam chunk, long-doc, multi-hop.

---

## Taxonomy kỹ thuật RAG hiện đại (2025)

### A) Foundational RAG
1. **Simple RAG**: retrieve → answer.
2. **CSV RAG**: embed row-wise + Q&A.
3. **Reliable RAG**: validation/refinement + highlight evidence.
4. **Chunk size tuning**: chọn chunk theo domain + latency.
5. **Proposition chunking**: tách thành factual sentences → cực hợp pháp lý/báo cáo.

### B) Query enhancement (tối ưu truy vấn)
6. **Query transformations**: rewrite, step-back, decomposition.
7. **HyDE**: sinh hypothetical doc rồi embed để tăng match.
8. **HyPE**: precompute hypothetical prompts → giảm chi phí online.
9. **Self-query retriever**: tự sinh filter metadata (type, time, owner, tag…)
10. **Text-to-SQL / Text-to-Cypher**: query DB quan hệ / graph bằng NL.

### C) Context & content enrichment (làm giàu ngữ cảnh)
11. **Contextual chunk headers**: thêm title/section breadcrumbs.
12. **Relevant Segment Extraction (RSE)**: ghép nhiều chunk thành đoạn dài liên quan.
13. **Semantic chunking**: cắt theo ngữ nghĩa thay vì fixed length.
14. **Contextual compression**: nén chunk bằng LLM (giữ facts).
15. **Doc augmentation (QGen)**: sinh câu hỏi liên quan cho mỗi đoạn.

### D) Advanced retrieval
16. **Fusion retrieval**: hybrid BM25/keyword + vector.
17. **Intelligent reranking**: cross-encoder / LLM-scoring / metadata ranking.
18. **Multi-faceted filtering**: metadata + threshold + diversity.
19. **Hierarchical indices**: summary layer → detail layer.
20. **Ensemble retrieval**: nhiều embedding models/algorithms.
21. **Dartboard retrieval**: tối ưu relevance + diversity đồng thời.
22. **Multi-modal retrieval**: text + caption + image embedding.

### E) Iterative & adaptive RAG
23. **Feedback loops**: học từ đánh giá/user feedback.
24. **Adaptive retrieval**: tự chọn chiến lược theo query.
25. **Iterative retrieval**: nhiều vòng, có follow-up queries.

### F) Evaluation & explainability
26. **DeepEval**: correctness/faithfulness/contextual relevancy.
27. **GroUSE**: chấm final answer theo 6 tiêu chí nền.
28. **Explainable retrieval**: giải thích vì sao chunk được chọn.

### G) Advanced architectures
29. **Agentic RAG**: planner → retrieve → verify → answer (prod-ready).
30. **Graph RAG**: triplets + graph traversal + vector.
31. **Knowledge Graph integration**: dữ liệu cấu trúc + quan hệ.
32. **Microsoft GraphRAG**: community graph cho multi-hop QA.
33. **RAPTOR**: cây tóm tắt nhiều tầng.
34. **Self-RAG / RRR**: model tự quyết định retrieve + tự rewrite.
35. **CRAG**: corrective RAG + fallback (web/new sources) khi retrieval kém.

---

## Breakthrough method (cách chọn chiến lược RAG theo loại câu hỏi)

### 1) Query classifier (nhanh, rẻ)
Phân loại câu hỏi thành 1 trong các nhóm:
- **Factual lookup** (1-hop): cần đúng & cite.
- **Multi-hop / synthesis**: cần nhiều doc + tổng hợp.
- **Structured data**: hỏi số liệu, bảng, quan hệ → SQL/Cypher.
- **Recent/unknown**: corpus có thể thiếu → CRAG + web/new sources.
- **Ambiguous**: cần clarification hoặc step-back.

### 2) Strategy mapping (mặc định an toàn)
- Factual lookup → Fusion retrieval + rerank + highlight evidence.
- Multi-hop → Decomposition + iterative retrieval + hierarchical index.
- Structured data → Text-to-SQL/Cypher + evidence join.
- Recent/unknown → CRAG (re-retrieve + external) + answer verification.
- Ambiguous → Step-back + ask 1–2 clarification questions.

### 3) Guardrails (bắt buộc)
- Nếu **context relevancy < threshold** → không trả lời chắc chắn; hỏi lại hoặc fallback.
- Nếu **không có evidence** → trả lời theo dạng “không đủ dữ liệu trong corpus”.

---

## Playbook triển khai (chuẩn hoá theo pipeline)

### Step 0 — Baseline (bắt buộc)
- Chốt baseline: Simple RAG + chunk fixed + vector search.
- Tạo eval set + logging schema.

### Step 1 — Ingestion & Chunking
- Ưu tiên: **Semantic chunking** + **Contextual headers**.
- Domain legal/report: **Proposition chunking**.
- Long docs: **Parent doc / multi-representation** (summary + chunks).

### Step 2 — Indexing
- Vector index cho chunks + (tuỳ chọn) index cho summaries.
- Nếu multi-hop: **RAPTOR** hoặc hierarchical summaries.
- Multi-modal: caption images + store embeddings.

### Step 3 — Retrieval
- Mặc định: **Fusion retrieval** (keyword + vector).
- Thêm: filters theo metadata (time/type/owner/tag).
- Diversity: MMR/dartboard nếu chunk quá giống nhau.

### Step 4 — Rerank & Refinement
- Rerank topK bằng cross-encoder/LLM-scoring.
- Nếu context dài: **contextual compression** hoặc RSE.
- Nếu relevance thấp: **CRAG** (re-retrieve, đổi nguồn).

### Step 5 — Generation (Grounded)
- Answer bắt buộc bám evidence; cite chunk ids.
- Dùng **Self-RAG / RRR** khi query khó: rewrite → retrieve lại.
- Answer verification: check claims vs evidence (faithfulness gate).

### Step 6 — Evaluation & Monitoring
- Metric core: correctness, faithfulness, context relevancy, latency/cost.
- DeepEval/GroUSE cho regression.
- Log: query → strategy → retrieved ids → rerank scores → citations.

### Step 7 — Feedback loops
- Thu user rating + “this is wrong because …”
- Lưu lỗi theo loại: retrieval miss / chunking bad / rerank fail.

---

## Checklist tối ưu nhanh (P0 trước)
P0 (high impact):
- [ ] Fusion retrieval + rerank
- [ ] Semantic chunking + headers
- [ ] Relevance threshold + refuse/clarify
- [ ] Explainable retrieval (highlight)

P1:
- [ ] Decomposition/step-back
- [ ] Iterative retrieval
- [ ] Contextual compression

P2:
- [ ] RAPTOR / GraphRAG
- [ ] HyDE/HyPE
- [ ] Multi-modal

---

## Ví dụ prompt để dùng skill
1) “Upgrade RAG cho hệ thống docs nội bộ: latency p95 < 800ms, bắt buộc citation, corpus 50k markdown. Hãy đề xuất blueprint + ablation matrix.”
2) “Query có metadata (team, date). Hãy thiết kế self-query retriever + filters + reranker + eval.”
3) “Multi-hop QA trên spec + code. Hãy đề xuất GraphRAG hoặc RAPTOR, cách triển khai và test.”

---

## Nguồn tham khảo (code)
- Nir Diamant — RAG Techniques (full source code): https://github.com/NirDiamant/RAG_Techniques
