import { createContext, useContext, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';
import { mockEvents, mockRuns, mockExecutionSteps, mockRAGQuery, mockRAGChunks, mockEvidence, mockClaims, mockEvidencePack, mockLiveMetrics } from '@/data/mockData';

interface EventStreamContextValue {
  isReplayMode: boolean;
  startReplay: () => void;
  stopReplay: () => void;
  sendCommand: (command: string, payload?: Record<string, unknown>) => void;
}

const EventStreamContext = createContext<EventStreamContextValue | null>(null);

export function useEventStream() {
  const ctx = useContext(EventStreamContext);
  if (!ctx) {
    throw new Error('useEventStream must be used within EventStreamProvider');
  }
  return ctx;
}

interface EventStreamProviderProps {
  children: ReactNode;
}

// Convert mock events to EventEnvelope format
function convertToEnvelope(event: typeof mockEvents[0], index: number): EventEnvelope {
  return {
    v: 1,
    seq: index + 1,
    ts: event.timestamp,
    run_id: event.run_id,
    type: event.event_type,
    step_id: event.step,
    payload: event.payload,
    explain: generateExplanation(event.event_type, event.payload),
  };
}

// Generate WHY explanations for events
function generateExplanation(eventType: string, payload: Record<string, unknown>): string {
  switch (eventType) {
    case 'ROUTER_DECISION':
      return `Routed to "${payload.route}" because: ${payload.reasoning || 'Pattern matched user intent with high confidence.'}`;
    case 'PLAN_GENERATED':
      return `Generated a ${payload.steps}-step plan using ${(payload.tools as string[])?.join(', ')} to efficiently complete the task within token budget.`;
    case 'RAG_RETRIEVAL':
      return `Used ${payload.tool} to search for "${payload.query}" and found ${payload.results_count} relevant chunks from the codebase.`;
    case 'TOOL_CALL':
      return `Called ${payload.tool} to read ${payload.file} (${payload.bytes_read} bytes) as it's directly relevant to the authentication implementation.`;
    case 'RAG_RERANK':
      return `Reranked ${payload.initial_count} chunks to ${payload.final_count} using cross-encoder model for higher precision context.`;
    case 'EVIDENCE_LINKED':
      return `Linked evidence from ${payload.source} to claim "${payload.claim}" with ${(payload.confidence as number * 100).toFixed(0)}% confidence.`;
    case 'CLAIM_CREATED':
      return `Created claim based on ${payload.evidence_count} pieces of evidence supporting the assertion.`;
    case 'REPORT_GENERATED':
      return `Synthesized ${payload.claims_count} claims into final report with ${payload.word_count} words.`;
    default:
      return 'Processing step completed as part of the execution plan.';
  }
}

export function EventStreamProvider({ children }: EventStreamProviderProps) {
  const replayIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const replayIndexRef = useRef(0);
  
  const { 
    setRuns, 
    setSteps, 
    processEventBatch, 
    setRagData, 
    setEvidenceData,
    setMetrics,
    setConnected,
    addEvent,
  } = useRuntimeStore();

  // Initialize with mock data
  useEffect(() => {
    setRuns(mockRuns);
    setSteps(mockExecutionSteps);
    setRagData(mockRAGQuery, mockRAGChunks);
    setEvidenceData(mockEvidence, mockClaims, mockEvidencePack);
    setMetrics(mockLiveMetrics);
    
    // Convert and add initial events
    const envelopes = mockEvents.map(convertToEnvelope);
    processEventBatch(envelopes);
  }, [setRuns, setSteps, processEventBatch, setRagData, setEvidenceData, setMetrics]);

  const startReplay = useCallback(() => {
    if (replayIntervalRef.current) return;
    
    replayIndexRef.current = 0;
    const envelopes = mockEvents.map(convertToEnvelope);
    
    replayIntervalRef.current = setInterval(() => {
      if (replayIndexRef.current < envelopes.length) {
        addEvent(envelopes[replayIndexRef.current]);
        replayIndexRef.current++;
      } else {
        if (replayIntervalRef.current) {
          clearInterval(replayIntervalRef.current);
          replayIntervalRef.current = null;
        }
      }
    }, 500);
  }, [addEvent]);

  const stopReplay = useCallback(() => {
    if (replayIntervalRef.current) {
      clearInterval(replayIntervalRef.current);
      replayIntervalRef.current = null;
    }
  }, []);

  const sendCommand = useCallback((command: string, payload?: Record<string, unknown>) => {
    console.log('[EventStream] Command:', command, payload);
    
    switch (command) {
      case 'pause':
        // Would send to backend
        break;
      case 'resume':
        // Would send to backend
        break;
      case 'cancel':
        // Would send to backend
        break;
      case 'rerun':
        // Would send to backend
        break;
      default:
        console.warn('Unknown command:', command);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (replayIntervalRef.current) {
        clearInterval(replayIntervalRef.current);
      }
    };
  }, []);

  const value: EventStreamContextValue = {
    isReplayMode: !!replayIntervalRef.current,
    startReplay,
    stopReplay,
    sendCommand,
  };

  return (
    <EventStreamContext.Provider value={value}>
      {children}
    </EventStreamContext.Provider>
  );
}
