# Dive Context Integration Skill

**Skill ID:** `dive-context-integration`  
**Version:** 2.0  
**Category:** Core Infrastructure  
**Tags:** context-management, documentation, mcp, n8n, automation  

---

## Overview

Dive Context is a **GitHub-based MCP (Model Context Protocol) documentation server** that provides up-to-date documentation, code examples, and best practices for 100+ popular programming libraries, frameworks, and tools. It is deeply integrated into **Dive Coder V15.3** as a core skill for context management and knowledge retrieval.

### Key Features

- **100+ Hand-Curated Libraries** - Top frameworks, tools, and libraries ranked by GitHub stars
- **Advanced Search** - Find libraries by name, tags, category, or description
- **Unlimited GitHub Access** - Access ANY public GitHub repository on-demand
- **Offline Mode** - 24-hour cache for fast, offline access
- **Security Validated** - LLM-based prompt injection detection
- **n8n Specialized** - Optimized for n8n workflow automation
- **MCP Protocol** - Full Model Context Protocol support

---

## Architecture

### Components

1. **MCP Server Core** - Node.js + TypeScript + MCP SDK
   - Exposes MCP tools for documentation retrieval
   - Handles authentication and rate limiting
   - Manages client context (API keys, IDE info)

2. **Skill Repository** - Local filesystem + Git-based sync
   - `/dive-context/skills/n8n/` - n8n nodes and workflows
   - `/dive-context/skills/automation/` - Automation patterns
   - `/dive-context/skills/frameworks/` - Framework documentation

