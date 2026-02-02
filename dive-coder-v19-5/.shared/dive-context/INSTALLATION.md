# Dive-Context Installation Guide

## Prerequisites

- Node.js 18+ or 20+
- pnpm (or npm/yarn)
- Git

## Installation Methods

### Method 1: Local Installation (Recommended)

1. **Clone/Download Dive-Context**

```bash
cd /path/to/your/projects
git clone <dive-context-repo> # Or extract from zip
cd dive-context
```

2. **Install Dependencies**

```bash
pnpm install
# or
npm install
```

3. **Build**

```bash
pnpm build
```

4. **Test**

```bash
pnpm list-libraries
```

You should see a list of 21+ registered libraries.

### Method 2: Global Installation

```bash
cd dive-context
pnpm build
npm link
# Now you can use 'dive-context' command globally
```

## Configuration

### For Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dive-context": {
      "command": "node",
      "args": ["/absolute/path/to/dive-context/dist/index-github.js"]
    }
  }
}
```

**With environment variables**:

```json
{
  "mcpServers": {
    "dive-context": {
      "command": "node",
      "args": ["/absolute/path/to/dive-context/dist/index-github.js"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here",
        "OPENAI_API_KEY": "sk_your_key_here"
      }
    }
  }
}
```

### For Claude Desktop

```bash
claude mcp add dive-context -- node /absolute/path/to/dive-context/dist/index-github.js
```

### For Dive Coder v14

Add to your Dive Coder configuration:

```bash
dive-coder config set mcp.dive-context.command "node /path/to/dive-context/dist/index-github.js"
```

## Environment Variables

### GITHUB_TOKEN (Optional but Recommended)

**Why?** GitHub API has rate limits:
- **Without token**: 60 requests/hour
- **With token**: 5000 requests/hour

**How to get**:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo` (read-only)
4. Copy the token

**Set it**:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`):

```bash
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### OPENAI_API_KEY (Optional)

**Why?** For LLM-based security validation of documentation content.

**Without it**: Falls back to pattern-based validation (still works, but less accurate).

**Set it**:

```bash
export OPENAI_API_KEY="sk-your_key_here"
```

## Verification

### Test the MCP Server

```bash
cd dive-context
pnpm dev
```

You should see:
```
Dive-Context MCP server running on stdio (GitHub mode)
Registered libraries: 21
Use --list-libraries to see all available libraries
```

Press `Ctrl+C` to stop.

### Test with Cursor

1. Open Cursor
2. Open a new chat
3. Type: "use dive-context to show me Next.js API routes documentation"
4. Cursor should invoke the MCP server and fetch docs from GitHub

### Test Cache

```bash
# First query (fetches from GitHub)
# Second query (uses cache)

# Update cache manually
pnpm update-cache

# Clear cache
pnpm clear-cache
```

## Troubleshooting

### Issue: "Cannot find module"

**Solution**: Make sure you ran `pnpm build` after installation.

### Issue: "GitHub API rate limit exceeded"

**Solution**: Add a `GITHUB_TOKEN` environment variable (see above).

### Issue: "Cursor doesn't recognize dive-context"

**Solution**:
1. Check that the path in `mcp.json` is absolute
2. Restart Cursor after editing `mcp.json`
3. Check Cursor logs: `Cursor Settings` → `MCP` → `View Logs`

### Issue: "Documentation not found"

**Solution**:
1. Check if the library is registered: `pnpm list-libraries`
2. Try using the full GitHub path: `/owner/repo`
3. Check if the repository is public

## Advanced Configuration

### Add Custom Libraries

Edit `src/lib/registry.ts`:

```typescript
export const REPO_REGISTRY: Record<string, GitHubRepo[]> = {
  // ... existing libraries ...
  
  "my-library": [
    { owner: "my-org", repo: "my-repo", path: "docs" },
  ],
};
```

Then rebuild:

```bash
pnpm build
```

### Change Cache Duration

Edit `src/lib/github.ts`:

```typescript
const CACHE_TTL = 24 * 60 * 60 * 1000; // Change to your preferred duration
```

## Next Steps

- Read the [README.md](./README.md) for usage examples
- Check the [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- Try the example prompts in your IDE

## Support

For issues or questions:
- Check the logs in `.cache/` directory
- Enable debug mode: `DEBUG=* pnpm dev`
- Report issues on GitHub

---

**Happy coding with Dive-Context! 🚀**
