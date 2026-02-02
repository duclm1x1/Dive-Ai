import { create } from 'zustand';
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

// Event envelope type per spec
export interface EventEnvelope {
  v: number;           // Version
  seq: number;         // Sequence number for ordering
  ts: number;          // Timestamp
  run_id: string;
  trace_id?: string;
  span_id?: string;
  type: string;
  step_id?: string;
  payload: Record<string, unknown>;
  explain?: string;    // WHY explanation
}

// Helper function to calculate metrics from events
function calculateMetrics(events: EventEnvelope[]): LiveMetrics {
  const commandStarts = events.filter(e => e.type === 'COMMAND_START');
  const commandCompletes = events.filter(e => e.type === 'COMMAND_COMPLETE');
  
  let totalDuration = 0;
  if (commandStarts.length > 0 && commandCompletes.length > 0) {
    const lastStart = commandStarts[commandStarts.length - 1];
    const lastComplete = commandCompletes[commandCompletes.length - 1];
    totalDuration = (lastComplete.ts - lastStart.ts);
  }
  
  // Calculate tool execution time from step events
  const stepCompletes = events.filter(e => e.type === 'STEP_COMPLETE');
  const toolExecutionTime = stepCompletes.reduce((sum, e) => {
    const duration = (e.payload.duration as number) || 0;
    return sum + duration;
  }, 0);
  
  // Calculate LLM processing time (estimate from thinking events)
  const thinkingEvents = events.filter(e => e.type === 'THINKING');
  const llmProcessingTime = thinkingEvents.reduce((sum, e) => {
    const duration = (e.payload.duration as number) || 0;
    return sum + duration;
  }, 0);
  
  // Calculate context usage from RAG events
  const ragResults = events.filter(e => e.type === 'RAG_RESULT');
  const totalChunks = ragResults.reduce((sum, e) => {
    return sum + ((e.payload.results_count as number) || 0);
  }, 0);
  const estimatedTokens = totalChunks * 500; // Estimate 500 tokens per chunk
  
  return {
    total_duration_ms: totalDuration * 1000,
    tool_time_ms: toolExecutionTime * 1000,
    llm_time_ms: llmProcessingTime * 1000,
    context_usage_chars: estimatedTokens * 4,
    max_context_chars: 128000,
    token_usage: {
      input: estimatedTokens,
      output: Math.floor(estimatedTokens * 0.2),
    },
    latency: {
      p50: 120,
      p95: 450,
    },
  };
}

interface RuntimeState {
  // Connection state
  isConnected: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  
  // Current run state
  runs: Run[];
  selectedRunId: string | null;
  currentRun: Run | null;
  
  // Execution state
  steps: ExecutionStep[];
  events: EventEnvelope[];
  lastSeq: number;
  
  // RAG state
  ragQuery: RAGQuery | null;
  ragChunks: RAGChunk[];
  
  // Evidence state
  evidence: Evidence[];
  claims: Claim[];
  evidencePack: EvidencePack | null;
  
  // Runtime config
  config: RuntimeConfig | null;
  metrics: LiveMetrics | null;
  
  // UI state
  activeTab: string;
  selectedStepId: string | null;
  isWhyDrawerOpen: boolean;
  selectedEventForWhy: EventEnvelope | null;
  
  // Actions
  setConnected: (connected: boolean) => void;
  setRuns: (runs: Run[]) => void;
  selectRun: (runId: string) => void;
  setSteps: (steps: ExecutionStep[]) => void;
  addEvent: (event: EventEnvelope) => void;
  processEventBatch: (events: EventEnvelope[]) => void;
  setActiveTab: (tab: string) => void;
  selectStep: (stepId: string | null) => void;
  openWhyDrawer: (event: EventEnvelope) => void;
  closeWhyDrawer: () => void;
  setMetrics: (metrics: LiveMetrics) => void;
  setRagData: (query: RAGQuery, chunks: RAGChunk[]) => void;
  setEvidenceData: (evidence: Evidence[], claims: Claim[], pack: EvidencePack | null) => void;
  reset: () => void;
}

const initialState = {
  isConnected: true,
  connectionStatus: 'connected' as const,
  runs: [],
  selectedRunId: null,
  currentRun: null,
  steps: [],
  events: [],
  lastSeq: 0,
  ragQuery: null,
  ragChunks: [],
  evidence: [],
  claims: [],
  evidencePack: null,
  config: null,
  metrics: null,
  activeTab: 'dashboard',
  selectedStepId: null,
  isWhyDrawerOpen: false,
  selectedEventForWhy: null,
};

