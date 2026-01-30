import { GitHubRepo } from "./github.js";
/**
 * Skill documentation structure
 */
export interface SkillDocs {
    libraryId: string;
    libraryName: string;
    description: string;
    category: string;
    tags: string[];
    stars: number;
    content: string;
    repos: GitHubRepo[];
    lastUpdated: string;
}
/**
 * Security validation result
 */
export interface SecurityValidationResult {
    safe: boolean;
    reason?: string;
    confidence: number;
}
//# sourceMappingURL=types.d.ts.map