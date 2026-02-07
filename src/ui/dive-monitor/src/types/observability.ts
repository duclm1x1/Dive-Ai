// Dive Coder Observability Types

export type RunStatus = 'QUEUED' | 'RUNNING' | 'WAITING' | 'COMPLETED' | 'FAILED';
export type RunType = 'review' | 'resolve' | 'build' | 'rag_ingest' | 'rag_eval';

export interface Run {
  run_id: string;
  type: RunType;
  status: RunStatus;
  start_time: number;
  end_time?: number;
  duration_ms?: number;
  workspace?: string;
}

export interface ExecutionStep {
  id: string;
  name: string;
  status: RunStatus;
  start_time: number;
  end_time?: number;
  duration_ms?: number;
  inputs?: Record<string, unknown>;
  outputs?: Record<string, unknown>;
  tool_used?: string;
  llm_used?: string;
}

export type EventType = 
  | 'ROUTER_DECISION'
  | 'PLAN_GENERATED'
  | 'STEP_STARTED'
  | 'STEP_COMPLETED'
  | 'RAG_RETRIEVAL'
  | 'RAG_RERANK'
  | 'TOOL_CALL'
  | 'LLM_CALL'
  | 'EVIDENCE_LINKED'
  | 'CLAIM_CREATED'
  | 'REPORT_GENERATED'
  | 'ERROR';

export interface ObservabilityEvent {
  event_type: EventType;
  run_id: string;
  step?: string;
  tool?: string;
  payload: Record<string, unknown>;
  timestamp: number;
}

export interface RAGChunk {
  id: string;
  source_file: string;
  section: string;
  content: string;
  score: number;
  rank: number;
  reason_selected: string;
  retrieval_method: 'bm25' | 'graphrag' | 'raptor';
}

export interface RAGQuery {
  original: string;
  enhanced: string[];
  step_back?: string;
}

export interface Evidence {
  id: string;
  type: 'file' | 'snippet' | 'url' | 'generated';
  source: string;
  content: string;
  metadata: Record<string, unknown>;
  created_at: number;
}

export interface Claim {
  claim_id: string;
  claim_text: string;
  supported_by: string[];
  confidence: number;
  created_at: number;
}

export interface EvidencePack {
  pack_id: string;
  run_id: string;
  evidence: Evidence[];
  claims: Claim[];
  report?: string;
  created_at: number;
}

export interface RuntimeConfig {
  transport: 'stdio';
  llm_enabled: boolean;
  llm_status: 'enabled' | 'skipped';
  rag: {
    max_context_chars: number;
    chunk_size: number;
    overlap: number;
  };
}

export interface LiveMetrics {
  total_duration_ms: number;
  tool_time_ms: number;
  llm_time_ms: number;
  context_usage_chars: number;
  max_context_chars: number;
  token_usage?: {
    input: number;
    output: number;
  };
  latency: {
    p50: number;
    p95: number;
  };
}
