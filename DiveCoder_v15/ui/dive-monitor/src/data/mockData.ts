import type { 
  Run, 
  ExecutionStep, 
  ObservabilityEvent, 
  RAGChunk, 
  RAGQuery,
  Evidence,
  Claim,
  EvidencePack,
  RuntimeConfig,
  LiveMetrics 
} from '@/types/observability';

// Mock Runs
export const mockRuns: Run[] = [
  {
    run_id: 'run_001',
    type: 'review',
    status: 'RUNNING',
    start_time: Date.now() - 45000,
    workspace: 'my-project',
  },
  {
    run_id: 'run_002',
    type: 'resolve',
    status: 'COMPLETED',
    start_time: Date.now() - 180000,
    end_time: Date.now() - 120000,
    duration_ms: 60000,
    workspace: 'my-project',
  },
  {
    run_id: 'run_003',
    type: 'rag_ingest',
    status: 'COMPLETED',
    start_time: Date.now() - 300000,
    end_time: Date.now() - 280000,
    duration_ms: 20000,
    workspace: 'my-project',
  },
  {
    run_id: 'run_004',
    type: 'build',
    status: 'FAILED',
    start_time: Date.now() - 500000,
    end_time: Date.now() - 480000,
    duration_ms: 20000,
    workspace: 'my-project',
  },
];

// Mock Execution Steps
export const mockExecutionSteps: ExecutionStep[] = [
  {
    id: 'step_001',
    name: 'Router Decision',
    status: 'COMPLETED',
    start_time: Date.now() - 45000,
    end_time: Date.now() - 44500,
    duration_ms: 500,
    outputs: { route: 'code_review', confidence: 0.95 },
  },
  {
    id: 'step_002',
    name: 'Plan Generation',
    status: 'COMPLETED',
    start_time: Date.now() - 44500,
    end_time: Date.now() - 43000,
    duration_ms: 1500,
    outputs: { steps: 5, tools: ['file_read', 'grep', 'semantic_search'] },
  },
  {
    id: 'step_003',
    name: 'RAG Retrieval',
    status: 'RUNNING',
    start_time: Date.now() - 43000,
    tool_used: 'bm25',
    inputs: { query: 'authentication handler implementation' },
  },
  {
    id: 'step_004',
    name: 'Evidence Linking',
    status: 'QUEUED',
    start_time: 0,
  },
  {
    id: 'step_005',
    name: 'Report Generation',
    status: 'QUEUED',
    start_time: 0,
  },
];

// Mock Events
export const mockEvents: ObservabilityEvent[] = [
  {
    event_type: 'ROUTER_DECISION',
    run_id: 'run_001',
    payload: { route: 'code_review', confidence: 0.95, reasoning: 'User requested code review with specific file patterns' },
    timestamp: Date.now() - 45000,
  },
  {
    event_type: 'PLAN_GENERATED',
    run_id: 'run_001',
    payload: { steps: 5, estimated_time_ms: 30000, tools: ['file_read', 'grep', 'semantic_search'] },
    timestamp: Date.now() - 44500,
  },
  {
    event_type: 'RAG_RETRIEVAL',
    run_id: 'run_001',
    step: 'retrieve',
    tool: 'bm25',
    payload: { query: 'authentication handler implementation', top_k: 20, results_count: 15 },
    timestamp: Date.now() - 43000,
  },
  {
    event_type: 'TOOL_CALL',
    run_id: 'run_001',
    step: 'execute',
    tool: 'file_read',
    payload: { file: 'src/auth/handler.ts', bytes_read: 4520 },
    timestamp: Date.now() - 42000,
  },
];

// Mock RAG Data
export const mockRAGQuery: RAGQuery = {
  original: 'How does the authentication handler work?',
  enhanced: [
    'authentication handler implementation details',
    'auth middleware function signature',
    'JWT token validation process',
  ],
  step_back: 'What are the core authentication patterns in this codebase?',
};

