# Dive-Context vs Context7: Detailed Comparison

## Overview

Both **Dive-Context** and **Context7** are MCP (Model Context Protocol) servers designed to provide up-to-date documentation to LLMs. However, they have fundamentally different architectures and target audiences.

## Architecture Comparison

| Aspect | Context7 | Dive-Context |
|---|---|---|
| **Data Source** | Upstash-hosted database | GitHub repositories (direct) |
| **Indexing** | Pre-indexed by Upstash | On-demand fetching + caching |
| **Updates** | Controlled by Upstash | Real-time from GitHub |
| **Storage** | Cloud-based | Local cache (.cache/) |
| **Offline Mode** | ❌ No | ✅ Yes (24h cache) |

## Cost Comparison

| Feature | Context7 | Dive-Context |
|---|---|---|
| **Free Tier** | Limited requests/month | ✅ Unlimited (GitHub limits apply) |
| **Paid Plans** | Required for heavy use | ❌ Not needed |
| **API Costs** | $X/month for Pro | ✅ $0 forever |
| **Self-Hosting** | ❌ Not possible | ✅ Fully self-hosted |

## Feature Comparison

### Documentation Coverage

| Category | Context7 | Dive-Context |
|---|---|---|
| **Pre-Indexed Libraries** | 1000+ | 21 (expandable) |
| **Custom Repos** | ❌ No | ✅ Any public GitHub repo |
| **Version Support** | ✅ Yes | ✅ Yes (via branches/tags) |
| **Private Repos** | ❌ No | ✅ Yes (with GITHUB_TOKEN) |

### Performance

| Metric | Context7 | Dive-Context |
|---|---|---|
| **First Query** | ~500ms | ~2-3s (GitHub API) |
| **Cached Query** | ~500ms | ~50ms (local cache) |
| **Rate Limits** | Plan-dependent | 5000/hour (with token) |
| **Concurrent Requests** | High | Medium (GitHub limits) |

### Security

| Feature | Context7 | Dive-Context |
|---|---|---|
| **Prompt Injection Detection** | Basic | ✅ LLM-based (GPT-4.1-mini) |
| **Content Validation** | Server-side | ✅ Local + LLM |
| **Data Privacy** | Upstash servers | ✅ Local cache only |
| **Audit Trail** | Limited | ✅ Full (local logs) |

## Use Case Comparison

### When to Use Context7

✅ **Best for**:
- You need access to 1000+ pre-indexed libraries immediately
- You want zero setup time
- You're okay with paid plans for heavy use
- You need enterprise support

❌ **Not ideal for**:
- Cost-sensitive projects
- Private/internal documentation
- Custom documentation sources
- Offline development

### When to Use Dive-Context

✅ **Best for**:
- **Dive Coder v14 users** (optimized for this)
- **n8n workflow developers** (specialized support)
- Cost-sensitive projects (100% free)
- Private repositories (with GITHUB_TOKEN)
- Custom documentation sources
- Offline development (with cache)
- Self-hosted environments

❌ **Not ideal for**:
- Need 1000+ libraries immediately (only 21 pre-configured)
- Don't want to manage caching
- Need guaranteed 99.9% uptime

## Integration Comparison

### Cursor Integration

**Context7**:
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

**Dive-Context**:
```json
{
  "mcpServers": {
    "dive-context": {
      "command": "node",
      "args": ["/path/to/dive-context/dist/index-github.js"],
      "env": {
        "GITHUB_TOKEN": "optional"
      }
    }
  }
}
```

### Claude Desktop Integration

**Context7**:
```bash
claude mcp add --header "CONTEXT7_API_KEY: YOUR_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

**Dive-Context**:
```bash
claude mcp add dive-context -- node /path/to/dive-context/dist/index-github.js
```

## Specialized Features

### Dive-Context Exclusive Features

1. **n8n Node Documentation**
   - Direct access to n8n node docs
   - Operation-specific examples
   - Best practices for n8n workflows

2. **Dive Coder v14 Integration**
   - Optimized for Dive Coder workflows
   - Skill-based documentation structure
   - CLI integration (`dive-coder context`)

3. **GitHub-Native**
   - Works with ANY public GitHub repo
   - Private repo support (with token)
   - Branch/tag specific docs

4. **Self-Hosted**
   - No external dependencies
   - Full data control
   - Offline mode

### Context7 Exclusive Features

1. **Massive Library Coverage**
   - 1000+ pre-indexed libraries
   - Automatic updates by Upstash
   - No setup required

2. **Enterprise Features**
   - SLA guarantees
   - Priority support
   - Advanced analytics

3. **Zero Maintenance**
   - No caching management
   - No GitHub token needed
   - Always available

## Cost Analysis (1 Year)

### Scenario: Heavy User (10,000 queries/month)

**Context7**:
- Free tier: ~1,000 queries/month
- Pro plan: $X/month × 12 = $Y/year
- **Total**: $Y/year

**Dive-Context**:
- GitHub API: Free (with token)
- OpenAI validation: ~$5/month (optional)
- Hosting: $0 (self-hosted)
- **Total**: $0-60/year

### Scenario: Team of 5 Developers

**Context7**:
- 5 × Pro plan = $Z/year
- **Total**: $Z/year

**Dive-Context**:
- Self-hosted: $0
- Optional OpenAI: $25/month
- **Total**: $0-300/year

## Migration Path

### From Context7 to Dive-Context

1. **Install Dive-Context**
   ```bash
   cd dive-context
   pnpm install && pnpm build
   ```

2. **Update IDE Config**
   - Replace Context7 MCP config with Dive-Context
   - Add GITHUB_TOKEN (optional)

3. **Test with Common Libraries**
   ```
   "use dive-context to show Next.js documentation"
   ```

4. **Add Custom Libraries** (if needed)
   - Edit `src/lib/registry.ts`
   - Rebuild: `pnpm build`

### From Dive-Context to Context7

1. **Sign up at context7.com**
2. **Get API key**
3. **Update IDE config** with Context7 URL
4. **Remove Dive-Context** (optional)

## Conclusion

| Criteria | Winner |
|---|---|
| **Cost** | 🏆 Dive-Context (free) |
| **Library Coverage** | 🏆 Context7 (1000+ libs) |
| **Customization** | 🏆 Dive-Context (any repo) |
| **Setup Time** | 🏆 Context7 (instant) |
| **Privacy** | 🏆 Dive-Context (local) |
| **n8n Support** | 🏆 Dive-Context (specialized) |
| **Enterprise** | 🏆 Context7 (SLA, support) |
| **Offline Mode** | 🏆 Dive-Context (cache) |

**Recommendation**:
- **Choose Context7** if you need 1000+ libraries immediately and don't mind paying
- **Choose Dive-Context** if you're a Dive Coder/n8n user, want 100% free, or need custom repos

---

**Both are excellent tools. Choose based on your specific needs!**
