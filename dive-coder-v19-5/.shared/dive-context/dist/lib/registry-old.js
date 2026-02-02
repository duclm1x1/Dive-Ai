/**
 * Registry of popular repositories for documentation
 */
export const REPO_REGISTRY = {
    // n8n and workflow automation
    n8n: [
        { owner: "n8n-io", repo: "n8n", path: "packages/nodes-base/nodes" },
        { owner: "n8n-io", repo: "n8n-docs", path: "docs" },
    ],
    // JavaScript/TypeScript frameworks
    nextjs: [
        { owner: "vercel", repo: "next.js", path: "docs" },
    ],
    react: [
        { owner: "facebook", repo: "react", path: "docs" },
    ],
    vue: [
        { owner: "vuejs", repo: "core", path: "packages/vue/README.md" },
    ],
    express: [
        { owner: "expressjs", repo: "express", path: "Readme.md" },
    ],
    fastify: [
        { owner: "fastify", repo: "fastify", path: "docs" },
    ],
    // Python frameworks
    fastapi: [
        { owner: "fastapi", repo: "fastapi", path: "docs/en/docs" },
    ],
    django: [
        { owner: "django", repo: "django", path: "docs" },
    ],
    flask: [
        { owner: "pallets", repo: "flask", path: "docs" },
    ],
    // Databases and ORMs
    supabase: [
        { owner: "supabase", repo: "supabase", path: "apps/docs/content" },
    ],
    prisma: [
        { owner: "prisma", repo: "prisma", path: "docs" },
    ],
    mongodb: [
        { owner: "mongodb", repo: "docs", path: "source" },
    ],
    // Cloud and deployment
    vercel: [
        { owner: "vercel", repo: "vercel", path: "docs" },
    ],
    cloudflare: [
        { owner: "cloudflare", repo: "workers-sdk", path: "packages/wrangler/docs" },
    ],
    // AI and LLM
    openai: [
        { owner: "openai", repo: "openai-node", path: "README.md" },
        { owner: "openai", repo: "openai-python", path: "README.md" },
    ],
    langchain: [
        { owner: "langchain-ai", repo: "langchainjs", path: "docs" },
    ],
    // Telegram bots
    telegram: [
        { owner: "telegraf", repo: "telegraf", path: "docs" },
        { owner: "yagop", repo: "node-telegram-bot-api", path: "doc" },
    ],
    // Testing
    jest: [
        { owner: "jestjs", repo: "jest", path: "docs" },
    ],
    playwright: [
        { owner: "microsoft", repo: "playwright", path: "docs/src" },
    ],
    // DevOps
    docker: [
        { owner: "docker", repo: "docs", path: "content" },
    ],
    kubernetes: [
        { owner: "kubernetes", repo: "website", path: "content/en/docs" },
    ],
};
/**
 * Get repositories for a library name
 */
export function getReposForLibrary(libraryName) {
    const lowerName = libraryName.toLowerCase();
    // Exact match
    if (REPO_REGISTRY[lowerName]) {
        return REPO_REGISTRY[lowerName];
    }
    // Partial match
    for (const [key, repos] of Object.entries(REPO_REGISTRY)) {
        if (key.includes(lowerName) || lowerName.includes(key)) {
            return repos;
        }
    }
    return [];
}
/**
 * Add a custom repository to the registry
 */
export function addCustomRepo(libraryName, repo) {
    if (!REPO_REGISTRY[libraryName]) {
        REPO_REGISTRY[libraryName] = [];
    }
    REPO_REGISTRY[libraryName].push(repo);
}
/**
 * List all registered libraries
 */
export function listAllLibraries() {
    return Object.keys(REPO_REGISTRY).sort();
}
//# sourceMappingURL=registry-old.js.map