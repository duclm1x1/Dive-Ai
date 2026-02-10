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
  activeTab: 'activity',
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
    const runs = get().runs;
    const run = runs.find(r => r.run_id === runId) || null;
    set({ selectedRunId: runId, currentRun: run });
  },

  setSteps: (steps) => set({ steps }),

  addEvent: (event) => {
    const state = get();
    // Handle out-of-order events by sorting on seq
    const events = [...state.events, event].sort((a, b) => a.seq - b.seq);
    const lastSeq = Math.max(state.lastSeq, event.seq);
    set({ events, lastSeq });
  },

  processEventBatch: (newEvents) => {
    const state = get();
    const allEvents = [...state.events, ...newEvents].sort((a, b) => a.seq - b.seq);
    // Dedupe by seq
    const deduped = allEvents.filter((e, i, arr) => 
      i === 0 || e.seq !== arr[i - 1].seq
    );
    const lastSeq = deduped.length > 0 ? deduped[deduped.length - 1].seq : 0;
    set({ events: deduped, lastSeq });
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
