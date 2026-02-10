"""
🌐 DIVE AI - MULTI-GATEWAY ORCHESTRATOR
OpenClaw-inspired multiple gateway system for parallel processing

Architecture:
- Multiple independent gateways running in parallel
- Each gateway handles: Algorithms, Skills, Thinking Methods
- Load balancing between gateways
- Unified scoring and metric collection
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from queue import Queue
import time

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.algorithms.algorithm_manager import AlgorithmManager


class GatewayStatus(Enum):
    """Gateway status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class GatewayRequest:
    """Request to be processed by gateway"""
    request_id: str
    user_input: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 3  # 1-5, 5 is highest
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class GatewayResponse:
    """Response from gateway"""
    request_id: str
    gateway_id: str
    status: GatewayStatus
    result: Dict[str, Any]
    execution_time_ms: float
    algorithms_used: List[str] = field(default_factory=list)
    thinking_method: str = ""
    score: float = 0.0
    error: Optional[str] = None


class Gateway:
    """
    Individual Gateway Instance
    
    Each gateway can:
    - Select and execute algorithms
    - Apply thinking methods
    - Calculate scores
    - Process requests independently
    """
    
    def __init__(self, gateway_id: str, algorithm_manager: AlgorithmManager):
        self.gateway_id = gateway_id
        self.algorithm_manager = algorithm_manager
        self.status = GatewayStatus.IDLE
        self.requests_processed = 0
        self.total_execution_time = 0.0
        self.current_request: Optional[GatewayRequest] = None
        
        print(f"   🌐 Gateway {gateway_id} initialized")
    
    async def process_request(self, request: GatewayRequest) -> GatewayResponse:
        """Process a single request through this gateway"""
        self.status = GatewayStatus.BUSY
        self.current_request = request
        start_time = time.time()
        
        try:
            # Step 1: Select best algorithms
            algorithms = self._select_algorithms(request.user_input)
            
            # Step 2: Choose thinking method
            thinking_method = self._select_thinking_method(request.context)
            
            # Step 3: Execute with selected approach
            result = await self._execute(request, algorithms, thinking_method)
            
            # Step 4: Calculate score
            score = self._calculate_score(result, algorithms, thinking_method)
            
            execution_time_ms = (time.time() - start_time) * 1000
            self.requests_processed += 1
            self.total_execution_time += execution_time_ms
            
            self.status = GatewayStatus.IDLE
            self.current_request = None
            
            return GatewayResponse(
                request_id=request.request_id,
                gateway_id=self.gateway_id,
                status=GatewayStatus.IDLE,
                result=result,
                execution_time_ms=execution_time_ms,
                algorithms_used=[a['id'] for a in algorithms],
                thinking_method=thinking_method,
                score=score
            )
            
        except Exception as e:
            self.status = GatewayStatus.ERROR
            self.current_request = None
            
            return GatewayResponse(
                request_id=request.request_id,
                gateway_id=self.gateway_id,
                status=GatewayStatus.ERROR,
                result={},
                execution_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
                score=0.0
            )
    
    def _select_algorithms(self, user_input: str) -> List[Dict[str, Any]]:
        """Select best algorithms for the task"""
        # Score all available algorithms
        all_algorithms = self.algorithm_manager.list_algorithms()
        
        scored_algorithms = []
        for algo in all_algorithms:
            score = self._score_algorithm(algo, user_input)
            scored_algorithms.append({
                'id': algo.get('id', 'unknown'),
                'algorithm': algo,
                'score': score
            })
        
        # Sort by score and take top 3 (prioritize combinations)
        scored_algorithms.sort(key=lambda x: x['score'], reverse=True)
        return scored_algorithms[:3]
    
    def _score_algorithm(self, algorithm: Dict[str, Any], user_input: str) -> float:
        """Score algorithm based on context match"""
        score = 0.5  # Base score
        
        # Check if algorithm tags match user input
        tags = algorithm.get('tags', [])
        for tag in tags:
            if tag.lower() in user_input.lower():
                score += 0.2
        
        # Check historical success rate
        stats = self.algorithm_manager.get_stats(algorithm.get('id', ''))
        if stats:
            success_rate = stats.get('success_rate', 0.5)
            score += success_rate * 0.3
        
        return min(score, 1.0)
    
    def _select_thinking_method(self, context: Dict[str, Any]) -> str:
        """Select thinking method based on task complexity"""
        complexity = context.get('complexity', 'medium')
        
        methods = {
            'simple': 'direct',
            'medium': 'antigravity',
            'complex': 'claude_extended',
            'very_complex': 'openai_reasoning'
        }
        
        return methods.get(complexity, 'antigravity')
    
    async def _execute(
        self, 
        request: GatewayRequest, 
        algorithms: List[Dict[str, Any]], 
        thinking_method: str
    ) -> Dict[str, Any]:
        """Execute request with selected algorithms and thinking method"""
        
        results = []
        
        for algo_info in algorithms:
            algo = algo_info['algorithm']
            algo_id = algo_info['id']
            
            # Get algorithm instance
            algo_instance = self.algorithm_manager.get_algorithm(algo_id)
            
            if algo_instance:
                try:
                    # Execute algorithm
                    result = algo_instance.execute({
                        'user_input': request.user_input,
                        'context': request.context,
                        'thinking_method': thinking_method
                    })
                    
                    results.append({
                        'algorithm_id': algo_id,
                        'result': result,
                        'success': result.status == 'success' if hasattr(result, 'status') else True
                    })
                except Exception as e:
                    results.append({
                        'algorithm_id': algo_id,
                        'result': None,
                        'success': False,
                        'error': str(e)
                    })
        
        return {
            'thinking_method': thinking_method,
            'algorithms_executed': len(results),
            'results': results,
            'summary': f"Executed {len(results)} algorithms using {thinking_method} method"
        }
    
    def _calculate_score(
        self, 
        result: Dict[str, Any], 
        algorithms: List[Dict[str, Any]], 
        thinking_method: str
    ) -> float:
        """Calculate overall execution score"""
        
        # Base score from successful executions
        successful = sum(1 for r in result.get('results', []) if r.get('success', False))
        total = len(result.get('results', []))
        
        if total == 0:
            return 0.0
        
        success_score = successful / total  # 0-1
        
        # Method bonus
        method_bonus = {
            'claude_extended': 0.2,
            'openai_reasoning': 0.15,
            'antigravity': 0.1,
            'direct': 0.05
        }.get(thinking_method, 0.0)
        
        # Combination bonus (using multiple algorithms)
        combo_bonus = min(len(algorithms) * 0.05, 0.15)
        
        total_score = min(success_score + method_bonus + combo_bonus, 1.0)
        
        return total_score
    
    def get_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        avg_time = self.total_execution_time / self.requests_processed if self.requests_processed > 0 else 0
        
        return {
            'gateway_id': self.gateway_id,
            'status': self.status.value,
            'requests_processed': self.requests_processed,
            'avg_execution_time_ms': avg_time,
            'currently_processing': self.current_request.request_id if self.current_request else None
        }


