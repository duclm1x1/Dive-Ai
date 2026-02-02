/**
 * Language Mapping for Non-Coder Friendly UI
 * Converts technical terms to plain English
 */

export const FRIENDLY_TERMS = {
  // Command types
  'review': 'Code Review',
  'build': 'Create Code',
  'resolve': 'Fix Issues',
  'search': 'Find Information',
  'rag_ingest': 'Learn Codebase',
  'status': 'Check Status',
  
  // Execution steps
  'router_decision': 'Planning Approach',
  'plan_generation': 'Creating Plan',
  'rag_retrieval': 'Searching Files',
  'rag_query': 'Looking Up Information',
  'code_generation': 'Writing Code',
  'validation': 'Checking Quality',
  'evidence_linking': 'Connecting Evidence',
  'report_generation': 'Creating Report',
  'tool_call': 'Using Tool',
  'thinking': 'Reasoning',
  
  // Status labels
  'RUNNING': 'In Progress',
  'COMPLETED': 'Done',
  'FAILED': 'Error',
  'QUEUED': 'Waiting',
  'PENDING': 'Waiting',
  
  // Metrics
  'tool_execution': 'Tool Time',
  'llm_processing': 'AI Thinking Time',
  'context_usage': 'Memory Used',
  'token_usage': 'Words Processed',
  'latency': 'Response Speed',
  
  // Technical terms
  'RAG': 'Smart Search',
  'LLM': 'AI',
  'JWT': 'Security Token',
  'API': 'Connection',
  'CLI': 'Command Tool',
  'SSE': 'Live Updates',
  'bm25': 'Text Search',
  'GraphRAG': 'Smart Search',
  'RAPTOR': 'Smart Search',
} as const;

export const FRIENDLY_DESCRIPTIONS = {
  'router_decision': 'Deciding the best way to help you',
  'plan_generation': 'Making a step-by-step plan',
  'rag_retrieval': 'Finding relevant code in your project',
  'code_generation': 'Writing new code for you',
  'validation': 'Making sure everything works correctly',
  'evidence_linking': 'Gathering proof and examples',
  'report_generation': 'Preparing your results',
  'thinking': 'Figuring out the solution',
  'tool_call': 'Using a specialized tool',
} as const;

export const FRIENDLY_ICONS = {
  'router_decision': '🧭',
  'plan_generation': '📋',
  'rag_retrieval': '🔍',
  'code_generation': '✍️',
  'validation': '✅',
  'evidence_linking': '🔗',
  'report_generation': '📄',
  'thinking': '💭',
  'tool_call': '🔧',
  'review': '👀',
  'build': '🏗️',
  'resolve': '🔧',
  'search': '🔎',
} as const;

/**
 * Convert technical term to friendly term
 */
export function toFriendly(term: string): string {
  const normalized = term.toLowerCase().replace(/[-_]/g, '_');
  return FRIENDLY_TERMS[normalized as keyof typeof FRIENDLY_TERMS] || term;
}

/**
 * Get friendly description for a step
 */
export function getFriendlyDescription(step: string): string {
  const normalized = step.toLowerCase().replace(/[-_]/g, '_');
  return FRIENDLY_DESCRIPTIONS[normalized as keyof typeof FRIENDLY_DESCRIPTIONS] || '';
}

/**
 * Get icon for a step or command
 */
export function getIcon(key: string): string {
  const normalized = key.toLowerCase().replace(/[-_]/g, '_');
  return FRIENDLY_ICONS[normalized as keyof typeof FRIENDLY_ICONS] || '📌';
}

/**
 * Format duration in human-readable way
 */
export function formatDuration(seconds: number): string {
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const minutes = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${minutes}m ${secs}s`;
}

/**
 * Format bytes in human-readable way
 */
export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
}

/**
 * Format numbers with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}
