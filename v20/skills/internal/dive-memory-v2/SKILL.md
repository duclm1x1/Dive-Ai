# Dive-Memory v2 - AI Persistent Project Memory

## Skill Type
**Base Skill** (Always Active)

## Purpose
Dive-Memory v2 provides persistent project memory for AI agents, solving the critical problem of context loss and skill amnesia. This skill automatically injects project context, behavioral rules, and skill triggers into every AI interaction.

## When to Use
**Always Active** - This skill runs automatically for every project that has a `PROJECT.memory.md` file.

## Core Capabilities

### 1. Context Injection
Automatically prepends project constitution to every AI prompt:
- Project goal and objectives
- AI persona and behavioral guidelines
- Always-on skills that should be considered
- Behavioral rules that MUST be followed
- Current dynamic state (task, file, environment)

### 2. Skill Auto-Discovery
Intent-based skill triggering system:
- Matches user prompts against configured intent patterns
- Suggests relevant skills automatically
- Provides contextual prompts for skill usage

### 3. Knowledge Management
File-based knowledge store:
- `.known.md` files for research and decisions
- Semantic search with vector embeddings
- Automatic knowledge retrieval based on context

### 4. Task Management
Track work items with acceptance criteria:
- Task status and priority
- Acceptance criteria checklists
- Links to related knowledge documents

## File Structure

```
project-root/
├── PROJECT.memory.md          # Behavioral memory (YAML + Markdown)
├── knowns/                    # Knowledge documents
│   ├── auth-strategy.known.md
│   ├── api-design.known.md
│   └── ...
└── tasks/                     # Task documents
    ├── implement-auth.md
    └── ...
```

## PROJECT.memory.md Format

```yaml
---
project_goal: "Build a comprehensive e-commerce platform"
persona: "You are a senior full-stack engineer"
always_on_skills:
  - name: "code_reviewer"
    description: "Reviews code for best practices"
behavioral_rules:
  - "ALWAYS write tests before code"
  - "BEFORE implementing, check if .known.md exists"
skill_triggers:
  - intent:
      - "create api"
      - "build endpoint"
    skill_to_suggest: "api_generator"
    suggestion_prompt: "Use API generator for this task"
dynamic_state:
  last_command: "npm test"
  current_task: "#123"
---

Additional project notes...
```

## Usage Instructions

### For AI Agents

When you receive a user prompt:

1. **Check for PROJECT.memory.md** in the current project directory
2. **If found, read and parse it** using the memory parser
3. **Generate meta-prompt** with project constitution
4. **Match skill triggers** against the user prompt
5. **Inject context** by prepending meta-prompt to user request
6. **Follow behavioral rules** strictly (MUST/NEVER statements)
7. **Consider always-on skills** for every response
8. **Update dynamic state** after completing actions

### Example Workflow

**User Prompt:**
```
I need to implement user authentication
```

**After Context Injection:**
```
[BEGIN PROJECT CONSTITUTION]

Project Goal: Build a comprehensive e-commerce platform

AI Persona: You are a senior full-stack engineer

Available Skills (Always Consider):
  - code_reviewer: Reviews code for best practices
  - security_auditor: Checks for security vulnerabilities

Behavioral Rules (MUST Follow):
  1. ALWAYS write tests before code
  2. BEFORE implementing, check if .known.md exists

Current Context:
  - last_command: npm test
  - current_task: #123

[END PROJECT CONSTITUTION]

[Skill Suggestions]
Based on your request about "authentication", consider using:
  - security_auditor: Run security audit for auth implementation

[BEGIN USER REQUEST]
I need to implement user authentication
[END USER REQUEST]
```

## API Reference

### Memory Parser

```typescript
import { parseMemoryFile, generateMetaPrompt, matchSkillTriggers } from "./memoryParser";

// Parse PROJECT.memory.md
const { memory, markdownBody } = parseMemoryFile(fileContent);

// Generate meta-prompt for context injection
const metaPrompt = generateMetaPrompt(memory);

// Match skill triggers
const matches = matchSkillTriggers(userPrompt, memory.skillTriggers);
```

### Context Injection

```typescript
import { injectContext } from "./contextInjection";

// Inject context into user prompt
const result = injectContext(userPrompt, projectMemory);

console.log(result.finalPrompt);      // Full prompt with context
console.log(result.matchedTriggers);  // Matched skill triggers
console.log(result.suggestions);      // Skill suggestions
```

### Knowledge Store

