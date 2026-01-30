# /vibe-search

Search the repo using the local index.

Run:
```bash
python3 .shared/vibe-coder-v13/vibe.py search --repo . --query "<your query>" --mode hybrid --limit 20
```

Modes:
- `fts`: keyword (fast)
- `vector`: offline semantic-ish (approx)
- `hybrid`: merge
