import { fetchGitHubDocs, searchGitHubRepos } from "./github.js";
import { getReposForLibrary, listAllLibraries } from "./registry.js";
/**
 * Search for libraries/skills using GitHub
 */
export async function searchSkills(query, skillName) {
    try {
        // First, check our registry
        const registeredRepos = getReposForLibrary(skillName);
        if (registeredRepos.length > 0) {
            // Use registered repos
            const results = registeredRepos.map((repo, index) => ({
                id: `/${repo.owner}/${repo.repo}`,
                name: `${repo.owner}/${repo.repo}`,
                description: `Official documentation for ${repo.repo}`,
                examples: 10, // Placeholder
                rating: 5.0,
                updated: new Date().toISOString().split("T")[0],
            }));
            return { results };
        }
        // Fallback: Search GitHub
        console.error(`[Search] No registered repos for "${skillName}", searching GitHub...`);
        const githubRepos = await searchGitHubRepos(`${skillName} documentation`, 5);
        const results = githubRepos.map((repo) => ({
            id: `/${repo.owner}/${repo.repo}`,
            name: `${repo.owner}/${repo.repo}`,
            description: `GitHub repository: ${repo.owner}/${repo.repo}`,
            examples: 5,
            rating: 4.0,
            updated: new Date().toISOString().split("T")[0],
        }));
        if (results.length === 0) {
            return {
                results: [],
                error: `No documentation found for "${skillName}". Try: ${listAllLibraries().slice(0, 10).join(", ")}`,
            };
        }
        return { results };
    }
    catch (error) {
        return {
            results: [],
            error: `Error searching: ${error}`,
        };
    }
}
/**
 * Fetch skill documentation from GitHub
 */
export async function fetchSkillDocs(request) {
    try {
        // Parse skill ID or library ID: /owner/repo or /owner/repo/path
        const id = request.libraryId || request.skillId;
        if (!id) {
            return { data: "Error: No libraryId or skillId provided" };
        }
        const parts = id.split("/").filter(Boolean);
        if (parts.length < 2) {
            return {
                data: `Invalid skill ID format. Expected: /owner/repo or /owner/repo/path\nExample: /vercel/next.js or /n8n-io/n8n-docs`,
            };
        }
        const [owner, repo, ...pathParts] = parts;
        const repoPath = pathParts.length > 0 ? pathParts.join("/") : undefined;
        // Check if this is a registered repo
        const registeredRepos = getReposForLibrary(repo);
        let githubRepo;
        if (registeredRepos.length > 0) {
            // Use the first registered repo (or find exact match)
            githubRepo = registeredRepos.find((r) => r.owner === owner && r.repo === repo) || registeredRepos[0];
        }
        else {
            // Use the provided path
            githubRepo = {
                owner,
                repo,
                path: repoPath || "README.md",
            };
        }
        // Fetch documentation
        const { content, cached } = await fetchGitHubDocs(githubRepo, request.query);
        const header = `# ${owner}/${repo} Documentation\n\n`;
        const cacheNote = cached ? `> 📦 Cached documentation (updated within 24 hours)\n\n` : `> ✅ Fresh documentation from GitHub\n\n`;
        return {
            data: header + cacheNote + content,
        };
    }
    catch (error) {
        return {
            data: `Error fetching documentation: ${error}\n\nMake sure the repository exists and is public.`,
        };
    }
}
/**
 * Fetch n8n node documentation from GitHub
 */
export async function fetchN8nNodeDocs(nodeName, operation) {
    try {
        // n8n nodes are in the n8n-io/n8n repository
        const githubRepo = {
            owner: "n8n-io",
            repo: "n8n",
            path: `packages/nodes-base/nodes/${nodeName}`,
        };
        const { content, cached } = await fetchGitHubDocs(githubRepo, operation);
        const header = `# n8n ${nodeName} Node Documentation\n\n`;
        const cacheNote = cached ? `> 📦 Cached (updated within 24 hours)\n\n` : `> ✅ Fresh from GitHub\n\n`;
        return {
            data: header + cacheNote + content,
        };
    }
    catch (error) {
        // Fallback: Try n8n-docs repository
        try {
            const docsRepo = {
                owner: "n8n-io",
                repo: "n8n-docs",
                path: `docs/integrations/builtin/app-nodes/n8n-nodes-base.${nodeName.toLowerCase()}`,
            };
            const { content, cached } = await fetchGitHubDocs(docsRepo, operation);
            return {
                data: `# n8n ${nodeName} Node Documentation\n\n> ✅ From n8n-docs\n\n${content}`,
            };
        }
        catch {
            return {
                data: `# n8n ${nodeName} Node\n\nDocumentation not found in GitHub.\n\nPlease visit: https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.${nodeName.toLowerCase()}/`,
            };
        }
    }
}
//# sourceMappingURL=api-github-old.js.map