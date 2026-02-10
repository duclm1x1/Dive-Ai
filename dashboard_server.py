"""
🖥️ DIVE AI DASHBOARD SERVER
Serves the Multi-Agent Coordinator Dashboard and provides API endpoints
"""

import os
import sys
import json
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse

sys.path.append(os.path.dirname(__file__))

from core.orchestrator.multi_agent_coordinator import MultiAgentCoordinator


# Global coordinator instance
coordinator = MultiAgentCoordinator()


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for dashboard API endpoints"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="dashboard", **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        
        if parsed.path == '/api/status':
            self.send_json(self._get_status())
        elif parsed.path == '/api/agents':
            self.send_json(self._get_agents())
        elif parsed.path == '/api/plan':
            self.send_json(self._get_24h_plan())
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        if parsed.path == '/api/task':
            result = self._submit_task(data)
            self.send_json(result)
        elif parsed.path == '/api/autonomous':
            result = self._start_autonomous()
            self.send_json(result)
        else:
            self.send_error(404, "Endpoint not found")
    
    def send_json(self, data):
        """Send JSON response"""
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)
    
    def _get_status(self):
        """Get coordinator status"""
        result = coordinator.execute({"action": "get_status"})
        return result.data
    
    def _get_agents(self):
        """Get agent distribution"""
        result = coordinator.execute({"action": "spawn_agents"})
        return result.data
    
    def _get_24h_plan(self):
        """Get 24-hour plan"""
        result = coordinator.execute({"action": "generate_24h_plan"})
        return result.data
    
    def _submit_task(self, data):
        """Submit task for execution"""
        result = coordinator.execute({
            "action": "autonomous_execute",
            "task": data.get("task", ""),
            "priority": data.get("priority", 3)
        })
        return result.data
    
    def _start_autonomous(self):
        """Start autonomous mode"""
        result = coordinator.execute({
            "action": "autonomous_execute",
            "autonomous_mode": True
        })
        return result.data


def run_server(port=8080):
    """Run dashboard server"""
    print(f"\n" + "=" * 70)
    print(f"🖥️  DIVE AI DASHBOARD SERVER")
    print(f"=" * 70)
    print(f"\n✅ Multi-Agent Coordinator initialized (512 agents)")
    print(f"\n📡 Starting server on http://localhost:{port}")
    print(f"   Dashboard: http://localhost:{port}/")
    print(f"\n   API Endpoints:")
    print(f"   GET  /api/status    - Coordinator status")
    print(f"   GET  /api/agents    - Agent distribution")
    print(f"   GET  /api/plan      - 24-hour plan")
    print(f"   POST /api/task      - Submit task")
    print(f"   POST /api/autonomous - Start autonomous mode")
    print(f"\n" + "=" * 70)
    print(f"Press Ctrl+C to stop the server")
    print(f"=" * 70)
    
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
