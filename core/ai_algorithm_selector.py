"""
Dive AI V29.3 - AI Algorithm Selector
Core innovation: AI-powered algorithm selection instead of hardcoded routing

Flow:
1. Receive user request + context
2. Query all available algorithms
3. Use AI to select best algorithm(s)
4. Return selection with reasoning
5. Learn from execution results
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os

# Add path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


@dataclass
class AlgorithmSelection:
    """Selected algorithm with reasoning"""
    name: str
    params: Dict[str, Any]
    reasoning: str
    fallbacks: List[str] = field(default_factory=list)
    confidence: float = 1.0


class AIAlgorithmSelector:
    """
    AI-Powered Algorithm Selector
    
    Uses LLM to intelligently select the best algorithm for a given request
    instead of hardcoded routing logic.
    
    Features:
    - Analyzes user request intent
    - Considers algorithm capabilities
    - Selects best match
    - Provides explainable reasoning
    - Learns from past selections
    """
    
    def __init__(self, algorithm_manager, llm_provider="v98", model="claude-opus-4-6-thinking"):
        """
        Initialize AI Algorithm Selector
        
        Args:
            algorithm_manager: AlgorithmManager instance with registered algorithms
            llm_provider: LLM provider for selection (v98, aicoding, etc.)
            model: Model name
        """
        self.algorithm_manager = algorithm_manager
        self.llm_provider = llm_provider
        self.model = model
        
        # Selection history for learning
        self.selection_history: List[Dict[str, Any]] = []
        
        # Success rate tracking
        self.success_rates: Dict[str, List[bool]] = {}
        
        print(f"🤖 AI Algorithm Selector initialized")
        print(f"   Provider: {llm_provider}")
        print(f"   Model: {model}")
    
    async def select(
        self,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AlgorithmSelection:
        """
        Select best algorithm for user request
        
        Args:
            user_request: User's natural language request
            context: Additional context (session, history, etc.)
        
        Returns:
            AlgorithmSelection with chosen algorithm and reasoning
        """
        print(f"\n🤖 AI Selecting Algorithm for: '{user_request[:60]}...'")
        
        # 1. Get available algorithms
        available_algorithms = self._get_available_algorithms()
        
        # 2. Get selection history context
        history_context = self._get_history_context(user_request)
        
        # 3. Build selection prompt
        prompt = self._build_selection_prompt(
            user_request=user_request,
            available_algorithms=available_algorithms,
            context=context,
            history_context=history_context
        )
        
        # 4. Ask LLM to select
        try:
            response = await self._query_llm(prompt)
            selection = self._parse_selection(response)
            
            print(f"   ✅ Selected: {selection.name}")
            print(f"   Confidence: {selection.confidence:.0%}")
            print(f"   Reasoning: {selection.reasoning[:100]}...")
            
            # 5. Record selection
            self._record_selection(user_request, selection)
            
            return selection
            
        except Exception as e:
            print(f"   ❌ Selection failed: {e}")
            # Fallback to simple heuristic
            return self._fallback_selection(user_request, available_algorithms)
    
    def _get_available_algorithms(self) -> List[Dict[str, Any]]:
        """Get all registered algorithms with their specs"""
        algorithms = []
        
        for algo_name in self.algorithm_manager.algorithms.keys():
            algo = self.algorithm_manager.algorithms[algo_name]
            spec = algo.spec
            
            algorithms.append({
                'name': algo_name,
                'description': spec.description,
                'category': spec.category,
                'level': spec.level,
                'inputs': [
                    {'name': inp.name, 'type': inp.type, 'required': inp.required, 'description': inp.description}
                    for inp in spec.io.inputs
                ],
                'outputs': [
                    {'name': out.name, 'type': out.type, 'description': out.description}
                    for out in spec.io.outputs
                ],
                'tags': spec.tags,
                'success_rate': self._get_success_rate(algo_name)
            })
        
        return algorithms
    
    def _get_history_context(self, user_request: str) -> str:
        """Get relevant context from selection history"""
        if not self.selection_history:
            return "No previous selections"
        
        # Get last 5 selections
        recent = self.selection_history[-5:]
        
        context_lines = ["Recent selections:"]
        for entry in recent:
            context_lines.append(
                f"- Request: '{entry['request'][:40]}...' → {entry['selection'].name} "
                f"(Success: {entry.get('success', 'unknown')})"
            )
        
        return "\n".join(context_lines)
    
    def _build_selection_prompt(
        self,
        user_request: str,
        available_algorithms: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]],
        history_context: str
    ) -> str:
        """Build prompt for LLM selection"""
        
        # Format algorithms for AI
        algo_descriptions = []
        for algo in available_algorithms:
            algo_desc = f"""