```typescript
import { parseKnownFile } from "./memoryParser";

// Parse .known.md file
const { metadata, content } = parseKnownFile(fileContent);

// Semantic search
import { semanticSearch } from "./vectorSearch";
const results = await semanticSearch(projectId, "authentication best practices", 5);
```

## Integration Points

### With Dive AI V20 Orchestrator

```python
from v20.coder.orchestrator.orchestrator import Orchestrator
from v20.skills.internal.dive_memory_v2 import DiveMemorySkill

# Initialize orchestrator with Dive-Memory
orchestrator = Orchestrator()
memory_skill = DiveMemorySkill()

# Inject context before every AI call
def process_prompt(user_prompt, project_path):
    # Read PROJECT.memory.md
    memory = memory_skill.load_memory(project_path)
    
    # Inject context
    full_prompt = memory_skill.inject_context(user_prompt, memory)
    
    # Send to AI
    response = orchestrator.execute(full_prompt)
    
    # Update dynamic state
    memory_skill.update_state(project_path, {
        "last_command": get_last_command(),
        "last_file": get_last_file()
    })
    
    return response
```

### With Skill Registry

```yaml
# v20/runtime/skills_registry.yml
skills:
  - name: dive-memory-v2
    type: base
    always_active: true
    priority: 1  # Highest priority - runs first
    location: v20/skills/internal/dive-memory-v2
    entry_point: skill.py
    capabilities:
      - context_injection
      - knowledge_management
      - skill_discovery
```

## Behavioral Rules for AI

When this skill is active, you MUST:

1. **ALWAYS check for PROJECT.memory.md** before starting any task
2. **ALWAYS inject context** into every user prompt
3. **ALWAYS follow behavioral rules** defined in PROJECT.memory.md
4. **BEFORE implementing**, check if relevant `.known.md` exists
5. **AFTER completing a task**, update `dynamic_state` in PROJECT.memory.md
6. **WHEN skill triggers match**, suggest the appropriate skill
7. **NEVER skip context injection** even if the prompt seems simple

## Configuration

### Enable for a Project

```bash
cd your-project
dive-mem init
```

This creates:
- `PROJECT.memory.md` with default configuration
- `knowns/` directory for knowledge documents
- `tasks/` directory for task management

### Customize Behavior

Edit `PROJECT.memory.md`:

```yaml
---
project_goal: "Your project goal"
persona: "Your preferred AI persona"
always_on_skills:
  - name: "your_skill"
    description: "Description"
behavioral_rules:
  - "Your custom rules"
skill_triggers:
  - intent: ["keywords"]
    skill_to_suggest: "skill_name"
---
```

## Testing

### Test Context Injection

```bash
dive-mem context inject "Your test prompt"
```

### Test Skill Matching

```typescript
import { matchSkillTriggers } from "./memoryParser";

const triggers = [
  {
    intent: ["create api", "build endpoint"],
    skill: "api_generator",
  },
];

const matches = matchSkillTriggers("I need to create a new API", triggers);
console.log(matches); // Should match api_generator
```

## Troubleshooting

### Context Not Injecting

1. Verify `PROJECT.memory.md` exists
2. Check YAML syntax is valid
3. Ensure memory parser is imported correctly
4. Verify `project_goal` field is present

### Skills Not Triggering

1. Check `skill_triggers` configuration
2. Verify intent keywords match user prompt
3. Test with `matchSkillTriggers()` function
4. Add more intent variations

### Knowledge Not Found

1. Verify `.known.md` files exist in `knowns/` directory
2. Check file naming follows convention
3. Ensure files have YAML front-matter
4. Test semantic search with vector store

## Best Practices

1. **Document First, Code Second** - Always create `.known.md` before implementing
2. **Use Behavioral Rules** - Define clear MUST/NEVER rules
3. **Link Tasks to Knowledge** - Reference `@knowns/file.known.md` in tasks
4. **Update Dynamic State** - Keep AI informed of current context
5. **Use Skill Triggers** - Add triggers for common patterns
6. **Keep Memory Concise** - Focus on essential rules and context

## Example Projects

See `/home/ubuntu/dive-ai-local` for a complete implementation with:
- Web dashboard for memory management
- CLI tool (`dive-mem`) for local development
- Full tRPC API
- Vector search integration
- Task management system

## Dependencies

- `yaml` - YAML parsing
- `chromadb` - Vector search (optional)
- `mysql2` / `drizzle-orm` - Metadata storage

## License

MIT

## Support

For issues or questions:
- GitHub: [repository-url]
- Documentation: See `DIVE_MEMORY_V2_GUIDE.md`
