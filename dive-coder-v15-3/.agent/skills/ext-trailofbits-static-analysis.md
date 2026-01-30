# Trail of Bits: static-analysis

**Repo:** https://github.com/trailofbits/static-analysis

**Type:** tooling

## Why this is useful
Practical guidance/tools for static analysis pipelines.

## How to integrate with Antigravity + Vibe
Use as reference for enterprise static analysis design + SARIF practices.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
