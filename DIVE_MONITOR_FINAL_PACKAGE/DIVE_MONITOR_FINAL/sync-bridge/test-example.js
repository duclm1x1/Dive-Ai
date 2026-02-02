/**
 * Sync Bridge Test Examples
 * Run with: node test-example.js
 */

import fetch from 'node-fetch';
import WebSocket from 'ws';

const BRIDGE_URL = 'http://localhost:8787';
const WS_URL = 'ws://localhost:8787';

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
};

function log(color, ...args) {
  console.log(color, ...args, colors.reset);
}

async function testHealthCheck() {
  log(colors.blue, '\n📋 Test 1: Health Check');
  try {
    const response = await fetch(`${BRIDGE_URL}/health`);
    const data = await response.json();
    log(colors.green, '✅ Health check passed');
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    log(colors.red, '❌ Health check failed:', error.message);
  }
}

async function testCreateSession() {
  log(colors.blue, '\n📋 Test 2: Create Session');
  try {
    const response = await fetch(`${BRIDGE_URL}/api/sessions`, {
      method: 'POST',
    });
    const data = await response.json();
    log(colors.green, '✅ Session created');
    console.log(JSON.stringify(data, null, 2));
    return data.sessionId;
  } catch (error) {
    log(colors.red, '❌ Session creation failed:', error.message);
    return null;
  }
}

async function testListSessions() {
  log(colors.blue, '\n📋 Test 3: List Sessions');
  try {
    const response = await fetch(`${BRIDGE_URL}/api/sessions`);
    const data = await response.json();
    log(colors.green, '✅ Sessions listed');
    console.log(`Total sessions: ${data.total}`);
    data.sessions.forEach((session) => {
      console.log(
        `  - ${session.id}: ${session.status} (Dive Coder: ${session.diveCoderConnected}, Monitors: ${session.diveMonitorConnected})`
      );
    });
  } catch (error) {
    log(colors.red, '❌ List sessions failed:', error.message);
  }
}

async function testPushEvent(sessionId) {
  log(colors.blue, '\n📋 Test 4: Push Event');
  if (!sessionId) {
    log(colors.yellow, '⚠️  No session ID, skipping');
    return;
  }

  try {
    const event = {
      type: 'TEST_EVENT',
      payload: {
        message: 'This is a test event',
        timestamp: Date.now(),
      },
      run_id: 'test_run_' + Date.now(),
    };

    const response = await fetch(
      `${BRIDGE_URL}/api/sessions/${sessionId}/events`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event }),
      }
    );

    const data = await response.json();
    log(colors.green, '✅ Event pushed');
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    log(colors.red, '❌ Push event failed:', error.message);
  }
}

async function testGetEvents(sessionId) {
  log(colors.blue, '\n📋 Test 5: Get Events');
  if (!sessionId) {
    log(colors.yellow, '⚠️  No session ID, skipping');
    return;
  }

  try {
    const response = await fetch(
      `${BRIDGE_URL}/api/sessions/${sessionId}/events?limit=10`
    );
    const data = await response.json();
    log(colors.green, '✅ Events retrieved');
    console.log(`Total events: ${data.total}`);
    data.events.slice(0, 3).forEach((event, idx) => {
      console.log(`  ${idx + 1}. ${event.type} (${event.timestamp})`);
    });
  } catch (error) {
    log(colors.red, '❌ Get events failed:', error.message);
  }
}

