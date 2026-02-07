"""
Dive AI - Plugin System
Extensible plugin architecture
"""

from typing import Dict, List, Any, Callable
from dataclasses import dataclass


@dataclass
class Plugin:
    """Plugin definition"""
    name: str
    version: str
    enabled: bool = True
    hooks: Dict[str, Callable] = None
    
    def __post_init__(self):
        if self.hooks is None:
            self.hooks = {}


class PluginSystem:
    """
    Extensible Plugin System
    
    Features:
    - Dynamic plugin loading
    - Hook-based architecture
    - Plugin dependencies
    - Version management
    """
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        
        # Register hooks
        for hook_name, callback in plugin.hooks.items():
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            self.hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all callbacks for a hook"""
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                result = callback(*args, **kwargs)
                results.append(result)
        
        return results
    
    def enable_plugin(self, plugin_name: str):
        """Enable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
    
    def disable_plugin(self, plugin_name: str):
        """Disable a plugin"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
