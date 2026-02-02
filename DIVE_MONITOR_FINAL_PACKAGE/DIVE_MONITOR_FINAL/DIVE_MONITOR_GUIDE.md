# Dive Monitor 2 - Complete User Guide

## Overview

**Dive Monitor** is a real-time monitoring and analytics dashboard for **Dive Coder V15.3**. It provides:

- 📊 Real-time performance metrics
- 📈 Success rate tracking
- 💰 Cost monitoring
- 🔌 Provider health status
- 📋 Activity history
- ⚡ Quick actions

---

## Features

### Dashboard

The main dashboard displays:

1. **Total Runs** - All-time execution count
2. **Success Rate** - Percentage of successful executions
3. **Total Cost** - Cumulative API usage cost
4. **Active Provider** - Currently active LLM provider

### Sections

#### Recent Activity
- Shows last 5 executions
- Status indicators (success/running/failed)
- Duration and timestamp
- Click to view details

#### Provider Health
- Provider status and health metrics
- Success rate per provider
- API call counts
- Latency measurements
- Cost per provider

#### Quick Actions
- **Start Monitoring** - Begin tracking DiveCoder activity
- **Configure Providers** - Set up LLM API providers
- **View Analytics** - Detailed performance metrics

---

## Installation

### Prerequisites

- Node.js 18+
- Python 3.8+
- Dive Coder V15.3
- npm or pnpm

### Setup

```bash
# 1. Extract the Dive Monitor package
unzip dive-monitor2-main.zip
cd dive-monitor2-main

# 2. Install dependencies
pnpm install

# 3. Start the development server
pnpm dev

# 4. Open in browser
# Navigate to http://localhost:5173
```

### Production Build

```bash
# Build for production
pnpm build

# Start production server
pnpm start
```

---

## Integration with Dive Coder

### Connection Flow

```
Dive Coder V15.3
    ↓ (Events)
Sync Bridge (WebSocket)
    ↓
Dive Monitor Dashboard
    ↓ (Commands)
Dive Coder V15.3
```

### Starting Both Services

#### Terminal 1: Start Dive Coder with Sync Bridge

```bash
npx dive-coder
# or
python3 divecoder_v15_3.py --sync-bridge
```

#### Terminal 2: Start Dive Monitor

```bash
cd dive-monitor2-main
pnpm dev
```

#### Terminal 3 (Optional): Start Antigravity Extension

```bash
npx dive-coder-antigravity
```

---

## Dashboard Tabs

### Dashboard Tab (Default)

Main overview with:
- Metric cards
- Recent activity
- Provider health
- Quick actions

**Status Indicator:**
- 🟢 **Connected** - Dive Coder is running
- ⚫ **Disconnected** - Waiting for Dive Coder

### Activity Tab

Detailed execution history:
- Full event log
- Execution timeline
- Thinking process
- Artifacts and outputs
- RAG results
- Governance decisions

### Settings Tab

Configuration options:
- Provider setup
- API keys
- Monitoring preferences
- Export options

---

## Real-time Monitoring

### Metrics Updates

Metrics update in real-time as Dive Coder executes:

1. **During Execution:**
   - Status changes to "Running"
   - Duration timer starts
   - Events stream in real-time

2. **After Completion:**
   - Final metrics calculated
   - Cost updated
   - Activity logged
   - Success/failure recorded

### Event Streaming

Events are streamed via WebSocket:

```javascript
// Example event structure
{
  "type": "execution_start",
  "timestamp": "2024-01-31T12:00:00Z",
  "run_id": "abc123",
  "input": "Review this code",
  "metadata": { ... }
}
```

---

## Configuration

### Environment Variables

```bash
# Sync Bridge connection
SYNC_BRIDGE_URL=http://localhost:8787

# Dive Coder connection
DIVE_CODER_URL=http://localhost:8888

# Monitor port
MONITOR_PORT=5173

# Theme
THEME=light  # or 'dark'
```

### Config File

Create `.env.local`:

```
VITE_SYNC_BRIDGE_URL=http://localhost:8787
VITE_DIVE_CODER_URL=http://localhost:8888
VITE_THEME=light
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
  "active_provider": "gpt-4"
}
```

#### Get Recent Runs

```bash
GET /api/runs?limit=10
```

#### Get Provider Health

```bash
GET /api/providers/health
```

### WebSocket Events

#### Connection

```javascript
ws://localhost:8787/events
```

#### Event Types

- `execution_start` - Execution begins
- `execution_progress` - Progress update
- `execution_complete` - Execution finished
- `error` - Error occurred
- `metric_update` - Metrics changed

---

## Troubleshooting

### Dashboard Shows "Disconnected"

**Issue:** Dive Monitor can't connect to Dive Coder

**Solutions:**
1. Ensure Dive Coder is running
2. Check Sync Bridge is started
3. Verify network connectivity
4. Check firewall settings

```bash
# Test connection
curl http://localhost:8787/health
```

### Metrics Not Updating

**Issue:** Real-time metrics aren't showing

**Solutions:**
1. Check WebSocket connection
2. Verify events are being emitted
3. Check browser console for errors
4. Restart Sync Bridge

```bash
# Check Sync Bridge logs
DEBUG=* node sync-bridge/server.js
```

### Provider Health Shows "None"

**Issue:** No active provider detected

**Solutions:**
1. Configure providers in Settings
2. Ensure API keys are valid
3. Check provider availability
4. Verify network connectivity

---

## Performance Optimization

### Browser Performance

- Use Chrome/Edge for best performance
- Clear browser cache if slow
- Disable unused browser extensions
- Use hardware acceleration

### Server Performance

- Increase Sync Bridge worker threads
- Enable caching
- Optimize database queries
- Monitor memory usage

---

## Security

### API Security

- All API calls use HTTPS in production
- WebSocket connections are secured
- API keys are never logged
- Sensitive data is encrypted

### Data Privacy

- No data is stored permanently
- Events are streamed only to connected clients
- Historical data can be exported
- GDPR compliant

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

## Advanced Usage

### Custom Dashboards

Create custom dashboards by:
1. Cloning dashboard components
2. Modifying queries
3. Adding custom charts
4. Deploying as new route

### Webhooks

Configure webhooks for events:

```bash
POST /api/webhooks
{
  "url": "https://your-server.com/webhook",
  "events": ["execution_complete", "error"]
}
```

### API Integrations

Integrate with:
- Slack - Send notifications
- GitHub - Post results
- Jira - Create tickets
- DataDog - Send metrics

---

## Support & Resources

### Documentation

- [Dive Coder Docs](https://dive-coder.dev/docs)
- [Sync Bridge Guide](./sync-bridge/README.md)
- [API Reference](./API.md)

### Community

- GitHub: [dive-team/dive-monitor](https://github.com/dive-team/dive-monitor)
- Discord: [Join Community](https://discord.gg/dive-coder)
- Email: support@dive-coder.dev

### Troubleshooting

- [Common Issues](./TROUBLESHOOTING.md)
- [FAQ](./FAQ.md)
- [Debug Guide](./DEBUG.md)

---

## Version Information

- **Dive Monitor:** 2.0.0
- **Dive Coder:** 15.3
- **Sync Bridge:** 1.0.0
- **Node.js:** 18+
- **React:** 19.2.1
- **Tailwind CSS:** 4.1.14

---

## License

MIT License - See LICENSE file for details

---

**Happy monitoring! 🤿**
