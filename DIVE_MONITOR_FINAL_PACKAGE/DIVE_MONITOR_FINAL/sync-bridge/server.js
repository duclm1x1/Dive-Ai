/**
 * Dive Coder V15.3 + Dive Monitor 2 Sync Bridge Server
 * Real-time two-way synchronization hub
 */

import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { EventEmitter } from 'events';
import crypto from 'crypto';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Configuration
const CONFIG = {
  port: process.env.SYNC_BRIDGE_PORT || 8787,
  eventBufferSize: 1000,
  sessionTimeout: 3600000, // 1 hour
  maxConnections: 100,
};

// Global state
const sessions = new Map();
const eventBuffer = [];
let sessionCounter = 0;

// Event emitter for internal events
const eventEmitter = new EventEmitter();

/**
 * Session Management
 */
class SyncSession {
  constructor(id) {
    this.id = id;
    this.createdAt = Date.now();
    this.lastActivity = Date.now();
    this.diveCoderClient = null;
    this.diveMonitorClients = new Set();
    this.state = {
      status: 'initialized',
      metrics: {},
      config: {},
      events: [],
    };
  }

  updateActivity() {
    this.lastActivity = Date.now();
  }

  isExpired() {
    return Date.now() - this.lastActivity > CONFIG.sessionTimeout;
  }

  addEvent(event) {
    this.state.events.push({
      ...event,
      sessionId: this.id,
      addedAt: Date.now(),
    });

    // Keep only recent events in memory
    if (this.state.events.length > CONFIG.eventBufferSize) {
      this.state.events = this.state.events.slice(-CONFIG.eventBufferSize);
    }

    eventBuffer.push({
      sessionId: this.id,
      event,
      timestamp: Date.now(),
    });

    // Keep global buffer size manageable
    if (eventBuffer.length > CONFIG.eventBufferSize * 2) {
      eventBuffer.shift();
    }
  }

  broadcast(message) {
    const data = JSON.stringify(message);

    // Send to Dive Monitor clients
    this.diveMonitorClients.forEach((client) => {
      if (client.readyState === 1) { // OPEN
        client.send(data);
      }
    });

    // Send to Dive Coder client
    if (this.diveCoderClient && this.diveCoderClient.readyState === 1) {
      this.diveCoderClient.send(data);
    }
  }

  toJSON() {
    return {
      id: this.id,
      createdAt: this.createdAt,
      lastActivity: this.lastActivity,
      status: this.state.status,
      diveCoderConnected: this.diveCoderClient !== null && this.diveCoderClient.readyState === 1,
      diveMonitorConnected: this.diveMonitorClients.size,
      eventCount: this.state.events.length,
    };
  }
}

/**
 * WebSocket Connection Handler
 */
