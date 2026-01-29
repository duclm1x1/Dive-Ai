/**
 * GitHub repository configuration
 */
export interface GitHubRepo {
    owner: string;
    repo: string;
    path?: string;
    branch?: string;
}
/**
 * Fetch documentation from a GitHub repository
 */
export declare function fetchGitHubDocs(repo: GitHubRepo, query?: string): Promise<{
    content: string;
    cached: boolean;
}>;
/**
 * Search GitHub for repositories matching a query
 */
export declare function searchGitHubRepos(query: string, limit?: number): Promise<GitHubRepo[]>;
/**
 * Update all cached repositories
 */
export declare function updateAllCaches(): Promise<void>;
/**
 * Clear all caches
 */
export declare function clearAllCaches(): Promise<void>;
/**
 * Alias for fetchGitHubDocs for backward compatibility
 */
export declare function fetchDocumentation(owner: string, repo: string, path?: string, branch?: string): Promise<string>;
//# sourceMappingURL=github.d.ts.map