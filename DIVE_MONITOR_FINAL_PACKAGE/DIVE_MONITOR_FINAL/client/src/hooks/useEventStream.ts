import { useEffect, useRef, useState } from 'react';

export interface DiveEvent {
  id: string;
  timestamp: number;
  event_type: string;
  severity: 'info' | 'success' | 'warning' | 'error' | 'debug';
  command: string;
  message: string;
  data: Record<string, any>;
  run_id?: string;
}

interface UseEventStreamOptions {
  url: string;
  enabled?: boolean;
  onEvent?: (event: DiveEvent) => void;
  onError?: (error: Error) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

export function useEventStream({
  url,
  enabled = true,
  onEvent,
  onError,
  onConnect,
  onDisconnect,
}: UseEventStreamOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionFailed, setConnectionFailed] = useState(false);
  const [events, setEvents] = useState<DiveEvent[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);

  const connectRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const connect = () => {
      try {
        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onopen = () => {
          console.log('[EventStream] Connected');
          setIsConnected(true);
          onConnect?.();
        };

        eventSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            
            // Handle connection message
            if (data.type === 'connected') {
              console.log('[EventStream] Connection confirmed');
              return;
            }

            // Handle event
            const event: DiveEvent = data;
            setEvents((prev) => [...prev.slice(-999), event]); // Keep last 1000
            onEvent?.(event);
          } catch (err) {
            console.error('[EventStream] Parse error:', err);
          }
        };

        eventSource.onerror = (err) => {
          console.error('[EventStream] Error:', err);
          setIsConnected(false);
          eventSource.close();
          onDisconnect?.();
          onError?.(new Error('EventSource error'));

          reconnectAttemptsRef.current += 1;

          // Stop trying after 3 failed attempts
          if (reconnectAttemptsRef.current >= 3) {
            console.error('[EventStream] Max reconnection attempts reached');
            setConnectionFailed(true);
            return;
          }

          // Attempt reconnection with exponential backoff
          const delay = Math.min(5000 * Math.pow(2, reconnectAttemptsRef.current - 1), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log(`[EventStream] Attempting reconnection (${reconnectAttemptsRef.current}/3)...`);
            connect();
          }, delay);
        };
      } catch (err) {
        console.error('[EventStream] Connection error:', err);
        onError?.(err as Error);
      }
    };

    connectRef.current = connect;
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setIsConnected(false);
    };
  }, [url, enabled, onEvent, onError, onConnect, onDisconnect]);

  const retry = () => {
    reconnectAttemptsRef.current = 0;
    setConnectionFailed(false);
    setIsConnected(false);
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (connectRef.current) {
      connectRef.current();
    }
  };

  return {
    isConnected,
    connectionFailed,
    events,
    retry,
  };
}
