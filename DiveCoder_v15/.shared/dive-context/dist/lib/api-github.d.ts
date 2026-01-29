import { SkillDocs } from "./types.js";
/**
 * Fetch skill documentation for a library from GitHub
 */
export declare function fetchSkillDocs(libraryId: string): Promise<SkillDocs>;
/**
 * Search for libraries by query
 */
export declare function searchSkills(query: string): Promise<Array<{
    name: string;
    description: string;
    stars: number;
}>>;
//# sourceMappingURL=api-github.d.ts.map