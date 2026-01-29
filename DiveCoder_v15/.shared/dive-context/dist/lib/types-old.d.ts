export interface SearchResponse {
    results: Array<{
        id: string;
        name: string;
        description: string;
        examples: number;
        rating: number;
        updated: string;
    }>;
    error?: string;
}
export interface SkillRequest {
    skillId?: string;
    libraryId?: string;
    query: string;
}
export interface SkillResponse {
    data: string;
}
export interface N8nNodeDocsResponse {
    data: string;
}
export interface ValidationResult {
    safe: boolean;
    reason: string;
    confidence: number;
}
//# sourceMappingURL=types-old.d.ts.map