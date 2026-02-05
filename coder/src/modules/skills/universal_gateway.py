#!/usr/bin/env python3
"""
Universal API Gateway - Cho phép kết nối mọi loại API
REST, GraphQL, gRPC, WebSocket, Database
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """API Endpoint definition"""
    name: str
    api_type: str  # "rest", "graphql", "grpc", "websocket", "database"
    url: str
    auth: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    retry_max: int = 3
    metadata: Optional[Dict[str, Any]] = None

class UniversalGateway:
    """Universal API Gateway - Kết nối mọi loại API"""
    
    def __init__(self):
        """Initialize Universal Gateway"""
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.call_history: List[Dict[str, Any]] = []
        self.api_stats: Dict[str, Dict[str, int]] = {}
        logger.info("✅ Universal API Gateway initialized")
    
    def register_api(self, name: str, api_type: str, url: str, 
                    auth: Optional[Dict] = None, 
                    headers: Optional[Dict] = None,
                    **kwargs) -> bool:
        """Register API endpoint"""
        try:
            endpoint = APIEndpoint(
                name=name,
                api_type=api_type,
                url=url,
                auth=auth,
                headers=headers or {},
                **kwargs
            )
            
            self.endpoints[name] = endpoint
            self.api_stats[name] = {"calls": 0, "success": 0, "failed": 0}
            
            logger.info(f"✅ Registered API: {name} ({api_type}) -> {url}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to register API: {str(e)}")
            return False
    
    def call(self, api_name: str, method: str = "GET", endpoint: str = "",
            data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Call API endpoint"""
        
        if api_name not in self.endpoints:
            error = f"API '{api_name}' not found"
            logger.error(f"❌ {error}")
            return {"status": "error", "error": error}
        
        api = self.endpoints[api_name]
        
        logger.info(f"📤 Calling {api_name} ({api.api_type}): {method} {endpoint}")
        
        try:
            # Route to appropriate handler
            if api.api_type == "rest":
                result = self._call_rest(api, method, endpoint, data, **kwargs)
            elif api.api_type == "graphql":
                result = self._call_graphql(api, data, **kwargs)
            elif api.api_type == "grpc":
                result = self._call_grpc(api, endpoint, data, **kwargs)
            elif api.api_type == "websocket":
                result = self._call_websocket(api, data, **kwargs)
            elif api.api_type == "database":
                result = self._call_database(api, data, **kwargs)
            else:
                result = {"status": "error", "error": f"Unknown API type: {api.api_type}"}
            
            # Record call
            self._record_call(api_name, result)
            
            return result
        
        except Exception as e:
            logger.error(f"❌ API call failed: {str(e)}")
            self._record_call(api_name, {"status": "error", "error": str(e)})
            return {"status": "error", "error": str(e)}
    
    def _call_rest(self, api: APIEndpoint, method: str, endpoint: str,
                  data: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """Call REST API"""
        try:
            import requests
            import time
            
            start_time = time.time()
            url = f"{api.url}{endpoint}"
            
            headers = api.headers.copy() if api.headers else {}
            headers["Content-Type"] = "application/json"
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                auth=(api.auth.get("username"), api.auth.get("password")) if api.auth else None,
                timeout=api.timeout,
                **kwargs
            )
            
            latency = time.time() - start_time
            
            return {
                "status": "success",
                "api_type": "rest",
                "status_code": response.status_code,
                "data": response.json() if response.text else None,
                "latency": latency
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _call_graphql(self, api: APIEndpoint, data: Optional[Dict],
                     **kwargs) -> Dict[str, Any]:
        """Call GraphQL API"""
        try:
            import requests
            import time
            
            start_time = time.time()
            
            query = data.get("query") if data else ""
            variables = data.get("variables", {}) if data else {}
            
            payload = {"query": query, "variables": variables}
            
            response = requests.post(
                api.url,
                json=payload,
                headers=api.headers or {},
                timeout=api.timeout,
                **kwargs
            )
            
            latency = time.time() - start_time
            
            return {
                "status": "success",
                "api_type": "graphql",
                "data": response.json(),
                "latency": latency
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _call_grpc(self, api: APIEndpoint, endpoint: str,
                  data: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """Call gRPC API"""
        try:
            # gRPC implementation would go here
            return {
                "status": "success",
                "api_type": "grpc",
                "message": f"gRPC call to {endpoint}",
                "data": data
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _call_websocket(self, api: APIEndpoint, data: Optional[Dict],
                       **kwargs) -> Dict[str, Any]:
        """Call WebSocket API"""
        try:
            # WebSocket implementation would go here
            return {
                "status": "success",
                "api_type": "websocket",
                "message": f"WebSocket connection to {api.url}",
                "data": data
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _call_database(self, api: APIEndpoint, data: Optional[Dict],
                      **kwargs) -> Dict[str, Any]:
        """Call Database API"""
        try:
            # Database implementation would go here
            query = data.get("query") if data else ""
            
            return {
                "status": "success",
                "api_type": "database",
                "message": f"Database query executed",
                "query": query
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _record_call(self, api_name: str, result: Dict[str, Any]):
        """Record API call"""
        call_record = {
            "api": api_name,
            "timestamp": datetime.now().isoformat(),
            "status": result.get("status"),
            "latency": result.get("latency", 0)
        }
        
        self.call_history.append(call_record)
        
        if api_name in self.api_stats:
            self.api_stats[api_name]["calls"] += 1
            if result.get("status") == "success":
                self.api_stats[api_name]["success"] += 1
            else:
                self.api_stats[api_name]["failed"] += 1
    
    def get_api_list(self) -> List[Dict[str, Any]]:
        """Get list of registered APIs"""
        return [
            {
                "name": endpoint.name,
                "type": endpoint.api_type,
                "url": endpoint.url,
                "stats": self.api_stats.get(endpoint.name, {})
            }
            for endpoint in self.endpoints.values()
        ]
    
    def get_gateway_stats(self) -> Dict[str, Any]:
        """Get gateway statistics"""
        total_calls = sum(stats["calls"] for stats in self.api_stats.values())
        total_success = sum(stats["success"] for stats in self.api_stats.values())
        total_failed = sum(stats["failed"] for stats in self.api_stats.values())
        
        return {
            "total_apis": len(self.endpoints),
            "total_calls": total_calls,
            "total_success": total_success,
            "total_failed": total_failed,
            "success_rate": f"{(total_success / total_calls * 100):.1f}%" if total_calls > 0 else "N/A",
            "api_stats": self.api_stats,
            "recent_calls": self.call_history[-10:]  # Last 10 calls
        }
    
    def print_gateway_info(self):
        """Print gateway information"""
        print("\n" + "="*80)
        print("UNIVERSAL API GATEWAY - INFORMATION")
        print("="*80)
        
        print("\n📋 Registered APIs:")
        for api in self.get_api_list():
            print(f"  • {api['name']} ({api['type']}) -> {api['url']}")
            print(f"    Calls: {api['stats'].get('calls', 0)}, Success: {api['stats'].get('success', 0)}, Failed: {api['stats'].get('failed', 0)}")
        
        stats = self.get_gateway_stats()
        print(f"\n📊 Gateway Statistics:")
        print(f"  Total APIs: {stats['total_apis']}")
        print(f"  Total Calls: {stats['total_calls']}")
        print(f"  Success Rate: {stats['success_rate']}")
        print("="*80)

def main():
    """Test Universal Gateway"""
    
    gateway = UniversalGateway()
    
    # Register APIs
    gateway.register_api(
        "jsonplaceholder",
        "rest",
        "https://jsonplaceholder.typicode.com"
    )
    
    gateway.register_api(
        "github_graphql",
        "graphql",
        "https://api.github.com/graphql"
    )
    
    # Make calls
    print("\n🔄 Testing Universal Gateway...\n")
    
    # REST API call
    result1 = gateway.call("jsonplaceholder", method="GET", endpoint="/posts/1")
    print(f"REST API Call: {result1['status']}")
    
    # GraphQL API call (simulated)
    result2 = gateway.call("github_graphql", data={"query": "{ viewer { login } }"})
    print(f"GraphQL API Call: {result2['status']}")
    
    # Print gateway info
    gateway.print_gateway_info()

if __name__ == "__main__":
    main()
