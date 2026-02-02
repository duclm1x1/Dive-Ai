# Dive Monitor 2 + Dive Coder V15.3 - Complete Integration Guide

## Overview

**Dive Monitor** is a professional real-time monitoring dashboard for **Dive Coder V15.3**. It provides comprehensive analytics, performance tracking, and provider health monitoring.

### Key Features

- 📊 Real-time metrics dashboard
- 📈 Success rate and performance tracking
- 💰 API cost monitoring
- 🔌 Provider health status
- 📋 Complete activity history
- ⚡ Quick action buttons
- 🔄 Real-time WebSocket updates
- 📤 Export functionality

---

## Installation & Setup

### Prerequisites

- Node.js 18+
- Python 3.8+
- Dive Coder V15.3
- pnpm (recommended) or npm

### Quick Start

```bash
# 1. Extract Dive Monitor
unzip dive-monitor2-main.zip
cd dive-monitor2-main

# 2. Install dependencies
pnpm install

# 3. Start development server
pnpm dev

# 4. Open browser
# http://localhost:5173
```

### Production Deployment

```bash
# Build
pnpm build

# Start
pnpm start
```

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────┐
│  Dive Coder V15.3                                   │
│  - Dive Engine                                      │
│  - RAG System                                       │
│  - Governance                                       │
│  - 61 Skills                                        │
└────────────┬────────────────────────────────────────┘
             │ Events (HTTP/WebSocket)
             ▼
┌─────────────────────────────────────────────────────┐
│  Sync Bridge (Node.js)                              │
│  - Event Hub                                        │
│  - WebSocket Server (port 8787)                     │
│  - REST API                                         │
│  - Session Management                               │
└────────────┬────────────────────────────────────────┘
             │ WebSocket
             ▼
┌─────────────────────────────────────────────────────┐
│  Dive Monitor Dashboard (React + Tailwind)          │
│  - Dashboard Tab                                    │
│  - Activity Tab                                     │
│  - Settings Tab                                     │
│  - Real-time Updates                                │
└─────────────────────────────────────────────────────┘
```

---

## Dashboard Overview

### Metric Cards

The dashboard displays four key metrics:

1. **Total Runs**
   - Icon: Activity symbol
   - Shows: All-time execution count
   - Color: Gray

2. **Success Rate**
   - Icon: Trending up
   - Shows: Percentage of successful runs
   - Color: Green
   - Includes: Completed count

3. **Total Cost**
   - Icon: Dollar sign
   - Shows: Cumulative API costs
   - Color: Orange
   - Includes: Cost per run

4. **Active Provider**
   - Icon: Zap
   - Shows: Currently active LLM provider
   - Color: Blue
   - Status: Connected/Waiting

### Recent Activity Section

- Displays last 5 executions
- Shows status (success/running/failed)
- Displays timestamp and duration
- Color-coded status indicators
- Click to view full details

### Provider Health Section

- Lists all configured providers
- Shows success rate per provider
- Displays API call counts
- Shows latency measurements
- Displays cost per provider
- Health status indicators

### Quick Actions

Three action buttons:

1. **Start Monitoring**
   - Begin tracking DiveCoder activity
   - Starts real-time event streaming

2. **Configure Providers**
   - Set up LLM API providers
   - Manage API keys
   - Configure models

3. **View Analytics**
   - Detailed performance metrics
   - Historical data
   - Export reports

---

## Integration with Dive Coder

### Starting the Full Stack

#### Terminal 1: Dive Coder with Sync Bridge

```bash
npx dive-coder
```

This automatically:
- Detects OS
- Finds Dive Coder installation
- Installs Python dependencies
- Starts Sync Bridge (port 8787)
- Launches Antigravity extension (optional)

#### Terminal 2: Dive Monitor

```bash
cd dive-monitor2-main
pnpm dev
```

Opens dashboard at `http://localhost:5173`

#### Terminal 3: Antigravity Extension (Optional)

```bash
npx dive-coder-antigravity
```

