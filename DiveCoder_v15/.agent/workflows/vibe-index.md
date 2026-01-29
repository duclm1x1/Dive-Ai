# /vibe-index

Build or refresh the repo index for fast retrieval.

Run:
```bash
python3 .shared/vibe-coder-v13/vibe.py index-build --repo . --vec-dim 256 --out .vibe/reports/vibe-index.json
```

Notes:
- Uses SQLite FTS for keyword search and a lightweight offline vector index.
- Output is deterministic and stored under `.vibe/index/`.
