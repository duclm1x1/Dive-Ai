"""
Dive AI Proactive Heartbeat — Enhanced background monitoring and auto-action.
OpenClaw-style "Heartbeat" system that runs in background and triggers skills.
"""
import threading, time, json, os
from typing import Dict, List, Callable, Any, Optional


class HeartbeatMonitor:
    """Condition to monitor with auto-action when triggered."""
    def __init__(self, name: str, check_fn: Callable, action_fn: Callable,
                 interval: int = 60, cooldown: int = 300):
        self.name = name
        self.check_fn = check_fn        # Returns True when condition is met
        self.action_fn = action_fn      # Called when condition triggers
        self.interval = interval        # Check every N seconds
        self.cooldown = cooldown        # Min seconds between actions
        self.last_triggered = 0
        self.trigger_count = 0
        self.enabled = True


class ProactiveHeartbeat:
    """
    Enhanced always-on system that monitors conditions and auto-triggers skills.
    OpenClaw parity: background monitoring, auto-action, proactive suggestions.
    """

    def __init__(self, registry=None):
        self.registry = registry
        self.monitors: Dict[str, HeartbeatMonitor] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._log: List[Dict] = []
        self._state_file = os.path.expanduser("~/.dive-ai/heartbeat_state.json")
        os.makedirs(os.path.dirname(self._state_file), exist_ok=True)

    def add_monitor(self, monitor: HeartbeatMonitor):
        """Register a new monitor."""
        self.monitors[monitor.name] = monitor

    def add_skill_monitor(self, name: str, skill_name: str, check_inputs: Dict,
                          condition_fn: Callable, action_inputs: Dict,
                          interval: int = 60, cooldown: int = 300):
        """Add a monitor that checks a skill output and triggers an action skill."""
        if not self.registry:
            return

        def check():
            skill = self.registry.get(skill_name)
            if skill:
                result = skill.execute(check_inputs)
                return condition_fn(result)
            return False

        def action():
            # Execute the action by running the skill with action inputs
            skill = self.registry.get(skill_name)
            if skill:
                return skill.execute(action_inputs)

        self.add_monitor(HeartbeatMonitor(name, check, action, interval, cooldown))

    def remove_monitor(self, name: str):
        """Remove a monitor."""
        self.monitors.pop(name, None)

    def start(self):
        """Start the heartbeat background thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the heartbeat."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _loop(self):
        """Main heartbeat loop."""
        while self._running:
            now = time.time()
            for name, mon in list(self.monitors.items()):
                if not mon.enabled:
                    continue
                if now - mon.last_triggered < mon.cooldown:
                    continue

                try:
                    if mon.check_fn():
                        mon.action_fn()
                        mon.last_triggered = now
                        mon.trigger_count += 1
                        self._log.append({
                            "monitor": name, "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "trigger_count": mon.trigger_count,
                        })
                        # Keep log trimmed
                        if len(self._log) > 100:
                            self._log = self._log[-50:]
                except Exception as e:
                    self._log.append({
                        "monitor": name, "error": str(e),
                        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    })

            # Sleep for shortest interval
            min_interval = min((m.interval for m in self.monitors.values() if m.enabled), default=60)
            time.sleep(min_interval)

    def get_status(self) -> Dict:
        """Get heartbeat status."""
        return {
            "running": self._running,
            "monitors": {
                name: {
                    "enabled": m.enabled, "interval": m.interval,
                    "cooldown": m.cooldown, "triggers": m.trigger_count,
                    "last_triggered": time.strftime("%Y-%m-%d %H:%M:%S",
                        time.localtime(m.last_triggered)) if m.last_triggered else "never",
                }
                for name, m in self.monitors.items()
            },
            "total_monitors": len(self.monitors),
            "log_entries": len(self._log),
            "recent_log": self._log[-5:],
        }

    def save_state(self):
        """Save heartbeat state to disk."""
        state = {
            "monitors": {
                name: {"trigger_count": m.trigger_count, "last_triggered": m.last_triggered,
                       "enabled": m.enabled}
                for name, m in self.monitors.items()
            },
            "log": self._log[-50:],
        }
        with open(self._state_file, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        """Load heartbeat state from disk."""
        if os.path.exists(self._state_file):
            with open(self._state_file) as f:
                state = json.load(f)
            for name, data in state.get("monitors", {}).items():
                if name in self.monitors:
                    self.monitors[name].trigger_count = data.get("trigger_count", 0)
                    self.monitors[name].last_triggered = data.get("last_triggered", 0)
                    self.monitors[name].enabled = data.get("enabled", True)
            self._log = state.get("log", [])


# ── Pre-built monitors ──────────────────────────────

def create_default_monitors(heartbeat: ProactiveHeartbeat, registry=None):
    """Add default proactive monitors."""
    
    # 1. Disk space monitor — alert when disk < 10%
    def check_disk():
        try:
            import shutil
            usage = shutil.disk_usage("/")
            return (usage.free / usage.total) < 0.10
        except:
            return False

    def alert_disk():
        import shutil
        usage = shutil.disk_usage("/")
        pct = round(usage.free / usage.total * 100, 1)
        return {"alert": "low_disk", "free_percent": pct}

    heartbeat.add_monitor(HeartbeatMonitor("disk-space", check_disk, alert_disk, interval=300, cooldown=3600))

    # 2. High CPU monitor
    def check_cpu():
        try:
            import psutil
            return psutil.cpu_percent(interval=1) > 90
        except:
            return False

    heartbeat.add_monitor(HeartbeatMonitor("high-cpu", check_cpu, lambda: {"alert": "high_cpu"},
                                           interval=60, cooldown=600))

    # 3. Memory pressure monitor
    def check_memory():
        try:
            import psutil
            return psutil.virtual_memory().percent > 90
        except:
            return False

    heartbeat.add_monitor(HeartbeatMonitor("low-memory", check_memory, lambda: {"alert": "low_memory"},
                                           interval=60, cooldown=600))
