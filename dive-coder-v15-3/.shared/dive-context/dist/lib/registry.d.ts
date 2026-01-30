import { GitHubRepo } from "./github.js";
/**
 * Library metadata with popularity metrics
 */
export interface LibraryMeta {
    repos: GitHubRepo[];
    description: string;
    stars: number;
    category: string;
    tags: string[];
}
/**
 * Top 100 most popular libraries curated by stars/forks
 * Each entry includes metadata for advanced search and ranking
 */
export declare const POPULAR_LIBRARIES: Record<string, LibraryMeta>;
/**
 * Get library metadata by name
 */
export declare function getLibraryMeta(libraryName: string): LibraryMeta | undefined;
/**
 * Search libraries by tags, description, or category
 */
export declare function searchLibraries(query: string): Array<{
    name: string;
    meta: LibraryMeta;
    score: number;
}>;
/**
 * Get top libraries by category
 */
export declare function getLibrariesByCategory(category: string): Array<{
    name: string;
    meta: LibraryMeta;
}>;
/**
 * List all categories
 */
export declare function listCategories(): string[];
/**
 * Get total count of popular libraries
 */
export declare function getTotalLibraryCount(): number;
/**
 * List all libraries sorted by stars
 */
export declare function listAllLibraries(): Array<{
    name: string;
    stars: number;
    category: string;
}>;
//# sourceMappingURL=registry.d.ts.map