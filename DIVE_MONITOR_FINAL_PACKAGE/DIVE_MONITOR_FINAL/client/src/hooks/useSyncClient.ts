import { useEffect, useRef, useCallback } from 'react';
import { useSyncStore } from '@/stores/syncStore';
import { useRuntimeStore } from '@/stores/runtimeStore';

interface SyncClientConfig {
  websocketUrl: string;
  clientType?: string;
  clientName?: string;
  autoConnect?: boolean;
}

export const useSyncClient = (config: SyncClientConfig) => {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 1000; // ms

  const syncStore = useSyncStore();
  const runtimeStore = useRuntimeStore();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    syncStore.setConnectionStatus('connecting');

    try {
      const ws = new WebSocket(config.websocketUrl);

      ws.onopen = () => {
        console.log('[SyncClient] Connected to Sync Bridge');

        // Send handshake
        const handshake = {
          type: 'HANDSHAKE',
          sessionId: syncStore.sessionId,
          clientName: config.clientName || 'Dive Monitor 2',
        };

        ws.send(JSON.stringify(handshake));
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleMessage(message);
        } catch (error) {
          console.error('[SyncClient] Failed to parse message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('[SyncClient] WebSocket error:', error);
        syncStore.setConnectionStatus('disconnected');
      };

      ws.onclose = () => {
        console.log('[SyncClient] Disconnected from Sync Bridge');
        syncStore.setConnected(false);
        wsRef.current = null;

        // Attempt reconnection
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          const delay = reconnectDelay * reconnectAttemptsRef.current;
          console.log(
            `[SyncClient] Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          console.error('[SyncClient] Max reconnection attempts reached');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('[SyncClient] Connection error:', error);
      syncStore.setConnectionStatus('disconnected');
    }
  }, [config.websocketUrl, config.clientName, syncStore]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    syncStore.setConnected(false);
    syncStore.setConnectionStatus('disconnected');
  }, [syncStore]);

  const sendEvent = useCallback(
    (event: any) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const message = {
          type: 'EVENT',
          event,
        };
        wsRef.current.send(JSON.stringify(message));
      } else {
        console.warn('[SyncClient] WebSocket not connected, cannot send event');
      }
    },
    []
  );

  const sendMetrics = useCallback(
    (metrics: any) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const message = {
          type: 'METRICS_UPDATE',
          metrics,
        };
        wsRef.current.send(JSON.stringify(message));
      }
    },
    []
  );

  const sendConfig = useCallback(
    (config: any) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const message = {
          type: 'CONFIG_UPDATE',
          config,
        };
        wsRef.current.send(JSON.stringify(message));
      }
    },
    []
  );

  const sendControl = useCallback(
    (action: string, params?: any) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const message = {
          type: 'SYNC_CONTROL',
          action,
          params: params || {},
        };
        wsRef.current.send(JSON.stringify(message));
      }
    },
    []
  );

  const getState = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = {
        type: 'GET_STATE',
      };
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  const ping = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'PING' }));
    }
  }, []);

  const handleMessage = useCallback(
    (message: any) => {
      switch (message.type) {
        case 'HANDSHAKE_ACK':
          console.log('[SyncClient] Handshake acknowledged');
          syncStore.setSessionId(message.sessionId);
          syncStore.setClientId(message.clientId);
          syncStore.setConnected(true);
          syncStore.setConnectionStatus('connected');
          break;

        case 'PONG':
          console.debug('[SyncClient] Received PONG');
          break;

        case 'EVENT_BROADCAST':
          console.log('[SyncClient] Event broadcast:', message.event.type);
          syncStore.addEvent(message.event);

          // Also add to runtime store if it's a relevant event
          if (
            message.event.type === 'COMMAND_START' ||
            message.event.type === 'COMMAND_COMPLETE' ||
            message.event.type === 'STEP_COMPLETE'
          ) {
            runtimeStore.addEvent({
              v: 1,
              seq: syncStore.events.length,
              ts: message.event.timestamp || Date.now() / 1000,
              run_id: message.event.run_id || 'sync_run',
              type: message.event.type,
              payload: message.event.payload,
            });
          }
          break;

        case 'METRICS_UPDATE_BROADCAST':
          console.log('[SyncClient] Metrics update');
          syncStore.setMetrics(message.metrics);

          // Update runtime store metrics
          if (message.metrics) {
            runtimeStore.setMetrics(message.metrics);
          }
          break;

        case 'CONFIG_UPDATE_BROADCAST':
          console.log('[SyncClient] Config update');
          syncStore.setConfig(message.config);
          break;

        case 'SYNC_CONTROL_BROADCAST':
          console.log('[SyncClient] Control command:', message.action);
          // Handle control commands
          switch (message.action) {
            case 'PAUSE':
              console.log('[SyncClient] Execution paused');
              break;
            case 'RESUME':
              console.log('[SyncClient] Execution resumed');
              break;
            case 'CANCEL':
              console.log('[SyncClient] Execution cancelled');
              break;
          }
          break;

        case 'STATE_SNAPSHOT':
          console.log('[SyncClient] State snapshot received');
          if (message.state) {
            if (message.state.metrics) {
              syncStore.setMetrics(message.state.metrics);
            }
            if (message.state.config) {
              syncStore.setConfig(message.state.config);
            }
            if (message.state.events) {
              syncStore.setEvents(message.state.events);
            }
          }
          break;

        case 'CLIENT_CONNECTED':
          console.log(
            `[SyncClient] Client connected: ${message.clientType} (${message.clientId})`
          );
          break;

        case 'CLIENT_DISCONNECTED':
          console.log(
            `[SyncClient] Client disconnected: ${message.clientType} (${message.clientId})`
          );
          break;

        case 'ERROR':
          console.error('[SyncClient] Bridge error:', message.message);
          break;

        default:
          console.debug('[SyncClient] Unknown message type:', message.type);
      }
    },
    [syncStore, runtimeStore]
  );

  // Auto-connect on mount
  useEffect(() => {
    if (config.autoConnect !== false) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [config.autoConnect, connect, disconnect]);

  // Periodic ping to keep connection alive
  useEffect(() => {
    const pingInterval = setInterval(() => {
      ping();
    }, 30000); // Every 30 seconds

    return () => clearInterval(pingInterval);
  }, [ping]);

  return {
    isConnected: syncStore.isConnected,
    connectionStatus: syncStore.connectionStatus,
    sessionId: syncStore.sessionId,
    clientId: syncStore.clientId,
    connect,
    disconnect,
    sendEvent,
    sendMetrics,
    sendConfig,
    sendControl,
    getState,
    ping,
  };
};
