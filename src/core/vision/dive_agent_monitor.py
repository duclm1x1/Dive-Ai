"""
Dive Agent Fleet Monitoring Indicator
Real-time visual monitoring of 128-agent fleet activity
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum


class MonitorDisplay(Enum):
    """Display modes for monitoring"""
    COMPACT = "compact"      # Single line status
    DETAILED = "detailed"    # Multi-line with details
    DASHBOARD = "dashboard"  # Full dashboard view


@dataclass
class AgentMetrics:
    """Metrics for a single agent"""
    agent_id: int
    status: str
    task_name: str
    start_time: float
    elapsed: float
    progress: int  # 0-100


class DiveAgentMonitor:
    """
    Real-time monitoring indicator for 128-agent fleet
    
    Features:
    - Live agent status display
    - Progress tracking
    - Performance metrics
    - Visual indicators
    """
    
    def __init__(self, total_agents: int = 128):
        self.total_agents = total_agents
        self.agent_metrics: Dict[int, AgentMetrics] = {}
        self.start_time = time.time()
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.display_mode = MonitorDisplay.DETAILED
        
    def update_agent(self, agent_id: int, status: str, task_name: str, 
                    progress: int = 0, start_time: float = None):
        """Update agent status"""
        if start_time is None:
            start_time = time.time()
            
        elapsed = time.time() - start_time
        
        self.agent_metrics[agent_id] = AgentMetrics(
            agent_id=agent_id,
            status=status,
            task_name=task_name,
            start_time=start_time,
            elapsed=elapsed,
            progress=progress
        )
    
    def mark_completed(self, agent_id: int):
        """Mark agent task as completed"""
        if agent_id in self.agent_metrics:
            self.agent_metrics[agent_id].status = "completed"
            self.agent_metrics[agent_id].progress = 100
        self.completed_tasks += 1
    
    def mark_failed(self, agent_id: int):
        """Mark agent task as failed"""
        if agent_id in self.agent_metrics:
            self.agent_metrics[agent_id].status = "failed"
        self.failed_tasks += 1
    
    def get_status_counts(self) -> Dict[str, int]:
        """Get count of agents by status"""
        counts = {
            "idle": 0,
            "working": 0,
            "completed": 0,
            "failed": 0
        }
        
        for metric in self.agent_metrics.values():
            status = metric.status.lower()
            if status in counts:
                counts[status] += 1
        
        counts["idle"] = self.total_agents - sum(counts.values())
        return counts
    
    def get_progress_bar(self, progress: int, width: int = 20) -> str:
        """Generate progress bar"""
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {progress}%"
    
    def get_status_icon(self, status: str) -> str:
        """Get icon for status"""
        icons = {
            "idle": "⚪",
            "working": "🔵",
            "completed": "✅",
            "failed": "❌"
        }
        return icons.get(status.lower(), "⚪")
    
    def render_compact(self) -> str:
        """Render compact single-line status"""
        counts = self.get_status_counts()
        elapsed = time.time() - self.start_time
        
        return (
            f"🤖 Fleet: {counts['working']}/{self.total_agents} working | "
            f"✅ {counts['completed']} done | "
            f"❌ {counts['failed']} failed | "
            f"⏱️ {elapsed:.1f}s"
        )
    
    def render_detailed(self) -> str:
        """Render detailed multi-line status"""
        counts = self.get_status_counts()
        elapsed = time.time() - self.start_time
        
        lines = [
            "=" * 70,
            "🤖 DIVE AGENT FLEET MONITOR",
            "=" * 70,
            f"⏱️  Elapsed: {elapsed:.1f}s",
            f"📊 Status: {counts['working']}/{self.total_agents} agents working",
            "",
            f"   ⚪ Idle:      {counts['idle']:3d}",
            f"   🔵 Working:   {counts['working']:3d}",
            f"   ✅ Completed: {counts['completed']:3d}",
            f"   ❌ Failed:    {counts['failed']:3d}",
            "",
        ]
        
        # Show active agents
        if self.agent_metrics:
            lines.append("🔄 Active Agents:")
            lines.append("-" * 70)
            
            # Show up to 10 most recent active agents
            active = [m for m in self.agent_metrics.values() 
                     if m.status.lower() == "working"]
            active = sorted(active, key=lambda x: x.start_time, reverse=True)[:10]
            
            for metric in active:
                icon = self.get_status_icon(metric.status)
                progress_bar = self.get_progress_bar(metric.progress, 15)
                task_name = metric.task_name[:30]
                lines.append(
                    f"   {icon} Agent #{metric.agent_id:3d} | "
                    f"{progress_bar} | "
                    f"{task_name}"
                )
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def render_dashboard(self) -> str:
        """Render full dashboard view"""
        counts = self.get_status_counts()
        elapsed = time.time() - self.start_time
        
        # Calculate metrics
        total_tasks = self.completed_tasks + self.failed_tasks
        success_rate = (self.completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        avg_time = elapsed / total_tasks if total_tasks > 0 else 0
        
        lines = [
            "",
            "╔" + "═" * 68 + "╗",
            "║" + " " * 20 + "🤖 DIVE AGENT FLEET DASHBOARD" + " " * 18 + "║",
            "╠" + "═" * 68 + "╣",
            f"║  ⏱️  Runtime: {elapsed:.1f}s" + " " * (68 - 20 - len(f"{elapsed:.1f}")) + "║",
            f"║  📊 Fleet Size: {self.total_agents} agents" + " " * (68 - 27) + "║",
            "╠" + "═" * 68 + "╣",
            "║  STATUS DISTRIBUTION" + " " * 47 + "║",
            "╠" + "─" * 68 + "╣",
            f"║     ⚪ Idle:      {counts['idle']:3d} agents" + " " * (68 - 29) + "║",
            f"║     🔵 Working:   {counts['working']:3d} agents" + " " * (68 - 29) + "║",
            f"║     ✅ Completed: {counts['completed']:3d} tasks" + " " * (68 - 28) + "║",
            f"║     ❌ Failed:    {counts['failed']:3d} tasks" + " " * (68 - 27) + "║",
            "╠" + "═" * 68 + "╣",
            "║  PERFORMANCE METRICS" + " " * 46 + "║",
            "╠" + "─" * 68 + "╣",
            f"║     Success Rate: {success_rate:.1f}%" + " " * (68 - 25 - len(f"{success_rate:.1f}")) + "║",
            f"║     Avg Task Time: {avg_time:.2f}s" + " " * (68 - 26 - len(f"{avg_time:.2f}")) + "║",
            f"║     Tasks/Second: {(total_tasks/elapsed if elapsed > 0 else 0):.2f}" + " " * (68 - 25 - len(f"{(total_tasks/elapsed if elapsed > 0 else 0):.2f}")) + "║",
            "╚" + "═" * 68 + "╝",
            ""
        ]
        
        return "\n".join(lines)
    
    def render(self, mode: MonitorDisplay = None) -> str:
        """Render monitor display"""
        if mode is None:
            mode = self.display_mode
        
        if mode == MonitorDisplay.COMPACT:
            return self.render_compact()
        elif mode == MonitorDisplay.DETAILED:
            return self.render_detailed()
        elif mode == MonitorDisplay.DASHBOARD:
            return self.render_dashboard()
        else:
            return self.render_detailed()
    
    def print_status(self, mode: MonitorDisplay = None):
        """Print current status"""
        print("\033[2J\033[H")  # Clear screen
        print(self.render(mode))
    
    async def monitor_loop(self, interval: float = 1.0, mode: MonitorDisplay = None):
        """Run monitoring loop"""
        try:
            while True:
                self.print_status(mode)
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")


# Example usage
async def demo():
    """Demo the monitoring system"""
    monitor = DiveAgentMonitor(total_agents=128)
    
    # Simulate some agent activity
    for i in range(10):
        monitor.update_agent(
            agent_id=i,
            status="working",
            task_name=f"Implementing feature {i+1}",
            progress=50
        )
    
    # Show different display modes
    print("\n📊 COMPACT MODE:")
    print(monitor.render(MonitorDisplay.COMPACT))
    
    await asyncio.sleep(1)
    
    print("\n\n📊 DETAILED MODE:")
    print(monitor.render(MonitorDisplay.DETAILED))
    
    await asyncio.sleep(1)
    
    print("\n\n📊 DASHBOARD MODE:")
    print(monitor.render(MonitorDisplay.DASHBOARD))
    
    # Mark some as completed
    for i in range(5):
        monitor.mark_completed(i)
    
    await asyncio.sleep(1)
    
    print("\n\n📊 UPDATED DASHBOARD:")
    print(monitor.render(MonitorDisplay.DASHBOARD))


if __name__ == "__main__":
    asyncio.run(demo())