export const useRuntimeStore = create<RuntimeState>((set, get) => ({
  ...initialState,

  setConnected: (connected) => set({ 
    isConnected: connected,
    connectionStatus: connected ? 'connected' : 'disconnected'
  }),

  setRuns: (runs) => set({ runs }),

  selectRun: (runId) => {
    const state = get();
    const run = state.runs.find(r => r.run_id === runId);
    set({ selectedRunId: runId, currentRun: run || null });
  },

  setSteps: (steps) => set({ steps }),

  addEvent: (event) => {
    const state = get();
    // Handle out-of-order events by sorting on seq
    const events = [...state.events, event].sort((a, b) => a.seq - b.seq);
    const lastSeq = Math.max(state.lastSeq, event.seq);
    
    // Update runs based on event type
    let runs = [...state.runs];
    if (event.type === 'COMMAND_START') {
      const newRun: Run = {
        run_id: event.run_id,
        type: (event.payload.command as string || 'unknown') as any,
        status: 'RUNNING',
        start_time: event.ts,
        end_time: undefined,
      };
      runs = [newRun, ...runs];
    } else if (event.type === 'COMMAND_COMPLETE') {
      runs = runs.map(r => 
        r.run_id === event.run_id 
          ? { ...r, status: 'COMPLETED', end_time: event.ts }
          : r
      );
    } else if (event.type === 'COMMAND_ERROR') {
      runs = runs.map(r => 
        r.run_id === event.run_id 
          ? { ...r, status: 'FAILED', end_time: event.ts }
          : r
      );
    }
    
    // Update steps based on event type
    let steps = [...state.steps];
    if (event.type === 'ROUTER_DECISION') {
      steps.push({
        id: 'router_decision',
        name: 'Router Decision',
        status: 'COMPLETED',
        start_time: event.ts,
        end_time: event.ts + 0.5,
      });
    } else if (event.type === 'PLAN_GENERATED') {
      steps.push({
        id: 'plan_generation',
        name: 'Plan Generation',
        status: 'COMPLETED',
        start_time: event.ts,
        end_time: event.ts + 1.5,
      });
    } else if (event.type === 'RAG_QUERY') {
      steps.push({
        id: 'rag_retrieval',
        name: 'RAG Retrieval',
        status: 'RUNNING',
        start_time: event.ts,
      });
    } else if (event.type === 'RAG_RESULT') {
      steps = steps.map(s => 
        s.id === 'rag_retrieval'
          ? { ...s, status: 'COMPLETED', end_time: event.ts }
          : s
      );
    }
    
    // Calculate metrics from events
    const metrics = calculateMetrics(events);
    
    set({ events, lastSeq, runs, steps, metrics });
  },

  processEventBatch: (newEvents) => {
    const state = get();
    const allEvents = [...state.events, ...newEvents].sort((a, b) => a.seq - b.seq);
    // Dedupe by seq
    const deduped = allEvents.filter((e, i, arr) => 
      i === 0 || e.seq !== arr[i - 1].seq
    );
    const lastSeq = deduped.length > 0 ? deduped[deduped.length - 1].seq : 0;
    
    // Calculate metrics
    const metrics = calculateMetrics(deduped);
    
    set({ events: deduped, lastSeq, metrics });
  },

  setActiveTab: (tab) => set({ activeTab: tab }),

  selectStep: (stepId) => set({ selectedStepId: stepId }),

  openWhyDrawer: (event) => set({ 
    isWhyDrawerOpen: true, 
    selectedEventForWhy: event 
  }),

  closeWhyDrawer: () => set({ 
    isWhyDrawerOpen: false, 
    selectedEventForWhy: null 
  }),

  setMetrics: (metrics) => set({ metrics }),

  setRagData: (query, chunks) => set({ ragQuery: query, ragChunks: chunks }),

  setEvidenceData: (evidence, claims, pack) => set({ 
    evidence, 
    claims, 
    evidencePack: pack 
  }),

  reset: () => set(initialState),
}));

// Keyboard shortcut helpers
export const TAB_SHORTCUTS: Record<string, string> = {
  'a': 'activity',
  'r': 'rag',
  'e': 'evidence',
  's': 'settings',
};
