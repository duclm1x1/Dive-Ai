import { SearchResponse, SkillRequest, SkillResponse } from "./types.js";
/**
 * Search for libraries/skills using GitHub
 */
export declare function searchSkills(query: string, skillName: string): Promise<SearchResponse>;
/**
 * Fetch skill documentation from GitHub
 */
export declare function fetchSkillDocs(request: SkillRequest): Promise<SkillResponse>;
/**
 * Fetch n8n node documentation from GitHub
 */
export declare function fetchN8nNodeDocs(nodeName: string, operation?: string): Promise<SkillResponse>;
//# sourceMappingURL=api-github-old.d.ts.map