class MultiGatewayOrchestrator:
    """
    Multi-Gateway Orchestrator
    
    Manages multiple gateways for parallel processing
    OpenClaw-inspired architecture
    """
    
    def __init__(self, num_gateways: int = 4):
        self.num_gateways = num_gateways
        self.gateways: List[Gateway] = []
        self.request_queue: Queue = Queue()
        self.active_requests: Dict[str, GatewayResponse] = {}
        self.algorithm_manager = AlgorithmManager()
        
        print(f"\n🌐 Multi-Gateway Orchestrator")
        print(f"   Creating {num_gateways} parallel gateways...")
        
        # Create gateways
        for i in range(num_gateways):
            gateway = Gateway(f"gateway-{i+1}", self.algorithm_manager)
            self.gateways.append(gateway)
        
        print(f"   ✅ {num_gateways} gateways ready\n")
    
    def register_algorithm(self, algorithm):
        """Register algorithm with all gateways"""
        self.algorithm_manager.register(algorithm.spec.algorithm_id, algorithm)
    
    async def process_request(self, user_input: str, context: Dict[str, Any] = None) -> GatewayResponse:
        """Process request through available gateway"""
        
        request = GatewayRequest(
            request_id=f"req-{int(time.time() * 1000)}",
            user_input=user_input,
            context=context or {},
            priority=context.get('priority', 3) if context else 3
        )
        
        # Find idle gateway
        idle_gateway = self._find_idle_gateway()
        
        if idle_gateway:
            # Direct execution
            response = await idle_gateway.process_request(request)
        else:
            # Queue and wait
            self.request_queue.put(request)
            response = await self._wait_for_queue_processing(request)
        
        self.active_requests[request.request_id] = response
        return response
    
    async def process_batch(self, requests: List[Dict[str, Any]]) -> List[GatewayResponse]:
        """Process multiple requests in parallel using all gateways"""
        
        tasks = []
        for req_data in requests:
            task = self.process_request(
                user_input=req_data.get('input', ''),
                context=req_data.get('context', {})
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return responses
    
    def _find_idle_gateway(self) -> Optional[Gateway]:
        """Find an idle gateway"""
        for gateway in self.gateways:
            if gateway.status == GatewayStatus.IDLE:
                return gateway
        return None
    
    async def _wait_for_queue_processing(self, request: GatewayRequest) -> GatewayResponse:
        """Wait for queued request to be processed"""
        max_wait = 60  # seconds
        waited = 0
        
        while waited < max_wait:
            if request.request_id in self.active_requests:
                return self.active_requests[request.request_id]
            
            await asyncio.sleep(0.1)
            waited += 0.1
        
        # Timeout
        return GatewayResponse(
            request_id=request.request_id,
            gateway_id="timeout",
            status=GatewayStatus.ERROR,
            result={},
            execution_time_ms=max_wait * 1000,
            error="Request timeout"
        )
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get statistics from all gateways"""
        
        total_processed = sum(g.requests_processed for g in self.gateways)
        total_time = sum(g.total_execution_time for g in self.gateways)
        avg_time = total_time / total_processed if total_processed > 0 else 0
        
        gateway_stats = [g.get_stats() for g in self.gateways]
        
        busy_gateways = sum(1 for g in self.gateways if g.status == GatewayStatus.BUSY)
        
        return {
            'total_gateways': self.num_gateways,
            'busy_gateways': busy_gateways,
            'idle_gateways': self.num_gateways - busy_gateways,
            'total_requests_processed': total_processed,
            'avg_execution_time_ms': avg_time,
            'queue_size': self.request_queue.qsize(),
            'gateways': gateway_stats
        }
    
    def print_stats(self):
        """Print statistics"""
        stats = self.get_overall_stats()
        
        print("\n" + "=" * 70)
        print("📊 MULTI-GATEWAY ORCHESTRATOR STATISTICS")
        print("=" * 70)
        
        print(f"\nOverall:")
        print(f"  Total Gateways:        {stats['total_gateways']}")
        print(f"  Busy:                  {stats['busy_gateways']}")
        print(f"  Idle:                  {stats['idle_gateways']}")
        print(f"  Requests Processed:    {stats['total_requests_processed']}")
        print(f"  Avg Time:              {stats['avg_execution_time_ms']:.2f}ms")
        print(f"  Queue Size:            {stats['queue_size']}")
        
        print(f"\nGateway Details:")
        for gw_stat in stats['gateways']:
            status_emoji = "🟢" if gw_stat['status'] == 'idle' else "🔴"
            print(f"  {status_emoji} {gw_stat['gateway_id']}: {gw_stat['requests_processed']} requests, {gw_stat['avg_execution_time_ms']:.2f}ms avg")
        
        print("=" * 70)


# Global instance
_orchestrator: Optional[MultiGatewayOrchestrator] = None


def get_multi_gateway_orchestrator(num_gateways: int = 4) -> MultiGatewayOrchestrator:
    """Get or create global multi-gateway orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiGatewayOrchestrator(num_gateways=num_gateways)
    return _orchestrator


if __name__ == "__main__":
    print("\n🌐 Multi-Gateway Orchestrator Module\n")
    
    async def test():
        orchestrator = get_multi_gateway_orchestrator(num_gateways=4)
        
        # Test single request
        response = await orchestrator.process_request(
            user_input="Create a REST API with authentication",
            context={'complexity': 'complex'}
        )
        
        print(f"\nResponse from {response.gateway_id}:")
        print(f"  Status: {response.status.value}")
        print(f"  Score: {response.score:.2f}")
        print(f"  Time: {response.execution_time_ms:.2f}ms")
        print(f"  Method: {response.thinking_method}")
        
        # Show stats
        orchestrator.print_stats()
    
    asyncio.run(test())
