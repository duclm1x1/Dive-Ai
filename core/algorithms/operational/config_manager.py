"""
⚙️ CONFIG MANAGER
Manage configuration across the system

Based on V28's core_engine/config_manager.py
"""

import os
import sys
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class ConfigSource:
    """A configuration source"""
    name: str
    priority: int
    values: Dict


class ConfigManagerAlgorithm(BaseAlgorithm):
    """
    ⚙️ Config Manager
    
    Manages configuration:
    - Multi-source config
    - Priority-based merging
    - Environment overrides
    - Runtime updates
    
    From V28: core_engine/config_manager.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="ConfigManager",
            name="Config Manager",
            level="operational",
            category="system",
            version="1.0",
            description="Manage configuration across the system",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "get/set/load"),
                    IOField("key", "string", False, "Config key"),
                    IOField("value", "any", False, "Config value")
                ],
                outputs=[
                    IOField("result", "any", True, "Config value or status")
                ]
            ),
            steps=["Load sources", "Merge by priority", "Apply overrides", "Cache result"],
            tags=["config", "settings", "management"]
        )
        
        self.sources: Dict[str, ConfigSource] = {}
        self.merged_config: Dict[str, Any] = {}
        self._add_default_source()
    
    def _add_default_source(self):
        self.sources["default"] = ConfigSource(
            name="default",
            priority=0,
            values={
                "debug": False,
                "log_level": "INFO",
                "max_tokens": 4096,
                "temperature": 0.7,
                "timeout": 30
            }
        )
        self._merge_configs()
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "get")
        
        print(f"\n⚙️ Config Manager")
        
        if action == "get":
            return self._get_config(params.get("key"))
        elif action == "set":
            return self._set_config(params.get("key", ""), params.get("value"))
        elif action == "load":
            return self._load_source(params.get("source", {}))
        elif action == "list":
            return self._list_config()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _get_config(self, key: Optional[str]) -> AlgorithmResult:
        if key:
            # Support nested keys with dot notation
            value = self._get_nested(self.merged_config, key)
            return AlgorithmResult(
                status="success",
                data={"key": key, "value": value}
            )
        
        return AlgorithmResult(
            status="success",
            data={"config": self.merged_config}
        )
    
    def _get_nested(self, config: Dict, key: str) -> Any:
        parts = key.split(".")
        value = config
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        return value
    
    def _set_config(self, key: str, value: Any) -> AlgorithmResult:
        if not key:
            return AlgorithmResult(status="error", error="No key provided")
        
        # Add to runtime source
        if "runtime" not in self.sources:
            self.sources["runtime"] = ConfigSource(
                name="runtime",
                priority=100,
                values={}
            )
        
        self.sources["runtime"].values[key] = value
        self._merge_configs()
        
        return AlgorithmResult(
            status="success",
            data={"key": key, "value": value, "set": True}
        )
    
    def _load_source(self, source_data: Dict) -> AlgorithmResult:
        name = source_data.get("name", f"source_{len(self.sources)}")
        priority = source_data.get("priority", 50)
        values = source_data.get("values", {})
        
        self.sources[name] = ConfigSource(
            name=name,
            priority=priority,
            values=values
        )
        self._merge_configs()
        
        return AlgorithmResult(
            status="success",
            data={"loaded": name, "keys": len(values)}
        )
    
    def _merge_configs(self):
        """Merge configs by priority (higher priority wins)"""
        sorted_sources = sorted(
            self.sources.values(),
            key=lambda s: s.priority
        )
        
        self.merged_config = {}
        for source in sorted_sources:
            self._deep_merge(self.merged_config, source.values)
    
    def _deep_merge(self, base: Dict, override: Dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _list_config(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "sources": [
                    {"name": s.name, "priority": s.priority, "keys": len(s.values)}
                    for s in sorted(self.sources.values(), key=lambda x: x.priority)
                ],
                "merged_keys": list(self.merged_config.keys())
            }
        )


def register(algorithm_manager):
    algo = ConfigManagerAlgorithm()
    algorithm_manager.register("ConfigManager", algo)
    print("✅ ConfigManager registered")


if __name__ == "__main__":
    algo = ConfigManagerAlgorithm()
    result = algo.execute({"action": "get", "key": "max_tokens"})
    print(f"max_tokens: {result.data['value']}")
    
    algo.execute({"action": "set", "key": "debug", "value": True})
    result = algo.execute({"action": "get", "key": "debug"})
    print(f"debug: {result.data['value']}")
