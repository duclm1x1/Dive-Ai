#!/usr/bin/env python3
"""
Dive Monitoring Dashboard - V23.1 Component

Real-time monitoring dashboard for all Dive AI components.
Tracks performance, health, and usage statistics.
"""

import time
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class ComponentHealth(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentMetrics:
    """Metrics for a component"""
    component_name: str
    version: str
    health: ComponentHealth
    uptime: float
    requests_total: int
    requests_success: int
    requests_failed: int
    avg_response_time: float
    last_error: Optional[str] = None
    last_updated: str = ""


@dataclass
class SystemMetrics:
    """Overall system metrics"""
    total_components: int
    healthy_components: int
    degraded_components: int
    unhealthy_components: int
    total_requests: int
    total_success: int
    total_failures: int
    avg_response_time: float
    uptime: float


class DiveMonitoringDashboard:
    """
    Real-time monitoring dashboard for Dive AI.
    
    Features:
    - Component health tracking
    - Performance metrics
    - Real-time updates
    - Historical data
    - Alerts and notifications
    """
    
    def __init__(self):
        self.components: Dict[str, ComponentMetrics] = {}
        self.start_time = time.time()
        self.history: List[Dict] = []
        self.alerts: List[Dict] = []
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all Dive AI components"""
        components_def = [
            ("Search Engine", "21.0.0"),
            ("Thinking Engine", "22.0.0"),
            ("Claims Ledger", "22.0.0"),
            ("Adaptive RAG", "22.0.0"),
            ("Workflow Engine", "23.1.0"),
            ("CRUEL System", "23.1.0"),
            ("DAG Parallel", "23.1.0"),
            ("Distributed Execution", "23.1.0"),
            ("Update System", "23.1.0"),
            ("Orchestrator", "23.1.0"),
            ("Memory System", "21.0.0"),
            ("Smart Coder", "23.1.0")
        ]
        
        for name, version in components_def:
            self.components[name] = ComponentMetrics(
                component_name=name,
                version=version,
                health=ComponentHealth.HEALTHY,
                uptime=0.0,
                requests_total=0,
                requests_success=0,
                requests_failed=0,
                avg_response_time=0.0,
                last_updated=datetime.now().isoformat()
            )
    
    def update_component(
        self,
        component_name: str,
        success: bool,
        response_time: float,
        error: Optional[str] = None
    ):
        """Update component metrics"""
        if component_name not in self.components:
            return
        
        comp = self.components[component_name]
        comp.requests_total += 1
        
        if success:
            comp.requests_success += 1
        else:
            comp.requests_failed += 1
            comp.last_error = error
        
        # Update average response time
        total_time = comp.avg_response_time * (comp.requests_total - 1) + response_time
        comp.avg_response_time = total_time / comp.requests_total
        
        # Update health
        failure_rate = comp.requests_failed / comp.requests_total if comp.requests_total > 0 else 0
        if failure_rate > 0.5:
            comp.health = ComponentHealth.UNHEALTHY
            self._create_alert(component_name, "Component unhealthy", f"Failure rate: {failure_rate:.1%}")
        elif failure_rate > 0.2:
            comp.health = ComponentHealth.DEGRADED
            self._create_alert(component_name, "Component degraded", f"Failure rate: {failure_rate:.1%}")
        else:
            comp.health = ComponentHealth.HEALTHY
        
        comp.uptime = time.time() - self.start_time
        comp.last_updated = datetime.now().isoformat()
        
        # Record history
        self._record_history()
    
    def _create_alert(self, component: str, title: str, message: str):
        """Create an alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'title': title,
            'message': message
        }
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _record_history(self):
        """Record current state to history"""
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': asdict(self.get_system_metrics()),
            'component_count': len(self.components)
        }
        self.history.append(snapshot)
        
        # Keep only last 1000 snapshots
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
    
    def get_component_metrics(self, component_name: str) -> Optional[ComponentMetrics]:
        """Get metrics for a specific component"""
        return self.components.get(component_name)
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get overall system metrics"""
        healthy = sum(1 for c in self.components.values() if c.health == ComponentHealth.HEALTHY)
        degraded = sum(1 for c in self.components.values() if c.health == ComponentHealth.DEGRADED)
        unhealthy = sum(1 for c in self.components.values() if c.health == ComponentHealth.UNHEALTHY)
        
        total_requests = sum(c.requests_total for c in self.components.values())
        total_success = sum(c.requests_success for c in self.components.values())
        total_failures = sum(c.requests_failed for c in self.components.values())
        
        avg_response = sum(c.avg_response_time * c.requests_total for c in self.components.values())
        avg_response = avg_response / total_requests if total_requests > 0 else 0.0
        
        return SystemMetrics(
            total_components=len(self.components),
            healthy_components=healthy,
            degraded_components=degraded,
            unhealthy_components=unhealthy,
            total_requests=total_requests,
            total_success=total_success,
            total_failures=total_failures,
            avg_response_time=avg_response,
            uptime=time.time() - self.start_time
        )
    
    def get_dashboard(self) -> Dict:
        """Get complete dashboard data"""
        return {
            'system_metrics': asdict(self.get_system_metrics()),
            'components': {
                name: {
                    **asdict(metrics),
                    'health': metrics.health.value  # Convert enum to string
                }
                for name, metrics in self.components.items()
            },
            'recent_alerts': self.alerts[-10:],
            'timestamp': datetime.now().isoformat()
        }
    
    def print_dashboard(self):
        """Print dashboard to console"""
        system = self.get_system_metrics()
        
        print("\n" + "="*70)
        print("🔍 DIVE AI MONITORING DASHBOARD")
        print("="*70)
        
        print(f"\n📊 SYSTEM OVERVIEW")
        print(f"  Uptime: {system.uptime:.1f}s")
        print(f"  Components: {system.total_components}")
        print(f"    ✅ Healthy: {system.healthy_components}")
        print(f"    ⚠️  Degraded: {system.degraded_components}")
        print(f"    ❌ Unhealthy: {system.unhealthy_components}")
        print(f"  Requests: {system.total_requests}")
        print(f"    ✅ Success: {system.total_success}")
        print(f"    ❌ Failed: {system.total_failures}")
        print(f"  Avg Response Time: {system.avg_response_time:.3f}s")
        
        print(f"\n🔧 COMPONENT STATUS")
        for name, comp in sorted(self.components.items()):
            health_icon = {
                ComponentHealth.HEALTHY: "✅",
                ComponentHealth.DEGRADED: "⚠️ ",
                ComponentHealth.UNHEALTHY: "❌",
                ComponentHealth.UNKNOWN: "❓"
            }[comp.health]
            
            print(f"  {health_icon} {name} (v{comp.version})")
            if comp.requests_total > 0:
                success_rate = comp.requests_success / comp.requests_total * 100
                print(f"      Requests: {comp.requests_total} ({success_rate:.1f}% success)")
                print(f"      Avg time: {comp.avg_response_time:.3f}s")
        
        if self.alerts:
            print(f"\n🚨 RECENT ALERTS ({len(self.alerts)})")
            for alert in self.alerts[-5:]:
                print(f"  [{alert['timestamp']}] {alert['component']}: {alert['title']}")
                print(f"      {alert['message']}")
        
        print("\n" + "="*70 + "\n")
    
    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        data = self.get_dashboard()
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Test monitoring dashboard"""
    print("=== Dive Monitoring Dashboard Test ===\n")
    
    dashboard = DiveMonitoringDashboard()
    
    # Simulate some activity
    print("Simulating component activity...\n")
    
    components = list(dashboard.components.keys())
    
    # Successful requests
    for _ in range(10):
        for comp in components[:8]:  # Most components work fine
            dashboard.update_component(comp, success=True, response_time=0.1)
    
    # Some failures
    for _ in range(3):
        dashboard.update_component("Workflow Engine", success=False, response_time=0.5, error="Timeout")
    
    # Print dashboard
    dashboard.print_dashboard()
    
    # Export metrics
    dashboard.export_metrics("/tmp/dive_metrics.json")
    print("Metrics exported to /tmp/dive_metrics.json")


if __name__ == "__main__":
    main()
