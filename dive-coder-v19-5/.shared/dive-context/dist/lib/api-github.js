import { fetchDocumentation } from "./github.js";
import { getLibraryMeta, searchLibraries } from "./registry.js";
/**
 * Fetch skill documentation for a library from GitHub
 */
export async function fetchSkillDocs(libraryId) {
    // Try to find in popular libraries first
    const meta = getLibraryMeta(libraryId);
    if (meta) {
        // Fetch from first repo in the list
        const repo = meta.repos[0];
        const content = await fetchDocumentation(repo.owner, repo.repo, repo.path, repo.branch);
        return {
            libraryId,
            libraryName: libraryId,
            description: meta.description,
            category: meta.category,
            tags: meta.tags,
            stars: meta.stars,
            content,
            repos: meta.repos,
            lastUpdated: new Date().toISOString(),
        };
    }
    // If not found in popular libraries, try GitHub search
    throw new Error(`Library "${libraryId}" not found in popular libraries. Use GitHub search or add custom repo.`);
}
/**
 * Search for libraries by query
 */
export async function searchSkills(query) {
    const results = searchLibraries(query);
    return results.slice(0, 10).map(r => ({
        name: r.name,
        description: r.meta.description,
        stars: r.meta.stars,
    }));
}
//# sourceMappingURL=api-github.js.map