wss.on('connection', (ws, req) => {
  const clientType = req.headers['x-client-type'] || 'unknown';
  const sessionId = req.headers['x-session-id'];
  const clientId = crypto.randomBytes(8).toString('hex');

  console.log(`[${clientId}] New connection: ${clientType}`);

  let currentSession = null;

  // Handle initial connection
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data);

      // First message must be HANDSHAKE
      if (!currentSession) {
        if (message.type === 'HANDSHAKE') {
          handleHandshake(ws, message, clientType, clientId);
          return;
        } else {
          ws.close(1002, 'First message must be HANDSHAKE');
          return;
        }
      }

      // Route message based on type
      switch (message.type) {
        case 'EVENT':
          handleEvent(currentSession, message, clientType);
          break;
        case 'METRICS_UPDATE':
          handleMetricsUpdate(currentSession, message);
          break;
        case 'CONFIG_UPDATE':
          handleConfigUpdate(currentSession, message);
          break;
        case 'SYNC_CONTROL':
          handleSyncControl(currentSession, message);
          break;
        case 'PING':
          ws.send(JSON.stringify({ type: 'PONG', timestamp: Date.now() }));
          break;
        case 'GET_STATE':
          ws.send(JSON.stringify({
            type: 'STATE_SNAPSHOT',
            state: currentSession.state,
            timestamp: Date.now(),
          }));
          break;
        default:
          console.warn(`[${clientId}] Unknown message type: ${message.type}`);
      }

      currentSession.updateActivity();
    } catch (error) {
      console.error(`[${clientId}] Message processing error:`, error);
      ws.send(JSON.stringify({
        type: 'ERROR',
        message: 'Failed to process message',
        error: error.message,
      }));
    }
  });

  ws.on('close', () => {
    if (currentSession) {
      if (clientType === 'dive-coder') {
        currentSession.diveCoderClient = null;
        currentSession.state.status = 'disconnected';
      } else if (clientType === 'dive-monitor') {
        currentSession.diveMonitorClients.delete(ws);
      }

      // Notify remaining clients
      currentSession.broadcast({
        type: 'CLIENT_DISCONNECTED',
        clientType,
        clientId,
        timestamp: Date.now(),
      });

      console.log(`[${clientId}] Disconnected from session ${currentSession.id}`);

      // Clean up expired sessions
      if (currentSession.diveCoderClient === null && currentSession.diveMonitorClients.size === 0) {
        sessions.delete(currentSession.id);
        console.log(`[${clientId}] Session ${currentSession.id} cleaned up`);
      }
    }
  });

  ws.on('error', (error) => {
    console.error(`[${clientId}] WebSocket error:`, error);
  });

  /**
   * Handle initial HANDSHAKE message
   */
  function handleHandshake(ws, message, clientType, clientId) {
    const { sessionId, clientName } = message;

    // Create or get session
    if (sessionId && sessions.has(sessionId)) {
      currentSession = sessions.get(sessionId);
    } else {
      const newSessionId = `session_${++sessionCounter}_${Date.now()}`;
      currentSession = new SyncSession(newSessionId);
      sessions.set(newSessionId, currentSession);
    }

    // Register client in session
    if (clientType === 'dive-coder') {
      currentSession.diveCoderClient = ws;
      currentSession.state.status = 'connected';
    } else if (clientType === 'dive-monitor') {
      currentSession.diveMonitorClients.add(ws);
    }

    // Send handshake response
    ws.send(JSON.stringify({
      type: 'HANDSHAKE_ACK',
      sessionId: currentSession.id,
      clientId,
      clientType,
      timestamp: Date.now(),
      config: {
        eventBufferSize: CONFIG.eventBufferSize,
        maxConnections: CONFIG.maxConnections,
      },
    }));

    // Notify other clients
    currentSession.broadcast({
      type: 'CLIENT_CONNECTED',
      clientType,
      clientId,
      clientName,
      timestamp: Date.now(),
    });

    console.log(`[${clientId}] Handshake complete for session ${currentSession.id}`);
  }

  /**
   * Handle EVENT message
   */
  function handleEvent(session, message, clientType) {
    const { event } = message;

    if (!event) {
      ws.send(JSON.stringify({
        type: 'ERROR',
        message: 'Event is required',
      }));
      return;
    }

    // Add to session
    session.addEvent(event);

    // Broadcast to other clients
    session.broadcast({
      type: 'EVENT_BROADCAST',
      event,
      source: clientType,
      timestamp: Date.now(),
    });
  }

  /**
   * Handle METRICS_UPDATE message
   */
  function handleMetricsUpdate(session, message) {
    const { metrics } = message;

    if (!metrics) {
      ws.send(JSON.stringify({
        type: 'ERROR',
        message: 'Metrics are required',
      }));
      return;
    }

    session.state.metrics = {
      ...session.state.metrics,
      ...metrics,
      updatedAt: Date.now(),
    };

    session.broadcast({
      type: 'METRICS_UPDATE_BROADCAST',
      metrics: session.state.metrics,
      timestamp: Date.now(),
    });
  }

  /**
   * Handle CONFIG_UPDATE message
   */
  function handleConfigUpdate(session, message) {
    const { config } = message;

    if (!config) {
      ws.send(JSON.stringify({
        type: 'ERROR',
        message: 'Config is required',
      }));
      return;
    }

    session.state.config = {
      ...session.state.config,
      ...config,
      updatedAt: Date.now(),
    };

    session.broadcast({
      type: 'CONFIG_UPDATE_BROADCAST',
      config: session.state.config,
      timestamp: Date.now(),
    });
  }

  /**
   * Handle SYNC_CONTROL message
   */
  function handleSyncControl(session, message) {
    const { action, params } = message;

    switch (action) {
      case 'PAUSE':
        session.state.status = 'paused';
        break;
      case 'RESUME':
        session.state.status = 'running';
        break;
      case 'CANCEL':
        session.state.status = 'cancelled';
        break;
      default:
        console.warn(`Unknown control action: ${action}`);
    }

    session.broadcast({
      type: 'SYNC_CONTROL_BROADCAST',
      action,
      params,
      timestamp: Date.now(),
    });
  }
});

