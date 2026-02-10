"""
Dive AI V29.4 - Gateway Server with AI Algorithm Selection
Complete integration: Gateway → AI Selector → AlgorithmManager

This is the unified gateway that combines:
- Multi-channel support (Telegram, Discord, CLI, Web)
- AI-powered algorithm selection
- Algorithm execution via AlgorithmManager
- UI-TARS desktop automation
"""

import asyncio
import sys
import os
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add paths
# Add paths
# Add project root to sys.path to allow imports from core
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
print(f"DEBUG: sys.path = {sys.path}")

# Also add strict parent in case
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# Import Dive AI components
try:
    from core.algorithms.algorithm_manager import AlgorithmManager
    from core.ai_algorithm_selector import AIAlgorithmSelector
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    AlgorithmManager = None
    AIAlgorithmSelector = None


# FastAPI app
app = FastAPI(
    title="Dive AI V29.4 Gateway",
    description="Algorithm-based Agentic AI Gateway",
    version="29.4"
)


# Request/Response models
class ChatRequest(BaseModel):
    message: str
    channel: str = "web"
    user_id: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    status: str
    response: str
    algorithm_used: str
    reasoning: str
    execution_time_ms: float
    session_id: str


# Gateway Server
class GatewayServer:
    """
    Dive AI V29.3 Gateway Server
    
    Architecture:
    1. Receive request from channel
    2. AI selects best algorithm
    3. Execute via AlgorithmManager
    4. Return result to channel
    """
    
    def __init__(self, port: int = 1879):
        self.port = port
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize components
        print("🦞 Initializing Dive AI V29.4 Gateway Server...")
        
        # AlgorithmManager (V29.2)
        try:
            self.algorithm_manager = AlgorithmManager()
            print(f"   ✅ AlgorithmManager loaded ({len(self.algorithm_manager.algorithms)} algorithms)")
        except Exception as e:
            print(f"   ⚠️ AlgorithmManager initialization failed: {e}")
            self.algorithm_manager = None
        
        # AI Algorithm Selector
        if self.algorithm_manager:
            try:
                self.ai_selector = AIAlgorithmSelector(
                    algorithm_manager=self.algorithm_manager,
                    llm_provider="v98",
                    model="claude-opus-4-6-thinking"
                )
                print("   ✅ AI Algorithm Selector loaded")
            except Exception as e:
                print(f"   ⚠️ AI Selector initialization failed: {e}")
                self.ai_selector = None
        else:
            self.ai_selector = None
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        
        print(f"✅ Gateway Server initialized on port {port}")
    
    async def process_request(
        self,
        message: str,
        channel: str,
        user_id: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user request through the algorithm-based system
        
        Flow:
        1. Get/create session
        2. AI selects algorithm
        3. Execute algorithm
        4. Learn from result
        5. Return response
        """
        
        start_time = datetime.now()
        self.total_requests += 1
        
        # 1. Session management
        if not session_id:
            session_id = f"{channel}_{user_id}_{int(datetime.now().timestamp())}"
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'id': session_id,
                'channel': channel,
                'user_id': user_id,
                'created_at': datetime.now().isoformat(),
                'history': []
            }
        
        session = self.sessions[session_id]
        
        # 2. AI algorithm selection
        if self.ai_selector:
            try:
                selection = await self.ai_selector.select(
                    user_request=message,
                    context={
                        'session': session,
                        'channel': channel,
                        **(context or {})
                    }
                )
                
                algorithm_name = selection.name
                algorithm_params = selection.params
                reasoning = selection.reasoning
                
            except Exception as e:
                print(f"❌ AI selection failed: {e}")
                algorithm_name = "QueryClassifier"
                algorithm_params = {'query': message}
                reasoning = f"Fallback due to selection error: {str(e)}"
        else:
            # Fallback if no AI selector
            algorithm_name = "QueryClassifier"
            algorithm_params = {'query': message}
            reasoning = "AI Selector not available"
        
        # 3. Execute algorithm via AlgorithmManager
        if self.algorithm_manager:
            try:
                result = self.algorithm_manager.execute(
                    algorithm_name=algorithm_name,
                    params=algorithm_params
                )
                
                # 4. Learn from result
                if self.ai_selector:
                    await self.ai_selector.learn(
                        request=message,
                        selection=selection,
                        result=result
                    )
                
                # 5. Build response
                execution_time = (datetime.now() - start_time).total_seconds() * 1000
                
                response = {
                    'status': result.status,
                    'response': self._format_result(result),
                    'algorithm_used': algorithm_name,
                    'reasoning': reasoning,
                    'execution_time_ms': execution_time,
                    'session_id': session_id,
                    'details': result.data
                }
                
                # Update session history
                session['history'].append({
                    'message': message,
                    'algorithm': algorithm_name,
                    'response': response['response'],
                    'timestamp': datetime.now().isoformat()
                })
                
                self.successful_requests += 1
                return response
                
            except Exception as e:
                print(f"❌ Algorithm execution failed: {e}")
                return {
                    'status': 'error',
                    'response': f"Execution error: {str(e)}",
                    'algorithm_used': algorithm_name,
                    'reasoning': reasoning,
                    'execution_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
                    'session_id': session_id,
                    'error': str(e)
                }
        else:
            return {
                'status': 'error',
                'response': 'AlgorithmManager not available',
                'algorithm_used': 'none',
                'reasoning': 'System not initialized',
                'execution_time_ms': 0,
                'session_id': session_id
            }
    
    def _format_result(self, result) -> str:
        """Format algorithm result for user display"""
        if hasattr(result, 'data') and isinstance(result.data, dict):
            # Extract meaningful response from result data
            if 'response' in result.data:
                return result.data['response']
            elif 'output' in result.data:
                return result.data['output']
            elif 'summary' in result.data:
                return result.data['summary']
            else:
                return str(result.data)
        return str(result)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        stats = {
            'gateway': {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'active_sessions': len(self.sessions),
                'success_rate': self.successful_requests / self.total_requests if self.total_requests > 0 else 0
            }
        }
        
        # Add AI selector stats
        if self.ai_selector:
            stats['ai_selector'] = self.ai_selector.get_statistics()
        
        # Add algorithm manager stats
        if self.algorithm_manager:
            stats['algorithms'] = {
                'total_algorithms': len(self.algorithm_manager.algorithms),
                'registered': list(self.algorithm_manager.algorithms.keys())
            }
        
        return stats


# Global gateway instance
gateway = GatewayServer(port=1879)


# Serve Web IDE
@app.get("/")
async def serve_web_ide():
    """Serve Web IDE interface"""
    # Get absolute path to web_ide directory
    gateway_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(gateway_dir)
    web_ide_path = os.path.join(project_dir, 'web_ide', 'index.html')
    
    if os.path.exists(web_ide_path):
        return FileResponse(web_ide_path)
    else:
        return {"message": "Dive AI Gateway running", "version": "29.4", "path_checked": web_ide_path}


# API Routes
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    POST /chat
    Body:
    {
        "message": "Create a FastAPI endpoint",
        "channel": "web",
        "user_id": "user_123",
        "session_id": "optional_session_id",
        "context": {}
    }
    """
    
    result = await gateway.process_request(
        message=request.message,
        channel=request.channel,
        user_id=request.user_id,
        session_id=request.session_id,
        context=request.context
    )
    
    return ChatResponse(**result)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'Dive AI V29.4 Gateway',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'algorithm_manager': gateway.algorithm_manager is not None,
            'ai_selector': gateway.ai_selector is not None
        }
    }


