# Trail of Bits: differential-review

**Repo:** https://github.com/trailofbits/differential-review

**Type:** security-workflow

## Why this is useful
Security-focused differential review; aligns with PR-mode scanning.

## How to integrate with Antigravity + Vibe
Integrate ideas into Vibe diff mode to surface high-risk changes.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
