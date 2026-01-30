import { ValidationResult } from "./types.js";
/**
 * Validate skill content for prompt injection and security issues
 */
export declare function validateSkillSafety(skillContent: string): Promise<ValidationResult>;
/**
 * Quick pattern-based validation (fallback when LLM is not available)
 */
export declare function quickValidate(content: string): ValidationResult;
//# sourceMappingURL=security-old.d.ts.map