@app.get("/statistics")
async def get_statistics():
    """Get system statistics"""
    return gateway.get_statistics()


@app.get("/algorithms")
async def list_algorithms():
    """List all available algorithms"""
    if gateway.algorithm_manager:
        return {
            'total': len(gateway.algorithm_manager.algorithms),
            'algorithms': [
                {
                    'name': name,
                    'description': algo.spec.description if hasattr(algo, 'spec') else 'No description',
                    'category': algo.spec.category if hasattr(algo, 'spec') else 'unknown',
                    'level': algo.spec.level if hasattr(algo, 'spec') else 'unknown'
                }
                for name, algo in gateway.algorithm_manager.algorithms.items()
            ]
        }
    else:
        return {'error': 'AlgorithmManager not available'}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat
    
    ws://localhost:1879/ws/session_123
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process request
            result = await gateway.process_request(
                message=data.get('message', ''),
                channel='websocket',
                user_id=data.get('user_id', 'anonymous'),
                session_id=session_id,
                context=data.get('context')
            )
            
            # Send response
            await websocket.send_json(result)
            
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# Main entry point
def start_gateway(host: str = "127.0.0.1", port: int = 1879):
    """Start the gateway server"""
    
    print("\n" + "="*60)
    print("🦞 DIVE AI V29.4 GATEWAY SERVER")
    print("="*60)
    print(f"\nArchitecture: Gateway → AI Selector → AlgorithmManager")
    print(f"\nListening on: http://{host}:{port}")
    print(f"WebSocket:    ws://{host}:{port}/ws/{{session_id}}")
    print(f"\nEndpoints:")
    print(f"  POST /chat         - Send message")
    print(f"  GET  /health       - Health check")
    print(f"  GET  /statistics   - System stats")
    print(f"  GET  /algorithms   - List algorithms")
    print(f"  WS   /ws/{{id}}     - WebSocket chat")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    start_gateway()
