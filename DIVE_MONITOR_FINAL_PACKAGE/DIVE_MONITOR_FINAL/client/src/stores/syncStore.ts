import { create } from 'zustand';

export interface SyncSession {
  id: string;
  clientId: string;
  clientType: string;
  status: 'initialized' | 'connected' | 'disconnected' | 'paused' | 'running' | 'cancelled';
  createdAt: number;
  lastActivity: number;
  diveCoderConnected: boolean;
  diveMonitorConnected: number;
  eventCount: number;
}

export interface SyncMetrics {
  total_duration_ms?: number;
  tool_time_ms?: number;
  llm_time_ms?: number;
  context_usage_chars?: number;
  max_context_chars?: number;
  token_usage?: {
    input: number;
    output: number;
  };
  latency?: {
    p50: number;
    p95: number;
  };
  updatedAt?: number;
}

export interface SyncConfig {
  [key: string]: any;
  updatedAt?: number;
}

export interface SyncEvent {
  type: string;
  payload: Record<string, unknown>;
  run_id?: string;
  trace_id?: string;
  span_id?: string;
  step_id?: string;
  explain?: string;
  timestamp?: number;
  source?: string;
  sessionId?: string;
  addedAt?: number;
}

export interface SyncState {
  // Connection state
  isConnected: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
  websocketUrl: string;
  sessionId: string | null;
  clientId: string | null;

  // Session info
  session: SyncSession | null;

  // Sync data
  metrics: SyncMetrics | null;
  config: SyncConfig | null;
  events: SyncEvent[];
  lastEventCount: number;

  // UI state
  isSyncPanelOpen: boolean;
  showSyncDetails: boolean;
  selectedEventId: number | null;

  // Actions
  setConnected: (connected: boolean) => void;
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'connecting') => void;
  setSession: (session: SyncSession | null) => void;
  setMetrics: (metrics: SyncMetrics) => void;
  setConfig: (config: SyncConfig) => void;
  addEvent: (event: SyncEvent) => void;
  setEvents: (events: SyncEvent[]) => void;
  clearEvents: () => void;
  setWebsocketUrl: (url: string) => void;
  setSessionId: (id: string) => void;
  setClientId: (id: string) => void;
  toggleSyncPanel: () => void;
  setSyncPanelOpen: (open: boolean) => void;
  toggleSyncDetails: () => void;
  selectEvent: (index: number | null) => void;
  reset: () => void;
}

const initialState = {
  isConnected: false,
  connectionStatus: 'disconnected' as const,
  websocketUrl: 'ws://localhost:8787',
  sessionId: null,
  clientId: null,
  session: null,
  metrics: null,
  config: null,
  events: [],
  lastEventCount: 0,
  isSyncPanelOpen: false,
  showSyncDetails: false,
  selectedEventId: null,
};

export const useSyncStore = create<SyncState>((set, get) => ({
  ...initialState,

  setConnected: (connected) =>
    set({
      isConnected: connected,
      connectionStatus: connected ? 'connected' : 'disconnected',
    }),

  setConnectionStatus: (status) => set({ connectionStatus: status }),

  setSession: (session) => set({ session }),

  setMetrics: (metrics) =>
    set({
      metrics: {
        ...get().metrics,
        ...metrics,
        updatedAt: Date.now(),
      },
    }),

  setConfig: (config) =>
    set({
      config: {
        ...get().config,
        ...config,
        updatedAt: Date.now(),
      },
    }),

  addEvent: (event) => {
    const state = get();
    const newEvents = [...state.events, event];

    // Keep only last 1000 events in memory
    if (newEvents.length > 1000) {
      newEvents.shift();
    }

    set({
      events: newEvents,
      lastEventCount: state.lastEventCount + 1,
    });
  },

  setEvents: (events) => set({ events }),

  clearEvents: () => set({ events: [], lastEventCount: 0 }),

  setWebsocketUrl: (url) => set({ websocketUrl: url }),

  setSessionId: (id) => set({ sessionId: id }),

  setClientId: (id) => set({ clientId: id }),

  toggleSyncPanel: () =>
    set((state) => ({
      isSyncPanelOpen: !state.isSyncPanelOpen,
    })),

  setSyncPanelOpen: (open) => set({ isSyncPanelOpen: open }),

  toggleSyncDetails: () =>
    set((state) => ({
      showSyncDetails: !state.showSyncDetails,
    })),

  selectEvent: (index) => set({ selectedEventId: index }),

  reset: () => set(initialState),
}));
