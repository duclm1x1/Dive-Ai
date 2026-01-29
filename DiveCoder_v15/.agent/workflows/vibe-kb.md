# /vibe-kb

Update the local knowledge base (network is policy-gated).

Examples:
```bash
python3 .shared/vibe-coder-v13/vibe.py kb-update --repo . --source github --repo-name vercel-labs/agent-skills --ref main --paths skills/react-best-practices/SKILL.md
```

```bash
python3 .shared/vibe-coder-v13/vibe.py kb-update --repo . --source reddit --subreddit reactjs --query "best practices" --limit 25
```

After update, re-run `/vibe-index` to index the KB.
