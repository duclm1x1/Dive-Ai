/**
 * Format search results for display
 */
export function formatSearchResults(results: any[]): string {
  if (results.length === 0) {
    return "No results found.";
  }

  return results
    .map((result: any, index: number) => {
      return `${index + 1}. ${result.name} (${result.stars} ⭐)\n   ${result.description}`;
    })
    .join("\n\n");
}

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength - 3) + "...";
}

/**
 * Sleep for a given number of milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
