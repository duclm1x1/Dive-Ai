import { createContext, useContext, useEffect, useCallback, useRef, type ReactNode } from 'react';
import { useRuntimeStore, type EventEnvelope } from '@/stores/runtimeStore';

const MONITOR_SERVER_URL = import.meta.env.VITE_MONITOR_SERVER_URL || 'http://localhost:8787';

interface EventStreamContextValue {
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



export function EventStreamProvider({ children }: EventStreamProviderProps) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  
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

  // Load historical events on mount
  useEffect(() => {
    const loadHistoricalEvents = async () => {
      try {
        const response = await fetch(`${MONITOR_SERVER_URL}/v1/events?limit=100`, {
          signal: AbortSignal.timeout(5000) // 5 second timeout
        });
        if (response.ok) {
          const data = await response.json();
          const envelopes = data.events.map((event: any, index: number) => ({
            v: 1,
            seq: index + 1,
            ts: event.timestamp,
            run_id: event.run_id,
            type: event.event_type.toUpperCase(),
            step_id: event.data?.step_id || 'unknown',
            payload: event.data || {},
            explain: event.message,
          }));
          processEventBatch(envelopes);
          console.log('[EventStream] Loaded', envelopes.length, 'historical events');
        }
      } catch (err) {
        // Silently fail if monitor server not available
        console.warn('[EventStream] Monitor server not available, running in demo mode');
      }
    };
    
    loadHistoricalEvents();
  }, [processEventBatch]);

  // Connect to real monitor server
  useEffect(() => {
    const connect = () => {
      try {
        const eventSource = new EventSource(`${MONITOR_SERVER_URL}/v1/stream/events`);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
          console.log('[EventStream] Connected to monitor server');
          setConnected(true);
        };

        eventSource.onmessage = (e) => {
          try {
            const event = JSON.parse(e.data);
            console.log('[EventStream] Real event received:', event);
            
            // Convert DiveCoder event to EventEnvelope format
            const envelope: EventEnvelope = {
              v: 1,
              seq: Date.now(),
              ts: event.timestamp,
              run_id: event.run_id,
              type: event.event_type.toUpperCase(),
              step_id: event.data?.step || 'unknown',
              payload: event.data || {},
              explain: event.message,
            };
            
            addEvent(envelope);
          } catch (err) {
            console.error('[EventStream] Parse error:', err);
          }
        };

        eventSource.onerror = () => {
          console.warn('[EventStream] Connection failed, running in demo mode');
          setConnected(false);
          eventSource.close();

          // Don't attempt reconnection in demo mode
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('[EventStream] Attempting reconnection...');
            connect();
          }, 5000);
        };
      } catch (err) {
        console.error('[EventStream] Connection error:', err);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      setConnected(false);
    };
  }, [setConnected, addEvent]);



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



  const value: EventStreamContextValue = {
    sendCommand,
  };

  return (
    <EventStreamContext.Provider value={value}>
      {children}
    </EventStreamContext.Provider>
  );
}
