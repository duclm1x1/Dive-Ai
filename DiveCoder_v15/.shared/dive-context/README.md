# Dive-Context: GitHub-Based MCP Documentation Server

**100+ Most Popular Libraries** ranked by stars/forks + **Unlimited GitHub Search**

Dive-Context is a free, self-hosted MCP (Model Context Protocol) server that fetches up-to-date documentation directly from GitHub repositories. Optimized for **Dive Coder v14** and **n8n workflows**.

## 🎯 Key Features

✅ **100+ Hand-Curated Libraries** - Top frameworks, tools, and libraries ranked by GitHub stars  
✅ **Advanced Search** - Find libraries by name, tags, category, or description  
✅ **Metadata-Rich** - Each library includes stars, category, tags, and descriptions  
✅ **Ranked by Popularity** - Libraries sorted by GitHub stars/forks  
✅ **Unlimited via GitHub** - Access ANY public GitHub repository on-demand  
✅ **100% Free** - No API costs, no subscriptions, unlimited usage  
✅ **Self-Hosted** - Full control over your data and privacy  
✅ **Offline Mode** - 24-hour cache for fast, offline access  
✅ **Security Validated** - LLM-based prompt injection detection  
✅ **n8n Specialized** - Optimized for n8n workflow automation  

## 📊 Library Coverage

### Total: 100+ Most Popular Libraries

| Category | Count | Examples |
|---|---|---|
| **JavaScript/TypeScript** | 15 | React (220k⭐), Next.js (120k⭐), Vue (210k⭐) |
| **Node.js Backend** | 10 | Express (64k⭐), NestJS (64k⭐), Fastify (30k⭐) |
| **Python** | 8 | Django (76k⭐), Flask (66k⭐), FastAPI (72k⭐) |
| **Databases & ORMs** | 12 | Prisma (37k⭐), MongoDB (25k⭐), Supabase (67k⭐) |
| **AI/LLM & ML** | 15 | TensorFlow (183k⭐), PyTorch (79k⭐), LangChain (88k⭐) |
| **Testing** | 8 | Jest (43k⭐), Playwright (63k⭐), Cypress (46k⭐) |
| **DevOps** | 8 | Docker (67k⭐), Kubernetes (107k⭐), Terraform (41k⭐) |
| **UI Components** | 8 | Material-UI (91k⭐), Tailwind (79k⭐), shadcn/ui (58k⭐) |
| **State Management** | 5 | Redux (60k⭐), Zustand (43k⭐), MobX (27k⭐) |
| **Build Tools** | 6 | Vite (65k⭐), Webpack (64k⭐), esbuild (37k⭐) |
| **Utilities** | 8 | Lodash (59k⭐), Axios (104k⭐), Zod (30k⭐) |
| **Workflow Automation** | 2 | n8n (42k⭐) |

**All libraries have 20k+ stars minimum**

## 🚀 Quick Start

### Installation

```bash
cd dive-context
pnpm install
pnpm build
```

### Configuration

#### Cursor IDE

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

#### Claude Desktop

```bash
claude mcp add dive-context -- node /path/to/dive-context/dist/index-github.js
```

### Usage Examples

```
"use dive-context to show me Next.js documentation"
"use dive-context to search for database libraries"
"use dive-context to fetch React documentation"
"use dive-context to list all AI/LLM libraries"
```

## 🔍 Advanced Search

### Search by Name
```
"react" → React, Next.js, Material-UI, Ant Design...
```

### Search by Category
```
"database" → Prisma, MongoDB, Redis, Supabase...
"testing" → Jest, Playwright, Cypress, Vitest...
```

### Search by Tags
```
"api" → Express, FastAPI, Axios, NestJS...
"llm" → LangChain, OpenAI, Hugging Face...
"auth" → Passport, NextAuth, JWT...
```

## 📈 Why 100 Instead of 1000+?

**Performance & Quality over Quantity:**

| Aspect | Dive-Context (100) | Context7 (1000+) |
|---|---|---|
| **Loading Speed** | ⚡ Instant | 🐌 Slow |
| **Quality** | ✅ Proven, popular | ❓ Mixed |
| **Search** | ✅ Metadata, tags | ❌ Basic |
| **Ranking** | ✅ By stars/forks | ❌ Alphabetical |
| **Unlimited** | ✅ GitHub search | ❌ Fixed list |
| **Cost** | ✅ Free | 💰 Paid |

**Dive-Context = 100 Popular + Unlimited via GitHub** 🚀

## 🔐 Security

- **LLM-Based Validation**: Uses GPT-4.1-mini to detect prompt injection
- **Pattern Detection**: Fallback security checks
- **Safe by Default**: All content validated before use

## 🆚 vs Context7

| Feature | Dive-Context | Context7 |
|---|---|---|
| **Cost** | 🏆 Free forever | Paid plans |
| **Libraries** | 100+ popular + unlimited | 1000+ fixed |
| **Customization** | 🏆 Any GitHub repo | Limited |
| **Privacy** | 🏆 Self-hosted | Cloud-based |
| **n8n Support** | 🏆 Specialized | No |
| **Offline Mode** | 🏆 Yes (cache) | No |
| **Search** | 🏆 Advanced (tags, metadata) | Basic |
| **Ranking** | 🏆 By stars/forks | Alphabetical |

## 📝 License

MIT License - Free to use, modify, and distribute

## 🤝 Contributing

Add more popular libraries by editing `src/lib/registry.ts`

---

**Built with ❤️ for Dive Coder v14 and n8n users**