Algorithm: {algo['name']}
Category: {algo['category']}
Level: {algo['level']}
Description: {algo['description']}
Inputs: {', '.join([f"{i['name']} ({i['type']})" for i in algo['inputs']])}
Outputs: {', '.join([f"{o['name']} ({o['type']})" for o in algo['outputs']])}
Tags: {', '.join(algo['tags'])}
Success Rate: {algo['success_rate']:.0%}
---
"""
            algo_descriptions.append(algo_desc)
        
        prompt = f"""You are an expert AI algorithm selector for the Dive AI system.

USER REQUEST:
"{user_request}"

CONTEXT:
{json.dumps(context, indent=2) if context else 'None'}

SELECTION HISTORY:
{history_context}

AVAILABLE ALGORITHMS ({len(available_algorithms)}):
{''.join(algo_descriptions)}

TASK:
Analyze the user request and select the BEST algorithm to handle it.

CONSIDER:
1. Algorithm capabilities and description
2. Input/output requirements
3. Category and level appropriateness
4. Past success rates
5. Tags matching request keywords
6. Context from user session

RETURN ONLY A JSON object with this EXACT structure:
{{
    "selected_algorithm": "AlgorithmName",
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }},
    "reasoning": "Brief explanation of why this algorithm was chosen",
    "confidence": 0.95,
    "fallback_algorithms": ["FallbackAlgo1", "FallbackAlgo2"]
}}

