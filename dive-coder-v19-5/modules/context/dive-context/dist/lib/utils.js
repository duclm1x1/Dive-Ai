/**
 * Format search results for display
 */
export function formatSearchResults(results) {
    if (results.length === 0) {
        return "No results found.";
    }
    return results
        .map((result, index) => {
        return `${index + 1}. ${result.name} (${result.stars} ⭐)\n   ${result.description}`;
    })
        .join("\n\n");
}
/**
 * Truncate text to a maximum length
 */
export function truncate(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substring(0, maxLength - 3) + "...";
}
/**
 * Sleep for a given number of milliseconds
 */
export function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}
//# sourceMappingURL=utils.js.map