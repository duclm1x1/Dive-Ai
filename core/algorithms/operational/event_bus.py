"""
📡 EVENT BUS
Publish-subscribe event system

Based on V28's core_engine/event_bus.py
"""

import os
import sys
import time
from typing import Dict, Any, List, Callable
from dataclasses import dataclass, field

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from core.algorithms.base_algorithm import (
    BaseAlgorithm, AlgorithmResult, AlgorithmSpec, AlgorithmIOSpec, IOField
)


@dataclass
class EventSubscription:
    """An event subscription"""
    id: str
    event: str
    callback: Callable
    once: bool = False


@dataclass
class EventRecord:
    """A record of an emitted event"""
    event: str
    data: Dict
    timestamp: float
    listener_count: int


class EventBusAlgorithm(BaseAlgorithm):
    """
    📡 Event Bus
    
    Publish-subscribe system:
    - Event publishing
    - Subscription management
    - Async delivery
    - Event history
    
    From V28: core_engine/event_bus.py
    """
    
    def __init__(self):
        self.spec = AlgorithmSpec(
            algorithm_id="EventBus",
            name="Event Bus",
            level="operational",
            category="messaging",
            version="1.0",
            description="Publish-subscribe event system",
            io=AlgorithmIOSpec(
                inputs=[
                    IOField("action", "string", True, "subscribe/emit/unsubscribe"),
                    IOField("event", "string", False, "Event name"),
                    IOField("data", "object", False, "Event data")
                ],
                outputs=[
                    IOField("result", "object", True, "Operation result")
                ]
            ),
            steps=["Register handlers", "Emit events", "Deliver to subscribers", "Track history"],
            tags=["events", "pubsub", "messaging"]
        )
        
        self.subscriptions: Dict[str, List[EventSubscription]] = {}
        self.history: List[EventRecord] = []
        self.sub_counter = 0
    
    def execute(self, params: Dict[str, Any]) -> AlgorithmResult:
        action = params.get("action", "list")
        
        print(f"\n📡 Event Bus")
        
        if action == "subscribe":
            return self._subscribe(params.get("event", ""), params.get("once", False))
        elif action == "emit":
            return self._emit(params.get("event", ""), params.get("data", {}))
        elif action == "unsubscribe":
            return self._unsubscribe(params.get("subscription_id", ""))
        elif action == "list":
            return self._list()
        elif action == "history":
            return self._get_history()
        else:
            return AlgorithmResult(status="error", error=f"Unknown action: {action}")
    
    def _subscribe(self, event: str, once: bool = False) -> AlgorithmResult:
        if not event:
            return AlgorithmResult(status="error", error="Event name required")
        
        self.sub_counter += 1
        sub = EventSubscription(
            id=f"sub_{self.sub_counter}",
            event=event,
            callback=lambda d: d,  # Placeholder
            once=once
        )
        
        if event not in self.subscriptions:
            self.subscriptions[event] = []
        self.subscriptions[event].append(sub)
        
        print(f"   Subscribed: {sub.id} -> {event}")
        
        return AlgorithmResult(
            status="success",
            data={"subscription_id": sub.id, "event": event}
        )
    
    def _emit(self, event: str, data: Dict) -> AlgorithmResult:
        if not event:
            return AlgorithmResult(status="error", error="Event name required")
        
        subs = self.subscriptions.get(event, [])
        delivered = 0
        to_remove = []
        
        for sub in subs:
            try:
                sub.callback(data)
                delivered += 1
                if sub.once:
                    to_remove.append(sub)
            except:
                pass
        
        # Remove one-time subscriptions
        for sub in to_remove:
            subs.remove(sub)
        
        # Record history
        self.history.append(EventRecord(
            event=event,
            data=data,
            timestamp=time.time(),
            listener_count=delivered
        ))
        
        print(f"   Emitted: {event} -> {delivered} listeners")
        
        return AlgorithmResult(
            status="success",
            data={"event": event, "delivered": delivered}
        )
    
    def _unsubscribe(self, subscription_id: str) -> AlgorithmResult:
        for event, subs in self.subscriptions.items():
            for sub in subs:
                if sub.id == subscription_id:
                    subs.remove(sub)
                    return AlgorithmResult(
                        status="success",
                        data={"unsubscribed": subscription_id}
                    )
        
        return AlgorithmResult(status="error", error="Subscription not found")
    
    def _list(self) -> AlgorithmResult:
        events = []
        for event, subs in self.subscriptions.items():
            events.append({"event": event, "subscribers": len(subs)})
        
        return AlgorithmResult(
            status="success",
            data={"events": events, "total_subscriptions": sum(len(s) for s in self.subscriptions.values())}
        )
    
    def _get_history(self) -> AlgorithmResult:
        return AlgorithmResult(
            status="success",
            data={
                "history": [
                    {"event": r.event, "listeners": r.listener_count, "timestamp": r.timestamp}
                    for r in self.history[-50:]
                ]
            }
        )


def register(algorithm_manager):
    algo = EventBusAlgorithm()
    algorithm_manager.register("EventBus", algo)
    print("✅ EventBus registered")


if __name__ == "__main__":
    algo = EventBusAlgorithm()
    algo.execute({"action": "subscribe", "event": "task.completed"})
    algo.execute({"action": "subscribe", "event": "task.completed"})
    result = algo.execute({"action": "emit", "event": "task.completed", "data": {"task_id": "123"}})
    print(f"Delivered to: {result.data['delivered']} listeners")
