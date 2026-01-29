import fs from "fs/promises";
import path from "path";
const SKILLS_DIR = path.join(process.cwd(), "skills");
/**
 * Searches for skills matching the given query
 */
export async function searchSkills(query, skillName) {
    try {
        // Ensure skills directory exists
        await fs.mkdir(SKILLS_DIR, { recursive: true });
        // Read all skill directories
        const categories = await fs.readdir(SKILLS_DIR);
        const results = [];
        for (const category of categories) {
            const categoryPath = path.join(SKILLS_DIR, category);
            const stat = await fs.stat(categoryPath);
            if (!stat.isDirectory())
                continue;
            const skills = await fs.readdir(categoryPath);
            for (const skill of skills) {
                const skillPath = path.join(categoryPath, skill);
                const skillStat = await fs.stat(skillPath);
                if (!skillStat.isDirectory())
                    continue;
                // Read SKILL.md
                const skillMdPath = path.join(skillPath, "SKILL.md");
                try {
                    const skillContent = await fs.readFile(skillMdPath, "utf-8");
                    // Extract metadata from SKILL.md
                    const nameMatch = skillContent.match(/^#\s+(.+)$/m);
                    const descMatch = skillContent.match(/^##\s+Description\s*\n(.+)$/m);
                    const skillData = {
                        id: `/${category}/${skill}`,
                        name: nameMatch ? nameMatch[1] : skill,
                        description: descMatch ? descMatch[1] : "No description available",
                        examples: (skillContent.match(/```/g) || []).length / 2, // Count code blocks
                        rating: 5.0, // Default rating
                        updated: skillStat.mtime.toISOString().split("T")[0],
                    };
                    // Simple relevance scoring
                    const lowerSkillName = skillName.toLowerCase();
                    const lowerName = skillData.name.toLowerCase();
                    const lowerDesc = skillData.description.toLowerCase();
                    if (lowerName.includes(lowerSkillName) ||
                        lowerDesc.includes(lowerSkillName) ||
                        skill.includes(lowerSkillName)) {
                        results.push(skillData);
                    }
                }
                catch (e) {
                    // Skip skills without SKILL.md
                    continue;
                }
            }
        }
        // Sort by relevance (exact match first, then partial)
        results.sort((a, b) => {
            const aExact = a.name.toLowerCase() === skillName.toLowerCase();
            const bExact = b.name.toLowerCase() === skillName.toLowerCase();
            if (aExact && !bExact)
                return -1;
            if (!aExact && bExact)
                return 1;
            return b.rating - a.rating;
        });
        return { results };
    }
    catch (error) {
        return {
            results: [],
            error: `Error searching skills: ${error}`,
        };
    }
}
/**
 * Fetches skill documentation
 */
export async function fetchSkillDocs(request) {
    try {
        const skillPath = path.join(SKILLS_DIR, request.skillId);
        const skillMdPath = path.join(skillPath, "SKILL.md");
        const skillContent = await fs.readFile(skillMdPath, "utf-8");
        // Simple query-based filtering (extract relevant sections)
        const sections = skillContent.split(/^##\s+/m);
        let relevantContent = skillContent;
        // If query is specific, try to find relevant sections
        if (request.query && request.query.length > 10) {
            const queryLower = request.query.toLowerCase();
            const relevantSections = sections.filter((section) => section.toLowerCase().includes(queryLower));
            if (relevantSections.length > 0) {
                relevantContent = relevantSections.join("\n\n## ");
            }
        }
        return { data: relevantContent };
    }
    catch (error) {
        return {
            data: `Error fetching skill documentation: ${error}\n\nThe skill ID '${request.skillId}' may not exist. Use 'resolve-skill-id' to find available skills.`,
        };
    }
}
/**
 * Fetches n8n node documentation
 */
export async function fetchN8nNodeDocs(nodeName, operation) {
    try {
        // Check if we have local n8n node docs
        const n8nDocsPath = path.join(SKILLS_DIR, "n8n", "nodes", `${nodeName}.md`);
        try {
            const nodeContent = await fs.readFile(n8nDocsPath, "utf-8");
            // If operation is specified, filter to that section
            if (operation) {
                const operationSection = nodeContent
                    .split(/^##\s+/m)
                    .find((section) => section.toLowerCase().includes(operation.toLowerCase()));
                if (operationSection) {
                    return { data: `## ${operationSection}` };
                }
            }
            return { data: nodeContent };
        }
        catch {
            // Fallback: Generate basic documentation
            return {
                data: `# ${nodeName} Node Documentation

## Overview
The ${nodeName} node is used in n8n workflows for ${nodeName.toLowerCase()} operations.

## Common Operations
${operation ? `- ${operation}` : "- Various operations available"}

## Parameters
Please refer to the official n8n documentation at https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.${nodeName.toLowerCase()}/

## Example
\`\`\`json
{
  "nodes": [
    {
      "parameters": {},
      "name": "${nodeName}",
      "type": "n8n-nodes-base.${nodeName.toLowerCase()}",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ]
}
\`\`\`

## Best Practices
- Configure authentication properly
- Handle errors with proper error handling
- Test with sample data before production

For more details, visit: https://docs.n8n.io`,
            };
        }
    }
    catch (error) {
        return {
            data: `Error fetching n8n node documentation: ${error}`,
        };
    }
}
//# sourceMappingURL=api.js.map