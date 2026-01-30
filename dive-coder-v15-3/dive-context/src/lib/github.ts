import { Octokit } from "@octokit/rest";
import fs from "fs/promises";
import path from "path";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const CACHE_DIR = path.join(process.cwd(), ".cache", "github");
const CACHE_TTL = 24 * 60 * 60 * 1000; // 24 hours

// Initialize Octokit (works without token but has lower rate limits)
const octokit = new Octokit({
  auth: GITHUB_TOKEN,
});

/**
 * GitHub repository configuration
 */
export interface GitHubRepo {
  owner: string;
  repo: string;
  path?: string; // Path within repo (e.g., "docs", "README.md")
  branch?: string; // Default: main
}

/**
 * Cached documentation entry
 */
interface CachedDoc {
  content: string;
  fetchedAt: number;
  sha: string; // Git commit SHA for version tracking
}

/**
 * Fetch documentation from a GitHub repository
 */
export async function fetchGitHubDocs(
  repo: GitHubRepo,
  query?: string
): Promise<{ content: string; cached: boolean }> {
  const cacheKey = `${repo.owner}_${repo.repo}_${repo.path || "root"}`;
  const cachePath = path.join(CACHE_DIR, `${cacheKey}.json`);

  // Check cache first
  const cached = await getCachedDoc(cachePath);
  if (cached && Date.now() - cached.fetchedAt < CACHE_TTL) {
    console.error(`[GitHub] Using cached docs for ${repo.owner}/${repo.repo}`);
    return { content: filterContent(cached.content, query), cached: true };
  }

  // Fetch from GitHub
  try {
    console.error(`[GitHub] Fetching docs from ${repo.owner}/${repo.repo}...`);

    const { data } = await octokit.rest.repos.getContent({
      owner: repo.owner,
      repo: repo.repo,
      path: repo.path || "",
      ref: repo.branch || "main",
    });

    let content = "";

    if (Array.isArray(data)) {
      // Directory - fetch all markdown files
      for (const file of data) {
        if (file.type === "file" && file.name.match(/\.(md|mdx)$/i)) {
          const fileContent = await fetchFileContent(repo.owner, repo.repo, file.path, repo.branch);
          content += `\n\n# ${file.name}\n\n${fileContent}`;
        }
      }
    } else if (data.type === "file") {
      // Single file
      content = await fetchFileContent(repo.owner, repo.repo, data.path, repo.branch);
    }

    // Cache the result
    await cacheDoc(cachePath, {
      content,
      fetchedAt: Date.now(),
      sha: Array.isArray(data) ? "dir" : data.sha,
    });

    return { content: filterContent(content, query), cached: false };
  } catch (error: any) {
    console.error(`[GitHub] Error fetching docs: ${error.message}`);

    // Fallback to cached version if available
    if (cached) {
      console.error(`[GitHub] Using stale cache as fallback`);
      return { content: filterContent(cached.content, query), cached: true };
    }

    throw error;
  }
}

/**
 * Fetch file content from GitHub
 */
async function fetchFileContent(
  owner: string,
  repo: string,
  filePath: string,
  branch?: string
): Promise<string> {
  const { data } = await octokit.rest.repos.getContent({
    owner,
    repo,
    path: filePath,
    ref: branch || "main",
  });

  if ("content" in data && data.content) {
    return Buffer.from(data.content, "base64").toString("utf-8");
  }

  return "";
}

/**
 * Search GitHub for repositories matching a query
 */
export async function searchGitHubRepos(query: string, limit: number = 10): Promise<GitHubRepo[]> {
  try {
    const { data } = await octokit.rest.search.repos({
      q: `${query} in:name,description,readme`,
      sort: "stars",
      order: "desc",
      per_page: limit,
    });

    return data.items
      .filter((item) => item.owner !== null)
      .map((item) => ({
        owner: item.owner!.login,
        repo: item.name,
        path: "README.md",
      }));
  } catch (error: any) {
    console.error(`[GitHub] Search error: ${error.message}`);
    return [];
  }
}

/**
 * Get cached documentation
 */
async function getCachedDoc(cachePath: string): Promise<CachedDoc | null> {
  try {
    const content = await fs.readFile(cachePath, "utf-8");
    return JSON.parse(content);
  } catch {
    return null;
  }
}

/**
 * Cache documentation
 */
async function cacheDoc(cachePath: string, doc: CachedDoc): Promise<void> {
  await fs.mkdir(path.dirname(cachePath), { recursive: true });
  await fs.writeFile(cachePath, JSON.stringify(doc, null, 2));
}

/**
 * Filter content based on query
 */
function filterContent(content: string, query?: string): string {
  if (!query || query.length < 5) {
    return content;
  }

  const queryLower = query.toLowerCase();
  const sections = content.split(/^#{1,3}\s+/m);

  // Find relevant sections
  const relevantSections = sections.filter((section) => {
    const sectionLower = section.toLowerCase();
    return sectionLower.includes(queryLower);
  });

  if (relevantSections.length > 0) {
    return relevantSections.join("\n\n## ");
  }

  return content;
}

/**
 * Update all cached repositories
 */
export async function updateAllCaches(): Promise<void> {
  console.error("[GitHub] Updating all cached repositories...");

  try {
    const cacheFiles = await fs.readdir(CACHE_DIR);

    for (const file of cacheFiles) {
      if (!file.endsWith(".json")) continue;

      const cachePath = path.join(CACHE_DIR, file);
      const cached = await getCachedDoc(cachePath);

      if (cached && Date.now() - cached.fetchedAt > CACHE_TTL) {
        // Parse repo info from filename
        const [owner, repo, ...pathParts] = file.replace(".json", "").split("_");

        try {
          await fetchGitHubDocs({
            owner,
            repo,
            path: pathParts.join("/") || undefined,
          });
          console.error(`[GitHub] Updated ${owner}/${repo}`);
        } catch (error: any) {
          console.error(`[GitHub] Failed to update ${owner}/${repo}: ${error.message}`);
        }
      }
    }

    console.error("[GitHub] Cache update complete");
  } catch (error: any) {
    console.error(`[GitHub] Error updating caches: ${error.message}`);
  }
}

/**
 * Clear all caches
 */
export async function clearAllCaches(): Promise<void> {
  try {
    await fs.rm(CACHE_DIR, { recursive: true, force: true });
    console.error("[GitHub] All caches cleared");
  } catch (error: any) {
    console.error(`[GitHub] Error clearing caches: ${error.message}`);
  }
}

/**
 * Alias for fetchGitHubDocs for backward compatibility
 */
export async function fetchDocumentation(
  owner: string,
  repo: string,
  path?: string,
  branch?: string
): Promise<string> {
  const result = await fetchGitHubDocs({ owner, repo, path, branch });
  return result.content;
}
