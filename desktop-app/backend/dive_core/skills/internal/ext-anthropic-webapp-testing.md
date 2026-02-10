# Anthropic: webapp-testing

**Repo:** https://github.com/anthropics/webapp-testing

**Type:** testing-skill

## Why this is useful
Playwright-centric testing workflows; helps enterprise QA automation.

## How to integrate with Antigravity + Vibe
Port steps into /vibe-test and /vibe-debug workflows.

## Recommended usage pattern
- Treat this as an **optional skill module**.
- If it introduces lint/test/security outputs, wire it into Vibe **Gates** and export **SARIF/Markdown**.