Opens Antigravity with CLI tab

### Data Flow

```
User Input (Dive Monitor)
    ↓
REST API / WebSocket
    ↓
Sync Bridge
    ↓
Dive Coder V15.3
    ↓
Command Execution
    ↓
Event Emission
    ↓
Sync Bridge (WebSocket)
    ↓
Dive Monitor (Real-time Update)
```

---

## Configuration

### Environment Variables

Create `.env.local`:

```bash
# Sync Bridge
VITE_SYNC_BRIDGE_URL=http://localhost:8787

# Dive Coder
VITE_DIVE_CODER_URL=http://localhost:8888

# Monitor
VITE_MONITOR_PORT=5173

# Theme
VITE_THEME=light  # or 'dark'

# Debug
VITE_DEBUG=false
```

### Config File

Create `config.json`:

```json
{
  "syncBridge": {
    "url": "http://localhost:8787",
    "reconnectInterval": 3000,
    "maxReconnectAttempts": 5
  },
  "monitor": {
    "theme": "light",
    "refreshInterval": 1000,
    "autoExport": false
  },
  "providers": {
    "defaultProvider": "gpt-4",
    "timeout": 30000
  }
}
```

---

## API Reference

### REST Endpoints

#### Get Metrics

```bash
GET /api/metrics
```

Response:
```json
{
  "total_runs": 42,
  "success_rate": 85.7,
  "total_cost": 12.34,
  "active_provider": "gpt-4",
  "timestamp": "2024-01-31T12:00:00Z"
}
```

#### Get Recent Runs

```bash
GET /api/runs?limit=10&offset=0
```

Response:
```json
{
  "runs": [
    {
      "id": "run-123",
      "type": "code_review",
      "status": "success",
      "duration": 1234,
      "timestamp": "2024-01-31T12:00:00Z",
      "cost": 0.02
    }
  ],
  "total": 42
}
```

#### Get Provider Health

```bash
GET /api/providers/health
```

Response:
```json
{
  "providers": [
    {
      "name": "gpt-4",
      "status": "healthy",
      "success_rate": 95.5,
      "total_calls": 100,
      "avg_latency": 0.45,
      "total_cost": 2.50
    }
  ]
}
```

### WebSocket Events

#### Connection

```javascript
const ws = new WebSocket('ws://localhost:8787/events');

ws.onopen = () => {
  console.log('Connected to Sync Bridge');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from Sync Bridge');
};
```

#### Event Types

**Execution Start**
```json
{
  "type": "execution_start",
  "run_id": "run-123",
  "input": "Review this code",
  "timestamp": "2024-01-31T12:00:00Z"
}
```

**Execution Progress**
```json
{
  "type": "execution_progress",
  "run_id": "run-123",
  "step": "analyzing",
  "progress": 45,
  "timestamp": "2024-01-31T12:00:05Z"
}
```

**Execution Complete**
```json
{
  "type": "execution_complete",
  "run_id": "run-123",
  "status": "success",
  "duration": 5000,
  "cost": 0.02,
  "timestamp": "2024-01-31T12:00:10Z"
}
```

**Metric Update**
```json
{
  "type": "metric_update",
  "metrics": {
    "total_runs": 43,
    "success_rate": 86.0,
    "total_cost": 12.36
  },
  "timestamp": "2024-01-31T12:00:10Z"
}
```

---

## Troubleshooting

### Dashboard Shows "Disconnected"

**Problem:** Dive Monitor can't connect to Sync Bridge

**Solutions:**
1. Verify Dive Coder is running
2. Check Sync Bridge is started
3. Verify port 8787 is available
4. Check firewall settings

```bash
# Test connection
curl http://localhost:8787/health

# Check if port is in use
lsof -i :8787
```

### Metrics Not Updating

**Problem:** Real-time metrics aren't showing

**Solutions:**
1. Check WebSocket connection in browser console
2. Verify events are being emitted
3. Check for JavaScript errors
4. Restart Sync Bridge

