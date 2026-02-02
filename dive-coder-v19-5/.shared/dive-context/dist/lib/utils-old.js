/**
 * Format search results for display
 */
export function formatSearchResults(response) {
    if (!response.results || response.results.length === 0) {
        return "No results found.";
    }
    return response.results
        .map((result, index) => {
        return `${index + 1}. **${result.name}**
   - ID: \`${result.id}\`
   - Description: ${result.description}
   - Examples: ${result.examples}
   - Rating: ${"⭐".repeat(Math.floor(result.rating))} (${result.rating}/5)
   - Updated: ${result.updated}`;
    })
        .join("\n\n");
}
/**
 * Extract code blocks from markdown content
 */
export function extractCodeBlocks(content) {
    const codeBlockRegex = /```[\s\S]*?```/g;
    const matches = content.match(codeBlockRegex);
    return matches || [];
}
/**
 * Truncate text to a maximum length
 */
export function truncate(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength) + "...";
}
//# sourceMappingURL=utils-old.js.map