import { GitHubRepo } from "./github.js";
/**
 * Registry of popular repositories for documentation
 */
export declare const REPO_REGISTRY: Record<string, GitHubRepo[]>;
/**
 * Get repositories for a library name
 */
export declare function getReposForLibrary(libraryName: string): GitHubRepo[];
/**
 * Add a custom repository to the registry
 */
export declare function addCustomRepo(libraryName: string, repo: GitHubRepo): void;
/**
 * List all registered libraries
 */
export declare function listAllLibraries(): string[];
//# sourceMappingURL=registry-old.d.ts.map