Be concise and accurate. Focus on the best match.
"""
        
        return prompt
    
    async def _query_llm(self, prompt: str) -> str:
        """Query LLM for algorithm selection"""
        
        # Use AlgorithmManager's LLM connection
        result = self.algorithm_manager.get_connection(
            provider=self.llm_provider,
            model=self.model
        )
        
        if result.status != "success":
            raise Exception(f"LLM connection failed: {result.data.get('error')}")
        
        # In production, would make actual LLM call here
        # For now, simulate with intelligent heuristic
        
        # Simple simulation: return a reasonable response
        # TODO: Replace with actual LLM API call
        
        return json.dumps({
            "selected_algorithm": "CodeGenerator",  # Placeholder
            "parameters": {},
            "reasoning": "Simulated selection - LLM integration pending",
            "confidence": 0.8,
            "fallback_algorithms": ["TestWriter", "DocumentationGenerator"]
        })
    
    def _parse_selection(self, llm_response: str) -> AlgorithmSelection:
        """Parse LLM response into AlgorithmSelection"""
        
        try:
            data = json.loads(llm_response)
            
            return AlgorithmSelection(
                name=data['selected_algorithm'],
                params=data.get('parameters', {}),
                reasoning=data['reasoning'],
                confidence=data.get('confidence', 0.8),
                fallbacks=data.get('fallback_algorithms', [])
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse LLM response: {e}")
    
    def _fallback_selection(
        self,
        user_request: str,
        available_algorithms: List[Dict[str, Any]]
    ) -> AlgorithmSelection:
        """Fallback to simple keyword matching if AI selection fails"""
        
        request_lower = user_request.lower()
        
        # Simple keyword matching
        keywords_to_algo = {
            'code': 'CodeGenerator',
            'test': 'TestWriter',
            'document': 'DocumentationGenerator',
            'ui': 'UITARS',
            'browser': 'UITARS',
            'click': 'UITARS',
            'open': 'UITARS',
            'memory': 'MemoryStore',
            'classify': 'QueryClassifier',
            'error': 'ErrorRecovery',
        }
        
        for keyword, algo_name in keywords_to_algo.items():
            if keyword in request_lower:
                if algo_name in self.algorithm_manager.algorithms:
                    return AlgorithmSelection(
                        name=algo_name,
                        params={},
                        reasoning=f"Fallback selection based on keyword '{keyword}'",
                        confidence=0.5,
                        fallbacks=[]
                    )
        
        # Default to QueryClassifier
        return AlgorithmSelection(
            name="QueryClassifier",
            params={'query': user_request},
            reasoning="Default fallback - query classification",
            confidence=0.3,
            fallbacks=[]
        )
    
    def _record_selection(self, user_request: str, selection: AlgorithmSelection):
        """Record selection for learning"""
        self.selection_history.append({
            'request': user_request,
            'selection': selection,
            'timestamp': datetime.now().isoformat()
        })
    
    async def learn(
        self,
        request: str,
        selection: AlgorithmSelection,
        result: Any
    ):
        """Learn from execution result"""
        
        # Determine success
        success = result.status == "success" if hasattr(result, 'status') else True
        
        # Update success rate
        if selection.name not in self.success_rates:
            self.success_rates[selection.name] = []
        
        self.success_rates[selection.name].append(success)
        
        # Keep last 100 results per algorithm
        if len(self.success_rates[selection.name]) > 100:
            self.success_rates[selection.name] = self.success_rates[selection.name][-100:]
        
        # Update history
        if self.selection_history:
            self.selection_history[-1]['success'] = success
            self.selection_history[-1]['result_status'] = result.status if hasattr(result, 'status') else 'unknown'
        
        print(f"   📊 Learning: {selection.name} → {'✅ Success' if success else '❌ Failed'}")
        print(f"      Success rate: {self._get_success_rate(selection.name):.0%}")
    
    def _get_success_rate(self, algorithm_name: str) -> float:
        """Get success rate for an algorithm"""
        if algorithm_name not in self.success_rates:
            return 0.5  # Default: unknown
        
        results = self.success_rates[algorithm_name]
        if not results:
            return 0.5
        
        return sum(results) / len(results)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get selector statistics"""
        return {
            'total_selections': len(self.selection_history),
            'algorithms_used': len(set(entry['selection'].name for entry in self.selection_history)),
            'success_rates': {
                algo: self._get_success_rate(algo)
                for algo in self.success_rates.keys()
            },
            'recent_selections': [
                {
                    'request': entry['request'][:50],
                    'algorithm': entry['selection'].name,
                    'success': entry.get('success', 'pending')
                }
                for entry in self.selection_history[-10:]
            ]
        }


# Test function
async def test_selector():
    """Test AI Algorithm Selector"""
    print("\n🧪 Testing AI Algorithm Selector\n")
    
    # Mock AlgorithmManager for testing
    class MockAlgorithmManager:
        def __init__(self):
            self.algorithms = {
                'CodeGenerator': type('obj', (object,), {'spec': type('obj', (object,), {
                    'description': 'Generate code from requirements',
                    'category': 'composite',
                    'level': 'composite',
                    'io': type('obj', (object,), {
                        'inputs': [],
                        'outputs': []
                    })(),
                    'tags': ['code', 'generation']
                })()})(),
                'UITARS': type('obj', (object,), {'spec': type('obj', (object,), {
                    'description': 'Desktop automation via natural language',
                    'category': 'operational',
                    'level': 'operational',
                    'io': type('obj', (object,), {
                        'inputs': [],
                        'outputs': []
                    })(),
                    'tags': ['ui', 'automation', 'desktop']
                })()})(),
            }
        
        def get_connection(self, provider, model):
            return type('obj', (object,), {'status': 'success', 'data': {}})()
    
    # Create selector
    selector = AIAlgorithmSelector(
        algorithm_manager=MockAlgorithmManager(),
        llm_provider="v98"
    )
    
    # Test selection
    selection = await selector.select(
        user_request="Create a FastAPI endpoint for user login",
        context={'session_id': 'test_123'}
    )
    
    print(f"\n✅ Selection Result:")
    print(f"   Algorithm: {selection.name}")
    print(f"   Reasoning: {selection.reasoning}")
    print(f"   Confidence: {selection.confidence:.0%}")


if __name__ == "__main__":
    asyncio.run(test_selector())
