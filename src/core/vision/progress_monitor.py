#!/usr/bin/env python3
"""
Dive AI V20 Progress Monitor
Real-time dashboard showing 128 agents working
"""

import json
import time
import os
from datetime import datetime

PROGRESS_FILE = "/tmp/dive_ai_progress.json"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def format_duration(ms):
    """Format milliseconds to human readable"""
    if ms < 1000:
        return f"{ms:.0f}ms"
    elif ms < 60000:
        return f"{ms/1000:.1f}s"
    else:
        return f"{ms/60000:.1f}m"

def render_agent_grid(agents, cols=16):
    """Render agents in a grid"""
    rows = (len(agents) + cols - 1) // cols
    
    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row * cols + col
            if idx < len(agents):
                agent = agents[idx]
                status = agent.get('status', 'idle')
                
                if status == 'complete':
                    symbol = '✓'
                    color = '\033[92m'  # Green
                elif status == 'working':
                    symbol = '●'
                    color = '\033[93m'  # Yellow
                elif status == 'error':
                    symbol = '✗'
                    color = '\033[91m'  # Red
                else:
                    symbol = '○'
                    color = '\033[90m'  # Gray
                
                line += f"{color}{symbol}\033[0m "
            else:
                line += "  "
        print(line)

def monitor():
    """Monitor progress in real-time"""
    print("\n" + "="*100)
    print("DIVE AI V20 - AGENT PROGRESS MONITOR")
    print("="*100 + "\n")
    print("Waiting for orchestrator to start...\n")
    
    last_update = None
    
    while True:
        try:
            if not os.path.exists(PROGRESS_FILE):
                time.sleep(1)
                continue
            
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            
            # Check if data changed
            current_update = progress.get('last_update')
            if current_update == last_update:
                time.sleep(0.5)
                continue
            
            last_update = current_update
            clear_screen()
            
            # Header
            print("\n" + "="*100)
            print("DIVE AI V20 - AGENT PROGRESS MONITOR")
            print("="*100 + "\n")
            
            # Overall status
            task = progress.get('task', 'Unknown')
            phase = progress.get('phase', 'Initializing')
            total_agents = progress.get('total_agents', 128)
            agents = progress.get('agents', [])
            
            complete = sum(1 for a in agents if a.get('status') == 'complete')
            working = sum(1 for a in agents if a.get('status') == 'working')
            errors = sum(1 for a in agents if a.get('status') == 'error')
            idle = total_agents - complete - working - errors
            
            completion_pct = (complete / total_agents * 100) if total_agents > 0 else 0
            
            print(f"Task: {task[:80]}...")
            print(f"Phase: {phase}")
            print(f"\nProgress: {complete}/{total_agents} agents ({completion_pct:.1f}%)")
            print(f"Status: ✓ {complete} Complete | ● {working} Working | ○ {idle} Idle | ✗ {errors} Errors")
            
            # Progress bar
            bar_width = 50
            filled = int(bar_width * completion_pct / 100)
            bar = '█' * filled + '░' * (bar_width - filled)
            print(f"\n[{bar}] {completion_pct:.1f}%\n")
            
            # Agent grid
            print("Agent Status Grid (128 agents):\n")
            render_agent_grid(agents)
            
            # Active agents details
            active_agents = [a for a in agents if a.get('status') == 'working']
            if active_agents:
                print(f"\n\nCurrently Working ({len(active_agents)} agents):")
                print("-" * 100)
                for agent in active_agents[:10]:  # Show first 10
                    agent_id = agent.get('agent_id', '?')
                    subtask = agent.get('subtask', 'Unknown')[:60]
                    model = agent.get('model', '?').upper()
                    elapsed = agent.get('elapsed_ms', 0)
                    print(f"  Agent #{agent_id:3d} [{model:6s}] {subtask}... ({format_duration(elapsed)})")
            
            # Recent completions
            recent = [a for a in agents if a.get('status') == 'complete'][-5:]
            if recent:
                print(f"\n\nRecent Completions ({len(recent)}):")
                print("-" * 100)
                for agent in recent:
                    agent_id = agent.get('agent_id', '?')
                    subtask = agent.get('subtask', 'Unknown')[:60]
                    model = agent.get('model', '?').upper()
                    duration = agent.get('duration_ms', 0)
                    tokens = agent.get('tokens', {}).get('total', 0)
                    print(f"  Agent #{agent_id:3d} [{model:6s}] {subtask}... ({format_duration(duration)}, {tokens} tokens)")
            
            # Errors
            error_agents = [a for a in agents if a.get('status') == 'error']
            if error_agents:
                print(f"\n\nErrors ({len(error_agents)}):")
                print("-" * 100)
                for agent in error_agents[:5]:
                    agent_id = agent.get('agent_id', '?')
                    error = agent.get('error', 'Unknown error')[:70]
                    print(f"  Agent #{agent_id:3d} ERROR: {error}")
            
            # Footer
            print("\n" + "="*100)
            print(f"Last Update: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to exit")
            print("="*100)
            
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n\nMonitor stopped.")
            break
        except Exception as e:
            print(f"\nError reading progress: {e}")
            time.sleep(1)

if __name__ == "__main__":
    monitor()
