#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import { fetchSkillDocs } from "./lib/api-github.js";
import { validateContent } from "./lib/security.js";
import { listAllLibraries, searchLibraries, listCategories } from "./lib/registry.js";
const server = new Server({
    name: "dive-context",
    version: "1.0.0",
}, {
    capabilities: {
        tools: {},
    },
});
// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "list_libraries",
                description: "List all 100+ popular libraries ranked by stars/forks",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
            {
                name: "search_libraries",
                description: "Search libraries by name, tags, category, or description",
                inputSchema: {
                    type: "object",
                    properties: {
                        query: {
                            type: "string",
                            description: "Search query (e.g., 'react', 'database', 'testing')",
                        },
                    },
                    required: ["query"],
                },
            },
            {
                name: "fetch_docs",
                description: "Fetch documentation for a specific library from GitHub",
                inputSchema: {
                    type: "object",
                    properties: {
                        library: {
                            type: "string",
                            description: "Library name (e.g., 'nextjs', 'fastapi', 'prisma')",
                        },
                    },
                    required: ["library"],
                },
            },
            {
                name: "list_categories",
                description: "List all available library categories",
                inputSchema: {
                    type: "object",
                    properties: {},
                },
            },
        ],
    };
});
// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    try {
        switch (name) {
            case "list_libraries": {
                const libraries = listAllLibraries();
                const formatted = libraries
                    .map((lib, i) => `${i + 1}. ${lib.name} (${lib.stars.toLocaleString()} ⭐) - ${lib.category}`)
                    .join("\n");
                return {
                    content: [
                        {
                            type: "text",
                            text: `Top 100 Popular Libraries:\n\n${formatted}`,
                        },
                    ],
                };
            }
            case "search_libraries": {
                const query = args?.query || "";
                const results = searchLibraries(query);
                if (results.length === 0) {
                    return {
                        content: [
                            {
                                type: "text",
                                text: `No libraries found for query: "${query}"`,
                            },
                        ],
                    };
                }
                const formatted = results
                    .slice(0, 10)
                    .map((r, i) => `${i + 1}. ${r.name} (${r.meta.stars.toLocaleString()} ⭐)\n   ${r.meta.description}\n   Category: ${r.meta.category}\n   Tags: ${r.meta.tags.join(", ")}`)
                    .join("\n\n");
                return {
                    content: [
                        {
                            type: "text",
                            text: `Search Results for "${query}":\n\n${formatted}`,
                        },
                    ],
                };
            }
            case "fetch_docs": {
                const library = args?.library || "";
                const docs = await fetchSkillDocs(library);
                // Validate content
                const validation = await validateContent(docs.content);
                if (!validation.safe) {
                    return {
                        content: [
                            {
                                type: "text",
                                text: `⚠️ Security Warning: ${validation.reason}\n\nDocumentation fetch aborted for safety.`,
                            },
                        ],
                        isError: true,
                    };
                }
                return {
                    content: [
                        {
                            type: "text",
                            text: `# ${docs.libraryName}\n\n${docs.description}\n\n**Category:** ${docs.category}\n**Stars:** ${docs.stars.toLocaleString()} ⭐\n**Tags:** ${docs.tags.join(", ")}\n\n---\n\n${docs.content}`,
                        },
                    ],
                };
            }
            case "list_categories": {
                const categories = listCategories();
                return {
                    content: [
                        {
                            type: "text",
                            text: `Available Categories:\n\n${categories.map((c, i) => `${i + 1}. ${c}`).join("\n")}`,
                        },
                    ],
                };
            }
            default:
                return {
                    content: [
                        {
                            type: "text",
                            text: `Unknown tool: ${name}`,
                        },
                    ],
                    isError: true,
                };
        }
    }
    catch (error) {
        return {
            content: [
                {
                    type: "text",
                    text: `Error: ${error.message}`,
                },
            ],
            isError: true,
        };
    }
});
// Start server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Dive-Context MCP server running on stdio");
}
main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
});
//# sourceMappingURL=index-github.js.map