export const mockRAGChunks: RAGChunk[] = [
  {
    id: 'chunk_001',
    source_file: 'src/auth/handler.ts',
    section: 'AuthHandler.validateToken',
    content: 'export async function validateToken(token: string): Promise<TokenPayload> {\n  const decoded = jwt.verify(token, process.env.JWT_SECRET);\n  return decoded as TokenPayload;\n}',
    score: 0.92,
    rank: 1,
    reason_selected: 'Direct match for authentication handler implementation',
    retrieval_method: 'bm25',
  },
  {
    id: 'chunk_002',
    source_file: 'src/auth/middleware.ts',
    section: 'authMiddleware',
    content: 'export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {\n  const token = req.headers.authorization?.split(" ")[1];\n  if (!token) return res.status(401).json({ error: "Unauthorized" });\n  // ...\n}',
    score: 0.87,
    rank: 2,
    reason_selected: 'Related middleware showing authentication flow',
    retrieval_method: 'bm25',
  },
  {
    id: 'chunk_003',
    source_file: 'src/types/auth.ts',
    section: 'TokenPayload interface',
    content: 'export interface TokenPayload {\n  userId: string;\n  email: string;\n  roles: string[];\n  exp: number;\n  iat: number;\n}',
    score: 0.78,
    rank: 3,
    reason_selected: 'Type definition referenced by handler',
    retrieval_method: 'graphrag',
  },
  {
    id: 'chunk_004',
    source_file: 'docs/authentication.md',
    section: 'Overview',
    content: '# Authentication\n\nThis project uses JWT-based authentication. Tokens are issued on login and validated on each request through the auth middleware.',
    score: 0.71,
    rank: 4,
    reason_selected: 'Documentation providing context',
    retrieval_method: 'raptor',
  },
];

// Mock Evidence & Claims
export const mockEvidence: Evidence[] = [
  {
    id: 'ev_001',
    type: 'snippet',
    source: 'src/auth/handler.ts:15-25',
    content: 'export async function validateToken(token: string): Promise<TokenPayload> {...}',
    metadata: { lines: '15-25', language: 'typescript' },
    created_at: Date.now() - 30000,
  },
  {
    id: 'ev_002',
    type: 'file',
    source: 'src/auth/middleware.ts',
    content: 'Full middleware implementation',
    metadata: { size_bytes: 2340, language: 'typescript' },
    created_at: Date.now() - 29000,
  },
  {
    id: 'ev_003',
    type: 'snippet',
    source: 'docs/authentication.md:1-10',
    content: '# Authentication\n\nThis project uses JWT-based authentication...',
    metadata: { lines: '1-10', language: 'markdown' },
    created_at: Date.now() - 28000,
  },
];

export const mockClaims: Claim[] = [
  {
    claim_id: 'claim_001',
    claim_text: 'The authentication handler uses JWT tokens for validation',
    supported_by: ['ev_001', 'ev_003'],
    confidence: 0.95,
    created_at: Date.now() - 25000,
  },
  {
    claim_id: 'claim_002',
    claim_text: 'Token validation occurs in the authMiddleware before request processing',
    supported_by: ['ev_002'],
    confidence: 0.88,
    created_at: Date.now() - 24000,
  },
  {
    claim_id: 'claim_003',
    claim_text: 'The TokenPayload interface defines user identity and permissions',
    supported_by: ['ev_001'],
    confidence: 0.92,
    created_at: Date.now() - 23000,
  },
];

export const mockEvidencePack: EvidencePack = {
  pack_id: 'pack_001',
  run_id: 'run_001',
  evidence: mockEvidence,
  claims: mockClaims,
  report: '## Code Review Summary\n\nThe authentication implementation follows security best practices...',
  created_at: Date.now() - 20000,
};

// Mock Runtime Config
export const mockRuntimeConfig: RuntimeConfig = {
  transport: 'stdio',
  llm_enabled: true,
  llm_status: 'enabled',
  rag: {
    max_context_chars: 128000,
    chunk_size: 1024,
    overlap: 128,
  },
};

// Mock Live Metrics
export const mockLiveMetrics: LiveMetrics = {
  total_duration_ms: 45000,
  tool_time_ms: 12000,
  llm_time_ms: 8000,
  context_usage_chars: 45000,
  max_context_chars: 128000,
  token_usage: {
    input: 15420,
    output: 3200,
  },
  latency: {
    p50: 120,
    p95: 450,
  },
};
