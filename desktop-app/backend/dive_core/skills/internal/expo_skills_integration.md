# expo/skills (external skill pack integration)

Expo maintains an official skill pack with plugins such as `expo-app-design`, `upgrading-expo`, and `expo-deployment`.

## Use in Dive Coder
- Treat as an **external skill source** you can import into Dive Coder’s skill registry.
- Recommended: vendor the skills into `.agent/skills/external/expo_skills/` for determinism.

## Installation patterns (per upstream)
- Claude Code plugin marketplace (`/plugin marketplace add expo/skills`, then `/plugin install ...`)
- Cursor remote rules via GitHub repo URL
- Any agent via `bunx skills add expo/skills`

## Dive Coder adapter
Implement a command:
- `dive skills import expo/skills --into .agent/skills/external/expo_skills`

Then index:
- `dive skills reindex`

## Governance
Imported skills must be:
- hashed (integrity)
- version-pinned (commit SHA)
- tracked in EvidencePack when used in a run