/**
 * REST API Endpoints
 */

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: Date.now(),
    sessions: sessions.size,
    connections: wss.clients.size,
  });
});

// Get all sessions
app.get('/api/sessions', (req, res) => {
  const sessionList = Array.from(sessions.values()).map((s) => s.toJSON());
  res.json({
    sessions: sessionList,
    total: sessionList.length,
    timestamp: Date.now(),
  });
});

// Get specific session
app.get('/api/sessions/:sessionId', (req, res) => {
  const session = sessions.get(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }
  res.json({
    session: session.toJSON(),
    state: session.state,
    timestamp: Date.now(),
  });
});

// Get session events
app.get('/api/sessions/:sessionId/events', (req, res) => {
  const session = sessions.get(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const limit = parseInt(req.query.limit) || 100;
  const events = session.state.events.slice(-limit);

  res.json({
    sessionId: req.params.sessionId,
    events,
    total: session.state.events.length,
    timestamp: Date.now(),
  });
});

// Create new session (for CLI)
app.post('/api/sessions', express.json(), (req, res) => {
  const sessionId = `session_${++sessionCounter}_${Date.now()}`;
  const session = new SyncSession(sessionId);
  sessions.set(sessionId, session);

  res.status(201).json({
    sessionId,
    session: session.toJSON(),
    timestamp: Date.now(),
  });
});

// Push event (for CLI)
app.post('/api/sessions/:sessionId/events', express.json(), (req, res) => {
  const session = sessions.get(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  const { event } = req.body;
  if (!event) {
    return res.status(400).json({ error: 'Event is required' });
  }

  session.addEvent(event);
  session.broadcast({
    type: 'EVENT_BROADCAST',
    event,
    source: 'cli',
    timestamp: Date.now(),
  });

  res.json({
    success: true,
    sessionId: req.params.sessionId,
    eventCount: session.state.events.length,
    timestamp: Date.now(),
  });
});

// Get metrics (for CLI)
app.get('/api/sessions/:sessionId/metrics', (req, res) => {
  const session = sessions.get(req.params.sessionId);
  if (!session) {
    return res.status(404).json({ error: 'Session not found' });
  }

  res.json({
    sessionId: req.params.sessionId,
    metrics: session.state.metrics,
    timestamp: Date.now(),
  });
});

/**
 * Cleanup expired sessions periodically
 */
setInterval(() => {
  let cleaned = 0;
  for (const [sessionId, session] of sessions) {
    if (session.isExpired()) {
      sessions.delete(sessionId);
      cleaned++;
    }
  }
  if (cleaned > 0) {
    console.log(`Cleaned up ${cleaned} expired sessions`);
  }
}, 60000); // Every minute

/**
 * Start server
 */
server.listen(CONFIG.port, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  Dive Coder V15.3 + Dive Monitor 2 Sync Bridge             ║
║  Real-time Synchronization Server                          ║
╚════════════════════════════════════════════════════════════╝

🚀 Server running on http://localhost:${CONFIG.port}
📡 WebSocket: ws://localhost:${CONFIG.port}
🔗 API: http://localhost:${CONFIG.port}/api

Available endpoints:
  GET  /health                           - Health check
  GET  /api/sessions                     - List all sessions
  GET  /api/sessions/:sessionId          - Get session details
  GET  /api/sessions/:sessionId/events   - Get session events
  POST /api/sessions                     - Create new session
  POST /api/sessions/:sessionId/events   - Push event
  GET  /api/sessions/:sessionId/metrics  - Get metrics

WebSocket: Connect with x-client-type header (dive-coder or dive-monitor)
  `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
