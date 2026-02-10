"""
📈 PERFORMANCE TRACKER
Track and analyze system performance

Based on V28's core_engine/performance_tracker.py
"""

import os
import sys
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class PerformanceMetric:
    """A performance metric"""
    name: str
    value: float
    unit: str
    timestamp: float


@dataclass
class PerformanceReport:
    """A performance report"""
    period_start: float
    period_end: float
    metrics: Dict[str, Dict] = field(default_factory=dict)


class PerformanceTrackerAlgorithm(BaseAlgorithm):
    """
    📈 Performance Tracker
    
    Tracks system performance:
    - Metric collection
    - Trend analysis
    - Bottleneck detection
    - Performance reporting
    
    From V28: core_engine/performance_tracker.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="PerformanceTracker",
            name="Performance Tracker",
            level="operational",
            category="monitoring",
            version="1.0",
            description="Track and analyze system performance",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "record/report/analyze"),
                    IOField("metric", "object", False, "Metric to record")
                ],
                outputs=[
                    IOField("result", "object", True, "Performance data")
                ]
            ),
            steps=["Collect metrics", "Aggregate data", "Analyze trends", "Generate reports"],
            tags=["performance", "metrics", "monitoring", "analysis"]
        )
        
        self.metrics: Dict[str, List[PerformanceMetric]] = {}
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "report")
        
        print(f"\n📈 Performance Tracker")
        
        if action == "record":
            return self._record_metric(params.get("metric", {}))
        elif action == "report":
            return self._generate_report()
        elif action == "analyze":
            return self._analyze_trends(params.get("metric_name", ""))
        elif action == "clear":
            return self._clear_metrics()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _record_metric(self, metric_data: Dict) -> AlgorithmResult:
        metric = PerformanceMetric(
            name=metric_data.get("name", "unknown"),
            value=metric_data.get("value", 0),
            unit=metric_data.get("unit", ""),
            timestamp=time.time()
        )
        
        if metric.name not in self.metrics:
            self.metrics[metric.name] = []
        self.metrics[metric.name].append(metric)
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[metric.name]) > 1000:
            self.metrics[metric.name] = self.metrics[metric.name][-1000:]
        
        return AlgorithmResult(
            status="success",
            data={"recorded": metric.name, "value": metric.value}
        )
    
    def _generate_report(self) -> AlgorithmResult:
        if not self.metrics:
            return AlgorithmResult(status="success", data={"report": "No metrics recorded"})
        
        report = {}
        now = time.time()
        
        for name, values in self.metrics.items():
            if not values:
                continue
            
            recent = [v for v in values if now - v.timestamp < 3600]  # Last hour
            
            if recent:
                vals = [v.value for v in recent]
                report[name] = {
                    "current": recent[-1].value,
                    "average": sum(vals) / len(vals),
                    "min": min(vals),
                    "max": max(vals),
                    "count": len(vals),
                    "unit": recent[-1].unit
                }
        
        return AlgorithmResult(
            status="success",
            data={
                "report": report,
                "metric_count": len(report),
                "period": "last_hour"
            }
        )
    
    def _analyze_trends(self, metric_name: str = "") -> AlgorithmResult:
        if metric_name and metric_name in self.metrics:
            metrics_to_analyze = {metric_name: self.metrics[metric_name]}
        else:
            metrics_to_analyze = self.metrics
        
        trends = {}
        
        for name, values in metrics_to_analyze.items():
            if len(values) < 2:
                trends[name] = {"trend": "insufficient_data"}
                continue
            
            # Simple trend calculation
            recent = values[-10:]
            older = values[-20:-10] if len(values) >= 20 else values[:10]
            
            recent_avg = sum(v.value for v in recent) / len(recent)
            older_avg = sum(v.value for v in older) / len(older) if older else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
            
            trends[name] = {
                "trend": trend,
                "recent_avg": recent_avg,
                "older_avg": older_avg,
                "change_pct": ((recent_avg - older_avg) / older_avg * 100) if older_avg else 0
            }
        
        return AlgorithmResult(
            status="success",
            data={"trends": trends}
        )
    
    def _clear_metrics(self) -> AlgorithmResult:
        count = sum(len(v) for v in self.metrics.values())
        self.metrics.clear()
        
        return AlgorithmResult(status="success", data={"cleared": count})


def register(algorithm_manager):
    algo = PerformanceTrackerAlgorithm()
    algorithm_manager.register("PerformanceTracker", algo)
    print("✅ PerformanceTracker registered")


if __name__ == "__main__":
    algo = PerformanceTrackerAlgorithm()
    algo.execute({"action": "record", "metric": {"name": "response_time", "value": 150, "unit": "ms"}})
    algo.execute({"action": "record", "metric": {"name": "response_time", "value": 120, "unit": "ms"}})
    algo.execute({"action": "record", "metric": {"name": "token_usage", "value": 1500, "unit": "tokens"}})
    result = algo.execute({"action": "report"})
    print(f"Metrics tracked: {result.data['metric_count']}")
