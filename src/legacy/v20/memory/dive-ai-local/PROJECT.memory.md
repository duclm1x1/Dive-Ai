---
always_on_skills:
- description: Persistent project memory and context injection
  name: dive-memory-v2
- description: Reviews code for best practices and potential issues
  name: code_reviewer
behavioral_rules:
- ALWAYS check PROJECT.memory.md before starting any task
- BEFORE implementing a feature, document the approach in a .known.md file
- AFTER completing a task, update dynamic_state with progress
- NEVER skip tests - always write and run tests before delivery
dynamic_state:
  current_phase: Phase 11 - Dive AI V20 Integration
  current_task: Building Electron desktop app
  docs_first: true
  following_rules: true
  last_action: Created electron-desktop-app.known.md
  last_checkpoint: '82052710'
  last_request: Can you review my code?
  last_response_length: 145
  next_features:
  - Electron desktop app
  - GitHub sync integration
  status: Testing Dive AI V20 orchestrator
  total_requests: 6
persona: You are a senior full-stack engineer and AI systems architect
project_goal: Build Dive AI Local - A comprehensive AI memory management system with
  desktop app and GitHub sync
skill_triggers:
- intent:
  - electron
  - desktop app
  - system tray
  skill_to_suggest: electron_builder
  suggestion_prompt: Use Electron to build cross-platform desktop application
- intent:
  - github
  - git sync
  - version control
  skill_to_suggest: git_integrator
  suggestion_prompt: Integrate GitHub for version control and sync
---

# Dive AI Local - Project Memory

This project uses Dive-Memory v2 for persistent AI context management.

## Current Status

We have completed the core Dive-Memory v2 system and are now integrating it with Dive AI V20 for battle testing.

## Next Steps

1. Deploy Dive AI V20 orchestrator
2. Test context injection and skill routing
3. Use Dive AI V20 to build remaining features
4. Monitor and fix issues in real-time