```bash
# Enable debug mode
DEBUG=* pnpm dev
```

### Provider Shows "None"

**Problem:** No active provider detected

**Solutions:**
1. Configure providers in Settings tab
2. Verify API keys are valid
3. Check provider availability
4. Test provider connection

---

## Performance Optimization

### Browser Performance

- Use Chrome/Edge for best performance
- Clear browser cache regularly
- Disable unused extensions
- Enable hardware acceleration

### Server Performance

- Increase Sync Bridge worker threads
- Enable Redis caching
- Optimize database queries
- Monitor memory usage

### Network Performance

- Use CDN for static assets
- Enable gzip compression
- Minimize WebSocket message size
- Implement message batching

---

## Security

### API Security

- All endpoints require authentication
- HTTPS in production
- WebSocket Secure (WSS) in production
- Rate limiting enabled
- CORS properly configured

### Data Protection

- API keys never logged
- Sensitive data encrypted
- No data stored permanently
- GDPR compliant

### Best Practices

1. **Never commit API keys**
   - Use environment variables
   - Use .env.local (not in git)

2. **Use HTTPS in production**
   - Get SSL certificate
   - Enable HSTS headers

3. **Implement authentication**
   - Use OAuth2
   - Implement JWT tokens
   - Add role-based access

---

## Export & Reporting

### Export Data

```bash
# Export as JSON
GET /api/export?format=json&start=2024-01-01&end=2024-01-31

# Export as CSV
GET /api/export?format=csv&start=2024-01-01&end=2024-01-31

# Export as PDF
GET /api/export?format=pdf&start=2024-01-01&end=2024-01-31
```

### Generate Reports

```bash
# Daily report
GET /api/reports/daily?date=2024-01-31

# Weekly report
GET /api/reports/weekly?week=5&year=2024

# Monthly report
GET /api/reports/monthly?month=1&year=2024
```

---

## Advanced Features

### Custom Dashboards

Create custom dashboards:
1. Clone dashboard components
2. Modify queries
3. Add custom charts
4. Deploy as new route

### Webhooks

Configure webhooks for events:

```bash
POST /api/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["execution_complete", "error"],
  "secret": "your-secret-key"
}
```

### Integrations

Integrate with:
- **Slack** - Send notifications
- **GitHub** - Post results
- **Jira** - Create tickets
- **DataDog** - Send metrics
- **PagerDuty** - Alert on errors

---

## File Structure

```
dive-monitor2-main/
├── client/                          # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/          # Dashboard components
│   │   │   ├── activity/           # Activity tab
│   │   │   └── settings/           # Settings tab
│   │   ├── pages/
│   │   │   └── Monitor.tsx         # Main page
│   │   ├── stores/                 # Zustand stores
│   │   ├── hooks/                  # Custom hooks
│   │   └── App.tsx                 # Root component
│   └── index.html
├── server/                          # Express backend
│   └── index.ts                    # Server entry
├── sync-bridge/                     # WebSocket sync
│   ├── server.js                   # Sync bridge server
│   └── package.json
├── shared/                          # Shared types
├── package.json
├── vite.config.ts
└── README.md
```

---

## Version Information

- **Dive Monitor:** 2.0.0
- **Dive Coder:** 15.3
- **Sync Bridge:** 1.0.0
- **Node.js:** 18+
- **React:** 19.2.1
- **Tailwind CSS:** 4.1.14
- **TypeScript:** 5.6.3

---

## Support & Resources

### Documentation

- [Dive Coder Docs](https://dive-coder.dev)
- [Sync Bridge Guide](./sync-bridge/README.md)
- [API Reference](./API.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

### Community

- **GitHub:** [dive-team/dive-monitor](https://github.com/dive-team/dive-monitor)
- **Discord:** [Join Community](https://discord.gg/dive-coder)
- **Email:** support@dive-coder.dev

---

## License

MIT License - See LICENSE file for details

---

**Ready to dive deep into your code? Let's go! 🤿**
