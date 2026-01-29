# Workflow: IKO (Issue Knowledge Object)

Use IKOs as the **single source of truth** for each issue.

## Commands

- Create:
  ```bash
  python3 .shared/vibe-coder-v13/vibe.py iko-new --repo . --id IKO-123 --title "..." --description "..." --actor <name>
  ```

- Show:
  ```bash
  python3 .shared/vibe-coder-v13/vibe.py iko-show --repo . --id IKO-123
  ```

- List:
  ```bash
  python3 .shared/vibe-coder-v13/vibe.py iko-list --repo .
  ```

## Rules

- Only Gatekeeper can change state.
- RLM/Cruel attach investigations and evidence pointers only.