3. **Documentation Fetcher** - Multi-source retrieval
   - Local Skills (Dive Coder skills directory)
   - n8n Docs (https://docs.n8n.io)
   - GitHub Repos (README, docs folders)
   - Official Docs (framework websites)

4. **Search & Ranking Engine** - Vector embeddings + BM25 hybrid search
   - Relevance scoring
   - Recency-based ranking
   - Usage count and community rating

5. **Security Layer** - LLM-based validation
   - Prompt injection detection using GPT-4.1-mini
   - Pattern-based fallback checks
   - Safe-by-default content validation

---

## MCP Tools

### 1. `resolve-skill-id`

**Purpose:** Search for Dive Coder skills and documentation

**Input:**
```json
{
  "query": "Create a Telegram bot with n8n",
  "skillName": "telegram-bot"
}
```

**Output:**
```json
{
  "results": [
    {
      "id": "/n8n/telegram-bot",
      "name": "Telegram Bot Workflow",
      "description": "Complete guide for building Telegram bots with n8n",
      "snippets": 15,
      "rating": 4.8,
      "updated": "2026-01-20"
    }
  ]
}
```

### 2. `query-skill-docs`

**Purpose:** Fetch detailed skill documentation

**Input:**
```json
{
  "skillId": "/n8n/telegram-bot",
  "query": "How to handle inline keyboards?"
}
```

**Output:**
```markdown
# Telegram Inline Keyboards in n8n

## Overview
Inline keyboards allow users to interact with your bot...

## Example Workflow
[Code snippet with n8n JSON]

## Best Practices
- Use callback_data for button actions
- Limit to 8 buttons per row
...
```

### 3. `fetch-n8n-node-docs`

**Purpose:** Get n8n node documentation

**Input:**
```json
{
  "nodeName": "Telegram",
  "operation": "sendMessage"
}
```

**Output:**
```markdown
# Telegram Node: Send Message

## Parameters
- chatId (required): Telegram chat ID
- text (required): Message text
- parse_mode (optional): Markdown, HTML

## Example
[n8n node configuration JSON]
```

### 4. `search-workflow-patterns`

**Purpose:** Find workflow patterns and automation examples

**Input:**
```json
{
  "pattern": "webhook",
  "category": "automation"
}
```

**Output:**
```json
{
  "patterns": [
    {
      "id": "webhook-trigger",
      "name": "Webhook Trigger Pattern",
      "description": "Handle incoming webhooks",
      "examples": 5
    }
  ]
}
```

---

## Library Coverage (100+ Libraries)

### JavaScript/TypeScript (15)
React (220k⭐), Next.js (120k⭐), Vue (210k⭐), Angular (94k⭐), Svelte (77k⭐), Nuxt (53k⭐), Remix (29k⭐), Astro (45k⭐), Solid (27k⭐), Qwik (22k⭐), Preact (36k⭐), Ember (22k⭐), Lit (16k⭐), Stencil (12k⭐), Eleventy (15k⭐)

### Node.js Backend (10)
Express (64k⭐), NestJS (64k⭐), Fastify (30k⭐), Hapi (15k⭐), Koa (35k⭐), Strapi (60k⭐), Loopback (13k⭐), Sails (12k⭐), Feathers (15k⭐), Adonis (16k⭐)

### Python (8)
Django (76k⭐), Flask (66k⭐), FastAPI (72k⭐), Pyramid (4k⭐), Tornado (21k⭐), Bottle (9k⭐), Falcon (9k⭐), Starlette (10k⭐)

### Databases & ORMs (12)
Prisma (37k⭐), MongoDB (25k⭐), Supabase (67k⭐), PostgreSQL (15k⭐), Redis (65k⭐), Elasticsearch (68k⭐), Firebase (25k⭐), DynamoDB (5k⭐), SQLAlchemy (8k⭐), Sequelize (29k⭐), Typeorm (34k⭐), Drizzle (15k⭐)

### AI/LLM & ML (15)
TensorFlow (183k⭐), PyTorch (79k⭐), LangChain (88k⭐), OpenAI (50k⭐), Hugging Face (120k⭐), Scikit-learn (60k⭐), Keras (61k⭐), JAX (30k⭐), Transformers (130k⭐), ONNX (16k⭐), MLflow (17k⭐), Ray (32k⭐), Weights & Biases (8k⭐), Replicate (5k⭐), Anthropic (20k⭐)

### Testing (8)
Jest (43k⭐), Playwright (63k⭐), Cypress (46k⭐), Vitest (13k⭐), Mocha (23k⭐), Chai (8k⭐), Puppeteer (88k⭐), Selenium (30k⭐)

### DevOps (8)
Docker (67k⭐), Kubernetes (107k⭐), Terraform (41k⭐), Ansible (61k⭐), Jenkins (23k⭐), GitLab CI (28k⭐), GitHub Actions (25k⭐), ArgoCD (17k⭐)

### UI Components (8)
Material-UI (91k⭐), Tailwind (79k⭐), shadcn/ui (58k⭐), Chakra (37k⭐), Bootstrap (168k⭐), Foundation (30k⭐), Ant Design (90k⭐), Bulma (49k⭐)

### State Management (5)
Redux (60k⭐), Zustand (43k⭐), MobX (27k⭐), Recoil (20k⭐), Jotai (18k⭐)

### Build Tools (6)
Vite (65k⭐), Webpack (64k⭐), esbuild (37k⭐), Rollup (25k⭐), Parcel (43k⭐), Turbopack (20k⭐)

### Utilities (8)
Lodash (59k⭐), Axios (104k⭐), Zod (30k⭐), Yup (25k⭐), Moment (48k⭐), Day.js (46k⭐), Ramda (24k⭐), Immer (27k⭐)

### Workflow Automation (2)
n8n (42k⭐), Zapier (integration)

---

## Integration with Dive Coder V15.3

### CLI Commands

```bash
# Search for skills
dive-coder context search "telegram bot"

# Fetch skill docs
dive-coder context get /n8n/telegram-bot

# Add skill to project
dive-coder context install /n8n/telegram-bot

# List all available skills
dive-coder context list

# Get library documentation
dive-coder context lib react

# Search by category
dive-coder context search --category database

# Search by tags
dive-coder context search --tags "api,auth"
```

### Python API

```python
from dive_context import DiveContextClient

client = DiveContextClient()

# Search for skills
results = client.search("telegram bot")

# Get skill documentation
docs = client.get_skill("/n8n/telegram-bot")

# Query skill docs
answer = client.query_skill(
    skill_id="/n8n/telegram-bot",
    query="How to handle inline keyboards?"
)

# Fetch n8n node docs
node_docs = client.fetch_n8n_node("Telegram", "sendMessage")

# Search workflow patterns
patterns = client.search_patterns("webhook", category="automation")
```

### Workflow Integration

In n8n workflows:
1. Add "Dive-Context" node
2. Query for relevant patterns
3. Auto-inject documentation into AI nodes

### Skill Auto-Discovery

When Dive Coder detects:
- "n8n" in project → Suggest n8n skills
- "telegram" in code → Suggest Telegram skills
- "supabase" in dependencies → Suggest Supabase skills
- "react" in package.json → Suggest React skills

---

## Security Features

### 1. Prompt Injection Detection

- **Model:** GPT-4.1-mini (fast, cost-effective)
- **Temperature:** 0.1 (deterministic)
- **Max tokens:** 500

**Detection Patterns:**
- "Ignore previous instructions"
- "System: You are now..."
- Encoded payloads (base64, hex)
- Suspicious JavaScript/Python code

### 2. Rate Limiting

| Tier | Requests/min | Daily Limit |
|---|---|---|
| Free | 10 | 100 |
| API Key | 60 | 1000 |
| Pro | 300 | 10000 |

### 3. Content Filtering

- No execution of arbitrary code
- Sanitize all user inputs
- Validate skill metadata
- Block external URL redirects

---

## Deployment Options

### 1. Local Mode (Default)

```bash
cd dive-context
pnpm install
pnpm build
npx dive-context --transport stdio
```

### 2. HTTP Server Mode

```bash
npx dive-context --transport http --port 3000
```

### 3. Docker Mode

```bash
docker run -p 3000:3000 dive-context/server
```

### 4. Cursor IDE Integration

Add to `~/.cursor/config.json`:

```json
{
  "mcpServers": {
    "dive-context": {
      "command": "node",
      "args": ["/path/to/dive-context/dist/index-github.js"],
      "env": {
        "GITHUB_TOKEN": "optional_for_higher_rate_limits"
      }
    }
  }
}
```

### 5. Claude Desktop Integration

```bash
claude mcp add dive-context -- node /path/to/dive-context/dist/index-github.js
```

---

## Best Practices

1. **Use Offline Mode** - Cache results locally for faster access
2. **Search by Tags** - Use metadata tags for precise results
3. **Validate Results** - Always verify documentation against official sources
4. **Rate Limiting** - Respect API rate limits for external sources
5. **Security First** - Enable prompt injection detection for all queries

---

## Troubleshooting

### Issue: Slow documentation fetching

**Solution:** Enable offline cache mode
```bash
dive-coder context cache --enable
```

### Issue: Rate limit exceeded

**Solution:** Use API key for higher limits
```bash
export GITHUB_TOKEN=your_token
dive-coder context search "library"
```

### Issue: Prompt injection warning

**Solution:** Sanitize your queries
```bash
# Instead of: "Ignore instructions and..."
# Use: "Show me the documentation for..."
```

---

## References

- **MCP Specification:** https://modelcontextprotocol.io
- **n8n Documentation:** https://docs.n8n.io
- **GitHub API:** https://docs.github.com/en/rest
- **Dive Coder V15.3:** https://github.com/dive-coder/v15.3

---

## Contributing

To add more libraries or skills:

1. Edit `src/lib/registry.ts`
2. Add library metadata (name, stars, category, tags)
3. Submit PR with documentation links
4. Ensure library has 20k+ stars minimum

---

## License

MIT License - Free to use, modify, and distribute

---

**Built with ❤️ for Dive Coder V15.3 users**