async function testWebSocketConnection(sessionId) {
  log(colors.blue, '\n📋 Test 6: WebSocket Connection');

  return new Promise((resolve) => {
    try {
      const ws = new WebSocket(WS_URL, {
        headers: {
          'x-client-type': 'test-client',
          'x-session-id': sessionId || '',
        },
      });

      let handshakeReceived = false;

      ws.on('open', () => {
        log(colors.green, '✅ WebSocket connected');

        // Send handshake
        const handshake = {
          type: 'HANDSHAKE',
          sessionId: sessionId,
          clientName: 'Test Client',
        };

        ws.send(JSON.stringify(handshake));
      });

      ws.on('message', (data) => {
        const message = JSON.parse(data);

        if (message.type === 'HANDSHAKE_ACK' && !handshakeReceived) {
          handshakeReceived = true;
          log(colors.green, '✅ Handshake acknowledged');
          console.log(`   Session: ${message.sessionId}`);
          console.log(`   Client: ${message.clientId}`);

          // Send a test event
          const testEvent = {
            type: 'EVENT',
            event: {
              type: 'TEST_EVENT',
              payload: { message: 'Test from WebSocket' },
              timestamp: Date.now(),
            },
          };

          ws.send(JSON.stringify(testEvent));
          log(colors.green, '✅ Test event sent');

          // Close after a short delay
          setTimeout(() => {
            ws.close();
          }, 1000);
        } else if (message.type === 'PONG') {
          log(colors.green, '✅ Received PONG');
        }
      });

      ws.on('close', () => {
        log(colors.green, '✅ WebSocket closed');
        resolve();
      });

      ws.on('error', (error) => {
        log(colors.red, '❌ WebSocket error:', error.message);
        resolve();
      });

      // Send ping after connection
      setTimeout(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'PING' }));
        }
      }, 500);
    } catch (error) {
      log(colors.red, '❌ WebSocket connection failed:', error.message);
      resolve();
    }
  });
}

async function testSimulateExecution(sessionId) {
  log(colors.blue, '\n📋 Test 7: Simulate Execution');
  if (!sessionId) {
    log(colors.yellow, '⚠️  No session ID, skipping');
    return;
  }

  try {
    const runId = 'sim_run_' + Date.now();
    const events = [
      {
        type: 'COMMAND_START',
        payload: { command: 'explain', file: 'example.py' },
        run_id: runId,
      },
      {
        type: 'PLAN_GENERATED',
        payload: { steps: 3 },
        run_id: runId,
      },
      {
        type: 'STEP_COMPLETE',
        payload: { step: 1, duration: 0.5 },
        run_id: runId,
      },
      {
        type: 'STEP_COMPLETE',
        payload: { step: 2, duration: 1.2 },
        run_id: runId,
      },
      {
        type: 'STEP_COMPLETE',
        payload: { step: 3, duration: 0.8 },
        run_id: runId,
      },
      {
        type: 'COMMAND_COMPLETE',
        payload: { command: 'explain', status: 'success' },
        run_id: runId,
      },
    ];

    for (const event of events) {
      const response = await fetch(
        `${BRIDGE_URL}/api/sessions/${sessionId}/events`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ event }),
        }
      );

      if (response.ok) {
        log(colors.green, `✅ ${event.type} sent`);
      } else {
        log(colors.red, `❌ Failed to send ${event.type}`);
      }

      // Small delay between events
      await new Promise((resolve) => setTimeout(resolve, 200));
    }

    log(colors.green, '✅ Simulated execution completed');
  } catch (error) {
    log(colors.red, '❌ Simulation failed:', error.message);
  }
}

async function runAllTests() {
  log(colors.bright + colors.blue, `
╔════════════════════════════════════════════════════════════╗
║  Dive Sync Bridge - Test Suite                             ║
╚════════════════════════════════════════════════════════════╝
  `);

  // Test 1: Health check
  await testHealthCheck();

  // Test 2: Create session
  const sessionId = await testCreateSession();

  // Test 3: List sessions
  await testListSessions();

  // Test 4: Push event
  await testPushEvent(sessionId);

  // Test 5: Get events
  await testGetEvents(sessionId);

  // Test 6: WebSocket connection
  await testWebSocketConnection(sessionId);

  // Test 7: Simulate execution
  await testSimulateExecution(sessionId);

  log(colors.bright + colors.green, `
╔════════════════════════════════════════════════════════════╗
║  All tests completed!                                       ║
╚════════════════════════════════════════════════════════════╝
  `);
}

// Run tests
runAllTests().catch((error) => {
  log(colors.red, 'Test suite failed:', error);
  process.exit(1);
});
