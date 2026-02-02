#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { Command } from "commander";
import { searchSkills, fetchSkillDocs, fetchN8nNodeDocs } from "./lib/api.js";
import { validateSkillSafety } from "./lib/security.js";
import { formatSearchResults } from "./lib/utils.js";
const SERVER_VERSION = "1.0.0";
// Parse CLI arguments
const program = new Command()
    .option("--transport <stdio|http>", "transport type", "stdio")
    .option("--port <number>", "port for HTTP transport", "3000")
    .option("--api-key <key>", "API key for authentication")
    .parse(process.argv);
const cliOptions = program.opts();
const TRANSPORT_TYPE = cliOptions.transport;
const API_KEY = cliOptions.apiKey || process.env.DIVE_CONTEXT_API_KEY;
/**
 * Create the Dive-Context MCP Server
 */
function createServer() {
    const server = new McpServer({
        name: "Dive-Context",
        version: SERVER_VERSION,
    }, {
        instructions: "Use this server to retrieve up-to-date documentation, code examples, and workflow patterns for Dive Coder v14, n8n, and automation tools.",
    });
    // ============================================================
    // TOOL 1: resolve-skill-id
    // ============================================================
    server.registerTool("resolve-skill-id", {
        title: "Resolve Dive Coder Skill ID",
        description: `Resolves a skill name to a Dive-Context-compatible skill ID and returns matching skills.

You MUST call this function before 'query-skill-docs' to obtain a valid skill ID UNLESS the user explicitly provides a skill ID in the format '/category/skill-name'.

Selection Process:
1. Analyze the query to understand what skill/library the user is looking for
2. Return the most relevant match based on:
   - Name similarity to the query
   - Description relevance
   - Usage count (prioritize popular skills)
   - Recency (last updated date)
   - Community rating

Response Format:
- Return the selected skill ID in a clearly marked section
- Provide a brief explanation for why this skill was chosen
- If multiple good matches exist, acknowledge this but proceed with the most relevant one

IMPORTANT: Do not call this tool more than 3 times per question.`,
        inputSchema: {
            query: z
                .string()
                .describe("The user's original question or task. Used to rank skill results by relevance."),
            skillName: z
                .string()
                .describe("Skill or library name to search for (e.g., 'telegram-bot', 'n8n-supabase', 'nextjs')"),
        },
        annotations: {
            readOnlyHint: true,
        },
    }, async ({ query, skillName }) => {
        const searchResponse = await searchSkills(query, skillName);
        if (!searchResponse.results || searchResponse.results.length === 0) {
            return {
                content: [
                    {
                        type: "text",
                        text: searchResponse.error || "No skills found matching the provided name.",
                    },
                ],
            };
        }
        const resultsText = formatSearchResults(searchResponse);
        const responseText = `Available Skills:

Each result includes:
- Skill ID: Dive-Context-compatible identifier (format: /category/skill-name)
- Name: Skill or library name
- Description: Short summary
- Examples: Number of available code examples
- Rating: Community rating (1-5 stars)
- Updated: Last update date

----------

${resultsText}`;
        return {
            content: [
                {
                    type: "text",
                    text: responseText,
                },
            ],
        };
    });
    // ============================================================
    // TOOL 2: query-skill-docs
    // ============================================================
    server.registerTool("query-skill-docs", {
        title: "Query Skill Documentation",
        description: `Retrieves and queries up-to-date documentation and code examples from Dive-Context for any Dive Coder skill, n8n workflow, or automation tool.

You must call 'resolve-skill-id' first to obtain the exact skill ID required to use this tool, UNLESS the user explicitly provides a skill ID in the format '/category/skill-name'.

IMPORTANT: Do not call this tool more than 3 times per question.`,
        inputSchema: {
            skillId: z
                .string()
                .describe("Exact Dive-Context-compatible skill ID (e.g., '/n8n/telegram-bot', '/automation/webhook-handler') retrieved from 'resolve-skill-id' or directly from user query."),
            query: z
                .string()
                .describe("The question or task you need help with. Be specific. Good: 'How to handle Telegram inline keyboards in n8n'. Bad: 'keyboards'."),
        },
        annotations: {
            readOnlyHint: true,
        },
    }, async ({ query, skillId }) => {
        const response = await fetchSkillDocs({ query, skillId });
        return {
            content: [
                {
                    type: "text",
                    text: response.data,
                },
            ],
        };
    });
    // ============================================================
    // TOOL 3: fetch-n8n-node-docs
    // ============================================================
    server.registerTool("fetch-n8n-node-docs", {
        title: "Fetch n8n Node Documentation",
        description: `Retrieves documentation for a specific n8n node and operation.

Use this tool when you need detailed information about:
- n8n node parameters
- Operation-specific examples
- Best practices for node configuration
- Common error solutions`,
        inputSchema: {
            nodeName: z
                .string()
                .describe("n8n node name (e.g., 'Telegram', 'HTTP Request', 'Code', 'Supabase')"),
            operation: z
                .string()
                .optional()
                .describe("Specific operation (e.g., 'sendMessage', 'get', 'post'). Optional."),
        },
        annotations: {
            readOnlyHint: true,
        },
    }, async ({ nodeName, operation }) => {
        const response = await fetchN8nNodeDocs(nodeName, operation);
        return {
            content: [
                {
                    type: "text",
                    text: response.data,
                },
            ],
        };
    });
    // ============================================================
    // TOOL 4: validate-skill-safety (Admin only)
    // ============================================================
    server.registerTool("validate-skill-safety", {
        title: "Validate Skill Safety (Admin)",
        description: `Validates a skill for prompt injection and security issues using LLM-based analysis.

This tool is used by administrators to check skills before adding them to the repository.

Returns:
- safe: boolean
- reason: explanation
- confidence: 0.0-1.0`,
        inputSchema: {
            skillContent: z
                .string()
                .describe("The complete skill content (SKILL.md file) to validate"),
        },
        annotations: {
            readOnlyHint: true,
        },
    }, async ({ skillContent }) => {
        const validation = await validateSkillSafety(skillContent);
        const responseText = `Skill Safety Validation Result:

Safe: ${validation.safe ? "✅ Yes" : "❌ No"}
Confidence: ${(validation.confidence * 100).toFixed(1)}%
Reason: ${validation.reason}

${validation.safe ? "This skill is safe to add to the repository." : "This skill contains security issues and should NOT be added."}`;
        return {
            content: [
                {
                    type: "text",
                    text: responseText,
                },
            ],
        };
    });
    return server;
}
async function main() {
    const server = createServer();
    if (TRANSPORT_TYPE === "stdio") {
        const transport = new StdioServerTransport();
        await server.connect(transport);
        console.error("Dive-Context MCP server running on stdio");
    }
    else if (TRANSPORT_TYPE === "http") {
        // HTTP transport implementation (similar to Context7)
        console.error("HTTP transport not yet implemented. Use stdio for now.");
        process.exit(1);
    }
}
main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map