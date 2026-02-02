import { SearchResponse, SkillRequest, SkillResponse, N8nNodeDocsResponse } from "./types.js";
/**
 * Searches for skills matching the given query
 */
export declare function searchSkills(query: string, skillName: string): Promise<SearchResponse>;
/**
 * Fetches skill documentation
 */
export declare function fetchSkillDocs(request: SkillRequest): Promise<SkillResponse>;
/**
 * Fetches n8n node documentation
 */
export declare function fetchN8nNodeDocs(nodeName: string, operation?: string): Promise<N8nNodeDocsResponse>;
//# sourceMappingURL=api.d.ts.map