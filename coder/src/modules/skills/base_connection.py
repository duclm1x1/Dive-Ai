#!/usr/bin/env python3
"""
Base Connection Module - Nền tảng cho tất cả các kết nối
Cung cấp các lớp cơ bản cho REST, GraphQL, gRPC, CLI
"""

import sys
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Connection types"""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    CLI = "cli"
    WEBSOCKET = "websocket"
    DATABASE = "database"

@dataclass
class ConnectionConfig:
    """Connection configuration"""
    provider: str
    url: str
    timeout: int = 30
    retry_max: int = 3
    retry_backoff: float = 2.0
    headers: Dict[str, str] = None
    auth: Optional[Dict[str, str]] = None
    compression: Optional[str] = None
    batching: bool = False
    caching: bool = False
    cache_ttl: int = 3600
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

class ConnectionMetrics:
    """Track connection metrics"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
        self.total_latency = 0.0
        self.start_time = datetime.now()
    
    def record_request(self, success: bool, bytes_sent: int = 0, 
                      bytes_received: int = 0, latency: float = 0.0):
        """Record a request"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_bytes_sent += bytes_sent
        self.total_bytes_received += bytes_received
        self.total_latency += latency
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{(self.successful_requests / self.total_requests * 100):.1f}%" if self.total_requests > 0 else "N/A",
            "total_bytes_sent": self.total_bytes_sent,
            "total_bytes_received": self.total_bytes_received,
            "total_latency": f"{self.total_latency:.2f}s",
            "avg_latency": f"{(self.total_latency / self.total_requests):.2f}s" if self.total_requests > 0 else "N/A",
            "throughput": f"{(self.total_bytes_received / duration):.2f} bytes/s" if duration > 0 else "N/A",
            "uptime": f"{duration:.2f}s"
        }

class BaseConnection:
    """Base Connection Class - Nền tảng cho tất cả các kết nối"""
    
    def __init__(self, config: ConnectionConfig):
        """Initialize Base Connection"""
        self.config = config
        self.metrics = ConnectionMetrics()
        self.session = None
        self.is_connected = False
        logger.info(f"✅ Base Connection initialized for {config.provider}")
    
    def connect(self) -> bool:
        """Establish connection"""
        try:
            logger.info(f"🔗 Connecting to {self.config.url}...")
            
            if self.config.provider == "rest":
                self.session = requests.Session()
                self.session.headers.update(self.config.headers)
                
                if self.config.auth:
                    self.session.auth = (self.config.auth.get("username"), 
                                        self.config.auth.get("password"))
            
            self.is_connected = True
            logger.info(f"✅ Connected to {self.config.provider}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Connection failed: {str(e)}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect"""
        if self.session:
            self.session.close()
        self.is_connected = False
        logger.info("✅ Disconnected")
    
    def execute(self, method: str = "GET", endpoint: str = "", 
               data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Execute request"""
        if not self.is_connected:
            self.connect()
        
        try:
            import time
            start_time = time.time()
            
            url = f"{self.config.url}{endpoint}"
            
            logger.info(f"📤 {method} {url}")
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.config.timeout,
                **kwargs
            )
            
            latency = time.time() - start_time
            
            result = {
                "status": "success",
                "status_code": response.status_code,
                "data": response.json() if response.text else None,
                "headers": dict(response.headers),
                "latency": latency
            }
            
            self.metrics.record_request(
                success=response.status_code < 400,
                bytes_sent=len(str(data)) if data else 0,
                bytes_received=len(response.text),
                latency=latency
            )
            
            logger.info(f"✅ Response: {response.status_code} ({latency:.2f}s)")
            
            return result
        
        except Exception as e:
            logger.error(f"❌ Request failed: {str(e)}")
            self.metrics.record_request(success=False)
            return {"status": "error", "error": str(e)}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get connection metrics"""
        return self.metrics.get_stats()

class ConnectionPool:
    """Connection Pool - Quản lý nhiều connections"""
    
    def __init__(self, max_connections: int = 10):
        """Initialize Connection Pool"""
        self.max_connections = max_connections
        self.connections: Dict[str, BaseConnection] = {}
        self.connection_count = 0
        logger.info(f"✅ Connection Pool initialized (max={max_connections})")
    
    def get_connection(self, config: ConnectionConfig) -> BaseConnection:
        """Get or create connection"""
        key = f"{config.provider}:{config.url}"
        
        if key not in self.connections:
            if self.connection_count >= self.max_connections:
                logger.warning("⚠️  Connection pool at max capacity")
                return None
            
            connection = BaseConnection(config)
            connection.connect()
            self.connections[key] = connection
            self.connection_count += 1
            logger.info(f"✅ Created new connection: {key}")
        
        return self.connections[key]
    
    def close_all(self):
        """Close all connections"""
        for connection in self.connections.values():
            connection.disconnect()
        
        self.connections.clear()
        self.connection_count = 0
        logger.info("✅ All connections closed")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "total_connections": self.connection_count,
            "max_connections": self.max_connections,
            "utilization": f"{(self.connection_count / self.max_connections * 100):.1f}%",
            "connections": {
                key: conn.get_metrics() 
                for key, conn in self.connections.items()
            }
        }

def main():
    """Test Base Connection"""
    
    # Test REST API connection
    config = ConnectionConfig(
        provider="rest",
        url="https://jsonplaceholder.typicode.com",
        timeout=10
    )
    
    connection = BaseConnection(config)
    
    if connection.connect():
        # GET request
        result = connection.execute(method="GET", endpoint="/posts/1")
        print(f"\nGET /posts/1:")
        print(json.dumps(result, indent=2, default=str))
        
        # Print metrics
        print(f"\nMetrics:")
        print(json.dumps(connection.get_metrics(), indent=2))
    
    connection.disconnect()

if __name__ == "__main__":
    main()
