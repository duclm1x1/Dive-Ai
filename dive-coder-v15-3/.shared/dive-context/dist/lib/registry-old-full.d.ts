import { GitHubRepo } from "./github.js";
/**
 * Expanded registry of 1000+ popular repositories for documentation
 * Organized by category for easy discovery
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
/**
 * Get total count of registered libraries
 */
export declare function getTotalLibraryCount(): number;
/**
 * Get libraries by category
 */
export declare function getLibrariesByCategory(): Record<string, string[]>;
//# sourceMappingURL=registry-old-full.d.ts.map